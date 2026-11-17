#!/usr/bin/env python3
"""Acrescenta observações fornecidas a uma nova versão de um manual validado.

O comando não interpreta imagens ou áudio, nem atesta que as observações são
verdadeiras. O responsável pela análise deve fornecer evidências temporais.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from validar_manual_estilo import validar


def enriquecer(manual: object, observacoes: object) -> dict:
    erros = validar(manual)
    if erros:
        raise ValueError('Manual de origem inválido: ' + '; '.join(erros))
    if not isinstance(observacoes, list) or not observacoes:
        raise ValueError('Informe uma lista não vazia de observações')
    resultado = copy.deepcopy(manual)
    resultado['observacoes'].extend(copy.deepcopy(observacoes))
    erros = validar(resultado)
    if erros:
        raise ValueError('Observações inválidas: ' + '; '.join(erros))
    return resultado


def carregar(caminho: Path):
    def constante_invalida(valor):
        raise ValueError('Número JSON não finito: ' + valor)
    with caminho.open(encoding='utf-8') as f:
        return json.load(f, parse_constant=constante_invalida)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('manual', type=Path, help='Manual de estilo v1 de origem')
    p.add_argument('--observacoes', required=True, type=Path, help='Arquivo JSON contendo uma lista de observações')
    p.add_argument('--saida', required=True, type=Path, help='Novo manual, sem sobrescrever o original')
    args = p.parse_args()
    try:
        if args.saida.exists() or args.saida.is_symlink():
            raise ValueError('A saída já existe')
        resultado = enriquecer(carregar(args.manual), carregar(args.observacoes))
        texto = json.dumps(resultado, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
        with args.saida.open('x', encoding='utf-8') as f:
            f.write(texto)
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        print(f'Manual não atualizado: {exc}', file=sys.stderr)
        return 1
    print('Novo manual gerado; a validade estrutural não comprova a observação audiovisual.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
