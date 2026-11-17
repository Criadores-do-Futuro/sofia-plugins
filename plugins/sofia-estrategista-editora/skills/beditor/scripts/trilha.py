#!/usr/bin/env python3
"""
trilha.py — a cama musical, composta a partir do guia.

Por que compor em vez de licenciar: nao ha biblioteca de musica na maquina,
e baixar de banco externo e decisao de quem edita. O que sai daqui e
original — senoides, ruido filtrado e envelopes — entao nao tem obra de
terceiro, nem licenca a cumprir, nem Content ID a temer.

O desenho e o do canal: grave, escuro, poucas notas, muito espaco. A cama nao
toca melodia; sustenta um acorde e muda de cor quando o assunto muda. Quem
diz quando o assunto muda e o diretor: cada momento traz `musica.clima` (a
cor) e `musica.cama` (sobe, desce, mantem, some).
"""
import math, struct, sys, wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import estilos  # noqa: E402

SR = 48000

# La menor natural, a tonica la embaixo. Frequencias em Hz.
A1, C2, D2, E2, F2, G2, A2 = 55.00, 65.41, 73.42, 82.41, 87.31, 98.00, 110.00
C3, E3, F3, G3, A3, B3 = 130.81, 164.81, 174.61, 196.00, 220.00, 246.94
C4, D4, E4, F4, A4 = 261.63, 293.66, 329.63, 349.23, 440.00

NEUTRO = {"acorde": [A1, E2, A3], "ganho": 0.13, "pulso": 0, "brilho": 0.12, "tensao": 0.0}
# clima -> cor. O diretor escreve uma palavra; se ela nao esta aqui, e neutro.
CLIMAS = {
    "abertura":  {"acorde": [A1, A2, E3, A3], "ganho": 0.16, "pulso": 0,   "brilho": 0.10, "tensao": 0.0},
    "suspense":  {"acorde": [A1, E2, A3],     "ganho": 0.11, "pulso": 60,  "brilho": 0.22, "tensao": 0.0},
    "espera":    {"acorde": [A1, E2],         "ganho": 0.09, "pulso": 0,   "brilho": 0.04, "tensao": 0.0},
    "revelacao": {"acorde": [F2, C3, F3, A3], "ganho": 0.17, "pulso": 0,   "brilho": 0.16, "tensao": 0.10},
    "tensao":    {"acorde": [F2, C3, E3, B3], "ganho": 0.19, "pulso": 80,  "brilho": 0.12, "tensao": 0.30},
    "maquina":   {"acorde": [D2, A2, D4, F4], "ganho": 0.18, "pulso": 100, "brilho": 0.26, "tensao": 0.18},
    "saida":     {"acorde": [C2, G2, C4, E4], "ganho": 0.15, "pulso": 0,   "brilho": 0.30, "tensao": 0.0},
    "neutro": NEUTRO,
}
CAMA = {"sobe": 1.25, "desce": 0.7, "mantem": 1.0, "some": 0.0}
CRUZAMENTO = 2.2   # segundos de fusao entre um movimento e o proximo


def envelope(t, dur, sobe=1.6, desce=1.6, mult=None):
    # o `estilo` (vox/editorial, `estilos.MUSICA`) encurta ou alonga o ataque
    # e o corte — e a unica diferenca sonora entre os dois, o resto do
    # envelope (respiro) e igual
    if mult:
        sobe *= mult.get("sobe_mult", 1.0)
        desce *= mult.get("desce_mult", 1.0)
    """entra e sai devagar; no meio, um respiro lento que evita a nota morta"""
    a = min(1.0, t / sobe) if sobe else 1.0
    b = min(1.0, (dur - t) / desce) if desce else 1.0
    respiro = 0.88 + 0.12 * math.sin(2 * math.pi * t / 11.0)
    return max(0.0, min(a, b)) * respiro


