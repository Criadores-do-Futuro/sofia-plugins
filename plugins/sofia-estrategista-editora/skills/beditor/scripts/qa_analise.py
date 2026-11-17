"""A folha de QA do formato `analise` — medida primeiro, olhada depois, e só se preciso.

    python3 qa_analise.py <projeto/> [--master edicao/master.mp4] [--folha] [--comparar outro.mp4]

Cinco medidas em texto (split edit no lugar, sincronia, buraco de voz, cama,
densidade) e, só com `--folha`, uma folha de contato que cabe no orçamento de
leitura (1 568 px de largura, ver `oficina.folha`).

Por que a folha é opcional: nos projetos 14 e 15 foram lidas 154 imagens, e
cada leitura é um turno inteiro do modelo com o contexto todo atrás. As cinco
medidas abaixo responderam à maioria das perguntas que a folha respondia — a
folha entra quando um número reprova e é preciso ver ONDE, ou na conferência
final de um cartão novo. Regra: primeiro o número; a imagem, só se o número
não bastar.

`--comparar` mede a diferença quadro a quadro entre dois masters (por exemplo
o aprovado e o refeito depois de um ajuste) e diz QUAIS trechos mudaram — é a
prova de que um ajuste pontual não mexeu no que já estava aprovado.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oficina  # noqa: E402
from oficina import FPS  # noqa: E402

L_ALVO, L_MIN = 240, 140


def _cinza(p, tam=(96, 170)):
    return np.asarray(Image.open(p).convert("L").resize(tam), dtype=np.float32)


def split_edit(mapa):
    tab = mapa["tabela"]
    aroll = mapa["aroll"]

    def dif(n):     # diferença entre o quadro n e n+1 do A-ROLL (não do composto)
        if not (1 <= n < len(aroll)):
            return None
        a, b = aroll[n - 1], aroll[n]
        if a == b:
            return 0.0
        return float(np.abs(_cinza(a) - _cinza(b)).mean())

    certos = errados = secas = 0
    for t in tab[1:]:
        L = t.get("splitEditMs", 0)
        if not L:
            secas += 1
            continue
        n_audio = int(t["corteDe"] / 1000 * FPS) + 1
        n_img = n_audio - int(L / 1000 * FPS)
        jan = {n: dif(n) for n in range(n_img - 4, n_audio + 5)}
        jan = {k: v for k, v in jan.items() if v is not None}
        if not jan:
            continue
        pico = max(jan, key=jan.get)
        base = float(np.median(list(jan.values())))
        if jan[pico] < base * 1.8:
            certos += 1
            continue
        perto = [jan[n] for n in range(n_img - 2, n_img + 3) if n in jan]
        if perto and max(perto) >= base * 1.8:
            certos += 1
        else:
            errados += 1
            print(f"  !! emenda em {t['corteDe']/1000:.2f}s: pico da imagem no quadro {pico}, esperado {n_img}")
    print(f"1. split edit: {certos} emendas com a imagem à frente, {errados} fora do lugar, {secas} secas por regra")
    return errados


def envelope(voz_raw):
    SR = 16000
    raw = subprocess.run(["ffmpeg", "-v", "error", "-f", "s16le", "-ar", "48000", "-ac", "2", "-i", str(voz_raw),
                          "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    j = int(0.01 * SR)
    k = len(a) // j
    env = np.sqrt((a[:k * j].reshape(k, j) ** 2).mean(1))
    vivo = env[env > 1e-5]
    lim = max(0.0015, float(np.percentile(vivo, 90)) * 0.08)
    return env, lim


def sincronia(mapa, env, lim):
    sujas = 0
    for t in mapa["tabela"][1:]:
        L = t.get("splitEditMs", 0)
        if not L:
            continue
        i0, i1 = int((t["corteDe"] - L) / 10), int(t["corteDe"] / 10)
        if (env[i0:i1] > lim).sum() * 10 > 80:
            sujas += 1
            print(f"  !! {t['corteDe']/1000:.2f}s: imagem nova entrou sobre FALA")
    print(f"2. sincronia: {sujas} emendas com voz sob a imagem adiantada (tem de ser 0)")
    return sujas


def buraco(env, lim):
    corrida, pior, onde = 0, 0, 0
    for i, v in enumerate(env > lim):
        if not v:
            corrida += 1
            if corrida > pior:
                pior, onde = corrida, i - corrida
        else:
            corrida = 0
    print(f"3. maior buraco de voz: {pior*10} ms em {onde*10//60000}:{(onde*10)%60000/1000:05.2f} (teto 500 ms)")
    return pior * 10


def cama(voz_raw, mix_raw):
    voz = np.frombuffer(Path(voz_raw).read_bytes(), dtype="<i2").astype(np.float32) / 32768.0
    mix = np.frombuffer(Path(mix_raw).read_bytes(), dtype="<i2").astype(np.float32) / 32768.0
    n = min(len(voz), len(mix))
    c = mix[:n] - voz[:n]
    falando = np.abs(voz[:n]) > 0.02
    if not falando.any() or float((c ** 2).mean()) < 1e-12:
        print("4. cama: sem música mensurável")
        return None
    db = 20 * np.log10(np.sqrt((voz[:n][falando] ** 2).mean()) / max(1e-9, np.sqrt((c ** 2).mean())))
    print(f"4. cama {db:.1f} dB abaixo da fala (alvo ~20)")
    return db


def comparar(a, b, passo_s=0.5, lim=None):
    """Onde dois masters diferem: amostra a cada `passo_s` e agrupa em trechos."""
    da = oficina.sonda(a)["dur"]
    db_ = oficina.sonda(b)["dur"]
    print(f"comparar: {Path(a).name} {da:.2f}s × {Path(b).name} {db_.__round__(2)}s")
    ts = np.arange(0.25, min(da, db_), passo_s)
    difs = []
    for t in ts:
        x = np.asarray(oficina.quadro_em(a, t).convert("L").resize((96, 170)), dtype=np.float32)
        y = np.asarray(oficina.quadro_em(b, t).convert("L").resize((96, 170)), dtype=np.float32)
        difs.append(float(np.abs(x - y).mean()))
    difs = np.array(difs)
    # Segmento que veio da cache é o MESMO arquivo: diferença 0,00 exata. Por isso
    # o limiar é baixo. Contra um master de outro pipeline (o aprovado do 15, por
    # exemplo) o ruído de codificação sozinho dá ~2 — aí passe `lim=3.0`.
    lim = 0.5 if lim is None else lim
    trechos, ini = [], None
    for t, d in zip(ts, difs):
        if d > lim and ini is None:
            ini = t
        elif d <= lim and ini is not None:
            trechos.append((ini, t))
            ini = None
    if ini is not None:
        trechos.append((ini, ts[-1]))
    print(f"   diferença média {difs.mean():.2f} · máxima {difs.max():.2f} em {ts[int(difs.argmax())]:.1f}s · "
          f"{len(trechos)} trecho(s) diferente(s): " +
          (", ".join(f"{x:.1f}–{y:.1f}s" for x, y in trechos) or "nenhum"))
    return trechos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("projeto")
    ap.add_argument("--master", default=None)
    ap.add_argument("--folha", action="store_true")
    ap.add_argument("--comparar", default=None, metavar="OUTRO.mp4")
    ap.add_argument("--limiar", type=float, default=None,
                    help="diferença mínima para contar como trecho diferente (padrão 0,5; ~3 entre pipelines distintos)")
    a = ap.parse_args()
    P = Path(a.projeto).resolve()
    ed = P / "edicao"
    of = ed / "oficina"
    master = Path(a.master) if a.master else ed / "master.mp4"
    with oficina.Cronometro(of, "medir", args={"folha": a.folha, "comparar": bool(a.comparar)}):
        _medir(a, ed, of, master)


def _medir(a, ed, of, master):
    mapa = json.loads((of / "mapa.json").read_text(encoding="utf-8"))
    man = json.loads((of / "manifesto.json").read_text(encoding="utf-8")) if (of / "manifesto.json").exists() else {}
    audio = sorted((of / "audio").glob("voz-*.raw"), key=lambda p: p.stat().st_mtime)
    mixes = sorted((of / "audio").glob("mix-*.raw"), key=lambda p: p.stat().st_mtime)
    if not audio or not mixes:
        raise SystemExit("sem voz/mix na oficina — rode render_analise.py antes")
    voz_raw, mix_raw = audio[-1], mixes[-1]

    split_edit(mapa)
    env, lim = envelope(voz_raw)
    sincronia(mapa, env, lim)
    buraco(env, lim)
    cama(voz_raw, mix_raw)
    prov = json.loads((ed / "provas.json").read_text(encoding="utf-8"))
    print(f"5. densidade de cartão {prov['densidadePct']}% (faixa 12–18, teto 25)")
    if man:
        e = man.get("etapas", {})
        s = e.get("segmentos", {})
        print(f"6. rodada: {s.get('refeitos', '?')} segmentos refeitos, {s.get('daCache', '?')} da cache · "
              f"{man.get('total_s', '?')}s")

    if a.comparar:
        comparar(a.comparar, master, lim=a.limiar)

    if a.folha:
        total = mapa["quadros"] / FPS
        segundos = sorted({1.5, 4.0}
                          | {round((c["emS"] + c["ateS"]) / 2, 2) for c in prov["cartoes"]}
                          | {round(m["emS"] + 0.6, 2) for m in prov["marcadores"]}
                          | {round(x, 2) for x in np.linspace(6, total - 3, 12)})
        ims = [oficina.quadro_em(master, s) for s in segundos]
        saida = oficina.folha(ims, ed / "qa.jpg", cols=8,
                              rotulos=[f"{int(s)//60}:{s%60:05.2f}" for s in segundos])
        print(f"folha de QA: {saida}")


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
