#!/usr/bin/env python3
"""entregar.py — leva um render para o SSD, com nome e lugar previsiveis.

O disco interno guarda o material de trabalho (proxy, pedacos, passadas); o SSD
guarda o que se assiste e o que se posta. Sao duas coisas diferentes e viviam
misturadas na mesma pasta `edicao/`.

    <RAIZ>/
      _APROVADOS/                      so o que o editor aprovou, qualidade maxima
        05 - Bastidor ... — 2026-09-10 — 2160x3840.mp4
      05 - Bastidor .../
        revisao/                       o que se manda olhar, datado
          2026-09-10_corte.mp4
          2026-09-10_preview.mp4
        master/                        qualidade maxima, ainda nao aprovado

A raiz sai da pasta `entregas` do config da maquina
(`~/.config/beditor/config.json`, escrito por `/sofia-estrategista-editora:setup`) ou da variavel
`BEDITOR_ENTREGAS`. Nao ha caminho padrao: sem uma das duas, o script para e
manda configurar. **Se o volume nao estiver montado, este script para e diz.**
Escrever num caminho de volume ausente cria uma pasta no disco interno com cara
de SSD — o arquivo some da vista e o editor so descobre quando precisa dele.

Uso:
  entregar.py --arquivo edicao/motion/out/preview.mp4 --projeto "05 - ..." --etapa preview
  entregar.py --arquivo .../master.mp4 --projeto "05 - ..." --etapa master --aprovado
"""
import argparse, os, shutil, subprocess, sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oficina  # noqa: E402

# NÃO existe padrão: o disco de quem escreveu o script não é o disco de quem
# instalou, e apontar para um caminho de outra máquina só produz erro confuso
# (ou, pior, uma pasta nova com cara de SSD). Sem `entregas` no config e sem
# BEDITOR_ENTREGAS, o script manda rodar `/sofia-estrategista-editora:setup` e para.
ETAPAS = ("corte", "motion", "preview", "master")


def _medidas(arquivo):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=width,height", "-of", "csv=p=0",
                        str(arquivo)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    w, h = (r.stdout.strip().rstrip(",").split(",") + ["", ""])[:2]
    return f"{w}x{h}" if w and h else "sem medida"


def raiz():
    # Le o caminho cru do config, nao `oficina.pasta("entregas", obrigatoria=False)`:
    # essa devolve None quando a pasta nao existe (disco fora), e o script cairia
    # em silencio no padrao do autor. Aqui a checagem de volume abaixo e quem
    # explica o porque — com o caminho configurado.
    cfg = oficina.config()
    configurada = cfg["pastas"].get("entregas") or os.environ.get("BEDITOR_ENTREGAS")
    if not configurada:
        sys.exit("a pasta `entregas` não está configurada — nada foi copiado.\n"
                 f"Rode `/sofia-estrategista-editora:setup`, ou grave direto:\n"
                 f"  python3 {Path(__file__).with_name('setup.py')} --pastas entregas=<caminho> --criar\n"
                 "(ou aponte BEDITOR_ENTREGAS para a pasta desta máquina)")
    r = Path(os.path.expanduser(configurada))
    # o ponto de montagem e o segundo nivel de /Volumes/<disco>
    volume = Path(*r.parts[:3]) if r.parts[:2] == ("/", "Volumes") else None
    if volume is not None and not volume.is_dir():
        sys.exit(f"o volume `{volume}` nao esta montado — nada foi copiado.\n"
                 f"Conecte o disco, ou ajuste a pasta `entregas` em {cfg['_arquivo']} "
                 f"(`/sofia-estrategista-editora:setup`), ou aponte BEDITOR_ENTREGAS para outro lugar.")
    return r


def entregar(arquivo, projeto, etapa, aprovado=False, rotulo=""):
    arquivo = Path(arquivo)
    if not arquivo.is_file():
        sys.exit(f"nao achei {arquivo}")
    base = raiz()
    hoje = date.today().isoformat()
    medida = _medidas(arquivo)
    if aprovado:
        destino = base / "_APROVADOS"
        nome = f"{projeto} — {hoje} — {medida}{arquivo.suffix}"
    else:
        pasta = "master" if etapa == "master" else "revisao"
        destino = base / projeto / pasta
        nome = f"{hoje}_{etapa}{('_' + rotulo) if rotulo else ''}{arquivo.suffix}"
    destino.mkdir(parents=True, exist_ok=True)
    alvo = destino / nome
    # dois renders no mesmo dia nao se sobrescrevem em silencio
    n = 2
    while alvo.exists() and alvo.stat().st_size != arquivo.stat().st_size:
        alvo = destino / f"{alvo.stem}-{n}{arquivo.suffix}"
        n += 1
    shutil.copy2(arquivo, alvo)
    print(f"{alvo}  ({alvo.stat().st_size / 1e6:.1f} MB · {medida})")
    return alvo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arquivo", required=True)
    ap.add_argument("--projeto", required=True, help="nome da pasta do projeto")
    ap.add_argument("--etapa", required=True, choices=ETAPAS)
    ap.add_argument("--rotulo", default="", help="sufixo curto (ex: sem-motion)")
    ap.add_argument("--aprovado", action="store_true",
                    help="vai para _APROVADOS: so o que o editor aprovou")
    a = ap.parse_args()
    entregar(a.arquivo, a.projeto, a.etapa, a.aprovado, a.rotulo)


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
