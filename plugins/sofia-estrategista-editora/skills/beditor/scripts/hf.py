#!/usr/bin/env python3
"""
hf.py — renderiza os planos de motion em HyperFrames (HTML + GSAP + SVG).

Por que existe: o treinamento (2.623 + 222 frames lidos por categoria) descreve
o COMO FAZER em tecnologia web — reticulado meio-tom em `mix-blend-mode`,
revelacao por track matte, paralaxe com `perspective`, barra de scanner, curvas
`power4.out`. Nada disso existe em Pillow. Este modulo escreve o HTML de cada
plano na gramatica do treino e chama `npx hyperframes render`.

A gramatica nao foi inventada aqui: ela esta nos `index.html` renderizados de
`guia-claude-hyperframes/exemplos/` e nas regras do `PROMPT-MESTRE-CLAUDE.md`.
As quatro que mais mudam o resultado, e que a primeira versao deste arquivo
nao tinha:

  1. A CAMERA NUNCA PARA. Todo plano vive dentro de um rig 3D com
     `perspective` e `preserve-3d`, e a camera anda em Z e gira alguns
     decimos de grau em Y e X do primeiro ao ultimo quadro. Um `scale`
     plano nao substitui isso: sem paralaxe entre camadas, o quadro parece
     um slide.
  2. TRACK MATTE. Texto nao aparece com fade: ele sobe de dentro de uma
     caixa com `overflow:hidden`, de 140% ate 0, em `power4.out`,
     escalonado 0,2 s entre linhas.
  3. AS CAMADAS TEM PROFUNDIDADE. Fundo em Z -250, sujeito em Z +40,
     tipografia em Z +140, bokeh em Z +280. E dai que vem a paralaxe.
  4. TIPOGRAFIA NO TERCO SUPERIOR, sujeito no terco medio/inferior, com as
     zonas seguras de 160 px em cima e 320 px embaixo.

O compositor em Pillow (`compor.py`) continua valendo e nao foi removido: e o
caminho de conserto quando o navegador falha, e o unico que roda sem Node.

Uso:
  hf.py --projeto edicao/motion --out out/motion.mp4
  hf.py --projeto edicao/motion --so M12          (um plano so, para revisar)
  hf.py --projeto edicao/motion --so-html         (escreve os HTML, nao renderiza)
"""
import argparse, hashlib, html, json, math, os, random, shutil, subprocess, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import estilos, hf_vox, hf_gravacao, hf_ilustrativo  # noqa: E402

FPS = 30

# ---------- tokens do estilo de motion escolhido --------------------------
# Eles NAO sao mais fixos: vem da galeria (`estilos.MOTION`, medida nos corpus
# de treinamento) e `aplicar_estilo()` troca todos de uma vez. O padrao da casa
# e `vox`; `noturno` traz de volta exatamente os numeros medidos nos 2.623
# frames do canal (MATRIZ-12-ESTILOS-VISUAIS.md + PROMPT-MESTRE-CLAUDE.md).
FUNDO = SUPERFICIE = TEXTO = TEXTO_2 = ""
CARTAO = JANELA = JANELA_BARRA = BORDA = CENTRO = HALO = SOMBRA_TEXTO = ""
CARTAO_VIVO = CARTAO_FRACO = PAINEL = CROMO = BOLHA = BOLHA_EU = ""
SOMBRA_CAMADA = ""
AMBAR = CIANO = DESTAQUE = ACIDO = NEGADO = NEON = NEON_2 = ""
FONTE_TITULO = FONTE_LEITURA = FONTE_MONO = ""
ESTILO_ATUAL = None
ACABAMENTO = {}

# A camera padrao da casa: push-in em Z com alguns decimos de grau de rotacao.
# Um estilo pode trocar a sua em `estilos.MOTION[...]["camera"]` — o `gravacao`
# troca, porque ali nao existe camera: o que empurra e o canvas, em escala
# digital, e meio grau de rotateY sobre um branco liso denuncia o rig 3D.
CAMERA_PADRAO = {"de": "{z:-160, rotateY:-3, rotateX:2}",
                 "para": "{z:120, rotateY:2.5, rotateX:-1.5}", "ease": "none"}
CAMERA = dict(CAMERA_PADRAO)


def aplicar_estilo(nome=None):
    """troca a paleta e as fontes do modulo inteiro pelo estilo escolhido.

    As composicoes montam o HTML com f-string na hora da chamada, entao trocar
    os globais aqui basta — nao ha token copiado em lugar nenhum."""
    global ESTILO_ATUAL, ACABAMENTO, CAMERA
    escolhido = estilos.escolher({"estilos": {"motion": nome}} if nome else None, "motion")
    globals().update(estilos.MOTION[escolhido]["tokens"])
    ACABAMENTO = estilos.acabamento(escolhido)
    CAMERA = dict(CAMERA_PADRAO, **(estilos.MOTION[escolhido].get("camera") or {}))
    ESTILO_ATUAL = escolhido
    return escolhido


aplicar_estilo()   # o modulo nunca fica sem paleta; main() reaplica a do plano

# zonas seguras do 9:16 (TikTok/Reels cobrem o topo e a base)
SEGURO_TOPO, SEGURO_BASE = 160, 320

GOOGLE_FONTS = ("https://fonts.googleapis.com/css2?family=Anton&family=Archivo+Black"
                # o `ilustrativo` pede didone com italico (o subtitulo em
                # serifa minuscula italica) e uma grotesca condensada com
                # algarismo tabular para rotulo de dado — dai Playfair 900,
                # o eixo italico, e Oswald
                "&family=Playfair+Display:ital,wght@0,600;0,800;0,900;1,600;1,800"
                "&family=Oswald:wght@400;500;600"
                "&family=Courier+Prime:wght@400;700"
                "&family=Inter:wght@400;700;900"
                "&family=JetBrains+Mono:wght@400;500;700&family=Fraunces:opsz,wght@9..144,600"
                "&display=swap")

# entrada/saida do guia -> como o PLANO INTEIRO entra e sai (ritmo.md). Fica no
# `#palco`, nunca no `#camera`: animar a mesma propriedade nos dois faz os
# tweens brigarem, e o motor de captura mostra a briga como tremor.
ENTRADAS = {
    "corte":    (None, None),
    "deslizar": ("{opacity:0,x:70}", "{opacity:1,x:0}"),
    "subir":    ("{opacity:0,y:80}", "{opacity:1,y:0}"),
    "escalar":  ("{opacity:0,scale:0.92}", "{opacity:1,scale:1}"),
}
SAIDAS = {"corte", "varrer", "empurrar", "implodir", "apagar"}


def _e(t):
    return html.escape(str(t or ""), quote=True)


# ---------- pecas da gramatica --------------------------------------------

def _tag(texto):
    """metadado tecnico em mono, entre colchetes — abre quase toda cena do
    treino e da a ela o ar de leitura de instrumento."""
    if not texto:
        return ""
    return f'<div class="tag-mono">[ {_e(str(texto).upper())} ]</div>'


def _bate(alvo, i, linha):
    """`alvo` pode ser um indice, o proprio texto, ou uma lista de qualquer um
    dos dois. `True`/`False` nao batem aqui: quem chama e que sabe o que True
    significa naquele tipo de plano."""
    if alvo is None or isinstance(alvo, bool):
        return False
    if isinstance(alvo, (list, tuple, set)):
        return any(_bate(a, i, linha) for a in alvo)
    if isinstance(alvo, int):
        return alvo == i
    return bool(str(alvo).strip()) and linha.strip().lower() == str(alvo).strip().lower()


