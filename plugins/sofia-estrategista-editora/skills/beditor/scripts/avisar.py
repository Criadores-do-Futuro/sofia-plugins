#!/usr/bin/env python3
"""O aviso de que alguma coisa terminou e o dono precisa voltar à mesa.

    python3 avisar.py "o 16 está pronto para revisar" --tipo revisar --projeto "16 - iPhone Duo"
    python3 avisar.py --ler            # o que ainda não foi lido (para a sessão avisar no celular)

Por que existe: um render longo termina enquanto o dono está longe do
computador. Sem aviso, ou ele fica olhando o terminal (tempo dele), ou descobre
meia hora depois (tempo de todo mundo). São dois canais, e nenhum substitui o
outro:

- **a máquina** — notificação do sistema (macOS, Windows ou Linux, por
  `plataforma.py`), disparada pelo próprio script, funciona
  mesmo quando não há nenhuma sessão de conversa aberta;
- **o celular** — quem manda é a sessão, com a ferramenta de push do harness,
  lendo daqui o que ficou pendente (`--ler`).

O aviso NUNCA derruba quem chamou: se o `osascript` não existir, se o disco
estiver cheio, se o log estiver corrompido, a falha é engolida de propósito —
render que morre por causa de um aviso seria a troca mais burra possível.

`BEDITOR_SEM_AVISO=1` desliga tudo (útil em teste e em lote).
"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

LOG = Path(os.environ.get("BEDITOR_AVISOS", Path.home() / ".beditor" / "avisos.jsonl"))
TIPOS = ("revisar", "publicar", "erro", "aviso")


def mudo():
    return os.environ.get("BEDITOR_SEM_AVISO") == "1"


def avisar(texto, tipo="aviso", projeto=None, subtitulo=None):
    """Registra o aviso e o mostra na tela da máquina. Devolve o registro."""
    if tipo not in TIPOS:
        raise ValueError(f"tipo «{tipo}» não existe; use {', '.join(TIPOS)}")
    reg = {"quando": time.strftime("%Y-%m-%dT%H:%M:%S"), "tipo": tipo, "texto": texto,
           "projeto": projeto, "lido": False}
    if mudo():
        return reg
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(reg, ensure_ascii=False) + "\n")
    except Exception:                      # noqa: BLE001 — aviso não derruba render
        pass
    try:
        import plataforma
        titulo = {"revisar": "pronto para revisar", "publicar": "pronto para publicar",
                  "erro": "parou com erro"}.get(tipo, "bEditor")
        plataforma.notificar(titulo, subtitulo or projeto or "", texto)
    except Exception:                      # noqa: BLE001
        pass
    return reg


def ler(pendentes=True, marcar=True):
    """Os avisos gravados; por padrão só os não lidos, e marca-os como lidos."""
    if not LOG.exists():
        return []
    linhas = [l for l in LOG.read_text(encoding="utf-8").splitlines() if l.strip()]
    regs = []
    for l in linhas:
        try:
            regs.append(json.loads(l))
        except json.JSONDecodeError:       # linha truncada por queda de energia: pula
            continue
    saida = [r for r in regs if not r.get("lido")] if pendentes else regs
    if marcar and saida:
        for r in regs:
            r["lido"] = True
        try:
            LOG.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in regs),
                           encoding="utf-8")
        except Exception:                  # noqa: BLE001
            pass
    return saida


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("texto", nargs="?", help="a frase do aviso, curta, sem markdown")
    ap.add_argument("--tipo", default="aviso", choices=TIPOS)
    ap.add_argument("--projeto", default=None)
    ap.add_argument("--ler", action="store_true", help="imprime os avisos pendentes e os marca como lidos")
    ap.add_argument("--tudo", action="store_true", help="com --ler: imprime todos, sem marcar")
    a = ap.parse_args()
    if a.ler:
        for r in ler(pendentes=not a.tudo, marcar=not a.tudo):
            print(f"{r['quando']} · {r['tipo']} · {r.get('projeto') or '-'} · {r['texto']}")
        return
    if not a.texto:
        ap.error("diga o texto do aviso, ou use --ler")
    avisar(a.texto, tipo=a.tipo, projeto=a.projeto)


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    sys.exit(main())
