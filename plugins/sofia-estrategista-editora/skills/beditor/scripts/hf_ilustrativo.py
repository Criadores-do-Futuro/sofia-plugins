#!/usr/bin/env python3
"""
hf_ilustrativo.py — composicoes do estilo `ilustrativo`: pagina de revista que
se move.

Direcao escrita pelo dono em 2026-09-12:

    "2D editorial motion design, not 3D. Layered flat graphics over photographic
    and archival material. Zero character animation. Everything is compositing +
    typography in motion — the frame is built like a magazine spread that moves."

As tres leis deste estilo, e nenhuma delas e decoracao:

1. **NADA FICA PARADO.** *"the core rule the video names explicitly is constant
   motion"*. Todo plano carrega deriva lenta (2-5%) por baixo, do primeiro ao
   ultimo quadro. O texto entra, trava e NAO se mexe mais — quem se move e o
   fundo. Texto parado sobre fundo parado le como slide; texto parado sobre
   fundo derivando le como pagina sendo lida.

2. **NADA QUICA.** *"snappy but never bouncy. No overshoot, no elastic, no
   wobble."* A entrada e um estalo de 3-6 quadros em `power3.out` e acabou.
   O estilo anterior (`gravacao`) usava `back.out` de proposito; aqui
   `back.out` e erro. O dono pediu o movimento "menos seco", e menos seco NAO
   e mais quique: e a deriva continua por baixo, que tira o solavanco entre um
   elemento e outro.

3. **UM ACENTO POR QUADRO.** Amarelo Vox #FFE01B, rosa #FF5A7E ou ardosia
   #2E4257 — nunca dois no mesmo plano. A escolha do acento sai do indice do
   plano, para o video inteiro nao cair sempre no mesmo.

Tipografia: numeral didone gigante (40-60% da altura do quadro), subtitulo em
serifa minuscula italica embaixo dele, rotulo em versalete espacado preso ao
objeto que ele anota, e algarismo tabular em grotesca condensada no dado.

Cada funcao devolve `(corpo, css, js)`, o mesmo contrato de `hf.py`.

**Nome de classe colide.** A CSS do estilo entra depois da folha comum do
`hf.py`, entao repetir um nome de la sobrescreve so o que voce escreveu e herda
o resto (ver a mesma nota em `hf_gravacao.py`). Dai o prefixo `il-`.
"""
import html

from estilos import MOTION

T = MOTION["ilustrativo"]["tokens"]

CREME = T["FUNDO"]
PAPEL_2 = T["SUPERFICIE"]
TINTA = T["TEXTO"]
TINTA_2 = T["TEXTO_2"]
AMARELO = T["AMBAR"]          # o badge circular
ROSA = T["DESTAQUE"]          # circulo de dado, preenchimento de mapa
ARDOSIA = T["CIANO"]          # campo de apoio
CORAL = T["NEGADO"]           # a anotacao a mao
PRETO = "#0D0D0D"             # o campo editorial escuro
BORDA = T["BORDA"]
CROMO = T["CROMO"]
DIDONE = T["FONTE_TITULO"]
SANS = T["FONTE_LEITURA"]
CONDENSADA = T["FONTE_MONO"]

ACENTOS = (AMARELO, ROSA, ARDOSIA)

# A janela onde o `acervo.py` encaixa o trecho de video de terceiro, em px do
# quadro de 1080x1920. Fica AQUI, e nao no CSS solto, porque dois programas
# precisam concordar sobre ela: o HTML desenha a moldura neste retangulo e o
# ffmpeg sobrepoe o video no mesmo retangulo. Se divergirem, o trecho aparece
# torto e ninguem descobre por que.
MOLDURA_ACERVO = (90, 430, 900, 1200)      # x, y, largura, altura


def _e(t):
    return html.escape(str(t or ""), quote=True)


def _linhas(p, maximo=4):
    cru = p.get("linhas") or [l for l in str(p.get("texto") or "").split("\n")]
    return [str(x).strip() for x in cru if str(x).strip()][:maximo]


def _palavras(p, maximo=5):
    cru = p.get("palavras") or _linhas(p, maximo)
    return [str(x).strip() for x in cru if str(x).strip()][:maximo]


def _acento(p):
    """um acento por quadro, e ele muda de plano para plano.

    A semente e o id do plano: assim dois planos vizinhos quase nunca caem no
    mesmo acento, e o mesmo plano escolhe sempre o mesmo em qualquer render."""
    semente = sum(ord(c) for c in str(p.get("id") or "M"))
    return ACENTOS[semente % len(ACENTOS)]


# ---------- os gestos do estilo -------------------------------------------
# Tres, e nenhum deles tem elastico.

SNAP = "power3.out"          # o estalo de 4 quadros
DERIVA = "none"              # a deriva e linear: ela nao pode ter sotaque


def snap(seletor, em=0.0, de="{opacity:0, y:26}", dur=0.133, stagger=None):
    """o estalo: 4 quadros a 30 fps, ease-out, e para. Sem overshoot."""
    st = f", stagger:{stagger}" if stagger else ""
    return (f"tl.from('{seletor}', Object.assign({de},"
            f" {{duration:{dur}, ease:'{SNAP}'{st}}}), {em});")


def deriva(seletor, de, para, em=0.0):
    """o movimento continuo por baixo do texto: do primeiro ao ultimo quadro,
    linear, sem comeco nem fim visiveis. E o que o estilo chama de constant
    motion — e o que impede o plano de ler como cartao parado."""
    return (f"tl.fromTo('{seletor}', {de},"
            f" Object.assign({para}, {{duration:DUR, ease:'{DERIVA}'}}), {em});")


