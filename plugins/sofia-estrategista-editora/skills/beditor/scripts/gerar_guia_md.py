#!/usr/bin/env python3
"""
gerar_guia_md.py — o guia como texto para gente ler.

O GUIA.md e sempre gerado do guia.json, nunca escrito a mao: dois arquivos
escritos separadamente divergem no primeiro ajuste. Quem edita, edita o JSON
(ou pede no chat); o markdown e renderizado de novo.
"""
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tempo, direcao  # noqa: E402


def render(guia):
    L = []
    take = guia.get("take") or {}
    L += ["# Guia de edição", "",
          f"take: `{take.get('arquivo', '?')}` · {tempo.ts(take.get('duracaoMs', 0))} · "
          f"branding: {guia.get('branding', '?')}", ""]
    L += ["## Arco", "", guia.get("arco", ""), ""]
    if guia.get("estrutura"):
        L += ["## Estrutura", ""]
        for p in guia["estrutura"]:
            an = (f" · anunciada em {tempo.ts(p['anunciadaEmMs'])}"
                  if p.get("anunciadaEmMs") is not None else "")
            L.append(f"- **{p['nome']}** {tempo.ts(p['deMs'])} → {tempo.ts(p['ateMs'])}{an}")
        L.append("")
    d = guia.get("densidade") or {}
    alvo = d.get("alvoPct", [40, 60])
    L += ["## Densidade", "",
          f"{d.get('previstoPct', '?')}% de motion (alvo {alvo[0]}–{alvo[1]}%)"
          + (f" — {d['justificativa']}" if d.get("justificativa") else ""), ""]
    if guia.get("correcoes"):
        L += ["## Correções", ""]
        for c in guia["correcoes"]:
            L.append(f"- {c.get('momento', '?')}: dito «{c.get('oQueFoiDito', '')}», "
                     f"o certo é «{c.get('oCerto', '')}»"
                     + (f" ({c['fonte']})" if c.get("fonte") else ""))
        L.append("")
    L += ["## Momentos", "",
          "| id | tempo | decisão | entrega | o que está na tela | por quê |",
          "|---|---|---|---|---|---|"]
    for m in guia.get("momentos", []):
        mo = m.get("motion") or {}
        if mo:
            tela = f"**{mo.get('tipo')}** — {mo.get('ideia', '')}<br>{mo.get('movimento', '')}"
            if mo.get("entraAntesMs"):
                tela += f"<br>entra {mo['entraAntesMs']} ms antes"
            if mo.get("familia"):
                tela += f"<br>família `{mo['familia']}`: {mo.get('estado', '')}"
        elif m.get("decisao") == "cortar":
            tela = "*(cortado)*"
        else:
            tela = "você"
        mus = m.get("musica") or {}
        musica = f" · música: {mus['clima']} ({mus['cama']})" if mus else ""
        L.append(f"| {m['id']} | {tempo.ts(m['deMs'])} → {tempo.ts(m['ateMs'])} | {m['decisao']} | "
                 f"{m.get('entrega', '')} | {tela} | {m.get('porque', '')}{musica} |")
    L.append("")
    L += direcao.markdown(guia)
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("guia")
    ap.add_argument("--out")
    a = ap.parse_args()
    md = render(json.loads(Path(a.guia).read_text(encoding="utf-8")))
    if a.out:
        Path(a.out).write_text(md, encoding="utf-8")
    else:
        sys.stdout.write(md)


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
