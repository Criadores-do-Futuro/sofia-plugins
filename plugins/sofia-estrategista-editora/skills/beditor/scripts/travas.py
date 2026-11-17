#!/usr/bin/env python3
"""
travas.py — o que nunca pode chegar a tela.

Cada funcao e uma licao paga: buraco na timeline (18 s de preto), tela sem
interface (32 s quase preto), palavra repetida pela acumulacao, grafico que
pisca. Elas rodam sobre o plano.json pronto, venha ele do montar.py ou do
aplicar.py legado.
"""
TEM_TEXTO_PROPRIO = {"cartela", "paper", "dado", "tela", "retrato", "palavras",
                     "galaxia", "camadas", "indice"}
MIN_GRAFICO_MS = 2500
MIN_VIZINHO_MS = 1400


def _vira_fala(p, plano):
    p["tipo"] = "fala" if plano.get("fonteVideo") else "cartela"
    p["asset"] = None
    p["legenda"] = True


def fechar_buracos(plano):
    ps, av, n = plano["planos"], [], 0
    for a, b in zip(ps, ps[1:]):
        if b["t0"] > a["t1"]:
            a["t1"] = b["t0"]
            a["duracaoMs"] = a["t1"] - a["t0"]
            n += 1
    if ps:
        if ps[0]["t0"] > 0:
            ps[0]["t0"] = 0
            ps[0]["duracaoMs"] = ps[0]["t1"]
            n += 1
        if ps[-1]["t1"] < plano["duracaoMs"]:
            ps[-1]["t1"] = plano["duracaoMs"]
            ps[-1]["duracaoMs"] = ps[-1]["t1"] - ps[-1]["t0"]
            n += 1
    if n:
        av.append(f"{n} buraco(s) de timeline fechados — sem tela preta")
    return av


def tela_sem_modo(plano):
    av = []
    for p in plano["planos"]:
        if p["tipo"] == "tela" and not ((p.get("tela") or {}).get("modo") or p.get("conversa")):
            _vira_fala(p, plano)
            av.append(f"{p['id']}: `tela` sem interface — virou `{p['tipo']}`. Janela vazia e tela preta.")
    return av


def palavras_dedupe(plano):
    vistas, rep = [], 0
    for p in plano["planos"]:
        if p["tipo"] != "palavras":
            vistas = []
            continue
        novas = []
        for w in (p.get("palavras") or []):
            k = w.strip().lower()
            if k and k not in vistas:
                vistas.append(k)
                novas.append(w)
            else:
                rep += 1
        p["palavras"] = novas
    return [f"{rep} palavra(s) repetida(s) removida(s) — a acumulacao ja e feita pelo Video.tsx"] if rep else []


def palavras_vazio(plano):
    av = []
    for p in plano["planos"]:
        if p["tipo"] == "palavras" and not p.get("palavras"):
            _vira_fala(p, plano)
            av.append(f"{p['id']}: `palavras` sem nada a acrescentar — virou `{p['tipo']}`")
    return av


def grafico_curto(plano):
    av, ps = [], plano["planos"]
    for k, p in enumerate(ps):
        if p["tipo"] == "fala" or p["duracaoMs"] >= MIN_GRAFICO_MS:
            continue
        prox = ps[k + 1] if k + 1 < len(ps) else None
        if not prox or prox["tipo"] != "fala":
            continue
        ganho = min(MIN_GRAFICO_MS - p["duracaoMs"], max(0, prox["duracaoMs"] - MIN_VIZINHO_MS))
        if ganho <= 0:
            continue
        p["t1"] += ganho
        p["duracaoMs"] += ganho
        prox["t0"] += ganho
        prox["duracaoMs"] -= ganho
        av.append(f"{p['id']}: `{p['tipo']}` curto demais — segurou +{ganho}ms por cima de {prox['id']}")
    return av


def aplicar_todas(plano):
    av = []
    for f in (fechar_buracos, tela_sem_modo, palavras_dedupe, palavras_vazio, grafico_curto):
        av += f(plano)
    for p in plano["planos"]:
        p.setdefault("legenda", p["tipo"] not in TEM_TEXTO_PROPRIO)
    return av
