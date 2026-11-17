#!/usr/bin/env python3
"""
medir.py — ninguem declara sucesso sem medir o quadro.

Tres rodadas de "tela preta" passaram porque a unica verificacao era o olho
de quem monta. Aqui o preview e medido: blackdetect por trecho (com o plano
correspondente), cobertura da timeline e loudness. Falha e falha.

Uso: medir.py preview.mp4 --plano plano.json [--voz voz.m4a --cama trilha.m4a --cama-volume 0.5]
"""
import argparse, json, math, re, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import acabamento  # noqa: E402

PRETO_TOTAL_MAX_S = 1.5
PRETO_TRECHO_MAX_S = 0.5
LUFS_FAIXA = (-16.0, -12.0)
SEPARACAO_MIN_DB = 14.0
PRETO_LEGITIMO = {"palavras"}   # uma palavra so no quadro e legitimo


def trechos_pretos(video, d=0.10, pix_th=0.15, pic_th=0.999):
    """preto = 99,9% dos pixels abaixo de pix_th. O padrao do blackdetect (98%)
    acusa uma cartela com duas palavras brancas — tipografia sobre fundo
    escuro e a lingua do canal, nao defeito. 99,9% so deixa passar o quadro
    onde NADA foi desenhado."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(video), "-vf",
                        f"blackdetect=d={d}:pix_th={pix_th}:pic_th={pic_th}", "-an", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return [(float(a), float(b)) for a, b in
            re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", r.stderr)]


def _plano_em(plano, s):
    ms = s * 1000
    for p in plano["planos"]:
        if p["t0"] <= ms < p["t1"]:
            return p
    return None


def avaliar(video, plano, voz=None, cama=None, cama_volume=1.0):
    erros = []
    total, pior = 0.0, []
    for a, b in trechos_pretos(video):
        p = _plano_em(plano, (a + b) / 2)
        dur = b - a
        total += dur
        legit = p is not None and p["tipo"] in PRETO_LEGITIMO
        if dur >= PRETO_TRECHO_MAX_S and not legit:
            onde = f"{p['id']} {p['tipo']}" if p else "nenhum plano"
            pior.append(f"{a:.1f}–{b:.1f}s ({dur:.1f}s) em {onde}")
    if total > PRETO_TOTAL_MAX_S:
        erros.append(f"preto: {total:.1f}s no total (limite {PRETO_TOTAL_MAX_S}s)")
    for t in pior:
        erros.append(f"preto: {t}")

    ps = plano["planos"]
    if not ps or ps[0]["t0"] != 0 or ps[-1]["t1"] != plano["duracaoMs"] or \
            any(b["t0"] != a["t1"] for a, b in zip(ps, ps[1:])):
        erros.append("cobertura: os planos nao cobrem 0 → duracao sem buraco")

    if voz:
        lv = acabamento.lufs(voz)
        if not (LUFS_FAIXA[0] <= lv <= LUFS_FAIXA[1]):
            erros.append(f"loudness: voz em {lv:.1f} LUFS, fora de {LUFS_FAIXA}")
        # `semMusica` mantém o caminho nominal no chamador, mas não cria o
        # arquivo e define volume zero. Nessa escolha não há cama para medir.
        if cama and Path(cama).exists() and cama_volume > 0:
            lc = acabamento.lufs(cama) + 20 * math.log10(max(1e-6, cama_volume))
            if lv - lc < SEPARACAO_MIN_DB:
                erros.append(f"cama: {lv - lc:.1f} dB abaixo da voz (minimo {SEPARACAO_MIN_DB})")
    return erros


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--plano", required=True)
    ap.add_argument("--voz")
    ap.add_argument("--cama")
    ap.add_argument("--cama-volume", type=float, default=1.0)
    a = ap.parse_args()
    plano = json.loads(Path(a.plano).read_text(encoding="utf-8"))
    erros = avaliar(a.video, plano, a.voz, a.cama, a.cama_volume)
    for e in erros:
        print("·", e)
    print("medicao: " + ("FALHOU" if erros else "ok"))
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
