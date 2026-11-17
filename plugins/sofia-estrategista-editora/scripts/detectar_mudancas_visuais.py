#!/usr/bin/env python3
"""Resume picos de mudança visual em quadros já analisados.

Produz candidatos para inspeção, não cortes confirmados nem uma análise semântica.
"""
import argparse
import json
import math
import sys
from pathlib import Path


def _numero(x):
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        return False
    try:
        return math.isfinite(x)
    except OverflowError:
        return False


def detectar(arquivo, limiar=10.0):
    if not _numero(limiar) or not 0 < limiar <= 100:
        raise ValueError('O limiar precisa ser maior que zero e no máximo 100')
    total = 0
    ultimo = None
    resumo = None
    grupo = None
    candidatos = []
    with Path(arquivo).open(encoding='utf-8') as entrada:
        for linha in entrada:
            if not linha.strip():
                continue
            item = json.loads(linha, parse_constant=lambda v: (_ for _ in ()).throw(ValueError('número não finito')))
            if not isinstance(item, dict):
                raise ValueError('Linha de medição inválida')
            if item.get('tipo') == 'resumo':
                if resumo is not None:
                    raise ValueError('Resumo duplicado')
                resumo = item
                continue
            if resumo is not None:
                raise ValueError('Quadro depois do resumo')
            indice, t, score = item.get('quadro'), item.get('pts_segundos'), item.get('pontuacao_mudanca')
            if type(indice) is not int or indice != total:
                raise ValueError('Sequência de quadros incompleta ou fora de ordem')
            if not _numero(t) or (ultimo is not None and t < ultimo):
                raise ValueError('Tempos ausentes ou fora de ordem')
            if not _numero(score) or not 0 <= score <= 100:
                raise ValueError('Pontuação de mudança ausente ou inválida')
            if score >= limiar:
                if grupo is None:
                    grupo = {'inicio_segundos': t, 'fim_segundos': t, 'pico_segundos': t,
                             'pico_pontuacao': score, 'quadros': 1}
                else:
                    grupo['fim_segundos'] = t
                    grupo['quadros'] += 1
                    if score > grupo['pico_pontuacao']:
                        grupo['pico_segundos'], grupo['pico_pontuacao'] = t, score
            elif grupo is not None:
                candidatos.append(grupo)
                grupo = None
            total += 1
            ultimo = t
    if grupo is not None:
        candidatos.append(grupo)
    if (not isinstance(resumo, dict) or resumo.get('processamento_sem_erro') is not True
            or (resumo.get('contagem_compativel') is not None and resumo.get('contagem_compativel') is not True) or total == 0
            or type(resumo.get('quadros_medidos')) is not int or resumo['quadros_medidos'] != total
            or type(resumo.get('quadros_sem_pts')) is not int or resumo['quadros_sem_pts'] != 0 or not isinstance(resumo.get('fonte'), str)
            or not resumo['fonte'].strip()):
        raise ValueError('Resumo ausente ou análise incompleta')
    return {'versao': 1, 'fonte': resumo['fonte'], 'quadros_analisados': total,
            'limiar_pontuacao': limiar, 'candidatos': candidatos,
            'limites': ['Picos indicam mudança visual; movimento, flashes e efeitos podem causar falsos positivos.',
                        'Transições graduais e cortes sutis podem não ser detectados; revise a imagem e o áudio.',
                        'A análise de origem não registra um hash do arquivo; verifique se a fonte não mudou.']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('quadros', type=Path, help='JSONL gerado pelo analisador de quadros')
    p.add_argument('--saida', required=True, type=Path)
    p.add_argument('--limiar', type=float, default=10.0)
    a = p.parse_args()
    try:
        resultado = detectar(a.quadros, a.limiar)
        with a.saida.open('x', encoding='utf-8') as saida:
            json.dump(resultado, saida, ensure_ascii=False, indent=2, allow_nan=False)
            saida.write('\n')
    except (OSError, ValueError, TypeError) as exc:
        print('Não foi possível detectar mudanças visuais: ' + str(exc), file=sys.stderr)
        return 1
    print(f"{len(resultado['candidatos'])} candidatos para revisão visual.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
