#!/usr/bin/env python3
"""
compor.py — o vídeo inteiro, sem navegador.

O Remotion precisava de um Chrome headless que, num dia, deixou de responder e
levou uma hora de espera com ele. Este compositor le o MESMO plano.json e faz o
trabalho com o que nunca trava: Pillow desenha cada motion graphics quadro a
quadro, e o ffmpeg sobrepoe os quadros no A-roll, mistura voz e cama, queima a
legenda palavra a palavra e aplica a grade.

O contrato e o plano.json — o diretor, o montar.py e as travas nao mudam.

Uso: compor.py --projeto motion/ [--out motion/out/master.mp4] [--escala 1.0]
                [--crf 18] [--so-clips]
"""
import argparse, json, math, shutil, subprocess, sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import acabamento  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

FPS = 30
FRAMES_ENTRADA, FRAMES_SAIDA = 10, 13   # entrada 0,33 s · saida ~0,43 s (ritmo.md)
GRADE = {"fundo": (12, 12, 12), "sujeito": (204, 202, 200), "texto": (255, 255, 255),
         "quente": (255, 176, 103), "frio": (127, 180, 255), "ambar": (255, 163, 58),
         "alerta": (201, 72, 80), "painel": (38, 42, 49), "cromo": (49, 54, 63)}
LOTE_OVERLAYS = 8   # sobreposicoes por passada de ffmpeg


# ---------- fontes e desenho ----------------------------------------------

_FONTES = {}


def fonte(nome, tamanho, raiz):
    chave = (nome, tamanho)
    if chave not in _FONTES:
        arq = {"impacto": "ArchivoBlack-Regular.ttf", "leitura": "Inter.ttf",
               "mono": "IBMPlexMono-Medium.ttf", "serifa": "Fraunces.ttf"}[nome]
        caminho = raiz / "public" / "fontes" / arq
        _FONTES[chave] = ImageFont.truetype(str(caminho), tamanho) if caminho.is_file() \
            else ImageFont.load_default(size=tamanho)
    return _FONTES[chave]


def ease_out(t):
    return 1 - (1 - max(0.0, min(1.0, t))) ** 3


def ease_in(t):
    return max(0.0, min(1.0, t)) ** 3


def mola(t):
    """uma mola simples: passa de 1 e assenta"""
    t = max(0.0, min(1.0, t))
    return 1 - math.exp(-6 * t) * math.cos(8 * t)


def quebrar(texto, f, largura, d):
    linhas, atual = [], ""
    for w in texto.split():
        prova = (atual + " " + w).strip()
        if d.textlength(prova, font=f) <= largura:
            atual = prova
        else:
            if atual:
                linhas.append(atual)
            atual = w
    if atual:
        linhas.append(atual)
    return linhas


def brilho(im, cor, raio=18, forca=0.6):
    """um halo atras do que ja esta desenhado (canal alfa)"""
    a = im.split()[3].filter(ImageFilter.GaussianBlur(raio))
    halo = Image.new("RGBA", im.size, cor + (0,))
    halo.putalpha(a.point(lambda v: int(v * forca)))
    return Image.alpha_composite(halo, im)


# ---------- componentes ---------------------------------------------------

