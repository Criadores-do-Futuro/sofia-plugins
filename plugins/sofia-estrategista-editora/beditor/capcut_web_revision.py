"""Prepara uma revisão local sobre um snapshot CapCut Web versionado.

As funções de mutação são injetadas a partir da skill oficial do host. Este
módulo não faz rede, não salva, não lida com conflitos e não confirma resultado
visual. O chamador deve executar o fluxo colaborativo de versão antes do push.
"""
from __future__ import annotations

from copy import deepcopy
import math
from typing import Any


class UnsupportedRevision(ValueError):
    """A revisão não pode ser executada sem alteração ou perda não planejada."""


def _index(draft: Any) -> tuple[dict[str, dict], str]:
    if not isinstance(draft, dict) or not isinstance(draft.get('segments'), list):
        raise UnsupportedRevision('Snapshot completo é obrigatório')
    index = {}
    for item in draft['segments']:
        if not isinstance(item, dict) or not isinstance(item.get('id'), str) or not item['id'] or item['id'] in index:
            raise UnsupportedRevision('Snapshot contém segmentos inválidos ou IDs duplicados')
        index[item['id']] = item
    roots = [item['id'] for item in index.values() if item.get('type') == 'DRAFT']
    if len(roots) != 1:
        raise UnsupportedRevision('Snapshot deve possuir exatamente um DRAFT')
    return index, roots[0]


def _valid_layout(layout: Any) -> bool:
    if not isinstance(layout, dict) or not layout or set(layout) - {'layer','position_x','position_y','scale_x','scale_y'}:
        return False
    for key, value in layout.items():
        if key == 'layer':
            if type(value) is not int or value < 0:
                return False
        elif isinstance(value, bool) or not isinstance(value, (int, float)):
            return False
        else:
            try:
                if not math.isfinite(value):
                    return False
            except OverflowError:
                return False
    return True


def prepare_revision(draft: dict, package_id: str, operations: list[dict], *,
                     update_material, update_placement, remove_material) -> dict:
    """Retorna draft completo revisado e a versão da base, sem salvá-lo.

    Cada operação usa um ID obtido no snapshot: `content` muda texto simples;
    `placement` altera tempo/layout em root-level; `remove` só remove um
    segmento sem filhos. Cada ID aparece no máximo uma vez por rodada. Não
    traduz legendas, estilização, transições, ripple ou edições indiretas.
    """
    if not isinstance(package_id, str) or not package_id.strip():
        raise UnsupportedRevision('Informe o package_id do snapshot vigente')
    index, root = _index(draft)
    if not isinstance(operations, list) or not operations:
        raise UnsupportedRevision('Informe ao menos uma operação explícita')
    seen = set()
    actions = []
    for op in operations:
        if not isinstance(op, dict):
            raise UnsupportedRevision('Operação deve ser um objeto')
        action, segment_id = op.get('op'), op.get('segment_id')
        permitted = {'content': {'op','segment_id','text'},
                     'placement': {'op','segment_id','start_ms','duration_ms','layout'},
                     'remove': {'op','segment_id'}}
        if not isinstance(action, str) or action not in permitted or set(op) - permitted[action]:
            raise UnsupportedRevision('Operação ou atributos não suportados')
        if not isinstance(segment_id, str) or segment_id not in index or segment_id == root:
            raise UnsupportedRevision('ID deve identificar segmento existente diferente da raiz')
        if segment_id in seen:
            raise UnsupportedRevision('Cada segmento pode ser revisado uma vez por rodada')
        seen.add(segment_id)
        segment = index[segment_id]
        children = [s for s in index.values() if s.get('parent_id') == segment_id]
        if action == 'content':
            attrs = segment.get('attributes', {})
            if segment.get('type') != 'TEXT' or not isinstance(attrs, dict) or any(k in attrs for k in ('caption_timeline','subtitle_timeline')):
                raise UnsupportedRevision('Somente texto simples pode ser atualizado; legenda usa fluxo próprio')
            text = op.get('text')
            if not isinstance(text, str) or not text.strip():
                raise UnsupportedRevision('Texto precisa ser não vazio')
            if children:
                old = attrs.get('content')
                if (not isinstance(old, str) or any(c.get('type') != 'PATCH' for c in children)
                        or len(old) != len(text)
                        or len(old.encode('utf-16-le')) != len(text.encode('utf-16-le'))):
                    raise UnsupportedRevision('Texto com estilos da nuvem exige revisão específica quando o comprimento muda')
                for child in children:
                    a = child.get('attributes')
                    if not isinstance(a, dict) or type(a.get('letter_start')) is not int or type(a.get('letter_end')) is not int or not 0 <= a['letter_start'] < a['letter_end'] <= len(old):
                        raise UnsupportedRevision('Faixa de estilo do texto é inválida ou não verificável')
            actions.append((action, segment_id, {'content': text}))
        elif action == 'placement':
            if segment.get('parent_id') != root:
                raise UnsupportedRevision('A posição só pode ser mudada em segmento ligado à raiz')
            values = {k:op[k] for k in ('start_ms','duration_ms','layout') if k in op}
            if not values:
                raise UnsupportedRevision('Informe tempo ou layout')
            if ('start_ms' in values and (type(values['start_ms']) is not int or values['start_ms'] < 0)
                    or 'duration_ms' in values and (type(values['duration_ms']) is not int or values['duration_ms'] <= 0)
                    or 'layout' in values and not _valid_layout(values['layout'])):
                raise UnsupportedRevision('Tempo ou layout inválido')
            actions.append((action, segment_id, values))
        else:
            if children:
                raise UnsupportedRevision('Remoção teria efeito em elementos filhos; revise-os separadamente')
            if segment.get('type') == 'VIDEO' and any(isinstance(s.get('attributes'), dict) and 'transition' in s['attributes'] for s in index.values() if s.get('type') == 'VIDEO'):
                raise UnsupportedRevision('Remoção de vídeo com transições requer revisão específica')
            actions.append((action, segment_id, {}))
    current = deepcopy(draft)
    changes, warnings = [], []
    for action, sid, args in actions:
        function = {'content':update_material,'placement':update_placement,'remove':remove_material}[action]
        result = function(current, sid, **args)
        if not isinstance(result, dict) or not isinstance(result.get('draft'), dict):
            raise ValueError('Builder retornou um resultado inválido')
        expected = 'removed_segment_ids' if action == 'remove' else 'updated_segment_ids'
        if sid not in result.get(expected, []):
            raise ValueError('Builder não confirmou o segmento solicitado')
        if action == 'remove' and set(result[expected]) != {sid}:
            raise ValueError('Remoção alterou elementos adicionais; resultado descartado')
        current = result['draft']
        warnings.extend(result.get('warnings', []))
        if action == 'placement' and index[sid].get('type') in ('VIDEO','AUDIO'):
            warnings.append('Revisar sincronismo audiovisual e duração da mídia após reposicionamento.')
        if action == 'remove':
            warnings.append('A remoção não fecha lacunas da timeline; revisar montagem.')
        changes.append({'op':action,'segment_id':sid})
    return {'base_package_id':package_id, 'draft':current, 'changes':changes, 'warnings':warnings,
            'notice':'Revisão local não salva; confirme versão no servidor e use o fluxo colaborativo oficial.'}
