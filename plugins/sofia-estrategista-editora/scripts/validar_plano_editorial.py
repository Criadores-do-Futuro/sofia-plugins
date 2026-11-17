#!/usr/bin/env python3
"""Validação estrutural e editorial do contrato neutro, sem acesso a editores."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:
    print("Dependência ausente: instale requirements-editorial.txt", file=sys.stderr)
    raise SystemExit(2)

SCHEMA = Path(__file__).resolve().parents[1] / "schemas" / "plano-editorial.v1.schema.json"


def _overlaps(a: dict, b: dict) -> bool:
    return max(a["start_ms"], b["start_ms"]) < min(a["end_ms"], b["end_ms"])


def _contains(outer: dict, inner: dict) -> bool:
    return outer["start_ms"] <= inner["start_ms"] and inner["end_ms"] <= outer["end_ms"]


def validate(plan: object) -> list[str]:
    """Retorna erros; lista vazia prova coerência do plano, não execução audiovisual."""
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    structural = sorted(Draft202012Validator(schema).iter_errors(plan), key=lambda e: tuple(map(str, e.absolute_path)))
    if structural:
        return [f"estrutura {'.'.join(map(str, error.absolute_path)) or '<raiz>'}: {error.message}" for error in structural]
    errors: list[str] = []
    for field in ("assets", "protected_speech", "clips", "text_layers"):
        seen = set()
        for item in plan.get(field, []):
            if item["id"] in seen:
                errors.append(f"{field}: id duplicado {item['id']}")
            seen.add(item["id"])
    assets = {asset["id"]: asset for asset in plan["assets"]}
    valid_clips = []
    for clip in plan["clips"]:
        source, timeline = clip["source"], clip["timeline"]
        asset = assets.get(clip["asset_id"])
        if asset is None:
            errors.append(f"clip {clip['id']}: asset inexistente {clip['asset_id']}")
            continue
        if source["end_ms"] <= source["start_ms"] or timeline["end_ms"] <= timeline["start_ms"]:
            errors.append(f"clip {clip['id']}: intervalo vazio ou invertido")
            continue
        if source["end_ms"] > asset["duration_ms"]:
            errors.append(f"clip {clip['id']}: intervalo excede a duração da fonte")
        if source["end_ms"] - source["start_ms"] != timeline["end_ms"] - timeline["start_ms"]:
            errors.append(f"clip {clip['id']}: duração de origem difere da timeline; velocidade variável não suportada nesta versão")
        if clip["kind"] == "audio" and asset["kind"] == "image":
            errors.append(f"clip {clip['id']}: imagem não contém áudio")
        if clip["kind"] == "video" and asset["kind"] == "audio":
            errors.append(f"clip {clip['id']}: áudio não contém imagem")
        if clip.get("speaker_visible") and (clip["kind"] != "video" or asset["kind"] != "video"):
            errors.append(f"clip {clip['id']}: speaker_visible exige imagem de vídeo")
        valid_clips.append(clip)
    for speech in plan["protected_speech"]:
        asset = assets.get(speech["asset_id"])
        source = speech["source"]
        if asset is None:
            errors.append(f"fala {speech['id']}: asset inexistente {speech['asset_id']}")
            continue
        if asset["kind"] == "image":
            errors.append(f"fala {speech['id']}: imagem não contém fala")
        if source["end_ms"] <= source["start_ms"] or source["end_ms"] > asset["duration_ms"]:
            errors.append(f"fala {speech['id']}: intervalo inválido para a fonte")
            continue
        covered = any(c["asset_id"] == speech["asset_id"] and (c["kind"] == "audio" or c.get("carries_source_audio", False)) and _contains(c["source"], source) for c in valid_clips)
        if not covered:
            errors.append(f"fala {speech['id']}: não está integralmente preservada em um clipe de áudio")
    speech_ids = {speech["id"] for speech in plan["protected_speech"]}
    for layer in plan.get("text_layers", []):
        if layer["timeline"]["end_ms"] <= layer["timeline"]["start_ms"]:
            errors.append(f"texto {layer['id']}: intervalo vazio ou invertido")
        if layer.get("speech_id") and layer["speech_id"] not in speech_ids:
            errors.append(f"texto {layer['id']}: fala inexistente {layer['speech_id']}")
        elif layer.get("speech_id"):
            speech = next(s for s in plan["protected_speech"] if s["id"] == layer["speech_id"])
            audible = []
            for clip in valid_clips:
                if clip["asset_id"] != speech["asset_id"] or not (clip["kind"] == "audio" or clip.get("carries_source_audio", False)) or not _contains(clip["source"], speech["source"]):
                    continue
                offset = clip["timeline"]["start_ms"] - clip["source"]["start_ms"]
                audible.append({"start_ms": speech["source"]["start_ms"] + offset, "end_ms": speech["source"]["end_ms"] + offset})
            if audible and not any(_overlaps(layer["timeline"], interval) for interval in audible):
                errors.append(f"texto {layer['id']}: não coincide com a fala na timeline")
    # Sobreposições em pistas separadas permitem J/L cuts. A voz do mesmo trecho
    # não pode ser deslocada enquanto sua boca aparece no mesmo intervalo.
    videos = [c for c in valid_clips if c["kind"] == "video" and c.get("speaker_visible")]
    audios = [c for c in valid_clips if c["kind"] == "audio"]
    for video in videos:
        for audio in audios:
            if audio["asset_id"] != video["asset_id"] or not _overlaps(video["timeline"], audio["timeline"]) or not _overlaps(video["source"], audio["source"]):
                continue
            speech_relevant = any(s["asset_id"] == video["asset_id"] and _overlaps(s["source"], video["source"]) and _overlaps(s["source"], audio["source"]) for s in plan["protected_speech"] if s["source"]["end_ms"] > s["source"]["start_ms"])
            if not speech_relevant:
                continue
            voffset = video["timeline"]["start_ms"] - video["source"]["start_ms"]
            aoffset = audio["timeline"]["start_ms"] - audio["source"]["start_ms"]
            if voffset != aoffset:
                errors.append(f"clipes {video['id']} e {audio['id']}: áudio deslocado enquanto a boca está visível")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validar um plano editorial bEditor v1")
    parser.add_argument("arquivo", type=Path)
    args = parser.parse_args()
    try:
        plan = json.loads(args.arquivo.read_text(encoding="utf-8"))
        errors = validate(plan)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Não foi possível ler o plano: {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"ERRO: {error}", file=sys.stderr)
        return 1
    print("Plano válido. A execução e o resultado audiovisual ainda exigem verificação.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
