#!/usr/bin/env python3
"""
montar.py — o pipeline obedece ao guia.

Substitui o plano.py quando ha take filmado. A decisao de onde motion entra
ja foi tomada pelo diretor; aqui ela vira material: corte de pausas que
respeita o guia, A-roll com grade, voz tratada, cama por momento, planos com
tempos convertidos, e um preview MEDIDO antes de qualquer "pronto".

Uso: montar.py --guia guia/guia.json [--fatos guia/fatos.json] --take take.mov
               --falas take.whisper.json --projeto motion/ --edicao edicao/
               [--so-planos] [--sem-preview] [--deslocamento 0]
"""
import argparse, json, re, subprocess, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tempo, travas, acabamento, cor, trilha, medir, validar, sdr, direcao, estilos, mascara  # noqa: E402
import voz as vozlib  # noqa: E402

FPS = 30
PAUSA_MAX_MS = 1300
PAD_MS = 600
MARGEM_FONETICA_MS = 600
# Um corte seco custa ritmo. Ele so se paga se comprar tempo suficiente para
# valer o solavanco, e se o que sobra dos dois lados ainda for um PLANO — nao
# um lampejo. Medido no 05: pausas de 298 a 560 ms tiradas do meio de frases
# continuas deixaram pedacos de 852 ms entre dois cortes, e o resultado
# gagueja. Buraco pequeno demais e pedaco curto demais voltam a ser material.
BURACO_MIN_MS = 300
PEDACO_MIN_MS = 1200
# Corte de silencio MEDIDO NO AUDIO. Pedido do dono em 2026-09-27, sobre o 19
# (9:51 de bruto virou 8:55): "voce nao editou". O corte por pausa entre
# palavras nao cortava nada: o whisper (MLX) cola o fim de uma palavra no
# comeco da seguinte, entao o transcript quase nao tem pausa — e a guarda de
# pronuncia (600 ms de margem por palavra) desfazia o pouco que sobrava. O audio
# tinha 148 silencios somando 85 s. Corte dentro de silencio medido nao come
# fala por construcao, entao ele dispensa a guarda por palavra.
SILENCIO_MIN_MS = 400        # silencio mais curto que isso e respiracao da frase
SILENCIO_LIMIAR_DB = -38     # abaixo disso e sala, nao voz
MARGEM_SILENCIO_MS = 90      # silencio que fica de cada lado da emenda (ataque e soltura)
# O split edit em cabeca falante (`referencias/sincronia.md`,
# `formato-analise.md` «O split edit»): a IMAGEM do trecho que entra chega
# SPLIT_MS antes, sobre o silencio da cauda de quem sai; o AUDIO nao se mexe.
# Em quadros inteiros, para que imagem e som fechem na mesma amostra.
SPLIT_QUADROS = 6            # 200 ms a 30 fps — o piso do que se le como split
SPLIT_FOLGA_CAUDA_MS = 40    # silencio a mais na cauda alem da janela do split
COM_MOTION = {"motion", "aroll+motion"}
TEM_TEXTO_PROPRIO = travas.TEM_TEXTO_PROPRIO


# ---------- corte ---------------------------------------------------------

def _pausas_protegidas(guia):
    """inicios de momento que o diretor apoiou numa pausa: J-cut
    (entraAntesMs > 0) ou respiro (musica.cama == some)"""
    prot = []
    for m in guia["momentos"]:
        mo = m.get("motion") or {}
        if int(mo.get("entraAntesMs") or 0) > 0 or (m.get("musica") or {}).get("cama") == "some":
            prot.append(m["deMs"])
    return prot


