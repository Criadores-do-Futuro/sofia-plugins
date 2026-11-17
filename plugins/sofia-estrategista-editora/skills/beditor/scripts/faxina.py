#!/usr/bin/env python3
"""Faxina do projeto publicado: apaga o que o render refaz sozinho, guarda o que custou decisão.

    python3 faxina.py <projeto/>          # mostra o que sairia e quanto libera
    python3 faxina.py <projeto/> --sim    # apaga

Medido no vídeo 16 depois de publicado: 4,9 GB em `edicao/`, dos quais só uns
MB são decisão (dados, plano, provas, publicação). O resto é cache — segmentos
compostos (934 MB), recortes do autor (1 GB), quadros extraídos (474 MB), áudio
intermediário (387 MB) — e masters de versões antigas (≈ 900 MB).

Só roda em projeto PUBLICADO (`edicao/entrega/agendado.json` existe): antes disso
a cache é justamente o que faz um ajuste custar segundos em vez de minutos.

Fica: dados.json, plano.json, provas.json, publicacao.json, entrega/ (o master
publicado e a capa), master.mp4, telemetria, custos, manifesto e a transcrição
dos takes (refazer custa minutos de Whisper). Sai: `oficina/seg`, `matte`, `aroll`,
`audio`, `clipe`, `janela`, `lupa`, `transcricao-acervo`, os WAV de linha e
`master-v*.mp4` / `revisao.mp4`. Um reajuste depois disso refaz a cache inteira
na primeira rodada — é o preço, e é pago só se o vídeo voltar para a mesa.
"""
import argparse
import shutil
from pathlib import Path

CACHE = ("seg", "matte", "aroll", "audio", "clipe", "janela", "lupa", "transcricao-acervo", "rosto")


def alvos(P):
    ed = P / "edicao"
    of = ed / "oficina"
    out = [of / n for n in CACHE if (of / n).exists()]
    out += sorted(of.glob("linha.*.wav"))
    out += sorted(ed.glob("master-v*.mp4"))
    if (ed / "revisao.mp4").exists():
        out.append(ed / "revisao.mp4")
    return out


def tamanho(p):
    if p.is_dir():
        return sum(x.stat().st_size for x in p.rglob("*") if x.is_file())
    return p.stat().st_size


def main(argv=None):
    ap = argparse.ArgumentParser(description="apaga a cache de um projeto já publicado")
    ap.add_argument("projeto")
    ap.add_argument("--sim", action="store_true", help="apaga de verdade (sem isto, só mostra)")
    a = ap.parse_args(argv)
    P = Path(a.projeto).resolve()
    if not (P / "edicao" / "entrega" / "agendado.json").exists():
        raise SystemExit(f"!! {P.name} não tem edicao/entrega/agendado.json — não foi publicado; a cache fica.")
    total = 0
    for p in alvos(P):
        t = tamanho(p)
        total += t
        print(f"  {t/1e6:8.1f} MB  {p.relative_to(P)}")
        if a.sim:
            shutil.rmtree(p) if p.is_dir() else p.unlink()
    print(f"{total/1e9:.2f} GB {'liberados' if a.sim else 'sairiam (rode com --sim)'}")


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