class Cena:
    """um motion graphics; `quadro(f)` devolve RGBA do frame f (sem envelope)"""

    def __init__(self, plano, raiz, W, H, acumulado):
        self.p, self.raiz, self.W, self.H = plano, raiz, W, H
        self.dur = max(1, round(plano["duracaoMs"] / 1000 * FPS))
        self.acumulado = acumulado
        self.img = None
        if plano.get("asset"):
            arq = raiz / "public" / plano["asset"]
            if arq.is_file():
                self.img = Image.open(arq).convert("RGB")

    def fundo(self):
        return Image.new("RGBA", (self.W, self.H), GRADE["fundo"] + (255,))

    def quadro(self, f):
        t = self.p["tipo"]
        fn = getattr(self, "c_" + t, None)
        return fn(f) if fn else self.c_objeto(f)

    # -- palavras --------------------------------------------------------
    def c_palavras(self, f):
        im = self.fundo()
        W, H, r = self.W, self.H, self.raiz
        s = W / 1080
        novas = self.p.get("palavras") or []
        lista = list(self.acumulado) + list(novas)
        fant = self.p.get("fantasmas") or []
        acender = bool(self.p.get("acender"))
        if fant:
            cam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(cam)
            fnt = fonte("impacto", int(64 * s), r)
            linhas = quebrar(" ".join(fant), fnt, W * 0.85, d)
            alt = int(74 * s)
            y = H / 2 - alt * len(linhas) / 2
            op = int(255 * (0.34 - 0.17 * min(1, f / (FPS * 0.7))))
            for L in linhas:
                d.text((W / 2, y), L, font=fnt, fill=GRADE["sujeito"] + (op,), anchor="mt")
                y += alt
            cam = cam.filter(ImageFilter.GaussianBlur(1.5))
            im = Image.alpha_composite(im, cam)
        passo = (self.dur * 0.78) / max(1, len(novas))
        cam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(cam)
        itens = []
        for i, w in enumerate(lista):
            nova = i >= len(self.acumulado)
            entra = (i - len(self.acumulado)) * passo if nova else 0
            if f < entra:
                continue
            m = mola((f - entra) / (FPS * 0.5)) if nova else 1.0
            recuo = max(0, len(lista) - 1 - i)
            corpo = (92 - min(recuo, 6) * (40 / 6)) * s
            if acender and nova:
                corpo *= 1.9
            op = 1 - min(recuo, 6) * (0.66 / 6)
            itens.append((w, corpo, op * min(1, m), 1.35 - 0.35 * min(1, m), acender and nova))
        # layout: uma linha que quebra, centrada
        x_tot, alt_max = 0, 0
        medidas = []
        for w, corpo, op, esc, ace in itens:
            fnt = fonte("impacto", max(8, int(corpo)), r)
            lw = d.textlength(w, font=fnt)
            medidas.append((lw, fnt))
        gap = 30 * s
        linhas, atual, larg = [], [], 0
        for k, (w, corpo, op, esc, ace) in enumerate(itens):
            lw = medidas[k][0]
            if atual and larg + gap + lw > W * 0.84:
                linhas.append(atual)
                atual, larg = [], 0
            atual.append(k)
            larg += (gap if larg else 0) + lw
        if atual:
            linhas.append(atual)
        alt_lin = 100 * s
        y = H * 0.46 - alt_lin * len(linhas) / 2
        for lin in linhas:
            larg = sum(medidas[k][0] for k in lin) + gap * (len(lin) - 1)
            x = W / 2 - larg / 2
            for k in lin:
                w, corpo, op, esc, ace = itens[k]
                lw, fnt = medidas[k]
                cor = GRADE["quente"] if ace else GRADE["texto"]
                d.text((x + lw / 2, y), w, font=fnt, fill=cor + (int(255 * op),), anchor="mm")
                x += lw + gap
            y += alt_lin
        if any(it[4] for it in itens):
            cam = brilho(cam, GRADE["quente"], 40, 0.9)
        return Image.alpha_composite(im, cam)

    # -- tela --------------------------------------------------------------
    def _janela(self, titulo, conteudo):
        W, H, r = self.W, self.H, self.raiz
        s = W / 1080
        im = self.fundo()
        jw = int(W * 0.88)
        jh = min(int(H * 0.7), conteudo.height + int(84 * s) + int(86 * s))
        x0, y0 = (W - jw) // 2, (H - jh) // 2
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([x0, y0, x0 + jw, y0 + jh], radius=int(26 * s), fill=GRADE["painel"] + (255,),
                            outline=GRADE["sujeito"] + (51,), width=2)
        d.rounded_rectangle([x0, y0, x0 + jw, y0 + int(84 * s)], radius=int(26 * s), fill=GRADE["cromo"] + (255,))
        d.rectangle([x0, y0 + int(50 * s), x0 + jw, y0 + int(84 * s)], fill=GRADE["cromo"] + (255,))
        for i, c in enumerate(("alerta", "ambar", "frio")):
            cx = x0 + int(30 * s) + i * int(32 * s)
            d.ellipse([cx, y0 + int(33 * s), cx + int(18 * s), y0 + int(51 * s)], fill=GRADE[c] + (170,))
        d.text((x0 + int(130 * s), y0 + int(42 * s)), titulo, font=fonte("mono", int(26 * s), r),
               fill=GRADE["sujeito"] + (153,), anchor="lm")
        im.alpha_composite(conteudo, (x0 + int(38 * s), y0 + int(84 * s) + int(40 * s)))
        d.text((W / 2, y0 + jh + int(60 * s)), "interface desenhada · não é captura de um app real",
               font=fonte("mono", int(22 * s), r), fill=GRADE["sujeito"] + (100,), anchor="mm")
        return im

    def c_tela(self, f):
        W, H, r = self.W, self.H, self.raiz
        s = W / 1080
        t = self.p.get("tela") or {}
        modo = t.get("modo") or ("chat" if self.p.get("conversa") else "terminal")
        cw = int(W * 0.88) - int(76 * s)
        if modo == "chat":
            msgs = t.get("mensagens") or [{"lado": m["lado"], "texto": "· · ·"} for m in (self.p.get("conversa") or [])]
            passo = (self.dur * 0.55) / max(1, len(msgs))
            some = 1 - 0.94 * max(0, min(1, (f - self.dur * 0.4) / (self.dur * 0.45)))
            a, b = math.floor(len(msgs) * 0.3), math.ceil(len(msgs) * 0.72)
            fnt = fonte("mono", int(34 * s), r)
            cam = Image.new("RGBA", (cw, int(H * 0.6)), (0, 0, 0, 0))
            d = ImageDraw.Draw(cam)
            y = 0
            for i, m in enumerate(msgs):
                if f < i * passo:
                    break
                e = min(1, (f - i * passo) / 6)
                linhas = quebrar(m["texto"], fnt, cw * 0.78 - 56 * s, d)
                bw = max(d.textlength(L, font=fnt) for L in linhas) + 56 * s
                bh = len(linhas) * 46 * s + 44 * s
                x = cw - bw if m.get("lado") == "dir" else 0
                meio = t.get("apagarMeio") and a <= i < b
                op = int(255 * e * (some if meio else 1))
                cor = (127, 180, 255, int(46 * e * (some if meio else 1))) if m.get("lado") == "dir" else (52, 57, 67, op)
                d.rounded_rectangle([x, y, x + bw, y + bh], radius=int(22 * s), fill=cor,
                                    outline=GRADE["sujeito"] + (int(42 * e),), width=1)
                yy = y + 22 * s
                for L in linhas:
                    d.text((x + 28 * s, yy), L, font=fnt, fill=GRADE["sujeito"] + (op,))
                    yy += 46 * s
                y += bh + 22 * s
                if y > cam.height - 60 * s:
                    break
            cam = cam.crop((0, 0, cw, min(cam.height, int(y))))
            return self._janela(t.get("titulo") or "conversa", cam)
        if modo == "pagina":
            # a pagina que ainda nao existe, se montando bloco a bloco. Esqueleto,
            # nao maquete: quem assiste tem de ver a ESTRUTURA nascer, e nao ler
            # uma pagina inteira em quatro segundos.
            paginas = t.get("paginas") or [{"nome": t.get("titulo") or "pagina",
                                            "blocos": t.get("blocos") or []}]
            fatia = self.dur / max(1, len(paginas))
            i_pag = min(len(paginas) - 1, int(f / max(1, fatia)))
            pag = paginas[i_pag]
            blocos = pag.get("blocos") or []
            fl = f - i_pag * fatia
            passo = (fatia * 0.66) / max(1, len(blocos))
            fnt = fonte("mono", int(30 * s), r)
            cam = Image.new("RGBA", (cw, int(H * 0.6)), (0, 0, 0, 0))
            d = ImageDraw.Draw(cam)
            y = 0
            for j, rot in enumerate(blocos):
                if fl < j * passo:
                    break
                e = min(1, (fl - j * passo) / 8)
                botao = j == len(blocos) - 1
                bh = int((132 if j == 0 else 74) * s)
                bw = int(cw * (0.46 if botao else 1.0))
                x = (cw - bw) // 2 if botao else 0
                dy = int((1 - e) * 22 * s)
                if botao:
                    d.rounded_rectangle([x, y + dy, x + bw, y + dy + bh], radius=int(16 * s),
                                        fill=GRADE["ambar"] + (int(225 * e),))
                    cor_txt = GRADE["painel"] + (int(255 * e),)
                else:
                    d.rounded_rectangle([x, y + dy, x + bw, y + dy + bh], radius=int(14 * s),
                                        fill=GRADE["cromo"] + (int(200 * e),),
                                        outline=GRADE["sujeito"] + (int(56 * e),), width=1)
                    cor_txt = GRADE["sujeito"] + (int(150 * e),)
                d.text((x + bw / 2, y + dy + bh / 2), str(rot), font=fnt, fill=cor_txt, anchor="mm")
                y += bh + int(20 * s)
                if y > cam.height - 60 * s:
                    break
            cam = cam.crop((0, 0, cw, max(int(80 * s), min(cam.height, int(y)))))
            nome = pag.get("nome") or ""
            titulo = t.get("titulo") or "pagina"
            return self._janela(f"{titulo} · {nome}" if nome else titulo, cam)
        # terminal
        prefixo, comando = t.get("prefixo") or "", t.get("comando") or ""
        linhas = t.get("linhas") or []
        fim_cmd = self.dur * (0.38 if linhas else 0.7)
        cursor = int(min(1, f / max(1, fim_cmd)) * len(comando))
        digitando = cursor < len(comando)
        fnt = fonte("mono", int(42 * s), r)
        fnt2 = fonte("mono", int(36 * s), r)
        cam = Image.new("RGBA", (cw, int(H * 0.6)), (0, 0, 0, 0))
        d = ImageDraw.Draw(cam)
        texto = prefixo + comando[:cursor]
        y = 0
        lin = quebrar("> " + texto, fnt, cw, d) or ["> "]
        for k, L in enumerate(lin):
            d.text((0, y), L, font=fnt, fill=GRADE["sujeito"] + (255,))
            if k == len(lin) - 1 and (digitando or not linhas) and (f % 30) < 15:
                d.text((d.textlength(L, font=fnt) + 6 * s, y), "▌", font=fnt, fill=GRADE["ambar"] + (255,))
            y += 60 * s
        passo = (self.dur * 0.45) / max(1, len(linhas))
        destaque = t.get("destaque")
        y += 20 * s
        for i, L in enumerate(linhas):
            nasce = fim_cmd + i * passo
            if f < nasce:
                break
            e = min(1, (f - nasce) / 8)
            for sub in quebrar(L, fnt2, cw, d):
                x = 8 * s
                if destaque and destaque in sub:
                    antes, depois = sub.split(destaque, 1)
                    d.text((x, y + (1 - e) * 16), antes, font=fnt2, fill=GRADE["sujeito"] + (int(208 * e),))
                    x += d.textlength(antes, font=fnt2)
                    d.text((x, y + (1 - e) * 16), destaque, font=fnt2, fill=GRADE["quente"] + (int(255 * e),))
                    x += d.textlength(destaque, font=fnt2)
                    d.text((x, y + (1 - e) * 16), depois, font=fnt2, fill=GRADE["sujeito"] + (int(208 * e),))
                else:
                    d.text((x, y + (1 - e) * 16), sub, font=fnt2, fill=GRADE["sujeito"] + (int(208 * e),))
                y += 50 * s
        cam = cam.crop((0, 0, cw, max(int(80 * s), min(cam.height, int(y)))))
        return self._janela(t.get("titulo") or "entrada", cam)

    # -- paper / retrato / cartela ----------------------------------------
    def _ficha(self, f, titulo, linhas, rodape, cor):
        W, H, r = self.W, self.H, self.raiz
        s = W / 1080
        im = self.fundo()
        cam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(cam)
        e = ease_out(f / 12)
        cw = int(W * 0.84)
        x0 = (W - cw) // 2
        ft = fonte("serifa", int(56 * s), r)
        lt = quebrar(titulo, ft, cw - 80 * s, d)
        alt = len(lt) * 66 * s + 60 * s + len(linhas) * 44 * s + (60 * s if rodape else 0) + 60 * s
        y0 = int(H / 2 - alt / 2 + (1 - e) * 40 * s)
        d.rounded_rectangle([x0, y0, x0 + cw, y0 + alt], radius=int(18 * s), fill=(20, 20, 22, int(255 * e)),
                            outline=cor + (int(160 * e),), width=3)
        d.rectangle([x0, y0, x0 + 10 * s, y0 + alt], fill=cor + (int(255 * e),))
        y = y0 + 40 * s
        for L in lt:
            d.text((x0 + 40 * s, y), L, font=ft, fill=GRADE["texto"] + (int(255 * e),))
            y += 66 * s
        y += 14 * s
        fl = fonte("leitura", int(30 * s), r)
        for L in linhas:
            for sub in quebrar(L, fl, cw - 80 * s, d):
                d.text((x0 + 40 * s, y), sub, font=fl, fill=GRADE["sujeito"] + (int(230 * e),))
                y += 44 * s
        if rodape:
            y += 16 * s
            d.text((x0 + 40 * s, y), rodape, font=fonte("mono", int(24 * s), r), fill=cor + (int(230 * e),))
        return Image.alpha_composite(im, cam)

    def c_paper(self, f):
        p = self.p.get("paper") or {}
        linhas = [x for x in (p.get("autores"), f"{p.get('publicacao', '')} · {p.get('ano', '')}".strip(" ·"))
                  if x]
        if p.get("citacao"):
            linhas.append("“" + p["citacao"] + "”")
        rod = f"DOI {p['doi']}" if p.get("doi") else (p.get("url") or "")
        if p.get("verificado") is False:
            rod = (rod + "  · não verificado").strip(" ·")
        return self._ficha(f, p.get("titulo") or self.p.get("texto", ""), linhas, rod, GRADE["frio"])

    def c_retrato(self, f):
        r = self.p.get("retrato") or {}
        linhas = [x for x in (r.get("anos"), r.get("instituicao")) if x]
        return self._ficha(f, r.get("nome") or self.p.get("texto", ""), linhas,
                           "sem imagem de licença livre — ficha tipográfica", GRADE["ambar"])

    def c_cartela(self, f):
        W, H, r = self.W, self.H, self.raiz
        s = W / 1080
        im = self.fundo()
        cam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(cam)
        fnt = fonte("impacto", int(84 * s), r)
        lin = quebrar(self.p.get("texto") or "", fnt, W * 0.84, d)
        e = ease_out(f / 10)
        y = H * 0.46 - len(lin) * 96 * s / 2
        for L in lin:
            d.text((W / 2, y), L, font=fnt, fill=GRADE["texto"] + (int(255 * e),), anchor="mt")
            y += 96 * s
        return Image.alpha_composite(im, cam)

    # -- dado --------------------------------------------------------------
    def c_dado(self, f):
        W, H, r = self.W, self.H, self.raiz
        s = W / 1080
        im = self.fundo()
        cam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(cam)
        x0, x1 = W * 0.12, W * 0.88
        y0, y1 = H * 0.30, H * 0.62
        prog = ease_out(f / (self.dur * 0.6))
        curva, serie = self.p.get("curva"), self.p.get("serie")
        fl = fonte("leitura", int(28 * s), r)
        d.line([(x0, y1), (x1, y1)], fill=GRADE["sujeito"] + (120,), width=2)
        if curva:
            n = len(curva)
            pts = [(x0 + (x1 - x0) * i / (n - 1), y1 - (y1 - y0) * v) for i, v in enumerate(curva)]
            k = max(2, int(prog * n))
            seg = pts[:k]
            if len(seg) >= 2:
                # area sob a curva, leve: e o "quanto ficou" que se le, nao so a linha
                d.polygon(seg + [(seg[-1][0], y1), (seg[0][0], y1)], fill=GRADE["quente"] + (34,))
                d.line(seg, fill=GRADE["quente"] + (255,), width=int(14 * s), joint="curve")
                cx, cy = seg[-1]
                d.ellipse([cx - 18 * s, cy - 18 * s, cx + 18 * s, cy + 18 * s], fill=GRADE["texto"] + (255,))
            for x, rot in ((x0, "início"), ((x0 + x1) / 2, "meio"), (x1, "fim")):
                d.text((x, y1 + 20 * s), rot, font=fl, fill=GRADE["sujeito"] + (200,), anchor="mt")
        elif serie:
            n = len(serie)
            bw = (x1 - x0) / n * 0.62
            vmax = max(1e-9, max(float(x["valor"]) for x in serie))
            for i, item in enumerate(serie):
                cx = x0 + (x1 - x0) * (i + 0.5) / n
                h = (y1 - y0) * float(item["valor"]) / vmax * prog
                d.rounded_rectangle([cx - bw / 2, y1 - h, cx + bw / 2, y1], radius=int(10 * s),
                                    fill=(GRADE["quente"] if i == 0 else GRADE["frio"]) + (230,))
                for sub in quebrar(str(item["rotulo"]), fl, bw * 1.5, d)[:2]:
                    d.text((cx, y1 + 20 * s), sub, font=fl, fill=GRADE["sujeito"] + (200,), anchor="mt")
                    y1_ = y1
                d.text((cx, y1 - h - 16 * s), f"{item['valor']:g}", font=fonte("impacto", int(34 * s), r),
                       fill=GRADE["texto"] + (int(255 * prog),), anchor="mb")
        cam = brilho(cam, GRADE["quente"], 30, 0.35)
        im = Image.alpha_composite(im, cam)
        d = ImageDraw.Draw(im)
        if self.p.get("texto"):
            d.text((W / 2, H * 0.22), self.p["texto"], font=fonte("impacto", int(52 * s), r),
                   fill=GRADE["texto"] + (255,), anchor="mm")
        if self.p.get("fonte"):
            d.text((W / 2, H * 0.70), self.p["fonte"], font=fonte("mono", int(24 * s), r),
                   fill=GRADE["sujeito"] + (160,), anchor="mm")
        return im

    # -- objeto / personagem / imagem ----------------------------------------
    def c_objeto(self, f):
        W, H = self.W, self.H
        im = self.fundo()
        if self.img is None:
            return im
        # push-in de 6% na duracao (ritmo.md); pull-out quando o plano pede
        cam = self.p.get("camera") or "push-in"
        t = f / max(1, self.dur)
        esc = (1.08 - 0.08 * t) if cam == "pull-out" else (1.0 + 0.06 * t)
        # A imagem SANGRA o quadro: a cena preenche 9:16 de borda a borda, como
        # nas referencias. O gerador devolve 1:1, entao cobre-se pela maior
        # dimensao e corta-se o excesso — o assunto vem centrado. Encaixar a
        # imagem inteira deixaria faixas pretas em cima e embaixo, e a cena
        # viraria cartao flutuando.
        iw, ih = self.img.size
        k = max(W / iw, H / ih) * esc
        nw, nh = max(1, int(iw * k)), max(1, int(ih * k))
        img = self.img.resize((nw, nh), Image.LANCZOS)
        im.paste(img, ((W - nw) // 2, (H - nh) // 2))
        return im


# ---------- envelope de movimento (entrada / saida) -----------------------

def envelope(im, f, dur, entrada, saida, W, H):
    """aplica a entrada nos primeiros FRAMES_ENTRADA e a saida depois de `dur`
    (a cauda), sobre um RGBA transparente — o que esta embaixo aparece."""
    x = y = 0
    esc = 1.0
    op = 1.0
    e = ease_out(f / FRAMES_ENTRADA) if entrada != "corte" else 1.0
    s_ = ease_in((f - dur) / FRAMES_SAIDA) if f >= dur and saida != "corte" else 0.0
    if entrada == "deslizar":
        x += W * 0.35 * (1 - e)
    if entrada == "subir":
        y += H * 0.12 * (1 - e)
    if entrada == "escalar":
        esc *= 1.14 - 0.14 * e
    if entrada != "corte":
        op *= e
    if saida == "varrer":
        x += -W * 1.06 * s_
    if saida == "empurrar":
        esc *= 1 + 0.34 * s_
    if saida == "implodir":
        esc *= 1 - 0.45 * s_
    if saida in ("apagar", "implodir", "empurrar"):
        op *= 1 - s_
    if esc != 1.0:
        nw, nh = int(im.width * esc), int(im.height * esc)
        im2 = im.resize((max(1, nw), max(1, nh)), Image.BILINEAR)
        x += (im.width - nw) / 2
        y += (im.height - nh) / 2
        im = im2
    if op < 1.0:
        a = im.split()[3].point(lambda v: int(v * op))
        im.putalpha(a)
    if x or y:
        base = Image.new("RGBA", (W, H) if im.size != (W, H) else im.size, (0, 0, 0, 0))
        base.alpha_composite(im, (int(x), int(y)))
        im = base
    if im.size != (W, H):
        base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        base.alpha_composite(im, (0, 0))
        im = base
    return im


def painel(im, W, H, s):
    """aroll+motion: o grafico num painel arredondado na metade de baixo"""
    pw, ph = int(W * 0.92), int(H * 0.46)
    cena = im.resize((pw, ph), Image.LANCZOS)
    mask = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, pw, ph], radius=int(28 * s), fill=255)
    cena.putalpha(mask)
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    base.alpha_composite(cena, (int(W * 0.04), int(H * 0.50)))
    return base