# ---------- os tres fundos -------------------------------------------------
# O estilo gira entre eles; quem escolhe e o tipo da cena, nunca o acaso.

def campo(escuro=False, semente=0):
    """a cartela creme com textura de cedula e vinco de papel, ou o campo
    editorial quase-preto. O `il-fundo` e o que deriva."""
    if escuro:
        return f"""<div class="il-fundo escuro" style="background:{PRETO}">
        <div class="il-grade"></div></div>"""
    giro = (semente % 3) - 1
    return f"""<div class="il-fundo" style="background:{CREME}">
        <div class="il-cedula"></div>
        <div class="il-vinco" style="left:{46 + giro * 8}%"></div>
      </div>"""


def css_campo():
    return f"""
  /* o fundo e maior que o quadro de proposito: e nele que a deriva acontece,
     e sem sobra ela mostraria a borda */
  .il-fundo {{ position:absolute; inset:-8%; }}
  /* a textura gravada de cedula: linhas finas cruzadas, quase invisiveis de
     perto e perceptiveis no conjunto — e o que da a materia de papel impresso */
  .il-cedula {{ position:absolute; inset:0; opacity:0.5;
    background-image:
      repeating-linear-gradient(38deg, rgba(13,13,13,0.05) 0 1px, transparent 1px 7px),
      repeating-linear-gradient(-38deg, rgba(13,13,13,0.04) 0 1px, transparent 1px 9px),
      radial-gradient(ellipse at 50% 42%, rgba(13,13,13,0.06) 0%, transparent 58%); }}
  /* o vinco: uma dobra de papel, um claro e um escuro colados */
  .il-vinco {{ position:absolute; top:-10%; bottom:-10%; width:26px;
    background:linear-gradient(90deg, transparent 0%, rgba(13,13,13,0.07) 46%,
      rgba(255,255,255,0.65) 54%, transparent 100%); }}
  .il-fundo.escuro .il-grade {{ position:absolute; inset:0; opacity:0.5;
    background-image:
      linear-gradient(to right, rgba(255,255,255,0.05) 1px, transparent 1px),
      linear-gradient(to bottom, rgba(255,255,255,0.05) 1px, transparent 1px);
    background-size:120px 120px; }}"""


def js_campo():
    """a deriva do fundo. Lateral num plano, push no outro — o estilo alterna,
    e nunca os dois ao mesmo tempo no mesmo plano."""
    return deriva('.il-fundo', "{scale:1.0, xPercent:0}", "{scale:1.05, xPercent:-1.6}")


# ---------- pecas de pagina ------------------------------------------------

def badge(acento):
    """o selo circular do canto superior esquerdo. Marca de publicacao, nao
    logo: e um circulo cheio, sem letra dentro."""
    return f'<div class="il-badge" style="background:{acento}"></div>'


def rotulo(texto, classe=""):
    """versalete espacado — o rotulo preso ao objeto que ele anota"""
    if not texto:
        return ""
    return f'<div class="il-rotulo {classe}">{_e(texto)}</div>'


def css_pagina(acento):
    return f"""
  .il-badge {{ position:absolute; left:64px; top:64px; width:76px; height:76px;
    border-radius:50%; z-index:6; }}
  .il-rotulo {{ font-family:{DIDONE}; font-variant:small-caps; font-weight:600;
    font-size:34px; letter-spacing:0.22em; color:{TINTA_2}; }}
  .il-numeral {{ font-family:{DIDONE}; font-weight:900; line-height:0.84;
    color:{TINTA}; letter-spacing:-0.02em; }}
  .il-sub {{ font-family:{DIDONE}; font-style:italic; font-weight:600;
    font-size:62px; color:{TINTA_2}; margin-top:18px; }}
  .il-dado {{ font-family:{CONDENSADA}; font-variant-numeric:tabular-nums;
    font-weight:500; color:{TINTA}; }}
  /* a linha de chamada: liga o rotulo ao ponto que ele anota */
  .il-chamada {{ position:absolute; height:2px; background:{acento}; }}
  .il-recorte {{ box-shadow:0 4px 9px rgba(13,13,13,0.20),
    0 18px 30px rgba(13,13,13,0.12); }}"""


def _css(p, **extra):
    return "\n".join([css_campo(), css_pagina(_acento(p))] + list(extra.values()))


# ---------- composicoes ----------------------------------------------------

def cartela(p):
    """a cartela de capitulo: numeral didone gigante no centro, subtitulo em
    serifa italica embaixo, badge no canto, tudo sobre a cedula que deriva."""
    linhas = _linhas(p, 3) or ["—"]
    ac = _acento(p)
    titulo = linhas[0]
    # numeral ocupa 40-60% da altura: corpo sai do comprimento da palavra
    corpo_px = max(150, min(760, int(2600 / max(3, len(titulo)))))
    corpo = f"""{campo(semente=len(titulo))}
      {badge(ac)}
      <div class="camada meio alta il-col">
        {rotulo(p.get('familia') or p.get('estado') or '')}
        <div class="il-numeral" style="font-size:{corpo_px}px">{_e(titulo)}</div>
        {''.join(f'<div class="il-sub">{_e(l)}</div>' for l in linhas[1:])}
        <div class="il-regua" style="background:{ac}"></div>
      </div>"""
    css = _css(p, mais=f"""
  .camada.meio {{ filter:none; }}
  .il-col {{ flex-direction:column; align-items:center; justify-content:center;
    padding:0 70px; text-align:center; }}
  .il-col .il-rotulo {{ margin-bottom:34px; }}
  .il-regua {{ width:180px; height:8px; margin-top:44px; transform-origin:left center; }}""")
    js = (js_campo()
          + snap('.il-rotulo', 0.06)
          + snap('.il-numeral', 0.13, "{opacity:0, y:40}")
          + snap('.il-sub', 0.26, "{opacity:0, y:22}", stagger=0.07)
          + f"tl.from('.il-regua', {{scaleX:0, duration:0.2, ease:'{SNAP}'}}, 0.34);")
    return corpo, css, js


