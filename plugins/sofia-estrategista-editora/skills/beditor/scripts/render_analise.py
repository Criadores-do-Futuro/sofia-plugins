"""O master do formato `analise`, por SEGMENTOS, em paralelo, com cache de conteúdo.

    python3 render_analise.py <projeto/> [--paralelo N] [--revisao] [--entrega N]
                              [--recodificar] [--limpar]

Lê `edicao/dados.json` (takes, palavras, tabela do corte — o que `silencio.py`
escreve) e `edicao/plano.json` (fontes, cartões, marcadores, hook, cama), e
escreve `edicao/master.mp4`, `edicao/provas.json` e `edicao/oficina/manifesto.json`.

O que mudou em relação ao render de projeto (render14/render15), e por quê:

  UM PROCESSO, 4 591 PNGs, RECODIFICAÇÃO INTEIRA
    Cada quadro era composto num laço sequencial, salvo em PNG, e no fim o
    ffmpeg lia os 4 591 arquivos e codificava o vídeo inteiro. Todo ajuste —
    «abaixa a música 20%», «conserta o insert de 1:48» — pagava os 10 minutos
    inteiros de novo. No 15 esse render rodou 32 vezes; no 14, 58.

  AGORA: SEGMENTOS COM CHAVE DE CONTEÚDO
    A linha do tempo é partida em segmentos de até 2 s, quebrando onde alguma
    camada muda (entra cartão, sai marcador, troca de take). Cada segmento tem
    uma RECEITA — tudo que decide o pixel de cada quadro dele: qual quadro do
    A-roll, qual enquadramento, qual cartão em qual fase, qual legenda — e a
    chave do segmento é o hash dessa receita mais o hash do código que desenha.
    O segmento é codificado UMA vez, para `oficina/seg/<chave>.mp4`. O master é
    a concatenação dos segmentos SEM recodificar (`-c copy`): quem não mudou
    não é tocado. Mudar a música refaz zero segmentos. Consertar um insert de
    2,4 s refaz dois.

  PARALELO
    Os segmentos são independentes, então vão para N processos (padrão: núcleos
    − 2, teto 8 — o teto é de memória). Cada processo compõe em Pillow e
    entrega os quadros crus ao seu próprio ffmpeg por um pipe: nenhum PNG toca o
    disco. O erro «png chunk too big» que apareceu no 15 vem daí e sumiu.

  O ÁUDIO TEM CACHE PRÓPRIO
    A voz do corte (PCM, amostra a amostra, uma codificação) tem chave pela
    tabela e pelos takes; a mistura tem chave pela voz mais a cama. Trocar o
    ganho da música refaz só a mistura — 3 s — e reaproveita todos os segmentos
    de imagem.

  A ENTREGA NÃO RECODIFICA
    `--entrega N` gera a capa (quadro limpo N) como um segmento a mais, com os
    mesmos parâmetros de codificação, e concatena capa + corpo. O corpo passa
    pelo x264 zero vezes a mais. No 14, a entrega recodificava tudo: 18 min.

O que NÃO mudou: as camadas, a ordem delas, as funções de `cartao.py`, o corte
L, a tarja medida uma vez por clipe, a cauda como evento — tudo o que foi
aprovado nos vídeos 14 e 15 é chamado daqui do mesmo jeito. Este script é o
mesmo desenho com outra logística.

Formato de `plano.json` (tempos em segundos da linha virtual, como sempre):

  {"fontes": {"trailer": {"arq": "...mp4", "url":..., "titulo":..., "autor":..., "data":..., "tipo": "prova"},
              "manchetes": {"arq": "acervo/manchetes_popup", ...}            ← pasta de PNG
              "logo": {"arq": "acervo/claude-logo-alpha.png", ...}},          ← PNG com alfa
   "popups": {"manchetes_popup": {"itens": [...], "dur": 3.8, "cada": 1.55}}, ← desenhados aqui, se não existirem
   "plano": {"M01": [{"fonte": "trailer", "src": 19.3, "dur": 1.2, "de": 5.15, "ate": 6.33, "modo": 1, "porque": "..."},
                     {"tipo": "frase", "de":..., "ate":..., "linhas": [...], "destaque": 0, "porque": "..."},
                     {"tipo": "triptico", "de":..., "ate":..., "paineis": [["morbius", 90.0, 1.4], ...], "porque": "..."},
                     {"tipo": "logo", "fonte": "logo", "de":..., "ate":..., "porque": "..."}]},
   "marcadores": [{"n": 1, "nome": "...", "de": 202.1, "ate": 203.8}],
   "hook": {"ateMs": 3000, "linhas": [...], "destaque": 2, "fonte": "trailer", "src": 94.4, "alto": 0.58, "suavizar": 0.30},
   "musicas": {"vi": {"arq": "...m4a", "src": 8.0, "url":..., "titulo":..., "autor":..., "tipo": "trilha"}},
   "trilha": [["M01", "vi"], ["M09", "v"]], "cruzada": 1.4, "ganho": 0.034,
   "grafias": {"Samadri": "San Andreas"}, "semCartao": [{"momento":..., "fala":..., "porque":...}]}

Caminhos relativos em `arq` são resolvidos a partir da pasta do projeto.
"""
import argparse
import bisect
import json
import math
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import acabamento  # noqa: E402
import cartao   # noqa: E402
import oficina  # noqa: E402
import visao    # noqa: E402
from oficina import FPS, H, SR, W  # noqa: E402

L_ALVO, L_MIN = 240, 140        # o corte L: alvo e mínimo, em ms
ENCOSTA = 700                   # cartão marcado até isto antes do pedaço encosta nele
TETO_LEGENDA = 1500             # grupo de legenda a mais que isto da borda é descartado
ABRE, FECHA = 0.40, 0.35        # a janela do modo 4
SEG_MAX = 60                    # quadros por segmento (2 s): granularidade da cache
CAPA_MS = 800

# Os mesmos parâmetros em TODO segmento e na capa: é isso que permite concatenar
# com `-c copy`. Mudar aqui invalida a cache inteira (a chave inclui esta lista).
ENC = ["-c:v", "libx264", "-crf", "15", "-preset", "medium", "-profile:v", "high",
       "-level", "4.2", "-x264-params", "ref=4:bframes=3", "-pix_fmt", "yuv420p",
       "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
       "-video_track_timescale", "15360"]

