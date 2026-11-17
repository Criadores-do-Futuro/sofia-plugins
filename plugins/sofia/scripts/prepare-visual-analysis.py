#!/usr/bin/env python3
'Prepara amostras visuais locais sem chave de API.'
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse

MESSAGES = {'description': 'Prepara amostras visuais locais sem chave de API.', 'arguments': 'argumentos', 'options': 'opções', 'input': 'Arquivo de vídeo ou endereço HTTPS autorizado', 'output': 'Pasta nova e vazia para os resultados', 'max_frames': 'Limite de quadros, de 1 a 1000', 'start': 'Segundo inicial', 'end': 'Segundo final', 'allow_download': 'Autoriza baixar uma referência pública que a pessoa pode utilizar', 'bad_frames': 'O limite de quadros deve ficar entre 1 e 1000.', 'bad_window': 'Janela inválida: use tempos finitos, não negativos e fim posterior ao início.', 'bad_input': 'Arquivo inexistente ou endereço público não permitido.', 'download_required': 'Downloads exigem --allow-download; prefira o arquivo fornecido pela pessoa.', 'missing': 'Dependências ausentes: ', 'not_empty': 'A pasta de saída precisa estar vazia para evitar dados de outra análise.', 'download_failed': 'Não foi possível baixar. Se houver login, peça o arquivo; não use cookies.', 'bad_video': 'O arquivo precisa ter uma faixa de vídeo e duração válida.', 'no_frames': 'Não foi possível relacionar os quadros aos tempos decodificados.', 'sampling': 'Amostragem de quadros; não representa observação contínua nem transcrição da fala.', 'no_audio': 'Não foi possível extrair o áudio.', 'silent': 'O vídeo não tem faixa de áudio.', 'no_contacts': 'Sem folhas de contato; abra os quadros em ordem.', 'failed': 'Falha na preparação. Confira o arquivo, as permissões e as dependências.'}
SUB_LANGS = 'pt.*,pt'


def execute(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=True, capture_output=True, text=True, stdin=subprocess.DEVNULL)


