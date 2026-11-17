#!/usr/bin/env python3
"""
hf_vox.py — as composicoes do estilo `vox`: colagem, nao cartao repintado.

O dono olhou a primeira tentativa e disse, com razao: *"a imagem que mostrou nao
tem nada de parecido com o vox style"*. Era o layout do `noturno` com a paleta
trocada — cartao arredondado, sombra macia, borda fina. O vox nao e isso.

O que o estilo e, medido nas referencias (estudo de video publico, fora do plugin, e o
quadro de templates que o dono mandou em 2026-09-11):

- **papel com grade tecnica** por baixo de tudo, e fibra de papel no grao;
- **recorte**: foto em preto e branco com borda serrilhada de tesoura, colada
  torta, com fita crepe e sombra curta;
- **grifo de marca-texto** amarelo atras da palavra que importa, entrando por
  varredura, como se alguem passasse o marcador agora;
- **anotacao vermelha a mao**: elipse, seta e sublinhado desenhados na hora
  (traco que aparece desenhando, nunca surgindo pronto);
- **tipografia de jornal**: serifa na manchete, sans pequena no rotulo,
  maquina de escrever na nota de arquivo;
- **linha de chamada tracejada** ligando o rotulo ao ponto do desenho.

Cada funcao aqui devolve `(corpo, css, js)`, o mesmo contrato de `hf.py`.
"""
import html
import math
import random

from estilos import MOTION

T = MOTION["vox"]["tokens"]

PAPEL = T["FUNDO"]
TINTA = T["TEXTO"]
TINTA_2 = T["TEXTO_2"]
AZUL = T["CIANO"]
FERRUGEM = T["DESTAQUE"]
AMBAR = T["AMBAR"]
VERMELHO = "#D8352A"        # a caneta da anotacao, so ela
GRIFO = "#F2DE4A"           # o marca-texto
SERIF = "'Playfair Display', Georgia, serif"
SANS = "'Inter', -apple-system, sans-serif"
MAQUINA = "'Courier Prime', 'JetBrains Mono', ui-monospace, monospace"


def _e(t):
    return html.escape(str(t), quote=True)


# ---------- os gestos menores ---------------------------------------------
# Quatro gestos que a Vox repete e que nao sao efeito grande nenhum: e o que
# separa a colagem animada do gráfico de template. A decupagem esta em
# `skills/motion-vox/referencias/gestos-menores.md`, junto com a versao em PIL
# do mesmo principio — as duas pontas do vox precisam concordar.

FPS = 30            # o mesmo do hf.py; o passo de 2 frames sai daqui


def passos(duracao, fps=FPS):
    """'on twos': a entrada segura o valor por 2 frames em vez de correr lisa.

    E o 12fps da Vox — o elemento simples ganha caráter de stop motion. Vale
    para rotulo, numero e tipografia de apoio; a manchete em serifa continua
    lisa, porque travar corpo grande le como falha de render, nao como escolha.
    """
    return f"steps({max(2, round(duracao * fps / 2))})"


# a mordida: a mascara nao abre em progresso linear, ela avanca em pedacos
# desiguais e SEGURA entre eles. Progresso reto devolve o wipe de template.
MORDIDA = "[0,0.18,0.22,0.55,0.61,1]"


def mordida(seletor, duracao=0.5, em=0.0, prop="scaleX"):
    """revelacao mordida: o marcador/faixa entra em pedacos, nunca varrendo."""
    return (f"tl.fromTo('{seletor}', {{{prop}:0}}, {{keyframes:{{{prop}:{MORDIDA},"
            f" easeEach:'none'}}, duration:{duracao}, ease:'none'}}, {em});")


def verniz():
    """a borda de lente: o quadro 2D ganha caracteristica de lente de verdade.

    So nas BORDAS — o centro fica limpo. Efeito de lente e do olho que olha,
    nao do objeto olhado; aplicado ao quadro inteiro vira filtro.
    """
    return '<div class="lente"></div>'