def silencios_medidos(take, cache=None, minimo_ms=SILENCIO_MIN_MS, limiar_db=SILENCIO_LIMIAR_DB):
    """[(deMs, ateMs)] dos silencios do audio do take, pelo `silencedetect` do
    ffmpeg. Cacheado por tamanho/data do take e pelos parametros."""
    take = Path(take)
    st = take.stat()
    chave = f"{take.resolve()}:{st.st_size}:{st.st_mtime_ns}:{minimo_ms}:{limiar_db}"
    if cache and Path(cache).exists():
        d = json.loads(Path(cache).read_text(encoding="utf-8"))
        if d.get("chave") == chave:
            return [tuple(s) for s in d["silencios"]]
    r = subprocess.run(["ffmpeg", "-nostdin", "-v", "info", "-i", str(take), "-vn",
                        "-af", f"silencedetect=n={limiar_db}dB:d={minimo_ms / 1000:.3f}",
                        "-f", "null", "-"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    sil, ini = [], None
    for linha in r.stderr.splitlines():
        m = re.search(r"silence_start: (-?[\d.]+)", linha)
        if m:
            ini = max(0.0, float(m.group(1)))
        m = re.search(r"silence_end: ([\d.]+)", linha)
        if m and ini is not None:
            sil.append((int(ini * 1000), int(float(m.group(1)) * 1000)))
            ini = None
    if cache:
        Path(cache).write_text(json.dumps({"chave": chave, "silencios": sil}), encoding="utf-8")
    return sil


def trechos_mantidos(guia, palavras, pausa_max_ms=PAUSA_MAX_MS, pad_ms=PAD_MS, silencios=None,
                     margem_silencio_ms=MARGEM_SILENCIO_MS):
    """1) tira os momentos `cortar`; 2) dentro do que sobra, tira as pausas
    entre palavras maiores que pausa_max — a nao ser que o diretor as tenha
    reservado. Devolve trechos no relogio do bruto."""
    blocos = []
    for m in guia["momentos"]:
        if m["decisao"] == "cortar":
            continue
        if blocos and blocos[-1][1] == m["deMs"]:
            blocos[-1][1] = m["ateMs"]
        else:
            blocos.append([m["deMs"], m["ateMs"]])
    protegidas = _pausas_protegidas(guia)
    saida = []
    for n, (de, ate) in enumerate(blocos):
        if silencios is not None:
            # corte pelo audio: cada silencio medido inteiro dentro do bloco sai,
            # menos a margem dos dois lados. As emendas vem marcadas `medida` e
            # nenhuma guarda por palavra mexe nelas.
            ini, primeiro = de, True
            for s0, s1 in silencios:
                if s0 <= de or s1 >= ate:
                    continue
                if any(s0 <= p <= s1 for p in protegidas):
                    continue
                corte_de, corte_ate = s0 + margem_silencio_ms, s1 - margem_silencio_ms
                if corte_ate - corte_de <= 0 or corte_de <= ini:
                    continue
                trecho = {"brutoDe": ini, "brutoAte": corte_de, "saidaMedida": True}
                if not primeiro:
                    trecho["entradaMedida"] = True
                if n > 0 and primeiro:
                    trecho["doDiretor"] = True
                saida.append(trecho)
                ini, primeiro = corte_ate, False
            trecho = {"brutoDe": ini, "brutoAte": ate}
            if not primeiro:
                trecho["entradaMedida"] = True
            if n > 0 and primeiro:
                trecho["doDiretor"] = True
            saida.append(trecho)
            continue
        dentro = [w for w in palavras if w["deMs"] >= de and w["ateMs"] <= ate]
        ini = de
        for a, b in zip(dentro, dentro[1:]):
            pausa = b["deMs"] - a["ateMs"]
            if pausa <= pausa_max_ms:
                continue
            # a pausa e protegida se um momento comeca dentro dela (o J-cut precisa dela)
            if any(a["ateMs"] <= p <= b["deMs"] for p in protegidas):
                continue
            saida.append({"brutoDe": ini, "brutoAte": a["ateMs"] + pad_ms})
            ini = b["deMs"] - pad_ms
        # `doDiretor` marca o comeco de bloco que veio de um momento `cortar`,
        # e nao de pausa removida por conta propria. As duas limpezas abaixo
        # desfazem corte que nao se paga — mas corte que o diretor escreveu ja
        # foi pago: ele tem `porque`, e a falsa partida que ele tira e
        # justamente a que atravessa a palavra do transcript.
        trecho = {"brutoDe": ini, "brutoAte": ate}
        if n > 0 and ini == de:
            trecho["doDiretor"] = True
        saida.append(trecho)
    return _respiro_nas_bordas(
        _preservar_pronuncia(_sem_gagueira(saida), palavras, pad_ms), palavras)


# a soltura de uma palavra falada dura mais que o timestamp do ASR. 140 ms e o
# minimo para a consoante final nao sair decepada; abaixo disso o ouvido
# registra "cortou no meio", mesmo sem saber por que.
RESPIRO_MS = 140
# e o corte nunca pode revelar a palavra seguinte: ela fica a pelo menos isto
# de distancia do ponto de saida
FOLGA_VIZINHA_MS = 40


def _respiro_nas_bordas(trechos, palavras, respiro_ms=RESPIRO_MS):
    """da de volta a cauda da ultima palavra e o ataque da primeira.

    `_preservar_pronuncia` ja cuida das emendas que o SCRIPT inventa, mas deixa
    passar inteira a emenda escrita pelo diretor (`doDiretor`) — e com razao,
    porque falsa partida corta no meio da palavra de proposito. So que essa
    porta deixava passar tambem o caso em que a fronteira do momento cai em
    cima da ultima palavra: medido em 2026-09-12, o M10 terminava em 49,200 e
    «propria» terminava em 49,200 tambem. Zero folga. O dono ouviu na hora:
    *"quando eu falo «regras de edicao propria», o «propria» ta cortado"*.

    O conserto certo NAO e desfazer o corte do diretor: e empurrar o ponto de
    saida uns quadros para dentro do silencio que vem depois. O corte continua
    onde ele mandou; a palavra e que sai inteira."""
    if not palavras:
        return trechos
    for t in trechos:
        dentro = [w for w in palavras
                  if w["deMs"] >= t["brutoDe"] and w["ateMs"] <= t["brutoAte"]]
        if not dentro:
            continue
        # cauda: empurra a saida ate `respiro_ms` depois da ultima palavra, sem
        # nunca alcancar a proxima (senao o corte devolve fala que saiu)
        if t.get("saidaMedida") and t.get("entradaMedida"):
            continue   # as duas bordas ja estao dentro de silencio medido no audio
        ult = dentro[-1]
        prox = next((w for w in palavras if w["deMs"] >= ult["ateMs"]), None)
        teto = (prox["deMs"] - FOLGA_VIZINHA_MS) if prox else ult["ateMs"] + respiro_ms
        if not t.get("saidaMedida"):
            t["brutoAte"] = max(t["brutoAte"], min(ult["ateMs"] + respiro_ms, teto))
        # ...e, se a fronteira ja estava DENTRO da palavra seguinte, puxa de
        # volta. So esticar nao bastava: o fim do video entrava 100 ms dentro
        # de «para» e o espectador ouvia «comenta aqui, pa-». Nunca recua a
        # ponto de comer a palavra que fica — quando nao ha silencio nenhum
        # entre as duas, a saida cai no limite exato e a cauda e resolvida pelo
        # fade de 80 ms que o compositor aplica no fim do master.
        if prox and t["brutoAte"] > prox["deMs"] and not t.get("saidaMedida"):
            t["brutoAte"] = max(ult["ateMs"], prox["deMs"] - FOLGA_VIZINHA_MS)
        # ataque: recua a entrada, sem alcancar a palavra anterior
        pri = dentro[0]
        ant = [w for w in palavras if w["ateMs"] <= pri["deMs"]]
        piso = (ant[-1]["ateMs"] + FOLGA_VIZINHA_MS) if ant else pri["deMs"] - respiro_ms
        if not t.get("entradaMedida"):
            t["brutoDe"] = min(t["brutoDe"], max(pri["deMs"] - respiro_ms, piso))
    return trechos


def _preservar_pronuncia(trechos, palavras, margem_ms=MARGEM_FONETICA_MS):
    """Desfaz qualquer emenda sem margem acústica para a palavra dos dois lados.

    Timestamp de ASR marca a palavra, não a respiração nem a soltura final do
    fonema. Cortar exatamente em ``ateMs`` pode amputar a cauda; cortar em
    ``deMs`` pode apagar a inspiração ou o ataque da palavra seguinte. Uma
    emenda só sobrevive quando deixa ``margem_ms`` depois da última palavra
    mantida e antes da próxima. Corte que atravessa palavra ou falsa partida
    colada à retomada é restaurado inteiro.
    """
    if len(trechos) < 2:
        return trechos
    saida = [dict(trechos[0])]
    for prox in trechos[1:]:
        atual = saida[-1]
        fim, inicio = atual["brutoAte"], prox["brutoDe"]
        if inicio <= fim:
            atual["brutoAte"] = max(atual["brutoAte"], prox["brutoAte"])
            continue

        # Emenda escrita pelo diretor passa inteira. A guarda abaixo existe para
        # a pausa que o script tira sozinho; aplicada a um momento `cortar` ela
        # desfaz a decisao em silencio — e some justamente com a falsa partida,
        # que por definicao atravessa a palavra que o transcript registrou.
        if prox.get("doDiretor") or (atual.get("saidaMedida") and prox.get("entradaMedida")):
            saida.append(dict(prox))
            continue

        corta_palavra = any(
            w["deMs"] < limite < w["ateMs"]
            for limite in (fim, inicio)
            for w in palavras
        )
        anteriores = [w for w in palavras if w["ateMs"] <= fim]
        seguintes = [w for w in palavras if w["deMs"] >= inicio]
        cauda = fim - anteriores[-1]["ateMs"] if anteriores else margem_ms
        ataque = seguintes[0]["deMs"] - inicio if seguintes else margem_ms

        if corta_palavra or cauda < margem_ms or ataque < margem_ms:
            # Restaurar o buraco é a única operação automaticamente segura.
            # Uma remoção sem silêncio suficiente exige audição e aprovação.
            atual["brutoAte"] = prox["brutoAte"]
        else:
            saida.append(dict(prox))
    return saida


def _sem_gagueira(trechos, buraco_min=BURACO_MIN_MS, pedaco_min=PEDACO_MIN_MS):
    """desfaz o corte que nao se paga: junta de volta o que ficou picado.

    Duas regras, e nenhuma delas toca em corte grande — tirar 15 s de rodeio
    continua valendo:

    1. buraco menor que `buraco_min`: o silencio removido nao compra o
       solavanco de um corte seco.
    2. pedaco menor que `pedaco_min`: o plano nao chega a existir. Ele se junta
       ao vizinho do lado do MENOR buraco — o corte mais barato de desfazer.

    Juntar devolve o material do buraco, entao a voz continua saindo do
    proprio A-roll, quadro a quadro em sincronia."""
    if len(trechos) < 2:
        return trechos
    while True:
        buraco = [trechos[i + 1]["brutoDe"] - trechos[i]["brutoAte"]
                  for i in range(len(trechos) - 1)]
        alvo = None
        for i, b in enumerate(buraco):
            if trechos[i + 1].get("doDiretor"):
                continue   # corte escrito no guia nao se desfaz sozinho
            if b >= buraco_min:
                esq = trechos[i]["brutoAte"] - trechos[i]["brutoDe"]
                dir_ = trechos[i + 1]["brutoAte"] - trechos[i + 1]["brutoDe"]
                curto = (esq < pedaco_min and (i == 0 or buraco[i - 1] >= b)) or \
                        (dir_ < pedaco_min and (i + 1 >= len(buraco) or buraco[i + 1] > b))
                if not curto:
                    continue
            if alvo is None or b < buraco[alvo]:
                alvo = i
        if alvo is None:
            return trechos
        juntado = {"brutoDe": trechos[alvo]["brutoDe"],
                   "brutoAte": trechos[alvo + 1]["brutoAte"]}
        for k in ("doDiretor", "entradaMedida"):
            if trechos[alvo].get(k):
                juntado[k] = True
        if trechos[alvo + 1].get("saidaMedida"):
            juntado["saidaMedida"] = True
        trechos = trechos[:alvo] + [juntado] + trechos[alvo + 2:]


def _boca_em_quadro(guia, ms):
    """a imagem em `ms` mostra a boca de quem fala? So o motion cobre o rosto."""
    for m in guia["momentos"]:
        if m["deMs"] <= ms <= m["ateMs"]:
            return m.get("decisao") not in COM_MOTION
    return True


def jcuts_por_trecho(guia, tabela, pad_ms=PAD_MS):
    """quanto o audio de cada trecho entra antes da imagem dele.

    O J-cut so tem onde acontecer numa emenda do corte — e ali que a imagem
    troca. Um `audioAntesMs` num momento que cai no meio de um trecho continuo
    nao tem corte para anteceder, e vale 0.

    E ha uma segunda condicao, que custou tres masters para eu aprender: o
    J-cut adianta a voz do trecho que ENTRA sobre a cauda do trecho que SAI.
    Se o que sai e o rosto de quem fala, a voz corre a frente da boca — e nao
    so na emenda: o desencontro dura o trecho inteiro. Isso nao e fluidez, e
    dublagem fora de sincronia. Entao o J-cut so vale quando a cauda de quem
    sai esta coberta por motion. No formato `dinamismo`, que e rosto do comeco
    ao fim, isso significa J-cut nenhum — e esta certo assim.

    A soma dos segmentos bater com a duracao do video NAO prova sincronia:
    prova so que nao ha deriva no fim. Foi esse o teste que me enganou."""
    saida = []
    for i, t in enumerate(tabela):
        n = 0
        for m in guia["momentos"]:
            v = int(m.get("audioAntesMs") or 0)
            # o trecho comeca `pad_ms` antes da fala; a folga cobre isso
            if v > 0 and t["brutoDe"] <= m["deMs"] <= t["brutoDe"] + pad_ms + 40:
                n = max(n, v)
        if n and (i == 0 or _boca_em_quadro(guia, tabela[i - 1]["brutoAte"] - 1)):
            n = 0
        saida.append(n)
    return saida


def cortar_voz(take, tabela, jcuts, edicao, suf=""):
    """a trilha de voz com os J-cuts aplicados de verdade.

    O A-roll corta imagem e som juntos, entao o som nunca podia chegar antes da
    imagem — o `audioAntesMs` ficava registrado no guia e nao saia no video.
    Aqui a voz e montada com uma tabela propria: o segmento `k` dura
    `dur_k + N_k - N_(k+1)`, onde N e o J-cut. Quem tem J-cut ganha no comeco o
    que o vizinho anterior perde no fim, a soma continua igual a duracao do
    video, e o que o vizinho perde e a pausa que o validador exigiu existir
    (`audioAntesMs` <= `pausaAntesMs`).

    Devolve None quando nao ha J-cut nenhum: ai a voz sai do proprio A-roll,
    que e mais barato e da exatamente o mesmo resultado.

    ATENCAO — esta implementacao esta ERRADA e por isso se recusa a rodar.
    Ela nao sobrepoe: ela DESLOCA o segmento inteiro (ver `sincronia.md`).
    J-cut de verdade e a cabeca do audio de quem entra estendida por cima da
    cauda de quem sai, com o corpo ancorado na propria imagem — o que exige
    duas pistas mixadas (`adelay` + `amix`), nao uma pista concatenada.
    Ate isso existir, um J-cut pedido tem de PARAR o pipeline, e nao sair como
    master com a boca fora de sincronia. Ja saiu tres vezes."""
    if not any(jcuts):
        return None
    sys.exit("J-cut pedido, mas o montador so sabe DESLOCAR a voz, nao "
             "sobrepor — isso desincroniza a boca o trecho inteiro. "
             "Ver referencias/sincronia.md. Zere o audioAntesMs ou "
             "implemente a mixagem de duas pistas antes de renderizar.")
    pasta = edicao / f"voz-pedacos{suf}"
    pasta.mkdir(exist_ok=True)
    inteira = edicao / f"voz-take{suf}.wav"
    if not inteira.exists():
        print("voz: extraindo o audio do take", flush=True)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(take), "-vn",
                        "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", str(inteira)], check=True)
    lista, n_jc = [], 0
    for i, t in enumerate(tabela):
        prox = jcuts[i + 1] if i + 1 < len(jcuts) else 0
        de = t["brutoDe"]
        ate = t["brutoAte"] + jcuts[i] - prox
        if ate - de < 40:                      # o vizinho nao tinha pausa para ceder
            ate = t["brutoAte"]
        if prox:
            n_jc += 1
        arq = pasta / f"{i:03d}.wav"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(inteira),
                        "-ss", f"{de/1000:.3f}", "-to", f"{ate/1000:.3f}",
                        "-c:a", "pcm_s16le", str(arq)], check=True)
        lista.append(f"file '{arq.resolve()}'")
    (edicao / f"voz-lista{suf}.txt").write_text("\n".join(lista) + "\n", encoding="utf-8")
    bruta = edicao / f"voz-bruta{suf}.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", str(edicao / f"voz-lista{suf}.txt"), "-c", "copy", str(bruta)], check=True)
    print(f"voz: {n_jc} J-cut(s) aplicados — o audio entra antes da imagem", flush=True)
    return bruta