def palavras(p):
    """a lista editorial: cada palavra e uma linha com versalete e regra, e
    elas estalam uma depois da outra. O acento marca so a ultima."""
    ps = _palavras(p, 5) or ["—"]
    ac = _acento(p)
    itens = "".join(
        f'<div class="il-item{" vivo" if i == len(ps) - 1 else ""}" data-i="{i}">'
        f'<span class="il-num">{i + 1:02d}</span>'
        f'<span class="il-palavra">{_e(w)}</span></div>' for i, w in enumerate(ps))
    corpo = f"""{campo(semente=len(ps))}
      {badge(ac)}
      <div class="camada meio alta il-col">
        <div class="il-lista">{itens}</div>
      </div>"""
    css = _css(p, mais=f"""
  .camada.meio {{ filter:none; }}
  .il-col {{ flex-direction:column; align-items:center; justify-content:center;
    padding:0 80px; }}
  .il-lista {{ width:100%; display:flex; flex-direction:column; gap:12px; }}
  .il-item {{ display:flex; align-items:baseline; gap:32px; padding:22px 0;
    border-bottom:2px solid {BORDA}; }}
  .il-num {{ font-family:{CONDENSADA}; font-variant-numeric:tabular-nums;
    font-size:38px; color:{TINTA_2}; }}
  .il-palavra {{ font-family:{DIDONE}; font-weight:800; font-size:92px;
    color:{TINTA}; line-height:1; }}
  .il-item.vivo .il-palavra {{ color:{ac}; }}""")
    js = js_campo() + snap('.il-item', 0.08, "{opacity:0, x:-34}", stagger=0.11)
    return corpo, css, js


def camadas(p):
    """as camadas do assunto, empilhadas como folhas de uma prancheta: cada
    uma entra por deslize lateral e assenta. Nao ha quique — o que da vida e a
    deriva do fundo por baixo."""
    ps = _palavras(p, 4) or ["—"]
    ac = _acento(p)
    n = len(ps)
    folhas = "".join(
        f'<div class="il-folha" data-i="{i}" style="top:{i * 148}px;'
        f' left:{i * 18}px; right:{(n - 1 - i) * 18}px">'
        f'<span class="il-rotulo">{i + 1:02d}</span>'
        f'<span class="il-nome">{_e(w)}</span></div>' for i, w in enumerate(ps))
    corpo = f"""{campo(semente=n)}
      {badge(ac)}
      <div class="camada meio alta il-col">
        <div class="il-prancheta" style="height:{n * 148 + 40}px">{folhas}</div>
      </div>"""
    css = _css(p, mais=f"""
  .camada.meio {{ filter:none; }}
  .il-col {{ flex-direction:column; align-items:center; justify-content:center;
    padding:0 60px; }}
  .il-prancheta {{ position:relative; width:100%; }}
  .il-folha {{ position:absolute; height:128px; display:flex; align-items:center;
    gap:28px; padding:0 40px; background:{T['CARTAO_VIVO']};
    border-left:10px solid {ac};
    box-shadow:0 4px 9px rgba(13,13,13,0.18), 0 18px 30px rgba(13,13,13,0.10); }}
  .il-nome {{ font-family:{DIDONE}; font-weight:800; font-size:72px; color:{TINTA}; }}""")
    js = js_campo() + snap('.il-folha', 0.08, "{opacity:0, x:120}", 0.166, stagger=0.12)
    return corpo, css, js


def indice(p):
    """o indice de destinos: nome em versalete, com a regra e o ponto de
    acento. E lista de pagina, nao menu de app."""
    ps = _palavras(p, 4) or ["—"]
    ac = _acento(p)
    marca = (p.get("texto") or "").strip()
    linhas = "".join(
        f'<div class="il-linha" data-i="{i}"><span class="il-ponto"></span>'
        f'<span class="il-nome">{_e(w)}</span>'
        f'{f"<span class=&quot;il-marca&quot;>{_e(marca)}</span>" if marca else ""}</div>'
        for i, w in enumerate(ps))
    corpo = f"""{campo(semente=len(ps))}
      {badge(ac)}
      <div class="camada meio alta il-col"><div class="il-indice">{linhas}</div></div>"""
    css = _css(p, mais=f"""
  .camada.meio {{ filter:none; }}
  .il-col {{ flex-direction:column; align-items:center; justify-content:center;
    padding:0 80px; }}
  .il-indice {{ width:100%; }}
  .il-linha {{ display:flex; align-items:center; gap:28px; padding:30px 0;
    border-bottom:2px solid {BORDA}; }}
  .il-ponto {{ width:26px; height:26px; border-radius:50%; background:{ac};
    flex:none; }}
  .il-linha .il-nome {{ font-family:{DIDONE}; font-weight:800; font-size:76px;
    color:{TINTA}; }}
  .il-marca {{ margin-left:auto; font-family:{CONDENSADA}; font-size:32px;
    letter-spacing:0.14em; text-transform:uppercase; color:{TINTA_2}; }}""")
    js = (js_campo()
          + snap('.il-linha', 0.08, "{opacity:0, x:-40}", stagger=0.13)
          + snap('.il-marca', 0.3, "{opacity:0}", 0.1, stagger=0.13))
    return corpo, css, js