def css_verniz():
    return """
      /* desfoque e franja de cor so no anel externo; o miolo nunca e tocado.
         Sem suporte a backdrop-filter a camada some, e nao estraga nada. */
      .lente { position:absolute; inset:0; pointer-events:none; z-index:54;
        backdrop-filter:blur(3.5px); -webkit-backdrop-filter:blur(3.5px);
        -webkit-mask-image:radial-gradient(ellipse 62% 56% at 50% 48%,
          rgba(0,0,0,0) 58%, rgba(0,0,0,1) 100%);
        mask-image:radial-gradient(ellipse 62% 56% at 50% 48%,
          rgba(0,0,0,0) 58%, rgba(0,0,0,1) 100%);
        box-shadow:inset 3px 0 26px rgba(216,53,42,0.055),
                   inset -3px 0 26px rgba(110,155,196,0.055); }"""


def _base_js(extra=""):
    """o fundo em movimento: vale para toda composicao do estilo.

    O plano longo em que nao ha o que ilustrar ainda precisa ser sustentado. A
    fibra do papel desloca em passos (~2,5 trocas por segundo): rapido demais
    para ser seguido, devagar demais para distrair. Deslocar a camada ja
    rasterizada e barato; resemear a turbulencia a cada passo custaria um
    recalculo de ruido em 1080x1920 e o render pagaria caro.
    """
    return ("tl.to('.fibra', {xPercent:-5, yPercent:-3, duration:DUR,"
            " ease:'steps('+Math.max(2,Math.round(DUR*2.5))+')'}, 0);") + extra


# ---------- pecas da colagem ----------------------------------------------
def papel():
    """o fundo: papel creme, grade tecnica fina e fibra no grao"""
    return """
      <div class="camada fundo">
        <div class="papel"></div>
        <div class="grade-tec"></div>
        <svg class="fibra" width="1080" height="1920"><defs>
          <filter id="fib"><feTurbulence type="fractalNoise" baseFrequency="0.9"
            numOctaves="4" seed="11" stitchTiles="stitch"/></filter></defs>
          <rect width="100%" height="100%" filter="url(#fib)"/></svg>
      </div>"""


def css_papel():
    return f"""
      .papel {{ position:absolute; inset:0; background:{PAPEL}; }}
      /* a grade e de milimetrado, nao de neon: azul lavado, 56 px, 1 px */
      .grade-tec {{ position:absolute; inset:0; opacity:0.9;
        background-image:
          repeating-linear-gradient(to right, rgba(92,112,150,0.16) 0 1px, transparent 1px 56px),
          repeating-linear-gradient(to bottom, rgba(92,112,150,0.16) 0 1px, transparent 1px 56px); }}
      /* maior que o quadro de proposito: a fibra se desloca em passos (o fundo
         em movimento), e com inset:0 o passo exporia a borda do papel. */
      .fibra {{ position:absolute; inset:-8%; width:116%; height:116%;
        mix-blend-mode:multiply; opacity:0.14; pointer-events:none; }}"""


def _serrilha(largura, altura, dente=13, semente=3):
    """poligono de borda de tesoura: o recorte nunca tem lado reto"""
    rng = random.Random(semente)
    pts = []

    def lado(x0, y0, x1, y1):
        n = max(6, int(math.hypot(x1 - x0, y1 - y0) / dente))
        for i in range(n):
            t = i / n
            x = x0 + (x1 - x0) * t
            y = y0 + (y1 - y0) * t
            # o dente sai perpendicular ao lado, alternando para dentro e para fora
            dx, dy = (y1 - y0), -(x1 - x0)
            m = math.hypot(dx, dy) or 1
            d = (rng.uniform(0.25, 1.0) * dente) * (1 if i % 2 else -0.35)
            pts.append((x + dx / m * d, y + dy / m * d))

    lado(0, 0, largura, 0)
    lado(largura, 0, largura, altura)
    lado(largura, altura, 0, altura)
    lado(0, altura, 0, 0)
    return "polygon(" + ", ".join(f"{x:.1f}px {y:.1f}px" for x, y in pts) + ")"


