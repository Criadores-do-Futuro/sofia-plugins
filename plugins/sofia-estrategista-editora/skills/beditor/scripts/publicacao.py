#!/usr/bin/env python3
"""
Etapa 4 — publicação: confere título, descrição e capa de cada rede e monta
UM agendamento para todas as redes.

Uso:
  publicacao.py entrega/publicacao.json [--capa] [--saida entrega/publicacao]

O `publicacao.json` é escrito pelo agente a partir do guia e do transcript
(`referencias/publicacao.md`). Este script não publica nada: ele

1. valida cada texto contra o limite da rede e contra a palavra-chave (a busca
   de Instagram, TikTok e YouTube lê legenda e título, e a primeira linha é a
   única que aparece antes do "mais");
2. desenha a capa 1080×1920 a partir de um quadro do master (`--capa`), com o
   texto dentro da área que sobrevive ao recorte 3:4 da grade do perfil e fora
   da interface das redes;
3. escreve `zernio.json`: **um** post com a lista de redes, o texto próprio de
   cada uma e a capa. Um agendamento, uma chamada, um upload de mídia
   reaproveitado por todas as redes. É esse o jeito econômico.

Quem publica é o MCP (Zernio ou Metricool), e só depois do sim explícito do
editor — ver `commands/publicar.md`.
"""
import argparse
import json
import subprocess
import sys
import unicodedata
from pathlib import Path

# limite de caracteres do texto e quanto aparece antes do "mais"
REDES = {
    "youtube":   {"texto": 5000, "titulo": 100, "visivel": 100, "hashtags": (1, 3)},
    "instagram": {"texto": 2200, "visivel": 125, "hashtags": (3, 5)},
    "tiktok":    {"texto": 4000, "visivel": 100, "hashtags": (3, 5)},
    "facebook":  {"texto": 63206, "visivel": 125, "hashtags": (0, 3)},
    "threads":   {"texto": 500, "visivel": 500, "hashtags": (0, 1)},
    "linkedin":  {"texto": 3000, "visivel": 140, "hashtags": (0, 3)},
    "x":         {"texto": 280, "visivel": 280, "hashtags": (0, 2)},
    "bluesky":   {"texto": 300, "visivel": 300, "hashtags": (0, 2)},
}
CAPA = (1080, 1920)
# a grade do perfil do Instagram mostra o centro 3:4 (1080x1440): y 240–1680.
# Fora disso a interface das redes cobre texto (topo 12%, base 22%, linguagem-visual.md)
AREA_TEXTO = (300, 1150)
# A Anton vem da skill irma motion-vox, empacotada no plugin.
_VOX = Path(__file__).resolve().parents[2] / "motion-vox" / "fontes"
FONTES = [Path.home() / ".beditor/fontes/BebasNeue-Regular.ttf",
          _VOX / "Anton-Regular.ttf"]
# o estilo da casa; a marca do projeto (marca.py) troca cores e fonte
TEXTO, DESTAQUE, SOMBRA = (255, 255, 255), (255, 208, 0), (0, 0, 0)


def _sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s.lower())
                   if unicodedata.category(c) != "Mn")


def texto_da_rede(rede, dados):
    d = dados["redes"][rede]
    return d.get("descricao") or d.get("legenda") or ""


