#!/usr/bin/env python3
"""
contato.py — transforma o take em material que um diretor le.

O diretor e um agente: le texto e imagem, nao assiste vídeo nem ouve audio.
Entao o take vira (1) frases com quatro numeros medidos — ritmo, voz, imagem,
pausa — e (2) folhas de contato do recorte 9:16, com timestamp gravado em
cada quadro. "A entrega cai" deixa de ser impressao: e frase com ritmo lento,
voz abaixo da media e imagem parada, e o diretor ve isso no mesmo lugar em
que ve o rosto.

Uso: contato.py --take take.mov --falas take.whisper.json [--roteiro r.md]
                [--branding auto|none] [--deslocamento 0] --out guia/
"""
import argparse, difflib, json, math, re, shutil, subprocess, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import escutar, tempo  # noqa: E402

COLS, LINHAS = 4, 3                 # 12 quadros por folha
QW, QH = 270, 480                   # quadro 9:16 na folha (folha = 1080 px de largura)
IMG_FPS, IMG_W, IMG_H = 5, 54, 96   # amostragem para medir movimento
SR = 16000                          # amostragem para medir voz


def sonda(take):
    """(largura, altura, duracaoMs) COMO O FFMPEG DECODIFICA. Celular grava
    deitado com rotacao nos metadados: o container diz 3840x2160, o quadro
    decodificado e 2160x3840. Recortar pelo numero do container pega o pedaco
    errado da imagem — foi assim que a primeira folha saiu com o rosto cortado."""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=width,height:stream_tags=rotate:"
                        "stream_side_data=rotation:format=duration",
                        "-of", "json", str(take)], capture_output=True, text=True, check=True, encoding="utf-8", errors="replace")
    d = json.loads(r.stdout)
    s = d["streams"][0]
    w, h = int(s["width"]), int(s["height"])
    rot = 0
    for sd in s.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = int(float(sd["rotation"]))
    if not rot and (s.get("tags") or {}).get("rotate"):
        rot = int(float(s["tags"]["rotate"]))
    if abs(rot) % 180 == 90:
        w, h = h, w
    return w, h, int(round(float(d["format"]["duration"]) * 1000))


def _pcm(take):
    """audio mono 16 kHz como float32 -1..1, de uma passada so"""
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(take), "-vn", "-ac", "1",
                        "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype=np.int16).astype(np.float32) / 32768.0


def medir_voz(take, frases):
    """RMS de cada frase em % da media das frases. Media das frases, nao do
    take: silencio entre frases nao e 'voz baixa', e nao pode puxar a media."""
    pcm = _pcm(take)
    rms = []
    for f in frases:
        a, b = int(f["deMs"] * SR / 1000), int(f["ateMs"] * SR / 1000)
        trecho = pcm[a:b]
        rms.append(float(np.sqrt(np.mean(trecho ** 2))) if len(trecho) else 0.0)
    # a media inclui as frases mudas: uma frase sem voz E voz abaixo da media
    media = float(np.mean(rms)) if rms and np.mean(rms) > 0 else 1.0
    return [round(100.0 * x / media, 1) for x in rms]


def medir_imagem(take, frases, recorte):
    """movimento no recorte 9:16: media da diferenca absoluta entre frames
    consecutivos, em % da media das frases. Mao e cabeca em movimento marcam
    alto; leitura parada marca baixo. Frames minusculos bastam: e energia de
    movimento, nao detalhe."""
    w, h, x, y = recorte
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(take),
                        "-vf", f"crop={w}:{h}:{x}:{y},scale={IMG_W}:{IMG_H},format=gray",
                        "-r", str(IMG_FPS), "-f", "rawvideo", "-"],
                       capture_output=True, check=True)
    frames = np.frombuffer(r.stdout, dtype=np.uint8)
    n = len(frames) // (IMG_W * IMG_H)
    frames = frames[: n * IMG_W * IMG_H].reshape(n, IMG_H, IMG_W).astype(np.float32)
    dif = np.abs(np.diff(frames, axis=0)).mean(axis=(1, 2)) if n > 1 else np.zeros(0)
    vals = []
    for f in frases:
        a, b = int(f["deMs"] * IMG_FPS / 1000), max(int(f["ateMs"] * IMG_FPS / 1000), 1)
        trecho = dif[a:b]
        vals.append(float(trecho.mean()) if len(trecho) else 0.0)
    media = float(np.mean(vals)) if vals and np.mean(vals) > 0 else 1.0
    return [round(100.0 * v / media, 1) for v in vals]


def _norm(t):
    return re.sub(r"[^\w\s]", "", t.lower()).strip()


def alinhar_roteiro(frases, texto_roteiro, limiar=0.6):
    """para cada frase, a linha do roteiro mais parecida (difflib), ou None se
    nada passa do limiar — o que marca improviso ou paragrafo pulado"""
    linhas = [l.strip() for l in texto_roteiro.splitlines() if l.strip()]
    saida = []
    for f in frases:
        alvo = _norm(f["texto"])
        melhor, nota = None, 0.0
        for l in linhas:
            r = difflib.SequenceMatcher(None, alvo, _norm(l)).ratio()
            if r > nota:
                melhor, nota = l, r
        saida.append(melhor if nota >= limiar else None)
    return saida