def render(mov, dur, mult=None):
    """um movimento: acorde sustentado + ar + pulso opcional. `mult` vem do
    estilo escolhido (`estilos.MUSICA`) e altera ataque, corte, pulso, tensao
    e ganho — nunca troca o acorde nem o timbre, so a FORMA do envelope."""
    mult = mult or {}
    n = int(dur * SR)
    esq = [0.0] * n
    dir_ = [0.0] * n
    vozes = mov["acorde"]
    # ruido rosa aproximado, para o "ar" da gravacao — sem ele soa sintetico
    rosa, b0, b1, b2 = [0.0] * n, 0.0, 0.0, 0.0
    semente = 12345
    for i in range(n):
        semente = (1103515245 * semente + 12345) % (1 << 31)
        branco = (semente / (1 << 30)) - 1.0
        b0 = 0.99765 * b0 + branco * 0.0990460
        b1 = 0.96300 * b1 + branco * 0.2965164
        b2 = 0.57000 * b2 + branco * 1.0526913
        rosa[i] = (b0 + b1 + b2 + branco * 0.1848) * 0.06

    for v, f in enumerate(vozes):
        # cada voz desafina um fio de cabelo e senta num ponto do palco:
        # e o que faz quatro senoides soarem como um instrumento, nao um teste
        desafina = 1.0 + (v - len(vozes) / 2) * 0.0016
        pan = 0.5 + (v - (len(vozes) - 1) / 2) * (0.30 / max(1, len(vozes) - 1))
        amp = 0.9 / (1 + v * 0.55)
        fase = v * 1.7
        for i in range(n):
            t = i / SR
            base = math.sin(2 * math.pi * f * desafina * t + fase)
            base += mov["brilho"] * 0.5 * math.sin(2 * math.pi * f * 2 * desafina * t + fase)
            if mov["tensao"] and v == len(vozes) - 1:
                base += mov["tensao"] * mult.get("tensao_mult", 1.0) * math.sin(
                    2 * math.pi * f * 1.06 * t + fase)
            g = amp * envelope(t, dur, mult=mult)
            esq[i] += base * g * (1 - pan)
            dir_[i] += base * g * pan

    if mov["pulso"]:
        periodo = 60.0 / mov["pulso"]
        for i in range(n):
            t = i / SR
            fase = (t % periodo) / periodo
            if fase < 0.16:
                bate = math.exp(-fase * 26) * math.sin(2 * math.pi * 52 * t)
                bate *= 0.35 * mult.get("pulso_mult", 1.0) * envelope(t, dur, mult=mult)
                esq[i] += bate
                dir_[i] += bate

    ganho = mov["ganho"] * mult.get("ganho_mult", 1.0)
    for i in range(n):
        ar = rosa[i] * envelope(i / SR, dur, mult=mult)
        esq[i] = (esq[i] + ar) * ganho
        dir_[i] = (dir_[i] + ar) * ganho
    return esq, dir_


def compor(movimentos, total, saida_wav, estilo="vox"):
    """movimentos: [{ateS, clima, cama}] em ordem, no relogio do corte.
    Momentos contiguos com o mesmo clima e a mesma cama sao fundidos antes,
    para a cama nao respirar a cada corte de plano. `estilo` e o id da
    galeria (`estilos.MUSICA`); um id desconhecido cai no padrao da casa."""
    mult = estilos.MUSICA.get(estilo) or estilos.MUSICA[estilos.PADRAO["musica"]]
    fundidos = []
    for m in movimentos:
        chave = (m.get("clima", "neutro"), m.get("cama", "mantem"))
        if fundidos and fundidos[-1][0] == chave:
            fundidos[-1][1] = float(m["ateS"])
        else:
            fundidos.append([chave, float(m["ateS"])])

    n = int(total * SR)
    esq, dir_ = [0.0] * n, [0.0] * n
    inicio = 0.0
    for (clima, cama), ate in fundidos:
        fim = min(ate, total)
        if fim <= inicio:
            continue
        cor = dict(CLIMAS.get(clima, NEUTRO))
        cor["ganho"] = cor["ganho"] * CAMA.get(cama, 1.0)
        if cor["ganho"] > 0:
            a, b = render(cor, fim - inicio + CRUZAMENTO, mult)
            base = int(inicio * SR)
            for i in range(len(a)):
                j = base + i
                if 0 <= j < n:
                    esq[j] += a[i]
                    dir_[j] += b[i]
        inicio = fim
        if inicio >= total:
            break

    pico = max(1e-9, max(max(abs(x) for x in esq), max(abs(x) for x in dir_)))
    g = (10 ** (-14 / 20)) / pico   # -14 dBFS de pico; o volume final vem do LUFS
    with wave.open(str(saida_wav), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        q = bytearray()
        for i in range(n):
            q += struct.pack("<hh", int(max(-1.0, min(1.0, esq[i] * g)) * 32767),
                             int(max(-1.0, min(1.0, dir_[i] * g)) * 32767))
        w.writeframes(bytes(q))