def _versao():
    """Hash do código que DESENHA: cartao.py inteiro e, deste arquivo, só o que compõe.

    Se a chave incluísse este arquivo inteiro, cada ajuste na logística (um
    print, um parâmetro de linha de comando) jogaria fora 98 segmentos prontos.
    O que decide o pixel é `compor` e `_matte` mais o `cartao.py`; é isso que entra.
    """
    import hashlib
    import inspect
    h = hashlib.sha1(Path(cartao.__file__).read_bytes())
    h.update(inspect.getsource(compor).encode())
    h.update(inspect.getsource(_matte).encode())
    return h.hexdigest()[:12]


def funcoes_do_segmento(recs):
    """Quais funções do `cartao.py` as receitas deste segmento chamam em `compor`.

    Tem de espelhar `compor` linha a linha: uma função chamada lá e esquecida
    aqui faria um ajuste nela não refazer o segmento. O teste
    `test_render_cache` confere o espelho.
    """
    usa = {"tipografia", "enquadrar_fixo"}
    for r in recs:
        if r["hook"]:
            usa.add("hook_banda")
        elif r["cartao"]:
            usa.add({"frase": "frase_hook", "triptico": "com_triptico", "logo": "logo_atras"}
                    .get(r["cartao"]["tipo"], "compor"))
        if r["marc"]:
            usa.add("marcador")
        if r["leg"]:
            usa.add("legenda")
    return sorted(usa)


def versao_do_segmento(recs):
    """A chave de código de UM segmento: só o que o desenha (ver `oficina.assinatura`)."""
    import inspect
    # "matte" é o MOTOR, não o código do _matte: trocar Vision por portátil muda o
    # pixel e tem que refazer; mexer no encanamento que chama o motor, não.
    return oficina.chave({"cartao": oficina.assinatura(cartao, funcoes_do_segmento(recs)),
                          "compor": inspect.getsource(compor), "matte": visao.motor()})


DESENHO = ("tipografia", "enquadrar_fixo", "hook_banda", "frase_hook", "com_triptico",
           "logo_atras", "compor", "marcador", "legenda")


