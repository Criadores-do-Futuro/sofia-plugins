#!/usr/bin/env python3
"""
acervo.py — traz trecho de video de terceiro para dentro de uma cena.

Decisao do dono em 2026-09-12, depois de eu levantar a questao de direito:

    "quero usar clipes da internet, do reels ou do tiktok pode usar, nao fere
    direitos porque eu estou criando meu proprio conteudo em volta, e o trecho
    do video da internet e apenas um insert, nao um repost"

Decisao do dono em 2026-09-15, ampliando a de cima para a ILUSTRACAO do formato
`analise`, que ate entao so buscava em banco de imagens:

    "nao precisa buscar somente em bibliotecas de video, pode buscar no youtube
    e no tiktok tambem, pra usar somente trechos em um conteudo criado, e
    legalmente permitido"

Quem publica e ele, e a decisao e dele — este cabecalho registra a decisao e a
data, nao um parecer. O que o script FAZ para que o argumento se sustente na
pratica, e nao so na intencao (e que continua valendo igual agora que YouTube e
TikTok tambem valem para a ilustracao):

- **trecho curto, nunca o video.** `dur` tem teto de 3 s por fonte. Insert e
  citacao; clipe inteiro e repost, e a diferenca e medida em segundos.
- **procedencia registrada.** A URL, o autor e a data ficam no `plano.json` e
  saem no `CENAS.md`. Sem credito escrito o plano nao entra.
- **o download e cache.** Baixa uma vez por URL, guarda em `public/acervo/`,
  e nunca rebaixa. O material bruto nao entra no repositorio.
- **quem escolhe e o editor.** O script NAO procura video sozinho. Buscar
  "slop" e apontar o resultado num video que chama aquilo de porcaria seria
  escolher, por conta propria, de quem falar mal. O trecho se escolhe olhando
  os quadros — a folha de contato do `varrer.py`/`lupa.py` vem antes de fixar
  o `src`, nunca o titulo do video.

Uso:
  acervo.py --projeto edicao/motion [--so M05]

Le os planos com `tela.modo == "acervo"`, baixa o que falta, corta os trechos e
compoe por cima do clip que o `hf.py` ja rendeu — a moldura vazia da cena vira
a janela onde os trechos passam, um depois do outro.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

FPS = 30
DUR_MAX = 3.0          # segundos por fonte — acima disso deixa de ser insert
YTDLP = shutil.which("yt-dlp")


def _chave(url):
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]


def baixar(url, destino_dir):
    """baixa uma vez e guarda. Devolve (arquivo, ficha) ou (None, erro)."""
    destino_dir.mkdir(parents=True, exist_ok=True)
    alvo = destino_dir / f"{_chave(url)}.mp4"
    ficha_arq = alvo.with_suffix(".json")
    if alvo.exists() and ficha_arq.exists():
        return alvo, json.loads(ficha_arq.read_text(encoding="utf-8"))
    if not YTDLP:
        return None, {"erro": "yt-dlp nao instalado"}
    meta = subprocess.run(
        [YTDLP, "--skip-download", "--no-warnings", "--socket-timeout", "20",
         "--print", "%(id)s\t%(uploader)s\t%(upload_date)s\t%(title)s", url],
        capture_output=True, text=True, timeout=180, encoding="utf-8", errors="replace")
    if meta.returncode != 0:
        return None, {"erro": (meta.stderr or "").strip()[-200:]}
    campos = (meta.stdout or "").strip().split("\t")
    ficha = {"url": url, "id": campos[0] if campos else "",
             "autor": campos[1] if len(campos) > 1 else "",
             "data": campos[2] if len(campos) > 2 else "",
             "titulo": campos[3] if len(campos) > 3 else ""}
    r = subprocess.run(
        [YTDLP, "--no-warnings", "--socket-timeout", "30",
         "-f", "bv*[height<=1080]+ba/b[height<=1080]/b",
         "--merge-output-format", "mp4", "-o", str(alvo), url],
        capture_output=True, text=True, timeout=900, encoding="utf-8", errors="replace")
    if r.returncode != 0 or not alvo.exists():
        return None, {"erro": (r.stderr or "").strip()[-200:]}
    ficha_arq.write_text(json.dumps(ficha, ensure_ascii=False, indent=1), encoding="utf-8")
    return alvo, ficha


def recortar(origem, de, dur, larg, alt, destino):
    """o trecho, preenchendo a moldura: amplia e corta, nunca deforma."""
    subprocess.run(
        ["ffmpeg", "-y", "-nostdin", "-v", "error", "-ss", f"{de:.2f}",
         "-i", str(origem), "-t", f"{dur:.2f}",
         "-vf", (f"scale={larg}:{alt}:force_original_aspect_ratio=increase,"
                 f"crop={larg}:{alt},fps={FPS},setpts=PTS-STARTPTS"),
         "-an", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
         "-pix_fmt", "yuv420p", str(destino)], check=True)
    return destino


def compor(base, trechos, rect, saida):
    """poe os trechos na janela da cena, um depois do outro.

    Cada trecho entra com o proprio `setpts` deslocado para o instante dele e
    so aparece na janela de tempo dele (`enable`). A base (a pagina desenhada
    pelo hf.py) continua por baixo o tempo todo — e dela que vem o creme, o
    selo e o rotulo."""
    x, y, _, _ = rect
    cmd = ["ffmpeg", "-y", "-nostdin", "-v", "error", "-i", str(base)]
    for arq, _, _ in trechos:
        cmd += ["-i", str(arq)]
    partes, atual = [], "[0:v]"
    for i, (_, t0, t1) in enumerate(trechos, start=1):
        partes.append(f"[{i}:v]setpts=PTS+{t0:.3f}/TB[t{i}]")
        alvo = f"[v{i}]" if i < len(trechos) else "[v]"
        partes.append(f"{atual}[t{i}]overlay={x}:{y}:"
                      f"enable='between(t,{t0:.3f},{t1:.3f})'{alvo}")
        atual = alvo
    cmd += ["-filter_complex", ";".join(partes), "-map", "[v]", "-an",
            "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
            "-pix_fmt", "yuv420p", str(saida)]
    subprocess.run(cmd, check=True)
    return saida


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projeto", required=True)
    ap.add_argument("--so", default="")
    a = ap.parse_args()
    raiz = Path(a.projeto)
    plano = json.loads((raiz / "plano.json").read_text(encoding="utf-8"))
    acervo_dir = raiz / "public" / "acervo"
    hf_dir = raiz / "out" / "hf"

    import hf_ilustrativo
    rect = hf_ilustrativo.MOLDURA_ACERVO

    pendencias, feitos = [], 0
    for p in plano["planos"]:
        t = p.get("tela") if isinstance(p.get("tela"), dict) else {}
        if (t.get("modo") or "").lower() != "acervo":
            continue
        if a.so and p["id"] != a.so:
            continue
        fontes = [f for f in (t.get("fontes") or []) if (f.get("url") or f.get("arquivo"))]
        if not fontes:
            pendencias.append(f"- **{p['id']}** `acervo` sem `fontes` — o editor escolhe "
                              f"os clipes; o script não procura sozinho.")
            continue
        base = hf_dir / p["id"] / "clip.mp4"
        if not base.exists():
            pendencias.append(f"- **{p['id']}** sem clip do hf.py — rode o hf.py antes.")
            continue
        dur_cena = (p["t1"] - p["t0"]) / 1000
        fatia = dur_cena / len(fontes)
        trabalho = hf_dir / p["id"] / "acervo"
        trabalho.mkdir(parents=True, exist_ok=True)
        trechos, creditos = [], []
        for i, f in enumerate(fontes):
            if f.get("arquivo"):
                origem = raiz / "public" / f["arquivo"]
                ficha = {"url": "", "autor": f.get("credito") or "", "titulo": f["arquivo"]}
                if not origem.exists():
                    pendencias.append(f"- **{p['id']}** arquivo não achado: {f['arquivo']}")
                    continue
            else:
                origem, ficha = baixar(f["url"], acervo_dir)
                if not origem:
                    pendencias.append(f"- **{p['id']}** falhou baixar {f['url']}: "
                                      f"{ficha.get('erro','')}")
                    continue
            dur = min(float(f.get("dur") or fatia), DUR_MAX, fatia)
            corte = recortar(origem, float(f.get("de") or 0), dur,
                             rect[2], rect[3], trabalho / f"{i:02d}.mp4")
            t0 = i * fatia
            trechos.append((corte, t0, t0 + dur))
            creditos.append({"url": ficha.get("url"), "autor": ficha.get("autor"),
                             "titulo": ficha.get("titulo"),
                             "credito": f.get("credito") or ficha.get("autor") or ""})
        if not trechos:
            continue
        compor(base, trechos, rect, trabalho / "montado.mp4")
        shutil.move(str(trabalho / "montado.mp4"), str(base))
        p["acervoCreditos"] = creditos          # procedencia viaja no plano
        feitos += 1
        print(f"  {p['id']}: {len(trechos)} trecho(s) de acervo", flush=True)

    if feitos:
        texto = json.dumps(plano, ensure_ascii=False, indent=2)
        (raiz / "plano.json").write_text(texto, encoding="utf-8")
        (raiz / "public" / "plano.json").write_text(texto, encoding="utf-8")
    if pendencias:
        print("acervo: pendências", file=sys.stderr)
        for x in pendencias:
            print("  " + x, file=sys.stderr)
    print(f"acervo: {feitos} cena(s) com trecho de terceiro")


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
