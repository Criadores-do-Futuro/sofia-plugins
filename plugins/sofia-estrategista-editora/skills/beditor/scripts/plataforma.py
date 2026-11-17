#!/usr/bin/env python3
"""As escolhas que dependem da máquina, num lugar só.

    python3 plataforma.py        # o que esta máquina vai usar, e por quê

O plugin roda em Mac Apple Silicon, Mac Intel, Windows e Linux, e em cada um a
opção mais eficiente é outra. Nenhum script decide isso sozinho: todos
perguntam aqui. As escolhas, e a medida ou o motivo de cada uma:

| O quê | Mac Apple Silicon | Windows / Linux | Mac Intel |
| --- | --- | --- | --- |
| transcrição | mlx-whisper, na GPU unificada | faster-whisper em CUDA float16 com NVIDIA; senão CPU int8 | faster-whisper CPU int8 |
| rosto e recorte | Vision (Neural Engine), `visao.py` | YuNet (OpenCV) + Selfie Segmenter (MediaPipe), CPU | igual ao Windows, se não houver Xcode |
| prévia de revisão | h264_videotoolbox | h264_nvenc (NVIDIA), h264_qsv (Intel), h264_amf (AMD); senão libx264 veryfast | h264_videotoolbox |
| master | libx264 CRF 15 em todas | ← | ← |
| aviso de pronto | notificação do macOS | notificação do Windows (PowerShell); notify-send no Linux | macOS |
| instalar | brew | winget no Windows; apt no Linux | brew |

**O master é libx264 em toda máquina, de propósito.** O render concatena
trechos com `-c copy`, e isso só funciona se todos saírem do mesmo codificador
com os mesmos parâmetros — codificador de GPU muda de máquina para máquina e de
driver para driver. E CRF 15 do x264 é a qualidade que se publica; os de GPU
gastam mais bits para chegar perto. A GPU entra onde o arquivo é descartável: a
prévia que vai para o painel.

**Codificador de GPU só entra depois de provado.** O ffmpeg lista `h264_nvenc`
mesmo numa máquina sem placa NVIDIA; ele só falha na hora de abrir. Por isso a
escolha codifica um quadro de teste antes de confiar, uma vez por processo.

Ao ser importado, este módulo também põe o console em UTF-8: no Windows o
padrão é cp1252, e o primeiro `·` ou acento impresso derrubava o script.
"""
import functools
import json
import os
import platform
import shutil
import subprocess
import sys


def _console_utf8():
    for fluxo in (sys.stdout, sys.stderr):
        try:
            if fluxo and (fluxo.encoding or "").lower().replace("-", "") != "utf8":
                fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):   # fluxo substituído (teste, pipe especial)
            pass


_console_utf8()


def sistema():
    """'mac-arm', 'mac-intel', 'windows' ou 'linux'."""
    s = platform.system()
    if s == "Darwin":
        return "mac-arm" if platform.machine() in ("arm64", "aarch64") else "mac-intel"
    if s == "Windows":
        return "windows"
    return "linux"


def mac():
    return sistema().startswith("mac")


@functools.lru_cache(maxsize=None)
def nvidia():
    """Há uma GPU NVIDIA utilizável? `nvidia-smi -L` responde só com driver instalado."""
    exe = shutil.which("nvidia-smi")
    if not exe:
        return False
    try:
        r = subprocess.run([exe, "-L"], capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=10)
        return r.returncode == 0 and "GPU" in r.stdout
    except (OSError, subprocess.SubprocessError):
        return False


# ---------------------------------------------------------------------------
# transcrição
# ---------------------------------------------------------------------------
def transcricao():
    """{'motor', 'device', 'compute'} — o que `transcrever.py` deve tentar primeiro."""
    if sistema() == "mac-arm":
        return {"motor": "mlx-whisper", "device": "gpu", "compute": "float16"}
    if nvidia():
        return {"motor": "faster-whisper", "device": "cuda", "compute": "float16"}
    return {"motor": "faster-whisper", "device": "cpu", "compute": "int8"}


# ---------------------------------------------------------------------------
# codificador da prévia
# ---------------------------------------------------------------------------
PREVIA = {
    "h264_videotoolbox": ["-c:v", "h264_videotoolbox", "-b:v", "1500k"],
    "h264_nvenc": ["-c:v", "h264_nvenc", "-preset", "p4", "-rc", "vbr", "-cq", "28", "-b:v", "0"],
    "h264_qsv": ["-c:v", "h264_qsv", "-global_quality", "28"],
    "h264_amf": ["-c:v", "h264_amf", "-rc", "cqp", "-qp_i", "28", "-qp_p", "28"],
    "libx264": ["-c:v", "libx264", "-preset", "veryfast", "-crf", "28"],
}


def _ordem_previa():
    if mac():
        return ["h264_videotoolbox", "libx264"]
    ordem = ["h264_nvenc"] if nvidia() else []
    return ordem + ["h264_qsv", "h264_amf", "libx264"]


