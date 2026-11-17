"""Tira de contatos de uma JANELA do clipe — a segunda pergunta da escolha.

    python3 lupa.py <saida/> <clipe.mp4> <de_s> <ate_s> [passo_s]

O `varrer.py` responde «onde no video», com um quadro por segundo. Esta responde
«em que segundo exatamente», com um quadro a cada 0,4-0,5 s. A segunda pergunta
nao e opcional, e o projeto 15 mediu o preco de pular ela: 84,5 s e 85,2 s do
mesmo trailer sao planos diferentes — um e uma estatua, o outro e o ator — e na
tira grossa os dois caem dentro do mesmo quadro amostrado.

Sao TRES perguntas, nesta ordem, e a terceira nao tem script:

  1. onde no video?      → varrer.py
  2. em que segundo?     → lupa.py
  3. aguenta o quadro?   → o olho, com a regra em `formato-analise.md`
     (interface em modo claro vira retangulo branco num 9:16; diagrama com uma
     duzia de nos nao e «emaranhado»; assunto fora do centro some no painel
     retrato do triptico; 2.39:1 leva tarja para dentro do cartao)

E olhe o ULTIMO quadro da janela, nao so o primeiro: e nele que o cartao congela
quando o trecho da origem acaba antes do cartao.
"""
import io
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def quadro(v, t):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(v),
                        "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
                       capture_output=True)
    return Image.open(io.BytesIO(r.stdout)).convert("RGB") if r.stdout else None


def lupa(v, saida, de, ate, passo=0.5, larg=260, cols=6, maxq=32):
    """Uma folha da janela [de, ate], cada quadro com o segundo escrito."""
    v, saida = Path(v), Path(saida)
    saida.mkdir(parents=True, exist_ok=True)
    de, ate = float(de), float(ate)
    ims, t = [], de
    while t < ate and len(ims) < maxq:
        im = quadro(v, t)
        if im:
            ims.append((im, t))
        t += passo
    if not ims:
        print(f"{v.name}: nenhum quadro lido em [{de}, {ate}]")
        return None

    alt = int(larg * ims[0][0].height / ims[0][0].width)
    lin = (len(ims) + cols - 1) // cols
    fol = Image.new("RGB", (cols * larg, lin * (alt + 20)), (14, 14, 16))
    dr = ImageDraw.Draw(fol)
    try:
        f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 14)
    except Exception:
        f = ImageFont.load_default()
    for i, (im, t) in enumerate(ims):
        x, y = (i % cols) * larg, (i // cols) * (alt + 20)
        fol.paste(im.resize((larg, alt)), (x, y))
        dr.text((x + 5, y + alt + 3), f"{t:.1f}s", fill=(240, 220, 120), font=f)
    p = saida / f"lupa-{v.stem}-{de:g}.jpg"
    fol.save(p, quality=88)
    print(f"{v.name} [{de}–{ate}] → {p.name} {fol.size}")
    return p


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    if len(sys.argv) < 5:
        print(__doc__)
        raise SystemExit(2)
    lupa(sys.argv[2], sys.argv[1], sys.argv[3], sys.argv[4],
         float(sys.argv[5]) if len(sys.argv) > 5 else 0.5)