def dado(p):
    """o numeral gigante com a ficha embaixo — o plano-assinatura do estilo."""
    valor = str(p.get("valor") or p.get("texto") or "").strip() or "—"
    rot = str(p.get("rotulo") or p.get("legenda") or "").strip()
    fonte = str(p.get("fonte") or "").strip()
    ac = _acento(p)
    corpo = f"""{campo(semente=len(valor))}
      {badge(ac)}
      <div class="camada meio alta il-col">
        {rotulo(rot)}
        <div class="il-numeral" style="font-size:520px">{_e(valor)}</div>
        {f'<div class="il-ficha">{_e(fonte)}</div>' if fonte else ''}
      </div>"""
    css = _css(p, mais=f"""
  .camada.meio {{ filter:none; }}
  .il-col {{ flex-direction:column; align-items:center; justify-content:center;
    text-align:center; padding:0 60px; }}
  .il-col .il-rotulo {{ margin-bottom:26px; }}
  .il-ficha {{ margin-top:40px; font-family:{CONDENSADA}; font-size:32px;
    letter-spacing:0.1em; color:{TINTA_2};
    border-top:2px solid {ac}; padding-top:18px; }}""")
    js = (js_campo() + snap('.il-rotulo', 0.06)
          + snap('.il-numeral', 0.12, "{opacity:0, y:44}")
          + snap('.il-ficha', 0.3))
    return corpo, css, js


def imagem(p):
    """o asset como RECORTE colado na pagina: sombra dura e curta, rotulo em
    versalete preso a ele por uma linha de chamada. A imagem deriva junto com
    o fundo, em paralaxe — ela anda um pouco mais que o papel."""
    asset = p.get("asset")
    if not asset:
        return cartela(p)
    ac = _acento(p)
    rot = (p.get("texto") or "").strip()
    corpo = f"""{campo(semente=3)}
      {badge(ac)}
      <div class="camada meio cheia il-col">
        <div class="il-porta">
          <div class="il-foto il-recorte"><img src="{_e(asset)}" alt=""/></div>
          {f'<div class="il-anota"><i class="il-chamada"></i>{rotulo(rot)}</div>'
           if rot else ''}
        </div>
      </div>"""
    css = _css(p, mais=f"""
  .camada.meio {{ filter:none; }}
  .il-col {{ flex-direction:column; align-items:center; justify-content:center; }}
  .il-porta {{ position:relative; width:980px; height:1420px; }}
  .il-foto {{ position:absolute; inset:0; overflow:hidden; }}
  .il-foto img {{ width:100%; height:100%; object-fit:cover; display:block; }}
  .il-anota {{ position:absolute; left:0; bottom:-96px; display:flex;
    align-items:center; gap:22px; }}
  .il-anota .il-chamada {{ position:relative; width:120px; }}""")
    js = (js_campo()
          # paralaxe: a foto anda mais que o papel. E o unico "3D" do estilo,
          # e ele e falso de proposito — sao duas camadas planas em ritmos
          # diferentes, nunca perspectiva.
          + deriva('.il-foto', "{scale:1.0, y:0}", "{scale:1.07, y:-18}")
          + snap('.il-foto', 0.04, "{opacity:0}", 0.166)
          + snap('.il-anota', 0.3, "{opacity:0, x:-30}"))
    return corpo, css, js


# ---------- as cenas de conteudo (o `tela` com modo) ------------------------

def _quadro_slop(i):
    """o motion generico, na leitura do genero: tudo centralizado, gradiente de
    fundo, mesma composicao seja qual for o assunto. O molde NAO muda — muda so
    a cor, e e a igualdade entre eles que prova o adjetivo."""
    a, b = [("#7C5CFF", "#3BC9F5"), ("#FF6B6B", "#FFB86B"), ("#2BD4A8", "#38A3F5"),
            ("#FF7AC8", "#8A5CFF"), ("#F5A623", "#F55F23"), ("#4D6BFF", "#00D4C8")][i % 6]
    barras = "".join(f'<i style="height:{h}%"></i>' for h in (46, 72, 58))
    return f"""<div class="il-vid" data-i="{i}">
        <div class="il-gradiente" style="background:linear-gradient(135deg,{a},{b})"></div>
        <div class="il-slop">
          <div class="il-s-tit"><b style="width:74%"></b><b style="width:46%"></b></div>
          <div class="il-s-marcas"><i></i><i></i><i></i></div>
          <div class="il-s-graf">{barras}</div>
        </div>
      </div>"""


