#!/usr/bin/env python3
"""Gera um ZIP por plugin público e inspeciona o conteúdo final.

Plugins internos (INTERNAL em validate_plugins.py, como a sofia-interna) nunca entram aqui.
"""

import argparse
import hashlib
import json
import tempfile
import zipfile
from pathlib import Path

from validate_plugins import ROOT, NAMES, validate_all, validate_plugin


def package(output: Path, require_submission: bool = False) -> list[dict]:
    reports = validate_all()
    if any(r["errors"] for r in reports):
        raise ValueError("Corrija os erros estruturais antes de empacotar")
    if require_submission and any(r["missing_listing_fields"] for r in reports):
        raise ValueError("Listagem incompleta; consulte tools/validate_plugins.py --submission")
    output.mkdir(parents=True, exist_ok=True)
    inventory = []
    # reports traz as públicas (NAMES) e depois as internas: só as públicas viram ZIP.
    for name, report in zip(NAMES, reports[:len(NAMES)]):
        folder = ROOT / "plugins" / name
        if output.resolve().is_relative_to(folder.resolve()):
            raise ValueError("O ZIP deve ficar fora da pasta do plugin")
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
            inventory.append({"plugin": name, "version": version, "archive": path.name,
                              "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                              "files": len(archive.namelist()), "structure_valid": True,
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