def _q(ms):
    return int(round(ms * FPS / 1000))


def _ms(q):
    return int(round(q * 1000 / FPS))


def split_edits(trechos, split_q=SPLIT_QUADROS, margem_ms=MARGEM_SILENCIO_MS):
    """o corte L de cabeca falante — pedido do dono em 2026-09-27: "quero jcut
    nos cortes pra ficar mais sutil e fluido [...] cuidado para nao
    dessincronizar o audio com o video".

    Em rosto do comeco ao fim o corte J (som antes da imagem) poe voz sobre boca
    parada, e `sincronia.md` proibe. O que fica sutil e seguro e o L: a imagem
    de quem ENTRA chega `split_q` quadros antes, enquanto ainda toca a cauda de
    quem sai — e essa cauda tem de ser SILENCIO, senao se veria a boca fechada
    de um trecho sob a voz do outro. So as emendas feitas num silencio MEDIDO
    (`saidaMedida` + `entradaMedida`) servem: a folga ali e silencio de
    verdade; emenda do diretor pode ter frase removida na folga.

    A cauda medida so guarda `margem_ms` de silencio, pouco para a janela.
    Entao a cauda cresce, tirando da propria folga removida, ate cobrir a
    janela + `SPLIT_FOLGA_CAUDA_MS`. Custa isso de pausa por emenda (~150 ms),
    e a pausa continua abaixo do que o ouvido le como buraco.

    Tudo vai para a grade de quadros: as bordas do trecho sao quadros inteiros,
    e o `cortar_aroll` fatia o audio na amostra exata de cada quadro."""
    janela_ms = _ms(split_q)
    cresce = max(0, janela_ms + SPLIT_FOLGA_CAUDA_MS - margem_ms)
    saida = [dict(t) for t in trechos]
    for i in range(1, len(saida)):
        a, b = saida[i - 1], saida[i]
        b["splitQuadros"] = 0
        if not (a.get("saidaMedida") and b.get("entradaMedida")):
            continue
        folga = b["brutoDe"] - a["brutoAte"]
        # a janela da imagem [b.de - L, b.de) tem de cair no silencio medido,
        # e a cauda crescida nao pode encostar na cabeca de b
        if folga - cresce < 60 or janela_ms > folga + margem_ms:
            continue
        a["brutoAte"] += cresce
        b["splitQuadros"] = split_q
    if saida:
        saida[0]["splitQuadros"] = 0
    for t in saida:
        # o respiro de cabeca pode empurrar o 1o trecho para antes do zero do
        # bruto (-133 ms no 20). Antes o ffmpeg engolia isso calado; no corte por
        # amostra um indice negativo virou 36 s de voz muda. Nada antes do zero.
        de, ate = max(0, _q(t["brutoDe"])), _q(t["brutoAte"])
        t["brutoDe"], t["brutoAte"] = _ms(de), _ms(ate)
    return saida


