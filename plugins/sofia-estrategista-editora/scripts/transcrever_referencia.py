#!/usr/bin/env python3
"""Transcreve localmente uma trilha com Whisper e um modelo .pt já disponível."""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from analisar_audio import _estado_arquivo


def _numero(value):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        raise ValueError('Tempo inválido na transcrição')
    return float(value)


def _execute(args: list[str], timeout: int) -> str:
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=True)
    except (OSError, subprocess.SubprocessError):
        # Saídas do reconhecedor podem conter dados do usuário; não as publique nos erros.
        raise ValueError('FFmpeg, ffprobe ou Whisper falhou; confira dependências e modelo local') from None
    return p.stdout


def _tempo(registro, offset):
    inicio = _numero(registro.get('start'))
    fim = _numero(registro.get('end'))
    if inicio < 0 or fim < inicio:
        raise ValueError('Intervalo inválido na transcrição')
    return round(inicio + offset, 6), round(fim + offset, 6)


def normalizar(raw: dict, offset: float) -> list[dict]:
    if not isinstance(raw, dict) or not isinstance(raw.get('segments'), list):
        raise ValueError('Formato JSON inesperado do Whisper')
    result = []
    for seg in raw['segments']:
        if not isinstance(seg, dict) or not isinstance(seg.get('text'), str):
            raise ValueError('Segmento inválido')
        inicio, fim = _tempo(seg, offset)
        palavras = []
        wordlist = seg.get('words', [])
        if not isinstance(wordlist, list):
            raise ValueError('Lista de palavras inválida')
        for word in wordlist:
            if not isinstance(word, dict) or not isinstance(word.get('word'), str):
                raise ValueError('Palavra inválida')
            a, b = _tempo(word, offset)
            item = {'texto': word['word'], 'inicio_segundos': a, 'fim_segundos': b}
            prob = word.get('probability')
            if prob is not None:
                prob = _numero(prob)
                if not 0 <= prob <= 1:
                    raise ValueError('Probabilidade de palavra inválida')
                item['probabilidade'] = prob
            palavras.append(item)
        result.append({'texto': seg['text'], 'inicio_segundos': inicio, 'fim_segundos': fim,
                       'palavras': palavras})
    return result


def transcrever(fonte: Path, modelo: Path, indice: int | None = None, idioma: str = 'pt',
                 timeout: int = 36000) -> dict:
    fonte = fonte.expanduser().resolve(strict=True)
    modelo = modelo.expanduser().resolve(strict=True)
    if not fonte.is_file() or not modelo.is_file() or modelo.suffix.lower() != '.pt':
        raise ValueError('São necessários fonte local e arquivo .pt local de modelo Whisper')
    if type(timeout) is not int or timeout <= 0:
        raise ValueError('Tempo limite inválido')
    if not isinstance(idioma, str) or not idioma.isalpha() or not 2 <= len(idioma) <= 8:
        raise ValueError('Idioma inválido')
    if indice is not None and (type(indice) is not int or indice < 0):
        raise ValueError('Índice de trilha inválido')
    before, before_model = _estado_arquivo(fonte), _estado_arquivo(modelo)
    probe = _execute(['ffprobe','-v','error','-show_entries',
                      'format=start_time:stream=index,codec_type,start_time', '-of','json',str(fonte)], 120)
    try:
        meta = json.loads(probe)
        streams = [s for s in meta.get('streams', []) if s.get('codec_type') == 'audio']
        selected = next((s for s in streams if indice is None or s.get('index') == indice), None)
        if selected is None or type(selected.get('index')) is not int:
            raise ValueError('A trilha de áudio solicitada não existe')
        def float_or_none(v):
            try:
                n = float(v)
                return n if math.isfinite(n) else None
            except (ValueError, TypeError):
                return None
        container_start = float_or_none((meta.get('format') or {}).get('start_time'))
        audio_start = float_or_none(selected.get('start_time'))
    except (TypeError, AttributeError, json.JSONDecodeError):
        raise ValueError('Metadados de áudio inválidos') from None
    verified = container_start is not None and audio_start is not None
    offset = audio_start - container_start if verified else 0.0
    with tempfile.TemporaryDirectory(prefix='beditor-transcricao-') as temp:
        folder = Path(temp)
        wav = folder / 'fonte.wav'
        _execute(['ffmpeg','-nostdin','-v','error','-xerror','-i',str(fonte),'-map',f"0:{selected['index']}",
                  '-vn','-ac','1','-ar','16000','-c:a','pcm_s16le','-n',str(wav)], timeout)
        _execute(['whisper',str(wav),'--model',str(modelo),'--device','cpu','--fp16','False',
                  '--language',idioma,'--word_timestamps','True','--output_format','json',
                  '--output_dir',str(folder),'--verbose','False'], timeout)
        path = folder / 'fonte.json'
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            raise ValueError('O Whisper não gerou JSON válido') from None
        segmentos = normalizar(data, offset)
    if _estado_arquivo(fonte) != before or _estado_arquivo(modelo) != before_model:
        raise ValueError('A fonte ou o modelo mudou durante a transcrição')
    return {'versao':1,'fonte':str(fonte),'estado_fonte':before,'modelo_local':str(modelo),
            'idioma_solicitado':idioma,'indice_trilha':selected['index'],
            'referencial_tempos':'container' if verified else 'inicio_da_trilha',
            'deslocamento_segundos':round(offset,6) if verified else None,
            'segmentos':segmentos,
            'limites':['Transcrição automática pode omitir ou inventar palavras; revise escutando.',
                       'Tempos de palavras são estimativas e só aparecem quando fornecidos pelo Whisper.',
                       'Não identifica música, sound effects ou intenção; uma trilha é analisada por vez.']}


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('fonte',type=Path)
    p.add_argument('--modelo',type=Path,required=True,help='Arquivo .pt já existente')
    p.add_argument('--saida',type=Path,required=True)
    p.add_argument('--trilha',type=int,help='Índice absoluto do stream ffprobe; padrão: primeira trilha')
    p.add_argument('--idioma',default='pt')
    args=p.parse_args()
    try:
        if args.saida.exists() or args.saida.is_symlink():
            raise ValueError('Arquivo de saída já existe')
        output=transcrever(args.fonte,args.modelo,args.trilha,args.idioma)
        with args.saida.open('x',encoding='utf-8') as f:
            json.dump(output,f,ensure_ascii=False,indent=2,allow_nan=False)
            f.write('\n')
    except (OSError,ValueError) as exc:
        print(f'Transcrição não concluída: {exc}',file=sys.stderr)
        return 1
    print(f"Transcrição gerada com {len(output['segmentos'])} segmentos; revise a fala e os tempos.")
    return 0

if __name__=='__main__':
    raise SystemExit(main())