def _matte(linhas, acesa=None, classe="matte-text", riscadas=None):
    """track matte: cada linha mora numa caixa que corta, e sobe de 140% ate 0.
    `acesa` (indice ou texto) recebe o amarelo de assinatura.

    `riscadas` existe porque a fala nega com frequencia — "elas NAO sao
    inteligentes" — e escrever a palavra limpa na tela inverte o sentido do que
    esta sendo dito. O risco e desenhado no tempo da negacao, nao antes."""
    saida = []
    for i, l in enumerate(linhas):
        cls = f"{classe} destaque" if _bate(acesa, i, l) else classe
        risco = ""
        if _bate(riscadas, i, l):
            cls += " riscado"
            risco = '<i class="risco"></i>'
        saida.append(f'<div class="matte-box"><span class="{cls}">{_e(l)}{risco}</span></div>')
    return "\n".join(saida)


JS_RISCO = ("tl.to('.risco', {width:'104%', duration:0.38, ease:'power2.inOut',"
            " stagger:0.34}, 0.85);")


JS_MATTE = ("gsap.set('.matte-text', {yPercent:140});"
            "tl.to('.matte-text', {yPercent:0, duration:0.55, ease:'power4.out',"
            " stagger:0.2}, 0.35);")

CSS_TIPOGRAFIA = f"""
  .tipografia {{ position:absolute; top:{SEGURO_TOPO + 40}px; left:0; width:100%;
    padding:0 70px; text-align:center; transform:translateZ(140px); }}
  .tipografia.baixa {{ top:auto; bottom:{SEGURO_BASE + 20}px; }}
  /* quando o texto E o sujeito (nao ha figura no meio), ele ocupa o quadro */
  .tipografia.centro {{ top:{SEGURO_TOPO}px; bottom:{SEGURO_BASE}px; left:0; right:0;
    width:auto; display:flex; flex-direction:column; justify-content:center; }}
  .tipografia.centro .matte-text {{ font-size:118px; }}
  .tag-mono {{ font-family:{FONTE_MONO}; font-size:24px; color:{TEXTO_2};
    letter-spacing:0.25em; text-transform:uppercase; margin-bottom:26px; }}
  .matte-box {{ overflow:hidden; display:block; margin:4px 0; }}
  .matte-text {{ font-family:{FONTE_TITULO}; font-size:92px; line-height:1.05;
    letter-spacing:-0.02em; text-transform:uppercase; display:block; color:{TEXTO};
    text-shadow:0 4px 22px {SOMBRA_TEXTO}; position:relative; }}
  .matte-text.riscado {{ color:{TEXTO_2}; }}
  .risco {{ position:absolute; left:-2%; top:52%; height:7px; width:0;
    background:{NEGADO}; border-radius:4px; box-shadow:0 0 18px {NEGADO}; }}
  .matte-text.destaque {{ color:{DESTAQUE};
    text-shadow:0 0 38px {HALO}, 0 4px 20px {SOMBRA_TEXTO}; }}
  .divisor {{ width:0; height:3px; background:{DESTAQUE}; margin:38px auto 0;
    box-shadow:0 0 15px {DESTAQUE}; }}
"""

JS_DIVISOR = "tl.to('.divisor', {width:160, duration:0.6, ease:'expo.out'}, 0.9);"


def _bloco_tipografia(linhas, tag=None, classe="tipografia"):
    """o terco de texto sobre a figura. Sem linha nenhuma nao existe bloco: uma
    etiqueta mono sozinha no alto de um quadro vazio parece sujeira, nao design."""
    if not linhas:
        return ""
    return f"""
      <div class="{classe}">
        {_tag(tag)}
        {_matte(linhas, len(linhas) - 1)}
      </div>"""


def _linhas_de(p, maximo=3):
    """as linhas de titulo do plano, venham de `texto` ou de `palavras`"""
    t = (p.get("texto") or "").strip()
    if t:
        return [l.strip() for l in t.split("\n") if l.strip()][:maximo]
    return [str(w).strip() for w in (p.get("palavras") or [])][:maximo]


# ---------- corpo por tipo -------------------------------------------------

def _palavras(p):
    """acumulo tipografico. As ja ditas ficam como fantasma pequeno no alto; as
    novas sobem em track matte, grandes. `acender` marca a que nunca foi dita —
    ela chega em amarelo. Aceita a palavra em si ou `true` (acende a ultima)."""
    itens = [str(w).strip() for w in (p.get("palavras") or [])]
    fant = [str(w).strip() for w in (p.get("fantasmas") or [])]
    ac = p.get("acender")
    if ac is True:
        acesa = itens[-1] if itens else None
    elif isinstance(ac, str) and ac.strip():
        acesa = ac.strip()
    else:
        acesa = None

    # `riscar: true` risca todas: e o caso "elas nao sao inteligentes, nao
    # raciocinam, nao aprendem" — a lista inteira e negada pela fala.
    ri = p.get("riscar")
    riscar = itens if ri is True else ri

    fantasmas = ""
    if fant:
        fantasmas = ('<div class="fantasmas">'
                     + " ".join(f'<span>{_e(w)}</span>' for w in fant)
                     + "</div>")
    corpo = f"""
      <div class="camada fundo"><div class="grade"></div></div>
      <div class="camada frente">
        <i class="bokeh" style="width:150px;height:150px;top:300px;left:90px"></i>
        <i class="bokeh" style="width:230px;height:230px;bottom:340px;right:70px"></i>
      </div>
      <div class="tipografia centro">
        {fantasmas}
        {_matte(itens, acesa, riscadas=riscar)}
        <div class="divisor"></div>
      </div>"""
    css = f"""
      .fantasmas {{ display:flex; flex-wrap:wrap; gap:10px 22px; justify-content:center;
        margin-bottom:34px; }}
      .fantasmas span {{ font-family:{FONTE_MONO}; font-size:30px; color:{TEXTO_2};
        opacity:0.42; letter-spacing:0.1em; text-transform:uppercase; }}
    """
    js = (JS_MATTE + JS_DIVISOR
          + "tl.from('.fantasmas span', {opacity:0, y:14, duration:0.4,"
            " stagger:0.05, ease:'power2.out'}, 0.1);"
          + (JS_RISCO if riscar else ""))
    return corpo, css, js


def _rng(semente):
    """aleatorio semeado pelo id do plano: as mesmas estrelas em todo render.
    O motor captura quadro a quadro reposicionando a timeline — qualquer sorteio
    no tempo de render daria um ceu diferente a cada quadro."""
    return random.Random(f"beditor:{semente}")


CORES_ESTRELA = ("#FFFFFF", "#CFE2FF", "#FFE7C4", "#9FD8FF", "#FFD1A8")

# lugares fixos para os vertices nomeados, em fracao do quadro. Sao poucos e
# espalhados de proposito: palavra sobre palavra vira sopa.
SLOTS = ((0.28, 0.30), (0.72, 0.25), (0.17, 0.56), (0.81, 0.60),
         (0.47, 0.43), (0.33, 0.77), (0.71, 0.81), (0.52, 0.66))


def _slots(palavras):
    """o lugar de cada palavra no ceu sai do nome dela, nao da ordem em que
    aparece. Sem isso CACHORRO estaria num canto num plano e no outro no plano
    seguinte, e a galaxia deixaria de ser o mesmo lugar de um corte para o
    outro — que e justamente o que ela precisa ser."""
    usados, saida = set(), []
    for w in palavras:
        i = int(hashlib.md5(w.strip().upper().encode()).hexdigest()[:8], 16) % len(SLOTS)
        while i in usados:
            i = (i + 1) % len(SLOTS)
        usados.add(i)
        saida.append(SLOTS[i])
    return saida


