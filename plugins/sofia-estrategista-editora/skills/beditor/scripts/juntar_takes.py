#!/usr/bin/env python3
"""Junta takes SDR num só take.sdr.mov sem desalinhar o som.

O concat com -c copy herda o start_time de cada áudio e o tamanho de cada um:
o som escorrega alguns ms a cada emenda (vídeo 21: 14 ms no take 2). Aqui a
imagem vai por cópia e o som é refeito por take em PCM — deslocado pela
diferença de start_time entre áudio e vídeo e cortado/completado para
exatamente quadros × 1600 amostras (30 fps, 48 kHz).

uso: juntar_takes.py <pasta_brutos> IMG_0004.sdr.mov IMG_0005.sdr.mov ...
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

SR = 48000
FPS = 30
POR_QUADRO = SR // FPS


def _probe(f):
    s = json.loads(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type,start_time,nb_frames", "-of", "json", str(f)],
        capture_output=True, text=True, check=True).stdout)["streams"]
    v = next(x for x in s if x["codec_type"] == "video")
    a = next(x for x in s if x["codec_type"] == "audio")
    return int(v["nb_frames"]), float(a["start_time"]) - float(v["start_time"])


def juntar(pasta, takes):
    pasta = Path(pasta)
    partes, limites, t = [], [], 0
    for nome in takes:
        f = pasta / nome
        n, desvio = _probe(f)
        pcm = np.frombuffer(subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(f), "-map", "0:a:0", "-f", "s16le",
             "-ac", "2", "-ar", str(SR), "-"], capture_output=True, check=True).stdout,
            np.int16).reshape(-1, 2)
        off = int(round(desvio * SR))
        if off > 0:
            pcm = np.vstack([np.zeros((off, 2), np.int16), pcm])
        elif off < 0:
            pcm = pcm[-off:]
        alvo = n * POR_QUADRO
        pcm = pcm[:alvo] if len(pcm) >= alvo else np.vstack(
            [pcm, np.zeros((alvo - len(pcm), 2), np.int16)])
        partes.append(pcm)
        t += n
        limites.append(round(t * 1000 / FPS))
        print(f"{nome}: {n} quadros, som deslocado {off} amostra(s)")
    lista = pasta / "lista.txt"
    lista.write_text("".join(f"file '{x}'\n" for x in takes))
    bruto = pasta / "take.sdr.s16"
    np.vstack(partes).tofile(bruto)
    so_imagem = pasta / "_v.mov"
    subprocess.run(["ffmpeg", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lista),
                    "-map", "0:v:0", "-c", "copy", "-y", str(so_imagem)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(so_imagem), "-f", "s16le", "-ar", str(SR),
                    "-ac", "2", "-i", str(bruto), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "pcm_s16le", "-y", str(pasta / "take.sdr.mov")], check=True)
    so_imagem.unlink()
    bruto.unlink()
    print(f"take.sdr.mov: {t} quadros = {t / FPS:.3f} s; fim de cada take (ms): {limites}")
    return t, limites


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    juntar(sys.argv[1], sys.argv[2:])
