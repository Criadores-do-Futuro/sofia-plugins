#!/usr/bin/env python3
"""Gera pranchas de inspeção com TODOS os quadros decodificados de um vídeo local.

Cada prancha é uma grade 5x5 (25 quadros) em resolução reduzida, na ordem de
decodificação (esquerda para a direita, de cima para baixo). Nenhum quadro é
pulado, duplicado ou descartado: o ffmpeg roda em modo ``passthrough`` e cada
quadro que entra na grade é contado no filtro ``showinfo``.

O script usa apenas ``ffmpeg`` e ``ffprobe`` via subprocess, não acessa a rede e
não usa git. A pasta de destino precisa ser NOVA: se já existir, o script
recusa e não toca em nada.

IMPORTANTE: as pranchas servem para inspeção visual, quadro a quadro. Elas NÃO
garantem análise semântica do conteúdo do vídeo.

Uso:
    python3 scripts/gerar_pranchas_quadros.py VIDEO [--saida PASTA_NOVA]
        [--largura 320] [--contar-quadros]

Códigos de saída: 0 = ok, 1 = erro de execução, 2 = erro de uso (entrada ou
destino inválido), 3 = pranchas geradas, mas com divergência a conferir.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

COLUNAS = 5
LINHAS = 5
QUADROS_POR_PRANCHA = COLUNAS * LINHAS
LARGURA_PADRAO = 320
LARGURA_MINIMA = 16
ESPACO_ENTRE_QUADROS = 2
MARGEM = 2
PREFIXO_PRANCHA = "prancha_"
MODELO_ARQUIVO_PRANCHA = PREFIXO_PRANCHA + "%04d.png"
NOME_MANIFESTO = "manifesto.json"
VERSAO_MANIFESTO = 1

AVISO_SEMANTICA = (
    "As pranchas servem apenas para inspeção visual de todos os quadros "
    "decodificados. Elas não garantem análise semântica do conteúdo do vídeo: "
    "quem olha as pranchas (pessoa ou modelo) ainda precisa interpretar cada "
    "quadro, e a resolução reduzida pode esconder detalhes."
)

# Linha emitida pelo filtro showinfo para cada quadro que o atravessa.
_REGEX_SHOWINFO = re.compile(r"Parsed_showinfo_\d+ @ [^\]]+\]\s+n:\s*\d+")

EXIT_OK = 0
EXIT_ERRO = 1
EXIT_USO = 2
EXIT_ATENCAO = 3


class ErroUso(Exception):
    """Entrada ou destino inválido (vídeo inexistente, pasta já existente...)."""


class ErroFerramenta(Exception):
    """Falha ao executar ffmpeg/ffprobe ou ao interpretar a saída deles."""


# --------------------------------------------------------------------------
# Sondagem (ffprobe)
# --------------------------------------------------------------------------


def _inteiro_positivo(valor):
    """Converte para int > 0; devolve None quando indisponível ("N/A", vazio...)."""
    try:
        numero = int(str(valor).strip())
    except (TypeError, ValueError):
        return None
    return numero if numero > 0 else None


def _decimal_positivo(valor):
    try:
        numero = float(str(valor).strip())
    except (TypeError, ValueError):
        return None
    return numero if numero > 0 else None


def _rotacao_graus(stream):
    """Rotação de exibição declarada no stream (0, 90, 180 ou 270)."""
    candidatos = []
    tags = stream.get("tags") or {}
    if "rotate" in tags:
        candidatos.append(tags["rotate"])
    for dado in stream.get("side_data_list") or []:
        if isinstance(dado, dict) and "rotation" in dado:
            candidatos.append(dado["rotation"])
    for candidato in candidatos:
        try:
            return int(round(float(candidato))) % 360
        except (TypeError, ValueError):
            continue
    return 0


def _rodar_ffprobe(ffprobe, argumentos):
    comando = [ffprobe, "-v", "error", *argumentos]
    try:
        resultado = subprocess.run(
            comando,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as erro:
        raise ErroFerramenta(f"não consegui executar o ffprobe: {erro}") from erro
    if resultado.returncode != 0:
        detalhe = resultado.stderr.strip() or "sem mensagem"
        raise ErroFerramenta(f"ffprobe falhou: {detalhe}")
    try:
        return json.loads(resultado.stdout or "{}")
    except json.JSONDecodeError as erro:
        raise ErroFerramenta(f"saída do ffprobe não é JSON válido: {erro}") from erro


def sondar_video(video, ffprobe="ffprobe"):
    """Lê do ffprobe os metadados do primeiro stream de vídeo "de verdade".

    Capas embutidas (attached_pic) são ignoradas. ``nb_frames`` vem só dos
    metadados do contêiner: é None quando o formato não o declara.
    """
    dados = _rodar_ffprobe(
        ffprobe,
        ["-print_format", "json", "-show_streams", "-show_format", "-i", str(video)],
    )
    escolhido = None
    for stream in dados.get("streams", []):
        if stream.get("codec_type") != "video":
            continue
        if (stream.get("disposition") or {}).get("attached_pic") == 1:
            continue
        escolhido = stream
        break
    if escolhido is None:
        raise ErroFerramenta("o arquivo não tem nenhum stream de vídeo decodificável")

    largura = _inteiro_positivo(escolhido.get("width"))
    altura = _inteiro_positivo(escolhido.get("height"))
    if largura is None or altura is None:
        raise ErroFerramenta("não consegui obter largura e altura do vídeo")

    duracao = _decimal_positivo(escolhido.get("duration"))
    if duracao is None:
        duracao = _decimal_positivo((dados.get("format") or {}).get("duration"))

    return {
        "indice_stream": int(escolhido.get("index", 0)),
        "codec": escolhido.get("codec_name"),
        "largura": largura,
        "altura": altura,
        "rotacao_graus": _rotacao_graus(escolhido),
        "taxa_media": escolhido.get("avg_frame_rate"),
        "duracao_segundos": duracao,
        "nb_frames": _inteiro_positivo(escolhido.get("nb_frames")),
    }


def contar_quadros_ffprobe(video, indice_stream, ffprobe="ffprobe"):
    """Conta os quadros decodificando o stream inteiro (lento, mas independente)."""
    dados = _rodar_ffprobe(
        ffprobe,
        [
            "-count_frames",
            "-select_streams",
            str(indice_stream),
            "-show_entries",
            "stream=nb_read_frames",
            "-print_format",
            "json",
            "-i",
            str(video),
        ],
    )
    streams = dados.get("streams") or []
    if not streams:
        return None
    return _inteiro_positivo(streams[0].get("nb_read_frames"))


# --------------------------------------------------------------------------
# Geometria e comando do ffmpeg
# --------------------------------------------------------------------------


def _par(numero):
    return numero + (numero % 2)


def calcular_caixa(info, largura):
    """Tamanho (largura, altura) fixo de cada célula da grade.

    Usa a proporção exibida (trocando largura/altura em rotações de 90/270).
    Os quadros que não couberem exatamente são encaixados com barras pretas,
    então a grade nunca descarta nem corta conteúdo.
    """
    largura = _par(max(int(largura), LARGURA_MINIMA))
    larg_origem, alt_origem = info["largura"], info["altura"]
    if info.get("rotacao_graus", 0) in (90, 270):
        larg_origem, alt_origem = alt_origem, larg_origem
    altura = _par(max(2, round(largura * alt_origem / larg_origem)))
    return largura, altura


def construir_filtro(caixa):
    largura, altura = caixa
    return ",".join(
        [
            f"scale={largura}:{altura}:force_original_aspect_ratio=decrease",
            f"pad={largura}:{altura}:(ow-iw)/2:(oh-ih)/2:color=black",
            "setsar=1",
            # showinfo vem ANTES do tile: conta cada quadro que entra na grade.
            "showinfo",
            f"tile={COLUNAS}x{LINHAS}:padding={ESPACO_ENTRE_QUADROS}"
            f":margin={MARGEM}:color=black",
        ]
    )


def construir_comando_ffmpeg(
    video, saida, indice_stream, caixa, ffmpeg="ffmpeg", opcao_sincronia="fps_mode"
):
    """Monta o comando. ``opcao_sincronia`` é ``fps_mode`` (ffmpeg >= 5.1) ou ``vsync``."""
    return [
        ffmpeg,
        "-hide_banner",
        "-nostdin",
        "-nostats",
        "-loglevel",
        "info",
        "-n",  # nunca sobrescreve
        "-i",
        str(video),
        "-map",
        f"0:{indice_stream}",
        "-an",
        "-sn",
        "-dn",
        "-vf",
        construir_filtro(caixa),
        f"-{opcao_sincronia}",
        "passthrough",  # sem duplicar nem descartar quadros
        "-start_number",
        "1",
        str(Path(saida) / MODELO_ARQUIVO_PRANCHA),
    ]


def executar_ffmpeg(comando):
    """Roda o ffmpeg e devolve (código, quadros que entraram na grade, cauda do log)."""
    contagem = 0
    cauda = deque(maxlen=30)
    try:
        processo = subprocess.Popen(
            comando,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as erro:
        raise ErroFerramenta(f"não consegui executar o ffmpeg: {erro}") from erro
    with processo:
        for linha in processo.stderr:
            if _REGEX_SHOWINFO.search(linha):
                contagem += 1
            else:
                cauda.append(linha.rstrip())
        codigo = processo.wait()
    return codigo, contagem, list(cauda)


# --------------------------------------------------------------------------
# Orquestração
# --------------------------------------------------------------------------


def _verificar_ferramentas(ffmpeg, ffprobe):
    for nome in (ffmpeg, ffprobe):
        if shutil.which(nome) is None:
            raise ErroFerramenta(f"ferramenta não encontrada no PATH: {nome}")


def _listar_pranchas(pasta):
    return sorted(Path(pasta).glob(PREFIXO_PRANCHA + "*.png"))


def _montar_pranchas(arquivos, processados):
    pranchas = []
    for posicao, arquivo in enumerate(arquivos):
        primeiro = posicao * QUADROS_POR_PRANCHA
        ultimo = min(primeiro + QUADROS_POR_PRANCHA, processados) - 1
        pranchas.append(
            {
                "arquivo": arquivo.name,
                "numero": posicao + 1,
                "quadro_inicial": primeiro,
                "quadro_final": ultimo,
                "quadros_na_prancha": max(ultimo - primeiro + 1, 0),
            }
        )
    return pranchas


def gerar_pranchas(
    video,
    saida,
    largura=LARGURA_PADRAO,
    contar_quadros=False,
    ffmpeg="ffmpeg",
    ffprobe="ffprobe",
):
    """Gera as pranchas em ``saida`` (pasta nova) e devolve o manifesto (dict)."""
    video = Path(video)
    saida = Path(saida)

    if not video.is_file():
        raise ErroUso(f"vídeo não encontrado: {video}")
    if saida.exists():
        raise ErroUso(
            f"a pasta de destino já existe e não será sobrescrita: {saida}. "
            "Informe uma pasta nova."
        )
    _verificar_ferramentas(ffmpeg, ffprobe)

    info = sondar_video(video, ffprobe)
    contados_ffprobe = (
        contar_quadros_ffprobe(video, info["indice_stream"], ffprobe)
        if contar_quadros
        else None
    )

    esperados, fonte_esperados = info["nb_frames"], "ffprobe nb_frames (metadados)"
    if esperados is None and contados_ffprobe is not None:
        esperados, fonte_esperados = contados_ffprobe, "ffprobe -count_frames"
    if esperados is None:
        fonte_esperados = None

    caixa = calcular_caixa(info, largura)

    try:
        saida.mkdir(parents=True, exist_ok=False)
    except FileExistsError as erro:
        raise ErroUso(f"a pasta de destino já existe: {saida}") from erro

    opcao = "fps_mode"
    comando = construir_comando_ffmpeg(video, saida, info["indice_stream"], caixa, ffmpeg, opcao)
    codigo, processados, cauda = executar_ffmpeg(comando)
    if codigo != 0 and any("Unrecognized option" in linha and "fps_mode" in linha for linha in cauda):
        # ffmpeg antigo (< 5.1): a opção equivalente chama-se -vsync.
        opcao = "vsync"
        comando = construir_comando_ffmpeg(video, saida, info["indice_stream"], caixa, ffmpeg, opcao)
        codigo, processados, cauda = executar_ffmpeg(comando)

    arquivos = _listar_pranchas(saida)
    pranchas_esperadas = math.ceil(processados / QUADROS_POR_PRANCHA)
    observacoes = []

    if codigo != 0:
        status = "erro"
        observacoes.append(f"o ffmpeg terminou com código {codigo}.")
    elif processados == 0:
        status = "erro"
        observacoes.append("nenhum quadro foi decodificado.")
    else:
        status = "ok"

    if status != "erro" and len(arquivos) != pranchas_esperadas:
        status = "atencao"
        observacoes.append(
            f"{processados} quadros pedem {pranchas_esperadas} prancha(s), "
            f"mas existem {len(arquivos)} arquivo(s) na pasta."
        )

    if esperados is None:
        conferencia = "sem_referencia"
        observacoes.append(
            "o contêiner não declara o número de quadros; use --contar-quadros "
            "para uma contagem independente (mais lenta)."
        )
    elif esperados == processados:
        conferencia = "confere"
    else:
        conferencia = "diverge"
        if status == "ok":
            status = "atencao"
        observacoes.append(
            f"esperados {esperados} quadros ({fonte_esperados}), "
            f"processados {processados}."
        )

    manifesto = {
        "versao_manifesto": VERSAO_MANIFESTO,
        "gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": status,
        "aviso": AVISO_SEMANTICA,
        "video": {
            "caminho": str(video.resolve()),
            "nome": video.name,
            "tamanho_bytes": video.stat().st_size,
            "codec": info["codec"],
            "largura": info["largura"],
            "altura": info["altura"],
            "rotacao_graus": info["rotacao_graus"],
            "taxa_media": info["taxa_media"],
            "duracao_segundos": info["duracao_segundos"],
            "indice_stream": info["indice_stream"],
        },
        "configuracao": {
            "colunas": COLUNAS,
            "linhas": LINHAS,
            "quadros_por_prancha": QUADROS_POR_PRANCHA,
            "largura_celula": caixa[0],
            "altura_celula": caixa[1],
            "ordem": "ordem de decodificação, esquerda para a direita e de cima para baixo",
            "modo_quadros": f"-{opcao} passthrough (sem duplicar nem descartar quadros)",
        },
        "quadros": {
            "esperados": esperados,
            "fonte_esperados": fonte_esperados,
            "contados_ffprobe": contados_ffprobe,
            "processados": processados,
            "conferencia": conferencia,
        },
        "pranchas": _montar_pranchas(arquivos, processados),
        "observacoes": observacoes,
        "comando_ffmpeg": comando,
    }
    if codigo != 0:
        manifesto["erro_ffmpeg_cauda"] = cauda

    # Modo "x": falha em vez de sobrescrever um manifesto existente.
    with open(saida / NOME_MANIFESTO, "x", encoding="utf-8") as arquivo:
        json.dump(manifesto, arquivo, ensure_ascii=False, indent=2)
        arquivo.write("\n")
    return manifesto


# --------------------------------------------------------------------------
# Linha de comando
# --------------------------------------------------------------------------


def _saida_padrao(video):
    carimbo = datetime.now().strftime("%Y%m%d-%H%M%S")
    return Path.cwd() / f"pranchas_{Path(video).stem}_{carimbo}"


def _criar_parser():
    parser = argparse.ArgumentParser(
        description="Gera pranchas 5x5 com todos os quadros decodificados de um vídeo local."
    )
    parser.add_argument("video", help="caminho do vídeo local")
    parser.add_argument(
        "--saida",
        help="pasta de destino NOVA (padrão: pranchas_<vídeo>_<data> no diretório atual)",
    )
    parser.add_argument(
        "--largura",
        type=int,
        default=LARGURA_PADRAO,
        help=f"largura em pixels de cada quadro na prancha (padrão: {LARGURA_PADRAO})",
    )
    parser.add_argument(
        "--contar-quadros",
        action="store_true",
        help="conta os quadros com ffprobe -count_frames (lento; útil quando o contêiner "
        "não declara o total)",
    )
    parser.add_argument("--ffmpeg", default="ffmpeg", help="executável do ffmpeg")
    parser.add_argument("--ffprobe", default="ffprobe", help="executável do ffprobe")
    return parser


def main(argv=None):
    argumentos = _criar_parser().parse_args(argv)
    if argumentos.largura < LARGURA_MINIMA:
        print(f"erro: --largura deve ser ao menos {LARGURA_MINIMA}.", file=sys.stderr)
        return EXIT_USO
    saida = Path(argumentos.saida) if argumentos.saida else _saida_padrao(argumentos.video)

    try:
        manifesto = gerar_pranchas(
            argumentos.video,
            saida,
            largura=argumentos.largura,
            contar_quadros=argumentos.contar_quadros,
            ffmpeg=argumentos.ffmpeg,
            ffprobe=argumentos.ffprobe,
        )
    except ErroUso as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return EXIT_USO
    except ErroFerramenta as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return EXIT_ERRO

    quadros = manifesto["quadros"]
    print(f"Status: {manifesto['status']}")
    print(f"Pasta: {saida}")
    print(f"Pranchas: {len(manifesto['pranchas'])} (5x5, {QUADROS_POR_PRANCHA} quadros cada)")
    print(
        f"Quadros esperados: {quadros['esperados'] if quadros['esperados'] is not None else 'indisponível'}"
        f" | processados: {quadros['processados']} | conferência: {quadros['conferencia']}"
    )
    for observacao in manifesto["observacoes"]:
        print(f"- {observacao}")
    print(f"Manifesto: {saida / NOME_MANIFESTO}")
    print(f"AVISO: {AVISO_SEMANTICA}")

    if manifesto["status"] == "erro":
        return EXIT_ERRO
    if manifesto["status"] == "atencao":
        return EXIT_ATENCAO
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
