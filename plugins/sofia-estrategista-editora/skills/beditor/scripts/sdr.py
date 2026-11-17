#!/usr/bin/env python3
"""
Converte o take HDR do iPhone (HLG ou Dolby Vision/PQ) em SDR BT.709 antes de
qualquer corte, e deixa o original intacto como matriz.

Uso: sdr.py brutos/take.mov [--saida brutos/take.sdr.mov]

Por que existe: o iPhone grava HLG em 10 bits. O ffmpeg desta máquina não tem
`zscale` nem `libplacebo`, e o pipeline copiava o sinal HLG para H.264 de 8
bits com a marcação BT.2020 — pele pálida e amarelada, contraste lavado, e
cada player decidindo por conta própria como mostrar (projetos 05 e 07). O
tone mapping certo é o da Apple: o `avconvert` com preset H.264 sai em BT.709,
na resolução do take e com a rotação já aplicada. O áudio volta do original,
sem recompressão, porque o `avconvert` o regrava em AAC.

O `avconvert` só faz tone mapping de HDR de verdade (HEVC 10 bits com os
metadados do iPhone). Um H.264 de 8 bits que só carrega a marca HLG — como os
proxies antigos — sai com a marca intacta, e o `conferir` recusa: converta
sempre a partir do bruto, nunca de um intermediário.

Depois de rodar, **o take de todo o resto do pipeline é o `.sdr.mov`**
(`contato.py`, `montar.py`). O relógio é o mesmo, então o transcript do bruto
vale para ele: `take.sdr.whisper.json` vira um link para `take.whisper.json`,
e a convenção `<take>.whisper.json` dos comandos continua funcionando. O
`montar.py` recusa take HDR.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

HDR = {"arib-std-b67": "HLG", "smpte2084": "PQ"}
PRESET = "PresetHighestQuality"     # H.264, mesma resolução, SDR BT.709


def _sonda(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "stream=codec_type,color_transfer:format=duration",
                        "-of", "json", str(video)], capture_output=True, text=True, check=True, encoding="utf-8", errors="replace")
    return json.loads(r.stdout)


def transferencia(video):
    d = _sonda(video)
    for s in d.get("streams", []):
        if s.get("codec_type") == "video":
            return s.get("color_transfer") or ""
    return ""


def hdr(video):
    """'HLG', 'PQ' ou None"""
    return HDR.get(transferencia(video))


def duracao(video):
    return float(_sonda(video)["format"]["duration"])


def saida_padrao(take):
    take = Path(take)
    return take.with_name(take.stem + ".sdr.mov")


def ligar_transcricao(take, saida):
    """o transcript do bruto serve ao SDR: mesmo relógio, um arquivo só"""
    take, saida = Path(take), Path(saida)
    orig = take.with_name(take.stem + ".whisper.json")
    novo = saida.with_name(saida.stem + ".whisper.json")
    if orig.exists() and not novo.exists() and not novo.is_symlink():
        novo.symlink_to(orig.name if orig.parent == novo.parent else orig.resolve())
    return novo if novo.exists() else None


def exigir_sdr(take, aceitar=False):
    """a trava do montar.py: take HDR não entra no corte"""
    tipo = hdr(take)
    if tipo and not aceitar:
        raise SystemExit(
            f"take {tipo}: converta antes — python3 {Path(__file__).resolve()} '{take}'\n"
            f"e use '{saida_padrao(take)}' como --take (--aceitar-hdr passa por cima, "
            "e o master sai com a pele lavada)")
    return tipo


def converter(take, saida=None):
    take = Path(take)
    saida = Path(saida) if saida else saida_padrao(take)
    tmp = saida.with_name(saida.stem + ".avconvert.mov")
    subprocess.run(["xcrun", "avconvert", "--source", str(take), "--preset", PRESET,
                    "--output", str(tmp), "--replace"], check=True)
    # vídeo convertido + áudio do original, sem recompressão
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(tmp), "-i", str(take),
                    "-map", "0:v:0", "-map", "1:a:0?", "-c", "copy",
                    "-movflags", "+faststart", str(saida)], check=True)
    tmp.unlink(missing_ok=True)
    conferir(take, saida)
    return saida


def conferir(take, saida, fps=30):
    """a conversão só vale se o relógio é o mesmo e o sinal é SDR"""
    trc = transferencia(saida)
    if trc in HDR:
        raise SystemExit(f"sdr: saída ainda em {trc}")
    d0, d1 = duracao(take), duracao(saida)
    if abs(d0 - d1) > 1.5 / fps:
        raise SystemExit(f"sdr: duração mudou ({d0:.3f} s → {d1:.3f} s); "
                         "o whisper e o guia perderiam a sincronia")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("take")
    ap.add_argument("--saida")
    a = ap.parse_args()
    take = Path(a.take)
    tipo = hdr(take)
    if not tipo:
        print(f"sdr: {take.name} já é SDR — use o próprio take", file=sys.stderr)
        print(take)
        return
    saida = Path(a.saida) if a.saida else saida_padrao(take)
    if saida.exists() and saida.stat().st_mtime >= take.stat().st_mtime \
            and not hdr(saida):
        conferir(take, saida)
        print(f"sdr: {saida.name} já existe e confere", file=sys.stderr)
    else:
        print(f"sdr: {take.name} é {tipo}; convertendo para SDR BT.709 (avconvert)…",
              file=sys.stderr, flush=True)
        converter(take, saida)
    ligar_transcricao(take, saida)
    print(saida)


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
