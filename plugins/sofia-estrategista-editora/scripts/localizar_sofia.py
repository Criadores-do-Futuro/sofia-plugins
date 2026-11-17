#!/usr/bin/env python3
"""Localiza a ficha de um formato e os princípios da Sofia, sem copiar nada.

Sem --acervo, usa SOFIA_ACERVO_DIR, depois BEDITOR_SOFIA_DIR e, por fim, as fichas
que vêm no próprio plugin (skills/sofia-estrategista).
"""
import argparse
import json
import os
import sys
from pathlib import Path

ACERVO_DO_PLUGIN = Path(__file__).resolve().parents[1] / 'skills' / 'sofia-estrategista'


def acervo_padrao(ambiente=None) -> Path:
    ambiente = os.environ if ambiente is None else ambiente
    for chave in ('SOFIA_ACERVO_DIR', 'BEDITOR_SOFIA_DIR'):
        if ambiente.get(chave):
            return Path(ambiente[chave])
    return ACERVO_DO_PLUGIN


def localizar(root: Path, formato: str) -> dict:
    root = root.expanduser().resolve(strict=True)
    if not formato or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in formato):
        raise ValueError('Informe o nome da ficha em minúsculas, com hífens.')
    principles = root / 'references' / 'principios.md'
    sheet = root / 'references' / 'formatos' / (formato + '.md')
    for path in (principles, sheet):
        if not path.is_file() or not path.resolve().is_relative_to(root):
            raise ValueError(f'Ficha ausente ou fora do acervo: {path}')
    return {'principios': str(principles.resolve()), 'formato': str(sheet.resolve())}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('formato', help='Ex.: dinamismo, tela-dividida')
    p.add_argument('--acervo', help='Pasta com references/principios.md e references/formatos/')
    a = p.parse_args()
    acervo = Path(a.acervo) if a.acervo else acervo_padrao()
    try:
        print(json.dumps(localizar(acervo, a.formato), ensure_ascii=False, indent=2))
    except (ValueError, OSError) as exc:
        print(f'Não foi possível localizar as fichas: {exc}', file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
