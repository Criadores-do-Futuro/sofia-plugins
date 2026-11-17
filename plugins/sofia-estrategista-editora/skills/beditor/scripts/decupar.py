"""Da decisão do diretor ao `dados.json` que o corte e o render entendem.

    python3 decupar.py <projeto/> [--estrutura]

O que o diretor escreve em `edicao/dados.json` é pouco e é dele: os takes
(`takes`), os momentos escolhidos com o take e o segundo LOCAL de cada um
(`momentos[].take`, `localDeS`, `localAteS`, `decisao`, `porque`), as recusas,
os cortes internos, as correções de grafia. O resto é conta, e conta não se
faz à mão duas vezes:

  - `offsetMs` de cada take na LINHA DO TEMPO VIRTUAL (o primeiro em 0, os
    seguintes em múltiplos de 100 s depois do anterior, com silêncio digital
    nos vãos — `formato-analise.md`, «Costurar takes diferentes»);
  - `palavras` em ms virtuais, a partir do `.whisper.json` de cada take;
  - `deMs`/`ateMs` virtuais de cada momento, e a `fala` quando não foi escrita;
  - `take.duracaoMs`, e a `tabela` inicial (um pedaço por momento, sem corte);
  - o wav da linha virtual, `edicao/oficina/linha.<chave>.wav`, que é o que o
    `silencio.py` escuta. A chave é o conteúdo dos takes mais os offsets: mudar
    a decupagem não o refaz; mudar um take, sim.

Nos projetos 14 e 15 isto foi um script por projeto na pasta de rascunho
(`cortar15.py`), reescrito e reeditado dezenas de vezes — é o desperdício nº 2
de `eficiencia.md`. Aqui é uma chamada, e o que ela decide fica escrito.

`--estrutura`: depois do `silencio.py`, preenche `deMs`/`ateMs`/`pct` de cada
bloco de `estrutura` (que o diretor escreve só com `nome`, `de`, `ate` em ids de
momento) a partir da tabela cortada — é o que permite conferir os portões do
formato (capítulo 1 em 16–22 %, 2 em 44–50 %, 3 em 65–75 %) sem assistir.
"""
import json
import math
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oficina  # noqa: E402

SR = 16000          # o mesmo do transcrever.py e do silencio.py
PASSO_OFFSET_MS = 100_000
FOLGA_ENTRE_TAKES_MS = 10_000


def _whisper(transcricao, take_arq):
    p = transcricao / f"{Path(take_arq).stem}.whisper.json"
    if not p.exists():
        raise SystemExit(f"!! falta a transcrição de {Path(take_arq).name}: rode transcrever.py primeiro ({p})")
    return json.loads(p.read_text(encoding="utf-8"))


def _wav_do_take(transcricao, take_arq, ident):
    p = transcricao / f"{Path(take_arq).stem}.{ident}.wav"
    if not p.exists():
        raise SystemExit(f"!! falta o wav do take {Path(take_arq).name} ({p}); rode transcrever.py")
    return p


def _pcm(wav):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(wav), "-f", "s16le", "-ac", "1",
                          "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.int16)


def offsets(takes, duracoes):
    """Offsets que faltam, em ordem de id: cada take começa no múltiplo de 100 s
    seguinte ao fim do anterior mais 10 s de folga. Os que o diretor já fixou ficam."""
    cursor = 0
    for tid in sorted(takes):
        t = takes[tid]
        if "offsetMs" not in t:
            t["offsetMs"] = 0 if cursor == 0 else int(math.ceil(cursor / PASSO_OFFSET_MS) * PASSO_OFFSET_MS)
        cursor = max(cursor, t["offsetMs"] + duracoes[tid] + FOLGA_ENTRE_TAKES_MS)
    return takes


def palavras_virtuais(takes, whispers):
    W = []
    for tid, t in takes.items():
        off = t["offsetMs"]
        for w in whispers[tid].get("words", []):
            p = (w.get("word") or w.get("p") or "").strip()
            de, ate = w.get("start", w.get("de", 0)), w.get("end", w.get("ate", 0))
            if not p or ate <= de:
                continue
            W.append({"p": p, "de": int(round(off + de * 1000)), "ate": int(round(off + ate * 1000)), "take": tid})
    W.sort(key=lambda w: (w["de"], w["ate"]))
    return W


