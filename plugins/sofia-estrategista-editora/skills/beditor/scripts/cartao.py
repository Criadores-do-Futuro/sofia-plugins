#!/usr/bin/env python3
"""
cartao.py — o cartao de prova do formato `analise`, nos quatro modos.

A regra-mae esta em `referencias/formato-analise.md`: QUEM TEM A VOZ MANDA NO
TAMANHO. Se o autor fala, o clipe e ilustracao e vai ATRAS dele. Se o clipe
fala, e citacao e vai NA FRENTE, com o autor apagado.

    modo 1  atras do autor       cenario intacto, clipe mudo, exige matte
    modo 2  sobreposto           A-roll em P&B e desfocado, audio do clipe assume
    modo 3  maximo               o autor sai de quadro, moldura ainda visivel
    modo 4  janela               tela cheia, com abertura e minimizacao fluidas

O modo 4 e decisao do dono em 2026-09-13: "podem ter alguns trechos onde aparece
em tela inteira mas faca uma transicao fluida de entrada e de saida, como se
estivesse abrindo uma janela num macbook, e depois minimizando." Ele e a unica
excecao ao teto de moldura dos modos 1-3 — e por isso a moldura VOLTA durante a
entrada e a saida: a janela cresce de um retangulo arredondado pequeno ate o
quadro cheio, e encolhe de volta. O espectador ve a moldura nos dois extremos,
que e o que continua dizendo "isto e o post de outra pessoa dentro do meu video".

GEOMETRIA — a licao que so a montagem ensina
--------------------------------------------
Os numeros medidos no corpus (largura 55-60%, topo 6%, base 43%) saem de fonte
VERTICAL: os quatro reels analisam reels 9:16, entao 57% de largura da 57% de
altura e a conta fecha. Com fonte HORIZONTAL (trailer, gameplay, YouTube) a 57%
de largura o cartao tem 18% de altura, e nao existe posicao que faca topo 6% e
base 43% ao mesmo tempo.

Para fonte horizontal, portanto, **quem manda e a BASE, nao o topo**: o cartao e
dimensionado e posto para a borda de baixo cair sobre o cabelo do autor. Sem esse
encontro o modo 1 vira adesivo colado no canto, e o efeito inteiro se perde.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pathlib import Path

W, H = 1080, 1920

# largura%, topo%, raio — por modo e por orientacao da fonte
GEO_VERTICAL = {1: (0.575, 0.06, 34), 2: (0.72, 0.14, 40), 3: (0.86, 0.14, 40)}
GEO_HORIZONTAL = {1: (0.80, 0.22, 34), 2: (0.88, 0.26, 40), 3: (0.96, 0.26, 40)}

# Com cartao em quadro o autor tambem e reenquadrado: dois elementos grandes que
# se tocam, em vez de dois pequenos com ar morto entre eles. Decisao do dono em
# 2026-09-14, olhando o primeiro master.
ESCALA_COM_CARTAO = 1.25
BASE_MODO1 = 0.44          # onde a borda de baixo do cartao cai, em fracao da altura


def sem_tarja(img, lim=26):
    """tira a tarja preta que a PROPRIA fonte traz.

    Trailer de cinema e 2.35:1 dentro de um 16:9: ele chega com barra preta em
    cima e embaixo, gravada no quadro. Ampliar o quadro inteiro amplia a barra
    junto, e no modo 4 sobra tarja da fonte MAIS o fundo desfocado — duas faixas
    mortas onde devia haver imagem.
    """
    g = img.convert("L")
    larg, alt = g.size
    linha = [sum(g.crop((0, y, larg, y + 1)).getdata()) / larg for y in range(alt)]
    topo = 0
    while topo < alt // 3 and linha[topo] < lim:
        topo += 1
    base = alt - 1
    while base > alt * 2 // 3 and linha[base] < lim:
        base -= 1
    if topo == 0 and base == alt - 1:
        return img
    return img.crop((0, topo, larg, base + 1))


def tarja_de(quadros, lim=26, amostras=9):
    """A tarja de um CLIPE, decidida uma vez — não quadro a quadro.

    `sem_tarja` mede o brilho de cada linha, e num clipe escuro esse brilho muda
    com a imagem: um celular no escuro tem a tela clara andando pelo quadro, e a
    linha que era «tarja» num quadro deixa de ser no seguinte. Aplicada quadro a
    quadro, a função devolve um recorte de tamanho DIFERENTE a cada quadro — e
    como a geometria do cartão sai das dimensões do clipe, a moldura muda de
    largura e de altura 30 vezes por segundo.

    O sintoma é exatamente o que o dono descreveu no projeto 15: «uma parte fixa
    e outra se mexendo». A moldura pulsa enquanto o conteúdo anda.

    Tarja é propriedade do CLIPE, não do quadro. Mede-se em algumas amostras e
    fica-se com o recorte MENOS agressivo — o que preserva imagem em todos os
    quadros, em vez de comer conteúdo naquele em que a cena escureceu.
    """
    if not quadros:
        return None
    passo = max(1, len(quadros) // amostras)
    topo, base = None, None
    for q in quadros[::passo]:
        im = Image.open(q) if not isinstance(q, Image.Image) else q
        g = im.convert("L")
        larg, alt = g.size
        linha = [sum(g.crop((0, y, larg, y + 1)).getdata()) / larg for y in range(alt)]
        t = 0
        while t < alt // 3 and linha[t] < lim:
            t += 1
        b = alt - 1
        while b > alt * 2 // 3 and linha[b] < lim:
            b -= 1
        topo = t if topo is None else min(topo, t)
        base = b if base is None else max(base, b)
    return (0, topo, larg, base + 1)


def base_para_rosto(rosto, escala, alto=0.40, sobra=0.035):
    """Onde a borda de baixo do cartao deve cair, DADA a cabeca do autor.

    Esta e a correcao mais importante do modo 1, e ela so aparece ao assistir:
    com base fixa em 44% o cartao fica com o MIOLO atras da cabeca, e a cabeca
    tapa justamente o meio do que se esta provando. O efeito do modo 1 nunca foi
    "cartao atras da pessoa" — e "cartao ACIMA da pessoa, com a borda de baixo
    passando atras do cabelo". A diferenca entre os dois e o vídeo ser legivel
    ou nao.

    Entao a base nao e um numero do formato: e uma funcao do topo da cabeca.
    `sobra` e o quanto o cabelo cruza a borda — 3,5% da altura basta para o olho
    ler "no mesmo espaco", e mais que isso comeca a comer o cartao.
    """
    if not rosto:
        return BASE_MODO1
    h = rosto.get("height", 0.12) * escala
    topo_rosto = alto - h / 2
    topo_cabelo = topo_rosto - 0.30 * h        # o cabelo sobe ~30% da caixa do rosto
    return max(0.24, topo_cabelo + sobra)


def base_do_cartao(modo, clipe_img):
    """onde a borda de baixo do cartao cai, em fracao da altura.

    A legenda precisa saber disto: cartao de comentario e muito mais alto que um
    clipe 16:9, e legenda em altura fixa cai em cima do rodape da fonte. Quem
    desenha a legenda pergunta aqui e desce o que for preciso.
    """
    lg, topo, _ = geo(modo, clipe_img)
    cw = W * lg
    return topo + (cw * clipe_img.height / clipe_img.width) / H


TOPO_MIN = 0.045       # nenhuma borda de cartao sobe acima disto
QUASE_QUADRADO = 1.15  # abaixo desta razao o clipe conta como vertical


def geo(modo, clipe_img):
    """a ficha do modo, escolhida pela orientacao real do clipe.

    Duas travas, e as duas nasceram do mesmo cartao saindo pelo topo do quadro:

    QUASE QUADRADO conta como vertical. A classificacao era `altura >= largura`,
    um precipicio exatamente em 1:1. Uma montagem 960x960 perdia 23 linhas
    escuras no `sem_tarja`, virava 960x937 e trocava de TABELA DE GEOMETRIA
    inteira por causa de um pixel. Fonte quase quadrada se comporta como vertical
    — e alta —, entao ela e tratada como vertical.

    O CARTAO ESTREITA, NAO SOBE. No modo 1 horizontal quem manda e a base (a
    cabeca do autor decide onde ela cai), e o topo sai de `BASE - altura`. Com
    uma fonte alta e uma base alta isso da topo NEGATIVO, e o cartao sai pelo
    teto sem que nada reclame. A saida certa nao e baixar a base — a base esta
    onde esta para o cartao nao ser tapado pela cabeca. E estreitar o cartao ate
    a altura dele caber entre TOPO_MIN e a base.
    """
    vertical = clipe_img.width / max(1, clipe_img.height) < QUASE_QUADRADO
    lg, topo, raio = (GEO_VERTICAL if vertical else GEO_HORIZONTAL)[modo]
    prop = clipe_img.height / clipe_img.width          # altura por largura

    if not vertical and modo == 1:
        topo = BASE_MODO1 - (W * lg) * prop / H

    alt = (W * lg) * prop / H
    if topo < TOPO_MIN:
        base = topo + alt                              # onde ele PRECISA terminar
        alt = max(0.12, base - TOPO_MIN)               # o que sobra de altura
        lg = alt * H / (W * prop)                      # e a largura que a produz
        topo = base - alt
    return lg, topo, raio


def _moldura(clipe_img, cw, raio, alt_min=None):
    """o trecho dentro da moldura arredondada.

    `alt_min` força uma altura mínima: o clipe é ampliado e cortado pelas
    laterais até preenchê-la, nunca deformado. Existe por causa do modo 4 com
    fonte horizontal — um 16:9 a largura cheia ocupa 32% da altura de um quadro
    9:16, e o resto vira cinza. Duas faixas mortas ocupando dois terços da tela
    leem como letterbox, não como tela cheia.
    """
    ch = max(1, int(cw * clipe_img.height / clipe_img.width))
    if alt_min and ch < alt_min:
        esc = alt_min / ch
        lw = int(cw * esc)
        c = clipe_img.resize((lw, alt_min), Image.LANCZOS).convert("RGB")
        c = c.crop(((lw - cw) // 2, 0, (lw - cw) // 2 + cw, alt_min))
        ch = alt_min
        m = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, cw - 1, ch - 1], radius=raio, fill=255)
        cart = Image.new("RGBA", (cw, ch))
        cart.paste(c, (0, 0))
        cart.putalpha(m)
        return cart
    c = clipe_img.resize((cw, ch), Image.LANCZOS).convert("RGB")
    m = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, cw - 1, ch - 1], radius=raio, fill=255)
    cart = Image.new("RGBA", (cw, ch))
    cart.paste(c, (0, 0))
    cart.putalpha(m)
    return cart


def _sombra(base, x, y, cw, ch, raio, desf=26, forca=150):
    s = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle([x, y + 10, x + cw, y + ch + 10],
                                        radius=raio, fill=(0, 0, 0, forca))
    return Image.alpha_composite(base, s.filter(ImageFilter.GaussianBlur(desf)))


def _pb_desfocado(a, empurrar=0.0):
    """o fundo dos modos 2, 3 e 4: o cenario do autor sem competir com o cartao.

    O topo que sobra quando o A-roll e empurrado NAO pode ser preto — barra preta
    no alto entrega a montagem e briga com a moldura. O que preenche e o proprio
    fundo desfocado, ampliado, por baixo do A-roll deslocado.
    """
    g = a.convert("L").convert("RGBA").filter(ImageFilter.GaussianBlur(18))
    if empurrar <= 0:
        return g
    emp = g.resize((int(W * 1.25), int(H * 1.25)), Image.LANCZOS)
    emp = emp.crop((int(W * 0.125), 0, int(W * 0.125) + W, H))
    emp.alpha_composite(g, (0, int(H * empurrar)))
    return emp


# --------------------------------------------------------------- modo 4: janela
def _suave_saida(u):   # easeOutCubic — abre rapido e assenta
    return 1 - (1 - u) ** 3


def _suave_entrada(u):  # easeInCubic — segura e some rapido
    return u ** 3


def janela(fase):
    """(escala, ancora_y, opacidade) da janela no instante `fase` de 0 a 1.

    `fase` < 0 e a abertura (de -1 a 0), > 1 e a minimizacao (de 1 a 2), e entre
    0 e 1 a janela esta aberta e parada. Abrir e minimizar sao os dois unicos
    momentos em que o modo 4 se mexe: janela aberta nao respira, nao flutua e nao
    faz zoom — quem se mexe e o conteudo dentro dela.
    """
    if fase < 0:                       # abrindo
        u = _suave_saida(max(0.0, 1 + fase))
        return 0.14 + 0.86 * u, 1.0 - u, min(1.0, u * 3)
    if fase > 1:                       # minimizando para a base
        u = _suave_entrada(min(1.0, fase - 1))
        return 1.0 - 0.88 * u, u, max(0.0, 1 - u * 1.15)
    return 1.0, 0.0, 1.0


def compor(aroll_img, clipe_img, modo, matte_png=None, fase=0.5, legenda_altura=None):
    """um quadro composto. `fase` so importa no modo 4."""
    a = aroll_img.convert("RGBA")

    if modo == 4:
        esc, anc, op = janela(fase)
        fundo = _pb_desfocado(a)
        cw = max(2, int(W * esc))
        raio = int(48 * (1 - esc) + 6)          # a moldura some so no quadro cheio
        # a janela aberta preenche 62% da altura: o suficiente para o olho ler
        # "tela cheia" sem perder as laterais do que se esta provando
        cart = _moldura(clipe_img, cw, raio, alt_min=int(H * 0.62 * esc))
        ch = cart.height
        # a janela nasce e morre perto da base, como o Dock do macOS
        x = (W - cw) // 2
        y = int((H - ch) / 2 * (1 - anc) + (H - ch * 0.25) * anc)
        out = _sombra(fundo, x, y, cw, ch, raio) if esc < 0.99 else fundo
        if op < 1:
            cart.putalpha(cart.getchannel("A").point(lambda v: int(v * op)))
        out.alpha_composite(cart, (x, y))
        return out.convert("RGB")

    lg, topo, raio = geo(modo, clipe_img)
    fundo = a if modo == 1 else _pb_desfocado(a, 0.20 if modo == 2 else 0.0)
    cw = int(W * lg)
    cart = _moldura(clipe_img, cw, raio)
    x, y = (W - cw) // 2, int(H * topo)
    out = _sombra(fundo, x, y, cw, cart.height, raio)
    out.alpha_composite(cart, (x, y))
    if modo == 1:
        if matte_png is None:
            raise ValueError("modo 1 exige o matte do autor — sem ele o cartao tapa a cabeca")
        out.alpha_composite(Image.open(matte_png).convert("RGBA"), (0, 0))
    return out.convert("RGB")


# ------------------------------------------------------------------- legenda
FONTES = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf",
          "/System/Library/Fonts/Helvetica.ttc"]
CREME = (239, 233, 230)


def _fonte(px):
    for c in FONTES:
        if Path(c).exists():
            try:
                return ImageFont.truetype(c, px)
            except Exception:
                pass
    return ImageFont.load_default()


# ------------------------------------------------------- tipografia (2026-09-15)
# Decisao do dono, vendo o primeiro master do 16 e mostrando duas referencias:
#   "use legendas assim quando for ilustrar pontos, partes, etapas" — um TITULO em
#   duas vozes: a primeira palavra em sans geometrica NEGRITO, caixa baixa, grande;
#   a segunda em SERIFA ITALICA, menor, deslocada para a direita e encostada por
#   baixo da primeira ("temas / universais");
#   "e use legendas assim para os dialogos" — a legenda corrente em sans REGULAR,
#   caixa baixa, branca, centralizada, corpo pequeno, sem barra ("a atencao").
# Medido nas duas referencias: no titulo a sans tem ~1,45x a altura da serifa e a
# serifa comeca a ~55% da largura da sans; a legenda de dialogo tem ~2,3% da altura
# do quadro (44 px em 1920) e senta a ~57% da altura.
# O registro anterior (caixa alta, Arial Bold, creme) continua disponivel como
# `explicativo` para os videos ja aprovados renderizarem igual; o novo e o padrao.
TIPOGRAFIA = "minusculo"
_FONTES_DIR = Path(__file__).resolve().parent.parent / "public" / "fontes"
SANS_VAR = _FONTES_DIR / "Montserrat-wght.ttf"
SERIF_IT_VAR = _FONTES_DIR / "Fraunces-Italic-SOFT-WONK-opsz-wght.ttf"
BRANCO = (255, 255, 255)
_CACHE_FONTES = {}


def tipografia(nome=None):
    """Define (ou consulta) o registro tipografico: `minusculo` ou `explicativo`."""
    global TIPOGRAFIA
    if nome:
        if nome not in ("minusculo", "explicativo"):
            raise ValueError(f"tipografia desconhecida: {nome}")
        TIPOGRAFIA = nome
    return TIPOGRAFIA


def _fonte_var(arq, px, wght):
    """Fonte variavel no peso pedido. Sem o arquivo, cai na fonte do sistema."""
    k = (str(arq), px, wght)
    if k in _CACHE_FONTES:
        return _CACHE_FONTES[k]
    f = None
    if Path(arq).exists():
        try:
            f = ImageFont.truetype(str(arq), px)
            eixos = f.get_variation_axes()          # [{'name': b'Weight', 'minimum':…}, …]
            valores = []
            for a in eixos:
                n = a["name"]
                n = (n.decode() if isinstance(n, bytes) else str(n)).lower()
                if "weight" in n or n == "wght":
                    valores.append(max(a["minimum"], min(a["maximum"], wght)))
                elif "optical" in n or n == "opsz":
                    valores.append(max(a["minimum"], min(a["maximum"], px)))
                else:
                    valores.append(a["default"])
            f.set_variation_by_axes(valores)
        except Exception:
            f = ImageFont.truetype(str(arq), px) if Path(arq).exists() else None
    _CACHE_FONTES[k] = f or _fonte(px)
    return _CACHE_FONTES[k]


def sans(px, wght=800):
    return _fonte_var(SANS_VAR, px, wght)


def serifa_italica(px, wght=400):
    return _fonte_var(SERIF_IT_VAR, px, wght)


def _sombra_suave(camada, texto_xy, texto, f, alpha=150, raio=6):
    """Sombra difusa (nao dura): a referencia de dialogo nao tem contorno, so uma
    leve separacao do fundo. Desenha em camada propria e desfoca."""
    s = Image.new("RGBA", camada.size, (0, 0, 0, 0))
    ImageDraw.Draw(s).text((texto_xy[0] + 2, texto_xy[1] + 3), texto, font=f, fill=(0, 0, 0, alpha))
    camada.alpha_composite(s.filter(ImageFilter.GaussianBlur(raio)))


def titulo_duas_vozes(camada, linhas, destaque, y, alpha=255, px_sans=185, larg_max=0.90):
    """O titulo «temas / universais»: linhas nao destacadas em sans negrito caixa
    baixa; a linha `destaque` em serifa italica, menor, deslocada a direita e
    encostada por baixo. Devolve a altura ocupada."""
    d = ImageDraw.Draw(camada)
    LIM = int(W * larg_max)
    px = px_sans
    # encolhe ate a linha sans mais larga caber. Titulo de UMA linha e todo sans
    # (o destaque so vira serifa quando ha outra linha), entao entra na conta —
    # sem isso «3 princípios» saia pelas bordas do quadro
    while px > 60 and any(d.textbbox((0, 0), l.lower(), font=sans(px))[2] > LIM
                          for i, l in enumerate(linhas) if i != destaque or len(linhas) == 1):
        px -= 6
    px_ser = int(px / 1.45)
    y0 = y
    x_sans_ini = None
    larg_sans = 0
    for i, l in enumerate(linhas):
        txt = l.lower()
        if i == destaque and len(linhas) > 1:
            f = serifa_italica(px_ser, 500)
            while d.textbbox((0, 0), txt, font=f)[2] > LIM and px_ser > 40:
                px_ser -= 4
                f = serifa_italica(px_ser, 500)
            w = d.textbbox((0, 0), txt, font=f)[2]
            # comeca a ~55% da largura da sans, sem sair do quadro
            x = (x_sans_ini + int(larg_sans * 0.55)) if x_sans_ini is not None else (W - w) // 2
            x = min(x, W - w - int(W * 0.05))
            y -= int(px_ser * 0.22)          # encosta por baixo da sans
            _sombra_suave(camada, (x, y), txt, f, alpha=int(alpha * 0.6))
            d.text((x, y), txt, font=f, fill=(*BRANCO, alpha))
            y += int(px_ser * 1.05)
        else:
            f = sans(px)
            w = d.textbbox((0, 0), txt, font=f)[2]
            x = (W - w) // 2
            x_sans_ini, larg_sans = x, w
            _sombra_suave(camada, (x, y), txt, f, alpha=int(alpha * 0.6), raio=8)
            d.text((x, y), txt, font=f, fill=(*BRANCO, alpha))
            y += int(px * 0.98)
    return y - y0


def legenda(img, texto, altura=0.63, px=64):
    """Legenda corrente do formato: creme, sem caixa e sem barra, so sombra.

    Decisao do dono em 2026-09-12: "nao use essas barras pretas nas legendas, use
    apenas sombra."

    Os 52-58% de altura medidos no corpus valem para plano ABERTO. Com o autor
    reenquadrado a 1,25-1,32x o queixo desce, e a legenda ali passa a encostar no
    rosto — foi o que aconteceu no primeiro master do 14. Com reenquadramento ela
    vai para 63% e o corpo sobe de 54 para 64 px, porque o quadro fechado pede
    letra maior para a mesma distancia de leitura.
    """
    if not texto:
        return img
    if TIPOGRAFIA == "minusculo":
        # a legenda de dialogo da referencia: caixa baixa, sans regular, branca,
        # corpo pequeno (2,3% da altura), so uma sombra difusa. `px` que o render
        # passa e o do registro antigo; aqui o corpo e o medido na referencia.
        txt = texto.lower()
        pxm = 46
        LIM = int(W * 0.86)
        camada = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(camada)
        f = sans(pxm, 500)
        w = d.textbbox((0, 0), txt, font=f)[2]
        while w > LIM and pxm > 34:
            pxm -= 2
            f = sans(pxm, 500)
            w = d.textbbox((0, 0), txt, font=f)[2]
        x, y = (W - w) // 2, int(H * altura) - pxm // 2
        _sombra_suave(camada, (x, y), txt, f, alpha=170, raio=5)
        d.text((x, y), txt, font=f, fill=(*BRANCO, 255))
        fora = img.convert("RGBA")
        fora.alpha_composite(camada)
        return fora.convert("RGB")
    texto = texto.upper()
    d = ImageDraw.Draw(img)
    # a legenda nunca encosta na borda: 88% da largura e o limite, e se o grupo
    # nao couber o corpo encolhe ate caber (piso de 40 px). Deixar estourar corta
    # a palavra na borda, que foi o defeito do primeiro master do 14.
    LIM = int(W * 0.88)
    f = _fonte(px)
    w = d.textbbox((0, 0), texto, font=f)[2]
    while w > LIM and px > 40:
        px -= 3
        f = _fonte(px)
        w = d.textbbox((0, 0), texto, font=f)[2]
    x, y = (W - w) // 2, int(H * altura) - px // 2
    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (3, 4), (4, 5)):
        d.text((x + dx, y + dy), texto, font=f, fill=(0, 0, 0))
    d.text((x, y), texto, font=f, fill=CREME)
    return img


def triptico(clipes, u, larg=0.96, topo=0.20, cada=0.34, raio=26, prop=1.25, tarjas=None):
    """Três provas LADO A LADO, entrando uma depois da outra.

    Existe para a frase que cita três coisas de uma vez. Mostrar as três em
    sequência, cada uma no seu cartão, gastaria o triplo do tempo e perderia o
    argumento: o que prova a frase «aconteceu no cinema» não é um filme, é a
    REPETIÇÃO — e repetição só se vê quando as três estão na tela juntas.

    Cada painel é retrato, recortado pelo centro do quadro original: a fonte é
    16:9 e o painel é 9:16, então o que sobra é o miolo. Por isso o trecho tem
    de ser escolhido com o assunto NO CENTRO — plano aberto vira moldura com
    nada dentro.

    `u` é o tempo em segundos desde o início do cartão; cada painel entra `cada`
    segundos depois do anterior, subindo e aparecendo.
    """
    fora = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    n = len(clipes)
    vao = int(W * 0.018)
    pw = (int(W * larg) - vao * (n - 1)) // n
    # 4:5, não 9:16. Trailer de cinema é 2.39:1, e um painel 9:16 guarda 23% da
    # largura do plano — o que sobra é um olho. `prop` 1,25 guarda um terço a
    # mais e o trecho continua reconhecível, que é a única coisa que o tríptico
    # precisa entregar.
    ph = int(pw * prop)
    x0 = (W - (pw * n + vao * (n - 1))) // 2
    y0 = int(H * topo)
    for i, c in enumerate(clipes):
        t = u - i * cada
        if t <= 0:
            continue
        k = _suave_saida(min(1.0, t / 0.30))
        # A tarja do cinemascope sai ANTES do recorte. Trailer de cinema vem
        # 2.39:1 dentro de um 16:9, e recortar o retrato sem tirar a tarja
        # primeiro guarda faixa preta dentro do painel — foi o que o primeiro
        # teste mostrou: três celulares com barra em cima e embaixo.
        # a tarja vem decidida de fora (uma por painel, `tarja_de`) sempre que
        # possível: medida quadro a quadro ela muda de tamanho e o painel pulsa
        cr = c.convert("RGB")
        cr = cr.crop(tarjas[i]) if tarjas and tarjas[i] else sem_tarja(cr)
        alvo = cr.height * pw / ph
        if cr.width > alvo:
            e = int((cr.width - alvo) / 2)
            cr = cr.crop((e, 0, cr.width - e, cr.height))
        cr = cr.resize((pw, ph), Image.LANCZOS).convert("RGBA")
        masc = Image.new("L", (pw, ph), 0)
        ImageDraw.Draw(masc).rounded_rectangle([0, 0, pw - 1, ph - 1], raio, fill=255)
        cr.putalpha(masc.point(lambda p: int(p * k)))
        x = x0 + i * (pw + vao)
        y = y0 + int((1 - k) * ph * 0.10)      # sobe um décimo da altura ao entrar
        fora.alpha_composite(cr, (x, y))
    return fora


def ate_o_corte(quadros, piso=6.0, fator=4.0):
    """Corta a lista de quadros no primeiro CORTE DE PLANO que houver dentro.

    Um painel de tríptico toca pouco mais de um segundo e depois congela no
    último quadro. Se o trecho escolhido atravessa um corte do vídeo de origem,
    o painel congela no plano SEGUINTE — e foi o que aconteceu nos três painéis
    do projeto 15: o rosto do ator virou uma cidade noturna, a atriz virou outro
    passageiro, e a heroína virou um céu de nuvens.

    Achar o corte é barato e não depende de escolher a duração na mão: a
    diferença média entre quadros vizinhos dá um salto de uma ordem de grandeza
    num corte seco. Quem escolhe o `src` continua escolhendo o plano; isto só
    garante que o painel não passa dele.

    **Só pega corte SECO.** Dissolução e chicote passam batido — a diferença
    entre quadros vizinhos numa dissolução é pequena, por definição. No 15 foi
    assim que a heroína virou céu de nuvens mesmo com a trava ligada. Onde a
    origem transiciona sem corte, o jeito é olhar o último quadro do painel; é
    por isso que a tira fina continua sendo obrigatória.
    """
    if len(quadros) < 3:
        return quadros
    pequenos = [np.asarray(Image.open(q).convert("L").resize((80, 45)), dtype=np.float32)
                for q in quadros]
    difs = [float(np.abs(pequenos[i + 1] - pequenos[i]).mean())
            for i in range(len(pequenos) - 1)]
    base = float(np.median(difs))
    for i, v in enumerate(difs):
        if v > max(piso, base * fator):
            return quadros[:max(1, i + 1)]
    return quadros


def com_triptico(aroll_img, clipes, u, **kw):
    """o tríptico sobre o A-roll escurecido — o fundo não disputa com as três."""
    base = _pb_desfocado(aroll_img, 0.0).convert("RGBA")
    base.alpha_composite(triptico(clipes, u, **kw))
    return base.convert("RGB")


def frase_hook(img, linhas, destaque=0, u=1.0, dur=2.0, altura=0.30):
    """Uma frase no REGISTRO DO HOOK, fora do hook.

    O hook tem uma tipografia própria — corpo grande, uma linha em destaque,
    sombra dura — e ela só existia nos 3 s iniciais. Quando a fala anuncia o
    que o vídeo vai fazer («três princípios do lançamento da Rockstar»), a
    promessa merece o mesmo peso da provocação que abriu. É a mesma letra, no
    meio do vídeo, sem o vídeo de prova em cima.

    Entra linha a linha e sai por opacidade; não desliza, porque texto que
    viaja pelo quadro rouba o olho do que está escrito.
    """
    t = u * dur
    saida = 1.0 if t < dur - 0.30 else max(0.0, (dur - t) / 0.30)
    if saida <= 0:
        return img
    camada = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if TIPOGRAFIA == "minusculo":
        # o titulo em duas vozes entra por opacidade (0,22 s) e sai por opacidade:
        # nada desliza, pela mesma razao do registro antigo
        k = min(1.0, t / 0.22)
        a = int(255 * _suave_saida(k) * saida)
        dest = destaque if 0 <= destaque < len(linhas) else len(linhas) - 1
        titulo_duas_vozes(camada, linhas, dest, int(H * altura), alpha=a)
        fora = img.convert("RGBA")
        fora.alpha_composite(camada)
        return fora.convert("RGB")
    d = ImageDraw.Draw(camada)
    LIM = int(W * 0.92)
    y = int(H * altura)
    for i, l in enumerate(linhas):
        if t < i * 0.14:
            continue
        k = min(1.0, (t - i * 0.14) / 0.22)
        px = 132 if i == destaque else 84
        f = _fonte(px)
        while d.textbbox((0, 0), l, font=f)[2] > LIM and px > 56:
            px -= 4
            f = _fonte(px)
        w = d.textbbox((0, 0), l, font=f)[2]
        lx = (W - w) // 2
        a = int(255 * _suave_saida(k) * saida)
        for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3), (5, 6)):
            d.text((lx + dx, y + dy), l, font=f, fill=(0, 0, 0, a))
        d.text((lx, y), l, font=f,
               fill=((246, 169, 59, a) if i == destaque else (255, 255, 255, a)))
        y += int(px * 1.06)
    fora = img.convert("RGBA")
    fora.alpha_composite(camada)
    return fora.convert("RGB")


def logo_atras(aroll_img, logo_img, u, dur, matte_png=None, larg=0.38, base=None):
    """Uma marca SOBE por trás de quem fala, e para ONDE OS INSERTS PARAM.

    É o modo 1 aplicado a um símbolo em vez de um trecho: o autor continua na
    frente, recortado, e a marca entra atrás dele. Some quando a frase que a
    citou acaba — marca que fica depois disso deixa de ilustrar e vira anúncio.

    A altura de parada não é um número solto: é `BASE_MODO1`, a mesma linha em
    que a borda de baixo de todo cartão de prova assenta. Um símbolo que para
    noutra altura lê como elemento de outro vídeo colado neste.

    O arquivo tem de vir com FUNDO TRANSPARENTE. Ícone de aplicativo vem com
    fundo chapado por desenho, e chapado sobre o A-roll vira adesivo; o que
    entra atrás de alguém é a marca, não a caixa dela.

    Sem o matte a função ainda funciona, mas a marca passa NA FRENTE do rosto;
    quem chama deve providenciar o recorte.
    """
    t = u * dur
    k = _suave_saida(min(1.0, t / 0.55))
    saida = 1.0 if t < dur - 0.35 else max(0.0, (dur - t) / 0.35)
    if saida <= 0:
        return aroll_img
    lw = int(W * larg)
    lh = int(lw * logo_img.height / max(1, logo_img.width))
    lg = logo_img.convert("RGBA").resize((lw, lh), Image.LANCZOS)
    if saida < 1.0:
        lg.putalpha(lg.getchannel("A").point(lambda p: int(p * saida)))
    y_fim = int(H * (BASE_MODO1 if base is None else base)) - lh
    y = int(H * 1.02 + (y_fim - H * 1.02) * k)
    fundo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fundo.alpha_composite(lg, ((W - lw) // 2, y))
    fora = aroll_img.convert("RGBA")
    fora.alpha_composite(fundo)
    if matte_png:
        fora.alpha_composite(Image.open(matte_png).convert("RGBA"))
    return fora.convert("RGB")


MARCADOR_X, MARCADOR_Y = 0.13, 0.11   # medidos no corpus
LARANJA = (249, 146, 3)


def _oblicuo(camada, k=0.20):
    """Inclina a camada para a direita sem deformar a altura da letra.

    O corpus usa negrito OBLIQUO, e oblique nao e italico: e a mesma letra
    cisalhada. Sintetizar por cisalhamento da camada da o mesmo desenho sem
    depender de o sistema ter a variante oblique da fonte instalada — e nao
    tem, nesta maquina.
    """
    w, h = camada.size
    return camada.transform((w + int(h * k), h), Image.AFFINE,
                            (1, k, -k * h, 0, 1, 0), resample=Image.BICUBIC)


def marcador(img, numero, nome, u, dur, cor=None):
    """O terceiro registro de tipografia do formato: o marcador de capitulo.

    `formato-analise.md` descreve as duas variantes do corpus e o `cartao.py`
    nunca teve nenhuma das duas — entao o unico jeito de o espectador saber em
    que principio esta era ouvir o numero. Quem assiste sem som (a maior parte)
    perdia a contagem, que e exatamente o que o teste final do formato mede.

    Esta e a segunda variante: `1.` branco em negrito obliquo no alto a
    esquerda, com o nome do capitulo entrando ao lado. O numero POPA e o nome
    ABRE por revelacao lateral — o nome nao desliza, ele e descoberto, porque
    texto que viaja pelo quadro puxa o olho para o movimento em vez da palavra.

    A ancora ideal do corpus e o GESTO (os dedos levantados). Nao ha detector de
    mao aqui, entao quem chama ancora na palavra que conta — e isso esta dito,
    para ninguem supor que a regra do gesto foi cumprida.
    """
    cor = cor or CREME
    ENTRA, ABRE, SAI = 0.16, 0.34, 0.24
    t = u * dur
    if t < 0:
        return img
    saida = 1.0 if t < dur - SAI else max(0.0, (dur - t) / SAI)
    if saida <= 0:
        return img

    px = int(H * 0.062)                      # altura de letra do numero
    camada = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(camada)
    x0, y0 = int(W * MARCADOR_X), int(H * MARCADOR_Y)

    if TIPOGRAFIA == "minusculo":
        # o marcador nas duas vozes da referencia: «1.» em sans negrito, o nome do
        # capitulo em serifa italica por baixo, ambos no alto a esquerda, no
        # mesmo lugar medido no corpus. O numero entra crescendo; o nome, por
        # opacidade — sem revelacao lateral, que so fazia sentido em caixa alta.
        k = min(1.0, t / ENTRA) if ENTRA else 1.0
        escala = 0.78 + 0.22 * _suave_saida(k)
        f_num = sans(int(px * 1.15 * escala), 800)
        txt = f"{numero}."
        _sombra_suave(camada, (x0, y0), txt, f_num, alpha=150, raio=7)
        d.text((x0, y0), txt, font=f_num, fill=(*cor, 255))
        if nome and t > ENTRA * 0.6:
            v = min(1.0, (t - ENTRA * 0.6) / ABRE)
            f_nome = serifa_italica(int(px * 0.62), 400)
            LIM = int(W * 0.94) - x0
            nm = nome.lower()
            while d.textbbox((0, 0), nm, font=f_nome)[2] > LIM and f_nome.size > 24:
                f_nome = serifa_italica(f_nome.size - 2, 400)
            ny = y0 + int(px * 1.15 * 0.92)
            nx = x0 + int(px * 0.55)
            a = int(255 * _suave_saida(v))
            _sombra_suave(camada, (nx, ny), nm, f_nome, alpha=int(a * 0.6), raio=5)
            d.text((nx, ny), nm, font=f_nome, fill=(*cor, a))
        if saida < 1.0:
            camada.putalpha(camada.getchannel("A").point(lambda p: int(p * saida)))
        fora = img.convert("RGBA")
        fora.alpha_composite(camada)
        return fora.convert("RGB")

    f_num, f_nome = _fonte(px), _fonte(int(px * 0.42))
    txt = f"{numero}."
    # o numero entra crescendo de 0,78 a 1,0 — desenhado em camada propria para
    # poder ser escalado e cisalhado sem tocar no resto
    k = min(1.0, t / ENTRA) if ENTRA else 1.0
    escala = 0.78 + 0.22 * _suave_saida(k)
    cx = d.textbbox((0, 0), txt, font=f_num)
    num = Image.new("RGBA", (cx[2] + px, cx[3] + px // 2), (0, 0, 0, 0))
    dn = ImageDraw.Draw(num)
    for dx, dy in ((3, 4), (5, 6)):
        dn.text((dx, dy), txt, font=f_num, fill=(0, 0, 0, 170))
    dn.text((0, 0), txt, font=f_num, fill=(*cor, 255))
    num = _oblicuo(num)
    if escala != 1.0:
        num = num.resize((max(1, int(num.width * escala)),
                          max(1, int(num.height * escala))), Image.LANCZOS)
    camada.alpha_composite(num, (x0, y0))

    # o nome abre a partir da direita do numero, por revelacao
    if nome and t > ENTRA * 0.6:
        v = min(1.0, (t - ENTRA * 0.6) / ABRE)
        # a direita do NUMERO, nao da camada: a camada tem folga para a sombra e
        # para o cisalhamento, e usar a largura dela abria um vao de ~90 px
        nx = x0 + int((cx[2] + px * 0.20) * escala) + int(px * 0.30)
        ny = y0 + int(px * 0.42)
        # o nome nunca sai pela borda: encolhe ate caber, como a legenda faz
        LIM = int(W * 0.94) - nx
        while d.textbbox((0, 0), nome.upper(), font=f_nome)[2] > LIM and f_nome.size > 20:
            f_nome = _fonte(f_nome.size - 2)
        alvo = Image.new("RGBA", (W - nx, px), (0, 0, 0, 0))
        da = ImageDraw.Draw(alvo)
        for dx, dy in ((2, 3), (3, 4)):
            da.text((dx, dy), nome.upper(), font=f_nome, fill=(0, 0, 0, 170))
        da.text((0, 0), nome.upper(), font=f_nome, fill=(*cor, 255))
        larg = int(alvo.width * _suave_saida(v))
        camada.alpha_composite(alvo.crop((0, 0, max(1, larg), alvo.height)), (nx, ny))

    if saida < 1.0:
        a = camada.getchannel("A").point(lambda p: int(p * saida))
        camada.putalpha(a)
    fora = img.convert("RGBA")
    fora.alpha_composite(camada)
    return fora.convert("RGB")


def grupos(palavras, por=3, pausa_ms=170):
    """As palavras em grupos de 2 a 4, quebrando ONDE A FALA RESPIRA.

    Agrupar de tres em tres mecanicamente produz "PAIS PRA COMPRAR", "AGORA,
    TEMOS CARTAO", "DE CREDITO, TEMOS" — a frase parte no meio e o olho tropeca.
    Era o defeito do primeiro master do projeto 14.

    Tres gatilhos de quebra, em ordem de forca:
      1. pontuacao de fim de frase na palavra (. ? ! :) — quebra sempre
      2. pausa entre duas palavras acima de `pausa_ms` — quebra
      3. o grupo chegou a `por` palavras E a proxima pausa nao e a menor da
         vizinhanca — quebra no respiro mais proximo, nao na contagem
    """
    def fecha(ws):
        return {"texto": " ".join(x["p"] for x in ws).strip(),
                "de": ws[0]["de"], "ate": ws[-1]["ate"]}

    # 1) parte em frases, pela pontuacao — a quebra mais forte que existe
    frases, atual = [], []
    for p in palavras:
        atual.append(p)
        if p["p"].strip().endswith((".", "?", "!", ":")):
            frases.append(atual)
            atual = []
    if atual:
        frases.append(atual)

    # 2) dentro da frase, quebra nos MAIORES respiros, nao a cada N palavras.
    #    Contar palavras produz "TEM PAI QUE VAI / VER O FILHO FAZER"; escolher o
    #    maior buraco produz "TEM PAI / QUE VAI VER O FILHO FAZER 13 ANOS".
    # Dentro da frase, a quebra e um problema de otimizacao, nao de heuristica:
    # duas regras competem — o grupo quer ter 3 ou 4 palavras, E quer terminar
    # onde a voz respira. Escolher so pelo respiro produz pedacos de duas
    # palavras; escolher so pela contagem parte o sintagma no meio. Uma
    # programacao dinamica sobre a frase inteira resolve as duas de uma vez.
    MIN, MAX, IDEAL = 2, 5, 3.5

    def custo(ws, gap_depois):
        n = len(ws)
        pena = (n - IDEAL) ** 2 * 12                 # fugir do tamanho ideal custa
        premio = min(gap_depois, 400) * 0.35         # respirar depois rende
        curto = 60 if len(" ".join(w["p"] for w in ws)) > 34 else 0
        return pena - premio + curto                 # linha longa demais custa

    g = []
    for f in frases:
        n = len(f)
        if n <= MAX:
            g.append(fecha(f))
            continue
        gap = [f[i + 1]["de"] - f[i]["ate"] for i in range(n - 1)] + [9999]
        INF = float("inf")
        melhor = [INF] * (n + 1)
        volta = [0] * (n + 1)
        melhor[0] = 0
        for j in range(1, n + 1):
            for i in range(max(0, j - MAX), j - MIN + 1):
                if melhor[i] == INF:
                    continue
                c = melhor[i] + custo(f[i:j], gap[j - 1])
                if c < melhor[j]:
                    melhor[j], volta[j] = c, i
        if melhor[n] == INF:                         # frase que nao fecha: parte igual
            g.append(fecha(f))
            continue
        cortes, j = [], n
        while j > 0:
            cortes.append((volta[j], j))
            j = volta[j]
        for i, j in reversed(cortes):
            g.append(fecha(f[i:j]))
    return g


# ----------------------------------------------------------- prova social
def _quebra(d, texto, f, larg):
    linhas, atual = [], ""
    for p in texto.split():
        t = (atual + " " + p).strip()
        if d.textbbox((0, 0), t, font=f)[2] > larg and atual:
            linhas.append(atual)
            atual = p
        else:
            atual = t
    if atual:
        linhas.append(atual)
    return linhas


def bolha(c, larg, pad=30):
    """um comentario, sozinho, no seu proprio cartao.

    Separar em bolhas existe para o pop-up: a prova social do formato nao e "um
    print com varios comentarios", e "varias pessoas dizendo a mesma coisa, uma
    depois da outra". Uma bolha por vez, entrando, faz o espectador CONTAR — e
    contar e o que transforma comentario em evidencia de volume.
    """
    f_txt, f_aut, f_num = _fonte(38), _fonte(29), _fonte(26)
    d0 = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    ls = _quebra(d0, c["texto"], f_txt, larg - 2 * pad)
    tr = c.get("traducao")
    lt = _quebra(d0, tr, _fonte(30), larg - 2 * pad) if tr else []
    alt = pad + 36 + len(ls) * 46 + (len(lt) * 36 + 8 if lt else 0) + 34 + pad

    im = Image.new("RGBA", (larg, alt), (0, 0, 0, 0))
    m = Image.new("L", (larg, alt), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, larg - 1, alt - 1], radius=26, fill=255)
    fundo = Image.new("RGBA", (larg, alt), (30, 28, 33, 250))
    im = Image.composite(fundo, im, m)

    d = ImageDraw.Draw(im)
    y = pad
    d.text((pad, y), c["autor"], font=f_aut, fill=(150, 200, 255))
    y += 36
    for l in ls:
        d.text((pad, y), l, font=f_txt, fill=(242, 240, 238))
        y += 46
    if lt:
        y += 8
        for l in lt:
            d.text((pad, y), l, font=_fonte(30), fill=(168, 164, 170))
            y += 36
    # `selo` troca o coracao por outra marca de procedencia — data, veiculo,
    # numero de compartilhamentos. O que nao pode e nao ter nenhuma: e a marca
    # que separa "alguem digitou isto" de "isto foi publicado e pode ser conferido".
    d.text((pad, y + 2), c.get("selo") or f"♥  {c['curtidas']}", font=f_num,
           fill=(150, 146, 150))
    return im


def _pop(u):
    """escala da bolha entrando: passa de 1 e volta, como balao de chat."""
    if u >= 1:
        return 1.0
    return 1.08 * (1 - (1 - u) ** 3) - 0.08 * (1 - u) ** 2 * 3 + 0.06 * u


def prova_social_popup(comentarios, t, larg=None, cada=1.15, pop=0.32, gap=18):
    """As bolhas entrando uma a uma, empilhadas, no instante `t` (segundos).

    Cada bolha entra `cada` segundos depois da anterior, com um pop de `pop`
    segundos. As que ja entraram ficam — o empilhamento E o argumento.
    """
    larg = larg or int(W * 0.86)
    bolhas = [bolha(c, larg) for c in comentarios]
    visiveis = [(b, i) for i, b in enumerate(bolhas) if t >= i * cada]
    if not visiveis:
        visiveis = [(bolhas[0], 0)]
    alt = sum(b.height for b, _ in visiveis) + gap * (len(visiveis) - 1)
    im = Image.new("RGBA", (larg, max(1, alt)), (0, 0, 0, 0))
    y = 0
    for b, i in visiveis:
        u = min(1.0, max(0.0, (t - i * cada) / pop))
        e = _pop(u)
        if e < 0.999:
            lw, lh = max(2, int(b.width * e)), max(2, int(b.height * e))
            bb = b.resize((lw, lh), Image.LANCZOS)
            a = bb.getchannel("A").point(lambda v: int(v * min(1.0, u * 2.5)))
            bb.putalpha(a)
            im.alpha_composite(bb, ((larg - lw) // 2, y + (b.height - lh) // 2))
        else:
            im.alpha_composite(b, (0, y))
        y += b.height + gap
    return im


def prova_social(comentarios, fonte, larg=None):
    """O cartao de comentarios: o texto real, o @ real, a contagem real.

    Por que NAO e uma captura da interface do YouTube: desenhar a interface de
    terceiro seria imitar marca alheia, que e limite escrito do SKILL.md. O que
    esta pagina faz e CITAR — texto integral, autor creditado, contagem de
    curtidas e a fonte escrita no rodape. Tudo verificavel, nada imitado.

    E por que a contagem vai junto: sem ela e um texto que alguem digitou; com
    ela e um fato sobre quantas pessoas concordaram. A contagem e metade da
    prova, e essa parte da regra do formato vale aqui igual.
    """
    larg = larg or int(W * 0.86)
    pad, gap = 34, 26
    f_txt, f_aut, f_num = _fonte(38), _fonte(30), _fonte(28)
    d0 = ImageDraw.Draw(Image.new("RGB", (10, 10)))

    blocos, alt = [], pad
    for c in comentarios:
        ls = _quebra(d0, c["texto"], f_txt, larg - 2 * pad)
        h = 40 + len(ls) * 46 + 34
        blocos.append((c, ls, h))
        alt += h + gap
    alt += 44

    im = Image.new("RGBA", (larg, alt), (28, 26, 30, 255))
    d = ImageDraw.Draw(im)
    y = pad
    for c, ls, h in blocos:
        d.text((pad, y), c["autor"], font=f_aut, fill=(150, 200, 255))
        y += 40
        for l in ls:
            d.text((pad, y), l, font=f_txt, fill=(242, 240, 238))
            y += 46
        d.text((pad, y + 2), f"♥  {c['curtidas']}", font=f_num, fill=(150, 146, 150))
        y += 34 + gap
    d.text((pad, alt - 40), fonte, font=_fonte(24), fill=(128, 124, 128))
    return im


# ------------------------------------------------------------- dramatizacao
def conversa(mensagens, larg=None, ate=None, titulo=None):
    """Um mock de conversa de celular, para ILUSTRAR uma memoria.

    ISTO NAO E PROVA, e a distincao e a regra mais importante deste arquivo.
    O cartao de comentarios (`prova_social`) cita gente real e por isso tem de
    ser verdadeiro. Isto aqui e encenacao — a cena universal que a frase
    descreve, do mesmo jeito que se contrataria um ator. Vale para "quando a
    gente tinha que pedir pros nossos pais", nunca para "olha o que as pessoas
    disseram".

    Duas travas que fazem a diferenca ficar de pe:
      - **sem marca.** Bolha, cor e horario leem como aplicativo de mensagem sem
        clonar logo, cabecalho nem tipografia de ninguem. Imitar a interface de
        um app e imitar marca de terceiro.
      - **sem pessoa real.** Nomes sao papeis ("Pai", "Eu aos 12"), nunca nome,
        foto ou numero de alguem.
    E no `provas.json` ela sai marcada `"tipo": "dramatizacao"`, para ninguem
    dois projetos adiante confundir com registro.
    """
    larg = larg or int(W * 0.84)
    pad, gap = 26, 14
    f_txt, f_hora, f_tit = _fonte(36), _fonte(22), _fonte(30)
    d0 = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    VERDE, BRANCO = (37, 91, 69, 255), (44, 44, 48, 255)

    postas = mensagens if ate is None else mensagens[:max(1, ate)]
    blocos = []
    for m in postas:
        ls = _quebra(d0, m["texto"], f_txt, int(larg * 0.72) - 2 * pad)
        blocos.append((m, ls, len(ls) * 44 + 2 * pad - 6))
    alt = sum(h for _, _, h in blocos) + gap * (len(blocos) + 1) + (52 if titulo else 0)

    im = Image.new("RGBA", (larg, alt), (17, 19, 18, 255))
    d = ImageDraw.Draw(im)
    y = gap
    if titulo:
        d.text((pad, y), titulo, font=f_tit, fill=(150, 146, 150))
        y += 52
    for m, ls, h in blocos:
        meu = m.get("meu", False)
        bw = max(_quebra and max(d0.textbbox((0, 0), l, font=f_txt)[2] for l in ls), 120) + 2 * pad
        bw = min(bw, int(larg * 0.72))
        bx = larg - bw - pad if meu else pad
        cor = VERDE if meu else BRANCO
        d.rounded_rectangle([bx, y, bx + bw, y + h], radius=20, fill=cor)
        ty = y + pad - 6
        for l in ls:
            d.text((bx + pad, ty), l, font=f_txt, fill=(236, 234, 232))
            ty += 44
        if m.get("hora"):
            d.text((bx + bw - 62, y + h - 26), m["hora"], font=f_hora, fill=(150, 160, 152))
        y += h + gap
    return im


# ------------------------------------------------- enquadramento pelo rosto
def enquadramento_fixo(amostras, escala=1.25, alto=0.50, sobra=0.03):
    """UM enquadramento para o vídeo inteiro, e a altura segura do cartão.

    O rastreamento ESCOLHE o quadro; ele não o anima. Cartão presa a uma cabeça
    que se mexe e um cartão que treme, e rosto rastreado quadro a quadro deriva
    dentro do plano e salta na emenda — o video fica picotado sem um corte a
    mais. Ver `formato-analise.md`, "O quadro nao se mexe".

    Devolve (centro, base_do_cartao). A ordem do calculo importa: primeiro o
    enquadramento, depois o ponto mais ALTO que a cabeca alcanca dentro dele, e
    so entao a largura de cartao que cabe. Escolher a largura primeiro leva a um
    topo negativo, fora da tela.
    """
    import statistics as st
    xs = sorted(a["centerX"] for a in amostras)
    ys = sorted(a["centerY"] for a in amostras)
    cx, cy = st.median(xs), st.median(ys)
    topos = []
    for a in amostras:
        y = (a["centerY"] - cy) * escala + alto
        h = a["height"] * escala
        topos.append(y - h / 2 - 0.30 * h)
    topos.sort()
    mais_alto = topos[len(topos) // 20]          # p5: descarta erro de rastreio
    return {"cx": cx, "cy": cy, "escala": escala, "alto": alto}, round(mais_alto + sobra, 3)


def enquadrar_fixo(img_cheia, q):
    """o recorte do enquadramento escolhido, igual em todo quadro."""
    cw, ch = int(W / q["escala"]), int(H / q["escala"])
    x = int(max(0, min(W - cw, q["cx"] * W - cw / 2)))
    y = int(max(0, min(H - ch, q["cy"] * H - ch * q["alto"])))
    return img_cheia.crop((x, y, x + cw, y + ch)).resize((W, H), Image.LANCZOS)


def brilho(img, forca):
    """O clarao quente do corte — o «Brilho 3», em dose baixa.

    Nao esconde o corte: da ao olho um evento para ancorar, e o olho para de
    CONTAR cortes. Acima de ~25% vira flash e o espectador passa a contar
    flashes, que e pior. `forca` de 0 a 1; o pico util fica entre 0,12 e 0,18.
    """
    if forca <= 0.001:
        return img
    v = Image.new("RGB", img.size, (255, 246, 232))
    return Image.blend(img.convert("RGB"), v, min(0.35, forca))


def rampa_brilho(quadros_do_corte, n, largura=4):
    """a forca do brilho no quadro `n`, dado o conjunto de quadros de emenda."""
    if not quadros_do_corte:
        return 0.0
    d = min(abs(n - c) for c in quadros_do_corte)
    if d > largura:
        return 0.0
    return 0.16 * (1 - d / (largura + 1)) ** 1.5


def enquadrar(img_cheia, rosto, escala=1.35, alto=0.40):
    """O autor maior, com o rosto ancorado, para os momentos SEM cartao.

    Sem cartao em quadro o plano e so rosto, e rosto parado em plano aberto e o
    que mais solta espectador. `rastrear-rosto` devolve centro e caixa em
    fracao do quadro; aqui o recorte segue o centro e poe os olhos em `alto`.

    Nao confundir com a aproximacao lenta de `formato-analise.md`: aquela e um
    movimento DENTRO de um plano. Esta e o enquadramento do plano, e ela so
    existe onde nao ha cartao — nunca as duas ao mesmo tempo.
    """
    cw, ch = int(W / escala), int(H / escala)
    cx = rosto["centerX"] * W
    cy = rosto["centerY"] * H
    x = int(max(0, min(W - cw, cx - cw / 2)))
    y = int(max(0, min(H - ch, cy - ch * alto)))
    return img_cheia.crop((x, y, x + cw, y + ch)).resize((W, H), Image.LANCZOS)


def suavizar(amostras, janela_s=0.8):
    """media movel no caminho do rosto: rastreio cru treme, e tremor em
    enquadramento le como camera na mao — que este formato nao tem."""
    out = []
    for i, a in enumerate(amostras):
        viz = [b for b in amostras if abs(b["time"] - a["time"]) <= janela_s / 2]
        out.append({**a,
                    "centerX": sum(b["centerX"] for b in viz) / len(viz),
                    "centerY": sum(b["centerY"] for b in viz) / len(viz)})
    return out


def rosto_em(amostras, t):
    """a amostra mais proxima de `t`; interpola entre as duas vizinhas."""
    if not amostras:
        return None
    ant = [a for a in amostras if a["time"] <= t]
    dep = [a for a in amostras if a["time"] > t]
    if not ant:
        return dep[0]
    if not dep:
        return ant[-1]
    a, b = ant[-1], dep[0]
    k = (t - a["time"]) / max(1e-6, b["time"] - a["time"])
    return {**a,
            "centerX": a["centerX"] + k * (b["centerX"] - a["centerX"]),
            "centerY": a["centerY"] + k * (b["centerY"] - a["centerY"])}


# ------------------------------------------------------- a banda do hook
def hook_banda(aroll_img, clipe_img, linhas, destaque=0, rosto=None,
               suavizar=0.30, alto=0.60):
    """Os primeiros 3 s: video em cima, o autor no meio, o texto embaixo.

    Decisao do dono em 2026-09-13: "no hook visual, pode ter o texto embaixo, eu
    no meio e em cima um video". E uma composicao de tres faixas, e vale so no
    hook — depois dele o quadro volta a ser o do formato.

    Isto NAO contraria "o formato nao tem cartela de abertura": nao ha cartela,
    nao ha fundo chapado e nao ha logo. O autor esta em quadro do primeiro
    quadro, falando, e o video de cima e prova, nao enfeite.
    """
    a = aroll_img.convert("RGBA")
    if rosto:
        a = enquadrar(a, rosto, escala=1.25, alto=alto).convert("RGBA")
    out = Image.new("RGBA", (W, H))
    out.paste(a, (0, 0))

    # O insert ocupa a FAIXA DE CIMA inteira, sem moldura e sem corte: largura
    # cheia, altura pela proporção dele. A divisa com o autor não é uma linha —
    # é uma dissolução dos últimos `suavizar` da altura do insert, de opaco a
    # transparente. Linha dura ali lê como duas janelas empilhadas; dissolvida,
    # lê como um quadro só.
    #
    # A versão anterior punha um cartão arredondado flutuando a 10% da altura, e
    # ele caía em cima da testa do autor. Duas coisas não podem ser cortadas
    # neste quadro: o rosto de quem fala e a prova de que se fala. Por isso o
    # insert é CONTIDO (nunca recortado para preencher) e o enquadramento do
    # autor desce, até a cabeça começar abaixo da parte opaca.
    ch = int(W * clipe_img.height / max(1, clipe_img.width))
    faixa = clipe_img.convert("RGB").resize((W, ch), Image.LANCZOS).convert("RGBA")
    n = max(1, int(ch * suavizar))
    rampa = np.linspace(255, 0, n).astype(np.uint8)
    alfa = np.full((ch, W), 255, dtype=np.uint8)
    alfa[ch - n:, :] = rampa[:, None]
    faixa.putalpha(Image.fromarray(alfa, mode="L"))
    out.alpha_composite(faixa, (0, 0))

    d = ImageDraw.Draw(out)
    y = int(H * 0.70)
    # A linha do hook NUNCA estoura a moldura. A `legenda` já encolhia até
    # caber; o hook não, e uma linha de 18 caracteres no corpo de destaque saiu
    # decepada dos dois lados no primeiro quadro do vídeo — o quadro que serve
    # de capa e que o feed mostra parado. O piso é 56 px: abaixo disso a linha
    # perde o contraste de corpo que define o registro, e o certo é reescrever a
    # frase, não espremer mais.
    LIM = int(W * 0.92)
    for i, l in enumerate(linhas):
        px = 132 if i == destaque else 84
        f = _fonte(px)
        while d.textbbox((0, 0), l, font=f)[2] > LIM and px > 56:
            px -= 4
            f = _fonte(px)
        w = d.textbbox((0, 0), l, font=f)[2]
        lx = (W - w) // 2
        for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3), (5, 6)):
            d.text((lx + dx, y + dy), l, font=f, fill=(0, 0, 0))
        d.text((lx, y), l, font=f, fill=(246, 169, 59) if i == destaque else (255, 255, 255))
        y += int(px * 1.06)
    return out.convert("RGB")
