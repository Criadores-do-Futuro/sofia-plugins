#!/usr/bin/env python3
"""Baixa uma referência pública individual para uma pasta local nova.

O download depende do yt-dlp e ffprobe. A URL não é salva nos metadados do
resultado; o site e o processo do sistema ainda podem vê-la durante o download.
Não usa cookies, credenciais de browser, configuração de usuário ou playlists.
"""
from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

EXTENSOES = {'.mp4', '.mkv', '.webm', '.mov', '.m4v', '.avi'}
OPCOES = ['--ignore-config', '--no-plugin-dirs', '--no-cookies', '--no-cookies-from-browser',
          '--no-cache-dir', '--no-playlist', '--max-downloads', '1', '--no-write-info-json',
          '--no-write-description', '--no-write-comments', '--no-write-thumbnail',
          '--no-write-subs', '--no-write-auto-subs', '--no-embed-metadata',
          '--no-progress', '--no-overwrites', '--no-continue', '--no-part']


def validar_url(url: str) -> None:
    if any(ord(c) < 32 or ord(c) == 127 for c in url):
        raise ValueError('URL inválida')
    try:
        partes = urlsplit(url)
        host = partes.hostname
        port = partes.port
    except ValueError:
        raise ValueError('URL inválida') from None
    if partes.scheme not in ('http', 'https') or not host or partes.username is not None or partes.password is not None:
        raise ValueError('Informe uma URL HTTP(S) sem credenciais embutidas')
    if host.lower() == 'localhost' or host.lower().endswith('.localhost') or '.' not in host and ':' not in host:
        raise ValueError('Informe um endereço público')
    try:
        endereco = ipaddress.ip_address(host)
    except ValueError:
        endereco = None
    if endereco is not None and not endereco.is_global:
        raise ValueError('Informe um endereço público')
    if port is not None and not 1 <= port <= 65535:
        raise ValueError('Porta inválida')


def executar(args: list[str], timeout: int) -> str:
    try:
        resultado = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=True)
    except (OSError, subprocess.SubprocessError):
        # stdout/stderr e argumentos do yt-dlp podem conter a URL assinada.
        raise ValueError('A ferramenta não concluiu a operação; verifique acesso, rede e dependências') from None
    return resultado.stdout


def baixar(url: str, destino: Path) -> dict:
    validar_url(url)
    destino = destino.expanduser().absolute()
    if destino.exists() or destino.is_symlink():
        raise ValueError('A pasta de destino já existe')
    parent = destino.parent.resolve(strict=True)
    if not parent.is_dir():
        raise ValueError('A pasta superior do destino precisa existir')
    # Só inspeciona o primeiro item antes de baixar. Um objeto playlist é recusado.
    saida = executar(['yt-dlp', *OPCOES, '--playlist-items', '1', '--skip-download',
                      '--dump-single-json', '--', url], 120)
    try:
        info = json.loads(saida)
    except json.JSONDecodeError:
        raise ValueError('Não foi possível identificar a referência') from None
    if not isinstance(info, dict) or info.get('_type') in ('playlist', 'multi_video') or 'entries' in info:
        raise ValueError('Forneça um vídeo individual; playlists não são aceitas')
    del info, saida
    with tempfile.TemporaryDirectory(prefix='.beditor-download-', dir=parent) as temp:
        scratch = Path(temp).resolve()
        linha = executar(['yt-dlp', *OPCOES, '--merge-output-format', 'mp4',
                          '-o', str(scratch/'referencia.%(ext)s'), '--print', 'after_move:filepath',
                          '--', url], 36000)
        arquivos = [Path(x) for x in linha.splitlines() if x.strip()]
        if len(arquivos) != 1 or arquivos[0].is_symlink():
            raise ValueError('O download não retornou um único vídeo local')
        video = arquivos[0].resolve(strict=True)
        if video.parent != scratch or video.suffix.lower() not in EXTENSOES or not video.is_file() or video.stat().st_size == 0:
            raise ValueError('O download não produziu um vídeo válido')
        probe = executar(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                          'stream=codec_type', '-of', 'json', str(video)], 120)
        try:
            if not json.loads(probe).get('streams'):
                raise ValueError('O arquivo não possui uma trilha de vídeo')
        except json.JSONDecodeError:
            raise ValueError('Não foi possível validar o vídeo baixado') from None
        h = hashlib.sha256()
        with video.open('rb') as f:
            for bloco in iter(lambda: f.read(1024 * 1024), b''):
                h.update(bloco)
        destino = parent / destino.name
        destino.mkdir(exist_ok=False)
        arquivo = destino / ('referencia' + video.suffix.lower())
        try:
            # Link exclusivo, no mesmo volume; o temporário é removido ao sair.
            os.link(video, arquivo, follow_symlinks=False)
        except OSError:
            destino.rmdir()
            raise
        return {'arquivo': str(arquivo), 'sha256': h.hexdigest(), 'bytes': arquivo.stat().st_size,
                'limites': ['URL não foi salva neste relatório; acesso depende do site.',
                            'Não valida direitos de uso e não contorna acesso restrito.']}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('url', nargs='?', help='Link HTTP(S) de um vídeo individual acessível sem login')
    p.add_argument('--url-stdin', action='store_true', help='Lê o link pela entrada padrão em vez de argumento')
    p.add_argument('--saida', type=Path, required=True, help='Pasta nova para o arquivo')
    args = p.parse_args()
    if bool(args.url) == bool(args.url_stdin):
        p.error('Informe URL como argumento ou use --url-stdin')
    url = sys.stdin.readline().strip() if args.url_stdin else args.url
    try:
        resultado = baixar(url, args.saida)
    except (OSError, ValueError):
        # Não exponha mensagens de terceiros que possam conter URL ou parâmetros.
        print('Download não concluído. Verifique a URL, acesso público, destino novo e dependências.', file=sys.stderr)
        return 1
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
