"""Adaptador explícito para a ponte MCP local do CapCut Desktop.

Esta rota cria apenas um novo projeto; não é o plugin oficial do CapCut Web.
O pacote preparado não significa que o CapCut o aceitou ou exibiu corretamente.
"""
from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse


class UnsupportedPlan(ValueError):
    """O plano pede uma operação que esta tradução não consegue preservar."""


class BridgeError(RuntimeError):
    """A ponte recusou ou não comprovou a operação solicitada."""


def _media_path(uri: str) -> Path:
    parsed = urlparse(uri)
    if parsed.scheme and parsed.scheme != "file":
        raise UnsupportedPlan("A ponte Desktop requer mídia local, não uma URL remota")
    if parsed.scheme == "file":
        if parsed.netloc not in ("", "localhost") or parsed.query or parsed.fragment:
            raise UnsupportedPlan("URI de mídia local inválida")
        value = unquote(parsed.path)
    else:
        value = uri
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise UnsupportedPlan("Caminho de mídia deve ser absoluto")
    path = path.resolve(strict=True)
    if not path.is_file():
        raise UnsupportedPlan("Mídia deve ser arquivo regular")
    return path


def translate(plan: dict[str, Any]) -> dict[str, Any]:
    """Traduz somente um corte simples de fala sem sobreposição ou lettering.

    Rejeita o restante em vez de descartar dados. A ponte sempre cria uma pista
    de diálogo por segmento; por isso cada vídeo deve declarar o áudio original.
    """
    from scripts.validar_plano_editorial import validate

    errors = validate(plan)
    if errors:
        raise UnsupportedPlan("Plano inválido: " + "; ".join(errors))
    if plan["project"]["editor"] != "capcut":
        raise UnsupportedPlan("Plano precisa selecionar CapCut explicitamente")
    if plan.get("text_layers"):
        raise UnsupportedPlan("Tradução de legendas e lettering ainda não implementada")
    clips = sorted(plan["clips"], key=lambda clip: clip["timeline"]["start_ms"])
    if not clips:
        raise UnsupportedPlan("É necessário ao menos um clipe de vídeo")
    if len({clip["track"] for clip in clips}) != 1:
        raise UnsupportedPlan("A ponte simples requer uma única pista de vídeo")
    assets = {asset["id"]: asset for asset in plan["assets"]}
    segments = []
    cursor = 0
    for clip in clips:
        asset = assets[clip["asset_id"]]
        if clip["kind"] != "video" or asset["kind"] != "video":
            raise UnsupportedPlan("Áudio independente e imagens ainda não são traduzidos")
        if not clip.get("carries_source_audio", False):
            raise UnsupportedPlan("A ponte criaria áudio não solicitado; declare áudio original ou use outra rota")
        start, end = clip["timeline"]["start_ms"], clip["timeline"]["end_ms"]
        if start != cursor:
            raise UnsupportedPlan("Lacunas e sobreposições não são representáveis nesta rota")
        duration = end - start
        if duration < 200:
            raise UnsupportedPlan("A ponte exige segmentos de pelo menos 200 ms")
        if not asset.get("uri"):
            raise UnsupportedPlan(f"Asset {asset['id']} sem URI local")
        try:
            media = _media_path(asset["uri"])
        except OSError as exc:
            raise UnsupportedPlan(f"Mídia inacessível para {asset['id']}: {exc}") from exc
        segments.append({
            "id": clip["id"], "assetID": asset["id"], "sourceURL": media.as_uri(),
            "sourceStart": clip["source"]["start_ms"] / 1000,
            "duration": duration / 1000,
            "reason": clip.get("reason", "Corte solicitado no plano"),
        })
        cursor = end
    return {"id": str(uuid.uuid4()), "format": plan["project"]["creative_format"], "segments": segments,
            "transitions": [], "captions": [], "mediaCues": [], "visualBeats": []}


def write_package(plan: dict[str, Any], directory: str | Path) -> Path:
    """Cria um pacote novo; falha se o destino já existir e preserva a fonte."""
    translated = translate(plan)
    directory = Path(directory).expanduser()
    if not directory.is_absolute():
        raise ValueError("O destino do pacote deve ser absoluto")
    directory = directory.parent.resolve(strict=True) / directory.name
    manifest = {"schemaVersion": "1.1.0", "projectID": translated["id"],
                "allowedRoot": directory.as_uri(), "planFile": "edit-plan.json",
                "handoffs": [{"integration": "capCut", "primaryArtifact": "edit-plan.json",
                              "phase": "preview", "operations": [], "safetyRules": []}]}
    directory.mkdir()  # Criação exclusiva: nunca sobrescrever uma pasta existente.
    try:
        (directory / "edit-plan.json").write_text(json.dumps(translated, ensure_ascii=False, indent=2), encoding="utf-8")
        (directory / "mcp-handoff.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        shutil.rmtree(directory)
        raise
    return directory


async def call_bridge(session: Any, operation: str, package: str | Path | None = None,
                      *, project_name: str | None = None, confirmation_token: str | None = None) -> Any:
    """Executa somente as ferramentas tipadas da ponte em uma sessão MCP existente.

    `commit` é uma chamada separada e exige o token exato obtido na prévia. A
    autorização da ação deve ser decidida pelo chamador conforme o pedido do usuário.
    """
    if operation not in {"status", "prepare", "preview", "commit"}:
        raise ValueError("Operação desconhecida")
    arguments: dict[str, str] = {}
    if operation != "status":
        if package is None or not Path(package).is_absolute():
            raise ValueError("Informe o caminho absoluto do pacote")
        arguments["packageRoot"] = str(Path(package).resolve(strict=True))
    if operation == "prepare" and project_name is not None:
        arguments["projectName"] = project_name
    if operation == "commit":
        import re
        if not confirmation_token or not re.fullmatch(r"[0-9a-f]{64}", confirmation_token):
            raise ValueError("Commit requer o token da prévia")
        arguments["confirmationToken"] = confirmation_token
    result = await session.call_tool("beditor_capcut_" + operation, arguments)
    if getattr(result, "is_error", getattr(result, "isError", False)):
        message = " ".join(getattr(item, "text", "") for item in result.content)
        raise BridgeError(message or "A ponte retornou erro")
    texts = [item.text for item in result.content if getattr(item, "type", None) == "text"]
    if len(texts) != 1:
        raise BridgeError("Resposta inesperada da ponte")
    try:
        return json.loads(texts[0])
    except (TypeError, json.JSONDecodeError) as exc:
        raise BridgeError("Resposta da ponte não é JSON válido") from exc


async def call_local_bridge(server_js: str | Path, operation: str, package: str | Path | None = None,
                            **options: Any) -> Any:
    """Abre a ponte MCP fornecida pelo host; não instala dependências nem edita por si."""
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError as exc:
        raise BridgeError("Instale o SDK Python MCP para chamar a ponte local") from exc
    server = Path(server_js).expanduser().resolve(strict=True)
    if not server.is_file():
        raise ValueError("O servidor MCP precisa ser um arquivo existente")
    params = StdioServerParameters(command="node", args=[str(server)])
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            return await call_bridge(session, operation, package, **options)
