#!/usr/bin/env python3
"""Acrescenta indícios de fala ao manual com base em transcrição local revisável.

O texto não é incorporado por padrão; a opção explícita também inclui palavras
estimadas. Uma transcrição não comprova fala, nem caracteriza sound effects.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import sys
from pathlib import Path
from analisar_audio import _estado_arquivo
from validar_manual_estilo import validar


def _num(valor):
    return not isinstance(valor, bool) and isinstance(valor, (int, float)) and math.isfinite(valor)


def incorporar(manual: object, transcricao: object, referencia_id: str,
               incluir_texto: bool = False) -> dict:
    erros = validar(manual)
    if erros:
        raise ValueError('Manual inválido: ' + '; '.join(erros))
    if not isinstance(transcricao, dict) or type(transcricao.get('versao')) is not int or transcricao['versao'] != 1:
        raise ValueError('Transcrição inválida ou de versão não suportada')
    if not isinstance(referencia_id, str):
        raise ValueError('ID de referência inválido')
    refs = [ref for ref in manual['referencias'] if ref['id'] == referencia_id]
    if len(refs) != 1:
        raise ValueError('Referência não encontrada no manual')
    ref = refs[0]
    fonte = Path(ref['fonte']).resolve(strict=True)
    if not isinstance(transcricao.get('fonte'), str) or Path(transcricao['fonte']).resolve() != fonte:
        raise ValueError('A transcrição pertence a outra fonte')
    if transcricao.get('estado_fonte') != _estado_arquivo(fonte):
        raise ValueError('A fonte mudou desde a transcrição')
    if transcricao.get('referencial_tempos') != 'container' or not _num(transcricao.get('deslocamento_segundos')):
        raise ValueError('Não é possível associar os tempos à referência: início da trilha não verificado')
    indice = transcricao.get('indice_trilha')
    if type(indice) is not int or indice < 0:
        raise ValueError('Índice da trilha inválido')
    segmentos = transcricao.get('segmentos')
    if not isinstance(segmentos, list):
        raise ValueError('Lista de segmentos inválida')
    resultado = copy.deepcopy(manual)
    novos = []
    ultimo = 0.0
    for i, seg in enumerate(segmentos, 1):
        if not isinstance(seg, dict) or not isinstance(seg.get('texto'), str) or not seg['texto'].strip():
            raise ValueError('Segmento de texto inválido')
        inicio, fim = seg.get('inicio_segundos'), seg.get('fim_segundos')
        if not _num(inicio) or not _num(fim) or inicio < 0 or fim < inicio or inicio < ultimo or fim > ref['duracao_segundos']:
            raise ValueError('Tempos de segmento inválidos ou fora da referência')
        ultimo = inicio
        palavras = seg.get('palavras')
        if not isinstance(palavras, list):
            raise ValueError('Lista de palavras inválida')
        anteriores = inicio
        for palavra in palavras:
            if not isinstance(palavra, dict) or not isinstance(palavra.get('texto'), str):
                raise ValueError('Palavra inválida')
            a, b = palavra.get('inicio_segundos'), palavra.get('fim_segundos')
            if not _num(a) or not _num(b) or a < inicio - .05 or b > fim + .05 or b < a or a < anteriores - .05 or a < 0 or b > ref['duracao_segundos']:
                raise ValueError('Tempos de palavra inválidos ou fora do segmento')
            anteriores = a
            prob = palavra.get('probabilidade')
            if prob is not None and (not _num(prob) or not 0 <= prob <= 1):
                raise ValueError('Probabilidade de palavra inválida')
        obs = {'id': f'transcricao-{referencia_id}-{indice}-{i}',
               'aspecto': 'trecho de fala identificado por transcrição automática',
               'estado': 'inferido',
               'descricao': 'Whisper estimou fala neste intervalo; confirme palavras e sincronismo escutando.',
               'evidencias': [{'referencia_id': referencia_id, 'inicio_segundos': inicio,
                              'fim_segundos': fim, 'modalidade': 'audio',
                              'nota': f'Trilha {indice}, segmento {i}; transcrição automática sujeita a erro.'}]}
        if incluir_texto:
            # Copia apenas campos conhecidos; evita propagar dados inesperados do JSON.
            obs['valor'] = {'texto': seg['texto'], 'palavras': [
                {k: w[k] for k in ('texto', 'inicio_segundos', 'fim_segundos', 'probabilidade') if k in w}
                for w in palavras]}
        novos.append(obs)
    if not novos:
        novos.append({'id': f'transcricao-{referencia_id}-{indice}-sem-segmentos',
                      'aspecto': 'transcrição automática', 'estado': 'indisponivel',
                      'descricao': 'O reconhecedor não retornou segmentos; isso não prova ausência de fala.',
                      'evidencias': []})
    resultado['observacoes'].extend(novos)
    erros = validar(resultado)
    if erros:
        raise ValueError('Manual resultante inválido: ' + '; '.join(erros))
    return resultado


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('manual', type=Path)
    p.add_argument('transcricao', type=Path)
    p.add_argument('--referencia', required=True)
    p.add_argument('--saida', type=Path, required=True)
    p.add_argument('--incluir-texto', action='store_true', help='Inclui fala e palavras no manual; podem ser dados privados')
    args = p.parse_args()
    try:
        if args.saida.exists() or args.saida.is_symlink():
            raise ValueError('Arquivo de saída já existe')
        def ler(path):
            with path.open(encoding='utf-8') as f:
                return json.load(f, parse_constant=lambda v: (_ for _ in ()).throw(ValueError('Número não finito')))
        resultado = incorporar(ler(args.manual), ler(args.transcricao), args.referencia, args.incluir_texto)
        serialized = json.dumps(resultado, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
        with args.saida.open('x', encoding='utf-8') as f:
            f.write(serialized)
    except (OSError, UnicodeError, ValueError, TypeError, OverflowError) as exc:
        print(f'Manual não atualizado: {exc}', file=sys.stderr)
        return 1
    print('Novo manual criado com inferências temporais; revise ouvindo a referência.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