def quadros_de(frases, passo_ms=6000):
    """um quadro no meio de cada frase, mais um a cada `passo_ms` dentro das
    frases longas — para nao perder um gesto entre dois pontos.

    O passo era 3000. O quadro do MEIO de cada frase continua sempre saindo —
    ele e a ancora semantica, e e o que o diretor cita ao justificar o corte. O
    que dobrou foi so o intervalo dos EXTRAS dentro de frase longa.

    Medido numa distribuicao de fala corrida (maioria de frases curtas, algumas
    longas): corta **11% a 14%** dos quadros, nao metade. A conta e essa porque
    a maioria das frases dura menos de 6 s e ja so recebia o quadro do meio —
    quem dita o numero de quadros e a quantidade de FRASES, nao o passo. Dobrar
    o passo de novo devolveria quase nada, e comecaria a cegar a frase longa.

    Se for preciso cortar mais, a alavanca e o TAMANHO do quadro, nao a
    quantidade: o custo de imagem e por area (ceil(larg/28) x ceil(alt/28)), e
    quadro 36% menor vale ~37% de token. O preco disso e a tarja do rotulo, que
    a 216 px nao cabe mais o timestamp com as primeiras palavras — e e por ele
    que o diretor liga o quadro a frase. Nao mude sem decidir isso.
    """
    q = []
    for i, f in enumerate(frases):
        meio = (f["deMs"] + f["ateMs"]) // 2
        q.append({"frase": i, "ms": meio})
        # extras a cada passo, pelo menos 0,9 s antes do fim e longe do meio
        t = f["deMs"] + passo_ms
        while t < f["ateMs"] - 900:
            if abs(t - meio) >= passo_ms // 3:
                q.append({"frase": i, "ms": t})
            t += passo_ms
    q.sort(key=lambda x: (x["frase"], x["ms"]))
    return q


def _quadro(take, ms, recorte, destino):
    w, h, x, y = recorte
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ms/1000:.3f}", "-i", str(take),
                    "-frames:v", "1", "-vf", f"crop={w}:{h}:{x}:{y},scale={QW}:{QH}",
                    str(destino)], check=True)


