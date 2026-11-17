#!/usr/bin/env python3
"""
hf_gravacao.py — as composicoes do estilo `gravacao`: cards de UI sobre branco.

Pedido do dono em 2026-09-12, com a referencia decupada quadro a quadro:

    "Nao e 2D nem 3D. E motion design de gravacao de tela: prints e UI reais de
    apps tratados como cards flutuando sobre uma tela branca continua, combinados
    com tipografia cinetica queimada por cima."

O que a decupagem mediu, e que vira regra aqui:

- **branco puro por baixo de tudo** (#FFFFFF), sem horizonte, sem sala, sem
  textura, sem gradiente. O canvas e continuo: ele nunca troca.
- **nenhum corte duro no miolo** — deteccao de corte a 0,3 nao achou um so em
  42 s. Transicao e troca de elemento sobre o mesmo branco: um card saindo em
  escala enquanto o proximo entra.
- **tudo seco e rapido**: entrada em escala crescente com overshoot curto
  (~0,25 s, `back.out`). Nada faz deriva lenta, nada tem movimento continuo
  longo. Um conceito a cada 4-6 s.
- **Grow Effect**: o print cresce para ALEM da propria moldura — e o efeito que
  a referencia demonstra pelo nome.
- **cards empilhados se separam lateralmente**; balao de iMessage sobe de baixo
  com mola.
- **cor so da UI nativa**: azul iMessage #007AFF, cromo azul-acinzentado do iOS,
  vermelho do Instagram. Nenhuma cor de marca entra.
- **terco inferior limpo**, sempre: e onde a legenda queimada mora.
- **titulo de display com extrusao**, no terco superior, com uma copia fantasma
  cinza deslocada para cima/esquerda que desliza ate o registro.

Uma decisao que a referencia nao fecha e esta foi tomada: na referencia a face
do titulo e branca, porque ela cai sobre print. Aqui o titulo cai sobre o branco
do canvas, onde face branca some — entao a face e a tinta (#0B0B0C) e o fantasma
e o cromo (#C7C9CE). O gesto (fantasma deslocado que desliza ate o registro) e o
que faz o estilo, e esse esta inteiro.

O "Do not render any legible text" da direcao vale para a IMAGEM GERADA, nao
para estas composicoes: aqui a tipografia e desenhada em fonte de verdade, que e
justamente o motivo de nao pedi-la ao gerador.

Cada funcao devolve `(corpo, css, js)`, o mesmo contrato de `hf.py`.

**Nome de classe colide.** A CSS do estilo entra DEPOIS da folha comum do
`hf.py` (`CSS_TIPOGRAFIA`), entao repetir um nome de la nao substitui a regra:
sobrescreve as propriedades que voce escreveu e herda as que voce nao escreveu.
Foi o que aconteceu com `.risco` — a folha comum a ancora em `position:absolute;
left:-2%; top:52%`, e a barra azul do titulo saiu grudada na borda esquerda do
quadro, com o halo vermelho do `box-shadow` original. Dai o prefixo `g-`. Os
nomes ocupados hoje sao: `.risco`, `.riscado`, `.divisor`, `.destaque`,
`.centro`, `.baixa`, `.matte-box`, `.matte-text`, `.tag-mono`, `.tipografia`.
"""
import html

from estilos import MOTION

T = MOTION["gravacao"]["tokens"]

BRANCO = T["FUNDO"]
CINZA = T["SUPERFICIE"]          # o cinza de campo do iOS
TINTA = T["TEXTO"]
TINTA_2 = T["TEXTO_2"]
AZUL = T["CIANO"]                # iMessage
CROMO = T["CROMO"]               # o cromo azul-acinzentado, e o fantasma
VERMELHO = T["NEGADO"]           # o vermelho do Instagram
VERDE = T["ACIDO"]
BOLHA = T["BOLHA"]
BOLHA_EU = T["BOLHA_EU"]
BORDA = T["BORDA"]
DISPLAY = T["FONTE_TITULO"]
SANS = T["FONTE_LEITURA"]
MONO = T["FONTE_MONO"]

# a sombra do card: um contato curto e um espalhamento largo. E a unica
# profundidade do estilo — nao ha luz, nao ha chao, nao ha perspectiva.
SOMBRA = "0 2px 5px rgba(17,24,39,0.10), 0 22px 44px rgba(17,24,39,0.16)"
SOMBRA_FUNDA = "0 4px 10px rgba(17,24,39,0.10), 0 40px 80px rgba(17,24,39,0.20)"

RAIO = 44        # raio de canto do card grande (a moldura de telefone do iOS)
RAIO_P = 26      # raio do card pequeno


def _e(t):
    return html.escape(str(t or ""), quote=True)


def _linhas(p, maximo=4):
    """as linhas de texto do plano, venham de onde vierem"""
    cru = p.get("linhas") or [l for l in str(p.get("texto") or "").split("\n")]
    linhas = [str(x).strip() for x in cru if str(x).strip()]
    return linhas[:maximo]


def _palavras(p, maximo=5):
    cru = p.get("palavras") or _linhas(p, maximo)
    return [str(x).strip() for x in cru if str(x).strip()][:maximo]


# ---------- os gestos do estilo -------------------------------------------
# Sao tres, e nenhum dura mais que um quarto de segundo. Fora deles nao ha
# movimento neste estilo: nada gira, nada deriva, nada pulsa em loop.

ENTRA = "back.out(2.4)"          # a escala crescente com quique curto
SAI = "power2.in"


def entrar(seletor, em=0.0, escala=0.72, dur=0.25, stagger=None):
    """o gesto-mae: o card vem de menor e passa um fio do tamanho final."""
    st = f", stagger:{stagger}" if stagger else ""
    return (f"tl.from('{seletor}', {{scale:{escala}, opacity:0, duration:{dur},"
            f" ease:'{ENTRA}'{st}}}, {em});")


def sair(seletor, antes=0.28, escala=1.16):
    """a saida e o mesmo gesto ao contrario: cresce e some. Nunca um corte —
    a decupagem nao achou um corte duro no miolo inteiro da referencia."""
    return (f"tl.to('{seletor}', {{scale:{escala}, opacity:0, duration:{antes},"
            f" ease:'{SAI}'}}, DUR-{antes});")


def subir_mola(seletor, em=0.0, stagger=0.12):
    """o balao do iMessage: sobe de baixo com mola, nunca aparece parado."""
    return (f"tl.from('{seletor}', {{y:90, scale:0.8, opacity:0, duration:0.34,"
            f" stagger:{stagger}, ease:'back.out(1.9)'}}, {em});")


# ---------- pecas de interface --------------------------------------------

def barra_status(hora="9:41"):
    """a barra de status do iOS. `9:41` e a hora de toda captura da Apple —
    e o detalhe que faz o card ler como print, e nao como desenho de card."""
    return f"""<div class="statusbar">
        <span class="hora">{_e(hora)}</span>
        <span class="dir"><i class="sinal"></i><i class="wifi"></i><i class="bat"></i></span>
      </div>"""