def tabela_corte(trechos):
    """no relogio do corte, contado em QUADROS e convertido no fim: somar ms
    arredondados trecho a trecho deixaria a legenda escorregar do video."""
    tab, acum = [], 0
    for t in trechos:
        q = _q(t["brutoAte"]) - _q(t["brutoDe"])
        tab.append({**t, "corteDe": _ms(acum), "corteAte": _ms(acum + q)})
        acum += q
    return tab


def cortes_visuais(tabela):
    """onde a IMAGEM troca, no relogio do corte: com o split edit, a emenda da
    imagem vem `splitQuadros` antes da emenda do som."""
    return [_ms(_q(t["corteDe"]) - t.get("splitQuadros", 0)) for t in tabela[1:]]


def bruto_para_corte(tabela, ms):
    for t in tabela:
        if t["brutoDe"] <= ms <= t["brutoAte"]:
            return t["corteDe"] + (ms - t["brutoDe"])
    # caiu numa pausa removida: o proximo trecho comeca ali
    for t in tabela:
        if ms < t["brutoDe"]:
            return t["corteDe"]
    return None


# ---------- planos --------------------------------------------------------

# Os moldes por classe sao os de `referencias/prompts-assets.md` — a linguagem
# que treinou o gerador. Cena fotografica com lente e luz, nao icone flutuando:
# a mao segurando a ficha, a plateia inteira, a parede de fichários. O
# enquadramento e cheio (full bleed 9:16), o preto vem da luz, nao de recorte.
# O molde diz a COMPOSICAO — o que ocupa o quadro e como esta enquadrado. O
# acabamento (lente, luz, material, textura) e do estilo de motion escolhido
# (`estilos.MOTION[...]["materia"]`), e um estilo pode trocar o molde de um tipo
# quando tem tratamento proprio para ele (`["moldes"]`). Antes o molde carregava
# as duas coisas, e a imagem gerada saia sempre no acabamento do `noturno`,
# qualquer que fosse o estilo escolhido.
MOLDES = {
    "objeto": ("Full bleed vertical 9:16 frame with a single object filling it, "
               "nothing else in the frame."),
    "cotidiano": ("Full bleed vertical 9:16 frame, an everyday scene caught as it is, "
                  "wide and close to the ground."),
    "personagem": ("A single human figure with no recognizable identity: no face, no "
                   "eyes, no mouth. Full bleed vertical 9:16, camera slightly below eye "
                   "level."),
    "obra": ("Full bleed vertical 9:16 reproduction of one artwork, framed as a museum "
             "piece."),
    "arquivo": ("Archival material from the period, full bleed vertical 9:16."),
}
# O ultimo bloco existe porque uma `ideia` de familia costuma nomear dois
# estados ("a mesa bagunçada, e a mesma mesa arrumada"), e o gerador obedece ao
# pe da letra: devolve um diptico antes/depois. Um plano e um quadro so.
NEGATIVOS = ("No readable text, no letters, no numbers, no labels or signage, no face of "
             "a real person, no logo, no watermark, no user interface. "
             "One single continuous scene filling the whole frame: no diptych, no split "
             "panel, no side-by-side or stacked comparison, no before-and-after, no grid "
             "of variations, no repeated copy of the same scene, no border or framing bar.")


def prompt_de_imagem(mo, materia="", moldes=None):
    """a ideia do diretor como prompt de um quadro parado: o que se ve, num
    estado so (o `estado` da familia, quando ha). O movimento e do Remotion,
    nao da imagem — por isso o `movimento` nao entra.

    `materia` e a materia do estilo de motion escolhido (`estilos.MOTION`): e
    ela que faz a imagem GERADA sair no mesmo estilo da composicao, em vez de
    sair generica e brigar com ela."""
    import re
    # Gerador de imagem erra glifo e alucina numero (ferramentas.md). Se a
    # ideia pede "paineis numerados", o gerador desenha 16 paineis com "IIII"
    # e "B". Numero e texto sao do Remotion; aqui a palavra sai do prompt.
    ideia = re.sub(r"\b(numerad[oa]s?|com n[uú]meros?|com texto|escrit[oa]s?|legív\w+)\b",
                   "", (mo.get("ideia") or ""), flags=re.I).strip()
    partes = [re.sub(r"\s{2,}", " ", ideia)]
    if mo.get("familia") and (mo.get("estado") or "").strip():
        partes.append(f"In this frame: {mo['estado'].strip()}")
    tipo = mo.get("tipo") or "objeto"
    partes.append((moldes or {}).get(tipo) or MOLDES.get(tipo, MOLDES["objeto"]))
    if materia:
        partes.append(f"Visual style, applied to everything in the frame: {materia}")
    partes.append(NEGATIVOS)
    return " ".join(x for x in partes if x)


