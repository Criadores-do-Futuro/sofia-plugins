#!/usr/bin/env python3
"""Mede silêncio e nível médio no primeiro áudio de uma referência local.

Os resultados são medições técnicas, não identificam música, SFX ou J-cuts.
Os tempos são relativos ao início do contêiner, quando seus metadados permitem.
"""
import argparse
import json
import math
import re
import subprocess
import sys
from pathlib import Path


class AnaliseErro(ValueError):
    pass


def _numero(valor):
    try:
        numero = float(valor)
    except (ValueError, TypeError):
        return None
    return numero if math.isfinite(numero) else None


def _estado_arquivo(fonte):
    estado = fonte.stat()
    return {"tamanho_bytes": estado.st_size, "mtime_ns": str(estado.st_mtime_ns),
            "dispositivo": str(estado.st_dev), "inode": str(estado.st_ino)}


def analisar(fonte, ruido_db=-40.0, silencio_minimo=0.2, timeout=300):
    fonte = Path(fonte).expanduser().resolve(strict=True)
    if not fonte.is_file():
        raise AnaliseErro("A referência não é um arquivo regular")
    estado_inicial = _estado_arquivo(fonte)
    if not math.isfinite(ruido_db) or not -120 <= ruido_db <= 0:
        raise AnaliseErro("O limiar de ruído deve estar entre -120 e 0 dB")
    if not math.isfinite(silencio_minimo) or not 0.05 <= silencio_minimo <= 30:
        raise AnaliseErro("A duração mínima deve estar entre 0,05 e 30 segundos")
    if not math.isfinite(timeout) or timeout <= 0:
        raise AnaliseErro("O limite de execução deve ser positivo")
    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration,start_time:stream=index,codec_type,start_time,duration,channels,sample_rate",
             "-of", "json", str(fonte)], capture_output=True, text=True, timeout=timeout, check=True)
        metadados = json.loads(probe.stdout)
    except FileNotFoundError as exc:
        raise AnaliseErro("FFmpeg e ffprobe precisam estar instalados") from exc
    except subprocess.TimeoutExpired as exc:
        raise AnaliseErro("A leitura dos metadados excedeu o tempo limite") from exc
    except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        raise AnaliseErro("Não foi possível ler os metadados da referência") from exc
    formato = metadados.get("format") or {}
    duracao = _numero(formato.get("duration"))
    if duracao is None or duracao <= 0:
        raise AnaliseErro("A duração da referência não está disponível")
    trilhas = [s for s in metadados.get("streams", []) if s.get("codec_type") == "audio"]
    resultado = {
        "versao": 1, "fonte": str(fonte), "duracao_segundos": duracao, "estado_fonte": estado_inicial,
        "possui_audio": bool(trilhas), "processamento_sem_erro": False,
        "limiar_ruido_db": ruido_db, "silencio_minimo_segundos": silencio_minimo,
        "silencios": [], "nivel_medio_dbfs": None,
        "limites": ["Silêncio é definido pelo limiar escolhido; não identifica fala, música ou efeitos.",
                    "O nível médio vem do filtro volumedetect do FFmpeg, com precisão limitada pela análise em 16 bits."],
    }
    if not trilhas:
        if _estado_arquivo(fonte) != estado_inicial:
            raise AnaliseErro("A referência mudou durante a análise")
        resultado["limites"].append("A referência não possui trilha de áudio; nada foi medido.")
        return resultado
    trilha = trilhas[0]
    inicio_audio = _numero(trilha.get("start_time"))
    inicio_container = _numero(formato.get("start_time"))
    inicio_conhecido = inicio_audio is not None and inicio_container is not None
    deslocamento = (inicio_audio - inicio_container) if inicio_conhecido else 0.0
    if not inicio_conhecido:
        resultado["limites"].append("Início da trilha desconhecido: tempos relativos ao início decodificado do áudio.")
    if deslocamento < 0:
        resultado["limites"].append("A trilha começa antes do contêiner; intervalos anteriores ao início foram limitados a zero.")
    if deslocamento >= duracao:
        raise AnaliseErro("O início do áudio excede a duração do contêiner")
    resultado["trilha"] = {"indice": trilha.get("index"), "canais": trilha.get("channels"),
                            "taxa_amostragem": trilha.get("sample_rate"),
                            "deslocamento_segundos": deslocamento, "deslocamento_verificado": inicio_conhecido}
    filtro = (f"asetpts=PTS-STARTPTS,silencedetect=noise={ruido_db}dB:d={silencio_minimo},"
              "volumedetect")
    try:
        execucao = subprocess.run(
            ["ffmpeg", "-hide_banner", "-nostdin", "-nostats", "-v", "info", "-xerror", "-i", str(fonte),
             "-map", "0:a:0", "-vn", "-sn", "-af", filtro, "-progress", "pipe:1", "-f", "null", "-"],
            capture_output=True, text=True, timeout=timeout, check=True)
    except FileNotFoundError as exc:
        raise AnaliseErro("FFmpeg e ffprobe precisam estar instalados") from exc
    except subprocess.TimeoutExpired as exc:
        raise AnaliseErro("A análise do áudio excedeu o tempo limite") from exc
    except subprocess.CalledProcessError as exc:
        raise AnaliseErro("O FFmpeg não concluiu a decodificação do áudio") from exc
    saida = execucao.stderr
    padrao = re.compile(r"silence_(start|end):\s*(-?[0-9]+(?:\.[0-9]+)?)")
    inicio = None
    for tipo, valor in padrao.findall(saida):
        t = float(valor) + deslocamento
        if tipo == "start":
            if inicio is not None:
                raise AnaliseErro("Marcadores de silêncio inconsistentes")
            inicio = t
        else:
            if inicio is None or t < inicio:
                raise AnaliseErro("Marcadores de silêncio inconsistentes")
            if t > 0 and inicio < duracao:
                resultado["silencios"].append({"inicio_segundos": round(max(0, inicio), 6),
                                               "fim_segundos": round(min(duracao, t), 6)})
            inicio = None
    if inicio is not None:
        raise AnaliseErro("O último silêncio não possui fim; análise incompleta")
    nivel = re.search(r"mean_volume:\s*(-?inf|-?[0-9]+(?:\.[0-9]+)?)\s*dB", saida)
    if nivel is None:
        raise AnaliseErro("O nível médio não foi reportado; análise incompleta")
    duracoes = re.findall(r"^out_time_us=(\d+)\s*$", execucao.stdout, flags=re.MULTILINE)
    if not duracoes or int(duracoes[-1]) <= 0:
        raise AnaliseErro("A duração de áudio decodificado não foi reportada")
    resultado["trilha"]["duracao_decodificada_segundos"] = int(duracoes[-1]) / 1_000_000
    if _estado_arquivo(fonte) != estado_inicial:
        raise AnaliseErro("A referência mudou durante a análise")
    resultado["nivel_medio_dbfs"] = _numero(nivel.group(1))
    if resultado["nivel_medio_dbfs"] is None:
        resultado["limites"].append("Nível médio negativo infinito: áudio digitalmente silencioso.")
    resultado["processamento_sem_erro"] = True
    return resultado


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("fonte", type=Path)
    p.add_argument("--saida", type=Path, required=True)
    p.add_argument("--ruido-db", type=float, default=-40.0)
    p.add_argument("--silencio-minimo", type=float, default=0.2)
    p.add_argument("--timeout", type=float, default=300)
    args = p.parse_args()
    if args.saida.exists():
        p.error("O arquivo de saída já existe")
    try:
        resultado = analisar(args.fonte, args.ruido_db, args.silencio_minimo, args.timeout)
        with args.saida.open("x", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2, allow_nan=False)
            f.write("\n")
    except (OSError, AnaliseErro, ValueError) as exc:
        print("Não foi possível analisar o áudio: " + str(exc), file=sys.stderr)
        return 1
    print("Áudio medido." if resultado["processamento_sem_erro"] else "Referência sem áudio; nenhum áudio medido.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
