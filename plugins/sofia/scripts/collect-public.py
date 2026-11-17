#!/usr/bin/env python3
"""Coleta metadados e comentários públicos, sem persistir dados de autores."""

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse


def sanitize(data: dict, limit: int) -> dict:
    comments = data.get("comments") or []
    cleaned = [{"texto": str(c.get("text") or ""), "curtidas": c.get("like_count") or 0}
               for c in comments if isinstance(c, dict)]
    cleaned.sort(key=lambda c: c["curtidas"] if isinstance(c["curtidas"], (int, float)) else 0, reverse=True)
    return {"titulo": data.get("title"), "endereco": data.get("webpage_url"),
            "duracao_segundos": data.get("duration"), "visualizacoes": data.get("view_count"),
            "curtidas": data.get("like_count"), "comentarios": cleaned[:limit]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="Endereço HTTPS público autorizado")
    parser.add_argument("--allow-download", action="store_true", help="Confirma coleta pública autorizada")
    parser.add_argument("--comments", action="store_true", help="Inclui comentários sem dados de autor")
    parser.add_argument("--limit", type=int, default=20, help="Limite de comentários, de 1 a 100")
    parser.add_argument("--output", help="Pasta nova e vazia de saída")
    args = parser.parse_args()
    host = urlparse(args.url)
    allowed = ("youtube.com", "youtu.be", "instagram.com", "tiktok.com")
    if host.scheme != "https" or host.username or host.password or not any(
        host.hostname == d or (host.hostname or "").endswith("." + d) for d in allowed
    ):
        parser.error("Use um endereço HTTPS público de YouTube, Instagram ou TikTok.")
    if not args.allow_download:
        parser.error("Confirme o direito de uso e acrescente --allow-download.")
    if not 1 <= args.limit <= 100:
        parser.error("O limite de comentários deve ficar entre 1 e 100.")
    if not shutil.which("yt-dlp"):
        parser.error("Dependência ausente: yt-dlp. Instale apenas com autorização.")
    dest = Path(args.output).expanduser().resolve() if args.output else Path(tempfile.mkdtemp(prefix="sofia-coleta-"))
    if dest.exists() and any(dest.iterdir()):
        parser.error("A pasta de saída precisa estar vazia.")
    dest.mkdir(parents=True, exist_ok=True)
    cmd = ["yt-dlp", "--ignore-config", "--no-playlist", "--skip-download", "--dump-single-json"]
    if args.comments:
        cmd += ["--write-comments", "--extractor-args", f"youtube:comment_sort=top;max_comments={args.limit}"]
    try:
        result = subprocess.run([*cmd, "--", args.url], check=True, capture_output=True, text=True,
                                stdin=subprocess.DEVNULL)
        data = sanitize(json.loads(result.stdout), args.limit)
    except (subprocess.CalledProcessError, ValueError, OSError):
        parser.exit(1, "Não foi possível coletar. Se houver login, peça o arquivo ou a transcrição; não use cookies.\n")
    path = dest / "dados.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
