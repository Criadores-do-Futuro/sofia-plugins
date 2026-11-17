#!/usr/bin/env python3
"""
aprender.py — mede um estilo a partir de uma pasta de frames (ou de vídeos).

O que ele faz sozinho, com número: luminância, saturação, contraste, vinheta,
grão no preto, franja cromática, paleta e densidade de borda. Depois agrupa os
frames por semelhança visual e monta uma folha de contato por grupo.

O que ele NÃO faz: dizer o que aquilo significa. Isso é leitura, e leitura é
trabalho do modelo — que abre as folhas de contato e escreve o estilo.
Ver referencias/aprender-estilo.md.

Uso:
  aprender.py --frames pasta/ --nome meu-estilo --out estilos/
  aprender.py --videos pasta/ --nome meu-estilo --out estilos/ --fps 2
"""
import argparse, json, math, shutil, subprocess, sys, tempfile
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image

EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
LADO = 256          # lado de analise
MIN_POR_GRUPO = 4   # abaixo disso o grupo vira "disperso"


# ---------- coleta ---------------------------------------------------------
def extrair_de_videos(pasta, destino, fps):
    destino.mkdir(parents=True, exist_ok=True)
    videos = [p for p in sorted(Path(pasta).rglob("*")) if p.suffix.lower() in {".mp4", ".mov", ".m4v", ".webm"}]
    if not videos:
        sys.exit(f"nenhum video em {pasta}")
    for v in videos:
        subprocess.run(
            ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(v),
             "-vf", f"fps={fps}", "-q:v", "3", str(destino / f"{v.stem}_%04d.jpg")],
            check=False)
    print(f"{len(videos)} video(s) → {len(list(destino.glob('*.jpg')))} frames")
    return destino


def dhash(a):
    g = np.array(Image.fromarray(a).convert("L").resize((9, 8), Image.BILINEAR), dtype=np.int16)
    bits = (g[:, 1:] > g[:, :-1]).flatten()
    return int("".join("1" if b else "0" for b in bits), 2)


def carregar(pasta):
    arquivos = [p for p in sorted(Path(pasta).rglob("*")) if p.suffix.lower() in EXT]
    if not arquivos:
        sys.exit(f"nenhum frame em {pasta}")
    imagens, vistos, caminhos = [], set(), []
    for p in arquivos:
        try:
            im = Image.open(p).convert("RGB")
        except Exception:
            continue
        a = np.asarray(im.resize((LADO, LADO), Image.BILINEAR), dtype=np.uint8)
        h = dhash(a)
        if any(bin(h ^ v).count("1") <= 4 for v in vistos):   # quase igual: descarta
            continue
        vistos.add(h)
        imagens.append(a)
        caminhos.append(p)
    print(f"{len(arquivos)} arquivo(s) · {len(imagens)} depois de tirar repetidos")
    return np.stack(imagens), caminhos


