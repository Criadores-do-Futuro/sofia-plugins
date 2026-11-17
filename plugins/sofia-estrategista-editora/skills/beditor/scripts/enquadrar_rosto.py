#!/usr/bin/env python3
"""
Transforma o rastreamento do rosto (`rastrear-rosto`) em keyframes de
`object-position` para a faixa de quem fala na tela dividida.

Uso:
  enquadrar_rosto.py rosto.json --video presenter.mp4 [--caixa 1080x1080]
                     [--saida enquadramento.json] [--js]

A caixa do Vision vai da sobrancelha ao queixo; o cabelo sobe cerca de 0,3 da
altura dessa caixa acima dela (medido nos quadros do projeto 08). Por isso a
faixa protegida é `topo - 0,30·h` até `base + 0,05·h`, em duas partes:

- **dura**: sobrancelha → queixo. Se não cabe, o enquadramento não resolve e a
  proporção da tela dividida está errada (`rosto` nas colisões).
- **cabelo**: os 0,30·h de cima. Se só ele não cabe, o quadro mostra o queixo
  inteiro e corta o mínimo de cabelo, e o intervalo entra em `colisoes` como
  `cabelo` — é onde o matte (camada duplicada com o fundo removido, por cima do
  apoio) entra, e só ali (`tela-dividida.md`).

Entre as amostras o rosto não some: lacuna é preenchida pela vizinha, e quem
sai do quadro fica com a última posição até voltar. A trajetória é filtrada
(mediana contra detecção errada, média centrada contra tremor), recolocada
dentro dos limites em que a faixa protegida cabe, e reduzida aos pontos que
mudam o desenho (Ramer-Douglas-Peucker), sem que a reta entre dois keyframes
saia dos limites. Os tweens são lineares (`ease: "none"`): a curva já vem
suavizada, e um `sine.inOut` entre pontos distantes desviaria até um quinto do
salto para fora da faixa conferida. Tremor de poucos pixels num crop parece
erro de câmera; salto parece corte.
"""
import argparse
import json
import math
import sys
from pathlib import Path

CABELO = 0.30      # acima do topo da caixa do Vision, em alturas de rosto
QUEIXO = 0.05      # abaixo da base
JANELA_MEDIANA = 5     # amostras (1,25 s a 0,25 s): mata a detecção isolada
JANELA_MEDIA = 7       # amostras (1,75 s): mata o tremor sem atrasar a volta
TOLERANCIA = 0.5       # pontos percentuais que o desenho pode perder na redução
DIST_MAX = 1.5         # s: acima disso a lacuna é "saiu do quadro", segura a posição


def carregar(caminho):
    dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
    amostras = [a for a in dados if a.get("height", 0) > 0]
    if not amostras:
        raise SystemExit("enquadrar_rosto: nenhum rosto no rastreamento")
    return sorted(amostras, key=lambda a: a["time"])


def geometria(fonte_w, fonte_h, caixa_w, caixa_h):
    """object-fit: cover — escala, e quanto sobra para a posição mover"""
    escala = max(caixa_w / fonte_w, caixa_h / fonte_h)
    sobra_x = fonte_w * escala - caixa_w
    sobra_y = fonte_h * escala - caixa_h
    return escala, sobra_x, sobra_y


def alvo_vertical(amostra, fonte_h, escala, caixa_h, sobra_y, alvo=0.5):
    """(y0 desejado, limite baixo, limite alto, colisao) em px da fonte escalada.
    y0 é o topo da janela visível; a posição em % é y0 / sobra_y."""
    h_px = fonte_h * escala
    face_h = amostra["height"] * h_px
    topo = amostra["top"] * h_px
    base = amostra["bottom"] * h_px
    cabelo = topo - CABELO * face_h
    queixo = base + QUEIXO * face_h
    # a janela [y0, y0 + caixa_h] precisa conter [cabelo, queixo]
    lo, hi = queixo - caixa_h, cabelo
    colisao = None
    if lo > hi:
        # não cabe tudo: o queixo manda, o cabelo cede
        colisao = "cabelo" if queixo - topo <= caixa_h else "rosto"
        lo = hi = queixo - caixa_h
    centro = (cabelo + queixo) / 2
    desejado = centro - alvo * caixa_h
    lo, hi = max(lo, 0.0), min(hi, sobra_y)
    if lo > hi:                      # o próprio quadro acaba antes
        lo = hi = min(max(lo, 0.0), sobra_y)
        colisao = colisao or "borda"
    return min(max(desejado, lo), hi), lo, hi, colisao