# ---------- clips ---------------------------------------------------------
# Cada clip vira UM arquivo .mov com alpha (qtrle), alimentado por pipe do
# Pillow direto ao ffmpeg. Sequencia de PNG (milhares de arquivos) travava o
# ffmpeg em open(): o antivirus segura cada abertura de arquivo recem-escrito.

class Gravador:
    """recebe quadros RGBA e escreve um .mov com alpha"""

    def __init__(self, destino, W, H):
        self.destino = Path(destino)
        self.proc = subprocess.Popen(
            ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba",
             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
             "-c:v", "qtrle", "-pix_fmt", "argb", str(self.destino)],
            stdin=subprocess.PIPE)

    def quadro(self, im):
        self.proc.stdin.write(im.tobytes())

    def fechar(self):
        self.proc.stdin.close()
        if self.proc.wait() != 0:
            raise RuntimeError(f"ffmpeg falhou ao gravar {self.destino}")
        return self.destino


def renderizar_clips(plano, raiz, out, escala):
    W, H = int(plano["largura"] * escala), int(plano["altura"] * escala)
    s = W / 1080
    clips = []
    ps = plano["planos"]
    for i, p in enumerate(ps):
        if p["tipo"] == "fala":
            continue
        acum = []
        if p["tipo"] == "palavras":
            k = i - 1
            while k >= 0 and ps[k]["tipo"] == "palavras":
                acum = list(ps[k].get("palavras") or []) + acum
                k -= 1
        # aroll+motion: a cena e desenhada JA no tamanho do painel, nao
        # encolhida depois — senao a ficha vira letra de bula
        sobre = bool(p.get("sobreFala"))
        cw, ch = (int(W * 0.92), int(H * 0.46)) if sobre else (W, H)
        cena = Cena(p, raiz, cw, ch, acum)
        dur = cena.dur
        cauda = FRAMES_SAIDA if (p.get("saida") or "corte") != "corte" else 0
        (out / "clips").mkdir(parents=True, exist_ok=True)
        arquivo = out / "clips" / f"{p['id']}.mov"
        total = dur + cauda
        g = Gravador(arquivo, W, H)
        for f in range(total):
            im = cena.quadro(min(f, dur - 1))
            if sobre:
                im = painel(im, W, H, s)
            im = envelope(im, f, dur, p.get("entrada") or "corte", p.get("saida") or "corte", W, H)
            g.quadro(im.convert("RGBA"))
        g.fechar()
        clips.append({"id": p["id"], "arquivo": arquivo, "t0": p["t0"] / 1000, "frames": total})
        print(f"  {p['id']:<5} {p['tipo']:<10} {total:4d} quadros", flush=True)
    return clips, W, H