def momentos_virtuais(momentos, takes, W, duracoes):
    ids = [m["id"] for m in momentos]
    if len(ids) != len(set(ids)):
        raise SystemExit(f"!! ids de momento repetidos: {sorted(i for i in ids if ids.count(i) > 1)}")
    for m in momentos:
        tid = m["take"]
        if tid not in takes:
            raise SystemExit(f"!! {m['id']} aponta para o take «{tid}», que não está em `takes`")
        off = takes[tid]["offsetMs"]
        if "localDeS" in m and "localAteS" in m:
            m["deMs"] = int(round(off + m["localDeS"] * 1000))
            m["ateMs"] = int(round(off + m["localAteS"] * 1000))
        elif "deMs" in m and "ateMs" in m:
            m["localDeS"] = round((m["deMs"] - off) / 1000, 2)
            m["localAteS"] = round((m["ateMs"] - off) / 1000, 2)
        else:
            raise SystemExit(f"!! {m['id']} precisa de localDeS/localAteS (segundos do take) ou deMs/ateMs")
        if m["localDeS"] < 0 or m["localAteS"] * 1000 > duracoes[tid] + 500:
            raise SystemExit(f"!! {m['id']} sai do take {tid} ({m['localDeS']}–{m['localAteS']} s; take tem {duracoes[tid]/1000:.1f} s)")
        if m["ateMs"] <= m["deMs"]:
            raise SystemExit(f"!! {m['id']} termina antes de começar")
        if not m.get("fala"):
            m["fala"] = " ".join(w["p"] for w in W if w["take"] == tid and w["de"] >= m["deMs"] - 40 and w["ate"] <= m["ateMs"] + 40)
        m.setdefault("decisao", "aroll")
    return momentos


def tabela_inicial(momentos):
    tab, cursor = [], 0
    for m in momentos:
        if m.get("decisao") == "cortar":
            continue
        dur = m["ateMs"] - m["deMs"]
        tab.append({"brutoDe": m["deMs"], "brutoAte": m["ateMs"], "momento": m["id"], "take": m["take"],
                    "doDiretor": True, "corteDe": cursor, "corteAte": cursor + dur,
                    "folgaMs": 0, "folgaLimpa": False, "remontagem": False, "caudaCaladaMs": 0})
        cursor += dur
    return tab


