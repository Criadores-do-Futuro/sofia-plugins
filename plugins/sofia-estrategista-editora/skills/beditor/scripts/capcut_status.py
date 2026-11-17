#!/usr/bin/env python3
"""Read-only CapCut installation inventory. Never reads account credentials."""

import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess


SERVERS = {
    "capcut_creation": "https://www.capcut.com/api/external_mcp",
    "capcut_creation_resource": "https://www.capcut.com/api/external_mcp/resource",
}


def emit(status, **fields):
    print(json.dumps({"status": status, "authorization": "not_checked", **fields},
                     ensure_ascii=False, indent=2))
    return 0 if status == "ready" else 1


def resolve_cli(explicit):
    if explicit:
        candidate = Path(explicit)
        if not candidate.is_absolute() or not candidate.is_file():
            return None
        return str(candidate)
    if platform.system() == "Darwin":
        # A running app identifies which bundled CLI belongs to this host.
        try:
            processes = subprocess.run(["ps", "-axo", "comm="], capture_output=True,
                                       text=True, timeout=10, check=True).stdout
        except (OSError, subprocess.SubprocessError):
            return None
        apps = [name for name in ("ChatGPT", "Codex")
                if f"/Applications/{name}.app/Contents/" in processes]
        if len(apps) != 1:
            return None
        root = Path(f"/Applications/{apps[0]}.app/Contents/Resources")
        for relative in ("codex", "codex-cli/bin/codex",
                         "codex-cli/CodexCLI.app/Contents/MacOS/codex"):
            candidate = root / relative
            if candidate.is_file() and os.access(candidate, os.X_OK):
                return str(candidate)
    # Other layouts require an explicitly confirmed absolute native CLI.
    return None


def cli_json(cli, arguments):
    try:
        result = subprocess.run([cli, *arguments], capture_output=True, text=True,
                                timeout=30, check=False)
    except (OSError, subprocess.SubprocessError):
        return None, "inventory_execution_failed"
    if result.returncode:
        # Do not echo raw stderr/headers/configuration into the conversation.
        missing = arguments[:2] == ["mcp", "get"] and "No MCP server named" in result.stderr
        return None, "server_missing" if missing else "inventory_command_failed"
    try:
        return json.loads(result.stdout), None
    except (ValueError, TypeError):
        return None, "inventory_invalid_json"


def same_path(actual, expected):
    if not isinstance(actual, str) or not Path(actual).is_absolute():
        return False
    return os.path.normcase(str(Path(actual).resolve())) == os.path.normcase(str(expected.resolve()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-cli", help="Confirmed absolute native CLI path")
    args = parser.parse_args()
    if platform.system() not in ("Darwin", "Windows"):
        return emit("prerequisite_missing", reason="native_desktop_host_required")
    cli = resolve_cli(args.codex_cli)
    if not cli:
        return emit("prerequisite_missing", reason="confirm_native_host_cli",
                    path_candidate=shutil.which("codex"))
    home = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex").expanduser().resolve()
    managed = home / "plugin-marketplaces" / "CapCut"
    inventory, error = cli_json(cli, ["plugin", "list", "--marketplace", "CapCut", "--available", "--json"])
    if error:
        return emit("unknown", reason=error, codex_cli=cli)
    if not isinstance(inventory, dict) or not isinstance(inventory.get("installed"), list):
        return emit("unknown", reason="inventory_shape_unrecognized", codex_cli=cli)
    entries = [p for p in inventory["installed"]
               if isinstance(p, dict) and p.get("pluginId") == "CapCut@CapCut"]
    if not entries:
        return emit("not_installed", codex_cli=cli, codex_data=str(home))
    if len(entries) != 1:
        return emit("unknown", reason="ambiguous_plugin_registration", codex_cli=cli)
    plugin = entries[0]
    issues = []
    if not plugin.get("installed") or not plugin.get("enabled"):
        issues.append("plugin_not_installed_or_disabled")
    source = plugin.get("source") or {}
    marketplace = plugin.get("marketplaceSource") or {}
    if not isinstance(source, dict) or not isinstance(marketplace, dict):
        return emit("unknown", reason="source_shape_unrecognized", codex_cli=cli)
    if not same_path(source.get("path"), managed / "codex") or not same_path(marketplace.get("source"), managed):
        issues.append("source_not_managed")
    server_states = {}
    for name, url in SERVERS.items():
        server, error = cli_json(cli, ["mcp", "get", name, "--json"])
        if error and error != "server_missing":
            return emit("unknown", reason=error, server=name, codex_cli=cli)
        if error:
            server_states[name] = "missing"
        elif not isinstance(server, dict) or not isinstance(server.get("transport"), dict):
            return emit("unknown", reason="server_shape_unrecognized", server=name, codex_cli=cli)
        elif server.get("enabled") is not True or server["transport"].get("url") != url:
            server_states[name] = "disabled_or_unexpected_endpoint"
        else:
            server_states[name] = "enabled"
        if server_states[name] != "enabled":
            issues.append(name + ":" + server_states[name])
    helpers = managed / "codex" / "skills" / "mcp-auth" / "scripts"
    for name in ("capcut-login.mjs", "check-connection.mjs"):
        if not (helpers / name).is_file():
            issues.append("helper_missing:" + name)
    return emit("review_required" if issues else "ready", version=plugin.get("version"),
                codex_cli=cli, codex_data=str(home), servers=server_states, issues=issues)


if __name__ == "__main__":
    raise SystemExit(main())
