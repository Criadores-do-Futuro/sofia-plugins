#!/usr/bin/env python3
"""Gera dois ZIPs por plugin (Claude e OpenAI) e inspeciona o conteúdo final de cada um.

- `<nome>-<versão>.zip`: a pasta do plugin como está, para o Claude (só texto e imagem).
- `<nome>-<versão>-openai.zip`: o pacote do diretório do ChatGPT e do Codex, com o manifesto
  portátil (`listings/<nome>.json`) como `plugin.json` e o MCP (`listings/<nome>.mcp.json`)
  como `mcp.json` na raiz. Sai sem `.claude-plugin/`, `.codex-plugin/` e `agents/` (os agentes
  são do Claude Code); a raiz com `extensions.com.openai` já substitui o manifesto do Codex.
"""

import argparse
import hashlib
import json
import re
import tempfile
import zipfile
from pathlib import Path

import jsonschema

from validate_plugins import (LISTINGS, MCP_SCHEMA, NAMES, ROOT, SCHEMA, listing, mcp_config, validate_all,
                              validate_plugin)

# O que fica fora do pacote da OpenAI, no primeiro nível da pasta do plugin.
OPENAI_SKIP = {".claude-plugin", ".codex-plugin", "agents", ".gitignore"}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect_openai(path: Path) -> list[str]:
    """Confere o ZIP da OpenAI como o portal o lê: manifestos na raiz e skills autocontidas."""
    problems: list[str] = []
    with zipfile.ZipFile(path) as archive, tempfile.TemporaryDirectory() as temp:
        if archive.testzip():
            return ["ZIP corrompido"]
        names = archive.namelist()
        if len(names) != len(set(names)):
            problems.append("Caminho repetido no ZIP")
        archive.extractall(temp)
        root = Path(temp)
        jsonschema.validate(json.loads((root / "plugin.json").read_text()), SCHEMA)
        jsonschema.validate(json.loads((root / "mcp.json").read_text()), MCP_SCHEMA)
        for forbidden in (".app.json", "hooks", ".claude-plugin", ".codex-plugin", ".mcp.json"):
            if (root / forbidden).exists():
                problems.append(f"O portal recusa ou ignora {forbidden} no pacote da OpenAI")
        for skill in (root / "skills").glob("*/SKILL.md"):
            base = skill.parent.resolve()
            for doc in skill.parent.rglob("*.md"):
                for href in re.findall(r"\]\(([^)]+)\)", doc.read_text()):
                    target = href.split("#", 1)[0]
                    if target and ":" not in target:
                        dest = (doc.parent / target).resolve()
                        if not (dest.is_relative_to(base) and dest.exists()):
                            problems.append(f"Link fora da skill ou ausente: {doc.relative_to(root)} -> {target}")
        # Fora das skills (README e afins): o link só precisa existir dentro do pacote. Pega, por
        # exemplo, um README que aponta para agents/, pasta que não vai para a OpenAI.
        for doc in root.rglob("*.md"):
            if doc.is_relative_to(root / "skills"):
                continue
            for href in re.findall(r"\]\(([^)]+)\)", doc.read_text()):
                target = href.split("#", 1)[0].strip()
                if target and ":" not in target:
                    dest = (doc.parent / target).resolve()
                    if not (dest.is_relative_to(root.resolve()) and dest.exists()):
                        problems.append(f"Link quebrado no pacote da OpenAI: {doc.relative_to(root)} -> {target}")
    return problems


def package_openai(name: str, folder: Path, output: Path) -> Path:
    manifest = listing(name)
    path = output / f"{name}-{manifest['version']}-openai.zip"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("plugin.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        archive.writestr("mcp.json", json.dumps(mcp_config(name), ensure_ascii=False, indent=2) + "\n")
        for source in sorted(folder.rglob("*")):
            relative = source.relative_to(folder)
            if source.is_file() and relative.parts[0] not in OPENAI_SKIP:
                archive.write(source, str(relative))
    problems = inspect_openai(path)
    if problems:
        raise ValueError(json.dumps(problems, ensure_ascii=False))
    return path


def package(output: Path, require_submission: bool = False) -> list[dict]:
    reports = validate_all()
    if any(r["errors"] for r in reports):
        raise ValueError("Corrija os erros estruturais antes de empacotar")
    if require_submission and any(r["missing_listing_fields"] for r in reports):
        raise ValueError("Listagem incompleta; consulte tools/validate_plugins.py --submission")
    output.mkdir(parents=True, exist_ok=True)
    inventory = []
    for name, report in zip(NAMES, reports):
        folder = ROOT / "plugins" / name
        if output.resolve().is_relative_to(folder.resolve()) or output.resolve().is_relative_to(LISTINGS.resolve()):
            raise ValueError("O ZIP deve ficar fora da pasta do plugin e de listings/")
        version = json.loads((folder / ".claude-plugin/plugin.json").read_text())["version"]
        path = output / f"{name}-{version}.zip"
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
            for source in sorted(folder.rglob("*")):
                if source.is_file():
                    archive.write(source, str(source.relative_to(folder)))
        with zipfile.ZipFile(path) as archive, tempfile.TemporaryDirectory() as temp:
            if archive.testzip():
                raise ValueError("ZIP corrompido")
            extracted = Path(temp) / name
            archive.extractall(extracted)
            inspected = validate_plugin(extracted)
            if inspected["errors"]:
                raise ValueError(json.dumps(inspected["errors"], ensure_ascii=False))
            files = len(archive.namelist())
        openai = package_openai(name, folder, output)
        with zipfile.ZipFile(openai) as archive:
            openai_files = len(archive.namelist())
        inventory.append({"plugin": name, "version": version, "archive": path.name, "sha256": _sha(path),
                          "files": files, "openai_archive": openai.name, "openai_sha256": _sha(openai),
                          "openai_files": openai_files, "structure_valid": True,
                          "missing_listing_fields": report["missing_listing_fields"],
                          "publication_ready": False})
    (output / "inventory.json").write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n")
    return inventory


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    parser.add_argument("--require-submission-ready", action="store_true")
    args = parser.parse_args()
    print(json.dumps(package(args.output, args.require_submission_ready), ensure_ascii=False, indent=2))
