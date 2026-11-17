#!/usr/bin/env python3
"""Rosto e recorte de pessoa, com o motor mais eficiente de cada máquina.

    python3 visao.py rosto   <video> <saida.json>
    python3 visao.py recorte <quadro.png|jpg> <saida.png>
    python3 visao.py motor                        # qual motor esta máquina usa

Dois contratos, e todo o plugin fala só com eles:

- **rosto** — uma amostra a cada 0,25 s: `time`, `centerX`, `centerY`, `top`,
  `bottom`, `width`, `height` (0–1, origem no canto superior esquerdo, na
  imagem JÁ girada como se assiste) e `confidence`. O maior rosto do quadro.
  Nenhum rosto no vídeo inteiro é erro.
- **recorte** — PNG RGBA do mesmo tamanho da entrada, o sujeito opaco e o
  fundo transparente.

Os motores, do mais eficiente para o mais portátil:

- **vision** (macOS) — os binários Swift em `~/.beditor/bin`, que rodam o
  Vision da Apple no Neural Engine. É o melhor recorte que existe localmente
  (máscara de instância, cabelo inteiro) e o mais rápido num Mac. Compilados
  por `instalar_bin.sh`.
- **portatil** (Windows, Linux, Mac sem Xcode), em CPU:
  - rosto pelo **YuNet do OpenCV** — o OpenCV já é dependência obrigatória do
    plugin, então não entra pacote novo; 4,8 ms por quadro em 360×640 no take
    007 do projeto 16, score 0,9. Precisa de OpenCV ≥ 4.8.
  - recorte pelo **Selfie Segmenter do MediaPipe** (API Tasks) — 83 ms por
    quadro 1080×1920 com o segmentador reaproveitado. A API antiga
    `mp.solutions` foi removida no mediapipe 1.x; não usar exemplo que a cite.
    A borda é mais macia que a do Vision: serve para o cartão atrás da pessoa,
    não para close de cabelo.
  O detector de rosto do MediaPipe NÃO serve: no macOS ele abre um ajudante de
  GPU Metal mesmo com delegado de CPU e aborta o processo (graph_service.h,
  «Service is unavailable»). Os dois modelos (menos de 1 MB somados) baixam uma
  vez para `~/.beditor/modelos/`.

Nada sai da máquina em nenhum dos dois: o rosto de quem fala não vai para
serviço de terceiro.
"""
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

BIN = Path.home() / ".beditor" / "bin"
MODELOS = Path(os.environ.get("BEDITOR_MODELOS", Path.home() / ".beditor" / "modelos"))
INTERVALO = 0.25          # o mesmo passo do rastrear-rosto.swift
LARGURA_ROSTO = 360       # rosto de quem fala ocupa 10–30% do quadro: 360 px sobra

URL_MODELO = {
    "rosto": "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/"
             "face_detection_yunet_2023mar.onnx",
    "recorte": "https://storage.googleapis.com/mediapipe-models/image_segmenter/"
               "selfie_segmenter/float16/latest/selfie_segmenter.tflite",
}


# ---------------------------------------------------------------------------
# escolha do motor
# ---------------------------------------------------------------------------
def _binario(nome):
    b = BIN / (nome + (".exe" if os.name == "nt" else ""))
    return b if b.is_file() and os.access(b, os.X_OK) else None


def motor(forcar=None):
    """'vision' ou 'portatil'. `BEDITOR_VISAO` força um dos dois (teste, ou
    para comparar); sem isso, Vision onde existir, o portátil no resto."""
    escolha = forcar or os.environ.get("BEDITOR_VISAO")
    if escolha:
        return escolha
    if platform.system() == "Darwin" and _binario("rastrear-rosto") and _binario("recorte"):
        return "vision"
    return "portatil"


def _modelo(tipo):
    """O .tflite em disco, baixado uma vez. Escrita atômica: download
    interrompido não deixa arquivo pela metade com cara de modelo."""
    MODELOS.mkdir(parents=True, exist_ok=True)
    destino = MODELOS / Path(URL_MODELO[tipo]).name
    if not destino.is_file():
        tmp = destino.with_suffix(".baixando")
        with urllib.request.urlopen(URL_MODELO[tipo], timeout=60) as r, open(tmp, "wb") as f:
            shutil.copyfileobj(r, f)
        tmp.replace(destino)
    return str(destino)


def _cpu(BaseOptions, tipo):
    """Delegado de CPU, sempre. No Mac o MediaPipe tenta a GPU pela Metal e
    aborta o processo fora de um app gráfico (DrishtiMetalHelper); no Windows a
    CPU já é o padrão. BlazeFace e o selfie segmenter são pequenos o bastante
    para a CPU não ser o gargalo."""
    return BaseOptions(model_asset_path=_modelo(tipo), delegate=BaseOptions.Delegate.CPU)


def _falta(pacote):
    return SystemExit(f"o motor de visão desta máquina precisa de `{pacote}`, e ele não está instalado.\n"
                      f"  pip3 install {pacote}\n"
                      "(em Mac, `instalar_bin.sh` compila o Vision da Apple, que é melhor e dispensa isto)")


# ---------------------------------------------------------------------------
# rosto
# ---------------------------------------------------------------------------
def _dimensoes(video):
    """(largura, altura, duração) como se assiste — girada pelos metadados."""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=width,height:stream_side_data=rotation:"
                        "stream_tags=rotate:format=duration", "-of", "json", str(video)],
                       capture_output=True, text=True, encoding="utf-8", check=True)
    d = json.loads(r.stdout)
    s = d["streams"][0]
    w, h = int(s["width"]), int(s["height"])
    rot = int(float((s.get("tags") or {}).get("rotate", 0) or 0))
    for sd in s.get("side_data_list") or []:
        if "rotation" in sd:
            rot = int(float(sd["rotation"]))
    if abs(rot) % 180 == 90:
        w, h = h, w
    return w, h, float(d["format"]["duration"])


