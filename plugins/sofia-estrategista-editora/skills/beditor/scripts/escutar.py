#!/usr/bin/env python3
"""
escutar.py — acha no AUDIO a fala que o transcript nao conta.

O problema que este script existe para resolver foi medido num take real
(2026-09-11): o dono disse "Entao eu decidi..." , travou, e recomecou a frase
inteira. No video final as duas tentativas ficaram. Ninguem errou o corte — o
TRANSCRIPT e que mentiu: o Whisper colapsou 2,8 s de fala, pausa e retomada numa
unica palavra, «treinar», de 36,08 a 38,90. Transcrever de novo sem filtro de
voz, sem condicionamento pelo contexto e pedindo transcricao literal devolveu
exatamente o mesmo texto: o modelo **limpa disfluencia de proposito**, e nao ha
parametro que desligue isso.

Entao a deteccao nao pode sair do texto. Sai do audio:

  - uma palavra que dura muito mais do que palavra nenhuma dura, e que tem
    energia de voz dentro, esconde fala que o texto nao registrou;
  - dentro dela, dois blocos de voz separados por silencio, com o texto contando
    uma coisa so, e uma FALSA PARTIDA: a pessoa comecou, parou e recomecou.

A regra de qual pedaco fica e do mundo, nao do codigo: **quem recomeca acerta na
ultima vez**. Entao o corte proposto vai do inicio do trecho ate o comeco do
ultimo bloco de voz, menos um respiro.

O script nao corta nada. Ele escreve o que ouviu, com o tempo e o motivo, para o
diretor decidir — e para o editor ver na mesa de decupagem por que aquele pedaco
esta marcado para sair.
"""
import argparse
import json
import subprocess
import unicodedata
from pathlib import Path

import numpy as np

SR = 8000              # 8 kHz basta para envelope de energia; a voz vive abaixo disso
PASSO_MS = 20          # janela do envelope
PAUSA_MIN_MS = 320     # silencio que separa duas tentativas (abaixo disso e respiro)
VOZ_MIN_MS = 180       # bloco de voz mais curto que isto e estalo, nao fala
PALAVRA_LONGA_MS = 950  # nenhuma palavra do portugues falado dura isto
RESPIRO_MS = 120       # o que se deixa antes da retomada, para nao comer o ataque
NGRAMA = 3             # tamanho da repeticao literal que conta como retomada


# ------------------------------------------------------------------ o audio
def envelope(audio, passo_ms=PASSO_MS):
    """RMS por janela. E o suficiente: o que se quer saber e 'ha voz aqui'."""
    n = int(SR * passo_ms / 1000)
    sobra = len(audio) % n
    if sobra:
        audio = audio[:-sobra]
    janelas = audio.reshape(-1, n)
    return np.sqrt((janelas ** 2).mean(axis=1))


def carregar_audio(arquivo):
    bruto = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(arquivo), "-ac", "1", "-ar", str(SR),
         "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(bruto, dtype=np.int16).astype(np.float32) / 32768.0


def limiar_de_voz(env):
    """O piso da sala e o percentil 10; a voz e o percentil 90. O limiar fica
    perto do piso, nao no meio: consoante surda tem energia baixa e nao pode
    virar silencio."""
    piso, alto = np.percentile(env, 10), np.percentile(env, 90)
    return piso + 0.18 * (alto - piso)


def blocos_de_voz(env, limiar, de_ms, ate_ms):
    """Os pedacos com voz dentro de uma janela, em ms, ja costurados: silencio
    menor que PAUSA_MIN_MS nao separa nada, e bloco menor que VOZ_MIN_MS some."""
    i0, i1 = int(de_ms / PASSO_MS), min(len(env), int(ate_ms / PASSO_MS))
    tem = env[i0:i1] > limiar
    blocos, dentro, comeco = [], False, 0
    for i, v in enumerate(tem):
        if v and not dentro:
            dentro, comeco = True, i
        elif not v and dentro:
            dentro = False
            blocos.append([(i0 + comeco) * PASSO_MS, (i0 + i) * PASSO_MS])
    if dentro:
        blocos.append([(i0 + comeco) * PASSO_MS, i1 * PASSO_MS])

    costurados = []
    for b in blocos:
        if costurados and b[0] - costurados[-1][1] < PAUSA_MIN_MS:
            costurados[-1][1] = b[1]
        else:
            costurados.append(b)
    return [b for b in costurados if b[1] - b[0] >= VOZ_MIN_MS]


# ------------------------------------------------------------------- o texto
def limpo(palavra):
    s = unicodedata.normalize("NFKD", palavra.strip().lower())
    return "".join(c for c in s if c.isalnum())


def _fechou(palavra):
    """A frase terminou? Pontuacao final e a marca de que a tentativa chegou ao
    fim — e o que chegou ao fim nao e falsa partida."""
    return palavra["word"].strip().endswith((".", "!", "?", "…"))