def css_interface():
    return f"""
  .card {{ background:{BRANCO}; border-radius:{RAIO}px; box-shadow:{SOMBRA};
    overflow:hidden; }}
  .card.fundo {{ box-shadow:{SOMBRA_FUNDA}; }}
  .statusbar {{ display:flex; justify-content:space-between; align-items:center;
    padding:26px 44px 10px; font-family:{SANS}; font-weight:600; font-size:30px;
    color:{TINTA}; }}
  .statusbar .dir {{ display:flex; gap:12px; align-items:center; }}
  .statusbar i {{ display:block; background:{TINTA}; border-radius:4px; }}
  .statusbar .sinal {{ width:34px; height:20px;
    clip-path:polygon(0 70%,22% 70%,22% 100%,0 100%,0 70%,28% 45%,50% 45%,50% 100%,
      28% 100%,28% 45%,56% 22%,78% 22%,78% 100%,56% 100%,56% 22%,84% 0,100% 0,
      100% 100%,84% 100%); }}
  .statusbar .wifi {{ width:30px; height:22px;
    clip-path:polygon(50% 100%,0 34%,18% 18%,50% 48%,82% 18%,100% 34%); }}
  .statusbar .bat {{ width:44px; height:22px; border-radius:7px; }}
  .navbar {{ display:flex; align-items:center; gap:18px; padding:16px 40px 22px;
    border-bottom:1px solid {BORDA}; font-family:{SANS}; }}
  .navbar .volta {{ width:22px; height:22px; border-left:5px solid {AZUL};
    border-bottom:5px solid {AZUL}; transform:rotate(45deg); border-radius:2px; }}
  .navbar .titulo {{ font-size:34px; font-weight:600; color:{TINTA}; }}
  .navbar .acao {{ margin-left:auto; font-size:32px; color:{AZUL}; }}
  .icone {{ border-radius:24%; flex:none; }}"""


def titulo(texto, olho=""):
    """o titulo de display: face em tinta e uma copia fantasma cinza deslocada
    para cima/esquerda, que desliza ate o registro."""
    if not texto:
        return ""
    return f"""<div class="display">
        {f'<div class="olho">{_e(olho)}</div>' if olho else ''}
        <div class="palco-titulo">
          <div class="fantasma" aria-hidden="true">{_e(texto)}</div>
          <div class="face">{_e(texto)}</div>
        </div>
      </div>"""


def css_titulo(tamanho=126):
    return f"""
  .display {{ width:100%; text-align:center; }}
  .olho {{ font-family:{SANS}; font-weight:700; font-size:28px; letter-spacing:0.18em;
    text-transform:uppercase; color:{TINTA_2}; margin-bottom:22px; }}
  .palco-titulo {{ position:relative; display:inline-block; }}
  .face, .fantasma {{ font-family:{DISPLAY}; font-size:{tamanho}px; line-height:0.94;
    letter-spacing:0.005em; text-transform:uppercase; }}
  .face {{ color:{TINTA}; position:relative; }}
  /* a extrusao e do fantasma, nao da face: assim a face fica limpa e a
     profundidade inteira desliza de uma vez ate o registro */
  .fantasma {{ position:absolute; inset:0; color:{CROMO};
    text-shadow:-2px -2px 0 {CROMO}, -4px -4px 0 {CROMO}, -6px -6px 0 {CROMO},
      -8px -8px 0 {CROMO}, -10px -10px 0 {CROMO}, -12px -12px 0 {CROMO}; }}"""


def js_titulo(em=0.06):
    """o fantasma entra deslocado e desliza ate o registro; a face entra junto,
    em escala. Os dois param no mesmo quadro — depois disso nada mais se move."""
    return (f"tl.from('.face', {{scale:0.78, opacity:0, duration:0.26,"
            f" ease:'{ENTRA}'}}, {em});"
            f"tl.from('.fantasma', {{x:-46, y:-46, opacity:0, duration:0.34,"
            f" ease:'power3.out'}}, {em});"
            f"tl.from('.olho', {{y:-16, opacity:0, duration:0.22,"
            f" ease:'power3.out'}}, {em + 0.1});")


def _css(**extra):
    return "\n".join([css_interface()] + list(extra.values()))


def _js(extra=""):
    return extra


# ---------- composicoes ----------------------------------------------------

def cartela(p):
    """a cartela e um titulo de display sobre o branco, e mais nada. A
    referencia usa exatamente isso entre um card e o proximo: o canvas fica, o
    elemento troca."""
    linhas = _linhas(p, 3) or ["—"]
    corpo = f"""<div class="camada meio alta col">
        <div class="bloco">
          {titulo(" ".join(linhas) if len(linhas) == 1 else linhas[0],
                  olho=p.get('familia') or p.get('estado') or '')}
          {''.join(f'<div class="sub">{_e(l)}</div>' for l in linhas[1:])}
          <div class="g-risco"></div>
        </div>
      </div>"""
    # O risco mora DENTRO do bloco, e o bloco centra os proprios filhos. Deixar
    # o centro por conta do `align-items` herdado da `.camada` poe uma barra de
    # 280 px na borda esquerda do quadro assim que algo mexe no eixo cruzado.
    css = _css(titulo=css_titulo(132), mais=f"""
  .camada.meio {{ filter:none; }}
  .col {{ flex-direction:column; align-items:center; justify-content:center;
    padding:0 80px; }}
  .bloco {{ display:flex; flex-direction:column; align-items:center;
    justify-content:center; width:100%; }}
  .sub {{ font-family:{SANS}; font-weight:600; font-size:46px; color:{TINTA_2};
    margin-top:26px; text-align:center; }}
  .g-risco {{ width:280px; height:10px; border-radius:5px; background:{AZUL};
    margin-top:48px; transform-origin:center; }}""")
    js = _js(js_titulo()
             + "tl.from('.sub', {y:24, opacity:0, duration:0.22, stagger:0.08,"
               f" ease:'{ENTRA}'}}, 0.3);"
             + "tl.from('.g-risco', {scaleX:0, duration:0.28, ease:'power3.out'}, 0.4);"
             + sair('.display, .sub, .g-risco'))
    return corpo, css, js


def palavras(p):
    """cada palavra e um chip de UI que entra em escala, uma depois da outra.
    Nao ha barra de cor nem caixa alta esticada: chip de interface, so isso."""
    ps = _palavras(p, 5) or _linhas(p, 5) or ["—"]
    aceso = len(ps) - 1
    corpo = f"""<div class="camada meio alta col">
        <div class="chips">
          {''.join(f'<div class="chip{" vivo" if i == aceso else ""}">{_e(w)}</div>'
                   for i, w in enumerate(ps))}
        </div>
      </div>"""
    css = _css(mais=f"""
  .camada.meio {{ filter:none; }}
  .col {{ flex-direction:column; align-items:center; justify-content:center; padding:0 70px; }}
  .chips {{ display:flex; flex-direction:column; align-items:center; gap:28px; }}
  .chip {{ padding:26px 54px; border-radius:999px; background:{CINZA};
    box-shadow:{SOMBRA}; font-family:{SANS}; font-weight:700; font-size:62px;
    color:{TINTA}; white-space:nowrap; }}
  .chip.vivo {{ background:{AZUL}; color:#FFFFFF; }}""")
    js = _js(entrar('.chip', 0.08, 0.66, 0.25, stagger=0.13) + sair('.chip'))
    return corpo, css, js