# ---------- legenda (faixa PNG) --------------------------------------------
# O ffmpeg daqui nao tem libass; a legenda segue o mesmo caminho dos clips:
# o Pillow desenha uma faixa transparente quadro a quadro e o ffmpeg sobrepoe.

def grupos_legenda(plano, captions):
    mudos = [(p["t0"], p["t1"]) for p in plano["planos"] if not p.get("legenda", True)]

    def calado(ms):
        return any(a <= ms < b for a, b in mudos)

    # frases curtas: junta ate 4 palavras ou 1,6 s
    grupos, atual = [], []
    for c in captions:
        if calado(c["startMs"]):
            if atual:
                grupos.append(atual)
                atual = []
            continue
        if atual and (len(atual) >= 4 or c["endMs"] - atual[0]["startMs"] > 1600 or
                      c["startMs"] - atual[-1]["endMs"] > 700):
            grupos.append(atual)
            atual = []
        atual.append(c)
    if atual:
        grupos.append(atual)
    return [(g[0]["startMs"], g[-1]["endMs"], " ".join(c["text"].strip() for c in g)) for g in grupos]


def faixa_legenda(plano, captions, raiz, W, H, out):
    """PNG por frame, transparente onde nao ha fala; entrada em 0,10 s com
    escala 0,92 -> 1 (ritmo.md). Devolve a pasta da sequencia."""
    s = W / 1080
    grupos = grupos_legenda(plano, captions)
    arquivo = out / "legenda.mov"
    total = round(plano["duracaoMs"] / 1000 * FPS)
    vazio = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    grav = Gravador(arquivo, W, H)
    k = 0
    cache = {}
    for f in range(total):
        ms = f * 1000 / FPS
        g = grupos[k] if k < len(grupos) else None
        while g and ms >= g[1]:
            k += 1
            g = grupos[k] if k < len(grupos) else None
        if not g or ms < g[0]:
            grav.quadro(vazio)
            continue
        e = ease_out((ms - g[0]) / 100)
        chave = (g[2], round(e, 2))
        if chave not in cache:
            im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            esc = 0.92 + 0.08 * e
            fn = fonte("leitura", max(8, int(64 * s * esc)), raiz)
            linhas = quebrar(g[2], fn, W * 0.86, d)
            y = H * 0.52 - len(linhas) * 76 * s * esc / 2
            for L in linhas:
                d.text((W / 2, y), L, font=fn, fill=(255, 255, 255, int(255 * e)), anchor="mt",
                       stroke_width=int(4 * s), stroke_fill=(0, 0, 0, int(230 * e)))
                y += 76 * s * esc
            cache[chave] = im
            if len(cache) > 64:
                cache.pop(next(iter(cache)))
        grav.quadro(cache[chave])
    return grav.fechar()