def _tela_slop(p, t):
    """o mesmo molde, video atras de video. Aqui a pilha de videos genericos e
    um RECORTE colado na pagina — o estilo nao mostra tela de app, mostra
    material citado dentro de uma composicao editorial."""
    ac = _acento(p)
    n = 6
    corpo = f"""{campo(semente=2)}
      {badge(ac)}
      <div class="camada meio alta il-col">
        {rotulo('o mesmo molde')}
        <div class="il-moldura il-recorte">{''.join(_quadro_slop(i) for i in range(n))}</div>
      </div>"""
    css = _css(p, mais=f"""
  .camada.meio {{ filter:none; }}
  .il-col {{ flex-direction:column; align-items:center; justify-content:center; }}
  .il-col .il-rotulo {{ margin-bottom:26px; }}
  .il-moldura {{ position:relative; width:900px; height:1280px; overflow:hidden;
    background:{PAPEL_2}; }}
  .il-vid {{ position:absolute; inset:0; }}
  .il-gradiente {{ position:absolute; inset:0; }}
  .il-slop {{ position:absolute; inset:0; display:flex; flex-direction:column;
    align-items:center; justify-content:center; gap:8%; padding:14% 10%; }}
  .il-slop b, .il-slop i {{ display:block; background:rgba(255,255,255,0.92);
    border-radius:6px; }}
  .il-s-tit {{ width:100%; display:flex; flex-direction:column; align-items:center;
    gap:14px; }}
  .il-s-tit b {{ height:32px; }}
  .il-s-marcas {{ display:flex; gap:16px; }}
  .il-s-marcas i {{ width:68px; height:14px; border-radius:999px; opacity:0.85; }}
  .il-s-graf {{ display:flex; align-items:flex-end; gap:18px; height:22%; }}
  .il-s-graf i {{ width:48px; border-radius:6px 6px 2px 2px; opacity:0.9; }}""")
    marcas, q = [], 0.12
    for i in range(n):
        marcas.append((i, q))
        q += max(0.55, 0.9 - i * 0.07)
    troca = "".join(
        f"tl.set('.il-vid', {{autoAlpha:0}}, {x:.2f});"
        f"tl.set('.il-vid[data-i=\"{i}\"]', {{autoAlpha:1}}, {x:.2f});"
        for i, x in marcas)
    js = (js_campo() + snap('.il-rotulo', 0.04)
          + snap('.il-moldura', 0.08, "{opacity:0, y:34}", 0.166)
          + deriva('.il-moldura', "{scale:1.0}", "{scale:1.04}") + troca)
    return corpo, css, js


def _tela_recusa(p, t):
    """o video citado e a anotacao a mao por cima — a recusa e coral, riscada
    sobre o material, do jeito que se marca uma prova impressa."""
    corpo = f"""{campo(semente=4)}
      {badge(CORAL)}
      <div class="camada meio alta il-col">
        {rotulo('o resultado')}
        <div class="il-moldura il-recorte">{_quadro_slop(1)}</div>
        <svg class="il-risco" viewBox="0 0 900 1280" preserveAspectRatio="none">
          <path d="M70,120 C300,360 480,520 660,880" fill="none" stroke="{CORAL}"
                stroke-width="18" stroke-linecap="round"/>
          <path d="M660,140 C470,400 300,560 90,880" fill="none" stroke="{CORAL}"
                stroke-width="18" stroke-linecap="round"/>
        </svg>
      </div>"""
    css = _css(p, mais=f"""
  .camada.meio {{ filter:none; }}
  .il-col {{ flex-direction:column; align-items:center; justify-content:center;
    position:relative; }}
  .il-col .il-rotulo {{ margin-bottom:26px; }}
  .il-moldura {{ position:relative; width:720px; height:1000px; overflow:hidden;
    background:{PAPEL_2}; }}
  .il-vid {{ position:absolute; inset:0; }}
  .il-gradiente {{ position:absolute; inset:0; }}
  .il-slop {{ position:absolute; inset:0; display:flex; flex-direction:column;
    align-items:center; justify-content:center; gap:8%; padding:14% 10%; }}
  .il-slop b, .il-slop i {{ display:block; background:rgba(255,255,255,0.92);
    border-radius:6px; }}
  .il-s-tit {{ width:100%; display:flex; flex-direction:column; align-items:center;
    gap:14px; }}
  .il-s-tit b {{ height:32px; }}
  .il-s-marcas {{ display:flex; gap:16px; }}
  .il-s-marcas i {{ width:68px; height:14px; border-radius:999px; opacity:0.85; }}
  .il-s-graf {{ display:flex; align-items:flex-end; gap:18px; height:22%; }}
  .il-s-graf i {{ width:48px; border-radius:6px 6px 2px 2px; opacity:0.9; }}
  /* o risco cobre exatamente a moldura, nao o quadro inteiro */
  .il-risco {{ position:absolute; width:900px; height:1280px; top:auto; }}""")
    js = (js_campo() + snap('.il-rotulo', 0.04)
          + snap('.il-moldura', 0.08, "{opacity:0, y:34}", 0.166)
          + deriva('.il-moldura', "{scale:1.0}", "{scale:1.04}")
          # a anotacao APARECE DESENHANDO: e traço de mão, não carimbo pronto
          + "tl.fromTo('.il-risco path', {strokeDasharray:1400, strokeDashoffset:1400},"
            " {strokeDashoffset:0, duration:0.34, stagger:0.16,"
            " ease:'power2.inOut'}, 0.9);")
    return corpo, css, js


