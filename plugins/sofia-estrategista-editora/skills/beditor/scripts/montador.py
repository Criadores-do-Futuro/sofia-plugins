#!/usr/bin/env python3
"""
montador.py — costura os clips de motion com o A-roll numa linha do tempo.

No modo storytelling do canal, o motion graphics TOMA A TELA INTEIRA: ele nao
e um selo sobre o rosto, ele substitui o rosto. Entao a costura e simples e
exata — cada faixa de tempo pertence a um dono so:

    [aroll 0–4.2s][M03 4.2–9.1s][aroll 9.1–11.0s][M05 11.0–15.4s]…

Isso e mais barato e mais fiel que sobrepor com alpha: nada de mascara, nada
de canal extra, e o corte fica limpo no quadro exato. A voz e a cama correm por
cima da linha inteira, sem serem tocadas pelo corte de imagem — e o que faz o
J-cut funcionar: a imagem troca antes da frase, o audio nao.

Uso: montador.py --projeto edicao/motion --out out/motion.mp4 [--legenda sim|nao]
"""
import argparse, hashlib, json, subprocess, sys
from pathlib import Path

FPS = 30


def _dur(arq):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(arq)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return float((r.stdout or "0").strip() or 0)


# ---------- reenquadramento ------------------------------------------------
# Pedido do dono em 2026-09-27, a partir de um defeito real: a versao anterior
# repartia todo A-roll em pedacos de tamanho fixo (1,8-3,4 s) e girava por uma
# lista de zooms sem olhar pra fala — zoom em lugar nenhum, so por ritmo. O
# dono ouviu na hora: "tem muito zoom fora do lugar". A regra dele e outra:
# zoom IN so em enfase (o volume da propria voz decide onde), e zoom OUT so
# quando ha um corte de verdade, desfazendo o zoom que ficou. Um plano sem
# nenhuma enfase real fica 1,0x do inicio ao fim — sem sub-corte nenhum.
#
# Isso tambem ataca a dessincronia de audio que o dono relatou: a versao
# antiga gerava dezenas de pedacos por minuto so pelo ritmo, cada um virando
# um ponto de emenda (`xfade`) a mais — e cada emenda e uma chance a mais de
# desvio de quadro se acumular. Reenquadrar so nas enfases reais derruba
# drasticamente esse numero de emendas.
PLANO_MIN = 0.7        # pedaco mais curto que isto e flick, nao enfase — descarta
# 1,0 e o enquadramento do take; os seguintes escalam a enfase. Era
# (1.18, 1.32, 1.45) — pensado para reenquadrar take deitado. Take de celular
# ja chega vertical e em close: 1,45x estourava o rosto e cortava a tela que o
# dono aponta. Pedido do dono em 2026-09-27: "voce esta editando um video
# vertical como se fosse horizontal".
ZOOMS_ENFASE = (1.12, 1.20)

SR_ENVELOPE = 16000
HOP_S = 0.04           # 40 ms por amostra do envelope — fino o bastante pra palavra
PROMINENCIA_DB = 8.0   # o quanto o pico tem que saltar acima da vizinhanca pra contar
# 6s de vizinhanca (nao 1-2s): comparado so com a propria frase, todo silaba
# tonica vira "pico" — janela larga compara com varias frases ao redor, entao
# so sobra uma subida de volume real, nao a cadencia normal da fala
JANELA_VIZINHANCA_S = 6.0
ESPACO_MIN_PICOS_S = 5.0    # dois picos mais pertos que isto viram um so
PISO_PERCENTIL = 88         # abaixo deste percentil do envelope inteiro, nunca e enfase
MARGEM_BORDA_S = 0.35       # nao reparte a menos disto do inicio/fim do plano