def camadas(p):
    """cards empilhados que se separam lateralmente — o gesto que a referencia
    mostra quando enumera partes de uma mesma coisa. Eles entram JUNTOS, como
    uma pilha, e so depois se abrem: separar sem empilhar antes nao le."""
    ps = _palavras(p, 4) or ["—"]
    n = len(ps)
    corpo = f"""<div class="camada meio alta col">
        <div class="pilha">
          {''.join(f'<div class="folha" data-i="{i}"><span>{_e(w)}</span>'
                   f'<i class="marca"></i></div>' for i, w in enumerate(ps))}
          <div class="agulha"></div>
        </div>
      </div>"""
    css = _css(mais=f"""
  .camada.meio {{ filter:none; }}
  .col {{ flex-direction:column; align-items:center; justify-content:center; }}
  .pilha {{ position:relative; width:820px; height:{n * 150 + 60}px; }}
  .folha {{ position:absolute; left:0; right:0; height:132px; display:flex;
    align-items:center; gap:30px; padding:0 44px; border-radius:{RAIO_P}px;
    background:{BRANCO}; box-shadow:{SOMBRA}; font-family:{SANS};
    font-weight:600; font-size:56px; color:{TINTA}; }}
  .folha .marca {{ margin-left:auto; width:34px; height:34px; border-radius:50%;
    background:{CINZA}; }}
  .folha:last-child .marca {{ background:{AZUL}; }}
  /* a agulha: depois que as faixas estao montadas, ela atravessa a timeline.
     E o que faz os 8 s terem fim — sem ela a cena fica parada os ultimos
     tres segundos, que foi a reclamacao da Sofia sobre este plano. */
  .agulha {{ position:absolute; top:-26px; bottom:-26px; left:0; width:6px;
    background:{AZUL}; border-radius:3px; box-shadow:0 0 0 1px rgba(255,255,255,0.6); }}""")
    # posicao final: uma abaixo da outra, com um desencontro lateral de 26 px
    # por folha — e o "se separam lateralmente" da decupagem.
    # `top:450px` sem aspas NAO e JavaScript valido: o script inteiro da cena
    # morre em SyntaxError, nenhum tween roda e as quatro folhas ficam
    # empilhadas em top:0 — uma so aparece. Foi o que saiu no M12 as 07:59.
    coloca = "".join(
        f"gsap.set('.folha[data-i=\"{i}\"]',"
        f" {{top:'{i * 150}px', x:{(i - (n - 1) / 2) * 26:.0f}}});" for i in range(n))
    js = _js(
        coloca
        # entram como pilha: todas no lugar da primeira, sobrepostas
        + f"tl.from('.folha', {{top:0, x:0, scale:0.8, opacity:0, duration:0.28,"
          f" stagger:0.09, ease:'{ENTRA}'}}, 0.06);"
        # a agulha so existe depois da ultima faixa, e varre o que sobra da cena
        + f"tl.set('.agulha', {{opacity:0}}, 0);"
        + f"tl.to('.agulha', {{opacity:1, duration:0.12}}, {0.1 + n * 0.09 + 0.3:.2f});"
        + f"tl.fromTo('.agulha', {{x:0}}, {{x:814, duration:Math.max(0.9, DUR-"
          f"{0.1 + n * 0.09 + 0.7:.2f}), ease:'none'}}, {0.1 + n * 0.09 + 0.4:.2f});"
        + sair('.folha, .agulha'))
    return corpo, css, js


def indice(p):
    """a lista de apps: cada linha e uma linha de tabela do iOS, com o quadrado
    do icone, o nome e a seta. Onde o vox poria carimbo, aqui vai UI."""
    ps = _palavras(p, 4) or ["—"]
    # os quadrados de icone tomam a cor da UI de cada app, na ordem da lista
    cores = [VERMELHO, TINTA, VERMELHO, AZUL]
    # quando o plano traz `texto`, cada linha recebe a marca de estado no fim —
    # e o que transforma a lista num aviso de "publicado", em vez de um menu
    marca = (p.get("texto") or "").strip()
    fim = (f'<b class="chip">{_e(marca)}</b>' if marca else '<b class="seta"></b>')
    linhas = "".join(
        f'<div class="linha"><i class="icone" style="background:{cores[i % len(cores)]}">'
        f'</i><span>{_e(w)}</span>{fim}</div>'
        for i, w in enumerate(ps))
    corpo = f"""<div class="camada meio alta col">
        <div class="card fundo lista">{linhas}</div>
      </div>"""
    css = _css(mais=f"""
  .camada.meio {{ filter:none; }}
  .col {{ flex-direction:column; align-items:center; justify-content:center; }}
  .lista {{ width:840px; padding:16px 0; }}
  .linha {{ display:flex; align-items:center; gap:34px; padding:34px 46px;
    font-family:{SANS}; font-weight:600; font-size:56px; color:{TINTA}; }}
  .linha + .linha {{ border-top:1px solid {BORDA}; }}
  .linha .icone {{ width:92px; height:92px; }}
  .seta {{ margin-left:auto; width:22px; height:22px; border-top:6px solid {CROMO};
    border-right:6px solid {CROMO}; transform:rotate(45deg); border-radius:2px; }}
  .chip {{ margin-left:auto; padding:12px 28px; border-radius:999px;
    background:{VERDE}; color:#FFFFFF; font-size:34px; font-weight:700; }}""")
    js = _js(entrar('.lista', 0.05, 0.82, 0.26)
             + "tl.from('.linha', {x:-40, opacity:0, duration:0.22, stagger:0.1,"
               " ease:'power3.out'}, 0.2);"
             # a marca acende DEPOIS da linha assentar: primeiro chega, depois publica
             + f"tl.from('.chip', {{scale:0, duration:0.22, stagger:0.1,"
               f" ease:'{ENTRA}'}}, 0.44);"
             + sair('.lista'))
    return corpo, css, js


# ---------- o video de outra pessoa ---------------------------------------
# Um retangulo que LE como quadro de video sem ser video nenhum: faixa de cor
# no alto, massa escura embaixo, um bloco claro fora do centro. Cada semente da
# um arranjo diferente — e a diferenca entre eles que faz a repeticao do
# tratamento virar argumento. Nenhum deles imita canal de ninguem.
_MASSAS = [
    (AZUL, "18% 12%", "62% 54%"), (VERMELHO, "56% 20%", "20% 48%"),
    (T["AMBAR"], "12% 48%", "58% 14%"), (VERDE, "48% 52%", "16% 18%"),
    (CROMO, "30% 16%", "44% 60%"), (TINTA_2, "60% 46%", "22% 22%"),
]
# a mesma palavra em seis tipografias: o sintoma que a fala nao nomeia
_FACES = [DISPLAY, "'Archivo Black', sans-serif", "'Playfair Display', serif",
          "'Courier Prime', monospace", "'Fraunces', serif",
          f"{SANS}"]


