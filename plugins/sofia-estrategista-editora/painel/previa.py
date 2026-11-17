#!/usr/bin/env python3
"""A edição como dados: o que a mesa precisa para mostrar o vídeo pronto SEM render.

    python3 painel/previa.py <projeto/guia> [--nota "zoom só nas ênfases"]

Pedido do dono, 2026-09-27: *"se a edição fosse um xml que afeta o preview, mas
não renderiza necessariamente pra eu aprovar, mostrando no artifact como eu
sempre planejei para este artifact, faria tudo ser muito mais rápido e
reaproveitado e edições não levariam 30 minutos, 40 minutos, nem custariam
tanto tokens"*.

O que custa no render final é a composição: reenquadrar cada pedaço, desenhar a
legenda quadro a quadro no Chrome e juntar tudo. Nada disso é preciso para
aprovar. A mesa recebe três arquivos e faz o resto ao vivo:

  - `take.mp4`: `public/fonte.mp4` + `voz.m4a`, já na linha do tempo do corte
    (pausas apertadas), em 360x640 e com bitrate calculado para caber nos 15 MB
    por arquivo do artifact. Cache pelo estado das fontes: mudar zoom, legenda
    ou hook NÃO refaz o proxy.
  - `edicao.json`: as faixas do `montador.faixas()` — as mesmas funções, os
    mesmos picos de ênfase, o mesmo recorte do rosto — em números: de, até,
    zoom, recorte (x, y) no quadro de 1080x1920. A mesa aplica isso como
    `transform` no vídeo.
  - `legenda.html`: a página EXATA do `legenda_hf.html_legenda()`, a mesma que
    o hyperframes grava no render. A mesa carrega por cima do vídeo e só faz
    `seek()` na timeline dela. O que se aprova é o que vai ao ar.

Depois: republicar a mesa com
`files: {"previa/edicao.json": ..., "previa/legenda.html": ..., "previa/take.mp4": ...}`
— o take só quando o script disser que mudou.
"""
import argparse
import hashlib
import json
import re
import subprocess
import unicodedata
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "skills" / "beditor" / "scripts"))
import compor        # noqa: E402
import legenda_hf    # noqa: E402
import montador      # noqa: E402

LIMITE = 14_500_000          # folga sob os 15 MB por arquivo do artifact
PROXY_W, PROXY_H = 360, 640
AUDIO_KBPS = 48


def _estado(arq):
    s = Path(arq).stat()
    return f"{Path(arq).resolve()}:{s.st_size}:{s.st_mtime_ns}"


def proxy(fonte, voz, offset_s, dur_s, destino):
    """o take leve. Devolve True se precisou refazer."""
    chave = hashlib.sha256(f"{_estado(fonte)}|{_estado(voz)}|{offset_s}|{PROXY_W}".encode()).hexdigest()
    marca = destino.with_name(destino.name + ".sha256")
    if destino.exists() and marca.exists() and marca.read_text().strip() == chave:
        return False
    total_kbps = LIMITE * 8 / 1000 / max(dur_s, 1)
    v_kbps = int(max(90, min(700, total_kbps * 0.92 - AUDIO_KBPS)))
    for tentativa in range(3):
        entrada_voz = (["-itsoffset", f"{offset_s:.3f}"] if offset_s >= 0 else ["-ss", f"{-offset_s:.3f}"])
        cmd = ["ffmpeg", "-y", "-nostdin", "-v", "error", "-i", str(fonte), *entrada_voz, "-i", str(voz),
               "-map", "0:v:0", "-map", "1:a:0",
               "-vf", f"scale={PROXY_W}:{PROXY_H}:force_original_aspect_ratio=decrease,"
                      f"pad={PROXY_W}:{PROXY_H}:(ow-iw)/2:(oh-ih)/2,fps=30",
               "-c:v", "libx264", "-preset", "veryfast", "-b:v", f"{v_kbps}k",
               "-maxrate", f"{int(v_kbps * 1.4)}k", "-bufsize", f"{v_kbps * 2}k",
               # um quadro-chave por segundo: a mesa pula de ponto em ponto
               "-g", "30", "-keyint_min", "30", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", f"{AUDIO_KBPS}k", "-ac", "1",
               "-t", f"{dur_s:.3f}", "-movflags", "+faststart", str(destino)]
        subprocess.run(cmd, check=True)
        if destino.stat().st_size <= LIMITE:
            marca.write_text(chave)
            return True
        v_kbps = int(v_kbps * 0.8)
        print(f"  proxy passou de {LIMITE/1e6:.1f} MB; refazendo a {v_kbps} kbps", flush=True)
    raise SystemExit(f"!! proxy não coube em {LIMITE/1e6:.1f} MB")


