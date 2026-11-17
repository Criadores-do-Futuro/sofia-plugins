#!/usr/bin/env python3
"""Cria um manual inicial com as medições disponíveis de uma ou mais referências."""
import argparse
import json
import math
import sys
from pathlib import Path

from validar_manual_estilo import validar


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('quadros', nargs='+', type=Path, help='JSONL produzido pelo analisador de quadros')
    parser.add_argument('--duracao', action='append', type=float, required=True, help='Duração verificada da referência em segundos')
    parser.add_argument('--nome', required=True)
    parser.add_argument('--saida', type=Path, required=True)
    args = parser.parse_args()
    if len(args.quadros) != len(args.duracao) or any(not math.isfinite(v) or v <= 0 for v in args.duracao) or not args.nome.strip():
        parser.error('Informe nome e uma duração positiva finita para cada referência')
    if args.saida.exists():
        parser.error('O arquivo de saída já existe')
    try:
        references, observations = [], []
        for indice, (arquivo, duracao) in enumerate(zip(args.quadros, args.duracao), 1):
            ref_id = f'ref-{indice}'
            count, previous, summary = 0, None, None
            totals = {'luma_media': 0.0, 'saturacao_media': 0.0}
            with arquivo.open(encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue
                    frame = json.loads(line, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
                    if frame.get('tipo') == 'resumo':
                        if summary is not None:
                            raise ValueError('Resumo duplicado')
                        summary = frame
                        continue
                    if summary is not None:
                        raise ValueError('Quadro depois do resumo')
                    time = frame.get('pts_segundos')
                    if not isinstance(time, (int, float)) or isinstance(time, bool) or not math.isfinite(time) or time < 0 or time > duracao:
                        raise ValueError('Tempo ausente ou fora da duração informada')
                    if previous is not None and time < previous:
                        raise ValueError('Tempos dos quadros fora de ordem')
                    previous = time
                    for key in totals:
                        value = frame.get(key)
                        if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
                            raise ValueError('Medição ausente ou inválida: ' + key)
                        totals[key] += value
                    count += 1
            if (not summary or not summary.get('processamento_sem_erro') or
                    summary.get('contagem_compativel') is False or not count or
                    summary.get('quadros_medidos') != count or summary.get('quadros_sem_pts') != 0):
                raise ValueError('Medições incompletas ou sem tempos suficientes')
            metrics = {key: value / count for key, value in totals.items()}
            source = summary['fonte']
            if not isinstance(source, str) or not source.strip():
                raise ValueError('Fonte ausente no resumo')
            references.append({'id': ref_id, 'fonte': source, 'duracao_segundos': duracao})
            evidence = [{'referencia_id': ref_id, 'inicio_segundos': 0,
                         'fim_segundos': duracao, 'modalidade': 'video',
                         'nota': 'Média dos quadros decodificados; não é interpretação visual.'}]
            observations.extend([
                {'id': f'luma-{indice}', 'aspecto': 'luminância média', 'estado': 'medido',
                 'descricao': 'Média de YAVG na escala do filtro signalstats do FFmpeg.',
                 'valor': round(metrics['luma_media'], 3), 'evidencias': evidence},
                {'id': f'saturacao-{indice}', 'aspecto': 'saturação média', 'estado': 'medido',
                 'descricao': 'Média de SATAVG na escala do filtro signalstats do FFmpeg.',
                 'valor': round(metrics['saturacao_media'], 3), 'evidencias': evidence},
            ])
        for index, aspect in enumerate(('cortes', 'J-cut', 'legendas e fontes', 'lettering', 'zoom e câmera',
                                        'transições e máscaras', 'som e efeitos sonoros'), 1):
            observations.append({'id': f'pendente-{index}', 'aspecto': aspect, 'estado': 'indisponivel',
                                 'descricao': 'Requer análise específica e evidência audiovisual.', 'evidencias': []})
        manual = {'versao': 1, 'nome': args.nome, 'referencias': references, 'observacoes': observations}
        errors = validar(manual)
        if errors:
            raise ValueError('; '.join(errors))
        with args.saida.open('x', encoding='utf-8') as f:
            json.dump(manual, f, ensure_ascii=False, indent=2, allow_nan=False)
            f.write('\n')
    except (OSError, ValueError, KeyError, TypeError, IndexError, json.JSONDecodeError) as exc:
        print('Não foi possível gerar o manual: ' + str(exc), file=sys.stderr)
        return 1
    print('Manual inicial criado; os aspectos não medidos exigem análise adicional.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