def _quadro(i, legenda=""):
    """um quadro de video com o tratamento automatico ja por cima: a legenda
    amarela no meio, o emoji colado no canto. O tratamento e SEMPRE o mesmo; o
    que muda e o video por baixo — e a fonte da legenda, que e o sintoma.

    O que faz isto LER como quadro de video nao e a cor: e a mobilia. Sem a
    barra de progresso, o botao de play e uma figura recortada, o retangulo
    vira mancha colorida e a cena inteira perde o chao. (Foi o que saiu na
    primeira tentativa: seis borroes, nenhum video.)"""
    cor, a, b = _MASSAS[i % len(_MASSAS)]
    face = _FACES[i % len(_FACES)]
    # a figura muda de lugar e de tamanho a cada video: e a diferenca entre
    # eles que faz a igualdade do tratamento pesar
    fx, fy, fw = [(30, 34, 34), (58, 28, 30), (44, 40, 42),
                  (24, 30, 28), (62, 38, 32), (40, 26, 36)][i % 6]
    return f"""<div class="vid" data-i="{i}">
        <div class="massa" style="background:
          radial-gradient(closest-side at {a}, {cor}44 0%, transparent 60%),
          linear-gradient(160deg,#E9E9EE 0%,#C6C6D0 60%,#AFAFBA 100%)"></div>
        <div class="chao" style="background:
          linear-gradient(0deg, rgba(11,11,12,0.30) 0%, transparent 46%)"></div>
        <div class="figura" style="left:{fx}%; top:{fy}%; width:{fw}%">
          <i class="cabeca"></i><i class="tronco"></i>
        </div>
        <div class="play"></div>
        <div class="barra"><i style="width:{28 + i * 11}%"></i></div>
        {f'<div class="auto-legenda" style="font-family:{face}">{_e(legenda)}</div>'
         if legenda else ''}
        <div class="auto-emoji">🔥</div>
      </div>"""


def _css_quadro(l=760, a=1040):
    return f"""
  .moldura {{ position:relative; width:{l}px; height:{a}px; border-radius:{RAIO}px;
    overflow:hidden; box-shadow:{SOMBRA_FUNDA}; background:{CINZA}; }}
  .vid {{ position:absolute; inset:0; }}
  .massa {{ position:absolute; inset:0; }}
  .chao {{ position:absolute; inset:0; }}
  /* a figura: cabeca e ombros, que e o que quase todo video vertical tem.
     Um vulto borrado so vira mancha — o que faz ler como gente e a silhueta
     ter DUAS partes com a proporcao certa entre elas. */
  .figura {{ position:absolute; aspect-ratio:0.66; }}
  .figura i {{ position:absolute; display:block; background:rgba(11,11,12,0.42); }}
  .cabeca {{ left:29%; top:0; width:42%; aspect-ratio:0.86; border-radius:48%; }}
  .tronco {{ left:0; right:0; top:38%; bottom:0;
    border-radius:46% 46% 12% 12% / 62% 62% 8% 8%; }}
  .play {{ position:absolute; left:50%; top:50%; width:130px; height:130px;
    margin:-65px 0 0 -65px; border-radius:50%; background:rgba(255,255,255,0.86);
    clip-path:circle(50%); }}
  .play::after {{ content:''; position:absolute; left:52%; top:50%;
    transform:translate(-50%,-50%); border-left:44px solid {TINTA};
    border-top:26px solid transparent; border-bottom:26px solid transparent; }}
  .barra {{ position:absolute; left:6%; right:6%; bottom:5%; height:8px;
    border-radius:4px; background:rgba(255,255,255,0.55); overflow:hidden; }}
  .barra i {{ display:block; height:100%; background:#FFFFFF; }}
  /* o tratamento automatico: sempre no MESMO lugar, em todos */
  .auto-legenda {{ position:absolute; left:6%; right:6%; top:46%; text-align:center;
    font-size:76px; line-height:1.05; color:{TINTA}; background:#F2DE4A;
    padding:10px 0; text-transform:uppercase; }}
  .auto-emoji {{ position:absolute; right:7%; top:12%; font-size:96px; }}"""


def _slop(i):
    """um quadro de motion graphics generico — o "slop".

    Nao e opiniao: e o que a pesquisa do genero descreve, e foi o que o dono
    pediu para mostrar em vez de escrever a palavra. Tudo centrado ao meio, no
    nivel do olho, sem movimento de camera; gradiente de fundo; titulo grande
    no centro; tres marcadores iguais; um grafico de tres barras; e um rodape
    de terco inferior. O molde e SEMPRE o mesmo — muda so a cor. E a igualdade
    entre eles que faz o argumento.

    O texto e barra borrada, nao palavra: inventar frase para o video de
    terceiro seria por na boca de alguem o que essa pessoa nao disse."""
    a, b = [("#7C5CFF", "#3BC9F5"), ("#FF6B6B", "#FFB86B"), ("#2BD4A8", "#38A3F5"),
            ("#FF7AC8", "#8A5CFF"), ("#F5A623", "#F55F23"), ("#4D6BFF", "#00D4C8")][i % 6]
    barras = "".join(f'<i style="height:{h}%"></i>' for h in (46, 72, 58))
    return f"""<div class="vid" data-i="{i}">
        <div class="massa" style="background:linear-gradient(135deg,{a} 0%,{b} 100%)"></div>
        <div class="slop">
          <div class="s-titulo"><b style="width:72%"></b><b style="width:48%"></b></div>
          <div class="s-marcas"><i></i><i></i><i></i></div>
          <div class="s-grafico">{barras}</div>
          <div class="s-rodape"><b style="width:54%"></b></div>
        </div>
      </div>"""


def _css_slop():
    return """
  .slop { position:absolute; inset:0; display:flex; flex-direction:column;
    align-items:center; justify-content:center; gap:7%; padding:12% 9%; }
  .slop b, .slop i { display:block; background:rgba(255,255,255,0.92);
    border-radius:8px; }
  .s-titulo { width:100%; display:flex; flex-direction:column; align-items:center;
    gap:14px; }
  .s-titulo b { height:34px; }
  .s-marcas { display:flex; gap:18px; }
  .s-marcas i { width:74px; height:16px; border-radius:999px; opacity:0.85; }
  .s-grafico { display:flex; align-items:flex-end; gap:20px; height:24%; }
  .s-grafico i { width:54px; border-radius:8px 8px 2px 2px; opacity:0.9; }
  .s-rodape { position:absolute; left:9%; right:9%; bottom:9%; display:flex;
    justify-content:center; }
  .s-rodape b { height:20px; opacity:0.8; }"""