def planos_do_guia(guia, fatos, tabela, fps=FPS):
    estilo_motion = estilos.tokens(guia, "motion")
    materia = estilo_motion.get("materia", "")
    moldes_do_estilo = estilo_motion.get("moldes") or {}
    ps, antes_de = [], []
    for m in guia["momentos"]:
        if m["decisao"] == "cortar":
            continue
        t0, t1 = bruto_para_corte(tabela, m["deMs"]), bruto_para_corte(tabela, m["ateMs"])
        if t0 is None or t1 is None or t1 <= t0:
            continue
        mo = m.get("motion") or {}
        tipo = mo.get("tipo") if m["decisao"] in COM_MOTION else "fala"
        p = {"id": m["id"], "t0": t0, "t1": t1, "duracaoMs": t1 - t0, "tipo": tipo,
             "fala": m.get("fala", ""), "texto": "", "camera": "push-in", "asset": None, "prompt": "",
             "entrada": mo.get("entrada", "corte"), "saida": mo.get("saida", "corte"),
             "ideia": mo.get("ideia", ""), "movimento": mo.get("movimento", ""),
             "porque": m.get("porque", ""), "sobreFala": m["decisao"] == "aroll+motion"}
        if mo.get("familia"):
            p["familia"], p["estado"] = mo["familia"], mo.get("estado", "")
        if m["decisao"] in COM_MOTION and mo.get("cena"):
            p["cena"] = mo["cena"]
        for k, v in (mo.get("dados") or {}).items():
            p[k] = v
        f = (fatos or {}).get(m["id"]) or {}
        for k in ("paper", "retrato"):
            if f.get(k):
                p[k] = f[k]
        if f.get("numero"):
            p["fonte"] = f["numero"].get("fonte", "")
        # o texto do quadro vem dos dados (cartela, titulo de dado) ou das
        # palavras — NUNCA da fala: repetir a fala na tela e o erro antigo
        dados = mo.get("dados") or {}
        # Os tipos desenhados JA mostram as palavras — como vertice do ceu, laje
        # da pilha, item da lista. Repeti-las no titulo escreve tudo duas vezes:
        # a galaxia saia com CACHORRO BONITO FEIO MEDO em amarelo por cima do
        # ceu que ja tinha esses quatro nomes acesos.
        DESENHAM_AS_PALAVRAS = ("galaxia", "camadas", "indice")
        p["texto"] = (dados.get("texto") or dados.get("titulo") or
                      ("" if tipo in DESENHAM_AS_PALAVRAS
                       else " ".join((p.get("palavras") or [])[:4])) or "")
        # O gerador de imagem recebe a IDEIA do diretor, nao a fala. Sem isso o
        # prompt vai vazio e o gerador inventa qualquer coisa — foi assim que
        # "dez paineis de papel creme" virou um esqueleto sentado.
        if tipo in ("objeto", "personagem", "obra", "arquivo", "cotidiano", "pessoa"):
            p["prompt"] = prompt_de_imagem(mo, materia, moldes_do_estilo)
        ps.append(p)
        antes_de.append(int(mo.get("entraAntesMs") or 0))
    # J-cut: o grafico entra antes da frase; o vizinho de tras cede o tempo
    for i, antes in enumerate(antes_de):
        if antes and i > 0:
            cede = min(antes, max(0, ps[i - 1]["duracaoMs"] - travas.MIN_VIZINHO_MS))
            ps[i]["t0"] -= cede
            ps[i]["duracaoMs"] += cede
            ps[i - 1]["t1"] -= cede
            ps[i - 1]["duracaoMs"] -= cede
    for p in ps:
        p["legenda"] = p["tipo"] not in TEM_TEXTO_PROPRIO
    return ps


# ---------- material ------------------------------------------------------

def cortar_aroll(take, tabela, recorte, edicao, altura=1920):
    """proxy na altura pedida -> pedacos com output seeking -> concat CFR.
    O metodo que provou frame-accuracy: -ss depois do -i, e -r fixo.

    `altura` existe para o master: o take de celular chega em 2160x3840 e o
    recorte 9:16 e o quadro inteiro, entao 3840 aqui e resolucao nativa, nao
    ampliacao. O proxy e o A-roll guardam a altura no nome — misturar um proxy
    de 1920 com um master de 3840 seria upscale silencioso."""
    w, h, x, y = recorte
    larg = altura * 9 // 16
    suf = "" if altura == 1920 else f"-{altura}"
    proxy = edicao / f"proxy{suf}.mp4"
    if not proxy.exists():
        # Se ja existe um proxy MAIOR, reduza a partir dele em vez de decodificar
        # o take de novo: ele ja esta cortado em 9x16, ja esta em 30 fps, e a
        # reducao custa uma fracao do que custa reabrir o 4K original. Ampliar
        # a partir de um proxy menor seria fraude de resolucao — por isso so
        # vale para baixo.
        maiores = sorted((int(f.stem.split("-")[1]) for f in edicao.glob("proxy-*.mp4")
                          if f.stem.split("-")[-1].isdigit()), reverse=True)
        fonte_proxy = next((edicao / f"proxy-{n}.mp4" for n in maiores if n > altura), None)
        if fonte_proxy:
            print(f"aroll: proxy {larg}x{altura} reduzido de {fonte_proxy.name}", flush=True)
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(fonte_proxy),
                            "-vf", f"scale={larg}:{altura}:flags=lanczos", "-r", str(FPS),
                            *acabamento.encoder(17, "fast", altura),
                            "-c:a", "copy", str(proxy)], check=True)
        else:
            print(f"aroll: proxy {larg}x{altura} do take (alguns minutos)", flush=True)
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(take),
                            "-vf", f"crop={w}:{h}:{x}:{y},scale={larg}:{altura}", "-r", str(FPS),
                            *acabamento.encoder(17, "fast", altura),
                            "-c:a", "aac", "-b:a", "192k", str(proxy)], check=True)
    # IMAGEM: um pedaco por trecho, em quadros inteiros e sem audio. Com split
    # edit, o trecho i comeca `L_i` quadros antes no bruto e termina `L_(i+1)`
    # antes: o que um perde o outro ganha, e a soma de quadros nao muda.
    # O SOM nao passa por aqui (ver abaixo).
    pedacos = edicao / f"pedacos{suf}"
    pedacos.mkdir(exist_ok=True)
    lista = []
    PRE = 2.0
    for i, t in enumerate(tabela):
        arq = pedacos / f"{i:03d}.mp4"
        L = t.get("splitQuadros", 0)
        L_prox = tabela[i + 1].get("splitQuadros", 0) if i + 1 < len(tabela) else 0
        q0 = _q(t["brutoDe"]) - L
        q1 = _q(t["brutoAte"]) - L_prox
        de = q0 / FPS
        pre = min(PRE, de)
        print(f"aroll: pedaco {i+1}/{len(tabela)} ({de:.1f}s, {q1-q0} quadros"
              f"{f', imagem {L} q antes' if L else ''})", flush=True)
        # 1 ms antes do quadro: o seek preciso pega o primeiro quadro com
        # pts >= alvo, e o quadro anterior esta 33 ms atras
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{de-pre:.4f}", "-i", str(proxy),
                        "-ss", f"{max(0, pre-0.001):.4f}", "-frames:v", str(q1 - q0), "-an",
                        *acabamento.encoder(17, "fast", altura), "-vsync", "cfr", "-r", str(FPS),
                        str(arq)], check=True)
        lista.append(f"file '{arq.resolve()}'")
    (edicao / f"lista{suf}.txt").write_text("\n".join(lista) + "\n", encoding="utf-8")
    print("aroll: concatenando a imagem", flush=True)
    imagem = edicao / f"aroll-imagem{suf}.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", str(edicao / f"lista{suf}.txt"), "-c", "copy", str(imagem)], check=True)

    # SOM: decodificado uma vez, fatiado por indice de AMOSTRA nas bordas de
    # quadro SEM o split (o audio nunca se mexe), codificado uma vez no fim.
    # Fatiar AAC pedaco a pedaco somava o padding de cada quadro de 1024
    # amostras e fazia a voz escorregar ao longo do video (`sincronia.md`).
    import numpy as np
    SR = 48000
    por_quadro = SR // FPS
    bruto = np.frombuffer(subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(proxy), "-vn", "-ac", "2", "-ar", str(SR),
         "-f", "s16le", "-"], capture_output=True, check=True).stdout, dtype=np.int16).reshape(-1, 2)
    fatias = []
    for t in tabela:
        a0, a1 = _q(t["brutoDe"]) * por_quadro, _q(t["brutoAte"]) * por_quadro
        if a0 < 0 or a1 <= a0:
            raise SystemExit(f"trecho fora do bruto ({t['brutoDe']}–{t['brutoAte']} ms): "
                             "o som sairia mudo ou fora do lugar")
        f = bruto[a0:a1]
        if len(f) < a1 - a0:                   # fim do take: completa com silencio
            f = np.vstack([f, np.zeros((a1 - a0 - len(f), 2), np.int16)])
        fatias.append(f)
    voz = np.concatenate(fatias)
    total_q = sum(_q(t["brutoAte"]) - _q(t["brutoDe"]) for t in tabela)
    assert len(voz) == total_q * por_quadro, "o som nao fecha com a imagem, amostra a amostra"
    for i, (t, f) in enumerate(zip(tabela, fatias)):
        if len(f) > SR and np.abs(f).max() < 64:       # ~ -54 dBFS de pico: mudo
            raise SystemExit(f"aroll: trecho {i+1} saiu MUDO ({t['brutoDe']}–{t['brutoAte']} ms)")
    wav = edicao / f"aroll-som{suf}.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2",
                    "-i", "-", str(wav)], input=voz.tobytes(), check=True)
    print("aroll: juntando imagem e som", flush=True)
    aroll = edicao / f"aroll{suf}.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(imagem), "-i", str(wav),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", str(aroll)], check=True)
    n_split = sum(1 for t in tabela if t.get("splitQuadros"))
    print(f"aroll: {n_split} emenda(s) com split edit — a imagem entra antes, o som fica", flush=True)
    return aroll