def linha_virtual(oficina_dir, takes, wavs, duracao_ms):
    """O wav costurado, nomeado pelo conteúdo. Existe → não se refaz."""
    chave = oficina.chave({"takes": {k: [v["ident"], v["offsetMs"]] for k, v in takes.items()}, "sr": SR})
    saida = oficina_dir / f"linha.{chave}.wav"
    if saida.exists():
        return saida, False
    buf = np.zeros(int(duracao_ms / 1000 * SR) + SR, dtype=np.int16)
    for tid, t in takes.items():
        a = _pcm(wavs[tid])
        i0 = int(t["offsetMs"] / 1000 * SR)
        a = a[: max(0, len(buf) - i0)]
        buf[i0:i0 + len(a)] = a
    tmp = saida.with_suffix(".parcial")
    with wave.open(str(tmp), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(buf.tobytes())
    tmp.rename(saida)
    return saida, True


def estrutura(d):
    """deMs/ateMs/pct de cada bloco, lidos da tabela já cortada."""
    tab = d["tabela"]
    fim = tab[-1]["corteAte"]
    por_momento = {}
    for r in tab:
        a, b = por_momento.get(r["momento"], (r["corteDe"], r["corteAte"]))
        por_momento[r["momento"]] = (min(a, r["corteDe"]), max(b, r["corteAte"]))
    for bloco in d.get("estrutura", []):
        if bloco["de"] not in por_momento or bloco["ate"] not in por_momento:
            raise SystemExit(f"!! estrutura «{bloco['nome']}» cita momento fora da tabela ({bloco['de']}–{bloco['ate']})")
        bloco["deMs"] = por_momento[bloco["de"]][0]
        bloco["ateMs"] = por_momento[bloco["ate"]][1]
        bloco["pct"] = [round(bloco["deMs"] / fim * 100, 1), round(bloco["ateMs"] / fim * 100, 1)]
    return d.get("estrutura", [])


def tabela_por_momento(d):
    """Onde cada momento cai no corte, em segundos — para escrever o plano.json."""
    saida = {}
    for r in d["tabela"]:
        a, b = saida.get(r["momento"], (r["corteDe"], r["corteAte"]))
        saida[r["momento"]] = (min(a, r["corteDe"]), max(b, r["corteAte"]))
    return saida


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    P = Path(sys.argv[1]).resolve()
    ed = P / "edicao"
    of = ed / "oficina"
    dados = ed / "dados.json"
    d = json.loads(dados.read_text(encoding="utf-8"))

    if "--em" in sys.argv:
        # `--em 004:16.30 005:9.0 …` → onde cada segundo LOCAL do take cai no CORTE.
        # É a conta que o plano.json precisa (os inserts falam em segundos do corte) e
        # que, feita de cabeça, errou por meio segundo em cada cartão do 14.
        for par in sys.argv[sys.argv.index("--em") + 1:]:
            tid, loc = par.split(":")
            ms = d["takes"][tid]["offsetMs"] + float(loc) * 1000
            achou = [r for r in d["tabela"] if r["brutoDe"] <= ms <= r["brutoAte"]]
            if achou:
                r = achou[0]
                print(f"{par}  →  {(r['corteDe'] + ms - r['brutoDe'])/1000:7.2f} s  ({r['momento']})")
            else:
                print(f"{par}  →  fora do corte (silêncio removido ou momento recusado)")
        return

    with oficina.Cronometro(of, "decupar", args={"estrutura": "--estrutura" in sys.argv}) as cron:
        if "--estrutura" in sys.argv:
            blocos = estrutura(d)
            dados.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
            fim = d["tabela"][-1]["corteAte"] / 1000
            print(f"corte: {fim:.1f} s · {len(d['tabela'])} pedaços")
            for b in blocos:
                print(f"  {b['pct'][0]:5.1f}–{b['pct'][1]:5.1f} %  {b['deMs']/1000:6.1f}–{b['ateMs']/1000:6.1f} s  {b['nome']}")
            print("momentos no corte (s):")
            for mid, (a, b) in tabela_por_momento(d).items():
                print(f"  {mid} {a/1000:7.2f}–{b/1000:7.2f}")
            cron.extra.update(blocos=len(blocos), fimS=round(fim, 1))
            return

        transcricao = of / "transcricao"
        takes = d["takes"]
        for tid, t in takes.items():
            arq = Path(t["arq"])
            t["arq"] = str(arq if arq.is_absolute() else (P / arq))
            t["ident"] = oficina.identidade(t["arq"])
        whispers = {tid: _whisper(transcricao, t["arq"]) for tid, t in takes.items()}
        wavs = {tid: _wav_do_take(transcricao, t["arq"], t["ident"]) for tid, t in takes.items()}
        duracoes = {tid: int(round(oficina.sonda(t["arq"])["dur"] * 1000)) for tid, t in takes.items()}
        offsets(takes, duracoes)
        W = palavras_virtuais(takes, whispers)
        d["momentos"] = momentos_virtuais(d["momentos"], takes, W, duracoes)
        # cortes internos também se escrevem no segundo LOCAL do take; o silencio.py
        # os lê em ms virtuais, como os momentos
        for ci in d.get("cortesInternos", []):
            if "localDeS" in ci and ci["take"] in takes:
                off = takes[ci["take"]]["offsetMs"]
                ci["deMs"] = int(round(off + ci["localDeS"] * 1000))
                ci["ateMs"] = int(round(off + ci["localAteS"] * 1000))
        d["palavras"] = [{"p": w["p"], "de": w["de"], "ate": w["ate"]} for w in W]
        fim_virtual = max(t["offsetMs"] + duracoes[tid] for tid, t in takes.items())
        d["take"] = {"fps": int(round(oficina.sonda(next(iter(takes.values()))["arq"])["fps"])), "duracaoMs": fim_virtual}
        d["tabela"] = tabela_inicial(d["momentos"])
        d.setdefault("formato", "analise")
        d.setdefault("projeto", P.name)
        d["takes"] = {k: {"arq": v["arq"], "offsetMs": v["offsetMs"]} for k, v in takes.items()}
        linha, refeita = linha_virtual(of, {k: {**takes[k]} for k in takes}, wavs, fim_virtual)
        d["linha"] = str(linha.relative_to(P))
        dados.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        bruto = d["tabela"][-1]["corteAte"] / 1000 if d["tabela"] else 0
        print(f"{len(takes)} takes · offsets " + ", ".join(f"{k}@{v['offsetMs']//1000}s" for k, v in sorted(takes.items())))
        print(f"{len(W)} palavras · {len(d['momentos'])} momentos · {bruto:.1f} s antes do corte de silêncio")
        print(f"linha virtual: {linha} ({'refeita' if refeita else 'da cache'})")
        print(f"próximo: silencio.py {dados} {linha}")
        cron.extra.update(takes=len(takes), palavras=len(W), momentos=len(d["momentos"]), linhaRefeita=refeita)


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