def _tela_slop(p, t):
    """o mesmo molde, video atras de video: a repeticao E o argumento.

    Sofia, sobre a versao que escrevia a palavra: *"ilustracao pura, zero
    informacao nova"*. O dono foi mais direto: *"quando vai ilustrar videos
    genericos, mostre eles, em vez de simplesmente um texto escrito
    generico"*. Aqui o card nao sai do lugar — o que troca e o video dentro,
    e o molde nao muda nunca."""
    n = 6
    corpo = f"""<div class="camada meio alta col">
        <div class="moldura">{''.join(_slop(i) for i in range(n))}</div>
      </div>"""
    css = _css(quadro=_css_quadro(), slop=_css_slop(), mais="""
  .camada.meio { filter:none; }
  .col { flex-direction:column; align-items:center; justify-content:center; }""")
    marcas, t_ = [], 0.10
    for i in range(n):
        marcas.append((i, t_))
        t_ += max(0.55, 0.9 - i * 0.07)
    troca = "".join(
        f"tl.set('.vid', {{autoAlpha:0}}, {q:.2f});"
        f"tl.set('.vid[data-i=\"{i}\"]', {{autoAlpha:1}}, {q:.2f});"
        for i, q in marcas)
    js = _js(entrar('.moldura', 0.02, 0.8, 0.24) + troca + sair('.moldura'))
    return corpo, css, js


def _tela_pesquisa(p, t):
    """a pesquisa acontecendo: campo de busca e resultados chegando depressa.

    O que a fala diz e «ele já faz para mim A PESQUISA» — entao o que a tela
    mostra e a busca em curso, nao um icone de lupa parado. As linhas de
    resultado sao barras, nao texto: o conteudo de uma pesquisa que nao
    aconteceu seria invencao."""
    consulta = (t.get("texto") or " ".join(_palavras(p, 3)) or "").strip()
    linhas = "".join(
        f'<div class="res" data-i="{i}"><i class="fav"></i>'
        f'<span><b style="width:{86 - i * 9}%"></b><b class="fraca" '
        f'style="width:{62 - i * 6}%"></b></span></div>' for i in range(4))
    corpo = f"""<div class="camada meio alta col">
        <div class="card fundo busca">
          {barra_status()}
          <div class="campo"><i class="lupa"></i><span class="q">{_e(consulta)}</span>
            <i class="cursor"></i></div>
          <div class="resultados">{linhas}</div>
        </div>
      </div>"""
    css = _css(mais=f"""
  .camada.meio {{ filter:none; }}
  .col {{ flex-direction:column; align-items:center; justify-content:center; }}
  .busca {{ width:880px; }}
  .campo {{ display:flex; align-items:center; gap:20px; margin:14px 34px 26px;
    padding:24px 30px; border-radius:22px; background:{CINZA};
    font-family:{SANS}; font-size:42px; color:{TINTA}; }}
  .lupa {{ width:34px; height:34px; border:6px solid {TINTA_2}; border-radius:50%;
    flex:none; }}
  .cursor {{ width:4px; height:44px; background:{AZUL}; margin-left:auto; }}
  .resultados {{ padding:0 34px 44px; display:flex; flex-direction:column; gap:30px; }}
  .res {{ display:flex; align-items:center; gap:24px; }}
  .res .fav {{ width:62px; height:62px; border-radius:16px; background:{CINZA};
    flex:none; }}
  .res span {{ flex:1; display:flex; flex-direction:column; gap:12px; }}
  .res b {{ display:block; height:20px; border-radius:6px; background:{CROMO}; }}
  .res b.fraca {{ height:14px; background:{CINZA}; }}""")
    js = _js(
        entrar('.busca', 0.02, 0.86, 0.24)
        + "tl.from('.q', {opacity:0, duration:0.18}, 0.26);"
        # o cursor pisca enquanto os resultados chegam: e o unico movimento em
        # loop do estilo, e existe porque busca sem cursor le como print parado
        + "tl.to('.cursor', {opacity:0, duration:0.28, repeat:6, yoyo:true,"
          " ease:'none'}, 0.3);"
        + f"tl.from('.res', {{y:26, opacity:0, duration:0.2, stagger:0.16,"
          f" ease:'{ENTRA}'}}, 0.42);"
        + sair('.busca'))
    return corpo, css, js


def _tela_timeline(p, t):
    """a timeline do editor, com cada etapa acontecendo na pista certa.

    Pedido do dono, palavra por palavra: *"em corte e J-cut poderia ilustrar
    mostrando uma timeline de edicao de video"* e *"em «coloca os inserts que
    eu preciso» coloca uma imagem de timeline de programa de edicao com videos
    entrando na timeline"*. Entao cada palavra da fala tem o seu gesto na
    pista: o corte parte o clipe, o J-cut adianta o audio, a cor passa um
    filtro por cima, e os inserts CAEM na pista de cima."""
    etapas = _palavras(p, 4) or ["corte", "J-cut", "cor", "inserts"]
    marcas = "".join(f'<i style="left:{k * 7.5}%"></i>' for k in range(14))
    corpo = f"""<div class="camada meio alta col">
        <div class="card fundo editor">
          <div class="regua">{marcas}</div>
          <div class="pista inserts"><div class="ins i1"></div><div class="ins i2"></div></div>
          <div class="pista video">
            <div class="clipe c1"></div><div class="clipe c2"></div>
            <div class="cor"></div>
          </div>
          <div class="pista audio"><div class="onda"></div></div>
          <div class="agulha"></div>
          <div class="rotulos">
            {''.join(f'<span data-i="{i}">{_e(w)}</span>' for i, w in enumerate(etapas))}
          </div>
        </div>
      </div>"""
    css = _css(mais=f"""
  .camada.meio {{ filter:none; }}
  .col {{ flex-direction:column; align-items:center; justify-content:center; }}
  .editor {{ width:900px; padding:28px 0 34px; position:relative; }}
  .regua {{ position:relative; height:34px; margin:0 26px 18px;
    border-bottom:2px solid {BORDA}; }}
  .regua i {{ position:absolute; top:14px; width:2px; height:20px; background:{CROMO}; }}
  .pista {{ position:relative; height:104px; margin:0 26px 14px; border-radius:14px;
    background:{CINZA}; }}
  .clipe {{ position:absolute; top:8px; bottom:8px; border-radius:10px;
    background:{AZUL}; }}
  .c1 {{ left:8px; width:44%; }}
  .c2 {{ left:calc(44% + 20px); right:8px; }}
  .cor {{ position:absolute; top:8px; bottom:8px; left:calc(44% + 20px); right:8px;
    border-radius:10px; background:linear-gradient(90deg,{T['AMBAR']},{VERDE});
    opacity:0; }}
  .ins {{ position:absolute; top:8px; bottom:8px; border-radius:10px;
    background:{T['AMBAR']}; }}
  .ins.i1 {{ left:18%; width:22%; }}
  .ins.i2 {{ left:52%; width:26%; }}
  .onda {{ position:absolute; top:24px; bottom:24px; left:8px; right:8px;
    border-radius:8px; background:repeating-linear-gradient(90deg,
      {VERDE} 0 6px, transparent 6px 12px); }}
  .agulha {{ position:absolute; top:28px; bottom:64px; left:26px; width:5px;
    background:{VERMELHO}; border-radius:3px; }}
  .rotulos {{ display:flex; justify-content:space-between; margin:22px 30px 0;
    font-family:{SANS}; font-weight:700; font-size:34px; color:{TINTA_2}; }}
  .rotulos span {{ opacity:0.25; }}""")
    # cada etapa acende o proprio rotulo no instante do proprio gesto
    def acende(i, em):
        return (f"tl.to('.rotulos span[data-i=\"{i}\"]', {{opacity:1, color:'{TINTA}',"
                f" duration:0.16}}, {em});")
    js = _js(
        entrar('.editor', 0.02, 0.86, 0.26)
        + "tl.from('.pista', {scaleX:0.9, opacity:0, duration:0.2, stagger:0.08,"
          f" ease:'{ENTRA}'}}, 0.2);"
        # 1. CORTE: o clipe unico vira dois — a fenda abre
        + "tl.set('.c2', {opacity:0}, 0);"
        + "tl.to('.c1', {width:'44%', duration:0.01}, 0.62);"
        + "tl.to('.c2', {opacity:1, duration:0.12}, 0.62);"
        + acende(0, 0.62)
        # 2. J-CUT: o audio se adianta ao video — desliza para a esquerda
        + "tl.to('.onda', {x:-70, duration:0.26, ease:'power3.out'}, 1.25);"
        + acende(1, 1.25)
        # 3. COR: o filtro passa por cima do clipe
        + "tl.fromTo('.cor', {opacity:0}, {opacity:0.85, duration:0.3,"
          " ease:'power2.out'}, 1.95)"
        + acende(2, 1.95)
        # 4. INSERTS: os videos CAEM na pista de cima, um depois do outro
        + f"tl.from('.ins', {{y:-150, opacity:0, duration:0.3, stagger:0.18,"
          f" ease:'back.out(2.2)'}}, 2.6);"
        + acende(3, 2.6)
        # a agulha atravessa o que ficou montado
        + "tl.to('.agulha', {x:830, duration:Math.max(1.2, DUR-3.6),"
          " ease:'none'}, 3.35);"
        + sair('.editor'))
    return corpo, css, js


