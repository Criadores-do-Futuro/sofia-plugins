"""Sincronia de IMAGEM do master contra a montagem, pela energia de movimento.

    python3 scripts/conferir_movimento.py <projeto>            # guia/out/preview.mp4 x edicao/aroll.mp4
    python3 scripts/conferir_movimento.py <projeto> <arquivo>  # qualquer arquivo x edicao/aroll.mp4

Por que existe (vídeos 19 e 20, 2026-09-27): o master saiu com a imagem até
5 quadros atrás da voz, e os testes de imagem por diferença de quadro não
viram — no master a imagem tem grade de cor e zoom, e comparar pixel com a
montagem crua dá correlação plana. A energia de movimento (quanto a imagem
muda de um quadro para o próximo) não liga para cor nem para escala: o gesto
é o mesmo. Janelas de 10 s, lag de -8 a +8 quadros; a janela só vale se o pico
passa de 0,5 e ganha do segundo pico por mais de 0,05. Controle: a prévia
aprovada do 20 deu 0 nas 26 janelas.

Sai com código 1 se alguma janela válida tiver lag diferente de 0, ou se
nenhuma janela for válida.
"""
import subprocess, sys
from pathlib import Path
import numpy as np

JANELA, LAG = 300, 8


def movimento(arq):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(arq), "-an", "-vf",
                        "scale=36:64,format=gray", "-f", "rawvideo", "-"],
                       capture_output=True, check=True).stdout
    v = np.frombuffer(r, np.uint8).astype(np.float32).reshape(-1, 64, 36)
    return np.abs(np.diff(v, axis=0)).mean(axis=(1, 2))


def _z(x):
    return (x - x.mean()) / (x.std() + 1e-6)


def lags(final, montagem):
    A, B = movimento(final), movimento(montagem)
    out = []
    for s in range(LAG, min(len(A), len(B)) - JANELA - LAG, JANELA):
        a = _z(A[s:s + JANELA])
        cc = {k: float(np.mean(a * _z(B[s + k:s + k + JANELA]))) for k in range(-LAG, LAG + 1)}
        melhor = max(cc, key=cc.get)
        segundo = sorted(cc.values())[-2]
        if cc[melhor] > 0.5 and cc[melhor] - segundo > 0.05:
            out.append(melhor)
    return len(A) + 1, len(B) + 1, out


if __name__ == "__main__":
    projeto = Path(sys.argv[1])
    final = Path(sys.argv[2]) if len(sys.argv) > 2 else projeto / "guia" / "out" / "preview.mp4"
    qa, qb, ls = lags(final, projeto / "edicao" / "aroll.mp4")
    print("quadros final/montagem:", qa, qb)
    print("janelas válidas:", len(ls), "lags:", ls)
    pior = max(map(abs, ls)) if ls else None
    print("pior:", pior if ls else "-")
    sys.exit(0 if ls and pior == 0 else 1)