def validar(dados):
    """(erros, avisos) — erro bloqueia o agendamento, aviso vai para o editor"""
    erros, avisos = [], []
    chave = _sem_acento(dados.get("palavraChave", ""))
    if not chave:
        erros.append("sem `palavraChave`: é o termo que o público digita na busca")
    if not dados.get("redes"):
        erros.append("sem `redes`")
    for rede, d in (dados.get("redes") or {}).items():
        lim = REDES.get(rede)
        if not lim:
            avisos.append(f"{rede}: rede sem limite conhecido aqui; confira no MCP")
            continue
        texto = texto_da_rede(rede, dados)
        if not texto.strip():
            erros.append(f"{rede}: texto vazio")
            continue
        if len(texto) > lim["texto"]:
            erros.append(f"{rede}: {len(texto)} caracteres, o limite é {lim['texto']}")
        if chave and chave not in _sem_acento(texto[:lim["visivel"]]):
            avisos.append(f"{rede}: a palavra-chave não aparece nos primeiros "
                          f"{lim['visivel']} caracteres, o trecho que a busca e o feed mostram")
        n = sum(1 for p in texto.split() if p.startswith("#"))
        lo, hi = lim["hashtags"]
        if n > hi:
            avisos.append(f"{rede}: {n} hashtags; acima de {hi} vira ruído")
        if rede == "youtube":
            titulo = d.get("titulo", "")
            if not titulo:
                erros.append("youtube: sem `titulo`")
            elif len(titulo) > lim["titulo"]:
                erros.append(f"youtube: título com {len(titulo)} caracteres, o limite é 100")
            elif chave and chave not in _sem_acento(titulo[:45]):
                avisos.append("youtube: a palavra-chave não está nos primeiros 45 caracteres "
                              "do título, o que aparece cortado na busca do celular")
    capa = dados.get("capa") or {}
    palavras = sum(len(l.split()) for l in capa.get("linhas", []))
    if capa and not capa.get("linhas"):
        erros.append("capa: sem `linhas`")
    elif palavras > 8:
        erros.append(f"capa: {palavras} palavras; o máximo que se lê no feed é 8")
    elif palavras > 5:
        avisos.append(f"capa: {palavras} palavras; até 5 lê melhor em miniatura")
    ag = dados.get("agendamento") or {}
    if not ag.get("quando") or not ag.get("fuso"):
        erros.append("agendamento: `quando` e `fuso` são obrigatórios")
    return erros, avisos


def payload_zernio(dados, url_video="{{URL_DO_VIDEO}}", url_capa="{{URL_DA_CAPA}}"):
    """um post, todas as redes: `platforms` com texto e dado próprio de cada uma"""
    ag = dados["agendamento"]
    contas = ag.get("contas") or {}
    redes = dados["redes"]
    principal = texto_da_rede("instagram", dados) if "instagram" in redes \
        else texto_da_rede(next(iter(redes)), dados)
    plataformas = []
    for rede, d in redes.items():
        p = {"platform": rede, "accountId": contas.get(rede, f"{{{{CONTA_{rede.upper()}}}}}")}
        texto = texto_da_rede(rede, dados)
        if texto != principal:
            p["customContent"] = texto
        extra = {}
        if rede == "youtube":
            extra["title"] = d["titulo"]
        if rede == "instagram" and dados.get("capa"):
            extra["instagramThumbnail"] = url_capa
        if extra:
            p["platformSpecificData"] = extra
        plataformas.append(p)
    corpo = {
        "content": principal,
        "mediaItems": [{"url": url_video, "type": "video"}],
        "platforms": plataformas,
        "scheduledFor": ag["quando"],
        "timezone": ag["fuso"],
    }
    tags = (redes.get("youtube") or {}).get("tags")
    if tags:
        corpo["tags"] = tags
    return corpo


def _fonte(tamanho, marca_=None):
    from PIL import ImageFont
    propria = marca_.fonte("display") if marca_ else None
    for f in ([propria] if propria else []) + FONTES:
        if f.exists():
            return ImageFont.truetype(str(f), tamanho), f.name
    raise SystemExit("publicacao: nenhuma fonte de display (Bebas Neue ou Anton) encontrada")


