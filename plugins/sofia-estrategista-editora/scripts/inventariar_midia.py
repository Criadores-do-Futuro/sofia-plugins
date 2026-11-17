#!/usr/bin/env python3
"""Identifica mídia local e registra metadados, sem copiar ou alterar a origem."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone


def inventariar(path: Path, origem: str | None = None, licenca: str | None = None) -> dict:
    path = path.resolve(strict=True)
    if not path.is_file():
        raise ValueError('A origem precisa ser um arquivo regular.')
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(chunk)
    probe = subprocess.run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)],
                           capture_output=True, text=True, check=True)
    metadata = json.loads(probe.stdout)
    if not metadata.get('streams'):
        raise ValueError('Arquivo não contém fluxos de mídia reconhecidos.')
    return {'versao': 1, 'arquivo': str(path), 'bytes': path.stat().st_size,
            'sha256': digest.hexdigest(), 'origem_informada': origem,
            'licenca_informada': licenca, 'inventariado_em': datetime.now(timezone.utc).isoformat(),
            'ffprobe': metadata}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('arquivo', type=Path)
    parser.add_argument('--saida', required=True, type=Path)
    parser.add_argument('--origem', help='URL ou descrição da fonte, conforme informada')
    parser.add_argument('--licenca', help='Licença informada; não é uma verificação de direitos')
    args = parser.parse_args()
    try:
        result = inventariar(args.arquivo, args.origem, args.licenca)
        with args.saida.open('x', encoding='utf-8') as dest:
            json.dump(result, dest, ensure_ascii=False, indent=2)
            dest.write('\n')
    except (OSError, ValueError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        print(f'Não foi possível inventariar: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