# ---------- ffmpeg --------------------------------------------------------

def sobrepor(base, clips, W, H, out, crf, passada):
    """uma passada: ate LOTE_OVERLAYS clips sobre `base`"""
    destino = out / f"_pass{passada:02d}.mp4"
    cmd = ["ffmpeg", "-y", "-nostdin", "-v", "error", "-stats", "-i", str(base)]
    fc = []
    for c in clips:
        cmd += ["-i", str(c["arquivo"])]
    ant = "[0:v]"
    for k, c in enumerate(clips):
        fc.append(f"[{k+1}:v]format=rgba,setpts=PTS+{c['t0']:.3f}/TB[c{k}]")
        fc.append(f"{ant}[c{k}]overlay=0:0:eof_action=pass:format=auto[v{k}]")
        ant = f"[v{k}]"
    cmd += ["-filter_complex", ";".join(fc), "-map", ant, "-an",
            *acabamento.encoder(crf, "veryfast", H),
            "-r", str(FPS), str(destino)]
    subprocess.run(cmd, check=True)
    return destino


def finalizar(video, plano, raiz, legenda, out_final, crf, W, H):
    voz = raiz / "public" / (plano.get("fonteAudio") or plano.get("fonteVideo"))
    trilha = raiz / "public" / plano["trilha"] if plano.get("trilha") else None
    vol = float(plano.get("trilhaVolume") or 0.5)
    dur = plano["duracaoMs"] / 1000
    # entradas: 0 video, 1 legenda (mov com alpha, quando ha), depois voz e cama
    cmd = ["ffmpeg", "-y", "-nostdin", "-v", "error", "-stats", "-i", str(video)]
    if legenda:
        # O WebM do HyperFrames guarda o alpha no canal lateral do Matroska
        # (ALPHA_MODE=1, pix_fmt yuv420p). So o decodificador `libvpx-vp9` le
        # esse canal; o decodificador nativo devolve o quadro OPACO, e a camada
        # de legenda vira uma cortina preta sobre o video inteiro. Medido: 120 s
        # de preto num preview de 125 s.
        if str(legenda).endswith(".webm"):
            cmd += ["-c:v", "libvpx-vp9"]
        cmd += ["-i", str(legenda)]
    cmd += ["-i", str(voz)]
    iv = 2 if legenda else 1          # indice da voz entre as entradas
    if trilha:
        cmd += ["-i", str(trilha)]
    # A grade da identidade, na ordem de linguagem-visual.md e com os mesmos
    # numeros do Grade.tsx: bloom (halo largo nas altas luzes, screen a 35%)
    # -> aberracao (R +2 px, B -2 px) -> vinheta -> grao -> curva (preto
    # levantado a 12/255, branco segurado, saturacao 0,8). A legenda entra por
    # cima do grao para nao perder nitidez de glifo.
    ab = max(1, round(2 * W / 1080))
    # (o bloom e calculado a 1/4 da resolucao: mesmo halo, um quarto do custo)
    identidade = (f"split[ga][gb];[gb]scale=iw/4:ih/4,gblur=sigma=7,eq=brightness=0.06:contrast=1.6,"
                  f"scale=iw*4:ih*4[gc];[ga][gc]blend=all_mode=screen:all_opacity=0.35,"
                  f"rgbashift=rh={ab}:bh=-{ab},vignette=angle=PI/4.6,noise=alls=8:allf=t,"
                  f"lutrgb=r='0.874*val+12':g='0.874*val+12':b='0.874*val+12',eq=saturation=0.8")
    # A grade sobria e o PADRAO. A de identidade acima tinge: o `rgbashift`
    # separa o vermelho do azul em torno da pele e o bloom em `screen` levanta
    # as altas por cima — junto, isso deixa um rosto com luz de janela rosado.
    # Recusado pelo dono do canal com estas palavras: "deixou tudo rosa".
    # Aqui nao se mexe em cor nenhuma: uma curva igual nos tres canais, que
    # escurece a sombra e abre um fio de contraste. Sem matiz, sem saturacao,
    # sem vinheta, sem grao. A nitidez mora no `acabamento.py`, aplicada na
    # resolucao cheia, que e onde ela custa menos halo.
    sobria = "curves=all='0/0 0.12/0.082 0.5/0.5 0.88/0.895 1/1'"
    grade = identidade if plano.get("gradeIdentidade") else sobria
    if plano.get("semGrade"):
        grade = "null"
    # A legenda pode chegar menor que o quadro: num master 4K ela e desenhada em
    # Full HD de proposito — tipografia ampliada 2x nao perde nada visivel e o
    # render em 4K pedia ~124 GB de quadros temporarios. `scale` a encaixa; sem
    # ele o `overlay` a plantaria num canto, do tamanho de um selo.
    vf = (f"[0:v]{grade}[g];[1:v]scale={W}:{H}:flags=lanczos,format=rgba[leg];"
          f"[g][leg]overlay=0:0:eof_action=pass:format=auto[v]") \
        if legenda else f"[0:v]{grade}[v]"
    # O ultimo quadro do master e corte duro por definicao — nao ha emenda
    # depois dele. Se a fala termina colada no fim (e termina, quando a frase
    # final nao tem pausa depois), o corte seco decepa a consoante. 80 ms de
    # fade resolvem isso sem que ninguem perceba um fade; sem eles, percebe-se
    # o corte. Vale para a voz sempre, com ou sem trilha.
    fim = f"afade=t=out:st={max(0, dur - 0.08):.3f}:d=0.08"
    af = (f"[{iv+1}:a]volume={vol},afade=t=in:d=1,afade=t=out:st={max(0, dur-2):.2f}:d=2[m];"
          f"[{iv}:a]{fim}[v0];{acabamento.mistura_voz_cama('[v0]', '[m]')}"
          ) if trilha else f"[{iv}:a]{fim}[a]"
    cmd += ["-filter_complex", f"{vf};{af}", "-map", "[v]", "-map", "[a]", "-t", f"{dur:.3f}",
            *acabamento.encoder(crf, "medium", H),
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out_final)]
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projeto", required=True)
    ap.add_argument("--out")
    ap.add_argument("--escala", type=float, default=1.0)
    ap.add_argument("--crf", type=int, default=18)
    ap.add_argument("--so-clips", action="store_true")
    ap.add_argument("--base", help="vídeo já montado (caminho HyperFrames): pula a "
                                   "composição em Pillow e só aplica legenda, som e grade")
    ap.add_argument("--so-final", action="store_true",
                    help="pula clips e sobreposicoes; usa a ultima passada em out/")
    a = ap.parse_args()
    raiz = Path(a.projeto)
    plano = json.loads((raiz / "plano.json").read_text(encoding="utf-8"))
    captions = json.loads((raiz / "public" / "captions.json").read_text(encoding="utf-8"))
    out = raiz / "out"
    out.mkdir(exist_ok=True)
    final = Path(a.out) if a.out else out / "master.mp4"

    W, H = int(plano["largura"] * a.escala), int(plano["altura"] * a.escala)
    if a.base:
        # O caminho HyperFrames ja entregou o quadro pronto, em 1080x1920, com
        # o desenho de cada tipo de cena. O que falta e legenda, som e grade —
        # e era exatamente isso que este script refazia POR CIMA, redesenhando
        # tudo em Pillow a 0,3x. Como ele nao tem desenho para `camadas` nem
        # `indice`, essas cenas voltavam pretas: 18,6 s de preto num master de
        # 67,6 s, medido com `blackdetect` em 2026-09-12.
        base = Path(a.base)
        if not base.exists():
            sys.exit(f"--base nao existe: {base}")
        W, H = plano["largura"], plano["altura"]
        print(f"base: usando o master já montado ({base.name}, {W}x{H})", flush=True)
    elif a.so_final:
        passadas = sorted(out.glob("_pass*.mp4"))
        if not passadas:
            sys.exit("nenhuma passada em out/ para retomar")
        base = passadas[-1]
    else:
        print("clips:")
        clips, W, H = renderizar_clips(plano, raiz, out, a.escala)
        if a.so_clips:
            return
        fonte_v = raiz / "public" / plano["fonteVideo"]
        base = fonte_v
        if a.escala != 1.0:
            base = out / "_base.mp4"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(fonte_v), "-vf", f"scale={W}:{H}", "-an",
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", str(base)], check=True)
        for k in range(0, len(clips), LOTE_OVERLAYS):
            lote = clips[k:k + LOTE_OVERLAYS]
            print(f"sobrepondo {lote[0]['id']}…{lote[-1]['id']}", flush=True)
            base = sobrepor(base, lote, W, H, out, max(14, a.crf - 4), k // LOTE_OVERLAYS)
    if plano.get("semLegenda"):
        # etapa `motion`: o editor julga o desenho, nao a leitura. O GANCHO e a
        # excecao — ele nao e leitura, e a abertura, e sem ele o editor aprova
        # o motion sem nunca ter visto os primeiros segundos do video.
        gancho = out / "hook.webm"
        if gancho.exists():
            print(f"hook: sobrepondo o gancho da abertura ({gancho.name})", flush=True)
            legenda = gancho
        else:
            print("legenda: pulada (semLegenda no plano)", flush=True)
            legenda = None
    else:
        pronta = out / "legenda.webm"
        if pronta.exists():
            # camada vinda do `legenda_hf.py`: tipografia de verdade, com alpha
            print(f"legenda: usando a camada pronta ({pronta.name})", flush=True)
            legenda = pronta
        else:
            print("legenda: desenhando a faixa", flush=True)
            legenda = faixa_legenda(plano, captions, raiz, W, H, out)
    print("finalizando: legenda, voz, cama, grade", flush=True)
    finalizar(base, plano, raiz, legenda, final, a.crf, W, H)
    for f in out.glob("_pass*.mp4"):
        f.unlink()
    shutil.rmtree(out / "clips", ignore_errors=True)
    (out / "legenda.mov").unlink(missing_ok=True)
    print(f"pronto: {final}")


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
