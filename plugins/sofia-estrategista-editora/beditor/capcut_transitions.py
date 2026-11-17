"""Aplicação local de transições preparadas ao snapshot CapCut Web.

O helper oficial é injetado pelo host; não há rede, catálogo, push ou exportação.
"""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from typing import Any
from urllib.parse import urlsplit


class UnsupportedTransition(ValueError):
    """A transição não pode ser aplicada com segurança à versão fornecida."""


def _interval(segment: dict) -> tuple[int, int]:
    timeline = segment.get('timeline')
    if not isinstance(timeline, dict):
        raise UnsupportedTransition('Vídeo sem timeline válida')
    start, duration = timeline.get('start.ms'), timeline.get('duration.ms')
    if type(start) is not int or start < 0 or type(duration) is not int or duration <= 0:
        raise UnsupportedTransition('Intervalo de vídeo inválido')
    return start, start + duration


def prepare_transitions(draft: dict, package_id: str, operations: list[dict], *, apply_transition) -> dict:
    """Aplica transições sem modificar o snapshot original ou salvar no servidor.

    Cada operação tem `from_segment_id`, `to_segment_id`, `source` e
    `duration_ms`. Fonte deve ser URI vimo:// obtida no catálogo CapCut. O
    caller deve conferir a versão atual antes de editar e tratar conflitos.
    Para evitar sobrescrita ou combinação não planejada, esta primeira versão
    recusa snapshots que já possuam qualquer atributo de transição.
    """
    if not isinstance(package_id, str) or not package_id.strip():
        raise UnsupportedTransition('Informe o package_id da base')
    if not isinstance(draft, dict) or not isinstance(draft.get('segments'), list):
        raise UnsupportedTransition('Snapshot completo é obrigatório')
    index = {}
    for segment in draft['segments']:
        if not isinstance(segment, dict) or not isinstance(segment.get('id'), str) or not segment['id'] or segment['id'] in index:
            raise UnsupportedTransition('Segmento inválido ou ID repetido')
        index[segment['id']] = segment
    roots = [s['id'] for s in index.values() if s.get('type') == 'DRAFT']
    if len(roots) != 1:
        raise UnsupportedTransition('Snapshot precisa ter uma raiz DRAFT')
    root = roots[0]
    videos = []
    for segment in index.values():
        if segment.get('type') != 'VIDEO' or segment.get('parent_id') != root:
            continue
        attrs = segment.get('attributes', {})
        layout = segment.get('layout', {})
        if not isinstance(attrs, dict) or not isinstance(layout, dict):
            raise UnsupportedTransition('Atributos ou layout do vídeo inválidos')
        if any(key in attrs for key in ('transition','transition.duration.ms','transition.overlap')):
            raise UnsupportedTransition('Já há transição no draft; revise a existente sem substituição implícita')
        layer = layout.get('layer', 0)
        if type(layer) is not int or layer < 0:
            raise UnsupportedTransition('Layer de vídeo inválido')
        start, end = _interval(segment)
        videos.append((layer, start, end, segment['id']))
    if not isinstance(operations, list) or not operations:
        raise UnsupportedTransition('Informe as transições desejadas')
    by_layer = defaultdict(list)
    for layer, start, end, sid in sorted(videos):
        by_layer[layer].append((start, end, sid))
    adjacency = {}
    for clips in by_layer.values():
        for left, right in zip(clips, clips[1:]):
            if left[1] == right[0]:
                adjacency[(left[2], right[2])] = (left[1]-left[0],right[1]-right[0])
    prepared = []
    previous = set()
    incoming, outgoing = {}, {}
    for op in operations:
        if not isinstance(op, dict) or set(op) != {'from_segment_id','to_segment_id','source','duration_ms'}:
            raise UnsupportedTransition('Cada transição exige IDs, URI e duração')
        a,b,source,duration = op['from_segment_id'],op['to_segment_id'],op['source'],op['duration_ms']
        if not isinstance(a,str) or not isinstance(b,str) or (a,b) not in adjacency or a in previous:
            raise UnsupportedTransition('Os vídeos devem ser vizinhos contíguos na mesma camada, sem repetição')
        if not isinstance(source,str) or any(ch.isspace() for ch in source):
            raise UnsupportedTransition('URI de transição inválida')
        uri = urlsplit(source)
        if uri.scheme != 'vimo' or not (uri.netloc or uri.path) or uri.query or uri.fragment:
            raise UnsupportedTransition('Escolha uma URI vimo:// do catálogo CapCut')
        left_duration,right_duration = adjacency[(a,b)]
        if type(duration) is not int or duration <= 0 or duration > min(left_duration,right_duration):
            raise UnsupportedTransition('Duração deve ser positiva e caber nos dois vídeos')
        previous.add(a)
        outgoing[a] = duration
        incoming[b] = duration
        prepared.append(op)
    for sid in set(incoming) & set(outgoing):
        start,end = _interval(index[sid])
        if incoming[sid]+outgoing[sid] > end-start:
            raise UnsupportedTransition('Transições sobrepostas excedem a duração do clipe intermediário')
    current = deepcopy(draft)
    changes, warnings, checks = [], [], []
    for op in prepared:
        result = apply_transition(current, **op)
        if (not isinstance(result, dict) or not isinstance(result.get('draft'), dict)
                or result.get('updated_segment_ids') != [op['from_segment_id']]
                or result.get('added_segment_ids')):
            raise ValueError('Builder não confirmou a transição esperada')
        current = result['draft']
        target = next((s for s in current.get('segments', []) if s.get('id') == op['from_segment_id']), None)
        attrs = target.get('attributes', {}) if isinstance(target, dict) else {}
        if attrs.get('transition') != op['source'] or attrs.get('transition.duration.ms') != op['duration_ms']:
            raise ValueError('Draft retornado não contém a transição solicitada')
        changes.append({'from_segment_id':op['from_segment_id'],'to_segment_id':op['to_segment_id']})
        warnings.extend(result.get('warnings', []))
        checks.append(result.get('check_result'))
    return {'draft':current,'base_package_id':package_id,'changes':changes,'warnings':warnings,
            'check_results':checks,'notice':'Resultado local não salvo; valide versão e aparência no CapCut.'}