def css_recorte(largura=760, altura=760, semente=3):
    return f"""
      /* recorte: P&B de arquivo, borda de tesoura, colado torto, sombra curta */
      .recorte {{ position:relative; width:{largura}px; height:{altura}px;
        filter:grayscale(1) contrast(1.18) brightness(1.04);
        clip-path:{_serrilha(largura, altura, semente=semente)};
        transform:rotate(-1.6deg); }}
      .recorte img {{ width:100%; height:100%; object-fit:cover; display:block; }}
      .porta-recorte {{ position:relative;
        filter:drop-shadow(0 16px 26px rgba(70,55,35,0.34)); }}
      /* fita crepe: opaca o bastante para parecer fita, nunca um retangulo limpo */
      .fita {{ position:absolute; width:210px; height:54px; background:rgba(238,224,186,0.86);
        box-shadow:0 2px 5px rgba(70,55,35,0.28); mix-blend-mode:multiply;
        clip-path:polygon(3% 0,97% 4%,100% 96%,1% 100%); }}
      .fita.ne {{ top:-26px; right:-52px; transform:rotate(24deg); }}
      .fita.so {{ bottom:-24px; left:-56px; transform:rotate(18deg); }}"""


def grifo(texto, classe="", dentro=""):
    """o marca-texto amarelo: uma faixa de verdade atras da palavra, torta.

    `dentro` pendura algo na caixa da palavra — e assim que a elipse da caneta
    acha o alvo: ancorada no texto, nao num `top` calculado aqui.
    """
    return (f'<span class="grifo {classe}"><i></i>{_e(texto)}{dentro}</span>')


def css_grifo():
    return f"""
      .grifo {{ position:relative; display:inline-block; padding:0 0.1em; }}
      .grifo i {{ position:absolute; left:-0.08em; right:-0.08em; top:0.16em; bottom:0.08em;
        background:{GRIFO}; z-index:-1; transform-origin:left center;
        transform:rotate(-0.8deg); mix-blend-mode:multiply;
        clip-path:polygon(0 7%,100% 0,100% 93%,0 100%); }}"""


def anotacao(tipo="elipse", w=760, h=300, semente=5, elastica=False):
    """elipse ou seta de caneta vermelha, desenhada na hora (dash animado).

    `elastica=True` faz o desenho acompanhar a CAIXA REAL do elemento que ele
    anota, em vez de uma medida calculada aqui. E a diferenca entre circular a
    palavra certa e circular o vizinho: a altura de uma linha e a largura de uma
    palavra quem decide e o navegador, com a metrica da fonte — em Python isso e
    sempre estimativa, e a estimativa quebra assim que o texto quebra linha.
    O traco nao engorda ao esticar por causa do `non-scaling-stroke`.
    """
    rng = random.Random(semente)
    if tipo == "elipse":
        cx, cy, rx, ry = w / 2, h / 2, w * 0.44, h * 0.38
        pts = []
        for i in range(29):
            a = -0.35 + i * (2 * math.pi + 0.55) / 28
            j = 1 + rng.uniform(-0.045, 0.045)
            pts.append((cx + math.cos(a) * rx * j, cy + math.sin(a) * ry * j))
        d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    else:   # seta: curva com ponta
        d = (f"M {w*0.08:.0f} {h*0.18:.0f} C {w*0.30:.0f} {h*0.02:.0f}, "
             f"{w*0.62:.0f} {h*0.10:.0f}, {w*0.86:.0f} {h*0.62:.0f} "
             f"M {w*0.72:.0f} {h*0.46:.0f} L {w*0.87:.0f} {h*0.66:.0f} "
             f"L {w*0.66:.0f} {h*0.70:.0f}")
    if elastica:
        return (f'<svg class="anot elastica" viewBox="0 0 {w} {h}"'
                f' preserveAspectRatio="none">'
                f'<path d="{d}" vector-effect="non-scaling-stroke"/></svg>')
    return (f'<svg class="anot" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<path d="{d}"/></svg>')