FONTES = [
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def _fonte(tamanho):
    """uma fonte do sistema com acento — a padrao do Pillow desenha caixa no
    lugar de 'ã', e o rotulo do quadro fica ilegivel"""
    for f in FONTES:
        if Path(f).is_file():
            try:
                return ImageFont.truetype(f, tamanho)
            except OSError:
                continue
    try:
        return ImageFont.load_default(size=tamanho)
    except TypeError:  # Pillow < 10
        return ImageFont.load_default()


def folhas(take, quadros, frases, recorte, out):
    """grade COLSxLINHAS de quadros, timestamp e primeiras palavras gravados
    em cada um; devolve o indice quadro -> folha/posicao"""
    fonte = _fonte(16)
    tmp = out / "_q"
    tmp.mkdir(exist_ok=True)
    indice = []
    por_folha = COLS * LINHAS
    for n in range(0, len(quadros), por_folha):
        lote = quadros[n:n + por_folha]
        folha = Image.new("RGB", (COLS * QW, LINHAS * QH), (12, 12, 12))
        d = ImageDraw.Draw(folha)
        for k, q in enumerate(lote):
            arq = tmp / f"{n + k:04d}.jpg"
            _quadro(take, q["ms"], recorte, arq)
            im = Image.open(arq)
            cx, cy = (k % COLS) * QW, (k // COLS) * QH
            folha.paste(im, (cx, cy))
            rotulo = f"#{n + k:03d} {tempo.ts(q['ms'])}  " + \
                     " ".join(frases[q["frase"]]["texto"].split()[:4])
            d.rectangle([cx, cy + QH - 26, cx + QW, cy + QH], fill=(0, 0, 0))
            d.text((cx + 6, cy + QH - 22), rotulo[:38], fill=(240, 240, 240), font=fonte)
            indice.append({"quadro": n + k, "folha": n // por_folha + 1, "posicao": k,
                           "ms": q["ms"], "frase": q["frase"]})
        folha.save(out / f"contato-{n // por_folha + 1:02d}.jpg", quality=88)
    shutil.rmtree(tmp, ignore_errors=True)
    return indice


def escrever_fala(frases, voz, imagem, roteiro_alinhado, out, escuta=None):
    linhas = ["# fala — frases do take, com medidas", "",
              "ritmo = palavras/s · voz e imagem em % da media do take · pausas em ms", ""]
    # A escuta vem ANTES das frases de propósito: é o que o transcript não
    # conta, e um diretor que leia só o texto decide sem saber que existe.
    if escuta:
        linhas += [escutar.em_markdown(escuta), ""]
    for i, f in enumerate(frases):
        if i and f["pausaAntesMs"] > 900:
            de = frases[i - 1]["ateMs"]
            linhas.append(f"[{tempo.ts(de)} → {tempo.ts(f['deMs'])}] — pausa "
                          + f"{f['pausaAntesMs']/1000:.1f} s".replace(".", ","))
        dur = max(0.001, (f["ateMs"] - f["deMs"]) / 1000)
        ritmo = len(f["palavras"]) / dur
        rot = roteiro_alinhado[i] if roteiro_alinhado else None
        marca = f"  ≈ roteiro: {rot}" if rot else ("  (improviso)" if roteiro_alinhado else "")
        linhas.append(f"[{tempo.ts(f['deMs'])} → {tempo.ts(f['ateMs'])}] F{i:03d} {f['texto']}")
        linhas.append(f"    ritmo {ritmo:.1f} · voz {voz[i]:.0f}% · imagem {imagem[i]:.0f}% · "
                      f"pausaAntes {f['pausaAntesMs']} · pausaDepois {f['pausaDepoisMs']}{marca}")
    (out / "fala.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")


def escrever_branding(modo, out):
    """O branding.md do projeto vem da marca DESTE projeto (marca.py): a marca é
    de quem edita — uma por canal ou cliente — e não viaja com o plugin."""
    mc = None
    if modo == "auto":
        import marca
        mc = marca.resolver(projeto=Path(out).resolve().parent)
    if mc and (mc.manual.is_file() or mc.motion.is_file()):
        partes = [f"# branding — marca «{mc.nome}» ({mc.pasta})\n"]
        for arq in (mc.manual, mc.motion):
            if arq.is_file():
                partes.append(arq.read_text(encoding="utf-8"))
        texto = "\n\n".join(partes)
    else:
        texto = ("# branding\n\nSem manual de marca disponivel: o vocabulario visual e o "
                 "preset `noturno` da skill (fundo #0C0C0C, sujeito #CCCAC8, quente #FFB067, "
                 "frio #7FB4FF, ambar #FFA33A; Archivo Black para impacto, Inter para leitura, "
                 "IBM Plex Mono para interface).\n")
    (out / "branding.md").write_text(texto, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--take", required=True)
    ap.add_argument("--falas", required=True)
    ap.add_argument("--roteiro")
    ap.add_argument("--branding", default="auto", choices=["auto", "none"])
    ap.add_argument("--deslocamento", type=int, default=0)
    # o quadro do meio de cada frase sai sempre; isto e so o intervalo dos
    # extras dentro de frase longa. Baixar para 3000 dobra os quadros e a conta.
    ap.add_argument("--passo", type=int, default=6000,
                    help="ms entre quadros extras dentro de frase longa")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    take, out = Path(a.take), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    largura, altura, take_ms = sonda(take)
    recorte = tempo.recorte_9x16(largura, altura, a.deslocamento)

    fr = tempo.frases(tempo.carregar_palavras(a.falas))
    voz = medir_voz(take, fr)
    imagem = medir_imagem(take, fr, recorte)
    alinhado = alinhar_roteiro(fr, Path(a.roteiro).read_text(encoding="utf-8")) if a.roteiro else None
    try:
        escuta = escutar.escutar(take, a.falas)
    except Exception as erro:   # escuta e diagnostico: falhar aqui nao para a etapa
        print(f"  · aviso: nao consegui escutar o take ({erro})")
        escuta = []
    escrever_fala(fr, voz, imagem, alinhado, out, escuta)
    (out / "escuta.json").write_text(json.dumps(escuta, ensure_ascii=False, indent=2),
                                     encoding="utf-8")

    quadros = quadros_de(fr, a.passo)
    indice = folhas(take, quadros, fr, recorte, out)
    (out / "contato.json").write_text(json.dumps({
        "take": str(take), "takeMs": take_ms, "recorte": recorte,
        "frases": [{"id": f"F{i:03d}", "deMs": f["deMs"], "ateMs": f["ateMs"], "texto": f["texto"],
                    "pausaAntesMs": f["pausaAntesMs"], "pausaDepoisMs": f["pausaDepoisMs"],
                    "voz": voz[i], "imagem": imagem[i],
                    "roteiro": alinhado[i] if alinhado else None} for i, f in enumerate(fr)],
        "quadros": indice,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    escrever_branding(a.branding, out)
    n_folhas = (len(quadros) + COLS * LINHAS - 1) // (COLS * LINHAS)
    # O custo de imagem sai de ceil(largura/28) x ceil(altura/28) por folha. Sem
    # o numero na tela, ninguem percebe quando um take longo dobra a conta — e
    # esta etapa ja foi a mais cara da producao por exatamente isso.
    tokens = n_folhas * math.ceil(COLS * QW / 28) * math.ceil(LINHAS * QH / 28)
    print(f"{len(fr)} frases · {len(quadros)} quadros em {n_folhas} folha(s) "
          f"· ~{tokens // 1000}k tokens de imagem · {out}")


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
