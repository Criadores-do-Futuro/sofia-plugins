#!/usr/bin/env python3
"""Mede cada trilha de áudio de um arquivo sem interpretar conteúdo semântico."""
from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
from pathlib import Path
from analisar_audio import _estado_arquivo


def numero(valor):
    try:
        n = float(valor)
        return n if math.isfinite(n) else None
    except (ValueError, TypeError):
        return None


def analisar_todas(fonte: Path, ruido_db: float = -40, minimo: float = .2,
                   timeout: float = 36000) -> dict:
    fonte = fonte.expanduser().resolve(strict=True)
    if not fonte.is_file():
        raise ValueError('A fonte deve ser um arquivo local regular')
    if not math.isfinite(ruido_db) or not -120 <= ruido_db <= 0 or not math.isfinite(minimo) or not .05 <= minimo <= 30 or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError('Limiar, duração mínima ou timeout inválido')
    estado = _estado_arquivo(fonte)
    probe = subprocess.run(['ffprobe','-v','error','-show_entries',
                            'format=duration,start_time:stream=index,codec_type,start_time,duration,channels,sample_rate',
                            '-of','json',str(fonte)],capture_output=True,text=True,check=True,timeout=timeout)
    dados = json.loads(probe.stdout)
    formato = dados.get('format') or {}
    duracao = numero(formato.get('duration'))
    if duracao is None or duracao <= 0:
        raise ValueError('Duração da fonte indisponível')
    inicio_container = numero(formato.get('start_time'))
    saida = {'versao':1,'fonte':str(fonte),'duracao_segundos':duracao,
             'estado_fonte':estado,'limiar_ruido_db':ruido_db,
             'silencio_minimo_segundos':minimo,'trilhas':[],
             'limites':['Níveis e silêncios são medidas, não identificam voz, música, efeitos ou intenção.',
                        'Sem início verificável do contêiner e da trilha, tempos são relativos ao início da trilha.',
                        'Silêncios usam um limiar técnico configurável; revise seu significado no áudio.']}
    for trilha in dados.get('streams', []):
        if trilha.get('codec_type') != 'audio':
            continue
        indice = trilha.get('index')
        if type(indice) is not int or indice < 0:
            raise ValueError('Índice da trilha de áudio ausente')
        inicio_stream = numero(trilha.get('start_time'))
        verificado = inicio_container is not None and inicio_stream is not None
        offset = inicio_stream - inicio_container if verificado else 0.0
        filtro = f'asetpts=PTS-STARTPTS,silencedetect=noise={ruido_db}dB:d={minimo},volumedetect'
        processo = subprocess.run(['ffmpeg','-hide_banner','-nostdin','-nostats','-v','info','-xerror',
                                  '-i',str(fonte),'-map',f'0:{indice}','-vn','-sn','-af',filtro,
                                  '-progress','pipe:1','-f','null','-'],capture_output=True,text=True,
                                 timeout=timeout,check=True)
        tempos = re.findall(r'^out_time_us=(\d+)\s*$', processo.stdout, flags=re.MULTILINE)
        if not tempos or int(tempos[-1]) <= 0:
            raise ValueError(f'Trilha {indice}: duração decodificada não foi reportada')
        dur_audio = int(tempos[-1]) / 1_000_000
        valores = {}
        for atributo in ('mean_volume','max_volume'):
            m = re.search(rf'{atributo}:\s*(-?inf|-?[0-9]+(?:\.[0-9]+)?)\s*dB',processo.stderr)
            if not m:
                raise ValueError(f'Trilha {indice}: {atributo} ausente')
            valores[atributo] = numero(m.group(1))
        silencios, inicio = [], None
        for tipo, raw in re.findall(r'silence_(start|end):\s*(-?[0-9]+(?:\.[0-9]+)?)',processo.stderr):
            tempo = float(raw) + offset
            if tipo == 'start':
                if inicio is not None:
                    raise ValueError(f'Trilha {indice}: silêncio inconsistente')
                inicio = tempo
            else:
                if inicio is None or tempo < inicio:
                    raise ValueError(f'Trilha {indice}: silêncio inconsistente')
                a, b = max(0.,inicio), min(duracao,tempo) if verificado else tempo
                if b > a:
                    silencios.append({'inicio_segundos':round(a,6),'fim_segundos':round(b,6)})
                inicio = None
        if inicio is not None:
            raise ValueError(f'Trilha {indice}: silêncio não finalizado')
        saida['trilhas'].append({'indice_stream':indice,'canais':trilha.get('channels'),
                                 'taxa_amostragem':trilha.get('sample_rate'),
                                 'inicio_segundos':offset,'inicio_verificado':verificado,
                                 'duracao_decodificada_segundos':dur_audio,
                                 'nivel_medio_dbfs':valores['mean_volume'],
                                 'nivel_pico_dbfs':valores['max_volume'],'silencios':silencios})
    if _estado_arquivo(fonte) != estado:
        raise ValueError('A fonte mudou durante a análise')
    return saida


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('fonte',type=Path)
    p.add_argument('--saida',required=True,type=Path)
    p.add_argument('--ruido-db',type=float,default=-40)
    p.add_argument('--silencio-minimo',type=float,default=.2)
    args=p.parse_args()
    try:
        if args.saida.exists() or args.saida.is_symlink():
            raise ValueError("O arquivo de saída já existe")
        resultado=analisar_todas(args.fonte,args.ruido_db,args.silencio_minimo)
        with args.saida.open('x',encoding='utf-8') as f:
            json.dump(resultado,f,ensure_ascii=False,indent=2,allow_nan=False)
            f.write('\n')
    except (OSError,ValueError,subprocess.SubprocessError) as exc:
        print(f'Não foi possível medir as trilhas: {exc}',file=sys.stderr)
        return 1
    print(f"{len(resultado['trilhas'])} trilhas de áudio medidas.")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
