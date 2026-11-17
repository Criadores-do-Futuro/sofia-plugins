#!/usr/bin/env python3
"""
mascara.py — a máscara «Dividir» do CapCut: horizontal, com Suavizar.

Pedido do dono em 2026-09-14: *"adicionar o Dividir na máscara, horizontal, com
Suavizar em 30%, assim como fazem no capcut"* — na tela dividida e também no
vídeo dele, *"na parte de cima colocar a máscara de Dividir com Suavizar em 30%
só pra dar uma estética interessante pro vídeo, e isso tem que ser opcional"*.

É **opcional e desligada por padrão**. Liga pelo guia (`guia.mascara`) ou pela
mesa de decupagem, aba Máscara.

O que o Dividir faz: uma linha horizontal parte o clipe em dois; um lado fica,
o outro some. O Suavizar troca a borda seca por uma rampa. Aqui:

  linhaPct      onde a linha cai, em % da altura a partir do topo
  suavizarPct   0–100; a rampa mede `suavizar × metade da altura do quadro`,
                centrada na linha. 30% num quadro de 1920 = 288 px.
  manter        "baixo" (padrão: o de cima some) ou "cima"
  cor           o que aparece onde o clipe some quando não há nada embaixo
                (no CapCut é o fundo preto da pista principal)

Dois lugares usam a mesma conta:

* **vídeo do usuário (solo)** — o A-roll recebe por cima um degradê da `cor`
  que cobre a parte de cima. O motion de tela cheia não recebe: no CapCut a
  máscara é do clipe, não da linha do tempo. Hook e legenda vêm depois, por
  cima, e ganham fundo escuro para ler.
* **tela dividida** — a máscara vai no apoio (o vídeo de cima), com a linha na
  junção. O apoio desce meia rampa sobre quem fala e quem fala sobe meia rampa
  sob o apoio, então a troca é uma dissolução e não existe junção a olho — o
  que a regra de "nenhuma linha visível" (`tela-dividida.md`) já pedia.

A rampa é suave nas duas pontas (smoothstep): rampa linear deixa uma banda de
Mach, e banda de Mach é exatamente a linha que não pode aparecer.

Uso:
  mascara.py png   --largura 1080 --altura 1920 --saida mascara.png [--linha 20 --suavizar 30]
  mascara.py css   --modo solo  [--linha 20 --suavizar 30]
  mascara.py css   --modo split --juncao 840 [--suavizar 30]
"""
import argparse, sys

PADRAO = {
    "ligada": False,
    "tipo": "dividir",
    "orientacao": "horizontal",
    "linhaPct": 20.0,        # solo: a parte de cima escurece sem chegar no rosto
    "suavizarPct": 30.0,     # o número do pedido
    "manter": "baixo",
    "cor": "#000000",
}
ONDE = ("auto", "solo", "split")


def normalizar(cfg):
    """o bloco `mascara` do guia, completo e com os limites conferidos.

    `True` sozinho liga com o padrão; `None`/`False` desliga."""
    if cfg is True:
        cfg = {"ligada": True}
    if not isinstance(cfg, dict):
        return dict(PADRAO)
    m = dict(PADRAO)
    m.update({k: v for k, v in cfg.items() if v is not None})
    m["ligada"] = bool(m.get("ligada"))
    m["linhaPct"] = min(100.0, max(0.0, float(m["linhaPct"])))
    m["suavizarPct"] = min(100.0, max(0.0, float(m["suavizarPct"])))
    if m.get("onde") not in ONDE:
        m["onde"] = "auto"
    return m


def validar(guia):
    """erros em português para `validar.py`. Só reclama do que foi escrito."""
    cfg = guia.get("mascara")
    if cfg is None or isinstance(cfg, bool):
        return []
    if not isinstance(cfg, dict):
        return ["mascara: tem de ser um objeto {ligada, linhaPct, suavizarPct, ...}"]
    erros = []
    if cfg.get("tipo", "dividir") != "dividir":
        erros.append(f"mascara: tipo «{cfg.get('tipo')}» não existe — só «dividir»")
    if cfg.get("orientacao", "horizontal") != "horizontal":
        erros.append("mascara: só a orientação horizontal está implementada")
    if cfg.get("manter", "baixo") not in ("baixo", "cima"):
        erros.append("mascara: `manter` é «baixo» ou «cima»")
    for chave in ("linhaPct", "suavizarPct"):
        v = cfg.get(chave)
        if v is not None and not (isinstance(v, (int, float)) and 0 <= v <= 100):
            erros.append(f"mascara: `{chave}` vai de 0 a 100 (veio {v!r})")
    if cfg.get("onde", "auto") not in ONDE:
        erros.append(f"mascara: `onde` é um de {', '.join(ONDE)}")
    return erros


def rampa_px(altura, suavizar_pct):
    """largura da rampa em px: `suavizar × metade da altura`, par."""
    return int(round(suavizar_pct / 100.0 * altura / 2)) // 2 * 2


