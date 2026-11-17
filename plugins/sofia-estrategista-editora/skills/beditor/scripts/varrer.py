"""Tira de contatos de um clipe de acervo — para escolher o trecho pelo que ele
MOSTRA, e nao pelo que o titulo promete.

    python3 varrer.py <saida/> <clipe.mp4> [clipe2.mp4 ...]

Foi assim que dois inserts errados passaram para o master no projeto 14: eu
confiei no titulo ("PlayStation Retail Store", "Purchasing With A Card") e
peguei um segundo qualquer. Um dos clipes nao tinha console em quadro naquele
trecho; o outro nao tinha cartao em NENHUM dos seus 21 segundos — era outro
video. O titulo descreve o video, e as vezes nem isso. So o quadro descreve o
trecho.

Olhe a tira ANTES de fixar `src` e `dur`, e procure tres coisas:

  1. o VERBO da frase acontecendo (comprando ≠ fazer fila; jogando ≠ comprar)
  2. timecode, marca d'agua ou legenda QUEIMADOS — entram no cartao, e o
     `sem_tarja` nao os tira, porque nao sao tarja: sao imagem
  3. a fonte ser mesmo o que o titulo dizia
"""
import io
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def duracao(v):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(v)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return float(r.stdout.strip())


def quadro(v, t):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(v),
                        "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
                       capture_output=True)
    return Image.open(io.BytesIO(r.stdout)).convert("RGB") if r.stdout else None


def tira(v, saida, passo=None, larg=200, cols=8, maxq=32):
    """Uma folha com ate `maxq` quadros do clipe, cada um com o segundo escrito."""
    v = Path(v)
    d = duracao(v)
    passo = passo or max(1.0, d / 24)
    ims, t = [], 0.0
    while t < d - 0.5 and len(ims) < maxq:
        im = quadro(v, t)
        if im:
            ims.append((im, t))
        t += passo
    if not ims:
        print(f"{v.name}: nenhum quadro lido")
        return None

    alt = int(larg * ims[0][0].height / ims[0][0].width)
    lin = (len(ims) + cols - 1) // cols
    fol = Image.new("RGB", (cols * larg, lin * (alt + 18)), (14, 14, 16))
    dr = ImageDraw.Draw(fol)
    try:
        f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 12)
    except Exception:
        f = ImageFont.load_default()
    for i, (im, t) in enumerate(ims):
        x, y = (i % cols) * larg, (i // cols) * (alt + 18)
        fol.paste(im.resize((larg, alt)), (x, y))
        dr.text((x + 4, y + alt + 3), f"{t:.1f}s", fill=(230, 226, 220), font=f)

    p = Path(saida) / f"tira-{v.stem}.jpg"
    p.parent.mkdir(parents=True, exist_ok=True)
    fol.save(p, quality=86)
    print(f"{v.name}  {d:.1f}s  →  {p}  {fol.size[0]}x{fol.size[1]}")
    return p


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    if len(sys.argv) < 3:
        print(__doc__)
        raise SystemExit(2)
    for c in sys.argv[2:]:
        tira(c, sys.argv[1])