def desenhar_capa(video, capa, saida):
    """quadro do master + texto grande, dentro da área que a grade e a UI não comem"""
    from PIL import Image, ImageDraw
    quadro = saida.with_suffix(".quadro.png")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(capa.get("t", 1.0)), "-i", str(video),
                    "-frames:v", "1", "-vf",
                    f"scale={CAPA[0]}:{CAPA[1]}:force_original_aspect_ratio=increase,"
                    f"crop={CAPA[0]}:{CAPA[1]}", str(quadro)], check=True)
    img = Image.open(quadro).convert("RGB")
    quadro.unlink(missing_ok=True)
    # escurece o topo para o texto ler sobre qualquer fundo, sem virar tarja
    sombra = Image.new("L", CAPA, 0)
    ds = ImageDraw.Draw(sombra)
    for y in range(0, 1300):
        ds.line([(0, y), (CAPA[0], y)], fill=int(150 * max(0.0, 1 - y / 1300)))
    img.paste(Image.new("RGB", CAPA, (22, 11, 16)), (0, 0), sombra)
    linhas = [l.upper() for l in capa["linhas"]]
    destaque = (capa.get("destaque") or "").upper()
    import marca
    mc = marca.resolver(projeto=Path.cwd())
    texto_c = mc.cor("texto", TEXTO) if mc else TEXTO
    destaque_c = mc.cor("destaque", DESTAQUE) if mc else DESTAQUE
    sombra_c = mc.cor("sombra", SOMBRA) if mc else SOMBRA
    corpo = 150
    fonte, nome = _fonte(corpo, mc)
    d = ImageDraw.Draw(img)
    while corpo > 80 and max(d.textlength(l, font=fonte) for l in linhas) > CAPA[0] - 2 * 110:
        corpo -= 6
        fonte, nome = _fonte(corpo, mc)
    y = AREA_TEXTO[0]
    caixas = []
    for l in linhas:
        w = d.textlength(l, font=fonte)
        x = (CAPA[0] - w) / 2
        cor = destaque_c if destaque and destaque in l else texto_c
        d.text((x + 7, y + 7), l, font=fonte, fill=sombra_c)     # sombra dura
        d.text((x, y), l, font=fonte, fill=cor)
        caixas.append((x, y, x + w, y + corpo))
        y += int(corpo * 0.98)
    img.save(saida, "JPEG", quality=90, optimize=True)
    return {"arquivo": str(saida), "fonte": nome, "corpo": corpo,
            "base_do_texto": y, "cabe": y <= AREA_TEXTO[1],
            "bytes": saida.stat().st_size}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("publicacao")
    ap.add_argument("--capa", action="store_true", help="desenha a capa a partir do master")
    ap.add_argument("--saida")
    a = ap.parse_args()
    arq = Path(a.publicacao)
    dados = json.loads(arq.read_text(encoding="utf-8"))
    saida = Path(a.saida) if a.saida else arq.parent / "publicacao"
    saida.mkdir(parents=True, exist_ok=True)
    erros, avisos = validar(dados)
    for e in erros:
        print(" ✗", e, file=sys.stderr)
    for v in avisos:
        print(" !", v, file=sys.stderr)
    if erros:
        sys.exit(1)
    if a.capa and dados.get("capa"):
        # o quadro sai do A-roll sem legenda: do master viria a legenda queimada junto
        fonte = dados.get("fonteCapa")
        if not fonte:
            print(" ! capa: sem `fonteCapa` (A-roll limpo); usando o master, que tem legenda "
                  "queimada", file=sys.stderr)
        info = desenhar_capa(Path(fonte or dados["video"]), dados["capa"], saida / "capa.jpg")
        print(f"capa: {info['arquivo']} ({info['fonte']}, {info['corpo']} px, "
              f"{info['bytes'] // 1024} KB)", file=sys.stderr)
        if not info["cabe"]:
            sys.exit("capa: o texto passa da área segura — encurte as linhas")
        if info["bytes"] > 2 * 1024 * 1024:
            sys.exit("capa: acima de 2 MB, o YouTube recusa")
    corpo = payload_zernio(dados)
    (saida / "zernio.json").write_text(json.dumps(corpo, ensure_ascii=False, indent=2) + "\n",
                                       encoding="utf-8")
    print(f"agendamento: 1 post, {len(corpo['platforms'])} redes "
          f"({', '.join(p['platform'] for p in corpo['platforms'])}) → {saida / 'zernio.json'}",
          file=sys.stderr)


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