@functools.lru_cache(maxsize=None)
def _funciona(codificador):
    """Codifica meio segundo de preto com o codificador. Listado ≠ utilizável."""
    try:
        r = subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-f", "lavfi", "-i",
                            "color=c=black:s=320x568:d=0.5", *PREVIA[codificador][:2],
                            "-f", "null", "-"], capture_output=True, timeout=30)
        return r.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


@functools.lru_cache(maxsize=None)
def codificador_previa():
    """(nome, argumentos de vídeo) do codificador mais rápido QUE FUNCIONA aqui."""
    for nome in _ordem_previa():
        if nome == "libx264" or _funciona(nome):
            return nome, list(PREVIA[nome])
    return "libx264", list(PREVIA["libx264"])


# ---------------------------------------------------------------------------
# aviso na tela
# ---------------------------------------------------------------------------
def _ps(s):
    return "'" + str(s).replace("'", "''") + "'"


def comando_notificacao(titulo, subtitulo, texto):
    """A linha de comando que mostra a notificação neste sistema, ou None."""
    s = sistema()
    if s.startswith("mac"):
        return ["osascript", "-e",
                f"display notification {json.dumps(texto)} with title {json.dumps(titulo)} "
                f"subtitle {json.dumps(subtitulo or '')} sound name \"Submarine\""]
    if s == "windows":
        # toast nativo pelas APIs do Windows, sem módulo extra do PowerShell
        corpo = f"{subtitulo} · {texto}" if subtitulo else texto
        script = (
            "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType=WindowsRuntime] > $null;"
            "$x = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent("
            "[Windows.UI.Notifications.ToastTemplateType]::ToastText02);"
            f"$x.GetElementsByTagName('text')[0].AppendChild($x.CreateTextNode({_ps(titulo)})) > $null;"
            f"$x.GetElementsByTagName('text')[1].AppendChild($x.CreateTextNode({_ps(corpo)})) > $null;"
            "$t = [Windows.UI.Notifications.ToastNotification]::new($x);"
            "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('bEditor').Show($t)")
        exe = shutil.which("powershell") or shutil.which("pwsh")
        return [exe, "-NoProfile", "-NonInteractive", "-Command", script] if exe else None
    exe = shutil.which("notify-send")
    return [exe, titulo, f"{subtitulo} · {texto}" if subtitulo else texto] if exe else None


def notificar(titulo, subtitulo, texto):
    cmd = comando_notificacao(titulo, subtitulo, texto)
    if not cmd:
        return False
    try:
        return subprocess.run(cmd, check=False, capture_output=True, timeout=15).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


# ---------------------------------------------------------------------------
# instalação
# ---------------------------------------------------------------------------
PACOTES = {
    # item: (brew, winget, apt)
    "ffmpeg": ("ffmpeg", "Gyan.FFmpeg", "ffmpeg"),
    "yt-dlp": ("yt-dlp", "yt-dlp.yt-dlp", "yt-dlp"),
    "node": ("node", "OpenJS.NodeJS.LTS", "nodejs npm"),
    "python": ("python@3.12", "Python.Python.3.12", "python3 python3-pip"),
}


def instalar_sistema(itens):
    """O comando que instala `itens` (chaves de PACOTES) pelo gerenciador daqui."""
    s = sistema()
    if s.startswith("mac"):
        return "brew install " + " ".join(PACOTES[i][0] for i in itens)
    if s == "windows":
        return " && ".join(f"winget install -e --id {PACOTES[i][1]}" for i in itens)
    return "sudo apt install -y " + " ".join(PACOTES[i][2] for i in itens)


def pip():
    """`pip3` onde existe; no Windows o Python instalado responde por `py -m pip`."""
    if sistema() == "windows" and not shutil.which("pip3"):
        return "py -m pip"
    return "pip3"


def pacotes_python_da_maquina():
    """Os pacotes que a transcrição e a visão pedem NESTA máquina."""
    t = transcricao()
    pac = ["mlx-whisper"] if t["motor"] == "mlx-whisper" else ["faster-whisper"]
    if not mac():
        pac.append("mediapipe")
    return pac


def resumo():
    t = transcricao()
    nome, _ = codificador_previa()
    try:
        import visao
        motor_visao = visao.motor()
    except Exception:            # noqa: BLE001 — resumo não pode quebrar por dependência
        motor_visao = "?"
    return {"sistema": sistema(), "nvidia": nvidia(),
            "transcricao": f"{t['motor']} ({t['device']}, {t['compute']})",
            "visao": motor_visao, "previa": nome, "master": "libx264 CRF 15",
            "instalar": "brew" if mac() else ("winget" if sistema() == "windows" else "apt")}


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    for k, v in resumo().items():
        print(f"{k:<12} {v}")