def _tela_distribuicao(p, t):
    """de onde sai e para onde vai: o post viajando da ferramenta para a rede.

    *"quando eu falo «posta pra mim usando metricool ou zernio» ele vai
    mostrar videos indo de metricool e de zernio para instagram, facebook,
    tiktok, youtube"*. As duas pontas sao nomes que a fala diz; as redes
    aparecem pelo nome, nunca pelo logo — desenhar marca de terceiro e
    imitacao, e o nome entrega a mesma informacao."""
    origens = _palavras(p, 2) or ["Metricool", "Zernio"]
    destinos = [str(x).strip() for x in (t.get("destinos") or
                ["Instagram", "Facebook", "TikTok", "YouTube"]) if str(x).strip()][:4]
    cores = [VERMELHO, AZUL, TINTA, VERMELHO]
    corpo = f"""<div class="camada meio alta col">
        <div class="mapa">
          <div class="fila origens">
            {''.join(f'<div class="no fonte" data-i="{i}">{_e(o)}</div>'
                     for i, o in enumerate(origens))}
          </div>
          <div class="voos">
            {''.join(f'<div class="voo" data-i="{i}"></div>' for i in range(4))}
          </div>
          <div class="fila destinos">
            {''.join(f'<div class="no rede" data-i="{i}">'
                     f'<i style="background:{cores[i % len(cores)]}"></i>'
                     f'<span>{_e(d)}</span></div>' for i, d in enumerate(destinos))}
          </div>
        </div>
      </div>"""
    css = _css(mais=f"""
  .camada.meio {{ filter:none; }}
  .col {{ flex-direction:column; align-items:center; justify-content:center; }}
  .mapa {{ width:920px; position:relative; }}
  .fila {{ display:flex; justify-content:center; gap:26px; }}
  .no {{ background:{BRANCO}; box-shadow:{SOMBRA}; border-radius:{RAIO_P}px;
    font-family:{SANS}; font-weight:700; color:{TINTA}; }}
  .no.fonte {{ padding:26px 44px; font-size:46px; }}
  .destinos {{ margin-top:300px; flex-wrap:wrap; }}
  .no.rede {{ display:flex; align-items:center; gap:16px; padding:20px 30px;
    font-size:34px; }}
  .no.rede i {{ width:44px; height:44px; border-radius:24%; display:block; }}
  /* os voos: o post saindo de cima e pousando embaixo */
  .voos {{ position:absolute; left:0; right:0; top:96px; height:260px; }}
  .voo {{ position:absolute; top:0; width:76px; height:100px; border-radius:12px;
    background:{AZUL}; box-shadow:{SOMBRA}; }}
  .voo[data-i="0"] {{ left:14%; }} .voo[data-i="1"] {{ left:36%; }}
  .voo[data-i="2"] {{ left:58%; }} .voo[data-i="3"] {{ left:80%; }}""")
    voos = "".join(
        f"tl.fromTo('.voo[data-i=\"{i}\"]', {{y:-40, opacity:0, scale:0.6}},"
        f" {{y:250, opacity:1, scale:1, duration:0.46, ease:'power2.in'}},"
        f" {0.5 + i * 0.22:.2f});"
        f"tl.to('.voo[data-i=\"{i}\"]', {{opacity:0, duration:0.12}},"
        f" {0.94 + i * 0.22:.2f});"
        f"tl.from('.no.rede[data-i=\"{i}\"]', {{scale:0.7, opacity:0, duration:0.22,"
        f" ease:'{ENTRA}'}}, {0.9 + i * 0.22:.2f});"
        for i in range(len(destinos)))
    js = _js(
        entrar('.no.fonte', 0.04, 0.7, 0.24, stagger=0.12)
        + voos
        + sair('.mapa'))
    return corpo, css, js


def _tela_repeticao(p, t):
    """cinco videos diferentes com o MESMO tratamento, trocando a cada 0,8 s.

    Sofia, sobre a versao anterior (uma palavra parada por 6,4 s): *"ilustracao
    pura, zero informacao nova, e cai bem na janela em que o Reels decide"*. A
    repeticao e o argumento — generico deixa de ser adjetivo e vira evidencia.
    Por isso o card NAO se mexe: so o conteudo dentro dele troca."""
    palavra = (t.get("texto") or p.get("texto") or "").strip()
    n = 6
    corpo = f"""<div class="camada meio alta col">
        <div class="moldura">{''.join(_quadro(i, palavra) for i in range(n))}</div>
      </div>"""
    css = _css(quadro=_css_quadro(), mais="""
  .camada.meio { filter:none; }
  .col { flex-direction:column; align-items:center; justify-content:center; }""")
    # o passo acelera: 0,9 s no comeco, 0,55 s no fim. Passo constante le como
    # slideshow; acelerando le como "e sempre assim, sempre, sempre".
    marcas, t_ = [], 0.10
    for i in range(n):
        marcas.append((i, t_))
        t_ += max(0.55, 0.9 - i * 0.07)
    troca = "".join(
        f"tl.set('.vid', {{autoAlpha:0}}, {q:.2f});"
        f"tl.set('.vid[data-i=\"{i}\"]', {{autoAlpha:1}}, {q:.2f});"
        for i, q in marcas)
    js = _js(entrar('.moldura', 0.02, 0.8, 0.24) + troca + sair('.moldura'))
    return corpo, css, js


