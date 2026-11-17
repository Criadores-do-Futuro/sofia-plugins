"""Compara um plano Resolve com um retrato de timeline; não edita o projeto."""
from __future__ import annotations

from typing import Any
from beditor.davinci_plan import translate, _fps, _frame


class ResolvePreflightError(ValueError):
    """Não há evidência suficiente para preparar uma inserção segura."""


def prepare(plan: dict, media: dict, tracks: dict, timeline_fps: str, snapshot: dict[str, Any]) -> dict:
    """Prepara os argumentos e rejeita colisões com o retrato completo da timeline.

    snapshot exige timeline_id, version_token e complete=True informados pelo
    chamador e items com kind, track_index, start_frame e end_frame exclusivos,
    relativos ao início da timeline. Não verifica que o retrato seja atual nem
    garante que a escrita será aceita. Não salva nem executa chamadas MCP.
    """
    if (not isinstance(snapshot, dict) or snapshot.get('complete') is not True
            or not isinstance(snapshot.get('timeline_id'), str) or not snapshot['timeline_id'].strip()
            or not isinstance(snapshot.get('version_token'), str) or not snapshot['version_token'].strip()
            or not isinstance(snapshot.get('items'), list)):
        raise ResolvePreflightError('Retrato completo, identificação da timeline e versão são obrigatórios')
    existing = []
    for item in snapshot['items']:
        if not isinstance(item, dict):
            raise ResolvePreflightError('Item existente inválido')
        kind, track = item.get('kind'), item.get('track_index')
        start, end = item.get('start_frame'), item.get('end_frame')
        if (kind not in ('video', 'audio') or type(track) is not int or track < 1
                or type(start) is not int or start < 0 or type(end) is not int or end <= start):
            raise ResolvePreflightError('Faixa ou intervalo existente inválido')
        existing.append((kind, track, start, end))
    result = translate(plan, media, tracks, timeline_fps)
    rate = _fps(timeline_fps)
    for clip in plan['clips']:
        start = _frame(clip['timeline']['start_ms'], rate, clip['id'] + ' início')
        end = _frame(clip['timeline']['end_ms'], rate, clip['id'] + ' fim')
        track = tracks[clip['track']]
        if any(kind == clip['kind'] and existing_track == track and max(start, left) < min(end, right)
               for kind, existing_track, left, right in existing):
            raise ResolvePreflightError(f"Clipe {clip['id']} colide com um item da timeline existente")
    return {'timeline_id': snapshot['timeline_id'], 'version_token': snapshot['version_token'],
            'prepared': result,
            'warnings': ['O retrato precisa ser atualizado imediatamente antes da execução; não há bloqueio de edição concorrente.',
                         'Uma chamada bem-sucedida não prova persistência: salve e confira os itens novamente após salvar.',
                         'Nenhuma operação foi enviada ao DaVinci Resolve.']}
