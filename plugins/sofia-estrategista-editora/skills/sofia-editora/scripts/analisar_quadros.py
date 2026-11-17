#!/usr/bin/env python3
"""Mede todos os quadros decodificados, sem inferir efeitos ou intenção."""
import argparse
import json
import math
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', type=Path)
    parser.add_argument('--saida', required=True, type=Path,
                        help='Novo arquivo JSONL para as medições por quadro')
    args = parser.parse_args()
    if not args.video.is_file():
        parser.error('Vídeo não encontrado')
    if args.saida.exists():
        parser.error('O arquivo de saída já existe')

    probe = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                            '-show_entries', 'stream=width,height,avg_frame_rate,nb_frames',
                            '-of', 'json', str(args.video)], capture_output=True, text=True)
    if probe.returncode:
        print('Não foi possível examinar o vídeo.', file=sys.stderr)
        return 1
    streams = json.loads(probe.stdout).get('streams', [])
    if not streams:
        print('O arquivo não contém vídeo.', file=sys.stderr)
        return 1

    command = ['ffmpeg', '-nostdin', '-xerror', '-v', 'error', '-i', str(args.video), '-map', '0:v:0',
               '-vf', 'scdet=threshold=10,signalstats,metadata=mode=print:file=-', '-an', '-fps_mode', 'passthrough',
               '-f', 'null', '-']
    # stderr em arquivo temporário evita deadlock e não mistura logs com medições.
    import tempfile
    count = 0
    missing_pts = 0
    current = None
    with tempfile.TemporaryFile(mode='w+t') as errors, args.saida.open('x', encoding='utf-8') as out:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=errors, text=True)

        def write_frame(frame):
            nonlocal count, missing_pts
            if frame is None:
                return
            if frame.get('pts_segundos') is None:
                missing_pts += 1
            out.write(json.dumps(frame, ensure_ascii=False, allow_nan=False) + '\n')
            count += 1

        try:
            for line in process.stdout:
                line = line.strip()
                if line.startswith('frame:'):
                    write_frame(current)
                    fields = dict(token.split(':', 1) for token in line.split() if ':' in token)
                    try:
                        pts = float(fields.get('pts_time', 'nan'))
                        pts = pts if math.isfinite(pts) else None
                    except ValueError:
                        pts = None
                    current = {'quadro': count, 'pts_segundos': pts}
                elif current is not None and '=' in line:
                    key, value = line.split('=', 1)
                    if key in ('lavfi.signalstats.YAVG', 'lavfi.signalstats.SATAVG', 'lavfi.scd.score'):
                        try:
                            number = float(value)
                            metric = {'lavfi.signalstats.YAVG': 'luma_media',
                                      'lavfi.signalstats.SATAVG': 'saturacao_media',
                                      'lavfi.scd.score': 'pontuacao_mudanca'}[key]
                            current[metric] = number if math.isfinite(number) else None
                        except ValueError:
                            pass
            write_frame(current)
            code = process.wait()
        except BaseException:
            process.kill()
            process.wait()
            raise
        errors.seek(0)
        error_text = errors.read(4096).strip()
        declared = streams[0].get('nb_frames')
        declared = int(declared) if str(declared).isdigit() else None
        summary = {'tipo': 'resumo', 'fonte': str(args.video.resolve()), 'stream': streams[0],
                   'quadros_medidos': count, 'quadros_sem_pts': missing_pts,
                   'processamento_sem_erro': code == 0 and count > 0,
                   'quadros_declarados': declared,
                   'contagem_compativel': count == declared if declared is not None else None,
                   'limites': 'Medições de luma, saturação e mudança visual; não identifica efeitos, cortes confirmados ou áudio.'}
        if code:
            summary['erro_ffmpeg'] = error_text or 'FFmpeg terminou com erro'
        out.write(json.dumps(summary, ensure_ascii=False, allow_nan=False) + '\n')
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if summary['processamento_sem_erro'] and summary['contagem_compativel'] is not False else 1


if __name__ == '__main__':
    sys.exit(main())