def css_anotacao():
    return f"""
      /* a caneta desenha: o traco entra por dash, nunca aparece pronto */
      .anot {{ position:absolute; overflow:visible; pointer-events:none; }}
      .anot path {{ fill:none; stroke:{VERMELHO}; stroke-width:7;
        stroke-linecap:round; stroke-linejoin:round; }}
      /* a elastica e ancorada no ALVO e esticada pelas quatro bordas: a posicao
         sai da caixa real do elemento, nunca de um numero calculado em Python */
      .anot.elastica {{ width:auto; height:auto; }}"""


def chamada(rotulo, largura=300):
    """linha de chamada tracejada com o rotulo na ponta, como no infografico"""
    return (f'<div class="chamada" style="width:{largura}px">'
            f'<span class="ponto"></span><span class="linha"></span>'
            f'<span class="rot">{_e(rotulo)}</span></div>')


def css_chamada():
    return f"""
      .chamada {{ position:absolute; display:flex; align-items:center; gap:14px; }}
      .chamada .ponto {{ width:12px; height:12px; border-radius:50%; background:{TINTA}; }}
      .chamada .linha {{ flex:1; height:0; border-top:2px dashed rgba(27,23,20,0.45); }}
      .chamada .rot {{ font-family:{SANS}; font-size:30px; font-weight:600; color:{TINTA};
        white-space:nowrap; }}"""


def _base_css(**extra):
    return "\n".join([css_papel(), css_grifo(), css_anotacao(), css_chamada(),
                      css_verniz()] + list(extra.values()))


# ---------- composicoes ----------------------------------------------------
def cartela(p):
    """manchete de jornal: serifa grande, a linha que importa no grifo, credito
    em maquina de escrever e a caneta circulando o que interessa."""
    linhas = [str(x).strip() for x in (p.get("linhas") or
              [l for l in str(p.get("texto") or "").split("\n") if l.strip()]) if str(x).strip()]
    if not linhas:
        linhas = [str(p.get("texto") or "").strip() or "—"]
    acesa = len(linhas) - 1
    if isinstance(p.get("acender"), str):
        acesa = next((i for i, l in enumerate(linhas) if p["acender"].lower() in l.lower()), acesa)
    # A caneta circula a linha acesa. A elipse mora DENTRO do grifo: assim ela
    # herda a caixa real da palavra, quebre o texto em quantas linhas quiser.
    # (Antes saia de `acesa * 114 + 60` com a largura por contagem de letras —
    # batia no caso curto e circulava a linha de cima assim que o texto quebrava.
    # Medido por `conferir_layout.py`: errava 250px no caso "linha longa".)
    html_linhas = "\n".join(
        f'<div class="ln">'
        f'{grifo(l, dentro=anotacao("elipse", 760, 200, elastica=True)) if i == acesa else _e(l)}'
        f'</div>'
        for i, l in enumerate(linhas))
    corpo = f"""{papel()}
      <div class="camada meio alta">
        <div class="manchete">
          <div class="olho">{_e(p.get('familia') or p.get('estado') or 'reportagem')}</div>
          {html_linhas}
          <div class="regua"></div>
          <div class="credito">{_e(p.get('fonte') or '')}</div>
        </div>
      </div>{verniz()}"""
    css = _base_css(mais=f"""
      .manchete {{ width:900px; position:relative; }}
      .olho {{ font-family:{MAQUINA}; font-size:28px; letter-spacing:0.22em;
        text-transform:uppercase; color:{TINTA_2}; margin-bottom:26px; }}
      .ln {{ font-family:{SERIF}; font-weight:800; font-size:96px; line-height:1.08;
        color:{TINTA}; letter-spacing:-0.015em; margin-bottom:10px; }}
      .regua {{ height:3px; background:{TINTA}; opacity:0.8; margin:34px 0 18px; }}
      .credito {{ font-family:{MAQUINA}; font-size:26px; color:{TINTA_2}; }}
      /* esticada pelas quatro bordas da palavra grifada: sem numero nenhum */
      .grifo > .anot.elastica {{ left:-46px; right:-46px; top:-40px; bottom:-40px; }}""")
    # o olho e o credito sao tipografia de apoio: entram em passos. A manchete
    # em serifa NAO — corpo grande travado le como falha de render.
    js = _base_js(
        f"tl.from('.olho', {{opacity:0, y:-18, duration:0.4,"
        f" ease:'{passos(0.4)}'}}, 0.1);"
        f"tl.from('.ln', {{opacity:0, y:28, duration:0.5, stagger:0.14, ease:'power4.out'}}, 0.18);"
        # o marca-texto e passado por uma mao: avanca aos pedacos e segura
        + mordida('.grifo i', 0.5, 0.62) +
        f"tl.from('.regua', {{scaleX:0, transformOrigin:'left center', duration:0.5,"
        f" ease:'{passos(0.5)}'}}, 0.72);"
        # o credito entra depois da regua, nunca junto: papel posto, depois escrito
        f"tl.from('.credito', {{opacity:0, y:12, duration:0.34,"
        f" ease:'{passos(0.34)}'}}, 0.92);"
        # a caneta desenhando e o unico movimento continuo da cena: e a mao.
        f"tl.fromTo('.anot path', {{strokeDasharray:2600, strokeDashoffset:2600}},"
        f" {{strokeDashoffset:0, duration:0.9, ease:'power2.inOut'}}, 1.0);")
    return corpo, css, js


