"""Prepara, sem executar, uma montagem posicionada para o MCP do Resolve.

As taxas, os IDs da media pool e o mapa de pistas devem vir de uma consulta atual
no editor. O resultado é um plano de chamadas, não comprova montagem salva.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Any

from scripts.validar_plano_editorial import validate


class UnsupportedResolvePlan(ValueError):
    """O plano não pode ser convertido sem perder ou inventar informação."""


def _fps(value: Any) -> Fraction:
    try:
        if isinstance(value, bool):
            raise ValueError()
        rate = Fraction(str(value))
        if rate <= 0 or rate > 240:
            raise ValueError()
        return rate
    except (ValueError, TypeError, ZeroDivisionError):
        raise UnsupportedResolvePlan(f'Taxa de quadros inválida: {value!r}') from None


def _frame(ms: int, rate: Fraction, field: str) -> int:
    value = Fraction(ms, 1000) * rate
    if value.denominator != 1:
        raise UnsupportedResolvePlan(f'{field}: {ms} ms não coincide com quadro à taxa {rate}; ajuste o plano antes de montar')
    return int(value)


def translate(plan: dict, media: dict[str, dict], tracks: dict[str, int], timeline_fps: str) -> dict:
    """Retorna argumentos para media_pool.append_to_timeline, sem chamar o editor.

    media associa cada asset a {clip_id, source_fps}; tracks associa os nomes de
    pista do plano aos índices de 1 a N do respectivo tipo (video/audio). Tempos
    de origem são em quadros da fonte; posições da timeline usam taxa da timeline.
    O contrato interno usa intervalos semiabertos que devem coincidir com quadros.
    A interpretação de end_frame pelo Resolve ainda precisa ser verificada antes
    de usar estes argumentos numa timeline real.
    """
    errors = validate(plan)
    if errors:
        raise UnsupportedResolvePlan('Plano inválido: ' + '; '.join(errors))
    if plan['project']['editor'] != 'davinci':
        raise UnsupportedResolvePlan('O plano precisa selecionar DaVinci Resolve')
    if plan.get('text_layers'):
        raise UnsupportedResolvePlan('Legendas e lettering ainda não são traduzidos para Resolve')
    if not plan['clips']:
        raise UnsupportedResolvePlan('Nenhum clipe no plano')
    rate = _fps(timeline_fps)
    assets = {asset['id']: asset for asset in plan['assets']}
    rows = []
    intervals: dict[tuple[str, int], list[tuple[int, int]]] = {}
    for clip in plan['clips']:
        if assets[clip['asset_id']]['kind'] == 'image':
            raise UnsupportedResolvePlan('Imagens estáticas ainda não têm duração traduzida com segurança')
        if clip.get('carries_source_audio'):
            raise UnsupportedResolvePlan('Áudio vinculado automático não mapeado: declare áudio como clipe em pista independente')
        item = media.get(clip['asset_id'])
        if not isinstance(item, dict) or not isinstance(item.get('clip_id'), str) or not item['clip_id'].strip() or 'source_fps' not in item:
            raise UnsupportedResolvePlan(f"{clip['asset_id']}: informe ID da media pool e taxa de quadros da fonte")
        track = tracks.get(clip['track'])
        if isinstance(track, bool) or not isinstance(track, int) or track < 1:
            raise UnsupportedResolvePlan(f"{clip['track']}: informe índice de pista válido")
        source_rate = _fps(item['source_fps'])
        start = _frame(clip['source']['start_ms'], source_rate, clip['id'] + ' origem início')
        end = _frame(clip['source']['end_ms'], source_rate, clip['id'] + ' origem fim')
        record = _frame(clip['timeline']['start_ms'], rate, clip['id'] + ' timeline início')
        record_end = _frame(clip['timeline']['end_ms'], rate, clip['id'] + ' timeline fim')
        key = clip['kind'], track
        for prior_start, prior_end in intervals.setdefault(key, []):
            if max(prior_start, record) < min(prior_end, record_end):
                raise UnsupportedResolvePlan(f"{clip['id']}: sobreposição na mesma pista do Resolve")
        intervals[key].append((record, record_end))
        rows.append({'clip_id': item['clip_id'], 'start_frame': start, 'end_frame': end,
                     'record_frame': record, 'track_index': track,
                     'media_type': 1 if clip['kind'] == 'video' else 2})
    return {'tool': 'media_pool', 'action': 'append_to_timeline',
            'params': {'clip_infos': rows},
            'warnings': ['Prévia não validada em timeline real: confirme a interpretação de end_frame e a duração com as taxas da fonte e timeline antes de executar.', 'Consulte o projeto e as pistas atuais e verifique a timeline e o áudio após a execução.']}