def recorte(f, W, H, amostras):
    """(x, y) do recorte no quadro ampliado — a mesma conta do `_vf_aroll`."""
    z = float(f.get("zoom") or 1.0)
    if z <= 1.001:
        return [0, 0]
    if amostras:
        return list(montador._crop_do_rosto(f, amostras, W, H, z))
    zw, zh = int(W * z) // 2 * 2, int(H * z) // 2 * 2
    b = min(0.28, 44 * z / max(1.0, H * (z - 1)))
    return [(zw - W) // 2, int((zh - H) * b)]


def main(argv=None):
    ap = argparse.ArgumentParser(description="a edição como dados, para a mesa")
    ap.add_argument("projeto", help="a pasta com plano.json, public/ e out/ (a guia)")
    ap.add_argument("--nota", default="")
    ap.add_argument("--saida", default=None, help="padrao: painel/previa/<projeto>/")
    a = ap.parse_args(argv)

    P = Path(a.projeto).resolve()
    plano = json.loads((P / "plano.json").read_text(encoding="utf-8"))
    captions = json.loads((P / "public" / "captions.json").read_text(encoding="utf-8"))
    W, H = plano["largura"], plano["altura"]
    dur = plano["duracaoMs"] / 1000
    fonte = P / "public" / plano["fonteVideo"]
    voz = P / "public" / (plano.get("fonteAudio") or plano["fonteVideo"])
    offset = (plano.get("fonteOffsetMs") or 0) / 1000
    nome = P.parent.name if P.name == "guia" else P.name
    slug = re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", nome).encode("ascii", "ignore")
                  .decode().lower()).strip("-")
    out = Path(a.saida) if a.saida else RAIZ / "painel" / "previa" / slug
    out.mkdir(parents=True, exist_ok=True)

    # 1. as faixas: as mesmas funções do render, sem cortar nada
    fs = montador.faixas(plano, P / "out" / "hf", fonte=voz, offset_audio_s=offset)
    # onde o rosto esta: o mesmo rastreamento local do montador (cacheado em
    # out/rosto.json), senao o zoom da previa cairia num recorte diferente do render
    (P / "out").mkdir(exist_ok=True)
    rosto = montador.rastrear(fonte, P / "out" / "rosto.json")
    amostras = montador._amostras_do_rosto(rosto)
    faixas = []
    for f in fs:
        item = {"de": round(f["de"], 3), "ate": round(f["ate"], 3), "tipo": f["tipo"],
                "zoom": float(f.get("zoom") or 1.0)}
        if f["tipo"] == "aroll":
            item["recorte"] = recorte(f, W, H, amostras)
        else:
            item["id"] = f.get("id", "")
        faixas.append(item)
    buracos = [i for i in range(1, len(faixas)) if abs(faixas[i]["de"] - faixas[i - 1]["ate"]) > 0.002]
    if buracos:
        raise SystemExit(f"!! faixas com buraco na linha do tempo em {buracos[:5]} — dessincronia")

    # 2. a legenda: a página do render, byte por byte
    grupos = compor.grupos_legenda(plano, captions)
    pagina = legenda_hf.html_legenda(grupos, plano.get("hook"), W, H, dur,
                                     guia={"estilos": plano.get("estilos"),
                                           "configLegenda": plano.get("configLegenda"),
                                           "bocaPct": legenda_hf.boca_pct(P / "out" / "rosto.json")})
    (out / "legenda.html").write_text(pagina, encoding="utf-8")

    # 3. o take leve
    refez = proxy(fonte, voz, offset, dur, out / "take.mp4")

    zooms = [f for f in faixas if f["zoom"] > 1.001]
    dados = {
        "projeto": nome,
        "quando": datetime.now().strftime("%Y-%m-%dT%H:%M"),
        "nota": a.nota,
        "largura": W, "altura": H, "duracaoS": round(dur, 3),
        "hook": plano.get("hook"), "estilos": plano.get("estilos"),
        "faixas": faixas,
        # onde a IMAGEM emenda (split edit ja descontado): a barra de tempo marca
        "cortes": [c / 1000 for c in (plano.get("cortesMs") or [])],
        "legendas": [{"de": g[0] / 1000, "ate": g[1] / 1000, "texto": g[2]} for g in grupos],
        "resumo": {"faixas": len(faixas), "zooms": len(zooms), "grupos": len(grupos),
                   "cortesPorMin": round(len(faixas) / max(dur, 1) * 60, 1)},
    }
    (out / "edicao.json").write_text(json.dumps(dados, ensure_ascii=False, indent=1) + "\n",
                                     encoding="utf-8")
    mb = (out / "take.mp4").stat().st_size / 1e6
    print(f"prévia de {dados['projeto']}: {len(faixas)} faixas, {len(zooms)} zoom(s) de ênfase, "
          f"{len(grupos)} grupo(s) de legenda, {dur:.1f}s")
    print(f"take.mp4 {mb:.1f} MB ({'refeito' if refez else 'reaproveitado'})")
    arquivos = {"previa/edicao.json": str(out / "edicao.json"),
                "previa/legenda.html": str(out / "legenda.html")}
    if refez:
        arquivos["previa/take.mp4"] = str(out / "take.mp4")
    print("publicar files:", json.dumps(arquivos, ensure_ascii=False))


if __name__ == "__main__":
    main()