def palavras(p):
    """a lista que acumula: cada palavra numa tira de papel, o marcador passa
    na nova, e a caneta sublinha a que a voz carrega."""
    ps = [str(x).strip() for x in (p.get("palavras") or []) if str(x).strip()][:5]
    if not ps:
        ps = [str(p.get("texto") or "").strip() or "—"]
    acesa = len(ps) - 1 if p.get("acender") else None
    if isinstance(p.get("acender"), str):
        acesa = next((i for i, w in enumerate(ps) if p["acender"].lower() == w.lower()), acesa)
    itens = "\n".join(
        f'<div class="item" style="--r:{(-1.4 if i % 2 else 1.1):.1f}deg">'
        f'<b>{i + 1:02d}</b>'
        f'<span class="pal">{grifo(w) if i == acesa else _e(w)}</span></div>'
        for i, w in enumerate(ps))
    corpo = f"""{papel()}
      <div class="camada meio cheia">
        <div class="lista-v">{itens}</div>
      </div>{verniz()}"""
    css = _base_css(mais=f"""
      .lista-v {{ width:880px; display:flex; flex-direction:column; gap:30px; }}
      .item {{ display:flex; align-items:baseline; gap:28px; transform:rotate(var(--r)); }}
      .item b {{ font-family:{MAQUINA}; font-size:34px; color:{FERRUGEM}; }}
      .pal {{ font-family:{SERIF}; font-weight:800; font-size:84px; line-height:1.1;
        color:{TINTA}; letter-spacing:-0.01em; }}""")
    # a tira de papel e posta na mesa: passo, nao deslize. O numero em maquina
    # de escrever entra depois dela, com o mesmo caráter.
    js = _base_js(
        f"tl.from('.item', {{opacity:0, x:-60, duration:0.46, stagger:0.2,"
        f" ease:'{passos(0.46)}'}}, 0.15);"
        f"tl.from('.item b', {{opacity:0, duration:0.2, stagger:0.2,"
        f" ease:'{passos(0.2)}'}}, 0.28);"
        + mordida('.grifo i', 0.46, "'>-0.1'"))
    return corpo, css, js