def _envelope_de_voz(fonte):
    """RMS em dB a cada `HOP_S`, do audio inteiro de `fonte`. E a mesma tecnica
    de `silencio.py`, aqui em dB porque enfase e uma pergunta de PROPORCAO
    (quantos dB acima da fala ao redor), nao de amplitude crua."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(fonte), "-f", "s16le",
                          "-ac", "1", "-ar", str(SR_ENVELOPE), "-"],
                         capture_output=True, check=True).stdout
    import numpy as np
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    n = int(SR_ENVELOPE * HOP_S)
    k = len(a) // n
    if k < 3:
        return np.array([]), HOP_S
    rms = np.sqrt((a[:k * n].reshape(k, n) ** 2).mean(1))
    db = 20 * np.log10(np.maximum(rms, 1e-6))
    return db, HOP_S


def _picos_de_enfase(env, hop_s):
    """os instantes (s) onde a voz salta acima da propria vizinhanca — enfase
    de verdade, nao so "esta falando alto". Pico local + prominencia relativa
    ao redor, igual deteccao de pico de audio de verdade, sem depender de
    scipy."""
    if len(env) == 0:
        return []
    import numpy as np
    janela = max(1, int(JANELA_VIZINHANCA_S / hop_s))
    piso = float(np.percentile(env, PISO_PERCENTIL))
    picos = []
    for i in range(janela, len(env) - janela):
        v = env[i]
        if v < env[i - 1] or v <= env[i + 1]:
            continue   # nao e maximo local
        if v < piso:
            continue   # alto na vizinhanca mas baixo pro take inteiro — nao conta
        redor = np.concatenate([env[i - janela:i - janela // 3],
                                env[i + janela // 3:i + janela]])
        if len(redor) == 0:
            continue
        base = float(np.median(redor))
        if v - base >= PROMINENCIA_DB:
            picos.append((i * hop_s, v - base))
    picos.sort()
    # funde picos vizinhos: fica so o mais forte de cada grupo
    fundidos = []
    for t, forca in picos:
        if fundidos and t - fundidos[-1][0] < ESPACO_MIN_PICOS_S:
            if forca > fundidos[-1][1]:
                fundidos[-1] = (t, forca)
        else:
            fundidos.append((t, forca))
    return [t for t, _ in fundidos]


def _repartir_por_enfase(de, ate, picos):
    """so reparte um plano nos pontos de enfase que caem dentro dele. Sem
    enfase, o plano inteiro fica 1,0x — sem sub-corte nenhum. Cada enfase
    escala o zoom mais um degrau; o zoom SO desce no corte seguinte (o
    chamador de `faixas` sempre comeca o proximo plano em 1,0x de novo)."""
    dentro = [p for p in picos if de + MARGEM_BORDA_S < p < ate - MARGEM_BORDA_S]
    cortes = [de] + dentro + [ate]
    pedacos = []
    nivel = 0
    for k in range(len(cortes) - 1):
        a, b = cortes[k], cortes[k + 1]
        if k > 0 and b - a < PLANO_MIN:
            # enfase colada demais na anterior — nao vale sub-corte, mas o
            # trecho nao pode sumir: descartar deixava um buraco de imagem
            # (ate 0,7 s) com o audio correndo por cima — dessincronia
            pedacos[-1]["ate"] = b
            continue
        z = 1.0 if k == 0 else ZOOMS_ENFASE[min(nivel, len(ZOOMS_ENFASE) - 1)]
        if k > 0:
            nivel += 1
        pedacos.append({"tipo": "aroll", "de": a, "ate": b, "zoom": z})
    # a fusao acima pode deixar o ultimo pedaco largo demais sem o corte que
    # ele ia ter — devolve a ponta pro pedaco anterior em vez de perder tempo
    if len(pedacos) > 1 and pedacos[-1]["ate"] - pedacos[-1]["de"] < PLANO_MIN:
        pedacos[-2]["ate"] = pedacos[-1]["ate"]
        pedacos.pop()
    return pedacos


def faixas(plano, hf_dir, reenquadrar=True, fonte=None, offset_audio_s=0.0):
    """a linha do tempo em pedacos, cada um com dono: o A-roll ou um clip."""
    out, t = [], 0
    for p in plano["planos"]:
        t0, t1 = p["t0"] / 1000, p["t1"] / 1000
        clip = hf_dir / p["id"] / "clip.mp4"
        if p["tipo"] == "fala" or not clip.exists():
            out.append({"tipo": "aroll", "de": t0, "ate": t1})
        else:
            out.append({"tipo": "clip", "de": t0, "ate": t1, "arq": clip, "id": p["id"]})
        t = t1
    # funde faixas de A-roll vizinhas: menos cortes, menos reencode
    fundidas = []
    for f in out:
        if fundidas and f["tipo"] == "aroll" and fundidas[-1]["tipo"] == "aroll":
            fundidas[-1]["ate"] = f["ate"]
        else:
            fundidas.append(f)
    # o zoom so desce num corte DE VERDADE — e corte de verdade inclui o corte
    # de silencio, nao so a fronteira de plano do guia. Sem isto, o 19 tinha 11
    # planos e 46 emendas: a primeira enfase subia o zoom e ele ficava la por
    # minutos (93% do video em 1,45x).
    cortes = sorted(c / 1000 for c in (plano.get("cortesMs") or []))
    if cortes:
        repartidas = []
        for f in fundidas:
            if f["tipo"] != "aroll":
                repartidas.append(f)
                continue
            a = f["de"]
            for c in cortes:
                if f["de"] < c < f["ate"] and c - a > 0.001:
                    repartidas.append({"tipo": "aroll", "de": a, "ate": c})
                    a = c
            repartidas.append({"tipo": "aroll", "de": a, "ate": f["ate"]})
        fundidas = repartidas
    if not reenquadrar:
        return fundidas
    # ...e so entao reparte de novo, nos pontos onde a propria voz da a enfase.
    # `fonteAudio` pode ter um offset proprio contra `fonteVideo` (fonteOffsetMs
    # do plano) — o pico e medido no relogio do audio, entao volta pro relogio
    # do video antes de cortar por ele.
    picos = [p + offset_audio_s for p in _picos_de_enfase(*_envelope_de_voz(fonte))] if fonte else []
    if picos:
        print(f"enfase: {len(picos)} pico(s) de voz — zoom entra so ali", flush=True)
    final = []
    for f in fundidas:
        final.extend(_repartir_por_enfase(f["de"], f["ate"], picos) if f["tipo"] == "aroll" else [f])
    return _na_grade(final)


def _na_grade(fs, fps=FPS):
    """toda fronteira de faixa cai num quadro inteiro. O pico de enfase sai do
    envelope da voz (20,88 s = quadro 626,4) e cada pedaco cortado com -ss/-to
    arredondava a propria contagem de quadros: 31 pedacos somaram 5 quadros de
    atraso da imagem no fim do video 20, com o audio intacto. Na grade, a soma
    dos pedacos e a montagem, quadro por quadro."""
    out = []
    for f in fs:
        g = dict(f, de=round(f["de"] * fps) / fps, ate=round(f["ate"] * fps) / fps)
        if out:
            g["de"] = out[-1]["ate"]
        if g["ate"] - g["de"] >= 1 / fps - 1e-9:
            out.append(g)
        elif out:
            out[-1]["ate"] = g["ate"]
    return out


def rastrear(fonte, destino):
    """a caixa do rosto a cada 0,25 s, pelo motor de visão da máquina — local, nada sobe.

    O plugin ja tinha isto pronto (`rastrear_rosto.swift` + `enquadrar_rosto.py`),
    construido para a faixa de quem fala na tela dividida, e nunca tinha sido
    ligado ao reenquadramento. Aqui ele passa a decidir ONDE o recorte cai:
    sem isso, um plano de 1,45x centrado no meio do quadro corta quem nao esta
    no meio — e ninguem fala parado no centro geometrico por 45 s."""
    if destino.exists() and destino.stat().st_mtime > fonte.stat().st_mtime:
        return destino
    import visao
    try:
        visao.rastrear_rosto(fonte, destino)
    except (SystemExit, subprocess.CalledProcessError, OSError) as e:
        print(f"  rosto: rastreamento falhou, seguindo centrado ({str(e)[-120:].strip()})",
              flush=True)
        return None
    return destino if destino.exists() else None


def _amostras_do_rosto(caminho):
    if not caminho:
        return []
    try:
        import enquadrar_rosto as er
        return er.carregar(caminho)
    except Exception:
        return []


def _crop_do_rosto(faixa, amostras, W, H, z, alvo=0.44):
    """(x, y) do recorte para este trecho, a partir de onde o rosto esta.

    O enquadramento e CONSTANTE dentro do plano, nao segue o rosto quadro a
    quadro: este estilo pede camera travada, e crop perseguindo rosto le como
    camera na mao. O que a trajetoria decide e onde o plano fica parado — a
    mediana das amostras do trecho, que ignora a deteccao isolada errada."""
    import enquadrar_rosto as er
    zw, zh = int(W * z) // 2 * 2, int(H * z) // 2 * 2
    sobra_x, sobra_y = zw - W, zh - H
    dentro = [a for a in amostras if faixa["de"] <= a["time"] <= faixa["ate"]]
    if not dentro:                      # trecho sem rosto: fica no meio
        dentro = [min(amostras, key=lambda a: abs(a["time"] - faixa["de"]))]
    ys, xs = [], []
    for a in dentro:
        y0, _, _, _ = er.alvo_vertical(a, H, z, H, sobra_y, alvo)
        ys.append(y0)
        xs.append(a["centerX"] * zw - W / 2)
    ys, xs = sorted(ys), sorted(xs)
    y = ys[len(ys) // 2]
    x = xs[len(xs) // 2]
    return (int(min(max(x, 0), sobra_x)) // 2 * 2,
            int(min(max(y, 0), sobra_y)) // 2 * 2)


def _vf_aroll(faixa, W, H):
    """o reenquadramento do trecho: amplia e recorta de volta para 9:16.

    O recorte NAO e centrado no eixo vertical. Quem fala olhando para a camera
    tem a cabeca no terco de cima; cortar pela metade decepa a testa e sobra
    tronco. O que se corta e o TORSO, embaixo.

    E a fracao nao pode ser fixa. Com 0,28 da sobra vindo de cima, um plano de
    1,45x comia 167 px do quadro original — a testa inteira. A conta certa e
    em pixels do ORIGINAL: `(zh-H)*b/z` e quanto se perde do topo de verdade,
    entao `b` sai de um teto em pixels (TOPO_MAX) e encolhe sozinho conforme o
    plano fecha."""
    z = float(faixa.get("zoom") or 1.0)
    if z <= 1.001:
        return f"scale={W}:{H},fps={FPS}"
    zw, zh = int(W * z) // 2 * 2, int(H * z) // 2 * 2
    if faixa.get("crop"):                 # o rosto disse onde o recorte cai
        x, y = faixa["crop"]
    else:                                 # sem rastreamento: centro, teto de topo
        TOPO_MAX = 44      # px do quadro original que podem sair por cima
        b = min(0.28, TOPO_MAX * z / max(1.0, H * (z - 1)))
        x, y = (zw - W) // 2, int((zh - H) * b)
    return f"scale={zw}:{zh},crop={W}:{H}:{x}:{y},fps={FPS}"


def _transicao_do_estilo(plano):
    """a receita de emenda do estilo de motion, ou None para corte seco."""
    try:
        import estilos
    except ImportError:
        return None
    nome = estilos.escolher(plano, "motion")
    t = (estilos.MOTION.get(nome) or {}).get("transicao")
    if not t:
        return None
    return {"entre_rosto": t.get("entre_rosto", "fade"),
            "rosto_ms": int(t.get("rosto_ms") or 166),
            "com_motion": t.get("com_motion", "slideleft"),
            "motion_ms": int(t.get("motion_ms") or 233)}


def _costurar_com_transicao(fs, arquivos, trans, sobra, saida):
    """costura os pedacos com `xfade`, SEM encolher a linha do tempo.

    O `xfade` sobrepoe: duas faixas de 3 s emendadas com 0,2 s dao 5,8 s, nao
    6 s. Num video com voz gravada isso e fatal — a imagem encurta e o audio
    nao, e a partir da primeira emenda tudo sai dessincronizado, acumulando.

    A conta que resolve: cada pedaco (menos o ultimo) e renderizado com
    `sobra` segundos A MAIS, e o deslocamento de cada emenda e a **soma das
    duracoes NOMINAIS** dos pedacos anteriores — soma limpa, sem descontar a
    duracao da emenda e sem somar a sobra. O resultado de cada `xfade` tem
    `deslocamento + tamanho do pedaco que entra`, entao no fim ele fecha exato
    em `soma(duracoes)`. A sobra existe so para o pedaco que sai ter material
    por baixo enquanto a emenda acontece — dai a exigencia `emenda <= sobra`.

    (Errei isto na primeira versao: descontei a duracao da emenda do
    deslocamento e ainda somei a sobra que cada emenda nao consumia. Dava
    48,083 s numa linha de 47,614 s — meio segundo de dessincronia que cresce
    a cada emenda.)

    A emenda muda conforme o que ha dos dois lados: dissolve curto entre dois
    reenquadramentos do mesmo rosto (costura o jump cut), empurrao lateral
    quando um dos lados e motion (a troca de assunto merece ser vista)."""
    entradas, filtros, acumulado = [], [], 0.0
    for arq in arquivos:
        entradas += ["-i", str(arq)]
    atual = "[0:v]"
    for k in range(1, len(fs)):
        so_rosto = fs[k - 1]["tipo"] == "aroll" and fs[k]["tipo"] == "aroll"
        tipo = trans["entre_rosto"] if so_rosto else trans["com_motion"]
        dur = (trans["rosto_ms"] if so_rosto else trans["motion_ms"]) / 1000
        dur = min(dur, sobra)          # emenda nunca maior que o material extra
        acumulado += fs[k - 1]["ate"] - fs[k - 1]["de"]
        alvo = f"[x{k}]" if k < len(fs) - 1 else "[v]"
        filtros.append(f"{atual}[{k}:v]xfade=transition={tipo}:duration={dur:.3f}:"
                       f"offset={acumulado:.3f}{alvo}")
        atual = alvo
    subprocess.run(["ffmpeg", "-y", "-nostdin", "-v", "error", "-stats", *entradas,
                    "-filter_complex", ";".join(filtros), "-map", "[v]",
                    "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
                    "-pix_fmt", "yuv420p", str(saida)], check=True)


def swoosh(saida, dur=0.42, taxa=48000):
    """um swoosh suave, sintetizado — nao e sample baixado de lugar nenhum.

    A receita e a de sempre no som de transicao: ruido rosa passando por um
    passa-banda que SOBE e depois DESCE, com envelope de sino. O que separa o
    "suave" do "whoosh de pacote gratis" e nao ter ataque: o envelope entra em
    0,12 s em vez de estalar, e a banda para em 5 kHz em vez de varrer ate o
    agudo. Ele fica 18 dB abaixo da voz — pontua a emenda, nao concorre com ela.

    (`trilha.py` ja sintetiza a cama musical do mesmo jeito; este arquivo so
    acrescenta o acento de emenda, que faltava.)"""
    import numpy as np
    n = int(dur * taxa)
    t = np.arange(n) / taxa
    ruido = np.random.default_rng(7).normal(0, 1, n)
    # ruido rosa por integracao leve: tira o brilho de chiado do ruido branco
    rosa = np.convolve(ruido, np.ones(24) / 24, mode="same")
    # a banda sobe e desce: e o que da o senso de passagem
    centro = 420 + 4600 * np.sin(np.pi * t / dur) ** 1.4
    fase = np.cumsum(2 * np.pi * centro / taxa)
    corpo = rosa * np.sin(fase)
    # envelope de sino sem ataque: sobe em 0,12 s, desce o resto
    env = np.sin(np.pi * (t / dur)) ** 1.8
    onda = corpo * env
    onda = onda / (np.max(np.abs(onda)) or 1.0) * 0.16      # ~ -16 dBFS
    import wave
    with wave.open(str(saida), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(taxa)
        w.writeframes((onda * 32767).astype("<i2").tobytes())
    return saida


def _faixa_de_swoosh(marcas, total, saida, taxa=48000):
    """uma faixa do tamanho do video com um swoosh em cada emenda pedida.

    Uma faixa so, em vez de N entradas no ffmpeg: menos filtro, menos chance
    de erro, e o mesmo resultado. O acento comeca ANTES da emenda (o swoosh
    conduz o corte, nao reage a ele) — dai o recuo de 0,14 s."""
    import numpy as np
    tmp = saida.with_name("_swoosh_un.wav")
    swoosh(tmp)
    import wave
    with wave.open(str(tmp), "rb") as w:
        som = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32)
    faixa = np.zeros(int(total * taxa) + len(som), dtype=np.float32)
    for m in marcas:
        i = max(0, int((m - 0.14) * taxa))
        faixa[i:i + len(som)] += som
    faixa = faixa[:int(total * taxa)]
    pico = np.max(np.abs(faixa)) or 1.0
    faixa = faixa / pico * 0.10 * 32767        # ~ -20 dBFS: pontua, nao disputa
    with wave.open(str(saida), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(taxa)
        w.writeframes(faixa.astype("<i2").tobytes())
    tmp.unlink(missing_ok=True)
    return saida


def _estado(arq):
    s = Path(arq).stat()
    return f"{Path(arq).resolve()}:{s.st_size}:{s.st_mtime_ns}"


def cortar_em_cache(faixa, fonte, cache, W, H, sobra=0.0, mascara_png=None):
    """cada pedaco e nomeado pelo que o produz (faixa, recorte, zoom, sobra e o
    estado dos arquivos de origem). Mudou so o zoom de tres planos? Os outros
    saem do cache e so aqueles tres sao refeitos."""
    deps = [fonte] + ([faixa["arq"]] if faixa["tipo"] == "clip" else []) \
        + ([mascara_png] if mascara_png and faixa["tipo"] == "aroll" else [])
    chave = json.dumps({"v": 2, "f": {k: v for k, v in faixa.items() if k != "arq"},
                        "s": round(sobra, 4), "W": W, "H": H,
                        "vf": _vf_aroll(faixa, W, H) if faixa["tipo"] == "aroll" else None,
                        "deps": [_estado(d) for d in deps]}, sort_keys=True, default=str)
    destino = cache / (hashlib.sha256(chave.encode()).hexdigest()[:20] + ".mp4")
    if destino.exists() and destino.stat().st_size > 0:
        return destino, True
    tmp = destino.with_suffix(".tmp.mp4")
    cortar(faixa, fonte, tmp, W, H, 0, sobra, mascara_png)
    tmp.rename(destino)   # so entra no cache inteiro; ffmpeg interrompido nao deixa lixo valido
    return destino, False


def cortar(faixa, fonte, destino, W, H, i, sobra=0.0, mascara_png=None):
    if faixa["tipo"] == "aroll":
        # a mascara Dividir (opcional, `mascara.py`) e do clipe de quem fala:
        # entra depois do reenquadramento, entao a linha fica parada no quadro
        # enquanto o zoom troca — como no CapCut, onde ela e do clipe e nao da
        # imagem ampliada dentro dele
        # por contagem de quadros, nunca por -to: a fonte e CFR e a faixa esta
        # na grade, entao o pedaco tem exatamente os quadros que a faixa ocupa
        q0 = round(faixa["de"] * FPS)
        n = round((faixa["ate"] + sobra) * FPS) - q0
        entrada = ["-ss", f"{(q0 - 0.25) / FPS:.4f}", "-i", str(fonte), "-frames:v", str(n)]
        if mascara_png:
            filtro = ["-loop", "1", "-i", str(mascara_png), "-filter_complex",
                      f"[0:v]{_vf_aroll(faixa, W, H)}[b];[b][1:v]overlay=0:0:shortest=1[v]",
                      "-map", "[v]"]
        else:
            filtro = ["-vf", _vf_aroll(faixa, W, H)]
        subprocess.run(["ffmpeg", "-y", "-nostdin", "-v", "error", *entrada, *filtro, "-an",
                        "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
                        "-pix_fmt", "yuv420p", str(destino)], check=True)
        return destino
    # o clip ja e 9:16 no tempo do plano; so garante duracao e formato iguais.
    # A `sobra` da emenda sai do ultimo quadro segurado: o clip nao tem
    # material extra para dar, e o que fica por baixo do dissolve e justamente
    # o quadro final dele.
    alvo = faixa["ate"] - faixa["de"] + sobra
    tem = _dur(faixa["arq"])
    # se o clip saiu mais curto que a faixa, o ultimo quadro segura o resto
    vf = f"scale={W}:{H},fps={FPS}"
    if tem < alvo - 0.05:
        vf += f",tpad=stop_mode=clone:stop_duration={alvo-tem:.3f}"
    subprocess.run(["ffmpeg", "-y", "-nostdin", "-v", "error", "-i", str(faixa["arq"]),
                    "-frames:v", str(round((faixa["ate"] + sobra) * FPS) - round(faixa["de"] * FPS)),
                    "-vf", vf, "-an",
                    "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
                    "-pix_fmt", "yuv420p", str(destino)], check=True)
    return destino


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projeto", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--legenda", default="sim", choices=["sim", "nao"])
    ap.add_argument("--crf", type=int, default=18)
    ap.add_argument("--sem-reenquadrar", action="store_true",
                    help="nao reparte o A-roll em planos curtos; deixa a tomada "
                         "inteira num tamanho só (era o comportamento antigo)")
    ap.add_argument("--sem-transicao", action="store_true",
                    help="corta seco entre os planos, ignorando a receita de "
                         "emenda do estilo")
    ap.add_argument("--sem-rastrear", action="store_true",
                    help="nao rastreia o rosto; o recorte fica centrado no quadro")
    ap.add_argument("--sem-swoosh", action="store_true",
                    help="nao põe o acento sonoro nas emendas com motion")
    ap.add_argument("--sem-mascara", action="store_true",
                    help="ignora a mascara Dividir do plano mesmo ligada")
    a = ap.parse_args()

    projeto = Path(a.projeto)
    plano = json.loads((projeto / "plano.json").read_text(encoding="utf-8"))
    W, H = plano["largura"], plano["altura"]
    hf_dir = projeto / "out" / "hf"
    trabalho = projeto / "out" / "costura"
    trabalho.mkdir(parents=True, exist_ok=True)
    fonte = projeto / "public" / plano["fonteVideo"]
    # a enfase e do audio, e `fonte` (fonteVideo) e mudo — a voz mora em
    # fonteAudio, separada. Analisar a video muda daria zero pico sempre.
    fonte_audio = (projeto / "public" / plano["fonteAudio"]) if plano.get("fonteAudio") else fonte

    fs = faixas(plano, hf_dir, reenquadrar=not a.sem_reenquadrar, fonte=fonte_audio,
                offset_audio_s=(plano.get("fonteOffsetMs") or 0) / 1000)
    quantos = sum(1 for f in fs if f["tipo"] == "clip")
    dur_total = plano["duracaoMs"] / 1000
    print(f"linha do tempo: {len(fs)} faixa(s), {quantos} de motion, "
          f"{len(fs) / dur_total * 60:.0f} cortes/min", flush=True)

    # a emenda entre planos vem do ESTILO: corte seco quando ele nao pede nada,
    # dissolve/empurrao quando pede. `sobra` e o quanto cada pedaco (menos o
    # ultimo) e renderizado A MAIS, para a sobreposicao consumir exatamente
    # isso e a duracao total nao encolher — se encolher, a voz sai de sincronia.
    trans = _transicao_do_estilo(plano) if not a.sem_transicao else None
    sobra = (max(trans["rosto_ms"], trans["motion_ms"]) / 1000) if trans else 0.0

    # onde o rosto esta, para o recorte de cada plano cair nele
    amostras = []
    if not a.sem_rastrear:
        rosto = rastrear(fonte, projeto / "out" / "rosto.json")
        amostras = _amostras_do_rosto(rosto)
        if amostras:
            print(f"rosto: {len(amostras)} amostras — o reenquadramento segue o rosto",
                  flush=True)
            for f in fs:
                if f["tipo"] == "aroll" and float(f.get("zoom") or 1.0) > 1.001:
                    f["crop"] = _crop_do_rosto(f, amostras, W, H, float(f["zoom"]))

    mascara_png = None
    import mascara
    if mascara.ativa_no_solo(plano) and not a.sem_mascara:
        m = mascara.normalizar(plano.get("mascara"))
        mascara_png = mascara.png(m, W, H, trabalho / "_mascara.png")
        print(f"mascara: Dividir horizontal · linha {m['linhaPct']:.0f}% · "
              f"suavizar {m['suavizarPct']:.0f}%", flush=True)

    cache = trabalho / "cache"
    cache.mkdir(exist_ok=True)
    arquivos, reusados = [], 0
    for i, f in enumerate(fs):
        destino, veio_do_cache = cortar_em_cache(f, fonte, cache, W, H,
                                                 sobra if i < len(fs) - 1 else 0.0, mascara_png)
        reusados += veio_do_cache
        arquivos.append(destino)
        print(f"  {i+1}/{len(fs)} {f['tipo']}{' ' + f.get('id','') if f['tipo']=='clip' else ''}"
              f"{' (cache)' if veio_do_cache else ''}", flush=True)
    print(f"pedacos: {reusados} reaproveitado(s), {len(fs) - reusados} renderizado(s)", flush=True)

    mudo = trabalho / "_video.mp4"
    if trans and len(fs) > 1:
        _costurar_com_transicao(fs, arquivos, trans, sobra, mudo)
    else:
        lista = trabalho / "lista.txt"
        lista.write_text("\n".join(f"file '{p.resolve()}'" for p in arquivos) + "\n",
                         encoding="utf-8")
        subprocess.run(["ffmpeg", "-y", "-nostdin", "-v", "error", "-f", "concat", "-safe", "0",
                        "-i", str(lista), "-c", "copy", str(mudo)], check=True)

    # audio: voz sempre; cama quando o plano tem trilha; swoosh nas emendas
    voz = projeto / "public" / (plano.get("fonteAudio") or plano["fonteVideo"])
    trilha = projeto / "public" / plano["trilha"] if plano.get("trilha") else None
    dur = plano["duracaoMs"] / 1000

    # O estilo pede o acento SO na emenda deslizante — "sparse and restrained,
    # not a whoosh-fest". Emenda de reenquadramento (rosto→rosto) nao leva
    # nada: sao 10 delas em 47 s, e um swoosh em cada viraria tique.
    sw = None
    if trans and not a.sem_swoosh:
        acc, marcas = 0.0, []
        for k in range(1, len(fs)):
            acc += fs[k - 1]["ate"] - fs[k - 1]["de"]
            if not (fs[k - 1]["tipo"] == "aroll" and fs[k]["tipo"] == "aroll"):
                marcas.append(acc)
        if marcas:
            sw = _faixa_de_swoosh(marcas, dur, trabalho / "_swoosh.wav")
            print(f"swoosh: {len(marcas)} emenda(s) com acento", flush=True)

    cmd = ["ffmpeg", "-y", "-nostdin", "-v", "error", "-stats", "-i", str(mudo), "-i", str(voz)]
    entradas = 2
    partes, mix = [], ["[1:a]"]
    if trilha and trilha.exists():
        vol = float(plano.get("trilhaVolume") or 0.5)
        cmd += ["-i", str(trilha)]
        partes.append(f"[{entradas}:a]volume={vol},afade=t=in:d=1,"
                      f"afade=t=out:st={max(0,dur-2):.2f}:d=2[m]")
        mix.append("[m]")
        entradas += 1
    if sw:
        cmd += ["-i", str(sw)]
        mix.append(f"[{entradas}:a]")
        entradas += 1
    if "[m]" in mix:
        import acabamento
        partes.append(acabamento.mistura_voz_cama("[1:a]", "[m]", extras=mix[2:]))
        cmd += ["-filter_complex", ";".join(partes), "-map", "0:v", "-map", "[a]"]
    elif len(mix) > 1:
        partes.append(f"{''.join(mix)}amix=inputs={len(mix)}:duration=first:normalize=0[a]")
        cmd += ["-filter_complex", ";".join(partes), "-map", "0:v", "-map", "[a]"]
    else:
        cmd += ["-map", "0:v", "-map", "1:a"]
    saida = Path(a.out)
    saida.parent.mkdir(parents=True, exist_ok=True)
    cmd += ["-t", f"{dur:.3f}", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", str(saida)]
    subprocess.run(cmd, check=True)
    print(f"pronto: {saida}")


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