def prestar_contas(of, segs, refazer):
    """Diz, ANTES de compor, por que cada trecho vai ser refeito — e grava o estado.

    A regra «ajuste não refaz o vídeo inteiro» já estava escrita antes e mesmo
    assim o 16 recompôs 111 trechos por causa de dois títulos: a chave era o
    arquivo de código inteiro. Regra escrita não garante nada; o que garante é
    a máquina mostrar a conta de cada rodada. Aqui ela mostra quais funções de
    desenho mudaram desde a rodada anterior e quantos trechos cada motivo custa.
    """
    arq = of / "assinaturas.json"
    antes = json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {}
    agora = {f: oficina.assinatura(cartao, [f]) for f in DESENHO}
    mudadas = {f for f, v in agora.items() if f in antes and antes[f] != v}
    primeira = not antes
    por_codigo = [s for s in refazer if mudadas & set(funcoes_do_segmento(s))]
    if primeira:
        print("cache: primeira rodada com esta chave — tudo é composto uma vez", flush=True)
    elif mudadas:
        print(f"código de desenho mudou em: {', '.join(sorted(mudadas))} → "
              f"{len(por_codigo)} de {len(segs)} trechos", flush=True)
    else:
        print("código de desenho não mudou desde a última rodada", flush=True)
    if not primeira and len(refazer) > len(por_codigo):
        print(f"{len(refazer) - len(por_codigo)} trecho(s) refeitos por mudança no corte, "
              f"no plano ou nos insumos", flush=True)
    arq.write_text(json.dumps(agora, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"mudadas": sorted(mudadas), "porCodigo": len(por_codigo), "refeitos": len(refazer),
            "total": len(segs)}


# ---------------------------------------------------------------------------
# leitura do projeto
# ---------------------------------------------------------------------------
def carregar(projeto):
    P = Path(projeto).resolve()
    ed = P / "edicao"
    d = json.loads((ed / "dados.json").read_text(encoding="utf-8"))
    plano = json.loads((ed / "plano.json").read_text(encoding="utf-8"))

    def caminho(s):
        if str(s).startswith("midia:"):        # item da midiateca compartilhada
            return oficina.pasta("midia") / str(s)[len("midia:"):]
        p = Path(s)
        return p if p.is_absolute() else (P / p)

    for f in plano["fontes"].values():
        f["arq"] = str(caminho(f["arq"]))
    for m in plano.get("musicas", {}).values():
        m["arq"] = str(caminho(m["arq"]))
    takes = {k: {"arq": str(caminho(v["arq"])), "offsetMs": v["offsetMs"],
                 "ident": oficina.identidade(caminho(v["arq"]))}
             for k, v in d["takes"].items()}
    return {"P": P, "ed": ed, "of": ed / "oficina", "d": d, "plano": plano, "takes": takes,
            "tabela": d["tabela"]}


class Linha:
    """A linha do tempo: bruto virtual ↔ corte, e qual take é dono de cada instante."""

    def __init__(self, tabela, takes):
        self.tab = tabela
        self.takes = takes
        self.total = tabela[-1]["corteAte"]

    def local(self, b_ms, take):
        return (b_ms - self.takes[take]["offsetMs"]) / 1000.0

    def take_de(self, b_ms):
        for t in self.tab:
            if t["brutoDe"] <= b_ms <= t["brutoAte"]:
                return t["take"]
        return self.tab[-1]["take"]

    def bruto2corte(self, b):
        for t in self.tab:
            if t["brutoDe"] <= b <= t["brutoAte"]:
                return t["corteDe"] + (b - t["brutoDe"])
        return None

    def corte2bruto(self, c):
        for t in self.tab:
            if t["corteDe"] <= c <= t["corteAte"]:
                return t["brutoDe"] + (c - t["corteDe"])
        return self.tab[-1]["brutoAte"]

    def entrada(self, b):
        """Onde um cartão COMEÇA, tolerando a fronteira que o corte mexeu (ver render15)."""
        c = self.bruto2corte(b)
        if c is not None:
            return c
        seg = [t for t in self.tab if t["brutoDe"] >= b]
        if seg:
            t = min(seg, key=lambda x: x["brutoDe"])
            if t["brutoDe"] - b <= ENCOSTA:
                return t["corteDe"]
        return None

    def para_corte(self, b, fim=False, teto=TETO_LEGENDA):
        """Tempo do corte de um instante do bruto, encostando na borda mais próxima NO BRUTO."""
        c = self.bruto2corte(b)
        if c is not None:
            return c
        if fim:
            ant = [t for t in self.tab if t["brutoAte"] <= b]
            if ant:
                t = max(ant, key=lambda x: x["brutoAte"])
                if b - t["brutoAte"] <= teto:
                    return t["corteAte"]
            return None
        seg = [t for t in self.tab if t["brutoDe"] >= b]
        if seg:
            t = min(seg, key=lambda x: x["brutoDe"])
            if t["brutoDe"] - b <= teto:
                return t["corteDe"]
        return None

    def quando(self, mid):
        for t in self.tab:
            if t["momento"] == mid:
                return t["corteDe"] / 1000
        return 0.0

    def split_edits(self):
        """Carimba `splitEditMs` em cada linha que pode pagar o corte L."""
        n = 0
        for t in self.tab:
            t["splitEditMs"] = 0
        for t in self.tab[1:]:
            if not t.get("folgaLimpa"):
                continue
            L = min(L_ALVO, t["folgaMs"] - 60, t.get("caudaCaladaMs", 0) - 40)
            if L >= L_MIN:
                t["splitEditMs"] = int(L)
                n += 1
        return n

    def dono_do_quadro(self, tc):
        """(take, ms local) da IMAGEM no instante `tc` do corte — com o corte L aplicado."""
        for i, t in enumerate(self.tab):
            if t["corteDe"] <= tc < t["corteAte"] or (i == len(self.tab) - 1 and tc >= t["corteDe"]):
                if i + 1 < len(self.tab):
                    prox = self.tab[i + 1]
                    L = prox.get("splitEditMs", 0)
                    if L and tc >= prox["corteDe"] - L:
                        return prox["take"], self.local(prox["brutoDe"] - (prox["corteDe"] - tc), prox["take"]) * 1000
                return t["take"], self.local(t["brutoDe"] + (tc - t["corteDe"]), t["take"]) * 1000
        t = self.tab[-1]
        return t["take"], self.local(t["brutoAte"], t["take"]) * 1000


# ---------------------------------------------------------------------------
# insumos com cache: rosto, A-roll, clipes, pop-ups
# ---------------------------------------------------------------------------
def rosto_do_take(cfg, nome):
    tk = cfg["takes"][nome]
    # o nome da cache carrega o motor fora do Vision: rosto de outro motor é outra medida
    sufixo = "" if visao.motor() == "vision" else f"-{visao.motor()}"
    p = cfg["of"] / "rosto" / f"{nome}-{tk['ident']}{sufixo}.json"
    if not p.exists():
        visao.rastrear_rosto(tk["arq"], p)
    r = json.loads(p.read_text(encoding="utf-8"))
    return r if isinstance(r, list) else list(r.values())[0]


def pasta_aroll(cfg, nome):
    tk = cfg["takes"][nome]
    return cfg["of"] / "aroll" / f"{nome}-{tk['ident']}"


def extrair_aroll(cfg, linha, paralelo):
    """Um JPEG por quadro do A-roll, nomeado pelo QUADRO LOCAL do take.

    Nome por quadro local (não por posição no corte) é o que faz a cache
    sobreviver a um corte que muda: mexer numa emenda não move nenhum arquivo.
    A janela de cada linha começa `splitEditMs` antes, que é de onde o corte L
    puxa a imagem.
    """
    pedidos = []
    for t in linha.tab:
        pasta = pasta_aroll(cfg, t["take"])
        pasta.mkdir(parents=True, exist_ok=True)
        de_s = linha.local(t["brutoDe"] - t.get("splitEditMs", 0), t["take"])
        ate_s = linha.local(t["brutoAte"], t["take"])
        q0, q1 = int(round(de_s * FPS)), int(round(ate_s * FPS))
        if (pasta / f"{q0:06d}.jpg").exists() and (pasta / f"{q1:06d}.jpg").exists():
            continue
        pedidos.append((cfg["takes"][t["take"]]["arq"], de_s, ate_s - de_s + 1.5 / FPS, q0, pasta))

    def um(p):
        arq, de_s, dur, q0, pasta = p
        oficina.ffmpeg("-ss", f"{de_s:.3f}", "-i", arq, "-t", f"{dur:.3f}",
                       "-vf", f"scale={W}:{H},fps={FPS}", "-q:v", "2",
                       "-start_number", str(q0), str(pasta / "%06d.jpg"))
        return 1

    _, erros = oficina.paralelo(um, pedidos, n=min(4, paralelo), processos=False)
    if erros:
        raise RuntimeError(f"A-roll: {erros}")
    indices = {}
    for nome in cfg["takes"]:
        pasta = pasta_aroll(cfg, nome)
        indices[nome] = sorted(int(p.stem) for p in pasta.glob("*.jpg"))
    return len(pedidos), indices


def quadro_aroll(cfg, indices, take, local_ms):
    """O JPEG do A-roll em quadro no instante local; nunca devolve nada.

    Piso, não `round`: um corte que começa no meio de um quadro (5150 ms a
    30 fps = 154,5) cai em x,5 a cada quadro, e o `round` do Python arredonda
    meio para o PAR — 154,5→154, 155,5→156, 156,5→156. Metade dos quadros
    repetia e o trecho saía a 15 fps (vídeo 16, 2026-09-15, os 4 s de abertura).
    """
    q = int(math.floor(local_ms / 1000 * FPS + 1e-6))
    idx = indices[take]
    i = bisect.bisect_left(idx, q)
    cands = [idx[j] for j in (i - 1, i) if 0 <= j < len(idx)]
    q = min(cands, key=lambda x: abs(x - q))
    return str(pasta_aroll(cfg, take) / f"{q:06d}.jpg")


def pasta_clipe(cfg, fonte, src, dur):
    f = cfg["plano"]["fontes"][fonte]
    return cfg["of"] / "clipe" / f"{fonte}-{oficina.identidade(f['arq'])}-{src:g}-{dur:g}"


def extrair_clipes(cfg, pedidos, paralelo):
    """Os quadros de cada trecho de acervo, em paralelo, só os que faltam."""
    falta = []
    for fonte, src, dur in dict.fromkeys(pedidos):
        f = cfg["plano"]["fontes"][fonte]
        arq = Path(f["arq"])
        if arq.is_dir() or arq.suffix.lower() == ".png":
            continue
        alvo = pasta_clipe(cfg, fonte, src, dur)
        if not alvo.exists() or not any(alvo.glob("*.jpg")):
            total = oficina.sonda(arq)["dur"]
            if src + dur > total + 0.05:
                raise SystemExit(f"{fonte}: pediu {src:g}+{dur:g} s e o clipe tem {total:.2f} s — "
                                 f"confira o trecho com varrer.py/lupa.py antes de fixar o src")
            falta.append((str(arq), src, dur, alvo))

    def um(p):
        arq, src, dur, alvo = p
        tmp = alvo.with_suffix(".parcial")
        tmp.mkdir(parents=True, exist_ok=True)
        oficina.ffmpeg("-ss", str(src), "-i", arq, "-t", str(dur),
                       "-vf", f"scale=960:-2,fps={FPS}", "-q:v", "2", str(tmp / "%04d.jpg"))
        tmp.rename(alvo)
        return 1

    _, erros = oficina.paralelo(um, falta, n=min(4, paralelo), processos=False)
    if erros:
        raise RuntimeError(f"clipes: {erros}")
    return len(falta)


def quadros_de(cfg, fonte, src, dur):
    f = cfg["plano"]["fontes"][fonte]
    arq = Path(f["arq"])
    if arq.is_dir():
        return sorted(str(p) for p in arq.glob("*.png"))
    if arq.suffix.lower() == ".png":
        return [str(arq)]
    return sorted(str(p) for p in pasta_clipe(cfg, fonte, src, dur).glob("*.jpg"))


def desenhar_popups(cfg):
    """Pop-ups de prova social desenhados em código, uma vez por conteúdo."""
    n = 0
    for nome, spec in cfg["plano"].get("popups", {}).items():
        k = oficina.chave({"itens": spec["itens"], "dur": spec["dur"], "cada": spec["cada"], "v": VERSAO})
        pasta = cfg["of"] / "popup" / f"{nome}-{k}"
        if not pasta.exists():
            tmp = pasta.with_suffix(".parcial")
            tmp.mkdir(parents=True, exist_ok=True)
            for i in range(int(spec["dur"] * FPS)):
                cartao.prova_social_popup(spec["itens"], i / FPS, cada=spec["cada"]).save(tmp / f"{i+1:04d}.png")
            tmp.rename(pasta)
            n += 1
        cfg["plano"]["fontes"].setdefault(nome, {"tipo": "prova social"})["arq"] = str(pasta)
    return n


# ---------------------------------------------------------------------------
# as receitas: o que decide o pixel de cada quadro, sem desenhar nada
# ---------------------------------------------------------------------------
def montar_cartoes(cfg, linha, indices_clipe_fn):
    plano = cfg["plano"]
    cartoes = []
    for mid, cs in plano["plano"].items():
        for j, c in enumerate(cs):
            ch = f"{mid}_{j}"
            tipo = c.get("tipo", "clipe")
            a = linha.entrada(c["de"] * 1000)
            if a is None:
                print(f"  !! {ch} começa fora do corte, pulado", flush=True)
                continue
            b = min(a + (c["ate"] - c["de"]) * 1000, linha.total)
            item = {**c, "chave": ch, "tipo": tipo, "de": a, "ate": b}
            if tipo == "triptico":
                item["paineis_plano"] = [list(p) for p in c["paineis"]]
                item["paineis"] = [cartao.ate_o_corte(indices_clipe_fn(f, s, d)) for f, s, d in c["paineis"]]
                item["tarjas"] = [cartao.tarja_de(q) for q in item["paineis"]]
                print("   painéis: " + " · ".join(f"{f}@{s:g}s {len(q)/FPS:.2f}s"
                      for (f, s, _), q in zip(c["paineis"], item["paineis"])), flush=True)
            elif tipo == "logo":
                item["logo"] = plano["fontes"][c["fonte"]]["arq"]
            elif tipo == "clipe":
                qs = indices_clipe_fn(c["fonte"], c["src"], c["dur"])
                if not qs:
                    raise SystemExit(f"{ch}: nenhum quadro em {c['fonte']}@{c['src']}")
                item["quadros"] = qs
                item["tarja"] = cartao.tarja_de(qs) if not qs[0].endswith(".png") else None
            cartoes.append(item)
    cartoes.sort(key=lambda c: c["de"])
    return cartoes


def receitas(cfg, linha, indices, cartoes, marcs, legendas, hookq, quadros_take, rostos, base):
    """Uma receita por quadro. Só números e caminhos: nada aqui abre imagem."""
    NQ = int(linha.total / 1000 * FPS)
    HOOK = cfg["plano"].get("hook") or {"ateMs": 0}
    # o registro tipografico vem de `dados.estilos.legenda` (`minusculo`, o padrao
    # desde 2026-09-15, ou `explicativo`, o anterior). Vai em cada receita porque
    # os processos que compoem nao herdam o estado deste — e porque mudar o
    # registro tem de mudar a chave do segmento.
    tipografia = (cfg["d"].get("estilos") or {}).get("legenda") or "minusculo"
    if tipografia not in ("minusculo", "explicativo"):
        tipografia = "minusculo"
    out = []
    ci = mi = li = 0
    for n in range(1, NQ + 1):
        tc = (n - 1) / FPS * 1000
        tk, loc = linha.dono_do_quadro(tc)
        r = {"n": n, "take": tk, "aroll": quadro_aroll(cfg, indices, tk, loc), "tipografia": tipografia,
             "q": quadros_take[tk], "hook": None, "cartao": None, "marc": None, "leg": None}
        if tc < HOOK["ateMs"]:
            k = min(len(hookq) - 1, int(tc / 1000 * FPS))
            r["hook"] = {"quadro": hookq[k], "linhas": HOOK["linhas"], "destaque": HOOK.get("destaque", 0),
                         "rosto": cartao.rosto_em(rostos[tk], loc / 1000),
                         "suavizar": HOOK.get("suavizar", 0.30), "alto": HOOK.get("alto", 0.58)}
        while ci < len(cartoes) and cartoes[ci]["ate"] <= tc:
            ci += 1
        at = cartoes[ci] if ci < len(cartoes) and cartoes[ci]["de"] <= tc < cartoes[ci]["ate"] else None
        alt_legenda = 0.63
        if at and not r["hook"]:
            dur = (at["ate"] - at["de"]) / 1000
            u = (tc - at["de"]) / 1000
            c = {"chave": at["chave"], "tipo": at["tipo"], "u": round(u, 4), "dur": round(dur, 4)}
            if at["tipo"] == "frase":
                c.update(linhas=at["linhas"], destaque=at.get("destaque", 0), altura=at.get("altura", 0.30))
            elif at["tipo"] == "triptico":
                c["paineis"] = [p[min(len(p) - 1, int(u * FPS))] for p in at["paineis"]]
                c["tarjas"] = at["tarjas"]
                alt_legenda = 0.82
            elif at["tipo"] == "logo":
                c["logo"] = at["logo"]
            else:
                k = min(len(at["quadros"]) - 1, int(u * FPS))
                c.update(quadro=at["quadros"][k], tarja=at.get("tarja"), modo=at["modo"])
                if at["modo"] == 4:
                    c["fase"] = -1 + u / ABRE if u < ABRE else (1 + (u - (dur - FECHA)) / FECHA if u > dur - FECHA else 0.5)
                else:
                    # a altura da legenda depende do cartão: medida aqui, uma vez por quadro
                    with Image.open(c["quadro"]) as im:
                        if im.mode != "RGBA" and c["tarja"]:
                            im = im.crop(c["tarja"])
                        alt_legenda = max(0.63, cartao.base_do_cartao(at["modo"], im) + 0.06)
            r["cartao"] = c
        while mi < len(marcs) and marcs[mi]["ateC"] <= tc:
            mi += 1
        mk = marcs[mi] if mi < len(marcs) and marcs[mi]["deC"] <= tc < marcs[mi]["ateC"] else None
        if mk and not r["hook"]:
            r["marc"] = {"n": mk["n"], "nome": mk["nome"], "u": round((tc - mk["deC"]) / (mk["ateC"] - mk["deC"]), 4),
                         "dur": round((mk["ateC"] - mk["deC"]) / 1000, 4)}
        if not r["hook"]:
            while li < len(legendas) and legendas[li]["ate"] < tc:
                li += 1
            g = legendas[li] if li < len(legendas) and legendas[li]["de"] <= tc <= legendas[li]["ate"] else None
            if g:
                # a caixa (alta ou baixa) e decisao do registro tipografico, no cartao.py
                r["leg"] = {"txt": g["texto"].rstrip(",;"), "alt": round(min(alt_legenda, 0.84), 3)}
        out.append(r)
    return out


def segmentar(recs):
    """Segmentos de até SEG_MAX quadros, quebrando onde uma camada entra ou sai."""
    def assinatura(r):
        return (r["take"], bool(r["hook"]), r["cartao"]["chave"] if r["cartao"] else None,
                r["marc"]["n"] if r["marc"] else None)
    segs, atual = [], []
    for r in recs:
        if atual and (len(atual) >= SEG_MAX or assinatura(r) != assinatura(atual[-1])):
            segs.append(atual)
            atual = []
        atual.append(r)
    if atual:
        segs.append(atual)
    return segs


# ---------------------------------------------------------------------------
# o trabalhador: compõe um segmento e entrega ao ffmpeg por pipe
# ---------------------------------------------------------------------------
_W = {}


def _init(base, matte_dir):
    cartao.BASE_MODO1 = base
    _W["matte"] = Path(matte_dir)
    _W["matte"].mkdir(parents=True, exist_ok=True)
    _W["logos"] = {}


def _matte(aroll, base_img):
    """O recorte do autor, por quadro do A-roll — cache por arquivo do A-roll e motor."""
    prefixo = "" if visao.motor() == "vision" else f"{visao.motor()}-"
    mp = _W["matte"] / (prefixo + Path(aroll).parent.name + "-" + Path(aroll).stem + ".png")
    if not mp.exists():
        bp = mp.with_suffix(".jpg")
        base_img.save(bp, quality=95)
        visao.recortar(bp, mp)
        bp.unlink(missing_ok=True)
        _W["mattes"] = _W.get("mattes", 0) + 1
    return str(mp)


def compor(r):
    cartao.tipografia(r.get("tipografia", "minusculo"))
    base = cartao.enquadrar_fixo(Image.open(r["aroll"]), r["q"])
    if r["hook"]:
        h = r["hook"]
        im = cartao.hook_banda(base, Image.open(h["quadro"]), h["linhas"], h["destaque"], h["rosto"],
                               suavizar=h["suavizar"], alto=h["alto"])
    elif r["cartao"]:
        c = r["cartao"]
        if c["tipo"] == "frase":
            im = cartao.frase_hook(base, c["linhas"], c["destaque"], c["u"] / c["dur"], c["dur"],
                                   altura=c.get("altura", 0.30))
        elif c["tipo"] == "triptico":
            im = cartao.com_triptico(base, [Image.open(p) for p in c["paineis"]], c["u"], tarjas=c["tarjas"])
        elif c["tipo"] == "logo":
            logo = _W["logos"].get(c["logo"]) or _W["logos"].setdefault(c["logo"], Image.open(c["logo"]))
            im = cartao.logo_atras(base, logo, c["u"] / c["dur"], c["dur"], matte_png=_matte(r["aroll"], base))
        else:
            clipe = Image.open(c["quadro"])
            if clipe.mode != "RGBA" and c.get("tarja"):
                clipe = clipe.crop(tuple(c["tarja"]))
            if c["modo"] == 4:
                im = cartao.compor(base, clipe, 4, fase=c["fase"])
            elif c["modo"] == 1:
                im = cartao.compor(base, clipe, 1, matte_png=_matte(r["aroll"], base))
            else:
                im = cartao.compor(base, clipe, c["modo"])
    else:
        im = base
    if r["marc"]:
        m = r["marc"]
        im = cartao.marcador(im, m["n"], m["nome"], m["u"], m["dur"])
    if r["leg"]:
        im = cartao.legenda(im, r["leg"]["txt"], altura=r["leg"]["alt"], px=64)
    return im.convert("RGB")


def render_segmento(job):
    """job = (destino, receitas). Compõe e codifica; devolve (destino, quadros, mattes)."""
    destino, recs = job
    tmp = destino.with_suffix(".parcial.mp4")
    # cada x264 com 2 threads: são N processos ao mesmo tempo, e N × 10 threads
    # de x264 disputando 10 núcleos com N Pillows deixou 8 processos só 20% mais
    # rápidos que 2. O paralelismo já está nos segmentos; o codificador não precisa dele.
    p = subprocess.Popen(["ffmpeg", "-y", "-nostdin", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", *ENC, "-threads", "2", "-an", str(tmp)],
                         stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    _W["mattes"] = 0
    try:
        for r in recs:
            p.stdin.write(compor(r).tobytes())
        p.stdin.close()
        err = p.stderr.read()
        p.wait()
    except (BrokenPipeError, ValueError, OSError):
        # o ffmpeg morreu antes de receber tudo: o motivo está no stderr dele
        err = p.stderr.read()
        p.wait()
        raise RuntimeError(f"ffmpeg fechou o pipe no segmento {destino.name}: "
                           f"{err.decode(errors='replace')[-400:]}")
    if p.returncode != 0:
        raise RuntimeError(f"ffmpeg no segmento {destino.name}: {err.decode(errors='replace')[-400:]}")
    tmp.rename(destino)
    return str(destino), len(recs), _W["mattes"]


# ---------------------------------------------------------------------------
# áudio
# ---------------------------------------------------------------------------
def audio(cfg, linha, man):
    of = cfg["of"] / "audio"
    of.mkdir(parents=True, exist_ok=True)
    plano = cfg["plano"]
    t0 = time.time()
    pcm = {}
    for nome, tk in cfg["takes"].items():
        p = of / f"pcm-{nome}-{tk['ident']}.raw"
        if not p.exists():
            with open(p.with_suffix(".parcial"), "wb") as fh:
                subprocess.run(["ffmpeg", "-v", "error", "-i", tk["arq"], "-vn", "-f", "f32le",
                                "-ac", "2", "-ar", str(SR), "-"], stdout=fh, check=True)
            p.with_suffix(".parcial").rename(p)
        pcm[nome] = np.memmap(p, dtype=np.float32, mode="r").reshape(-1, 2)

    kv = oficina.chave({"tab": [(t["take"], t["brutoDe"], t["brutoAte"]) for t in linha.tab],
                        "takes": {k: v["ident"] for k, v in cfg["takes"].items()}})
    voz_p = of / f"voz-{kv}.raw"
    refeita_voz = not voz_p.exists()
    if refeita_voz:
        pedacos = []
        for t in linha.tab:
            x = pcm[t["take"]]
            a = int(linha.local(t["brutoDe"], t["take"]) * SR)
            b = int(linha.local(t["brutoAte"], t["take"]) * SR)
            fatia = np.zeros((b - a, 2), dtype=np.float32)
            lo, hi = max(0, a), min(len(x), b)
            if hi > lo:
                fatia[lo - a:hi - a] = x[lo:hi]
            pedacos.append(fatia)
        voz = np.concatenate(pedacos)
        nominal = int(linha.total / 1000 * SR)
        print(f"voz: {len(voz)} amostras, nominal {nominal} · deriva {(len(voz)-nominal)/SR*1000:+.1f} ms", flush=True)
        voz_p.write_bytes((np.clip(voz, -1, 1) * 32767).astype("<i2").tobytes())
    voz = np.frombuffer(voz_p.read_bytes(), dtype="<i2").astype(np.float32).reshape(-1, 2) / 32767

    musicas = plano.get("musicas", {})
    km = oficina.chave({"voz": kv, "mus": {k: (oficina.identidade(m["arq"]), m["src"]) for k, m in musicas.items()},
                        "trilha": plano.get("trilha", []), "cruzada": plano.get("cruzada", 1.4),
                        "ganho": plano.get("ganho", 0.0), "cama": acabamento.CAMA})
    mix_p = of / f"mix-{km}.raw"
    m4a = of / f"mix-{km}.m4a"
    refeita_mix = not m4a.exists()
    if refeita_mix:
        fim = linha.total / 1000
        GANHO, CRUZADA = plano.get("ganho", 0.0), plano.get("cruzada", 1.4)
        trocas = sorted((linha.quando(mid), chave) for mid, chave in plano.get("trilha", []))
        cama = np.zeros(int(fim * SR) + SR, dtype=np.float32)

        def leitura(m, precisa):
            x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-ss", str(m["src"]), "-i", m["arq"],
                                              "-af", acabamento.CAMA, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                                             capture_output=True).stdout, dtype=np.float32)
            n = int(precisa * SR)
            if len(x) < n:
                x = np.concatenate([x] * (n // max(1, len(x)) + 2))
            return x[:n].copy()

        for i, (t0_, chave) in enumerate(trocas):
            t1 = trocas[i + 1][0] if i + 1 < len(trocas) else fim
            ini = max(0.0, t0_ - (CRUZADA if i else 0.0))
            dur = (t1 + CRUZADA) - ini if i + 1 < len(trocas) else fim - ini
            x = leitura(musicas[chave], dur)
            env = np.ones(len(x), dtype=np.float32)
            nc = int(CRUZADA * SR)
            if i:
                env[:nc] = np.sin(np.linspace(0, np.pi / 2, nc, dtype=np.float32))
            else:
                ent = int(1.2 * SR)
                env[:ent] = np.sin(np.linspace(0, np.pi / 2, ent, dtype=np.float32))
            if i + 1 < len(trocas):
                env[-nc:] = np.cos(np.linspace(0, np.pi / 2, nc, dtype=np.float32))
            else:
                f = int(2.5 * SR)
                env[-f:] = np.cos(np.linspace(0, np.pi / 2, f, dtype=np.float32))
            j = int(ini * SR)
            cama[j:j + len(x)] += x * env
        if trocas:
            print("trilha: " + " → ".join(f"{k}@{t:.1f}s" for t, k in trocas), flush=True)
        mix = voz.copy()
        n = min(len(mix), len(cama))
        mix[:n] += (cama[:n] * GANHO)[:, None]
        pico = float(np.abs(mix).max())
        if pico > 1.0:
            mix /= pico
            print(f"mistura normalizada (pico era {pico:.2f})", flush=True)
        mix_p.write_bytes((np.clip(mix, -1, 1) * 32767).astype("<i2").tobytes())
        oficina.ffmpeg("-f", "s16le", "-ar", SR, "-ac", "2", "-i", str(mix_p), "-c:a", "aac", "-b:a", "256k", str(m4a))
    man.etapa("audio", int(refeita_voz) + int(refeita_mix), 2 - int(refeita_voz) - int(refeita_mix), t0=t0)
    return voz_p, mix_p, m4a


# ---------------------------------------------------------------------------
# montagem
# ---------------------------------------------------------------------------
def concatenar(segmentos, audio_arq, saida):
    lista = saida.with_suffix(".lista.txt")
    lista.write_text("".join(f"file '{Path(s).resolve()}'\n" for s in segmentos), encoding="utf-8")
    oficina.ffmpeg("-f", "concat", "-safe", "0", "-i", str(lista), "-i", str(audio_arq),
                   "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "copy",
                   "-movflags", "+faststart", "-shortest", str(saida))
    lista.unlink(missing_ok=True)
    # nb_frames vem do cabeçalho do MP4 (instantâneo); contar decodificando levava 40 s
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=nb_frames:format=duration,size",
                        "-of", "default=nw=1", str(saida)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    info = dict(l.split("=", 1) for l in r.stdout.strip().splitlines() if "=" in l)
    info["nb_read_frames"] = info.get("nb_frames", "0")
    return info


VERSAO = _versao()


def main():
    ap = argparse.ArgumentParser(description="master do formato analise, por segmentos com cache")
    ap.add_argument("projeto")
    ap.add_argument("--paralelo", type=int, default=oficina.nucleos())
    ap.add_argument("--revisao", action="store_true", help="também escreve edicao/revisao.mp4 (324×576)")
    ap.add_argument("--entrega", type=int, default=None, metavar="QUADRO",
                    help="gera edicao/entrega/master-final.mp4 com a capa (quadro limpo N) na frente")
    ap.add_argument("--recodificar", action="store_true",
                    help="além do master por concatenação, um encode único CRF 15 slow (lento; raramente vale)")
    ap.add_argument("--limpar", action="store_true", help="apaga a cache de segmentos antes (não a de insumos)")
    a = ap.parse_args()

    cfg = carregar(a.projeto)
    with oficina.Cronometro(cfg["of"], "renderizar",
                            args={"revisao": a.revisao, "entrega": a.entrega, "recodificar": a.recodificar,
                                  "limpar": a.limpar, "paralelo": a.paralelo}) as cron:
        d = _renderizar(a, cfg)
        # o manifesto já sabe o que foi refeito e de onde veio; a telemetria só copia
        cron.extra.update(etapas=d["etapas"], total_s=d["total_s"])


def _renderizar(a, cfg):
    of = cfg["of"]
    of.mkdir(parents=True, exist_ok=True)
    man = oficina.Manifesto(of / "manifesto.json")
    dl = oficina.dataless(cfg["P"])
    if dl:
        raise SystemExit("arquivos fora do disco (iCloud dataless):\n  " + "\n  ".join(dl[:10]))
    if a.limpar and (of / "seg").exists():
        for p in (of / "seg").glob("*.mp4"):
            p.unlink()

    linha = Linha(cfg["tabela"], cfg["takes"])
    plano = cfg["plano"]
    t0 = time.time()

    # -- enquadramento: um por take, base do cartão UMA para o vídeo ----------
    rostos, quadros_take, bases = {}, {}, {}
    # o rastreador (Vision) anda a ~11% de um núcleo por take: os takes vão juntos
    with ThreadPoolExecutor(max_workers=len(cfg["takes"])) as ex:
        for nome, r in zip(cfg["takes"], ex.map(lambda n: rosto_do_take(cfg, n), cfg["takes"])):
            rostos[nome] = r
    for nome in cfg["takes"]:
        quadros_take[nome], bases[nome] = cartao.enquadramento_fixo(rostos[nome])
        q = quadros_take[nome]
        print(f"take {nome}: centro ({q['cx']:.3f},{q['cy']:.3f}) {q['escala']}x · base do cartão em {bases[nome]:.3f}", flush=True)
    base = float(np.mean(list(bases.values())))
    cartao.BASE_MODO1 = base
    print(f"base do cartão unificada em {base:.3f}", flush=True)

    # -- legenda ----------------------------------------------------------------
    import re
    grafias = plano.get("grafias", {})

    def grafia(p):
        t = p["p"]
        for errado, certo in grafias.items():
            t = re.sub(rf"\b{re.escape(errado)}\b", certo, t)
        return {**p, "p": t}
    legendas, perdidos = [], 0
    for g in cartao.grupos([grafia(p) for p in cfg["d"]["palavras"]], 3):
        x, y = linha.para_corte(g["de"]), linha.para_corte(g["ate"], fim=True)
        if x is None or y is None or y <= x:
            perdidos += 1
            continue
        legendas.append({"texto": g["texto"], "de": x, "ate": y})
    legendas.sort(key=lambda g: g["de"])
    print(f"{len(legendas)} grupos de legenda ({perdidos} fora do corte)", flush=True)

    # -- insumos: split edit → A-roll; pop-ups; clipes; hook --------------------
    n_split = linha.split_edits()
    print(f"{n_split} emendas com split edit (imagem até {L_ALVO} ms à frente)", flush=True)
    n_aroll, indices = extrair_aroll(cfg, linha, a.paralelo)
    man.etapa("aroll", n_aroll, len(linha.tab) - n_aroll)
    n_pop = desenhar_popups(cfg)
    pedidos = []
    for cs in plano["plano"].values():
        for c in cs:
            if c.get("tipo", "clipe") == "clipe":
                pedidos.append((c["fonte"], c["src"], c["dur"]))
            elif c.get("tipo") == "triptico":
                pedidos += [tuple(p) for p in c["paineis"]]
    HOOK = plano.get("hook")
    if HOOK:
        pedidos.append((HOOK["fonte"], HOOK["src"], 3.0))
    n_clipes = extrair_clipes(cfg, pedidos, a.paralelo)
    man.etapa("clipes", n_clipes + n_pop, len(set(pedidos)) - n_clipes)
    cartoes = montar_cartoes(cfg, linha, lambda f, s, d: quadros_de(cfg, f, s, d))
    print(f"{len(cartoes)} cartões dentro do corte", flush=True)
    marcs = []
    for m in plano.get("marcadores", []):
        x = linha.entrada(m["de"] * 1000)
        if x is None:
            print(f"  !! marcador {m['n']} fora do corte", flush=True)
            continue
        marcs.append({**m, "deC": x, "ateC": x + (m["ate"] - m["de"]) * 1000})
    marcs.sort(key=lambda m: m["deC"])
    print(f"{len(marcs)} marcadores de capítulo", flush=True)
    hookq = quadros_de(cfg, HOOK["fonte"], HOOK["src"], 3.0) if HOOK else []

    # -- receitas e segmentos ---------------------------------------------------
    recs = receitas(cfg, linha, indices, cartoes, marcs, legendas, hookq, quadros_take, rostos, base)
    segs = segmentar(recs)
    seg_dir = of / "seg"
    seg_dir.mkdir(exist_ok=True)
    jobs, prontos = [], []
    for s in segs:
        k = oficina.chave({"v": versao_do_segmento(s), "enc": ENC, "base": round(base, 4), "q": s})
        dest = seg_dir / f"{k}.mp4"
        prontos.append(dest)
        if not dest.exists():
            jobs.append((dest, s))
    print(f"{len(segs)} segmentos · {len(jobs)} a compor · {len(segs)-len(jobs)} da cache · "
          f"{a.paralelo} processos", flush=True)
    conta = prestar_contas(of, segs, [s for _, s in jobs])
    (of / "mapa.json").write_text(json.dumps({
        "quadros": len(recs), "aroll": [r["aroll"] for r in recs],
        "tabela": linha.tab, "segmentos": [{"arq": str(p), "de": s[0]["n"], "ate": s[-1]["n"]}
                                            for p, s in zip(prontos, segs)]}), encoding="utf-8")
    t1 = time.time()
    if jobs:
        res, erros = oficina.paralelo(render_segmento, jobs, n=a.paralelo, processos=True,
                                      initializer=_init, initargs=(base, str(of / "matte")),
                                      rotulo=lambda j: j[0].name)
        if erros:
            for nome, e in erros:
                print(f"  !! segmento {nome}: {e}", flush=True)
            raise SystemExit(f"{len(erros)} segmento(s) falharam; o master não foi montado")
        q = sum(r[1] for r in res)
        mt = sum(r[2] for r in res)
        print(f"{q} quadros compostos em {len(jobs)} segmentos · {mt} mattes novos · "
              f"{time.time()-t1:.0f}s ({q/max(1e-6, time.time()-t1):.1f} q/s)", flush=True)
    man.etapa("segmentos", len(jobs), len(segs) - len(jobs), t0=t1)

    # -- áudio e master ---------------------------------------------------------
    voz_p, mix_p, m4a = audio(cfg, linha, man)
    t2 = time.time()
    master = cfg["ed"] / "master.mp4"
    info = concatenar(prontos, m4a, master)
    esperado = len(recs)
    lidos = int(info.get("nb_read_frames", 0))
    print(f"MASTER: {master} · {lidos} quadros (esperado {esperado}) · {float(info['duration']):.3f}s · "
          f"{int(info['size'])/1e6:.1f} MB · montagem {time.time()-t2:.1f}s", flush=True)
    if lidos != esperado:
        raise SystemExit(f"o master tem {lidos} quadros e o corte pede {esperado}")

    if a.revisao:
        # a prévia é descartável: vai no codificador de GPU da máquina, quando há
        # um que funcione. O master continua libx264 (ver plataforma.py)
        import plataforma
        cod, args_v = plataforma.codificador_previa()
        oficina.ffmpeg("-i", str(master), "-vf", "scale=324:576", *args_v, "-pix_fmt", "yuv420p",
                       "-c:a", "aac", "-b:a", "96k", str(cfg["ed"] / "revisao.mp4"))
        print(f"revisão: {cfg['ed'] / 'revisao.mp4'} ({cod})")

    if a.recodificar:
        t3 = time.time()
        oficina.ffmpeg("-i", str(master), "-c:v", "libx264", "-crf", "15", "-preset", "slow", "-profile:v", "high",
                       "-level", "4.2", "-x264-params", "ref=5:bframes=4", "-pix_fmt", "yuv420p", "-c:a", "copy",
                       "-movflags", "+faststart", str(cfg["ed"] / "master-recodificado.mp4"))
        print(f"recodificado em {time.time()-t3:.0f}s")

    # -- provas -----------------------------------------------------------------
    (cfg["ed"] / "provas.json").write_text(json.dumps({
        "formato": "analise",
        "densidadePct": round(100 * sum(c["ate"] - c["de"] for c in cartoes) / linha.total, 1),
        "takes": {k: v["arq"] for k, v in cfg["takes"].items()},
        "fontes": {k: {kk: vv for kk, vv in v.items() if kk != "arq"} for k, v in plano["fontes"].items()},
        "trilha": {"ganho": plano.get("ganho"), "faixas": {k: {kk: vv for kk, vv in v.items() if kk != "arq"}
                                                          for k, v in plano.get("musicas", {}).items()}},
        "marcadores": [{"n": m["n"], "nome": m["nome"], "emS": round(m["deC"] / 1000, 2),
                        "ancora": "palavra falada (não há detector de gesto)"} for m in marcs],
        "semCartao": plano.get("semCartao", []),
        "cartoes": [{"momento": c["chave"], "tipo": c["tipo"], "modo": c.get("modo"), "fonte": c.get("fonte"),
                     "srcS": c.get("src"), "durS": c.get("dur"),
                     "paineis": [{"fonte": f, "srcS": s, "durS": dd} for f, s, dd in c.get("paineis_plano", [])] or None,
                     "emS": round(c["de"] / 1000, 2), "ateS": round(c["ate"] / 1000, 2),
                     "porque": c.get("porque", "")} for c in cartoes]},
        ensure_ascii=False, indent=1), encoding="utf-8")

    # -- entrega: a capa como segmento, e nenhuma recodificação do corpo --------
    if a.entrega is not None:
        t4 = time.time()
        ent = cfg["ed"] / "entrega"
        ent.mkdir(exist_ok=True)
        n = a.entrega
        oficina.quadro_em(master, (n - 1) / FPS).save(ent / "quadro-capa.png")
        pub = cfg["P"] / "publicacao.json"
        if not pub.exists():
            raise SystemExit(f"--entrega precisa de {pub}")
        subprocess.run([sys.executable, str(Path(__file__).with_name("publicacao.py")), str(pub),
                        "--capa", "--saida", str(ent)], cwd=str(cfg["P"]), check=True)
        capa = ent / "capa.jpg"
        kc = oficina.chave({"capa": oficina.identidade(capa), "enc": ENC, "ms": CAPA_MS})
        capa_seg = seg_dir / f"capa-{kc}.mp4"
        if not capa_seg.exists():
            oficina.ffmpeg("-loop", "1", "-framerate", FPS, "-i", str(capa), "-t", f"{CAPA_MS/1000:.3f}",
                           "-vf", f"scale={W}:{H}", *ENC, "-an", str(capa_seg))
        mix = np.frombuffer(mix_p.read_bytes(), dtype="<i2").reshape(-1, 2)
        sil = np.zeros((CAPA_MS * SR // 1000, 2), dtype="<i2")
        ent_raw = of / "audio" / f"entrega-{kc}-{mix_p.stem}.raw"
        ent_raw.write_bytes(np.concatenate([sil, mix]).tobytes())
        ent_m4a = ent_raw.with_suffix(".m4a")
        oficina.ffmpeg("-f", "s16le", "-ar", SR, "-ac", "2", "-i", str(ent_raw), "-c:a", "aac", "-b:a", "256k", str(ent_m4a))
        final = ent / "master-final.mp4"
        info = concatenar([capa_seg, *prontos], ent_m4a, final)
        print(f"ENTREGA: {final} · {info.get('nb_read_frames')} quadros · {float(info['duration']):.2f}s · "
              f"{int(info['size'])/1e6:.1f} MB · {time.time()-t4:.0f}s (sem recodificar o corpo)", flush=True)

    d = man.fechar(total_s=round(time.time() - t0, 1), segmentos=len(segs), quadros=len(recs),
                   versao=VERSAO, cache=conta)
    print(f"manifesto: {man.resumo()} · total {d['total_s']}s")
    # o render longo termina com o dono longe da máquina: a notificação é o que
    # o traz de volta. Falha de aviso jamais derruba um master já pronto.
    try:
        import avisar
        avisar.avisar(f"{cfg['P'].name} · {man.resumo()}",
                      tipo="publicar" if a.entrega is not None else "revisar",
                      projeto=cfg["P"].name)
    except Exception as e:                 # noqa: BLE001
        print(f"(sem aviso: {e!r})")
    return d


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