def _tela_recusa(p, t):
    """um video puxado da pilha com o defeito a mostra, e so depois o selo.

    Sofia: *"o selo so carimba a opiniao que a voz ja deu. Puxa UM thumbnail
    da grade pra frente e deixa o defeito rodar — ai o espectador condena
    junto, em vez de ser informado da condenacao."* Por isso o selo entra no
    FIM: primeiro a prova, depois o veredito."""
    corpo = f"""<div class="camada meio alta col">
        <div class="moldura">{_quadro(1, (t.get('texto') or '').strip())}
          <div class="selo"><span>✕</span></div>
        </div>
      </div>"""
    # o selo e uma CAMADA que centra o circulo, e o circulo e que anima: assim
    # nenhum transform de centragem briga com o tween (o erro classico de somar
    # translate(-50%,-50%) do CSS com scale do GSAP no mesmo elemento).
    css = _css(quadro=_css_quadro(), mais=f"""
  .camada.meio {{ filter:none; }}
  .col {{ flex-direction:column; align-items:center; justify-content:center; }}
  /* o selo desce na altura do terco de baixo, nao no centro: no centro ele
     tapa a legenda automatica — ou seja, esconde justamente a prova que ele
     esta condenando. */
  .selo {{ position:absolute; inset:0; display:flex; align-items:flex-end;
    justify-content:center; padding-bottom:16%; }}
  .selo span {{ width:300px; height:300px; border-radius:50%; background:{VERMELHO};
    color:#FFFFFF; display:flex; align-items:center; justify-content:center;
    font-family:{SANS}; font-weight:700; font-size:170px; line-height:1;
    box-shadow:{SOMBRA_FUNDA}; }}""")
    js = _js(
        entrar('.moldura', 0.02, 0.78, 0.26)
        # o tratamento pousa peca por peca: primeiro a legenda, depois o emoji
        + f"tl.from('.auto-legenda', {{scale:0.6, opacity:0, duration:0.22,"
          f" ease:'{ENTRA}'}}, 0.34);"
        + f"tl.from('.auto-emoji', {{scale:0, rotate:-25, duration:0.24,"
          f" ease:'{ENTRA}'}}, 0.56);"
        # o veredito so no fim, e ele bate: vem de cima, grande, e assenta
        + "tl.fromTo('.selo span', {scale:2.4, opacity:0, y:-160},"
          " {scale:1, opacity:1, y:0, duration:0.3, ease:'back.out(2.6)'}, 1.05);"
        + sair('.moldura'))
    return corpo, css, js


def _tela_regras(p, t):
    """a regra ACONTECENDO sobre um quadro real do proprio take.

    O diretor ja tinha escrito no guia: *"mostrar uma regra acontecendo ensina o
    que e um formato em quatro segundos; tres rotulos empilhados nao ensinariam
    nada"*. A implementacao anterior desenhou os tres rotulos assim mesmo, em
    balao de iMessage. Aqui o rosto trava na metade de baixo, o apoio entra em
    cima e a legenda assenta na juncao — e o unico ponto do video em que a
    ferramenta se demonstra dentro do formato que ela vende."""
    fundo = (t.get("fundo") or "").strip()
    linhas = [str(x).strip() for x in (t.get("linhas") or []) if str(x).strip()]
    rot = (linhas + ["", "", ""])[:3]
    corpo = f"""<div class="camada meio alta col">
        <div class="moldura split">
          <div class="apoio"><div class="massa" style="background:
            radial-gradient(closest-side at 30% 24%, {AZUL} 0%, transparent 70%),
            linear-gradient(160deg,#EDEDF2 0%,#D6D6DE 100%)"></div></div>
          <div class="rosto">{f'<img src="{_e(fundo)}" alt=""/>' if fundo else ''}</div>
          <div class="juncao"></div>
          <div class="cc">{_e(t.get('titulo') or '')}</div>
          <i class="rot r1">{_e(rot[1])}</i>
          <i class="rot r0">{_e(rot[0])}</i>
          <i class="rot r2">{_e(rot[2])}</i>
        </div>
      </div>"""
    css = _css(mais=f"""
  .camada.meio {{ filter:none; }}
  .col {{ flex-direction:column; align-items:center; justify-content:center; }}
  .moldura.split {{ position:relative; width:800px; height:1230px;
    border-radius:{RAIO}px; overflow:hidden; box-shadow:{SOMBRA_FUNDA};
    background:{CINZA}; }}
  .apoio {{ position:absolute; left:0; right:0; top:0; height:50%; overflow:hidden; }}
  .apoio .massa {{ position:absolute; inset:0; }}
  .rosto {{ position:absolute; left:0; right:0; bottom:0; height:50%; overflow:hidden; }}
  /* o rosto preso na metade de baixo: o enquadramento e que se ajusta a ele */
  .rosto img {{ width:100%; height:100%; object-fit:cover; object-position:50% 26%;
    display:block; }}
  .juncao {{ position:absolute; left:0; right:0; top:50%; height:0;
    border-top:3px dashed rgba(255,255,255,0.9); }}
  /* a legenda na juncao, sem linha: ela senta em cima do encontro */
  .cc {{ position:absolute; left:8%; right:8%; top:50%; transform:translateY(-50%);
    text-align:center; font-family:{SANS}; font-weight:800; font-size:58px;
    color:#FFFFFF; text-transform:uppercase; letter-spacing:0.01em;
    text-shadow:0 3px 0 rgba(0,0,0,0.55), 0 0 18px rgba(0,0,0,0.4); }}
  .rot {{ position:absolute; right:24px; padding:10px 20px; border-radius:999px;
    background:rgba(255,255,255,0.94); font-family:{SANS}; font-style:normal;
    font-weight:600; font-size:26px; color:{TINTA}; box-shadow:{SOMBRA}; }}
  .r1 {{ top:24px; }} .r0 {{ bottom:24px; }} .r2 {{ top:50%; margin-top:56px; }}""")
    js = _js(
        entrar('.moldura', 0.02, 0.84, 0.26)
        # 1. o rosto trava embaixo — ele CHEGA no lugar, nao nasce nele
        + "tl.from('.rosto', {yPercent:60, duration:0.34, ease:'power3.out'}, 0.24);"
        + "tl.from('.juncao', {scaleX:0, duration:0.26, ease:'power3.out'}, 0.44);"
        # 2. o apoio entra em cima, depois — a ordem e a propria regra
        + "tl.from('.apoio', {yPercent:-70, duration:0.34, ease:'power3.out'}, 0.72);"
        # 3. a legenda assenta na juncao
        + f"tl.from('.cc', {{scale:0.7, opacity:0, duration:0.24,"
          f" ease:'{ENTRA}'}}, 1.12);"
        # os rotulos sao nota de rodape: entram pequenos, atras de cada gesto
        + "tl.from('.r0', {opacity:0, x:30, duration:0.2, ease:'power3.out'}, 0.46);"
        + "tl.from('.r1', {opacity:0, x:30, duration:0.2, ease:'power3.out'}, 0.94);"
        + "tl.from('.r2', {opacity:0, x:30, duration:0.2, ease:'power3.out'}, 1.32);"
        + sair('.moldura'))
    return corpo, css, js