def _mmss(ms):
    return f"{ms // 60000}:{(ms % 60000) // 1000:02d}"


def resumo_corte(guia, tabela):
    """a tabela que o editor revisa na etapa 1: o que ficou, o que saiu e
    onde o motion entra antes da frase (J-cut). Texto, para o chat e para
    edicao/corte.md."""
    L = ["## Trechos que ficam", "", "| # | bruto | no corte | dur |", "|--:|---|---|--:|"]
    for i, t in enumerate(tabela):
        L.append(f"| {i+1} | {_mmss(t['brutoDe'])}–{_mmss(t['brutoAte'])} | "
                 f"{_mmss(t['corteDe'])}–{_mmss(t['corteAte'])} | {(t['brutoAte']-t['brutoDe'])/1000:.1f}s |")
    L += ["", "## Removido", ""]
    for m in guia["momentos"]:
        if m.get("decisao") == "cortar":
            L.append(f"- **{m['id']}** {_mmss(m['deMs'])}–{_mmss(m['ateMs'])} "
                     f"({(m['ateMs']-m['deMs'])/1000:.1f}s): {m.get('porque', '')}")
    L += ["", "## J-cuts (motion entra antes da frase)", ""]
    for m in guia["momentos"]:
        antes = int((m.get("motion") or {}).get("entraAntesMs") or 0)
        if antes:
            L.append(f"- **{m['id']}** {_mmss(m['deMs'])} — entra {antes} ms antes")
    L += ["", "Para ajustar: mude `decisao` do momento em `guia/guia.json` (`cortar` ↔ `aroll`/`motion`), "
          "ou `entraAntesMs` do motion, e rode a etapa de novo."]
    return "\n".join(L) + "\n"


def _grafia(palavra, mapa):
    """troca a palavra que o Whisper errou (`guia.grafia`, ex. {"Cloud": "Claude"}),
    mantendo a pontuacao grudada nela — a legenda nao pode escrever errado o
    nome da ferramenta que o video ensina"""
    if not mapa:
        return palavra
    nucleo = palavra.strip(".,!?…:;\"'")
    if nucleo in mapa:
        return palavra.replace(nucleo, mapa[nucleo], 1)
    return palavra