def dado(p):
    """infografico de papel: linha vermelha sobre a grade, ponto anotado e
    chamada tracejada — sem painel escuro, sem neon."""
    curva = [float(x) for x in (p.get("curva") or [])][:12]
    serie = p.get("serie") or []
    W, H = 820, 460
    if curva:
        pts = " ".join(f"{i / max(1, len(curva) - 1) * W:.0f},{H - v * H * 0.86 - 20:.0f}"
                       for i, v in enumerate(curva))
        ultimo_x = W
        ultimo_y = H - curva[-1] * H * 0.86 - 20
        desenho = f"""
          <svg class="graf" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
            <polyline class="linha-dado" points="{pts}"/>
            <circle class="ponta" cx="{ultimo_x:.0f}" cy="{ultimo_y:.0f}" r="13"/>
          </svg>"""
    else:
        barras = "".join(
            f'<div class="barra"><i style="--v:{float(s.get("valor", 0)):.3f}"></i>'
            f'<span>{_e(s.get("rotulo", ""))}</span></div>' for s in serie[:6])
        desenho = f'<div class="barras">{barras}</div>'
    corpo = f"""{papel()}
      <div class="camada meio alta">
        <div class="quadro">
          <div class="titulo-q">{_e(p.get('texto') or p.get('fonte') or '')}</div>
          {desenho}
          {chamada(_e(p.get('fonte') or 'fonte medida'), 340)}
          {anotacao('seta', 300, 200, semente=9)}
        </div>
      </div>{verniz()}"""
    css = _base_css(mais=f"""
      .quadro {{ width:{W}px; position:relative; }}
      .titulo-q {{ font-family:{SERIF}; font-weight:800; font-size:58px; color:{TINTA};
        margin-bottom:30px; line-height:1.1; }}
      .linha-dado {{ fill:none; stroke:{VERMELHO}; stroke-width:9; stroke-linecap:round;
        stroke-linejoin:round; }}
      .ponta {{ fill:{VERMELHO}; }}
      .graf {{ display:block; overflow:visible; }}
      .barras {{ display:flex; gap:38px; align-items:flex-end; height:{H}px; }}
      .barra {{ flex:1; display:flex; flex-direction:column; align-items:center; gap:14px;
        justify-content:flex-end; height:100%; }}
      .barra i {{ width:100%; height:calc(var(--v) * 100%); background:{AZUL};
        transform-origin:bottom center; }}
      .barra:last-child i {{ background:{VERMELHO}; }}
      .barra span {{ font-family:{SANS}; font-size:26px; color:{TINTA_2}; }}
      .quadro .chamada {{ right:0; bottom:-64px; }}
      .quadro .anot {{ right:-40px; top:60px; }}""")
    # a linha vermelha e a seta sao tracos de mao: continuos. A barra e o
    # rotulo sao impressos: entram em passos.
    js = _base_js(
        "tl.from('.titulo-q', {opacity:0, y:22, duration:0.45, ease:'power3.out'}, 0.1);"
        "tl.fromTo('.linha-dado', {strokeDasharray:2400, strokeDashoffset:2400},"
        " {strokeDashoffset:0, duration:1.1, ease:'power2.inOut'}, 0.35);"
        "tl.from('.ponta', {scale:0, transformOrigin:'center', duration:0.34,"
        " ease:'back.out(2)'}, 1.25);"
        f"tl.from('.barra i', {{scaleY:0, duration:0.5, stagger:0.12,"
        f" ease:'{passos(0.5)}'}}, 0.4);"
        f"tl.from('.barra span', {{opacity:0, duration:0.22, stagger:0.12,"
        f" ease:'{passos(0.22)}'}}, 0.62);"
        f"tl.from('.chamada', {{opacity:0, x:-24, duration:0.4,"
        f" ease:'{passos(0.4)}'}}, 1.3);"
        "tl.fromTo('.anot path', {strokeDasharray:900, strokeDashoffset:900},"
        " {strokeDashoffset:0, duration:0.7, ease:'power2.inOut'}, 1.35);")
    return corpo, css, js