def main() -> int:
    parser = argparse.ArgumentParser(description=MESSAGES['description'])
    parser._positionals.title = MESSAGES['arguments']
    parser._optionals.title = MESSAGES['options']
    parser.add_argument('input', help=MESSAGES['input'])
    parser.add_argument('--output', help=MESSAGES['output'])
    parser.add_argument('--max-frames', type=int, default=80, help=MESSAGES['max_frames'])
    parser.add_argument('--start', type=float, default=0.0, help=MESSAGES['start'])
    parser.add_argument('--end', type=float, help=MESSAGES['end'])
    parser.add_argument('--allow-download', action='store_true', help=MESSAGES['allow_download'])
    args = parser.parse_args()
    if not 1 <= args.max_frames <= 1000:
        parser.error(MESSAGES['bad_frames'])
    if not math.isfinite(args.start) or args.start < 0 or (args.end is not None and not math.isfinite(args.end)):
        parser.error(MESSAGES['bad_window'])
    source = Path(args.input).expanduser()
    remote = not source.is_file()
    if remote:
        url = urlparse(args.input)
        allowed = ('youtube.com', 'youtu.be', 'instagram.com', 'tiktok.com')
        host = (url.hostname or '').lower()
        if url.scheme != 'https' or url.username or url.password or not any(host == d or host.endswith('.' + d) for d in allowed):
            parser.error(MESSAGES['bad_input'])
        if not args.allow_download:
            parser.error(MESSAGES['download_required'])
    required = ['ffmpeg', 'ffprobe'] + (['yt-dlp'] if remote else [])
    missing = [name for name in required if not shutil.which(name)]
    if missing:
        parser.error(MESSAGES['missing'] + ', '.join(missing))
    root = Path(args.output).expanduser().resolve() if args.output else Path(tempfile.mkdtemp(prefix='sofia-visual-'))
    if root.is_relative_to(Path(__file__).resolve().parents[1]):
        parser.error('A saída deve ficar fora da instalação do plugin.')
    if root.exists() and any(root.iterdir()):
        parser.error(MESSAGES['not_empty'])
    root.mkdir(parents=True, exist_ok=True)
    if remote:
        try:
            execute(['yt-dlp', '--ignore-config', '--no-playlist', '--no-progress',
                     '--write-auto-subs', '--write-subs', '--sub-langs', SUB_LANGS,
                     '--sub-format', 'vtt/best', '--merge-output-format', 'mp4',
                     '-f', 'bv*+ba/b', '-o', str(root / 'video.%(ext)s'), '--', args.input])
        except subprocess.CalledProcessError:
            raise RuntimeError(MESSAGES['download_failed']) from None
        videos = [p for p in root.glob('video.*') if p.suffix.lower() in {'.mp4', '.webm', '.mkv', '.mov'}]
        if len(videos) != 1:
            raise RuntimeError(MESSAGES['download_failed'])
        source = videos[0]
    source = source.resolve()
    info = json.loads(execute(['ffprobe', '-v', 'error', '-show_entries',
                              'format=duration:stream=index,codec_type,codec_name,width,height,r_frame_rate',
                              '-of', 'json', str(source)]).stdout)
    source_duration = float(info.get('format', {}).get('duration', 0))
    if not math.isfinite(source_duration) or source_duration <= 0 or not any(s.get('codec_type') == 'video' for s in info.get('streams', [])):
        raise RuntimeError(MESSAGES['bad_video'])
    end = min(source_duration, args.end) if args.end is not None else source_duration
    if end <= args.start:
        raise RuntimeError(MESSAGES['bad_window'])
    duration = end - args.start
    interval = duration / args.max_frames
    for folder in ['frames', 'contacts']:
        (root / folder).mkdir()
    timing = ['-ss', str(args.start), '-t', str(duration)]
    frame_filter = f"select='isnan(prev_selected_t)+gte(t-prev_selected_t,{interval:.9f})',scale='min(960,iw)':-2,showinfo"
    sampled = execute(['ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'info', *timing, '-i', str(source),
                       '-vf', frame_filter, '-fps_mode', 'vfr', '-frames:v', str(args.max_frames),
                       '-q:v', '3', str(root / 'frames/t-%05d.jpg')])
    times = [float(t) for t in re.findall(r'\bn:\s*\d+.*?\bpts_time:([\d.eE+\-]+)', sampled.stderr)]
    frames = sorted((root / 'frames').glob('*.jpg'))
    if not frames or len(times) != len(frames):
        raise RuntimeError(MESSAGES['no_frames'])
    audio = None
    limitations = [MESSAGES['sampling']]
    if any(s.get('codec_type') == 'audio' for s in info.get('streams', [])):
        try:
            execute(['ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error', *timing, '-i', str(source),
                     '-vn', '-ac', '1', '-ar', '16000', '-c:a', 'libmp3lame', '-b:a', '64k', str(root / 'audio.mp3')])
            audio = str(root / 'audio.mp3')
        except subprocess.CalledProcessError:
            limitations.append(MESSAGES['no_audio'])
    else:
        limitations.append(MESSAGES['silent'])
    try:
        execute(['ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error', '-framerate', '1',
                 '-i', str(root / 'frames/t-%05d.jpg'), '-vf', 'scale=240:-2,tile=5x4:padding=8:margin=8',
                 '-frames:v', str(math.ceil(len(frames) / 20)), str(root / 'contacts/timeline-%03d.jpg')])
    except subprocess.CalledProcessError:
        limitations.append(MESSAGES['no_contacts'])
    manifest = {'video': str(source), 'audio': audio, 'duration_seconds': duration,
                'source_duration_seconds': source_duration, 'window_start_seconds': args.start,
                'window_end_seconds': end, 'sample_interval_seconds': interval,
                'timestamp_basis': 'decoded_frame_pts_plus_window_start',
                'frames': [{'path': str(p), 'seconds': round(args.start + t, 6)} for p, t in zip(frames, times)],
                'contact_sheets': [str(p) for p in sorted((root / 'contacts').glob('*.jpg'))],
                'limitations': limitations}
    (root / 'metadata.json').write_text(json.dumps(info, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (root / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(root)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        # A saída externa pode conter caminhos privados; informe apenas o resumo.
        print(str(error) if isinstance(error, RuntimeError) else MESSAGES['failed'], file=sys.stderr)
        raise SystemExit(1)