def captions(palavras, tabela, grafia=None):
    out = []
    for w in palavras:
        a, b = bruto_para_corte(tabela, w["deMs"]), bruto_para_corte(tabela, w["ateMs"])
        if a is None or b is None or b <= a:
            continue
        out.append({"text": " " + _grafia(w["palavra"], grafia), "startMs": a, "endMs": b,
                    "timestampMs": (a + b) // 2, "confidence": None})
    return out


def cama(guia, tabela, edicao, projeto):
    movs = []
    for m in guia["momentos"]:
        if m["decisao"] == "cortar":
            continue
        ate = bruto_para_corte(tabela, m["ateMs"])
        mus = m.get("musica") or {}
        movs.append({"ateS": (ate or 0) / 1000, "clima": mus.get("clima", "neutro"),
                     "cama": mus.get("cama", "mantem")})
    total = tabela[-1]["corteAte"] / 1000 if tabela else 0
    wav = edicao / "trilha.wav"
    trilha.compor(movs, total, wav, estilos.escolher(guia, "musica"))
    m4a = projeto / "public" / "trilha.m4a"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(wav), "-af", acabamento.CAMA,
                    "-c:a", "aac", "-b:a", "160k", str(m4a)], check=True)
    return m4a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--guia", required=True)
    ap.add_argument("--fatos")
    ap.add_argument("--take", required=True)
    ap.add_argument("--falas", required=True)
    ap.add_argument("--projeto", required=True)
    ap.add_argument("--edicao", required=True)
    ap.add_argument("--deslocamento", type=int, default=0)
    ap.add_argument("--so-planos", action="store_true")
    ap.add_argument("--sem-preview", action="store_true")
    ap.add_argument("--renderizador", choices=["hyperframes", "pillow"], default="hyperframes",
                    help="hyperframes: HTML+GSAP, a gramatica do treinamento (padrao) · "
                         "pillow: compor.py, sem navegador — o caminho de conserto")
    ap.add_argument("--altura", type=int, default=1920,
                    help="altura do quadro (9:16). 1920 e o preview e a entrega comum; "
                         "3840 e o master 4K, que so faz sentido quando o take chega em "
                         "2160x3840 — acima disso vira ampliacao")
    ap.add_argument("--etapa", choices=["corte", "previa", "motion", "final"], default="final",
                    help="corte: so a decupagem, para revisar · previa: a edicao como dados para "
                         "a mesa (zoom, legenda e hook ao vivo, sem render) · motion: planos + "
                         "assets + preview sem cama/legenda · final: tudo (cama, legenda, grade)")
    ap.add_argument("--sem-apertar", action="store_true",
                    help="nao tira as pausas longas entre palavras: o take sai inteiro, no "
                         "relogio original, e so os momentos `cortar` saem. Use quando o pedido "
                         "for 'sem cortar o video', ou quando a pausa for o efeito — o tempo "
                         "comico de um esquete morre se o silencio some.")
    ap.add_argument("--aceitar-hdr", action="store_true",
                    help="deixa entrar take HLG/PQ sem converter. Nao use: o corte copia o "
                         "sinal HDR para H.264 de 8 bits e a pele sai lavada — rode sdr.py")
    a = ap.parse_args()
    # antes de qualquer trabalho: take HDR do iPhone vira SDR pelo sdr.py
    sdr.exigir_sdr(a.take, a.aceitar_hdr)

    guia = json.loads(Path(a.guia).read_text(encoding="utf-8"))
    fatos = json.loads(Path(a.fatos).read_text(encoding="utf-8")) \
        if a.fatos and Path(a.fatos).exists() else {}
    erros = validar.validar(guia)
    if erros:
        print("guia invalido:")
        for e in erros:
            print(" ·", e)
        sys.exit(1)

    take, projeto, edicao = Path(a.take), Path(a.projeto), Path(a.edicao)
    edicao.mkdir(parents=True, exist_ok=True)
    (projeto / "public").mkdir(parents=True, exist_ok=True)
    palavras = tempo.carregar_palavras(a.falas)
    # pausa_max infinita = nenhuma pausa e apertada; o trecho so quebra onde o
    # diretor mandou cortar
    silencios = None if a.sem_apertar else silencios_medidos(Path(a.take),
                                                            Path(a.edicao) / "silencios.json")
    tabela = tabela_corte(split_edits(trechos_mantidos(
        guia, palavras, pausa_max_ms=float("inf") if a.sem_apertar else PAUSA_MAX_MS,
        silencios=silencios)))
    corte_json = edicao / "corte.json"
    # tudo que muda de tamanho carrega a altura no nome: um A-roll de 1920
    # reaproveitado num master de 3840 seria ampliacao passando por resolucao
    suf = "" if a.altura == 1920 else f"-{a.altura}"
    aroll_arq = edicao / f"aroll{suf}.mp4"
    nome_fonte = f"fonte{suf}.mp4"
    # o corte so e refeito quando a tabela mudou: a etapa 2 nao paga de novo
    # pela etapa 1 aprovada
    corte_mudou = not corte_json.exists() or json.loads(corte_json.read_text(encoding="utf-8")) != tabela \
        or not aroll_arq.exists()
    corte_json.write_text(json.dumps(tabela, indent=2), encoding="utf-8")
    dur = tabela[-1]["corteAte"] if tabela else 0
    (edicao / "corte.md").write_text(resumo_corte(guia, tabela), encoding="utf-8")

    if a.etapa == "corte":
        import contato as ct
        largura, altura, _ = ct.sonda(take)
        recorte = tempo.recorte_9x16(largura, altura, a.deslocamento)
        if corte_mudou:
            cortar_aroll(take, tabela, recorte, edicao, a.altura)
        revisao = edicao / "corte-revisao.mp4"
        print("corte: versao leve para revisao", flush=True)
        subprocess.run(["ffmpeg", "-y", "-nostdin", "-v", "error", "-i", str(aroll_arq),
                        "-vf", "scale=324:576", "-c:v", "libx264", "-preset", "veryfast", "-crf", "27",
                        "-c:a", "aac", "-b:a", "96k", str(revisao)], check=True)
        print(f"corte: {dur/1000:.1f}s em {len(tabela)} trecho(s) → {revisao}")
        print(resumo_corte(guia, tabela))
        return

    aprovado = edicao / "aprovado"
    if a.etapa == "motion" and not (aprovado / "corte").exists():
        print("  · aviso: o corte ainda nao foi aprovado (edicao/aprovado/corte nao existe)")
    if a.etapa == "final" and not (aprovado / "motion").exists():
        print("  · aviso: o motion ainda nao foi aprovado (edicao/aprovado/motion nao existe)")

    planos = planos_do_guia(guia, fatos, tabela)
    plano = {"versao": 2, "preset": guia.get("estilo") or "noturno", "fps": FPS,
             "largura": a.altura * 9 // 16, "altura": a.altura,
             "duracaoMs": dur, "duracaoEmFrames": tempo.ms_para_frames(dur, FPS),
             "fonteVideo": nome_fonte, "fonteAudio": "voz.m4a", "fonteOffsetMs": 0,
             "trilha": "trilha.m4a", "trilhaVolume": 0.5, "planos": planos,
             # onde a IMAGEM emenda dois trechos (no relogio do video cortado,
             # com o split edit ja descontado): o zoom de enfase volta a 1,0x ali
             "cortesMs": cortes_visuais(tabela),
             "arco": guia.get("arco", ""), "correcoes": guia.get("correcoes", [])}
    avisos = travas.aplicar_todas(plano)

    if not a.so_planos:
        import contato as ct
        largura, altura, _ = ct.sonda(take)
        recorte = tempo.recorte_9x16(largura, altura, a.deslocamento)
        aroll = cortar_aroll(take, tabela, recorte, edicao, a.altura) if corte_mudou else aroll_arq
        fonte, voz = projeto / "public" / nome_fonte, projeto / "public" / "voz.m4a"
        if corte_mudou or not fonte.exists():
            grade = cor.da_ficha(guia)
            print(f"acabamento: imagem · grade {cor.resumo(grade)}", flush=True)
            acabamento.tratar_imagem(aroll, fonte, FPS, grade)
        # a cadeia da voz leva os cortes desta voz (voz.py); mudou a cadeia,
        # refaz a voz mesmo com o corte igual
        cadeia_arq = edicao / "voz-cadeia.txt"
        cortes_voz = vozlib.cortes_para(take, Path(a.guia).resolve().parent.parent,
                                        log=lambda m: print(m, flush=True))
        cadeia = acabamento.cadeia_voz(cortes_voz)
        cadeia_mudou = not cadeia_arq.exists() or cadeia_arq.read_text(encoding="utf-8") != cadeia
        if corte_mudou or cadeia_mudou or not voz.exists():
            print("acabamento: voz (-14 LUFS)", flush=True)
            com_jcut = cortar_voz(take, tabela, jcuts_por_trecho(guia, tabela), edicao, suf)
            acabamento.tratar_voz(com_jcut or aroll, voz, cortes_voz)
            cadeia_arq.write_text(cadeia, encoding="utf-8")
        if a.etapa == "final" and not guia.get("semMusica"):
            print("cama: compondo a trilha por momento", flush=True)
            m4a = cama(guia, tabela, edicao, projeto)
            plano["trilhaVolume"] = acabamento.volume_da_cama(voz, m4a)
            print(f"cama: volume {plano['trilhaVolume']:.3f}", flush=True)
        elif a.etapa == "final":
            # `semMusica` no guia: a cama sintetica do `trilha.py` nao passa de
            # um chiado em vídeo de fala seca, e chiado atras da voz e pior que
            # silencio. Vídeo sem cama e escolha, nao esquecimento.
            print("cama: pulada (semMusica no guia)", flush=True)
            plano["trilha"] = None
            plano["trilhaVolume"] = 0.0

    if a.etapa == "motion":
        # etapa 2 mostra so o desenho: sem cama, sem legenda, sem grade. O que
        # o editor julga aqui e a ideia e o timing de cada motion.
        plano["trilha"] = None
        plano["semLegenda"] = True
        plano["semGrade"] = True
    # o hook da abertura viaja no guia e e desenhado junto da legenda: e
    # tipografia sobre o rosto, nao um momento de motion
    if guia.get("hook"):
        plano["hook"] = guia["hook"]
    # hook e legenda leem a galeria de estilos a partir do plano — nunca do
    # guia direto, porque o plano e o unico arquivo que sobrevive ate o render
    if guia.get("estilos"):
        plano["estilos"] = guia["estilos"]
    if guia.get("configLegenda"):
        plano["configLegenda"] = guia["configLegenda"]
    # a mascara Dividir e opcional (`mascara.py`): so viaja quando o guia a tem
    if guia.get("mascara"):
        plano["mascara"] = mascara.normalizar(guia["mascara"])
    # a direcao de motion e o prompt de cada cena viajam no plano para quem
    # desenha, e ficam num CENAS.md ao lado para o editor ler
    if direcao.tem_motion(guia):
        plano["direcaoMotion"] = guia.get("direcaoMotion") or {}
        prompts = {m["id"]: pr for m, pr in direcao.cenas(guia)}
        for pl in planos:
            if pl["id"] in prompts:
                pl["cenaPrompt"] = prompts[pl["id"]]
        (projeto / "CENAS.md").write_text(
            "\n".join(["# Cenas de motion", ""] + direcao.markdown(guia)),
            encoding="utf-8")
    texto = json.dumps(plano, ensure_ascii=False, indent=2)
    (projeto / "plano.json").write_text(texto, encoding="utf-8")
    (projeto / "public" / "plano.json").write_text(texto, encoding="utf-8")
    (projeto / "public" / "captions.json").write_text(
        json.dumps(captions(palavras, tabela, guia.get("grafia")), ensure_ascii=False), encoding="utf-8")

    if a.etapa == "previa":
        # para APROVAR nao se renderiza: a mesa toca o take leve e aplica zoom,
        # legenda e hook ao vivo (painel/previa.py). Pedido do dono em
        # 2026-09-27 — cada rodada de ajuste custava 30-40 min de render.
        subprocess.run([sys.executable, str(Path(__file__).resolve().parents[3] / "painel" / "previa.py"),
                        str(projeto)], check=True)
        return
    print(f"{len(planos)} planos · {dur/1000:.1f}s · corte em {len(tabela)} trecho(s)")
    for t, n in Counter(p["tipo"] for p in planos).most_common():
        print(f"  {t:<12} {n}")
    for w in avisos:
        print("  ·", w)

    if a.so_planos or a.sem_preview:
        return
    print("assets: gerando imagens dos planos", flush=True)
    subprocess.run([sys.executable, str(Path(__file__).parent / "assets.py"), "--projeto", str(projeto)],
                   check=False)
    (projeto / "out").mkdir(exist_ok=True)
    saida = projeto / "out" / ("motion.mp4" if a.etapa == "motion" else "preview.mp4")
    base_pronta = None
    if a.renderizador == "hyperframes":
        # Cada plano de motion vira um HTML na gramatica do treinamento e sai
        # como clip proprio; o `montador.py` costura os clips com o A-roll.
        print("motion: renderizando os planos em HyperFrames", flush=True)
        subprocess.run([sys.executable, str(Path(__file__).parent / "hf.py"),
                        "--projeto", str(projeto)], check=True)
        # trecho de video de terceiro entra DEPOIS do hf.py: o HTML desenha a
        # pagina com a janela vazia, e o ffmpeg encaixa o material citado nela
        print("acervo: trechos de terceiro nas cenas que pedem", flush=True)
        subprocess.run([sys.executable, str(Path(__file__).parent / "acervo.py"),
                        "--projeto", str(projeto)], check=False)
        print("costura: clips de motion + A-roll", flush=True)
        subprocess.run([sys.executable, str(Path(__file__).parent / "montador.py"),
                        "--projeto", str(projeto), "--out", str(saida),
                        "--legenda", "nao" if a.etapa == "motion" else "sim"], check=True)
        base_pronta = projeto / "out" / "costura" / "_video.mp4"
    else:
        print(f"preview: compondo em 0.3x → {saida.name}", flush=True)
    if a.renderizador == "hyperframes" and plano.get("semLegenda") and plano.get("hook"):
        # A etapa `motion` julga desenho, nao leitura — por isso sem legenda.
        # Mas o GANCHO nao e leitura: e a abertura, o trecho que decide se
        # alguem fica. Ele ficava invisivel ate o `finalizar`, e o editor
        # aprovava o motion sem nunca ter visto os primeiros segundos como o
        # publico vai ver. Agora ele vem junto, e so ele.
        print("hook: desenhando o gancho da abertura", flush=True)
        subprocess.run([sys.executable, str(Path(__file__).parent / "legenda_hf.py"),
                        "--projeto", str(projeto), "--so-hook",
                        "--saida", str(projeto / "out" / "hook.webm")], check=True)
    if a.renderizador == "hyperframes" and not plano.get("semLegenda"):
        # A legenda sai da mesma gramatica dos planos: HTML, fonte web, kerning,
        # sombra macia. Chega como WebM com alpha e o compor sobrepoe no lugar
        # da faixa que o Pillow desenhava quadro a quadro.
        print("legenda: desenhando em HyperFrames", flush=True)
        subprocess.run([sys.executable, str(Path(__file__).parent / "legenda_hf.py"),
                        "--projeto", str(projeto), "--escala", "0.3"], check=True)
    # O preview sai pelo compositor do plugin (Pillow + ffmpeg): sem navegador,
    # sem webpack, sem antivirus no caminho. O Remotion continua disponivel
    # (`npx remotion render`), mas nao e mais o caminho padrao.
    #
    # Quando o render foi em HyperFrames, o quadro JA ESTA PRONTO e o compositor
    # entra so para legenda, som e grade (`--base`). Antes ele rodava aqui sem
    # condicao nenhuma, com o mesmo `--out`, e redesenhava tudo em Pillow a
    # 0,3x por cima do master: 1080x1920 as 23:40:52 viravam 324x576 as 23:41:04,
    # com as cenas que o Pillow nao sabe desenhar (`camadas`, `indice`) pretas.
    cmd_compor = [sys.executable, str(Path(__file__).parent / "compor.py"),
                  "--projeto", str(projeto), "--out", str(saida)]
    cmd_compor += (["--base", str(base_pronta), "--crf", "18"]
                   if base_pronta and base_pronta.exists()
                   else ["--escala", "0.3", "--crf", "28"])
    subprocess.run(cmd_compor, check=True)
    if a.etapa == "motion":
        print(f"motion: {saida} — reveja momento a momento (GUIA.md tem a ideia de cada um)")
        return
    erros = medir.avaliar(saida, plano, projeto / "public" / "voz.m4a",
                          projeto / "public" / "trilha.m4a", plano["trilhaVolume"])
    # O teste de imagem do `medir` compara pixel, e no master a grade e o zoom
    # achatam a correlacao: nos 19 e 20 (2026-09-27) ele deu "3 quadros" num
    # master certo e deixou passar 5 quadros num master errado. A energia de
    # movimento nao liga para cor nem escala — ela decide (sincronia.md).
    if a.etapa == "final" and (edicao / "aroll.mp4").exists():
        import conferir_movimento
        _, _, lags = conferir_movimento.lags(saida, edicao / "aroll.mp4")
        pior = max(map(abs, lags)) if lags else None
        print(f"imagem x montagem (movimento): {len(lags)} janela(s), pior {pior} quadro(s)")
        if not lags:
            erros.append("sincronia de imagem: nenhuma janela de movimento valida — confira a olho")
        elif pior:
            erros.append(f"sincronia de imagem: {pior} quadro(s) de desvio contra o aroll.mp4")
    for e in erros:
        print("  ✗", e)
    print("medicao: " + ("FALHOU — nao esta pronto" if erros else "ok — preview medido"))
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