def _tela_regras(p, t):
    """a regra do formato acontecendo sobre um quadro real do proprio take,
    com rotulo em versalete preso a cada gesto por linha de chamada."""
    ac = _acento(p)
    fundo_img = (t.get("fundo") or "").strip()
    rot = [str(x).strip() for x in (t.get("linhas") or []) if str(x).strip()]
    rot = (rot + ["", "", ""])[:3]
    corpo = f"""{campo(escuro=True)}
      {badge(ac)}
      <div class="camada meio alta il-col">
        {rotulo(t.get('titulo') or '')}
        <div class="il-split il-recorte">
          <div class="il-apoio"></div>
          <div class="il-rosto">{f'<img src="{_e(fundo_img)}" alt=""/>' if fundo_img else ''}</div>
          <div class="il-juncao" style="background:{ac}"></div>
          <i class="il-nota n1">{_e(rot[1])}</i>
          <i class="il-nota n0">{_e(rot[0])}</i>
          <i class="il-nota n2">{_e(rot[2])}</i>
        </div>
      </div>"""
    css = _css(p, mais=f"""
  .camada.meio {{ filter:none; }}
  .il-col {{ flex-direction:column; align-items:center; justify-content:center; }}
  .il-col .il-rotulo {{ margin-bottom:24px; color:{PAPEL_2}; }}
  .il-split {{ position:relative; width:940px; height:1400px; overflow:hidden;
    background:{PRETO}; }}
  .il-apoio {{ position:absolute; left:0; right:0; top:0; height:50%;
    background:linear-gradient(150deg,{ARDOSIA} 0%,#16222E 100%); }}
  .il-rosto {{ position:absolute; left:0; right:0; bottom:0; height:50%;
    overflow:hidden; }}
  .il-rosto img {{ width:100%; height:100%; object-fit:cover;
    object-position:50% 26%; display:block; }}
  .il-juncao {{ position:absolute; left:0; right:0; top:50%; height:4px;
    transform-origin:left center; }}
  .il-nota {{ position:absolute; right:22px; font-family:{DIDONE};
    font-variant:small-caps; font-style:normal; font-weight:600; font-size:27px;
    letter-spacing:0.16em; color:{CREME}; background:rgba(13,13,13,0.55);
    padding:8px 16px; }}
  .n1 {{ top:22px; }} .n0 {{ bottom:22px; }} .n2 {{ top:50%; margin-top:34px; }}""")
    js = (js_campo() + snap('.il-rotulo', 0.04)
          + snap('.il-split', 0.08, "{opacity:0, y:30}", 0.166)
          # a ordem dos gestos E a regra: rosto embaixo, apoio em cima,
          # legenda na juncao. Deslizam, nao quicam.
          + snap('.il-rosto', 0.3, "{yPercent:55}", 0.2)
          + f"tl.from('.il-juncao', {{scaleX:0, duration:0.2, ease:'{SNAP}'}}, 0.46);"
          + snap('.il-apoio', 0.7, "{yPercent:-60}", 0.2)
          + snap('.il-nota', 0.5, "{opacity:0, x:24}", 0.13, stagger=0.3)
          + deriva('.il-rosto img', "{scale:1.0}", "{scale:1.06}"))
    return corpo, css, js


def _tela_pesquisa(p, t):
    """a pesquisa como pagina: a consulta em didone grande e os achados
    entrando como recortes de documento, um sobre o outro."""
    ac = _acento(p)
    consulta = (t.get("texto") or " ".join(_palavras(p, 3)) or "").strip()
    fichas = "".join(
        f'<div class="il-ficha-res" data-i="{i}" style="left:{i * 6}%;'
        f' top:{i * 120}px"><b style="width:{84 - i * 8}%"></b>'
        f'<b class="fraca" style="width:{60 - i * 7}%"></b></div>' for i in range(4))
    corpo = f"""{campo(semente=5)}
      {badge(ac)}
      <div class="camada meio alta il-col">
        {rotulo('pesquisa')}
        <div class="il-consulta">{_e(consulta)}<i style="background:{ac}"></i></div>
        <div class="il-achados">{fichas}</div>
      </div>"""
    css = _css(p, mais=f"""
  .camada.meio {{ filter:none; }}
  .il-col {{ flex-direction:column; align-items:center; justify-content:center;
    padding:0 70px; }}
  .il-col .il-rotulo {{ margin-bottom:22px; }}
  .il-consulta {{ position:relative; font-family:{DIDONE}; font-weight:800;
    font-size:136px; color:{TINTA}; border-bottom:4px solid {BORDA};
    padding-bottom:18px; margin-bottom:52px; }}
  .il-consulta i {{ display:inline-block; width:6px; height:88px;
    margin-left:16px; vertical-align:-14px; }}
  .il-achados {{ position:relative; width:100%; height:680px; }}
  .il-ficha-res {{ position:absolute; width:86%; padding:44px 48px;
    background:{T['CARTAO_VIVO']}; display:flex; flex-direction:column; gap:16px;
    box-shadow:0 4px 9px rgba(13,13,13,0.18), 0 16px 26px rgba(13,13,13,0.10); }}
  .il-ficha-res b {{ display:block; height:22px; background:{CROMO};
    border-radius:4px; }}
  .il-ficha-res b.fraca {{ height:16px; background:{PAPEL_2}; }}""")
    js = (js_campo() + snap('.il-rotulo', 0.04)
          + snap('.il-consulta', 0.1, "{opacity:0, y:26}", 0.166)
          + "tl.to('.il-consulta i', {opacity:0, duration:0.3, repeat:5,"
            " yoyo:true, ease:'none'}, 0.3);"
          + snap('.il-ficha-res', 0.42, "{opacity:0, x:70}", 0.166, stagger=0.17))
    return corpo, css, js


