"""
tempo.py — o relogio do take, em uma unica implementacao.

Tudo que le o transcript, agrupa em frases ou converte tempo passa por aqui.
Antes cada script tinha a sua copia, e cada copia arredondava diferente — o
resultado foi um transcript que precisou ser reconstruido a partir de
duracoes medidas. Um relogio so.
"""
import json, re
from pathlib import Path

FIM_DE_FRASE = re.compile(r"[.!?…]$")


def carregar_palavras(caminho):
    """whisper.json -> [{palavra, deMs, ateMs}], em ms inteiros, sem espacos"""
    d = json.loads(Path(caminho).read_text(encoding="utf-8"))
    # o motor MLX grava as palavras numa lista so, na raiz, e deixa os
    # segmentos sem `words` — ler so dos segmentos dava zero palavra, e com
    # zero palavra a legenda saia vazia e nenhuma pausa era apertada
    por_segmento = [w for seg in d.get("segments", []) for w in seg.get("words", [])]
    saida = []
    for w in por_segmento or d.get("words", []):
        texto = w["word"].strip()
        if not texto:
            continue
        saida.append({"palavra": texto,
                      "deMs": int(round(w["start"] * 1000)),
                      "ateMs": int(round(w["end"] * 1000))})
    return saida


def frases(palavras, pausa_ms=900):
    """agrupa palavras em frases: quebra em pontuacao final ou em pausa maior
    que `pausa_ms`. A pausa e decisao editorial, entao ela fica registrada nos
    dois lados (antes e depois)."""
    grupos, atual = [], []
    for i, w in enumerate(palavras):
        atual.append(w)
        prox = palavras[i + 1] if i + 1 < len(palavras) else None
        pausa = (prox["deMs"] - w["ateMs"]) if prox else 0
        if FIM_DE_FRASE.search(w["palavra"]) or pausa > pausa_ms or prox is None:
            grupos.append(atual)
            atual = []
    saida = []
    for k, g in enumerate(grupos):
        de, ate = g[0]["deMs"], g[-1]["ateMs"]
        antes = de - (grupos[k - 1][-1]["ateMs"] if k else 0)
        depois = (grupos[k + 1][0]["deMs"] - ate) if k + 1 < len(grupos) else 0
        saida.append({"deMs": de, "ateMs": ate,
                      "texto": " ".join(w["palavra"] for w in g),
                      "palavras": g,
                      "pausaAntesMs": antes, "pausaDepoisMs": depois})
    return saida


def ts(ms):
    """MM:SS.d — o formato que aparece nas folhas e no fala.md"""
    s = ms / 1000.0
    return f"{int(s // 60):02d}:{s % 60:04.1f}"


def ms_para_frames(ms, fps):
    return int(round((ms / 1000.0) * fps))


def recorte_9x16(largura, altura, deslocamento=0):
    """o recorte vertical que vai ao ar: altura inteira, largura 9/16 dela,
    centrado; `deslocamento` empurra para o lado quando o assunto nao esta no
    centro. Devolve (w, h, x, y) prontos para o crop do ffmpeg."""
    w = min(largura, int(round(altura * 9 / 16)))
    x = max(0, min(largura - w, (largura - w) // 2 + deslocamento))
    return (w, altura, x, 0)
