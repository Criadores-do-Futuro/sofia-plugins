"""Aplicação local de legendas já reconhecidas no CapCut Web.

Somente usa o helper oficial injetado; reconhecimento, cobrança, sessão,
controle de versão, push e revisão visual continuam no workflow oficial.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any


class UnsupportedCaptions(ValueError):
    """O batch ou os vínculos não são seguros para aplicação."""


def _identity(item: Any) -> tuple[str, ...]:
    if not isinstance(item, dict):
        raise UnsupportedCaptions('Identidade do recurso inválida')
    vid = item.get('vid')
    workspace, resource = item.get('workspace_id'), item.get('resource_id')
    if isinstance(vid, str) and vid.strip() and workspace in (None, '') and resource in (None, ''):
        return ('vid', vid)
    if vid in (None, '') and all(isinstance(v, str) and v.strip() for v in (workspace, resource)):
        return ('workspace', workspace, resource)
    raise UnsupportedCaptions('Use VID ou o par workspace_id/resource_id')


def apply_recognized(draft: dict, package_id: str, query_result: dict, bindings: list[dict], *,
                     apply_captions, complete_query_result: bool, source_proofs=None,
                     layout=None, text_style=None) -> dict:
    """Aplica recursos reconhecidos já finalizados a cópia de snapshot versionado.

    `bindings` lista {resource: {vid} ou {workspace_id,resource_id},
    segment_ids:[...]} com IDs efetivos do snapshot. A fonte vid:// é conferida
    diretamente. Para asset:// exige `source_proofs[segment_id]` com `source`,
    `package_id`, identidade do recurso e `evidence` não vazio, com a identidade
    verificada anteriormente pelo chamador. Snapshot não fornece esse vínculo.

    `complete_query_result=True` declara que o chamador reteve o resultado completo
    estruturado, não apenas uma resposta truncada. Uma operação de append é
    recusada quando já há legendas no snapshot, para evitar duplicação silenciosa.
    """
    if not isinstance(package_id, str) or not package_id.strip():
        raise UnsupportedCaptions('Informe a versão do snapshot')
    if complete_query_result is not True or not isinstance(query_result, dict) or query_result.get('next_action') != 'none':
        raise UnsupportedCaptions('Reconhecimento precisa estar concluído, liquidado e integralmente disponível')
    resources = query_result.get('resources')
    if not isinstance(resources, list):
        raise UnsupportedCaptions('Batch sem recursos estruturados')
    if not isinstance(bindings, list) or not bindings:
        raise UnsupportedCaptions('Informe os vínculos explícitos de cada recurso')
    if not isinstance(draft, dict) or not isinstance(draft.get('segments'), list):
        raise UnsupportedCaptions('Snapshot completo é obrigatório')
    index = {}
    for segment in draft['segments']:
        if not isinstance(segment, dict) or not isinstance(segment.get('id'), str) or not segment['id'] or segment['id'] in index:
            raise UnsupportedCaptions('Segmentos inválidos ou IDs repetidos no snapshot')
        index[segment['id']] = segment
        attrs = segment.get('attributes', {})
        if isinstance(attrs, dict) and ('caption_timeline' in attrs or 'subtitle_timeline' in attrs):
            raise UnsupportedCaptions('Snapshot já possui legendas; use revisão de legendas existentes para evitar duplicação')
    roots = [s['id'] for s in index.values() if s.get('type') == 'DRAFT']
    if len(roots) != 1:
        raise UnsupportedCaptions('Snapshot deve possuir uma raiz DRAFT')
    root = roots[0]
    recognized = {}
    failures = []
    for entry in resources:
        identity = _identity(entry)
        if identity in recognized:
            raise UnsupportedCaptions('Resultado contém recurso duplicado')
        recognized[identity] = entry
        if type(entry.get('status')) is not int or entry['status'] != 0:
            failures.append(identity)
    proofs = {} if source_proofs is None else source_proofs
    if not isinstance(proofs, dict):
        raise UnsupportedCaptions('Comprovações de fonte inválidas')
    groups: dict[tuple[str, ...], list[tuple[dict, list[str]]]] = {}
    used_segments, used_resources = set(), set()
    for binding in bindings:
        if not isinstance(binding, dict) or set(binding) != {'resource','segment_ids'}:
            raise UnsupportedCaptions('Vínculo exige resource e segment_ids')
        identity = _identity(binding['resource'])
        if identity in used_resources or identity not in recognized:
            raise UnsupportedCaptions('Recurso duplicado ou ausente do resultado reconhecido')
        used_resources.add(identity)
        item = recognized[identity]
        if type(item.get('status')) is not int or item['status'] != 0:
            raise UnsupportedCaptions('Recurso vinculado não teve reconhecimento bem-sucedido')
        ids = binding['segment_ids']
        if not isinstance(ids, list) or not ids:
            raise UnsupportedCaptions('Cada recurso exige segmentos vinculados')
        for sid in ids:
            if not isinstance(sid, str) or sid in used_segments or sid not in index:
                raise UnsupportedCaptions('Segmento ausente ou vinculado mais de uma vez')
            used_segments.add(sid)
            segment = index[sid]; attrs = segment.get('attributes', {})
            if (segment.get('type') not in ('VIDEO','AUDIO') or segment.get('parent_id') != root
                    or not isinstance(attrs, dict) or attrs.get('meta_type') == 'photo'):
                raise UnsupportedCaptions('Legenda precisa de segmento de áudio ou vídeo na raiz')
            source = attrs.get('source')
            if identity[0] == 'vid' and source == 'vid://' + identity[1]:
                continue
            proof = proofs.get(sid)
            if (not isinstance(source, str) or not source.startswith('asset://') or not isinstance(proof, dict)
                    or proof.get('source') != source or proof.get('package_id') != package_id
                    or not isinstance(proof.get('evidence'), str) or not proof['evidence'].strip()
                    or _identity(proof.get('resource')) != identity):
                raise UnsupportedCaptions('Identidade da fonte não comprovada para o snapshot; não infira por nome de arquivo')
        utterances = item.get('utterances', [])
        if utterances is None:
            utterances = []
        if not isinstance(utterances, list):
            raise UnsupportedCaptions('Transcrição de recurso incompleta ou inválida')
        normalized = {'utterances':deepcopy(utterances)}
        if identity[0] == 'vid':
            normalized['vid'] = identity[1]
            group = ('vid',)
        else:
            normalized['workspace_id'], normalized['resource_id'] = identity[1], identity[2]
            group = ('workspace', identity[1])
        groups.setdefault(group, []).append((normalized, ids))
    current = deepcopy(draft)
    ids_added, warnings, checks = [], [], []
    if failures:
        warnings.append('Alguns recursos do batch falharam; seus resultados não foram aplicados.')
    if set(recognized) - used_resources:
        warnings.append('O batch contém recursos sem vínculo solicitado; eles não foram aplicados.')
    for group in groups.values():
        batch = [row[0] for row in group]
        table = {(item.get('vid') or item['resource_id']): ids for item, ids in group}
        result = apply_captions(current, batch, bindings=table, layout=layout, text_style=text_style)
        if not isinstance(result, dict) or not isinstance(result.get('draft'), dict) or not isinstance(result.get('added_segment_ids'), list):
            raise ValueError('Builder retornou resultado inválido')
        current = result['draft']
        ids_added.extend(result['added_segment_ids'])
        warnings.extend(result.get('warnings', []))
        checks.append(result.get('check_result'))
    return {'draft':current,'base_package_id':package_id,'added_segment_ids':ids_added,
            'warnings':warnings,'check_results':checks,
            'notice':'Aplicação local; não salva nem confirma reconhecimento visual no CapCut.'}