def repeticoes_literais(palavras):
    """Quando o Whisper DEIXA as duas tentativas no texto (acontece quando a
    segunda muda alguma palavra), a retomada aparece como um n-grama repetido
    com pausa no meio. Aqui o texto basta, e a medida e barata.

    Duas guardas, aprendidas num falso positivo real: "ele ja faz a pesquisa.
    Ele ja faz a edicao. Ele ja faz o corte" nao e gagueira, e ANAFORA — figura
    de linguagem que carrega o ritmo do trecho. O que separa uma da outra nao e
    a repeticao em si; e se a primeira tentativa **fechou**. Frase que terminou
    com ponto chegou onde queria. E n-grama que volta tres vezes e figura de
    linguagem, nunca engano."""
    achados = []
    chaves = [limpo(w["word"]) for w in palavras]
    quantas = {}
    for i in range(len(chaves) - NGRAMA + 1):
        g = tuple(chaves[i:i + NGRAMA])
        if all(g):
            quantas[g] = quantas.get(g, 0) + 1
    i = 0
    while i < len(chaves) - NGRAMA * 2:
        a = chaves[i:i + NGRAMA]
        if not all(a) or quantas.get(tuple(a), 0) >= 3:
            i += 1
            continue
        for j in range(i + 1, min(i + NGRAMA * 3, len(chaves) - NGRAMA + 1)):
            if chaves[j:j + NGRAMA] != a:
                continue
            pausa = palavras[j]["start"] * 1000 - palavras[j - 1]["end"] * 1000
            if pausa < 120 and j - i <= NGRAMA:
                continue   # "muito, muito bom" — enfase, nao retomada
            if any(_fechou(w) for w in palavras[i:j]):
                continue   # a primeira tentativa chegou ao ponto final
            achados.append({
                "tipo": "repeticao",
                "deMs": round(palavras[i]["start"] * 1000),
                "ateMs": round(palavras[j]["start"] * 1000 - RESPIRO_MS),
                "texto": " ".join(w["word"].strip() for w in palavras[i:j]),
                "retomada": " ".join(w["word"].strip() for w in palavras[j:j + NGRAMA]),
                "porque": "a mesma frase recomeca aqui; quem recomeca acerta na ultima vez",
            })
            i = j
            break
        i += 1
    return achados


# ------------------------------------------------------------------ a escuta
def escutar(take, falas, so_palavra_longa=PALAVRA_LONGA_MS):
    audio = carregar_audio(take)
    env = envelope(audio)
    limiar = limiar_de_voz(env)
    ws = json.loads(Path(falas).read_text(encoding="utf-8"))
    # o transcrever.py grava as palavras na raiz e deixa os segmentos sem `words`
    palavras = [w for s in ws.get("segments", []) for w in s.get("words", [])] \
        or ws.get("words", [])

    achados = []

    # 1. fala que o transcript nao conta: uma palavra longa demais com voz dentro
    for i, w in enumerate(palavras):
        de, ate = w["start"] * 1000, w["end"] * 1000
        if ate - de < so_palavra_longa:
            continue
        # A tentativa comecou ANTES da palavra engolida: «Entao eu decidi» ja
        # estava no transcript, colado nela. Anda para tras enquanto as palavras
        # se encostam, e para no ponto final — senao o corte come a frase de cima.
        j = i
        while j > 0:
            anterior = palavras[j - 1]
            if _fechou(anterior):
                break
            if palavras[j]["start"] * 1000 - anterior["end"] * 1000 >= PAUSA_MIN_MS:
                break
            j -= 1
        de = palavras[j]["start"] * 1000
        inicio_da_frase = " ".join(x["word"].strip() for x in palavras[j:i + 1])
        bs = blocos_de_voz(env, limiar, de, ate)
        voz_ms = sum(b[1] - b[0] for b in bs)
        if len(bs) < 2 or voz_ms < 300:
            continue   # palavra arrastada de verdade, ou so silencio: nao e isto
        ultimo = bs[-1]
        achados.append({
            "tipo": "falsa-partida",
            "deMs": round(de),
            "ateMs": round(max(de, ultimo[0] - RESPIRO_MS)),
            "texto": inicio_da_frase,
            "retomada": None,
            "blocos": [[round(b[0]), round(b[1])] for b in bs],
            "vozNaoContadaMs": round(voz_ms - (ultimo[1] - ultimo[0])),
            "porque": (f"o transcript conta uma palavra so («{w['word'].strip()}») em "
                       f"{round(ate - w['start'] * 1000)} ms, mas o audio tem {len(bs)} "
                       f"blocos de voz separados por silencio: «{inicio_da_frase}» foi "
                       f"comecada, travou, e recomecou inteira depois da pausa"),
        })

    # 2. a retomada que o texto deixou aparecer
    achados += repeticoes_literais(palavras)

    achados.sort(key=lambda a: a["deMs"])
    # nada que proponha cortar menos de um respiro vale o risco fonetico
    return [a for a in achados if a["ateMs"] - a["deMs"] >= 250]


def em_markdown(achados):
    if not achados:
        return "Nenhuma falsa partida ouvida no take.\n"
    l = ["## Falsas partidas ouvidas no áudio", "",
         "O transcript não registra estas — o Whisper limpa disfluência de propósito.",
         "Quem decide é o diretor; o que está aqui é o que o áudio mostra.", ""]
    for a in achados:
        seg = lambda ms: f"{int(ms // 60000)}:{ms % 60000 / 1000:05.2f}"
        l.append(f"- **{seg(a['deMs'])} → {seg(a['ateMs'])}** "
                 f"({a['ateMs'] - a['deMs']} ms, `{a['tipo']}`) — {a['porque']}")
        if a.get("retomada"):
            l.append(f"  - recomeça em «{a['retomada']}»")
    return "\n".join(l) + "\n"


def main():
    p = argparse.ArgumentParser(description="fala que o transcript nao conta")
    p.add_argument("--take", required=True)
    p.add_argument("--falas", required=True)
    p.add_argument("--out", help="escreve escuta.json e escuta.md nesta pasta")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    achados = escutar(a.take, a.falas)
    if a.json:
        print(json.dumps(achados, ensure_ascii=False, indent=2))
    else:
        print(em_markdown(achados))
    if a.out:
        d = Path(a.out)
        d.mkdir(parents=True, exist_ok=True)
        (d / "escuta.json").write_text(json.dumps(achados, ensure_ascii=False, indent=2),
                                       encoding="utf-8")
        (d / "escuta.md").write_text(em_markdown(achados), encoding="utf-8")
        print(f"{len(achados)} achado(s) → {d}/escuta.json")


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
