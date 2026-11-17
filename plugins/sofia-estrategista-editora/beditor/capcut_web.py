"""Tradução limitada de um plano para um novo draft CapCut Web, sem rede.

O módulo chama apenas as funções públicas injetadas do builder oficial. Gestão de
sessão, upload, concorrência, salvamento e revisão pertencem ao chamador.
"""
from __future__ import annotations

from copy import deepcopy
import math
from typing import Any
from urllib.parse import urlsplit

from scripts.validar_plano_editorial import validate


class UnsupportedWebPlan(ValueError):
    """Não é possível representar o plano sem perder informação."""


def _source(uri: object, *, audio: bool = False) -> str:
    if not isinstance(uri, str) or any(ch.isspace() for ch in uri):
        raise UnsupportedWebPlan('A mídia precisa de uma URI CapCut válida e já carregada')
    parsed = urlsplit(uri)
    schemes = ('vid', 'tos', 'asset', 'sid') if audio else ('vid', 'tos', 'asset')
    if parsed.scheme not in schemes or not (parsed.netloc or parsed.path) or parsed.query or parsed.fragment:
        raise UnsupportedWebPlan('Use uma URI de mídia CapCut válida e já carregada ou selecionada')
    return uri


def apply_new_plan(draft: dict[str, Any], plan: dict[str, Any], *, resources: dict[str, str],
                   video_layers: dict[str, int], text_layers: dict[str, int],
                   apply_video, apply_text, apply_audio=None, audio_layers=None,
                   audio_roles=None, audio_volumes=None, text_layouts=None) -> dict[str, Any]:
    """Aplica clipes visuais, áudio e lettering simples em cópia de draft vazio.

    `resources` é o mapeamento asset_id -> URI CapCut obtida no upload ou
    snapshot; índices de layer são explícitos e compartilhados por vídeo/texto.
    `apply_video`, `apply_audio` e `apply_text` são funções públicas do builder
    oficial. `audio_roles` informa por ID de clipe fala, musica ou efeito;
    `audio_layers` associa pistas de áudio a layers próprios; `audio_volumes`
    opcionalmente define ganho de 0 a 4 por ID de clipe.
    Nenhum objeto de entrada é alterado; qualquer exceção interrompe a operação.
    O chamador deve gerir sessão/versão e não repetir uma gravação incerta.
    """
    errors = validate(plan)
    if errors:
        raise UnsupportedWebPlan('Plano inválido: ' + '; '.join(errors))
    if plan['project']['editor'] != 'capcut':
        raise UnsupportedWebPlan('Plano deve selecionar CapCut')
    segments = draft.get('segments') if isinstance(draft, dict) else None
    if (not isinstance(segments, list) or len(segments) != 1 or not isinstance(segments[0], dict)
            or segments[0].get('type') != 'DRAFT'):
        raise UnsupportedWebPlan('A montagem automática requer um draft inicial sem conteúdo; edite drafts existentes pelo fluxo colaborativo')
    assets = {a['id']: a for a in plan['assets']}
    prepared = []
    additional_warnings = []
    audio_layers = {} if audio_layers is None else audio_layers
    audio_roles = {} if audio_roles is None else audio_roles
    audio_volumes = {} if audio_volumes is None else audio_volumes
    if not all(isinstance(value, dict) for value in (audio_layers, audio_roles, audio_volumes)):
        raise UnsupportedWebPlan('Mapeamentos de áudio devem ser objetos')
    audio_ids = {clip['id'] for clip in plan['clips'] if clip['kind'] == 'audio'}
    if set(audio_roles) - audio_ids or set(audio_volumes) - audio_ids:
        raise UnsupportedWebPlan('Papel ou volume informado para clipe de áudio inexistente')
    for clip in plan['clips']:
        asset = assets[clip['asset_id']]
        if clip['kind'] == 'audio':
            if not callable(apply_audio):
                raise UnsupportedWebPlan('Áudio independente requer a função apply_audio oficial')
            role = audio_roles.get(clip['id'])
            if role not in ('fala', 'musica', 'efeito'):
                raise UnsupportedWebPlan('Informe o papel do áudio: fala, musica ou efeito')
            layer = audio_layers.get(clip['track'])
            if type(layer) is not int or layer < 0:
                raise UnsupportedWebPlan('Mapeie cada pista de áudio para um layer inteiro não negativo')
            volume = audio_volumes.get(clip['id'], 1.0)
            try:
                valid_volume = not isinstance(volume, bool) and isinstance(volume, (int, float)) and math.isfinite(volume) and 0 <= volume <= 4
            except OverflowError:
                valid_volume = False
            if not valid_volume:
                raise UnsupportedWebPlan('Volume de áudio deve ser finito entre 0 e 4')
            for visual in plan['clips']:
                if visual['kind'] != 'video' or not visual.get('carries_source_audio') or visual['asset_id'] != clip['asset_id']:
                    continue
                if (max(visual['timeline']['start_ms'], clip['timeline']['start_ms']) < min(visual['timeline']['end_ms'], clip['timeline']['end_ms'])
                        and max(visual['source']['start_ms'], clip['source']['start_ms']) < min(visual['source']['end_ms'], clip['source']['end_ms'])):
                    raise UnsupportedWebPlan('Áudio separado se sobrepõe ao áudio original do mesmo vídeo; silencie o vídeo ou revise o plano')
            source = _source(resources.get(clip['asset_id']), audio=True)
            prepared.append(('audio', clip['id'], {'source':source, 'start_ms':clip['timeline']['start_ms'],
                             'duration_ms':clip['timeline']['end_ms'] - clip['timeline']['start_ms'],
                             'source_start_ms':clip['source']['start_ms'], 'meta_type':'MUSIC' if role == 'musica' else 'SOUND',
                             'volume':volume, 'layer':layer}))
            if role == 'fala':
                additional_warnings.append('Fala mapeada como SOUND pela API do builder; confirme reprodução e sincronismo no CapCut.')
            continue
        if clip['kind'] != 'video' or asset['kind'] not in ('video', 'image'):
            raise UnsupportedWebPlan('Tipo de clipe visual não suportado')
        if asset['kind'] == 'image' and clip.get('carries_source_audio'):
            raise UnsupportedWebPlan('Uma imagem não contém áudio original')
        layer = video_layers.get(clip['track'])
        if type(layer) is not int or layer < 0:
            raise UnsupportedWebPlan('Mapeie cada pista visual para um layer inteiro não negativo')
        source = _source(resources.get(clip['asset_id']))
        duration = clip['timeline']['end_ms'] - clip['timeline']['start_ms']
        prepared.append(('video', clip['id'], {'source': source, 'start_ms': clip['timeline']['start_ms'],
                          'duration_ms': duration, 'source_start_ms': clip['source']['start_ms'],
                          'meta_type': 'photo' if asset['kind'] == 'image' else 'video',
                          'volume': 1.0 if clip.get('carries_source_audio', False) else 0.0, 'layer': layer}))
    text_layouts = {} if text_layouts is None else text_layouts
    if not isinstance(text_layouts, dict) or set(text_layouts) - {t['id'] for t in plan.get('text_layers', [])}:
        raise UnsupportedWebPlan('Layouts devem identificar textos existentes')
    for text in plan.get('text_layers', []):
        if text['type'] != 'lettering':
            raise UnsupportedWebPlan('Legendas usam o fluxo oficial próprio; não são texto simples')
        if text.get('style'):
            raise UnsupportedWebPlan('Estilo de lettering ainda não está mapeado; não descarte atributos')
        layer = text_layers.get(text['track'])
        if type(layer) is not int or layer < 0:
            raise UnsupportedWebPlan('Mapeie cada pista de texto para um layer inteiro não negativo')
        layout = text_layouts.get(text['id'], {})
        if not isinstance(layout, dict) or set(layout) - {'position_x', 'position_y', 'scale_x', 'scale_y'}:
            raise UnsupportedWebPlan('Layout de texto inválido')
        for key, value in layout.items():
            try:
                valido = not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)
            except OverflowError:
                valido = False
            if not valido:
                raise UnsupportedWebPlan('Coordenada de texto inválida')
            if (key.startswith('position_') and not -1 <= value <= 1) or (key.startswith('scale_') and not 0 < value <= 4):
                raise UnsupportedWebPlan('Coordenada ou escala de texto fora do intervalo')
        prepared.append(('text', text['id'], {'content': text['text'], 'start_ms': text['timeline']['start_ms'],
                          'duration_ms': text['timeline']['end_ms'] - text['timeline']['start_ms'],
                          'layout': {'layer': layer, **layout}}))
    if not prepared:
        raise UnsupportedWebPlan('O plano não contém clipes nem lettering')
    current = deepcopy(draft)
    mapping, warnings = {}, additional_warnings
    for kind, identifier, arguments in prepared:
        function = {'video': apply_video, 'audio': apply_audio, 'text': apply_text}[kind]
        result = function(current, **arguments)
        ids = result.get('added_segment_ids')
        if not isinstance(ids, list) or len(ids) != 1 or not isinstance(ids[0], str) or not ids[0]:
            raise ValueError('Builder não retornou exatamente um ID para a operação')
        current = result['draft']
        mapping[f'{kind}:{identifier}'] = ids[0]
        warnings.extend(result.get('warnings', []))
    return {'draft': current, 'segment_ids': mapping, 'warnings': warnings,
            'notice': 'Resultado local; não foi salvo no CapCut. Confirme versão, salve e leia de volta pelo fluxo colaborativo.'}