def indice(p):
    """as partes do video como tiras de papel numeradas; a da vez ganha a
    elipse vermelha."""
    ps = [str(x).strip() for x in (p.get("palavras") or []) if str(x).strip()][:5] or ["—"]
    ativo = p.get("acender")
    ativo = ativo if isinstance(ativo, int) else \
        next((i for i, w in enumerate(ps) if str(ativo).lower() == w.lower()), 0)
    # a elipse mora DENTRO da tira ativa: a altura de uma tira depende de o
    # rotulo caber numa linha ou em duas, e so o navegador sabe disso. Antes
    # saia de `ativo * 122` — errava ~150px assim que um rotulo quebrava.
    tiras = "\n".join(
        f'<div class="tira{" agora" if i == ativo else ""}" '
        f'style="--r:{(-1.1 if i % 2 else 0.9):.1f}deg"><b>{i + 1:02d}</b>'
        f'<span>{_e(w)}</span>'
        f'{anotacao("elipse", 820, 150, semente=7, elastica=True) if i == ativo else ""}'
        f'</div>' for i, w in enumerate(ps))
    corpo = f"""{papel()}
      <div class="camada meio cheia">
        <div class="tiras">{tiras}</div>
      </div>{verniz()}"""
    css = _base_css(mais=f"""
      .tiras {{ width:820px; position:relative; display:flex; flex-direction:column; gap:26px; }}
      .tira {{ position:relative; display:flex; align-items:center; gap:30px; padding:26px 34px;
        background:rgba(252,247,236,0.92); transform:rotate(var(--r));
        clip-path:polygon(0 6%,100% 0,99% 96%,1% 100%);
        box-shadow:0 10px 20px rgba(70,55,35,0.20); }}
      .tira b {{ font-family:{MAQUINA}; font-size:40px; color:{TINTA_2}; }}
      .tira span {{ font-family:{SERIF}; font-weight:800; font-size:54px; color:{TINTA_2};
        line-height:1.05; }}
      .tira.agora b {{ color:{FERRUGEM}; }}
      .tira.agora span {{ color:{TINTA}; }}
      /* ancorada na tira ativa, nao num `ativo * 122` que a quebra de linha desmente */
      .tira > .anot.elastica {{ left:-30px; right:-30px; top:-18px; bottom:-18px; }}""")
    js = _base_js(
        f"tl.from('.tira', {{opacity:0, x:-70, duration:0.46, stagger:0.16,"
        f" ease:'{passos(0.46)}'}}, 0.15);"
        "tl.fromTo('.anot path', {strokeDasharray:2200, strokeDashoffset:2200},"
        " {strokeDashoffset:0, duration:0.85, ease:'power2.inOut'}, 0.85);")
    return corpo, css, js


