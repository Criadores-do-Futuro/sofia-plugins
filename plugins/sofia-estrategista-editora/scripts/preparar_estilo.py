#!/usr/bin/env python3
"""Prepara medições, transcrição opcional e cadastro local de um estilo.

O resultado é um ponto de partida técnico, não uma análise semântica completa.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from analisar_referencias_estilo import preparar, gravar
from transcrever_referencia import transcrever
from adicionar_transcricao_ao_manual import incorporar
from biblioteca_estilos import ErroBiblioteca, cadastrar_estilo, pasta_do_estilo


def executar(videos: list[Path], nome: str, identificador: str, analise: Path,
             biblioteca: Path, modelo: Path | None = None) -> dict:
    destino = pasta_do_estilo(biblioteca, identificador)
    if destino.exists() or destino.is_symlink():
        raise ValueError('Já existe um estilo com esse identificador')
    if analise.exists() or analise.is_symlink():
        raise ValueError('A pasta de análise já existe')
    registro = preparar(videos, nome, analise)
    manual_path = analise / 'manual.json'
    if modelo is not None:
        manual = json.loads(manual_path.read_text(encoding='utf-8'))
        for i, video in enumerate(videos, 1):
            trilhas = json.loads((analise / f'ref-{i}-trilhas-audio.json').read_text(encoding='utf-8'))
            if not trilhas['trilhas']:
                continue
            transcricao = transcrever(video, modelo)
            gravar(analise / f'ref-{i}-transcricao.json', transcricao)
            manual = incorporar(manual, transcricao, f'ref-{i}')
        manual_path = analise / 'manual-com-transcricao.json'
        gravar(manual_path, manual)
    estilo = cadastrar_estilo(biblioteca, id_estilo=identificador, nome=nome,
                             manual=str(manual_path), capa=str(analise / 'capa.jpg'))
    return {'id': identificador, 'nome': nome, 'analise': str(analise.resolve()),
            'biblioteca': str(biblioteca.resolve()), 'manual': estilo['manual']['arquivo'],
            'capa': estilo['capa']['arquivo'],
            'limites': registro['limites'] + ['As transcrições e observações exigem revisão audiovisual.']}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('videos', nargs='+', type=Path)
    p.add_argument('--nome', required=True)
    p.add_argument('--id', required=True)
    p.add_argument('--analise', required=True, type=Path, help='Pasta nova para arquivos de análise')
    p.add_argument('--biblioteca', required=True, type=Path)
    p.add_argument('--modelo', type=Path, help='Modelo Whisper .pt já existente; opcional')
    a = p.parse_args()
    try:
        resultado = executar(a.videos, a.nome, a.id, a.analise, a.biblioteca, a.modelo)
    except (OSError, ValueError, RuntimeError, ErroBiblioteca) as exc:
        print(f'Preparação incompleta: {exc}. Se a pasta de análise foi criada, pode conter resultados parciais.', file=sys.stderr)
        return 1
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
