#!/usr/bin/env python3
"""Os cortes de EQ de cada voz — medidos no take, guardados na marca.

    python3 voz.py medir <take> [--projeto <pasta>] [--marca <nome>] [--gravar] [--fixar]
    python3 voz.py mostrar [--projeto <pasta>] [--marca <nome>]
    python3 voz.py soltar [--projeto <pasta>] [--marca <nome>]

A cadeia de `acabamento.VOZ` vale para qualquer voz: corte de rumor, barro em
240 Hz, presença, brilho. O que ela não sabe é onde **esta** voz soa fanhosa ou
estridente — isso muda de pessoa para pessoa. O jeito de ouvido é subir uma
banda estreita ao máximo, varrer o espectro e baixar 3 a 4 dB onde honka. Aqui
se faz a mesma varredura medindo: o espectro médio da fala, suavizado em
1/12 de oitava, comparado com a tendência de 1 oitava. O que sobra acima da
tendência, numa faixa estreita, é ressonância — até 4 cortes, -3 dB (-4 dB
quando o excesso passa de 5 dB), Q 4.

Fora da busca: abaixo de 250 Hz (é o corpo da voz; o barro em 240 Hz e o rumor
já têm corte na cadeia) e em volta da presença de 3,2 kHz (cortar ali desfaria
o que a cadeia soma para a palavra ser entendida).

Mede a cada take, e não uma vez por pessoa: a ressonância que se ouve é voz
somada a sala, microfone e distância. Medido em quatro takes da mesma voz, um
corte (~1,9 kHz) voltou em todos; os outros mudaram de um dia para o outro. A
medição custa ~5 s.

Onde fica: `marca.json` → `"voz": {"cortes": [{"f", "g", "q"}], "medidoEm",
"fixo"}`. `montar.py` mede o take e guarda a última medição na marca. Com
`--fixar` (estúdio que não muda), a marca passa a mandar e o take não é mais
medido; `soltar` volta a medir. Sem marca, mede para o vídeo e não guarda.
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

SR = 48000
N_FFT = 8192
BUSCA_HZ = (250.0, 6000.0)
PRESENCA_HZ, PRESENCA_FOLGA_OIT = 3200.0, 0.25
LIMIAR_DB, FORTE_DB = 2.5, 5.0
MAX_CORTES, Q = 4, 4.0
SEPARACAO_OIT = 1 / 3
MAX_SEGUNDOS = 600   # 10 min de fala dizem tudo que a voz tem


def ler_audio(arquivo, segundos=MAX_SEGUNDOS):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(arquivo), "-vn", "-t", str(segundos),
                        "-ac", "1", "-ar", str(SR), "-af", "highpass=f=85", "-f", "f32le", "-"],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype=np.float32)


def espectro_da_fala(x):
    """potência média (dB) só dos quadros com fala: os 60% mais fortes."""
    hop = N_FFT // 2
    n = (len(x) - N_FFT) // hop
    if n < 8:
        raise SystemExit("!! áudio curto demais para medir a voz (precisa de alguns segundos de fala)")
    janela = np.hanning(N_FFT).astype(np.float32)
    quadros = np.lib.stride_tricks.as_strided(
        x, shape=(n, N_FFT), strides=(x.strides[0] * hop, x.strides[0]))
    energia = np.sqrt((quadros ** 2).mean(axis=1))
    fala = quadros[energia >= np.quantile(energia, 0.4)]
    pot = np.zeros(N_FFT // 2 + 1)
    for i in range(0, len(fala), 256):
        pot += (np.abs(np.fft.rfft(fala[i:i + 256] * janela, axis=1)) ** 2).sum(axis=0)
    freqs = np.fft.rfftfreq(N_FFT, 1 / SR)
    return freqs, 10 * np.log10(pot / len(fala) + 1e-12)


def _suavizar(freqs, db, grade, largura_oit):
    meia = 2 ** (largura_oit / 2)
    return np.array([db[(freqs >= f / meia) & (freqs <= f * meia)].mean() for f in grade])


def achar_cortes(freqs, db):
    grade = np.geomspace(BUSCA_HZ[0], BUSCA_HZ[1], 360)   # 1/50 de oitava
    fino = _suavizar(freqs, db, grade, 1 / 12)
    tendencia = _suavizar(freqs, db, grade, 1.0)
    excesso = fino - tendencia
    picos = [i for i in range(1, len(grade) - 1)
             if excesso[i] >= LIMIAR_DB and excesso[i] >= excesso[i - 1] and excesso[i] >= excesso[i + 1]
             and abs(np.log2(grade[i] / PRESENCA_HZ)) > PRESENCA_FOLGA_OIT]
    escolhidos = []
    for i in sorted(picos, key=lambda i: -excesso[i]):
        if all(abs(np.log2(grade[i] / grade[j])) >= SEPARACAO_OIT for j in escolhidos):
            escolhidos.append(i)
        if len(escolhidos) == MAX_CORTES:
            break
    return [{"f": int(round(grade[i], -1)), "g": -4.0 if excesso[i] >= FORTE_DB else -3.0, "q": Q,
             "excessoDb": round(float(excesso[i]), 1)}
            for i in sorted(escolhidos, key=lambda i: grade[i])]


def medir(arquivo):
    return achar_cortes(*espectro_da_fala(ler_audio(arquivo)))


def _marca(projeto=None, nome=None):
    import marca
    try:
        return marca.resolver(projeto, nome)
    except (KeyError, OSError, ValueError):
        return None   # máquina sem config: vale para este vídeo, sem guardar


def cortes_fixos(mc):
    v = (mc.dados.get("voz") or {}) if mc else {}
    return v.get("cortes") if v.get("fixo") else None


def gravar(mc, cortes, origem, fixo=False):
    arq = mc.pasta / "marca.json"
    dados = json.loads(arq.read_text(encoding="utf-8"))
    dados["voz"] = {"cortes": cortes, "medidoEm": Path(origem).name,
                    "data": time.strftime("%Y-%m-%d"), "fixo": fixo}
    arq.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    mc.dados["voz"] = dados["voz"]
    return arq


def cortes_para(take, projeto=None, log=print):
    """os cortes que valem para `take`: os fixados na marca; senão, mede o take
    (e guarda a medição na marca, se houver)."""
    mc = _marca(projeto)
    fixos = cortes_fixos(mc)
    if fixos is not None:
        log(f"voz: cortes fixados na marca {mc.nome} — {resumo(fixos)}")
        return fixos
    cortes = medir(take)
    if mc:
        gravar(mc, cortes, take)
        log(f"voz: medida neste take e guardada na marca {mc.nome} — {resumo(cortes)}")
    else:
        log(f"voz: medida para este vídeo (sem marca, nada guardado) — {resumo(cortes)}")
    return cortes


def resumo(cortes):
    return ", ".join(f"{c['f']} Hz {c['g']:+.0f} dB" for c in cortes) or "nenhuma ressonância acima do limiar"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("medir")
    m.add_argument("take")
    m.add_argument("--projeto")
    m.add_argument("--marca")
    m.add_argument("--gravar", action="store_true", help="guarda a medição na marca")
    m.add_argument("--fixar", action="store_true", help="guarda e fixa: os próximos takes usam estes cortes")
    for nome in ("mostrar", "soltar"):
        s = sub.add_parser(nome)
        s.add_argument("--projeto")
        s.add_argument("--marca")
    a = ap.parse_args()

    if a.cmd == "medir":
        cortes = medir(a.take)
        print(resumo(cortes))
        if a.gravar or a.fixar:
            mc = _marca(a.projeto, a.marca)
            if not mc:
                raise SystemExit("!! nenhuma marca escolhida: crie ou escolha uma com `marca.py`")
            print(f"gravado em {gravar(mc, cortes, a.take, fixo=a.fixar)}"
                  + (" — fixado: os próximos takes usam estes cortes" if a.fixar else ""))
    elif a.cmd == "soltar":
        mc = _marca(a.projeto, a.marca)
        if not mc or not mc.dados.get("voz"):
            raise SystemExit("!! nada a soltar: a marca não tem cortes de voz guardados")
        v = mc.dados["voz"]
        print(f"solto em {gravar(mc, v.get('cortes') or [], v.get('medidoEm') or '', fixo=False)}"
              " — cada take volta a ser medido")
    else:
        mc = _marca(a.projeto, a.marca)
        if not mc:
            print("nenhuma marca escolhida: a voz é medida a cada vídeo")
        else:
            v = mc.dados.get("voz") or {}
            if not v:
                print(f"marca {mc.nome}: voz ainda não medida (o primeiro take montado mede)")
            else:
                print(f"marca {mc.nome}: {resumo(v.get('cortes') or [])} "
                      f"(medido em {v.get('medidoEm')}, {v.get('data', '')}"
                      + (", fixado)" if v.get("fixo") else ", cada take é medido de novo)"))


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