def camadas(p):
    """a pilha revelada: tiras de papel empilhadas, a que sobe ganha o grifo"""
    ps = [str(x).strip() for x in (p.get("palavras") or []) if str(x).strip()][:5] or ["—"]
    viva = p.get("acender")
    viva = viva if isinstance(viva, int) else \
        next((i for i, w in enumerate(ps) if str(viva).lower() == w.lower()), len(ps) - 1)
    tiras = "\n".join(
        f'<div class="laje-v{" viva" if i == viva else ""}" '
        f'style="--i:{i}; --r:{(-1.3 if i % 2 else 1.0):.1f}deg">'
        f'{grifo(w) if i == viva else _e(w)}</div>' for i, w in enumerate(ps))
    corpo = f"""{papel()}
      <div class="camada meio cheia"><div class="pilha-v">{tiras}</div></div>{verniz()}"""
    css = _base_css(mais=f"""
      .pilha-v {{ width:820px; display:flex; flex-direction:column-reverse; gap:22px; }}
      .laje-v {{ padding:30px 40px; background:rgba(252,247,236,0.94);
        transform:rotate(var(--r)) translateX(calc(var(--i) * 26px));
        clip-path:polygon(0 5%,100% 0,99% 97%,1% 100%);
        box-shadow:0 12px 22px rgba(70,55,35,0.22);
        font-family:{SERIF}; font-weight:800; font-size:62px; color:{TINTA_2};
        opacity:0.62; }}
      .laje-v.viva {{ opacity:1; color:{TINTA}; }}""")
    js = _base_js(
        f"tl.from('.laje-v', {{opacity:0, y:44, duration:0.46, stagger:0.15,"
        f" ease:'{passos(0.46)}'}}, 0.15);"
        + mordida('.grifo i', 0.42, "'>-0.05'"))
    return corpo, css, js


def imagem(p):
    """o asset gerado como recorte: P&B, borda de tesoura, fita, seta vermelha
    e um rotulo de papel com a palavra."""
    asset = p.get("asset")
    if not asset:
        return cartela(p)
    rotulo = (p.get("texto") or p.get("estado") or "").strip()
    corpo = f"""{papel()}
      <div class="camada meio cheia">
        <div class="colagem">
          <div class="porta-recorte">
            <div class="recorte"><img src="{_e(asset)}" alt=""/></div>
            <div class="fita ne"></div><div class="fita so"></div>
          </div>
          {f'<div class="etiqueta">{_e(rotulo)}</div>' if rotulo else ''}
          {anotacao('seta', 320, 220, semente=4)}
        </div>
      </div>{verniz()}"""
    css = _base_css(recorte=css_recorte(760, 900, semente=4), mais=f"""
      .colagem {{ position:relative; }}
      .etiqueta {{ position:absolute; left:-40px; bottom:-34px; padding:14px 26px;
        background:rgba(252,247,236,0.96); transform:rotate(-2deg);
        clip-path:polygon(0 8%,100% 0,99% 94%,1% 100%);
        box-shadow:0 8px 16px rgba(70,55,35,0.25);
        font-family:{SANS}; font-weight:600; font-size:34px; color:{TINTA}; }}
      .colagem .anot {{ right:-120px; top:60px; }}""")
    # o recorte e POSTO na mesa: passo, nao deslize. A fita mantem o `back`,
    # que e a pressao do dedo — e o unico elastico que a colagem admite.
    js = _base_js(
        f"tl.from('.porta-recorte', {{opacity:0, scale:0.94, rotate:-4, duration:0.5,"
        f" ease:'{passos(0.5)}'}}, 0.1);"
        "tl.from('.fita', {opacity:0, scale:0.7, duration:0.3, stagger:0.1,"
        " ease:'back.out(2)'}, 0.4);"
        # a etiqueta so depois da fita: papel colado primeiro, escrito depois
        f"tl.from('.etiqueta', {{opacity:0, y:18, duration:0.36,"
        f" ease:'{passos(0.36)}'}}, 0.72);"
        "tl.fromTo('.anot path', {strokeDasharray:900, strokeDashoffset:900},"
        " {strokeDashoffset:0, duration:0.7, ease:'power2.inOut'}, 0.8);")
    return corpo, css, js


# os tipos que o estilo `vox` desenha de outro jeito. O que nao esta aqui cai
# na composicao generica do hf.py, ja com a paleta de papel.
CORPOS = {
    "cartela": cartela, "palavras": palavras, "dado": dado,
    "indice": indice, "camadas": camadas,
    "objeto": imagem, "personagem": imagem, "obra": imagem, "arquivo": imagem,
    "cotidiano": imagem, "broll": imagem, "hibrido": imagem,
}