def _campo(rng, n, z0, z1, t0, t1, o0, o1):
    """uma casca de estrelas. A profundidade e o que faz a paralaxe: sem Z
    diferente entre as cascas, a camera so daria zoom num papel de parede."""
    saida = []
    for _ in range(n):
        x, y = rng.uniform(-16, 116), rng.uniform(-12, 112)
        z, t = rng.uniform(z0, z1), rng.uniform(t0, t1)
        o, cor = rng.uniform(o0, o1), rng.choice(CORES_ESTRELA)
        saida.append(
            f'<i class="es" style="left:{x:.2f}%;top:{y:.2f}%;width:{t:.1f}px;'
            f'height:{t:.1f}px;opacity:{o:.2f};background:{cor};'
            f'box-shadow:0 0 {t*3.2:.0f}px {cor};transform:translateZ({z:.0f}px)"></i>')
    return "".join(saida)


def _curva(pontos):
    """Catmull-Rom convertida em cubicas: a rota passa POR cada vertice, sem
    bico nas junções. Devolve o `d` do path, a amostragem e o comprimento."""
    if len(pontos) < 2:
        return "", list(pontos), 0.0
    p = [pontos[0]] + list(pontos) + [pontos[-1]]
    d = f"M {pontos[0][0]:.1f} {pontos[0][1]:.1f}"
    amostras, comp = [pontos[0]], 0.0
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += (f" C {c1[0]:.1f} {c1[1]:.1f}, {c2[0]:.1f} {c2[1]:.1f},"
              f" {p2[0]:.1f} {p2[1]:.1f}")
        for k in range(1, 15):
            t = k / 14
            u = 1 - t
            x = u**3 * p1[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t**3 * p2[0]
            y = u**3 * p1[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t**3 * p2[1]
            comp += math.hypot(x - amostras[-1][0], y - amostras[-1][1])
            amostras.append((x, y))
    return d, amostras, comp


def _galaxia(p, W=1080, H=1920):
    """O plano que faltava. Quando a fala diz galaxia, vertice e rota, escrever
    a palavra GALAXIA na tela e desistir da imagem: o espectador ja ouviu a
    palavra, o que ele nao tem e o desenho.

    Aqui o quadro e um ceu de verdade em tres cascas de profundidade, as
    palavras da fala sao vertices acesos nesse ceu, e a rota entre elas e
    tracada por dentro — em `voo`, na velocidade de quem atravessa."""
    g = p.get("galaxia") or {}
    itens = [str(w).strip() for w in (p.get("palavras") or [])][:len(SLOTS)]
    modo = g.get("modo") or ("rota" if len(itens) >= 2 else "campo")
    rng = _rng(p.get("id", "M00"))

    cascas = ('<div class="nebulosa"><i class="nb a"></i><i class="nb b"></i></div>'
              f'<div class="casca longe">{_campo(rng, 320, -1100, -620, 1.4, 3.2, .30, .75)}</div>'
              f'<div class="casca media">{_campo(rng, 170, -520, -160, 2.4, 5.0, .45, .95)}</div>'
              f'<div class="casca perta">{_campo(rng, 42, 60, 300, 5.0, 12.0, .30, .65)}</div>')

    pontos = [(x * W, y * H) for x, y in _slots(itens)]
    vertices = "".join(
        f'<div class="vt" style="left:{x:.0f}px;top:{y:.0f}px">'
        f'<i class="nucleo"></i><span class="rotulo">{_e(w)}</span></div>'
        for w, (x, y) in zip(itens, pontos))

    d, amostras, comp = _curva(pontos)
    linhas = ""
    if len(pontos) >= 2:
        seq = " ".join(f"{x:.0f},{y:.0f}" for x, y in pontos)
        linhas = (f'<polyline class="constelacao" points="{seq}"/>'
                  f'<path class="rota" d="{d}"/>')

    nave = ""
    js_nave = ""
    if modo in ("rota", "voo") and amostras:
        passo = max(1, len(amostras) // 26)
        pts = amostras[::passo] + [amostras[-1]]
        xs = ",".join(f"{x:.0f}" for x, _ in pts)
        ys = ",".join(f"{y:.0f}" for _, y in pts)
        nave = '<i class="nave"></i>'
        js_nave = (
            f"gsap.set('.nave', {{x:{pts[0][0]:.0f}, y:{pts[0][1]:.0f}, opacity:0}});"
            f"tl.to('.nave', {{opacity:1, duration:0.2}}, 0.5)"
            f".to('.nave', {{keyframes:{{x:[{xs}], y:[{ys}], easeEach:'none'}},"
            f" duration:Math.max(0.8, DUR*0.62), ease:'power1.inOut'}}, 0.5)"
            f".to('.nave', {{opacity:0, duration:0.3}}, '>-0.1');")

    riscos = ""
    if modo == "voo":
        raias = []
        for _ in range(46):
            ang = rng.uniform(0, 360)
            dist = rng.uniform(210, 700)
            comprimento = rng.uniform(90, 260)
            x = W / 2 + dist * math.cos(math.radians(ang))
            y = H / 2 + dist * math.sin(math.radians(ang))
            raias.append(
                f'<i class="raia" style="left:{x:.0f}px;top:{y:.0f}px;'
                f'height:{comprimento:.0f}px;transform:translate(-50%,-50%) '
                f'rotate({ang + 90:.0f}deg)"></i>')
        riscos = f'<div class="raias">{"".join(raias)}</div>'

    titulo = ""
    if (p.get("texto") or "").strip():
        titulo = _bloco_tipografia(_linhas_de(p, 2), None, "tipografia baixa")

    corpo = f"""
      <div class="ceu">
        {cascas}
        <svg class="mapa" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{linhas}</svg>
        <div class="vertices">{vertices}{nave}</div>
        {riscos}
      </div>{titulo}"""

    css = f"""
      .ceu {{ position:absolute; inset:0; transform-style:preserve-3d; }}
      .casca {{ position:absolute; inset:0; transform-style:preserve-3d; }}
      /* sem a poeira colorida atras, o campo de estrelas vira ceu de subúrbio:
         pontinhos brancos num fundo chapado. A nebulosa e o que da materia. */
      .nebulosa {{ position:absolute; inset:0; transform:translateZ(-900px) scale(1.7);
        mix-blend-mode:screen; }}
      .nb {{ position:absolute; border-radius:50%; filter:blur(150px); }}
      .nb.a {{ width:900px; height:760px; left:4%; top:16%;
        background:radial-gradient(circle, rgba(123,44,255,0.17) 0%, transparent 68%); }}
      .nb.b {{ width:820px; height:900px; right:0%; bottom:12%;
        background:radial-gradient(circle, rgba(33,240,208,0.11) 0%, transparent 68%); }}
      .es {{ position:absolute; border-radius:50%; }}
      .casca.perta .es {{ filter:blur(3px); }}
      .mapa {{ position:absolute; left:0; top:0; transform:translateZ(60px);
        overflow:visible; }}
      .constelacao {{ fill:none; stroke:rgba(159,216,255,0.20); stroke-width:2;
        stroke-linejoin:round; }}
      .rota {{ fill:none; stroke:{NEON}; stroke-width:4; stroke-linecap:round;
        filter:drop-shadow(0 0 14px {NEON}); }}
      .vertices {{ position:absolute; inset:0; transform:translateZ(90px); }}
      .vt {{ position:absolute; transform:translate(-50%,-50%); text-align:center; }}
      .nucleo {{ display:block; width:16px; height:16px; margin:0 auto 14px;
        border-radius:50%; background:{DESTAQUE};
        box-shadow:0 0 16px {DESTAQUE}, 0 0 46px rgba(245,238,56,0.55); }}
      .rotulo {{ font-family:{FONTE_MONO}; font-size:38px; font-weight:500;
        letter-spacing:0.16em; text-transform:uppercase; color:{TEXTO};
        text-shadow:0 2px 16px {SOMBRA_TEXTO}; white-space:nowrap; }}
      .nave {{ position:absolute; left:0; top:0; width:22px; height:22px;
        margin:-11px 0 0 -11px; border-radius:50%; background:#FFFFFF;
        box-shadow:0 0 22px #FFFFFF, 0 0 70px {NEON}, 0 0 120px {NEON}; }}
      .raias {{ position:absolute; inset:0; transform:translateZ(200px);
        mix-blend-mode:screen; }}
      .raia {{ position:absolute; width:3px; border-radius:3px;
        background:linear-gradient(to bottom, transparent, #CFE2FF, transparent); }}
    """

    js = ("tl.from('.casca.longe .es', {opacity:0, duration:0.7, stagger:0.001,"
          " ease:'power1.out'}, 0);"
          "tl.to('.casca.longe', {rotateY:2.6, z:'+=70', duration:DUR, ease:'none'}, 0);"
          "tl.to('.casca.media', {rotateY:-2.0, z:'+=130', duration:DUR, ease:'none'}, 0);"
          "tl.to('.casca.perta', {x:-70, z:'+=220', duration:DUR, ease:'none'}, 0);"
          "tl.from('.vt', {opacity:0, scale:0.6, duration:0.5, stagger:0.16,"
          " ease:'power4.out'}, 0.25);")
    if linhas:
        js += ("tl.from('.constelacao', {opacity:0, duration:0.6}, 0.5);"
               f"tl.fromTo('.rota', {{strokeDasharray:{comp:.0f},"
               f" strokeDashoffset:{comp:.0f}}},"
               " {strokeDashoffset:0, duration:Math.max(0.8, DUR*0.62),"
               " ease:'power1.inOut'}, 0.5);")
    js += js_nave
    if modo == "voo":
        js += ("tl.fromTo('.raia', {scaleY:0, opacity:0},"
               " {scaleY:1, opacity:0.85, duration:0.45, stagger:0.012,"
               " ease:'power2.out'}, 0.3);"
               "tl.to('.ceu', {z:520, duration:DUR, ease:'power2.in'}, 0);")
    if titulo:
        js += JS_MATTE
    return corpo, css, js


def _camadas(p):
    """as camadas como lajes empilhadas em perspectiva, nao como a palavra
    CAMADAS. A citada sobe da pilha e acende; as outras recuam e escurecem."""
    itens = [str(w).strip() for w in (p.get("palavras") or [])][:6]
    ac = p.get("acender")
    ativo = None
    for i, w in enumerate(itens):
        if _bate(ac, i, w):
            ativo = i
    if ativo is None and ac is True and itens:
        ativo = len(itens) - 1
    # "todas": a pilha inteira acesa, sem uma laje se destacando das outras
    todas = isinstance(ac, str) and ac.strip().lower() == "todas"

    lajes = "".join(
        f'<div class="laje{" viva" if (todas or i == ativo) else ""}" style="--i:{i}">'
        f'<span class="ordem">{i + 1:02d}</span>'
        f'<span class="chapa">{_e(w)}</span></div>'
        for i, w in enumerate(itens))

    nome = [] if todas else ([itens[ativo]] if ativo is not None else [])
    corpo = f"""
      <div class="camada fundo"><div class="grade"></div></div>
      <div class="camada meio cheia"><div class="pilha">{lajes}</div></div>
      {_bloco_tipografia(nome, p.get('familia'), 'tipografia baixa')}"""

    css = f"""
      /* o angulo e o passo andam juntos: sob rotateX(a), um passo de Z vira
         passo*sin(a) na tela. Com 46 graus e 230 px de passo sobram 15 px de ar
         entre lajes de 150 — a 54 graus e 132 px de passo elas se cobriam. */
      .pilha {{ position:relative; width:{1080}px; height:900px;
        transform-style:preserve-3d;
        transform:translateY(300px) rotateX(46deg) rotateZ(-3deg); }}
      .laje {{ position:absolute; left:50%; top:50%; width:760px; height:150px;
        margin:-75px 0 0 -380px; border-radius:22px;
        background:{CARTAO}; border:1px solid {BORDA};
        box-shadow:0 24px 60px rgba(0,0,0,0.75);
        display:flex; align-items:center; gap:34px; padding:0 44px; opacity:0.42;
        transform:translateZ(calc(var(--i) * 230px)); }}
      .laje.viva {{ opacity:1; border-color:{ACIDO};
        background:{CARTAO_VIVO};
        box-shadow:0 0 0 1px {ACIDO}, 0 28px 70px rgba(0,0,0,0.8),
          0 0 90px rgba(168,255,83,0.30); }}
      .ordem {{ font-family:{FONTE_MONO}; font-size:44px; font-weight:700;
        color:{TEXTO_2}; letter-spacing:0.05em; }}
      .laje.viva .ordem {{ color:{ACIDO}; }}
      .chapa {{ font-family:{FONTE_TITULO}; font-size:62px; letter-spacing:-0.01em;
        text-transform:uppercase; color:{TEXTO_2}; }}
      .laje.viva .chapa {{ color:{TEXTO}; }}
      .tipografia.baixa .matte-text {{ font-size:88px; }}
    """

    js = ("tl.from('.laje', {z:-460, opacity:0, duration:0.6, stagger:0.13,"
          " ease:'power4.out'}, 0.1);"
          "tl.to('.pilha', {rotateZ:1.5, duration:DUR, ease:'none'}, 0);")
    if todas:
        js += "tl.to('.laje', {z:'+=40', duration:0.5, stagger:0.1, ease:'power3.out'}, 0.8);"
    elif ativo is not None:
        js += ("tl.to('.laje.viva', {z:'+=90', duration:0.55, ease:'power3.out'}, 0.85);"
               + JS_MATTE)
    return corpo, css, js


def _indice(p):
    """as partes do video como uma lista numerada de verdade — numeral grande em
    contorno, a da vez cheia — em vez de tres palavras soltas no meio do nada."""
    itens = [str(w).strip() for w in (p.get("palavras") or [])][:4]
    ac = p.get("acender")
    ativo = None
    for i, w in enumerate(itens):
        if _bate(ac, i, w):
            ativo = i
    if ativo is None and ac is True and itens:
        ativo = len(itens) - 1

    linhas = "".join(
        f'<div class="parte{" agora" if i == ativo else ""}">'
        f'<b>{i + 1:02d}</b><span>{_e(w)}</span></div>'
        for i, w in enumerate(itens))

    corpo = f"""
      <div class="camada fundo"><div class="grade"></div></div>
      <div class="camada meio cheia"><div class="lista">{linhas}</div></div>"""

    css = f"""
      .lista {{ width:900px; display:flex; flex-direction:column; gap:26px; }}
      .parte {{ display:flex; align-items:center; gap:34px; padding:26px 34px;
        border:1px solid {BORDA}; border-radius:24px;
        background:{CARTAO_FRACO}; }}
      .parte b {{ font-family:{FONTE_TITULO}; font-size:104px; line-height:0.9;
        color:transparent; -webkit-text-stroke:2px {TEXTO_2}; }}
      .parte span {{ font-family:{FONTE_TITULO}; font-size:56px; line-height:1.05;
        text-transform:uppercase; color:{TEXTO_2}; letter-spacing:-0.01em; }}
      .parte.agora {{ background:{CARTAO_VIVO}; border-color:{DESTAQUE};
        box-shadow:0 0 0 1px {DESTAQUE}, 0 26px 60px rgba(0,0,0,0.7); }}
      .parte.agora b {{ color:{DESTAQUE}; -webkit-text-stroke:0; }}
      .parte.agora span {{ color:{TEXTO}; }}
    """

    js = ("tl.from('.parte', {opacity:0, x:-70, duration:0.5, stagger:0.16,"
          " ease:'power4.out'}, 0.2);")
    if ativo is not None:
        js += "tl.from('.parte.agora', {scale:0.94, duration:0.5, ease:'power3.out'}, 0.75);"
    return corpo, css, js


def _cartela(p):
    """cartela tatil: card escuro com desfoque atras, tag mono, linhas em track
    matte e o risco amarelo abrindo embaixo. E o exemplo 01 do treino."""
    linhas = _linhas_de(p, 4)
    acesa = p.get("acender") if isinstance(p.get("acender"), str) else \
        (linhas[-1] if p.get("acender") is True and linhas else None)
    corpo = f"""
      <div class="camada fundo"><div class="grade"></div></div>
      <div class="camada meio alta">
        <div class="card">
          {_tag(p.get('familia') or p.get('estado') or '')}
          {_matte(linhas, acesa)}
          <div class="divisor"></div>
        </div>
      </div>"""
    css = f"""
      .card {{ background:{CARTAO}; border:1px solid {BORDA};
        border-radius:28px; padding:64px 50px; width:900px; backdrop-filter:blur(20px);
        filter:drop-shadow(0 20px 40px rgba(0,0,0,0.8)); text-align:center; }}
      .card .matte-text {{ font-size:84px; }}
    """
    js = ("tl.from('.card', {opacity:0, scale:0.92, y:30, duration:0.6,"
          " ease:'power3.out'}, 0.1);" + JS_MATTE + JS_DIVISOR)
    return corpo, css, js


def _paper(p):
    """ficha de paper: papel claro no escuro, com dupla sombra de contato."""
    d = p.get("paper") or {}
    corpo = f"""
      <div class="camada fundo"><div class="grade"></div></div>
      <div class="camada meio alta">
        <div class="ficha">
          <div class="veiculo">{_e(d.get('veiculo',''))}</div>
          <div class="titulo">{_e(d.get('titulo',''))}</div>
          <div class="autores">{_e(d.get('autores',''))}</div>
          <div class="doi">{_e(d.get('doi',''))}</div>
        </div>
      </div>"""
    css = f"""
      .ficha {{ width:900px; background:#F4F1EA; color:#14141A; padding:64px 60px;
        border-radius:6px;
        filter:drop-shadow(0 4px 10px rgba(0,0,0,0.9)) drop-shadow(0 25px 40px rgba(0,0,0,0.6)); }}
      .veiculo {{ font-family:{FONTE_MONO}; font-size:22px; letter-spacing:0.22em;
        text-transform:uppercase; color:#6B6B72; margin-bottom:26px; }}
      .titulo {{ font-family:'Fraunces',Georgia,serif; font-weight:600; font-size:64px;
        line-height:1.12; margin-bottom:26px; }}
      .autores {{ font-family:{FONTE_LEITURA}; font-size:30px; color:#3A3A42; }}
      .doi {{ font-family:{FONTE_MONO}; font-size:20px; color:#8A8A93; margin-top:26px; }}
    """
    js = ("tl.from('.ficha', {opacity:0, y:70, rotateX:6, duration:0.65,"
          " ease:'power4.out'}, 0.1)"
          ".from('.doi', {opacity:0, duration:0.4}, 0.6);")
    return corpo, css, js


def _retrato(p):
    d = p.get("retrato") or {}
    if p.get("asset"):
        corpo = (f'<div class="camada meio cheia">'
                 f'<img class="cena" src="{_e(p["asset"])}" alt=""></div>')
        css = """
          .cena { position:absolute; inset:0; width:100%; height:100%; object-fit:cover;
            filter:grayscale(1) contrast(1.15); }
        """
        return corpo, css, ""
    corpo = f"""
      <div class="camada fundo"><div class="grade"></div></div>
      <div class="camada meio alta">
        <div class="ficha-p">
          <div class="nome">{_e(d.get('nome',''))}</div>
          <div class="anos">{_e(d.get('anos',''))}</div>
          <div class="inst">{_e(d.get('instituicao',''))}</div>
        </div>
      </div>"""
    css = f"""
      .ficha-p {{ display:flex; flex-direction:column; gap:14px; align-items:center;
        text-align:center; padding:0 100px; }}
      .nome {{ font-family:'Fraunces',Georgia,serif; font-weight:600; font-size:88px; color:{TEXTO}; }}
      .anos {{ font-family:{FONTE_MONO}; font-size:30px; color:{TEXTO_2}; letter-spacing:0.2em; }}
      .inst {{ font-family:{FONTE_LEITURA}; font-size:32px; color:{TEXTO_2}; }}
    """
    js = ("tl.from('.ficha-p > *', {opacity:0, y:28, duration:0.5, stagger:0.12,"
          " ease:'power4.out'}, 0.1);")
    return corpo, css, js


def _dado(p):
    """retorica de dados em neon: caixa de vidro com borda ciano, curva desenhada
    como traco de caneta ou barras subindo, e a frase em track matte no alto."""
    curva = p.get("curva") or []
    serie = p.get("serie") or []
    linhas = _linhas_de(p, 2)
    W, H = 800, 460
    if curva:
        n = max(1, len(curva) - 1)
        mx, mn = max(curva), min(curva)
        amp = (mx - mn) or 1
        pts = " ".join(f"{i*W/n:.1f},{H - (v-mn)/amp*H*0.80 - H*0.10:.1f}"
                       for i, v in enumerate(curva))
        grafico = f"""
        <svg class="graf" viewBox="0 0 {W} {H}" preserveAspectRatio="none">
          <polyline class="linha" points="{pts}" fill="none" stroke="{NEON}" stroke-width="8"
            stroke-linecap="round" stroke-linejoin="round"/>
        </svg>"""
        js_graf = ("var L=document.querySelector('.linha'); var C=L.getTotalLength();"
                   "gsap.set(L,{strokeDasharray:C, strokeDashoffset:C});"
                   "tl.to(L,{strokeDashoffset:0, duration:Math.min(DUR*0.7,1.8),"
                   " ease:'power2.inOut'},0.5);")
    else:
        barras = "".join(
            f'<div class="barra"><i style="--v:{s.get("valor",0)}"></i>'
            f'<span>{_e(s.get("rotulo",""))}</span></div>' for s in serie)
        grafico = f'<div class="barras">{barras}</div>'
        js_graf = ("tl.from('.barra i', {scaleY:0, duration:0.8, stagger:0.14,"
                   " ease:'power4.out'}, 0.5);")
    corpo = f"""
      <div class="camada fundo"><div class="grade"></div></div>
      <div class="camada meio">
        <div class="caixa-neon">
          <div class="cabeca">
            <span>{_e(p.get('fonte') or 'MEDIDO')}</span><span class="viva">●  REC</span>
          </div>
          {grafico}
        </div>
      </div>{_bloco_tipografia(linhas, p.get('familia'))}"""
    css = f"""
      .caixa-neon {{ width:880px; padding:40px; background:{PAINEL};
        border:1px solid rgba(33,240,208,0.25); border-radius:20px;
        filter:drop-shadow(0 0 30px rgba(33,240,208,0.2)); }}
      .cabeca {{ display:flex; justify-content:space-between; font-family:{FONTE_MONO};
        font-size:22px; color:{NEON}; letter-spacing:0.15em; text-transform:uppercase;
        margin-bottom:26px; }}
      .cabeca .viva {{ color:{NEON_2}; }}
      .graf {{ width:100%; height:460px;
        filter:drop-shadow(0 0 26px rgba(33,240,208,0.45)); }}
      .barras {{ display:flex; gap:40px; align-items:flex-end; height:420px; }}
      .barra {{ flex:1; display:flex; flex-direction:column; align-items:center; gap:16px;
        height:100%; justify-content:flex-end; }}
      .barra i {{ display:block; width:100%; height:calc(var(--v) * 1%);
        background:linear-gradient(180deg,{NEON},{NEON_2}); border-radius:6px;
        transform-origin:50% 100%; box-shadow:0 0 24px rgba(33,240,208,0.45); }}
      .barra span {{ font-family:{FONTE_MONO}; font-size:22px; color:{TEXTO_2};
        text-transform:uppercase; letter-spacing:0.1em; }}
      .tipografia .matte-text {{ font-size:78px; }}
      .tipografia .matte-text.destaque {{ color:{NEON};
        text-shadow:0 0 38px {HALO}, 0 4px 20px {SOMBRA_TEXTO}; }}
    """
    js = ("tl.from('.caixa-neon', {opacity:0, y:40, duration:0.55, ease:'power3.out'}, 0.15);"
          + JS_MATTE + js_graf)
    return corpo, css, js


def _tela(p):
    """a tela como unica fonte de luz do quadro: a janela acende o ambiente ao
    redor e as mensagens entram uma a uma, no ritmo de quem le."""
    t = p.get("tela") or {}
    modo = t.get("modo") or "chat"
    if modo == "terminal":
        linhas = "".join(f'<div class="ln">{_e(l)}</div>' for l in (t.get("linhas") or []))
        interno = (f'<div class="cmd"><span class="prefixo">{_e(t.get("prefixo","$"))}</span>'
                   f'<span class="digita">{_e(t.get("comando",""))}</span></div>{linhas}')
        extra = ("tl.from('.digita', {width:0, duration:Math.min(1.2,DUR*0.4),"
                 " ease:'steps(24)'}, 0.35)"
                 ".from('.ln', {opacity:0, x:-18, duration:0.32, stagger:0.16,"
                 " ease:'power2.out'}, 1.0);")
    else:
        msgs = t.get("mensagens") or []
        # `de` e a chave; `lado` ("esq"/"dir") existe porque a documentacao do
        # diretor pedia esse nome — sem aceitar os dois, toda fala do usuario
        # saia desenhada como se fosse a maquina respondendo.
        def _quem(m):
            return "eu" if (m.get("de") == "eu" or m.get("lado") == "dir") else "ia"
        interno = "".join(
            f'<div class="msg {_quem(m)}">{_e(m.get("texto",""))}</div>'
            for m in msgs)
        extra = ("tl.from('.msg', {opacity:0, y:34, duration:0.45, stagger:0.34,"
                 " ease:'power4.out'}, 0.3);")
    corpo = f"""
      <div class="camada fundo"><div class="brilho-tela"></div></div>
      <div class="camada meio alta">
        <div class="janela">
          <div class="chrome"><i></i><i></i><i></i><span>{_e(t.get('titulo',''))}</span></div>
          <div class="corpo-janela">{interno}</div>
        </div>
      </div>"""
    css = f"""
      .brilho-tela {{ position:absolute; left:50%; top:50%; width:1500px; height:1500px;
        transform:translate(-50%,-50%);
        background:radial-gradient(circle, rgba(127,180,255,0.16) 0%, transparent 62%); }}
      .janela {{ width:970px; background:{JANELA}; border:1px solid {BORDA};
        border-radius:16px; overflow:hidden;
        filter:drop-shadow(0 4px 10px rgba(0,0,0,0.9)) drop-shadow(0 30px 60px rgba(0,0,0,0.75)); }}
      .chrome {{ display:flex; align-items:center; gap:10px; padding:22px 26px;
        background:{JANELA_BARRA}; border-bottom:1px solid {BORDA}; }}
      .chrome i {{ width:16px; height:16px; border-radius:50%; background:{CROMO}; }}
      .chrome span {{ margin-left:16px; font-family:{FONTE_MONO}; font-size:22px; color:{TEXTO_2}; }}
      .corpo-janela {{ padding:40px 34px; display:flex; flex-direction:column; gap:22px; }}
      .msg {{ max-width:78%; padding:26px 30px; border-radius:20px; font-family:{FONTE_LEITURA};
        font-size:36px; line-height:1.3; color:{TEXTO}; background:{BOLHA}; }}
      .msg.eu {{ align-self:flex-end; background:{BOLHA_EU}; }}
      .cmd {{ font-family:{FONTE_MONO}; font-size:38px; color:{TEXTO}; white-space:nowrap;
        margin-bottom:22px; }}
      .prefixo {{ color:{CIANO}; margin-right:14px; }}
      .digita {{ display:inline-block; overflow:hidden; vertical-align:bottom; }}
      .ln {{ font-family:{FONTE_MONO}; font-size:32px; color:{TEXTO_2}; line-height:1.55; }}
    """
    js = ("tl.from('.janela', {opacity:0, y:44, scale:0.96, duration:0.55,"
          " ease:'power4.out'}, 0.1);" + extra)
    return corpo, css, js


def _imagem(p):
    """objeto, personagem, obra, arquivo, cotidiano, broll, hibrido.

    A cena sangra o quadro e vive na camada do meio, entao a camera 3D a
    desloca contra o fundo e contra a tipografia. `objeto` ganha a barra de
    scanner — o efeito assinatura da categoria objeto-simbolo."""
    if not p.get("asset"):
        return '<div class="camada meio"></div>', "", ""
    tipo = p.get("tipo")
    linhas = _linhas_de(p, 2)
    tipografia = _bloco_tipografia(linhas, None, "tipografia baixa")
    scanner = '<div class="scanner"></div>' if tipo in ("objeto", "personagem") else ""
    corpo = f"""
      <div class="camada meio cheia">
        <img class="cena" src="{_e(p["asset"])}" alt="">
        {scanner}
      </div>{tipografia}"""
    css = f"""
      .cena {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }}
      .scanner {{ position:absolute; left:-100px; top:0; width:1280px; height:4px;
        background:linear-gradient(90deg, transparent 5%, {ACIDO} 50%, transparent 95%);
        box-shadow:0 0 20px 6px {ACIDO}, 0 0 50px 15px rgba(168,255,83,0.55);
        mix-blend-mode:screen; opacity:0; }}
    """
    cam = p.get("camera") or "push-in"
    a, b = (1.10, 1.0) if cam == "pull-out" else (1.0, 1.08)
    js = f"tl.fromTo('.cena', {{scale:{a}}}, {{scale:{b}, duration:DUR, ease:'none'}}, 0);"
    js += "tl.from('.cena', {opacity:0, duration:0.45, ease:'power2.out'}, 0);"
    if scanner:
        js += ("tl.fromTo('.scanner', {y:0, opacity:0},"
               " {y:1920, opacity:1, duration:Math.min(1.4, DUR*0.55),"
               " ease:'power2.inOut'}, 0.4);"
               "tl.to('.scanner', {opacity:0, duration:0.25, ease:'power2.out'},"
               " 0.4 + Math.min(1.4, DUR*0.55) - 0.1);")
    if linhas:
        js += JS_MATTE
    return corpo, css, js


# Um estilo nao e so paleta: o `vox` desenha colagem (papel, recorte serrilhado,
# grifo, anotacao a mao), e isso e composicao, nao cor. Onde o estilo tem
# desenho proprio para um tipo, ele ganha; onde nao tem, cai no generico.
CORPOS_POR_ESTILO = {"vox": hf_vox.CORPOS, "gravacao": hf_gravacao.CORPOS,
                     "ilustrativo": hf_ilustrativo.CORPOS}

CORPOS = {
    "palavras": _palavras, "cartela": _cartela, "paper": _paper, "retrato": _retrato,
    "dado": _dado, "tela": _tela,
    "galaxia": _galaxia, "camadas": _camadas, "indice": _indice,
    "objeto": _imagem, "personagem": _imagem, "obra": _imagem, "arquivo": _imagem,
    "cotidiano": _imagem, "broll": _imagem, "hibrido": _imagem,
}


# ---------- pagina --------------------------------------------------------

def html_do_plano(p, W=1080, H=1920, fps=FPS):
    dur = max(0.4, (p["t1"] - p["t0"]) / 1000)
    tipo = p.get("tipo")
    # o ceu precisa das medidas do quadro para posicionar vertices e rota em px
    proprio = CORPOS_POR_ESTILO.get(ESTILO_ATUAL, {}).get(tipo)
    corpo, css, js = (_galaxia(p, W, H) if tipo == "galaxia" and not proprio
                      else (proprio or CORPOS.get(tipo, _imagem))(p))
    de, para = ENTRADAS.get(p.get("entrada") or "corte", ENTRADAS["corte"])
    js_ent = ""
    if de:
        js_ent = (f"tl.fromTo('#palco', {de},"
                  f" Object.assign({para}, {{duration:0.45, ease:'power4.out'}}), 0);")
    saida = p.get("saida") or "corte"
    js_saida = {
        "varrer":   "tl.to('#palco', {xPercent:-100, duration:0.43, ease:'power3.inOut'}, DUR-0.43);",
        "empurrar": "tl.to('#palco', {yPercent:-100, duration:0.43, ease:'power3.inOut'}, DUR-0.43);",
        "implodir": "tl.to('#palco', {scale:0.86, opacity:0, duration:0.4, ease:'power3.in'}, DUR-0.4);",
        "apagar":   "tl.to('#palco', {opacity:0, duration:0.4, ease:'power2.in'}, DUR-0.4);",
    }.get(saida, "")

    # grade e bokeh sao luz sobre fundo escuro: num estilo de papel elas somem
    _grade = ACABAMENTO.get("grade_cor") or "transparent"
    _grade_off = "" if ACABAMENTO.get("grade_cor") else "display:none"
    _bokeh = ACABAMENTO.get("bokeh_cor") or "transparent"
    _bokeh_off = "" if ACABAMENTO.get("bokeh_cor") else "display:none"

    return f"""<!doctype html>
<html lang="pt-BR" data-resolution="portrait">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width={W}, height={H}"/>
<title>{_e(p.get('id',''))} · {_e(tipo)}</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{GOOGLE_FONTS}" rel="stylesheet">
<style>
  *{{margin:0;padding:0;box-sizing:border-box}}
  html,body{{width:{W}px;height:{H}px;overflow:hidden;background:{FUNDO};color:{TEXTO};
    font-family:{FONTE_LEITURA}}}
  /* o rig 3D: e a perspectiva que transforma translateZ em paralaxe */
  #root{{position:relative;width:{W}px;height:{H}px;overflow:hidden;
    background:radial-gradient(circle at 50% 46%, {CENTRO} 0%, {FUNDO} 78%);
    perspective:1200px;perspective-origin:50% 50%}}
  #palco{{position:absolute;inset:0}}
  #camera{{position:absolute;inset:0;width:{W}px;height:{H}px;
    transform-style:preserve-3d;will-change:transform}}
  /* as camadas e suas profundidades (exemplo 02 do treino) */
  .camada{{position:absolute;left:0;right:0;display:flex;align-items:center;
    justify-content:center}}
  .camada.fundo{{inset:-150px;transform:translateZ(-250px) scale(1.34)}}
  .camada.meio{{top:{SEGURO_TOPO + 300}px;bottom:{SEGURO_BASE}px;
    transform:translateZ(40px);
    filter:{SOMBRA_CAMADA}}}
  /* sem tipografia no alto, o sujeito recupera o terco superior */
  .camada.meio.alta{{top:{SEGURO_TOPO}px}}
  .camada.meio.cheia{{top:0;bottom:0;transform:translateZ(20px);filter:none}}
  .camada.frente{{inset:0;transform:translateZ(280px);pointer-events:none}}
  .grade{{position:absolute;inset:0;background-size:80px 80px;mix-blend-mode:screen;
    background-image:linear-gradient(to right,{_grade} 1px,transparent 1px),
      linear-gradient(to bottom,{_grade} 1px,transparent 1px);{_grade_off}}}
  .bokeh{{position:absolute;border-radius:50%;filter:blur(25px);
    background:radial-gradient(circle,{_bokeh} 0%,transparent 70%);{_bokeh_off}}}
{CSS_TIPOGRAFIA}
  /* acabamento analogico obrigatorio, fora da camera para nao girar junto */
  .halftone{{position:absolute;inset:0;pointer-events:none;
    mix-blend-mode:{ACABAMENTO['halftone_blend']};z-index:50;
    opacity:{ACABAMENTO['halftone_camada']}}}
  .grao{{position:absolute;inset:0;pointer-events:none;
    mix-blend-mode:{ACABAMENTO['grao_blend']};z-index:55;
    opacity:{ACABAMENTO['grao_opacidade']}}}
  .vinheta{{position:absolute;inset:0;pointer-events:none;z-index:45;
    background:{ACABAMENTO['vinheta'] or 'none'}}}
{css}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{dur:.3f}"
     data-width="{W}" data-height="{H}">
  <div id="palco">
    <div id="camera">
{corpo}
    </div>
  </div>
  <div class="vinheta"></div>
  <svg class="halftone" width="{W}" height="{H}"><defs>
    <pattern id="ht" x="0" y="0" width="8" height="8" patternUnits="userSpaceOnUse">
      <circle cx="4" cy="4" r="1.6" fill="{ACABAMENTO['halftone_cor']}"
              opacity="{ACABAMENTO['halftone_opacidade']}"/></pattern></defs>
    <rect width="100%" height="100%" fill="url(#ht)"/></svg>
  <svg class="grao" width="{W}" height="{H}"><defs>
    <filter id="gr"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="3"
      seed="7" stitchTiles="stitch"/></filter></defs>
    <rect width="100%" height="100%" filter="url(#gr)"/></svg>
</div>
<script>
  var DUR = {dur:.3f};
  window.__timelines = window.__timelines || {{}};
  var tl = gsap.timeline({{paused:true}});
  window.__timelines["main"] = tl;

  // A CAMERA NUNCA PARA: do primeiro ao ultimo quadro, linear. E o que separa
  // uma cena de um slide. O movimento e do estilo (`estilos.MOTION[...].camera`):
  // push-in em Z na casa, escala digital do canvas no `gravacao`.
  tl.fromTo('#camera',
    {CAMERA['de']},
    Object.assign({CAMERA['para']}, {{duration:DUR, ease:'{CAMERA['ease']}'}}), 0);

  {js_ent}
  {js}
  {js_saida}
  tl.to({{}}, {{duration:DUR}}, 0);
</script>
</body>
</html>
"""


# ---------- render --------------------------------------------------------

# O hyperframes TRAVA (sem mensagem, para sempre) quando o diretorio de
# trabalho tem parenteses ou acentos — e todo projeto de video tem: "01 - Efeito
# do Meio (Memoria e Alucinacao da IA)". Medido: o mesmo HTML renderiza em 8,3 s
# num caminho limpo e nunca termina no caminho do projeto. Por isso todo render
# acontece numa pasta neutra e o MP4 e copiado de volta.
OFICINA = Path.home() / ".beditor" / "render"


def _oficina(id_plano):
    d = OFICINA / "".join(c for c in id_plano if c.isalnum() or c in "-_")
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    return d


def render_plano(p, projeto, saida_dir, W, H, fps=FPS):
    pasta = saida_dir / p["id"]
    pasta.mkdir(parents=True, exist_ok=True)
    trabalho = _oficina(p["id"])
    # O render acontece numa pasta neutra, entao TODA imagem que a composicao
    # cita precisa viajar junto e virar caminho simples. Sao duas portas: o
    # `asset` do plano (a imagem gerada) e o `tela.fundo` (um quadro do proprio
    # take, quando a cena mostra a regra acontecendo em cima dele). Copiar so a
    # primeira deixa a segunda como <img> quebrada — metade do quadro em branco,
    # sem erro nenhum no log.
    p = dict(p)
    if p.get("asset"):
        origem = projeto / "public" / p["asset"]
        if origem.exists():
            nome = Path(p["asset"]).name
            (trabalho / nome).write_bytes(origem.read_bytes())
            p["asset"] = nome
    if isinstance(p.get("tela"), dict) and p["tela"].get("fundo"):
        origem = projeto / "public" / p["tela"]["fundo"]
        if origem.exists():
            nome = Path(p["tela"]["fundo"]).name
            (trabalho / nome).write_bytes(origem.read_bytes())
            p["tela"] = dict(p["tela"], fundo=nome)
    pagina = html_do_plano(p, W, H, fps)
    (trabalho / "index.html").write_text(pagina, encoding="utf-8")
    (pasta / "index.html").write_text(pagina, encoding="utf-8")   # para inspecao
    # versão fixa do CLI (HeyGen); BEDITOR_HYPERFRAMES troca, por exemplo "hyperframes@0.9.60"
    hyperframes = os.environ.get("BEDITOR_HYPERFRAMES", "hyperframes@0.9.58")
    r = subprocess.run(["npx", "--yes", hyperframes, "render", "-o", "clip.mp4"],
                       cwd=trabalho, capture_output=True, text=True, timeout=600, encoding="utf-8", errors="replace")
    feito = trabalho / "clip.mp4"
    if r.returncode != 0 or not feito.exists():
        raise RuntimeError(f"{p['id']}: hyperframes falhou\n{r.stdout[-800:]}{r.stderr[-800:]}")
    out = pasta / "clip.mp4"
    out.write_bytes(feito.read_bytes())
    shutil.rmtree(trabalho, ignore_errors=True)
    return out


def _paralelo_padrao():
    """Quantos renders ao mesmo tempo, sem pedir nada a quem roda.

    Cada render sobe um browser inteiro: e limitado por CPU e por memoria, nao
    por rede. Passar do numero de nucleos so faz as cenas disputarem o mesmo
    processador e chegarem todas mais tarde. O teto de 4 e por memoria — quatro
    browsers com uma pagina 1080x1920 ja e o que uma maquina de edicao aguenta
    sem comecar a paginar.
    """
    return max(1, min(4, os.cpu_count() or 1))


def _render_todos(alvos, projeto, saida, W, H, paralelo):
    """Renderiza as cenas em paralelo.

    O laco era sequencial por construcao, nao por necessidade: cada cena tem
    pasta de trabalho propria (`_oficina`) e sobe o proprio browser, entao nao
    ha estado compartilhado entre elas. Num video de 40 cenas eram 40 subidas de
    browser em fila — e era ai que a etapa passava as horas.

    Uma cena que falha nao derruba as outras: o erro e guardado, as demais
    terminam, e so no fim a falha e levantada com todas as que deram errado.
    Antes, a primeira falha jogava fora o trabalho ja pronto das seguintes.
    """
    if paralelo <= 1 or len(alvos) == 1:
        for p in alvos:
            out = render_plano(p, projeto, saida, W, H)
            print(f"  {p['id']:<5} {p['tipo']:<10} {out.stat().st_size//1024} KB", flush=True)
        return

    print(f"renderizando {len(alvos)} cenas, {paralelo} por vez")
    falhas = []
    feitos = 0
    with ThreadPoolExecutor(max_workers=paralelo) as pool:
        tarefas = {pool.submit(render_plano, p, projeto, saida, W, H): p for p in alvos}
        for t in as_completed(tarefas):
            p = tarefas[t]
            try:
                out = t.result()
            except Exception as e:
                falhas.append((p["id"], e))
                print(f"  {p['id']:<5} FALHOU: {e}", flush=True)
                continue
            feitos += 1
            print(f"  {p['id']:<5} {p['tipo']:<10} {out.stat().st_size//1024} KB "
                  f"({feitos}/{len(alvos)})", flush=True)
    if falhas:
        raise RuntimeError(
            f"{len(falhas)} de {len(alvos)} cenas falharam: "
            + ", ".join(i for i, _ in falhas))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projeto", required=True)
    ap.add_argument("--paralelo", type=int, default=_paralelo_padrao(),
                    help="cenas renderizadas ao mesmo tempo (1 = sequencial)")
    ap.add_argument("--saida", default=None, help="pasta dos clips (padrao: <projeto>/out/hf)")
    ap.add_argument("--so", default="", help="renderiza um plano so (ex: M12)")
    ap.add_argument("--so-html", action="store_true", help="escreve os HTML e para")
    ap.add_argument("--escala", type=float, default=1.0)
    a = ap.parse_args()

    projeto = Path(a.projeto)
    plano = json.loads((projeto / "plano.json").read_text(encoding="utf-8"))
    # o motion sai no estilo escolhido no guia (galeria-estilos.md); sem escolha,
    # no padrao da casa. A paleta e a fonte de todas as composicoes vem daqui.
    escolhido = aplicar_estilo((plano.get("estilos") or {}).get("motion"))
    print(f"estilo de motion: {escolhido} — {estilos.MOTION[escolhido]['rotulo']}")
    W, H = int(plano["largura"] * a.escala), int(plano["altura"] * a.escala)
    saida = Path(a.saida) if a.saida else projeto / "out" / "hf"
    saida.mkdir(parents=True, exist_ok=True)

    alvos = [p for p in plano["planos"] if p["tipo"] != "fala"
             and (not a.so or p["id"] == a.so)]
    if not alvos:
        # Video sem motion nenhum e uma escolha legitima — o rosto sustenta o
        # video inteiro, e foi assim que o editor pediu. Sair com erro aqui
        # derrubava o `montar.py` e o corte aprovado nao chegava a virar preview.
        print("nenhum plano de motion: o video e so A-roll, nada a renderizar")
        return
    if a.so_html:
        for p in alvos:
            pasta = saida / p["id"]
            pasta.mkdir(parents=True, exist_ok=True)
            (pasta / "index.html").write_text(html_do_plano(p, W, H), encoding="utf-8")
            print(f"  {p['id']:<5} html")
        print(f"pronto: {saida}")
        return

    _render_todos(alvos, projeto, saida, W, H, a.paralelo)
    print(f"pronto: {saida}")


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