def _tela_timeline(p, t):
    """a timeline de edicao desenhada como diagrama de pagina, nao como
    captura de app: pistas chapadas, rotulo em versalete, e cada etapa
    acontecendo no instante em que a voz a nomeia."""
    ac = _acento(p)
    etapas = _palavras(p, 4) or ["corte", "J-cut", "cor", "inserts"]
    corpo = f"""{campo(escuro=True)}
      {badge(ac)}
      <div class="camada meio alta il-col">
        {rotulo('a edição')}
        <div class="il-manchete">o que ele faz sozinho</div>
        <div class="il-editor">
          <div class="il-pista il-p-ins"><div class="il-ins a"></div><div class="il-ins b"></div></div>
          <div class="il-pista il-p-vid">
            <div class="il-clipe c1"></div><div class="il-clipe c2"></div>
            <div class="il-cor" style="background:{ac}"></div>
          </div>
          <div class="il-pista il-p-aud"><div class="il-onda"></div></div>
          <div class="il-agulha" style="background:{CORAL}"></div>
        </div>
        <div class="il-etapas">
          {''.join(f'<span data-i="{i}">{_e(w)}</span>' for i, w in enumerate(etapas))}
        </div>
      </div>"""
    css = _css(p, mais=f"""
  .camada.meio {{ filter:none; }}
  .il-col {{ flex-direction:column; align-items:center; justify-content:center;
    padding:0 60px; }}
  /* o terco de cima nao pode ficar vazio: num estilo editorial ele e o lugar
     da manchete, e sem ela o diagrama flutua num campo preto grande demais */
  .il-col .il-rotulo {{ color:{CROMO}; margin-bottom:18px; }}
  .il-manchete {{ font-family:{DIDONE}; font-style:italic; font-weight:600;
    font-size:76px; color:{CREME}; margin-bottom:54px; text-align:center;
    line-height:1.05; }}
  .il-editor {{ position:relative; width:100%; }}
  .il-pista {{ position:relative; height:168px; margin-bottom:22px;
    background:rgba(255,255,255,0.07); }}
  .il-clipe {{ position:absolute; top:10px; bottom:10px; background:{PAPEL_2}; }}
  .c1 {{ left:0; width:44%; }}
  .c2 {{ left:calc(44% + 16px); right:0; }}
  .il-cor {{ position:absolute; top:10px; bottom:10px; left:calc(44% + 16px);
    right:0; opacity:0; mix-blend-mode:multiply; }}
  .il-ins {{ position:absolute; top:10px; bottom:10px; background:{CREME}; }}
  .il-ins.a {{ left:16%; width:22%; }}
  .il-ins.b {{ left:52%; width:26%; }}
  .il-onda {{ position:absolute; top:28px; bottom:28px; left:0; right:0;
    background:repeating-linear-gradient(90deg, {PAPEL_2} 0 5px, transparent 5px 11px); }}
  .il-agulha {{ position:absolute; top:-14px; bottom:-14px; left:0; width:4px; }}
  .il-etapas {{ display:flex; justify-content:space-between; width:100%;
    margin-top:34px; font-family:{DIDONE}; font-variant:small-caps;
    font-weight:600; font-size:46px; letter-spacing:0.12em; color:{CROMO}; }}
  .il-etapas span {{ opacity:0.35; }}""")

    def acende(i, em):
        return (f"tl.to('.il-etapas span[data-i=\"{i}\"]', {{opacity:1,"
                f" color:'{CREME}', duration:0.13}}, {em});")
    js = (js_campo()
          + snap('.il-pista', 0.06, "{opacity:0, x:-60}", 0.166, stagger=0.09)
          + "tl.set('.c2', {opacity:0}, 0);"
          + "tl.to('.c2', {opacity:1, duration:0.05}, 0.62);" + acende(0, 0.62)
          + "tl.to('.il-onda', {x:-68, duration:0.2, ease:'power3.out'}, 1.25;)".replace(";)", ");")
          + acende(1, 1.25)
          + "tl.to('.il-cor', {opacity:0.9, duration:0.22, ease:'power2.out'}, 1.95);"
          + acende(2, 1.95)
          + snap('.il-ins', 2.6, "{opacity:0, y:-90}", 0.166, stagger=0.16)
          + acende(3, 2.6)
          + "tl.to('.il-agulha', {xPercent:0, x:'100%', duration:Math.max(1.2, DUR-3.4),"
            " ease:'none'}, 3.2);")
    return corpo, css, js


def _tela_distribuicao(p, t):
    """de onde sai e para onde vai, desenhado como mapa de pagina: as fontes em
    cima, os destinos embaixo, e o material descendo entre eles."""
    ac = _acento(p)
    origens = _palavras(p, 2) or ["Metricool", "Zernio"]
    destinos = [str(x).strip() for x in (t.get("destinos") or
                ["Instagram", "Facebook", "TikTok", "YouTube"]) if str(x).strip()][:4]
    corpo = f"""{campo(semente=6)}
      {badge(ac)}
      <div class="camada meio alta il-col">
        {rotulo('publicação')}
        <div class="il-manchete">um post, quatro redes</div>
        <div class="il-fontes">
          {''.join(f'<div class="il-fonte">{_e(o)}</div>' for o in origens)}
        </div>
        <div class="il-rota">
          {''.join(f'<i class="il-trilho" data-i="{i}" style="background:{ac}"></i>'
                   for i in range(len(destinos)))}
          {''.join(f'<div class="il-post" data-i="{i}"></div>'
                   for i in range(len(destinos)))}
        </div>
        <div class="il-redes">
          {''.join(f'<div class="il-rede" data-i="{i}">{_e(d)}</div>'
                   for i, d in enumerate(destinos))}
        </div>
      </div>"""
    css = _css(p, mais=f"""
  .camada.meio {{ filter:none; }}
  .il-col {{ flex-direction:column; align-items:center; justify-content:center;
    padding:0 50px; }}
  .il-col .il-rotulo {{ margin-bottom:16px; }}
  .il-manchete {{ font-family:{DIDONE}; font-style:italic; font-weight:600;
    font-size:72px; color:{TINTA_2}; margin-bottom:46px; text-align:center; }}
  .il-fontes {{ display:flex; gap:24px; }}
  .il-fonte {{ font-family:{DIDONE}; font-weight:800; font-size:92px; color:{TINTA};
    padding:16px 30px; border-bottom:6px solid {ac}; }}
  .il-rota {{ position:relative; width:100%; height:460px; }}
  .il-trilho {{ position:absolute; top:0; bottom:0; width:2px; opacity:0.35;
    transform-origin:top center; }}
  .il-trilho[data-i="0"] {{ left:12%; }} .il-trilho[data-i="1"] {{ left:37%; }}
  .il-trilho[data-i="2"] {{ left:62%; }} .il-trilho[data-i="3"] {{ left:87%; }}
  .il-post {{ position:absolute; top:0; width:104px; height:140px;
    background:{T['CARTAO_VIVO']};
    box-shadow:0 4px 9px rgba(13,13,13,0.20), 0 14px 22px rgba(13,13,13,0.10); }}
  .il-post[data-i="0"] {{ left:calc(12% - 36px); }}
  .il-post[data-i="1"] {{ left:calc(37% - 36px); }}
  .il-post[data-i="2"] {{ left:calc(62% - 36px); }}
  .il-post[data-i="3"] {{ left:calc(87% - 36px); }}
  .il-redes {{ display:flex; justify-content:space-between; width:100%; }}
  .il-rede {{ font-family:{DIDONE}; font-variant:small-caps; font-weight:600;
    font-size:44px; letter-spacing:0.10em; color:{TINTA_2}; }}""")
    voos = "".join(
        f"tl.from('.il-trilho[data-i=\"{i}\"]', {{scaleY:0, duration:0.18,"
        f" ease:'{SNAP}'}}, {0.34 + i * 0.2:.2f});"
        f"tl.fromTo('.il-post[data-i=\"{i}\"]', {{y:-20, opacity:0}},"
        f" {{y:450, opacity:1, duration:0.4, ease:'power2.inOut'}},"
        f" {0.4 + i * 0.2:.2f});"
        f"tl.to('.il-post[data-i=\"{i}\"]', {{opacity:0, duration:0.1}},"
        f" {0.8 + i * 0.2:.2f});"
        f"tl.to('.il-rede[data-i=\"{i}\"]', {{color:'{TINTA}', duration:0.12}},"
        f" {0.78 + i * 0.2:.2f});"
        for i in range(len(destinos)))
    js = (js_campo() + snap('.il-fonte', 0.06, "{opacity:0, y:-24}", 0.166, stagger=0.1)
          + snap('.il-rede', 0.2, "{opacity:0}", 0.13, stagger=0.08) + voos)
    return corpo, css, js