def _rosto_portatil(video, saida):
    try:
        import numpy as np
        import cv2
    except ImportError:
        raise _falta("opencv-python")
    if not hasattr(cv2, "FaceDetectorYN"):
        raise SystemExit(f"o OpenCV instalado ({cv2.__version__}) não tem o YuNet; "
                         "pip3 install -U opencv-python")
    w, h, _ = _dimensoes(video)
    lw = LARGURA_ROSTO
    lh = int(round(lw * h / w / 2)) * 2
    # fps=4 entrega um quadro por 0,25 s; o ffmpeg já aplica a rotação
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-nostdin", "-i", str(video), "-an",
                             "-vf", f"fps={1 / INTERVALO:g},scale={lw}:{lh}",
                             "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                            stdout=subprocess.PIPE)
    detector = cv2.FaceDetectorYN.create(_modelo("rosto"), "", (lw, lh), 0.6)
    amostras, i, n = [], 0, lw * lh * 3
    try:
        while True:
            buf = proc.stdout.read(n)
            if len(buf) < n:
                break
            quadro = np.frombuffer(buf, dtype=np.uint8).reshape(lh, lw, 3)
            _, rostos = detector.detect(quadro)
            t = round(i * INTERVALO, 3)
            i += 1
            if rostos is None or not len(rostos):
                continue
            x, y, bw, bh = max(rostos, key=lambda r: r[2] * r[3])[:4]
            score = float(max(rostos, key=lambda r: r[2] * r[3])[14])
            x, y = max(0.0, float(x)), max(0.0, float(y))
            topo, base = y / lh, min(1.0, (y + float(bh)) / lh)
            amostras.append({"time": t, "centerX": (x + float(bw) / 2) / lw,
                             "centerY": (topo + base) / 2, "top": topo, "bottom": base,
                             "width": float(bw) / lw, "height": float(bh) / lh,
                             "confidence": round(score, 4)})
    finally:
        proc.stdout.close()
        proc.wait()
    if not amostras:
        raise SystemExit(f"nenhum rosto detectado em {video}")
    Path(saida).write_text(json.dumps(amostras, indent=1), encoding="utf-8")
    return len(amostras)


def rastrear_rosto(video, saida, forcar=None):
    """Escreve o JSON de rosto em `saida` pelo motor desta máquina."""
    Path(saida).parent.mkdir(parents=True, exist_ok=True)
    if motor(forcar) == "vision":
        b = _binario("rastrear-rosto")
        if not b:
            raise SystemExit(f"falta {BIN / 'rastrear-rosto'} — rode scripts/instalar_bin.sh")
        subprocess.run([str(b), str(video), str(saida)], check=True, capture_output=True)
        return None
    return _rosto_portatil(video, saida)


# ---------------------------------------------------------------------------
# recorte
# ---------------------------------------------------------------------------
def _recorte_portatil(entrada, saida, _segmentador={}):
    try:
        import numpy as np
        import mediapipe as mp
        from PIL import Image
        from mediapipe.tasks.python import BaseOptions, vision
    except ImportError:
        raise _falta("mediapipe")
    # um segmentador por processo: o render chama isto quadro a quadro, e criar
    # o grafo a cada chamada custava mais que segmentar
    seg = _segmentador.get("s")
    if seg is None:
        opcoes = vision.ImageSegmenterOptions(
            base_options=_cpu(BaseOptions, "recorte"),
            output_confidence_masks=True, output_category_mask=False)
        seg = _segmentador["s"] = vision.ImageSegmenter.create_from_options(opcoes)
    rgb = np.asarray(Image.open(entrada).convert("RGB"))
    r = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb)))
    # o selfie segmenter devolve uma máscara só: confiança de ser pessoa
    conf = r.confidence_masks[-1].numpy_view()
    alfa = (np.clip(conf, 0, 1) * 255).astype(np.uint8)
    if alfa.ndim == 3:
        alfa = alfa[..., 0]
    if alfa.max() < 64:
        raise SystemExit(f"nenhum sujeito encontrado em {entrada}")
    rgba = np.dstack([rgb, alfa])
    Image.fromarray(rgba, "RGBA").save(saida)


def recortar(entrada, saida, forcar=None):
    """Escreve o PNG RGBA do sujeito em `saida` pelo motor desta máquina."""
    if motor(forcar) == "vision":
        b = _binario("recorte")
        if not b:
            raise SystemExit(f"falta {BIN / 'recorte'} — rode scripts/instalar_bin.sh")
        subprocess.run([str(b), str(entrada), str(saida)], check=True, capture_output=True)
        return
    _recorte_portatil(entrada, saida)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("rosto")
    r.add_argument("video")
    r.add_argument("saida")
    c = sub.add_parser("recorte")
    c.add_argument("entrada")
    c.add_argument("saida")
    sub.add_parser("motor")
    ap.add_argument("--motor", choices=("vision", "portatil"), default=None)
    a = ap.parse_args()
    if a.cmd == "motor":
        print(motor(a.motor))
    elif a.cmd == "rosto":
        n = rastrear_rosto(a.video, a.saida, a.motor)
        print(f"rosto: {a.saida}" + (f" · {n} amostras" if n else ""))
    else:
        recortar(a.entrada, a.saida, a.motor)
        print(f"recorte: {a.saida}")


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    sys.exit(main())