def preencher(tempos, valores, t):
    """valor em t pela vizinha: interpola lacuna curta, segura a longa"""
    if t <= tempos[0]:
        return valores[0]
    if t >= tempos[-1]:
        return valores[-1]
    for i in range(1, len(tempos)):
        if tempos[i] >= t:
            a, b = tempos[i - 1], tempos[i]
            if b - a > DIST_MAX:
                return valores[i - 1]       # saiu do quadro: segura
            k = (t - a) / (b - a)
            return valores[i - 1] + (valores[i] - valores[i - 1]) * k
    return valores[-1]


def mediana(vals, janela):
    r = janela // 2
    out = []
    for i in range(len(vals)):
        viz = sorted(vals[max(0, i - r):i + r + 1])
        out.append(viz[len(viz) // 2])
    return out


def media(vals, janela):
    r = janela // 2
    out = []
    for i in range(len(vals)):
        viz = vals[max(0, i - r):i + r + 1]
        out.append(sum(viz) / len(viz))
    return out


def rdp(pontos, tol):
    """Ramer-Douglas-Peucker em (t, p): guarda só o que muda o desenho"""
    if len(pontos) < 3:
        return pontos
    (t0, p0), (t1, p1) = pontos[0], pontos[-1]
    pior, idx = -1.0, 0
    for i in range(1, len(pontos) - 1):
        t, p = pontos[i]
        linha = p0 + (p1 - p0) * (t - t0) / (t1 - t0) if t1 != t0 else p0
        d = abs(p - linha)
        if d > pior:
            pior, idx = d, i
    if pior <= tol:
        return [pontos[0], pontos[-1]]
    return rdp(pontos[:idx + 1], tol)[:-1] + rdp(pontos[idx:], tol)


def _linear(ts, vs, t):
    for i in range(1, len(ts)):
        if ts[i] >= t:
            k = (t - ts[i - 1]) / (ts[i] - ts[i - 1]) if ts[i] != ts[i - 1] else 0
            return vs[i - 1] + (vs[i] - vs[i - 1]) * k
    return vs[-1]


def intervalos(tempos, marcas, passo):
    """junta amostras seguidas com a mesma colisão em [de, ate, tipo]"""
    out = []
    for t, m in zip(tempos, marcas):
        if not m:
            continue
        if out and out[-1]["tipo"] == m and t - out[-1]["ate"] <= passo * 1.5:
            out[-1]["ate"] = round(t + passo, 2)
        else:
            out.append({"de": round(t, 2), "ate": round(t + passo, 2), "tipo": m})
    return out


def enquadrar(amostras, fonte_w, fonte_h, caixa_w, caixa_h, alvo=0.5, passo=0.25,
              duracao=None):
    escala, sobra_x, sobra_y = geometria(fonte_w, fonte_h, caixa_w, caixa_h)
    duracao = duracao if duracao is not None else amostras[-1]["time"] + passo
    tempos_a = [a["time"] for a in amostras]
    calc = [alvo_vertical(a, fonte_h, escala, caixa_h, sobra_y, alvo) for a in amostras]
    n = int(round(duracao / passo)) + 1
    grade = [round(i * passo, 3) for i in range(n)]
    campo = lambda k: [preencher(tempos_a, [c[k] for c in calc], t) for t in grade]
    desejado, lo, hi = campo(0), campo(1), campo(2)
    # o limite vale para a vizinhança: entre duas amostras a cabeça pode ter
    # passado do ponto — o crop respeita o pior caso da janela, não a média
    # a detecção errada também mente sobre os limites: mediana neles antes
    lo, hi = mediana(lo, JANELA_MEDIANA), mediana(hi, JANELA_MEDIANA)
    r = JANELA_MEDIA // 2
    lo_viz = [max(lo[max(0, i - r):i + r + 1]) for i in range(n)]
    hi_viz = [min(hi[max(0, i - r):i + r + 1]) for i in range(n)]
    liso = media(mediana(desejado, JANELA_MEDIANA), JANELA_MEDIA)
    y0 = []
    for v, a, b in zip(liso, lo_viz, hi_viz):
        if a > b:
            a = b = (a + b) / 2
        y0.append(min(max(v, a), b))
    pct = [100.0 * v / sobra_y if sobra_y > 0 else 50.0 for v in y0]
    pontos = rdp(list(zip(grade, pct)), TOLERANCIA)
    # a reta entre dois keyframes não pode sair do que foi conferido: onde sai,
    # o ponto da grade volta a ser keyframe
    lim = [(100.0 * a / sobra_y, 100.0 * b / sobra_y) if sobra_y > 0 else (50.0, 50.0)
           for a, b in zip(lo_viz, hi_viz)]
    while True:
        ts, vs = [t for t, _ in pontos], [v for _, v in pontos]
        fora = [i for i, t in enumerate(grade)
                if not (min(lim[i]) - 0.05 <= _linear(ts, vs, t) <= max(lim[i]) + 0.05)]
        if not fora:
            break
        pontos = sorted(set(pontos) | {(grade[i], pct[i]) for i in fora})
    keyframes = [{"t": round(t, 2), "p": round(p, 1)} for t, p in pontos]
    marcas = [c[3] for c in calc]
    faixa_prot = max((a["bottom"] - a["top"]) * (1 + CABELO + QUEIXO) for a in amostras)
    return {
        "fonte": [fonte_w, fonte_h],
        "caixa": [caixa_w, caixa_h],
        "sobra": [round(sobra_x, 1), round(sobra_y, 1)],
        "amostras": len(amostras),
        "keyframes": keyframes,
        "faixa": [min(k["p"] for k in keyframes), max(k["p"] for k in keyframes)],
        "colisoes": intervalos(tempos_a, marcas, passo),
        # a altura mínima da caixa de quem fala para nunca precisar de matte
        "caixaMinimaPx": math.ceil(faixa_prot * fonte_h * escala) + 2,
    }


def gsap(enq, seletor="#presenter-video", x="50%"):
    k = enq["keyframes"]
    linhas = [f'tl.set("{seletor}", {{ objectPosition: "{x} {k[0]["p"]}%" }}, 0);']
    for a, b in zip(k, k[1:]):
        linhas.append(f'tl.to("{seletor}", {{ objectPosition: "{x} {b["p"]}%", '
                      f'duration: {b["t"] - a["t"]:.2f}, ease: "none" }}, {a["t"]});')
    return "\n".join(linhas)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("rastreamento")
    ap.add_argument("--video", help="o vídeo de quem fala, para ler o tamanho exibido")
    ap.add_argument("--fonte", help="LxA exibido, sem --video (ex.: 1080x1920)")
    ap.add_argument("--caixa", default="1080x1080", help="a região de quem fala, em px")
    ap.add_argument("--alvo", type=float, default=0.5,
                    help="onde o centro da faixa protegida fica na caixa (0 topo, 1 base)")
    ap.add_argument("--duracao", type=float)
    ap.add_argument("--saida")
    ap.add_argument("--js", action="store_true", help="imprime os tweens GSAP")
    a = ap.parse_args()

    if a.video:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import contato
        fw, fh, dur_ms = contato.sonda(a.video)
        duracao = a.duracao or dur_ms / 1000
    elif a.fonte:
        fw, fh = (int(v) for v in a.fonte.lower().split("x"))
        duracao = a.duracao
    else:
        raise SystemExit("enquadrar_rosto: passe --video ou --fonte")
    cw, ch = (int(v) for v in a.caixa.lower().split("x"))
    enq = enquadrar(carregar(a.rastreamento), fw, fh, cw, ch, a.alvo, duracao=duracao)
    texto = json.dumps(enq, indent=2, ensure_ascii=False)
    if a.saida:
        Path(a.saida).write_text(texto + "\n", encoding="utf-8")
    col = enq["colisoes"]
    print(f"enquadrar_rosto: {len(enq['keyframes'])} keyframes · posição "
          f"{enq['faixa'][0]}–{enq['faixa'][1]}% · caixa mínima {enq['caixaMinimaPx']} px",
          file=sys.stderr)
    if col:
        tipos = sorted({c["tipo"] for c in col})
        print(f"enquadrar_rosto: {len(col)} intervalo(s) em que o rosto não cabe "
              f"({', '.join(tipos)}) — ver tela-dividida.md", file=sys.stderr)
    print(gsap(enq) if a.js else (a.saida or texto))


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