def _tela_acervo(p, t):
    """a pagina com uma JANELA VAZIA, onde o `acervo.py` encaixa o trecho de
    video de terceiro por cima, com ffmpeg.

    O HTML nao toca no video: navegador tocando `<video>` dentro de uma captura
    quadro a quadro e fonte de dessincronia — o tempo do elemento nao e o tempo
    da linha. Aqui o HTML entrega so a pagina (creme, selo, rotulo, credito) e
    a moldura em `MOLDURA_ACERVO`; o trecho entra depois, no mesmo retangulo.

    O credito fica na propria cena, embaixo da janela. Nao e enfeite: e o que
    separa citacao de repost, e sai junto com a imagem que foi citada."""
    ac = _acento(p)
    x, y, lw, lh = MOLDURA_ACERVO
    creditos = [c for c in (t.get("creditos") or []) if str(c).strip()]
    corpo = f"""{campo(semente=2)}
      {badge(ac)}
      <div class="il-topo">{rotulo(t.get('titulo') or 'o mesmo molde')}</div>
      <div class="il-janela"></div>
      {f'<div class="il-credito">{_e(" · ".join(creditos))}</div>' if creditos else ''}"""
    css = _css(p, mais=f"""
  .il-topo {{ position:absolute; left:0; right:0; top:{y - 78}px;
    display:flex; justify-content:center; }}
  /* a moldura vazia: e so o furo e a sombra. O conteudo vem por ffmpeg. */
  .il-janela {{ position:absolute; left:{x}px; top:{y}px; width:{lw}px;
    height:{lh}px; background:{PAPEL_2};
    box-shadow:0 4px 9px rgba(13,13,13,0.20), 0 18px 30px rgba(13,13,13,0.12); }}
  .il-credito {{ position:absolute; left:{x}px; right:{1080 - x - lw}px;
    top:{y + lh + 26}px; font-family:{CONDENSADA}; font-size:26px;
    letter-spacing:0.08em; color:{TINTA_2}; text-align:right; }}""")
    # a janela NAO pode animar depois do quadro 0: o ffmpeg sobrepoe num
    # retangulo fixo, e uma moldura que escala deixaria o video fora dela
    js = (js_campo() + snap('.il-topo', 0.04)
          + snap('.il-credito', 0.3, "{opacity:0}", 0.13))
    return corpo, css, js


def tela(p):
    """o `modo` do plano escolhe o desenho — os mesmos modos do estilo
    `gravacao`, redesenhados na gramatica editorial."""
    t = p.get("tela") if isinstance(p.get("tela"), dict) else {}
    modo = (t.get("modo") or "").strip().lower()
    por_modo = {
        "acervo": _tela_acervo,
        "slop": _tela_slop, "generico": _tela_slop, "repeticao": _tela_slop,
        "recusa": _tela_recusa, "regras": _tela_regras,
        "pesquisa": _tela_pesquisa, "timeline": _tela_timeline,
        "distribuicao": _tela_distribuicao, "distribuição": _tela_distribuicao,
    }
    fn = por_modo.get(modo)
    if fn:
        return fn(p, t)
    # sem modo conhecido, a tela vira cartela de capitulo — nunca janela de
    # software: este estilo nao tem app nenhum no vocabulario
    return cartela(dict(p, texto=(t.get("titulo") or p.get("texto") or "")))


CORPOS = {
    "cartela": cartela,
    "palavras": palavras,
    "camadas": camadas,
    "indice": indice,
    "dado": dado,
    "tela": tela,
    "objeto": imagem, "personagem": imagem, "obra": imagem, "arquivo": imagem,
    "cotidiano": imagem, "broll": imagem, "hibrido": imagem,
}