def _suave(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


def cobertura(y, altura, cfg):
    """0..1: o quanto a `cor` cobre o pixel na linha `y` (solo)."""
    m = normalizar(cfg)
    linha = m["linhaPct"] / 100.0 * altura
    r = rampa_px(altura, m["suavizarPct"])
    if r == 0:
        visivel = 1.0 if y >= linha else 0.0
    else:
        visivel = _suave((y - (linha - r / 2)) / r)
    if m["manter"] == "cima":
        visivel = 1.0 - visivel
    return 1.0 - visivel


def _hex_rgb(cor):
    c = (cor or "#000000").lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def png(cfg, largura, altura, saida):
    """o degradê do vídeo solo como PNG RGBA, para o ffmpeg sobrepor."""
    import numpy as np
    from PIL import Image
    alfa = np.array([cobertura(y + 0.5, altura, cfg) for y in range(altura)], dtype=np.float32)
    rgba = np.zeros((altura, largura, 4), dtype=np.uint8)
    rgba[..., :3] = _hex_rgb(normalizar(cfg)["cor"])
    rgba[..., 3] = np.round(alfa * 255).astype(np.uint8)[:, None]
    Image.fromarray(rgba, "RGBA").save(saida)
    return saida


def css_solo(cfg, altura=1920):
    """o `background` de uma camada por cima do A-roll em HyperFrames."""
    m = normalizar(cfg)
    r, g, b = _hex_rgb(m["cor"])
    linha = m["linhaPct"] / 100.0 * altura
    rp = rampa_px(altura, m["suavizarPct"])
    ini, fim = linha - rp / 2, linha + rp / 2
    paradas = []
    for k in range(7):
        t = k / 6
        cob = 1.0 - _suave(t)
        if m["manter"] == "cima":
            cob = 1.0 - cob
        paradas.append(f"rgba({r},{g},{b},{cob:.3f}) {ini + (fim - ini) * t:.1f}px")
    return f"linear-gradient(to bottom, {', '.join(paradas)})"


def geometria_split(largura=1080, altura=1920, juncao=840, suavizar_pct=30.0):
    """onde o apoio e quem fala ficam quando a junção é uma máscara suavizada.

    Devolve as caixas em px e a `mask-image` do apoio. `caixaRosto` é o que
    passa para `enquadrar_rosto.py --caixa`: a região de quem fala cresceu
    meia rampa para cima e o enquadramento tem de ser refeito com ela."""
    rp = rampa_px(altura, suavizar_pct)
    meia = rp // 2
    apoio_h = min(altura, juncao + meia)
    rosto_top = max(0, juncao - meia)
    ini = juncao - meia
    paradas = ["#000 0px"]
    for k in range(7):
        t = k / 6
        paradas.append(f"rgba(0,0,0,{1 - _suave(t):.3f}) {ini + rp * t:.1f}px")
    mask = f"linear-gradient(to bottom, {', '.join(paradas)})"
    return {
        "rampaPx": rp,
        "apoio": {"top": 0, "height": apoio_h, "maskImage": mask},
        "rosto": {"top": rosto_top, "height": altura - rosto_top},
        "caixaRosto": f"{largura}x{altura - rosto_top}",
        "css": (f".broll, .apoio {{ top:0; height:{apoio_h}px;"
                f" -webkit-mask-image:{mask}; mask-image:{mask}; }}\n"
                f".presenter, .rosto {{ top:{rosto_top}px; height:{altura - rosto_top}px; }}"),
    }


def ativa_no_solo(plano_ou_guia):
    """a máscara vale para o A-roll deste vídeo?"""
    m = normalizar(plano_ou_guia.get("mascara"))
    return m["ligada"] and m["onde"] in ("auto", "solo")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("png")
    p.add_argument("--largura", type=int, default=1080)
    p.add_argument("--altura", type=int, default=1920)
    p.add_argument("--saida", required=True)
    c = sub.add_parser("css")
    c.add_argument("--modo", choices=["solo", "split"], default="solo")
    c.add_argument("--altura", type=int, default=1920)
    c.add_argument("--largura", type=int, default=1080)
    c.add_argument("--juncao", type=int, default=840)
    for q in (p, c):
        q.add_argument("--linha", type=float, default=PADRAO["linhaPct"])
        q.add_argument("--suavizar", type=float, default=PADRAO["suavizarPct"])
        q.add_argument("--manter", choices=["baixo", "cima"], default="baixo")
        q.add_argument("--cor", default="#000000")
    a = ap.parse_args()
    cfg = {"ligada": True, "linhaPct": a.linha, "suavizarPct": a.suavizar,
           "manter": a.manter, "cor": a.cor}
    if a.cmd == "png":
        png(cfg, a.largura, a.altura, a.saida)
        print(f"mascara: {a.saida} · linha {a.linha:.0f}% · suavizar {a.suavizar:.0f}% "
              f"({rampa_px(a.altura, a.suavizar)} px)")
    elif a.modo == "solo":
        print(f".mascara-dividir {{ position:absolute; inset:0; pointer-events:none;"
              f" background:{css_solo(cfg, a.altura)}; }}")
    else:
        g = geometria_split(a.largura, a.altura, a.juncao, a.suavizar)
        print(g["css"])
        print(f"/* rampa {g['rampaPx']} px · refaça o enquadramento com "
              f"enquadrar_rosto.py --caixa {g['caixaRosto']} */", file=sys.stderr)


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
