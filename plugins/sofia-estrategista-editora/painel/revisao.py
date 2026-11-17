#!/usr/bin/env python3
"""Põe a revisão mais recente de um projeto no painel: o vídeo e o que o render refez.

    python3 painel/revisao.py <projeto/> [--nota "subi o título do M20"]

Pedido do dono, 2026-09-15: *"ao invés de ficar toda hora mandando ver o vídeo novo
na pasta, abra o artifact completo de edição que fizemos, e atualize por lá o vídeo
após cada ajuste."*

Copia `edicao/revisao.mp4` para `painel/revisao/<slug>.mp4` (o proxy leve, ~6 MB —
cabe no limite de 15 MB por arquivo do artifact) e acrescenta uma entrada em
`painel/revisao.json` com a hora, a nota do ajuste e o manifesto da rodada
(quantos segmentos saíram da cache, quanto tempo de máquina). Depois:
`python3 painel/gerar.py` e republicar o painel com
`files: {"revisao/<slug>.mp4": "painel/revisao/<slug>.mp4"}` — só o arquivo novo
sobe; os outros ficam como estão.
"""
import argparse
import json
import re
import shutil
import unicodedata
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
LIMITE = 15_000_000
HISTORICO = 12


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()


def main(argv=None):
    ap = argparse.ArgumentParser(description="revisão do projeto no painel")
    ap.add_argument("projeto")
    ap.add_argument("--nota", default="")
    a = ap.parse_args(argv)
    P = Path(a.projeto).resolve()
    video = P / "edicao" / "revisao.mp4"
    if not video.exists():
        raise SystemExit(f"!! {video} não existe — rode o render com --revisao")
    if video.stat().st_size > LIMITE:
        raise SystemExit(f"!! {video.name} tem {video.stat().st_size/1e6:.1f} MB; o artifact aceita até 15 MB")
    s = slug(P.name)
    destino = RAIZ / "painel" / "revisao" / f"{s}.mp4"
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(video, destino)
    man = P / "edicao" / "oficina" / "manifesto.json"
    rodada = {}
    if man.exists():
        m = json.loads(man.read_text(encoding="utf-8"))
        ult = m[-1] if isinstance(m, list) and m else m
        rodada = {k: ult.get(k) for k in ("etapas", "total_s", "segmentos", "quadros") if isinstance(ult, dict)}
    arq = RAIZ / "painel" / "revisao.json"
    estado = json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {"projetos": {}}
    pj = estado["projetos"].setdefault(s, {"nome": P.name, "video": f"revisao/{s}.mp4", "historico": []})
    pj["video"] = f"revisao/{s}.mp4"
    pj["versao"] = len(pj["historico"]) + 1
    pj["historico"].insert(0, {"quando": datetime.now().strftime("%Y-%m-%dT%H:%M"), "nota": a.nota,
                               "versao": pj["versao"], "rodada": rodada})
    pj["historico"] = pj["historico"][:HISTORICO]
    estado["ultimo"] = s
    arq.write_text(json.dumps(estado, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"revisão v{pj['versao']} de {P.name}: painel/revisao/{s}.mp4 ({destino.stat().st_size/1e6:.1f} MB)")
    print(f'publicar: files {{"revisao/{s}.mp4": "painel/revisao/{s}.mp4"}}')


if __name__ == "__main__":
    main()