def tela(p):
    """a tela como print flutuando. O `modo` do plano escolhe o desenho:
    `repeticao` (o mesmo tratamento em varios videos), `recusa` (o defeito a
    mostra e o selo depois), `regras` (a regra acontecendo sobre um quadro
    real) e, no resto, a conversa de app — que e o desenho neutro do estilo.
    `terminal` NAO vira terminal preto: neste estilo nao existe janela de
    software escura."""
    t = p.get("tela") if isinstance(p.get("tela"), dict) else {}
    modo = (t.get("modo") or "").strip().lower()
    if modo in ("slop", "generico"):
        return _tela_slop(p, t)
    if modo == "repeticao":
        return _tela_repeticao(p, t)
    if modo == "recusa":
        return _tela_recusa(p, t)
    if modo == "regras":
        return _tela_regras(p, t)
    if modo == "pesquisa":
        return _tela_pesquisa(p, t)
    if modo == "timeline":
        return _tela_timeline(p, t)
    if modo in ("distribuicao", "distribuição"):
        return _tela_distribuicao(p, t)
    titulo_app = t.get("titulo") or p.get("texto") or ""
    linhas = [str(x).strip() for x in (t.get("linhas") or _linhas(p, 4)) if str(x).strip()]
    comando = (t.get("comando") or "").strip()
    destaque = (t.get("destaque") or "").strip().lower()
    if comando:
        linhas = [comando] + linhas
    baloes = "".join(
        f'<div class="balao{" eu" if (destaque and destaque in l.lower()) else ""}'
        f'{" meu" if i == 0 and comando else ""}">{_e(l)}</div>'
        for i, l in enumerate(linhas[:4]))
    corpo = f"""<div class="camada meio alta col">
        <div class="card fundo fone">
          {barra_status()}
          <div class="navbar"><i class="volta"></i>
            <span class="titulo">{_e(titulo_app)}</span>
            <span class="acao">•••</span></div>
          <div class="conversa">{baloes}</div>
        </div>
      </div>"""
    css = _css(mais=f"""
  .camada.meio {{ filter:none; }}
  .col {{ flex-direction:column; align-items:center; justify-content:center; }}
  .fone {{ width:880px; }}
  .conversa {{ display:flex; flex-direction:column; gap:26px; padding:40px 40px 64px; }}
  .balao {{ align-self:flex-start; max-width:76%; padding:28px 38px;
    border-radius:40px; border-bottom-left-radius:12px; background:{BOLHA};
    font-family:{SANS}; font-size:44px; line-height:1.25; color:{TINTA}; }}
  .balao.meu, .balao.eu {{ align-self:flex-end; background:{BOLHA_EU}; color:#FFFFFF;
    border-bottom-left-radius:40px; border-bottom-right-radius:12px; }}""")
    js = _js(entrar('.fone', 0.04, 0.84, 0.26)
             + subir_mola('.balao', 0.22)
             + sair('.fone'))
    return corpo, css, js


def dado(p):
    """o numero grande com a ficha da fonte embaixo, em card de UI. Numero sem
    fonte escrita nao entra — a regra e a mesma de sempre, so o desenho muda."""
    valor = str(p.get("valor") or p.get("texto") or "").strip() or "—"
    rotulo = str(p.get("rotulo") or p.get("legenda") or "").strip()
    fonte = str(p.get("fonte") or "").strip()
    corpo = f"""<div class="camada meio alta col">
        {titulo(valor, olho=rotulo)}
        {f'<div class="ficha">{_e(fonte)}</div>' if fonte else ''}
      </div>"""
    css = _css(titulo=css_titulo(210), mais=f"""
  .camada.meio {{ filter:none; }}
  .col {{ flex-direction:column; align-items:center; justify-content:center; padding:0 70px; }}
  .ficha {{ margin-top:46px; padding:20px 40px; border-radius:999px;
    background:{CINZA}; box-shadow:{SOMBRA}; font-family:{MONO}; font-size:32px;
    color:{TINTA_2}; }}""")
    js = _js(js_titulo() + entrar('.ficha', 0.34, 0.8, 0.22)
             + sair('.display, .ficha'))
    return corpo, css, js


def imagem(p):
    """o asset gerado como PRINT: card de canto arredondado com sombra real,
    sobre o branco. Aqui mora o Grow Effect — o print entra pequeno e cresce
    para alem da propria moldura, que e o efeito que a referencia demonstra."""
    asset = p.get("asset")
    if not asset:
        return cartela(p)
    # So `texto` vira etiqueta. O `estado` do plano guarda palavras de direcao
    # ("antes", "durante") — desenha-las dava um chip escrito "antes" pendurado
    # embaixo de cada print, que e ruido de producao vazando para o master.
    rotulo = (p.get("texto") or "").strip()
    corpo = f"""<div class="camada meio cheia col">
        <div class="porta">
          <div class="print"><img src="{_e(asset)}" alt=""/></div>
        </div>
        {f'<div class="etiqueta">{_e(rotulo)}</div>' if rotulo else ''}
      </div>"""
    css = _css(mais=f"""
  .camada.meio {{ filter:none; }}
  .col {{ flex-direction:column; align-items:center; justify-content:center; }}
  /* a porta NAO corta: o print cresce para fora dela, e essa e a graca */
  .porta {{ position:relative; width:900px; height:1180px; display:flex;
    align-items:center; justify-content:center; overflow:visible; }}
  .print {{ width:900px; height:1180px; border-radius:{RAIO}px; overflow:hidden;
    box-shadow:{SOMBRA_FUNDA}; background:{BRANCO}; }}
  .print img {{ width:100%; height:100%; object-fit:cover; display:block; }}
  .etiqueta {{ margin-top:40px; padding:22px 44px; border-radius:999px;
    background:{BRANCO}; box-shadow:{SOMBRA}; font-family:{SANS}; font-weight:700;
    font-size:42px; color:{TINTA}; }}""")
    # Grow Effect: entra em 0,62 e vai a 1,12 — passa da moldura e para. Nao e
    # um zoom lento de fundo: sao 0,42 s e acabou.
    js = _js(
        f"tl.fromTo('.print', {{scale:0.62, opacity:0}},"
        f" {{scale:1.12, opacity:1, duration:0.42, ease:'{ENTRA}'}}, 0.04);"
        + entrar('.etiqueta', 0.34, 0.7, 0.24)
        + sair('.print, .etiqueta', 0.26, 1.34))
    return corpo, css, js


# os tipos que o `gravacao` desenha de outro jeito. O que nao esta aqui cai na
# composicao generica do hf.py, ja com a paleta branca.
CORPOS = {
    "cartela": cartela,
    "palavras": palavras,
    "camadas": camadas,
    "indice": indice,
    "tela": tela,
    "dado": dado,
    "objeto": imagem, "personagem": imagem, "obra": imagem, "arquivo": imagem,
    "cotidiano": imagem, "broll": imagem, "hibrido": imagem,
}