# ---------- medicao --------------------------------------------------------
def luma(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


def sobel(y):
    gx = np.abs(np.diff(y, axis=1, prepend=y[:, :1]))
    gy = np.abs(np.diff(y, axis=0, prepend=y[:1, :]))
    return gx + gy


def medir(a):
    """um frame -> dicionario de numeros"""
    f = a.astype(np.float32)
    y = luma(f)
    mx, mn = f.max(axis=2), f.min(axis=2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    g = sobel(y)

    # vinheta: centro contra cantos
    h, w = y.shape
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((yy - h / 2) / (h / 2)) ** 2 + ((xx - w / 2) / (w / 2)) ** 2)
    centro, canto = y[r < 0.45].mean(), y[r > 0.95].mean()

    # grao no preto: desvio local nas areas escuras e lisas.
    # o limiar de "liso" nao pode ser percentil: em quadro quase todo preto o
    # percentil 40 do gradiente e zero e a mascara sai vazia.
    escuro = (y < max(np.percentile(y, 25), 8)) & (g <= 6)
    if escuro.sum() < 400:
        escuro = y < max(np.percentile(y, 40), 8)
    grao = float(y[escuro].std()) if escuro.sum() > 200 else 0.0

    # cor na borda: diferenca R-B na borda descontando o liso.
    # ATENCAO: isto NAO separa aberracao cromatica de luz de contorno colorida.
    # Um valor alto significa "as bordas sao coloridas"; qual das duas causas e,
    # so olhando a folha de contato. O agente resolve isso.
    borda = g > max(np.percentile(g, 96), 8)
    liso = g <= 6
    rb = np.abs(f[..., 0] - f[..., 2])
    franja = (float(rb[borda].mean() - rb[liso].mean())
              if borda.sum() > 100 and liso.sum() > 100 else 0.0)

    p05, p95 = np.percentile(y, [5, 95])
    return {
        "y_mediana": float(np.median(y)),
        "preto": float(p05),          # onde o preto realmente assenta
        "branco": float(p95),         # onde a alta luz e segurada
        "y_media": float(y.mean()),
        "pct_abaixo_40": float((y < 40).mean() * 100),
        "pct_acima_235": float((y > 235).mean() * 100),
        "saturacao": float(sat.mean()),
        "contraste": float(y.std()),
        "vinheta": float(1 - canto / max(centro, 1e-6)),
        "grao_no_preto": grao,
        "cor_na_borda": franja,
        "densidade_borda": float((g > 24).mean() * 100),
        "temperatura": float(f[..., 0].mean() - f[..., 2].mean()),
    }


def paleta(imagens, n=6, amostras=60000):
    px = imagens.reshape(-1, 3).astype(np.float32)
    idx = np.random.default_rng(7).choice(len(px), size=min(amostras, len(px)), replace=False)
    px = px[idx]
    c = kmeans(px, n, iteracoes=14)[0]
    ordem = np.argsort(luma(c[None, :, :])[0])
    return ["#%02X%02X%02X" % tuple(int(v) for v in c[i]) for i in ordem]


# ---------- agrupamento ----------------------------------------------------
def vetor(a):
    """assinatura de ESTILO: cor, textura e distribuicao de luz — nao assunto"""
    f = a.astype(np.float32)
    y = luma(f)
    hist_y = np.histogram(y, bins=16, range=(0, 256))[0] / y.size
    mx, mn = f.max(axis=2), f.min(axis=2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    hist_s = np.histogram(sat, bins=8, range=(0, 1))[0] / sat.size
    g = sobel(y)
    hist_g = np.histogram(g, bins=8, range=(0, 128))[0] / g.size
    mini = np.asarray(Image.fromarray(a).resize((8, 8), Image.BILINEAR), dtype=np.float32).reshape(-1) / 255
    v = np.concatenate([hist_y * 3, hist_s * 2, hist_g * 2, mini])
    return v / (np.linalg.norm(v) + 1e-9)


def kmeans(X, k, iteracoes=40, semente=7):
    rng = np.random.default_rng(semente)
    n = len(X)
    k = min(k, n)
    # k-means++
    centros = [X[rng.integers(n)]]
    for _ in range(k - 1):
        d = np.min(((X[:, None, :] - np.array(centros)[None]) ** 2).sum(2), axis=1)
        p = d / max(d.sum(), 1e-9)
        centros.append(X[rng.choice(n, p=p)])
    C = np.array(centros)
    rot = np.zeros(n, dtype=int)
    for _ in range(iteracoes):
        rot = np.argmin(((X[:, None, :] - C[None]) ** 2).sum(2), axis=1)
        for j in range(k):
            m = rot == j
            if m.any():
                C[j] = X[m].mean(0)
    return C, rot


def folha_de_contato(imagens, indices, destino, colunas=5, celula=220):
    sel = indices[: colunas * 4]
    linhas = math.ceil(len(sel) / colunas)
    folha = Image.new("RGB", (colunas * celula, linhas * celula), (14, 14, 14))
    for n, i in enumerate(sel):
        im = Image.fromarray(imagens[i]).resize((celula - 6, celula - 6), Image.BILINEAR)
        folha.paste(im, ((n % colunas) * celula + 3, (n // colunas) * celula + 3))
    folha.save(destino, quality=88)


# ---------- saida ----------------------------------------------------------
def agregar(medidas):
    ch = medidas[0].keys()
    return {c: round(float(np.median([m[c] for m in medidas])), 3) for c in ch}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", help="pasta com imagens")
    ap.add_argument("--videos", help="pasta com videos (extrai frames)")
    ap.add_argument("--fps", type=float, default=2.0)
    ap.add_argument("--nome", required=True)
    ap.add_argument("--out", default="estilos")
    ap.add_argument("--grupos", type=int, default=6)
    a = ap.parse_args()

    tmp = None
    if a.videos:
        tmp = Path(tempfile.mkdtemp(prefix="beditor-frames-"))
        origem = extrair_de_videos(a.videos, tmp, a.fps)
    elif a.frames:
        origem = Path(a.frames)
    else:
        sys.exit("informe --frames ou --videos")

    imagens, caminhos = carregar(origem)
    medidas = [medir(im) for im in imagens]
    X = np.stack([vetor(im) for im in imagens])
    _, rot = kmeans(X, a.grupos)

    destino = Path(a.out) / a.nome
    (destino / "folhas").mkdir(parents=True, exist_ok=True)

    grupos = []
    for j in sorted(set(rot)):
        idx = np.where(rot == j)[0]
        if len(idx) < MIN_POR_GRUPO:
            continue
        centro = X[idx].mean(0)
        ordem = idx[np.argsort(((X[idx] - centro) ** 2).sum(1))]   # os mais tipicos primeiro
        nome = f"g{len(grupos):02d}"
        folha_de_contato(imagens, ordem, destino / "folhas" / f"{nome}.jpg")
        grupos.append({
            "grupo": nome,
            "frames": int(len(idx)),
            "medida": agregar([medidas[i] for i in idx]),
            "paleta": paleta(imagens[ordem[:24]]),
            "folha": f"folhas/{nome}.jpg",
            "exemplos": [str(caminhos[i]) for i in ordem[:4]],
            "leitura": "",     # preenchido pelo agente analista-de-estilo
            "quando_usar": "",
        })

    global_ = agregar(medidas)
    ficha = {
        "estilo": a.nome,
        "frames_analisados": int(len(imagens)),
        "medida_global": global_,
        "paleta_global": paleta(imagens),
        "grupos": grupos,
        "confianca": {
            "medido_direto": ["preto", "branco", "y_mediana", "pct_abaixo_40", "pct_acima_235",
                              "saturacao", "contraste", "vinheta", "temperatura", "paleta"],
            "aproximado": ["grao_no_preto (some com compressao forte)",
                           "cor_na_borda (nao separa aberracao de luz de contorno)",
                           "densidade_borda (conta textura junto com contorno)"],
            "so_olhando": ["tipografia", "movimento de camera", "ritmo de corte",
                           "o que cada grupo significa", "quando usar cada um"],
        },
        "leitura": "",
        "preset_sugerido": {
            "fundo": "#%02X%02X%02X" % ((int(round(global_["preto"])),) * 3),
            "sujeito": "#%02X%02X%02X" % ((int(round(global_["branco"])),) * 3),
            # calibrado contra o unico corpus em que existem os dois numeros: o
            # canal de referencia mede grao_no_preto 0,9 e usa opacidade 0,4.
            "grao": round(min(global_["grao_no_preto"] * 0.45, 1.0), 2),
            # so um chute grosseiro: confirme na folha de contato antes de fixar
            "aberracao_a_confirmar": 3 if global_["cor_na_borda"] > 14 else (2 if global_["cor_na_borda"] > 6 else 0),
            "vinheta": round(max(0.0, min(global_["vinheta"], 1.0)), 2),
            "dessaturacao_pct": round((1 - global_["saturacao"] / 0.35) * 100) if global_["saturacao"] < 0.35 else 0,
        },
    }
    (destino / "medicoes.json").write_text(json.dumps(ficha, ensure_ascii=False, indent=2), encoding="utf-8")

    g = global_
    print(f"\n=== {a.nome} · {len(imagens)} frames · {len(grupos)} grupos ===")
    print(f"  preto assenta em     {g['preto']:.0f}/255")
    print(f"  branco segurado em   {g['branco']:.0f}/255")
    print(f"  luminancia mediana   {g['y_mediana']:.0f}/255")
    print(f"  abaixo de 40         {g['pct_abaixo_40']:.0f}%")
    print(f"  acima de 235         {g['pct_acima_235']:.2f}%")
    print(f"  saturacao            {g['saturacao']:.2f}")
    print(f"  contraste            {g['contraste']:.0f}")
    print(f"  vinheta              {g['vinheta']:.2f}")
    print(f"  grao no preto        {g['grao_no_preto']:.1f}")
    print(f"  cor na borda         {g['cor_na_borda']:.1f}  (aberracao ou luz de contorno — olhe a folha)")
    print(f"  temperatura (R-B)    {g['temperatura']:+.1f}")
    print(f"  paleta               {' '.join(ficha['paleta_global'])}")
    print(f"\n  folhas de contato em {destino/'folhas'}")
    print("  abra as folhas, leia o que ve e preencha 'leitura' e 'quando_usar'")
    print("  — ou despache o agente analista-de-estilo, que faz isso.")
    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
