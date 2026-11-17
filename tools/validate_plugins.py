#!/usr/bin/env python3
"""Valida estrutura, referências e metadados sem confundir pacote com publicação."""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
from pathlib import Path

import jsonschema
import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("sofia-br", "sofia-latam", "sofia-english")
# Plugins de uso interno da equipe não ficam neste repositório público: a Sofia Interna
# vive no repositório privado Criadores-do-Futuro/sofia-interna. A lista fica vazia de
# propósito; os testes conferem que nenhum interno entra no pacote público.
INTERNAL: tuple[str, ...] = ()
# A Sofia Estrategista, a mais completa: além do método, edita vídeo, então leva scripts,
# fontes e modelos que o diretório público não aceita de organização não verificada.
# Ela é distribuída pelo próprio .zip (enviado em Personalizar > Plugins) e por este
# marketplace. A cópia vem do repositório de origem por tools/sincronizar_estrategista.sh;
# o conteúdo restrito do método fica no conector (MCP), não nos arquivos.
COMPLETE = ("sofia-estrategista-editora",)
ALL_NAMES = NAMES + INTERNAL + COMPLETE
# O envio de plugin no claude.ai recusa o .zip inteiro se um caminho tiver outro caractere.
PATH_CHARS = re.compile(r"[A-Za-z0-9._/-]+")
SCHEMA = json.loads((ROOT / "tools/schemas/plugin.schema.json").read_text())
CATEGORIES = {"Business & Operations", "Communication", "Creativity", "Data & Analytics",
              "Developer Tools", "Education & Research", "Entertainment", "Finance",
              "Healthcare", "Other", "Productivity", "Scientific Research", "Security", "Travel"}
URL_FIELDS = ("websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL")
# Manifesto agent-plugins (listagem do Codex) fica fora da pasta do plugin:
# o diretório da Anthropic avisa quando o encontra dentro do pacote.
LISTINGS = ROOT / "listings"


def listing(name: str) -> dict:
    return json.loads((LISTINGS / f"{name}.json").read_text())


def contained(base: Path, target: str) -> Path:
    result = (base / target).resolve()
    if not result.is_relative_to(base.resolve()):
        raise ValueError(f"Caminho fora do pacote: {target}")
    return result


# Regras que o diretório da Anthropic aplica a organizações não verificadas.
# Cada uma veio de um bloqueio ou aviso real do portal; acrescente as novas aqui.
PORTAL_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico"}
PORTAL_NAMES = {"LICENSE", ".gitignore"}
PORTAL_FORBIDDEN = {"package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb", ".npmrc",
                    "requirements.txt", "pyproject.toml", "Pipfile", "Pipfile.lock", "poetry.lock"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico"}
CREDENTIAL_READ = re.compile(r"process\.env|os\.environ|getenv\(|\$\{?[A-Z][A-Z0-9_]*_(?:KEY|TOKEN|SECRET)\b"
                             r"|\b[A-Z][A-Z0-9_]*_(?:API_KEY|TOKEN|SECRET)\b")
FRONT_LINE = re.compile(r"[A-Za-z_][\w-]*:( .*)?|- .*")


def frontmatter_lines(text: str) -> list[str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    return text[4:end].split("\n") if end != -1 else None


def fix_frontmatter(text: str) -> str:
    """Junta continuações soltas na linha da chave e tira espaços no fim (sem mudar o valor YAML)."""
    lines = frontmatter_lines(text)
    if lines is None:
        return text
    out: list[str] = []
    for line in lines:
        line = line.replace("\t", "  ").rstrip()
        block = out and re.search(r":\s*[|>][-+]?$", out[-1])
        nested = out and out[-1].endswith(":")
        if line.startswith(" ") and out and not block and not nested and not out[-1].startswith(" "):
            out[-1] = out[-1] + " " + line.strip()
        else:
            out.append(line)
    return "---\n" + "\n".join(out) + text[4 + len("\n".join(lines)):]


def portal_issues(folder: Path) -> list[str]:
    issues: list[str] = []
    if (folder / "plugin.json").exists():
        issues.append("plugin.json agent-plugins na raiz do pacote (o portal avisa e o ignora)")
    readme = folder / "README.md"
    if not readme.exists() or not re.search(r"\[[^\]]*Privacy[^\]]*\]\(https://[^)]+\)", readme.read_text()):
        issues.append("README sem link \"Privacy\" (o portal não lê o link de privacidade de outro lugar)")
    files = [p for p in folder.rglob("*") if p.is_file()]
    texts = {p: p.read_text(errors="replace") for p in files if p.suffix in {".md", ".json", ".yaml", ".yml", ".txt"}}
    corpus = "\n".join(texts.values())
    for path in files:
        rel = str(path.relative_to(folder))
        if path.name in PORTAL_FORBIDDEN:
            issues.append(f"Arquivo de gerenciador de pacotes: {rel}")
        elif path.name not in PORTAL_NAMES and path.suffix.lower() not in PORTAL_SUFFIXES:
            issues.append(f"Tipo de arquivo recusado: {rel}")
        if path.read_bytes()[:2] == b"#!":
            issues.append(f"Arquivo executável (#!): {rel}")
        if path.suffix.lower() in IMAGE_SUFFIXES and rel not in corpus and f"./{rel}" not in corpus:
            issues.append(f"Imagem sem uso no pacote: {rel}")
    for path, text in texts.items():
        rel = str(path.relative_to(folder))
        if CREDENTIAL_READ.search(text):
            issues.append(f"Instrução de ler credencial da máquina: {rel}")
        if path.name == "SKILL.md":
            lines = frontmatter_lines(text) or []
            prev = ""
            for line in lines:
                bad = "\t" in line or line != line.rstrip()
                cont = line.startswith(" ") and not re.search(r":\s*[|>][-+]?$", prev) and not prev.endswith(":")
                if bad or (line and not line.startswith(" ") and not FRONT_LINE.fullmatch(line)) or (cont and not prev.startswith(" ")):
                    issues.append(f"Frontmatter fora do formato chave: valor em uma linha: {rel}")
                    break
                prev = line
    return issues


def autofix(folder: Path) -> list[str]:
    """Correções seguras e mecânicas; o resto continua como erro para revisão."""
    done: list[str] = []
    for path in folder.rglob("SKILL.md"):
        text = path.read_text()
        fixed = fix_frontmatter(text)
        if fixed != text:
            path.write_text(fixed)
            done.append(f"Frontmatter em linhas simples: {path.relative_to(folder)}")
    return done


def validate_plugin(folder: Path) -> dict:
    errors: list[str] = []
    gaps: list[str] = []
    skills: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    try:
        manifest = listing(folder.name)
        errors.extend("Portal: " + issue for issue in portal_issues(folder))
        jsonschema.validate(manifest, SCHEMA)
        check(manifest["name"] == folder.name, "Identidade diferente da pasta")
        check(bool(re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"])), "Versão semântica inválida")
        ext = manifest["extensions"]["com.openai"]
        interface = ext["interface"]
        check(0 < len(interface["displayName"]) <= 30, "Nome público inválido")
        check(0 < len(interface["shortDescription"]) <= 30, "Subtítulo inválido")
        check(0 < len(interface["longDescription"]) <= 4000, "Descrição longa inválida")
        check(interface["category"] in CATEGORIES, "Categoria não suportada")
        internal = folder.name in INTERNAL
        if not internal:
            check(ext.get("requires_local_executor") is True, "Execução local precisa ser declarada")
        prompts = interface["defaultPrompt"]
        check(isinstance(prompts, list) and 1 <= len(prompts) <= 3, "Quantidade de sugestões inválida")
        check(all(isinstance(p, str) and p.strip() and len(p) <= 128 and "\n" not in p for p in prompts),
              "Sugestão inválida")
        check(len({" ".join(p.split()) for p in prompts}) == len(prompts), "Sugestões repetidas")
        check(ext["publication"]["countries"] == [], "Distribuição mundial não preservada")
        check(isinstance(ext["review"]["commerce"], bool), "Declaração de compras inválida")
        check(bool(ext["review"].get("commerce_description")), "Descrição de compras ausente")
        for locale, translation in ext["publication"].get("translations", {}).items():
            check(locale != "en-US", "Não sintetizar tradução inglesa de base")
            check(set(translation) == {"subtitle", "description"}, "Campos de tradução inválidos")
            check(0 < len(translation["subtitle"]) <= 30 and 0 < len(translation["description"]) <= 4000,
                  "Texto de tradução inválido")
        for field in URL_FIELDS:
            url = interface.get(field)
            if not url:
                if not internal:
                    gaps.append(field)
            else:
                check(url.startswith("https://") and len(url) <= 1024, f"Endereço inválido: {field}")
        for field in ("logo", "composerIcon"):
            path = contained(folder, interface[field])
            check(interface[field].startswith("./"), "O caminho do ícone deve começar com ./")
            with Image.open(path) as icon:
                minimum = 256 if field == "logo" else 48
                check(icon.format == "PNG" and icon.width == icon.height and minimum <= icon.width <= 4096,
                      f"Ícone inválido: {field}")
            check(path.stat().st_size <= 5 * 1024 * 1024, "Ícone maior que 5 MiB")
        for relative in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
            other = json.loads((folder / relative).read_text())
            for key in ("name", "version", "description", "author"):
                check(other.get(key) == manifest.get(key), f"Manifestos divergentes: {relative}/{key}")
            check(other.get("apps") is None, "Declaração apps não permitida no envio público")
            check(other.get("extensions", {}).get("com.openai", {}).get("apps") is None,
                  "Dependência privada não permitida no envio público")
        overlay = json.loads((folder / ".codex-plugin/plugin.json").read_text())
        check(overlay["interface"] == interface, "Interface Codex divergente")
        check(overlay.get("skills") == "./skills/", "Pasta de habilidades Codex inválida")
        check(not (folder / ".app.json").exists() and manifest.get("apps") is None and ext.get("apps") is None,
              "Vínculo privado de aplicativo no envio público")
        for path in folder.rglob("*"):
            check(not path.is_symlink(), f"Link simbólico: {path.relative_to(folder)}")
            check(path.name not in {"node_modules", ".env", ".DS_Store", "__pycache__"},
                  f"Arquivo indevido: {path.relative_to(folder)}")
            if not path.is_file():
                continue
            if path.suffix == ".json":
                json.loads(path.read_text())
            if path.suffix in {".yaml", ".yml"}:
                yaml.safe_load(path.read_text())
            if path.suffix == ".py":
                ast.parse(path.read_text(), filename=str(path))
            if path.suffix in {".sh", ".mjs"}:
                cmd = ["bash", "-n"] if path.suffix == ".sh" else ["node", "--check"]
                subprocess.run([*cmd, str(path)], check=True, capture_output=True)
            if path.suffix in {".md", ".json", ".yaml", ".py", ".sh", ".mjs"}:
                text = path.read_text()
                check(not re.search(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----|\bAIza[\w-]{30,}", text),
                      f"Possível credencial em {path.relative_to(folder)}; valor oculto")
                check("sofia-conteudo" not in text and "carregar_conteudo" not in text,
                      f"Conector ausente em {path.relative_to(folder)}")
            if path.suffix == ".md":
                for href in re.findall(r"\]\(([^)]+)\)", path.read_text()):
                    target = href.split("#", 1)[0]
                    if not target or ":" in target:
                        continue
                    dest = (path.parent / target).resolve()
                    check(dest.is_relative_to(folder.resolve()) and dest.exists(),
                          f"Referência ausente ou externa: {path.relative_to(folder)} -> {target}")
        for path in sorted((folder / "skills").glob("*/SKILL.md")):
            text = path.read_text()
            check(text.startswith("---\n"), "Habilidade sem cabeçalho YAML")
            front = yaml.safe_load(text.split("---", 2)[1])
            check(front["name"] == path.parent.name and front["name"] not in skills, "Nome de habilidade inválido")
            check(isinstance(front["description"], str) and bool(front["description"].strip()), "Descrição ausente")
            check(path.stat().st_size <= 1024 * 1024, "Habilidade maior que 1 MiB")
            skills.append(front["name"])
            ui = path.parent / "agents/openai.yaml"
            check(ui.exists(), "Metadados de habilidade ausentes")
            if ui.exists():
                metadata = yaml.safe_load(ui.read_text())
                check(isinstance(metadata, dict) and isinstance(metadata.get("interface"), dict),
                      "Metadados de habilidade inválidos")
                check("$" + front["name"] in metadata["interface"]["default_prompt"], "Sugestão de habilidade incorreta")
        check(bool(skills), "Pacote sem habilidade utilizável")
    except (KeyError, ValueError, OSError, TypeError, yaml.YAMLError, jsonschema.ValidationError,
            subprocess.CalledProcessError) as error:
        errors.append(str(error)[:600])
    return {"plugin": folder.name, "errors": errors, "missing_listing_fields": gaps, "skills": skills,
            "structure_valid": not errors, "submission_metadata_complete": not errors and not gaps}


def validate_complete(folder: Path) -> dict:
    """Checagens da Sofia completa: as mesmas de estrutura, sem as regras do diretório público."""
    errors: list[str] = []
    skills: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    try:
        claude = json.loads((folder / ".claude-plugin/plugin.json").read_text())
        codex = json.loads((folder / ".codex-plugin/plugin.json").read_text())
        check(claude["name"] == folder.name and codex["name"] == folder.name, "Identidade diferente da pasta")
        check(bool(re.fullmatch(r"\d+\.\d+\.\d+", claude["version"])), "Versão semântica inválida")
        check(codex["version"] == claude["version"], "Versões diferentes entre Claude e Codex")
        check(claude.get("displayName") == codex["interface"]["displayName"] == "Sofia Estrategista",
              "Nome público diferente de Sofia Estrategista")
        check(codex.get("skills") == "./skills/", "Pasta de habilidades Codex inválida")
        servers = json.loads((folder / ".mcp.json").read_text())["mcpServers"]
        check(bool(servers) and all(s.get("url", "").startswith("https://") for s in servers.values()),
              "Conector precisa ser https")
        check((folder / "README.md").exists() and (folder / "LICENSE").exists(), "README ou LICENSE ausente")
        for path in folder.rglob("*"):
            rel = path.relative_to(folder)
            check(not path.is_symlink(), f"Link simbólico: {rel}")
            check(path.name not in {"node_modules", ".env", ".DS_Store", "__pycache__"}, f"Arquivo indevido: {rel}")
            check(bool(PATH_CHARS.fullmatch(str(rel))), f"Caminho que o envio recusa: {rel}")
            if not path.is_file():
                continue
            if path.suffix == ".json":
                json.loads(path.read_text())
            if path.suffix in {".yaml", ".yml"}:
                yaml.safe_load(path.read_text())
            if path.suffix == ".py":
                ast.parse(path.read_text(), filename=str(path))
            if path.suffix in {".md", ".json", ".yaml", ".py", ".sh", ".mjs", ".ts", ".tsx"}:
                text = path.read_text(errors="replace")
                check(not re.search(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----|\bAIza[\w-]{30,}|\bsk-[A-Za-z0-9]{20,}"
                                    r"|\bghp_[A-Za-z0-9]{30,}", text),
                      f"Possível credencial em {rel}; valor oculto")
        for path in sorted((folder / "skills").glob("*/SKILL.md")):
            text = path.read_text()
            check(text.startswith("---\n"), "Habilidade sem cabeçalho YAML")
            front = yaml.safe_load(text.split("---", 2)[1])
            check(front["name"] == path.parent.name and front["name"] not in skills, "Nome de habilidade inválido")
            check(isinstance(front["description"], str) and bool(front["description"].strip()), "Descrição ausente")
            skills.append(front["name"])
        check(bool(skills), "Pacote sem habilidade utilizável")
    except (KeyError, ValueError, OSError, TypeError, yaml.YAMLError) as error:
        errors.append(str(error)[:600])
    return {"plugin": folder.name, "errors": errors, "missing_listing_fields": [], "skills": skills,
            "structure_valid": not errors, "submission_metadata_complete": False}


def validate_all(root: Path = ROOT) -> list[dict]:
    reports = [(validate_complete if name in COMPLETE else validate_plugin)(root / "plugins" / name)
               for name in ALL_NAMES]
    claude = json.loads((root / ".claude-plugin/marketplace.json").read_text())
    codex = json.loads((root / ".agents/plugins/marketplace.json").read_text())
    if [p["name"] for p in claude["plugins"]] != list(ALL_NAMES) or [p["name"] for p in codex["plugins"]] != list(ALL_NAMES):
        raise ValueError("Catálogos não contêm as identidades esperadas (três públicas e a completa)")
    for entry, other in zip(claude["plugins"], codex["plugins"]):
        folder = root / "plugins" / entry["name"]
        if entry["name"] in COMPLETE:
            manifest = json.loads((folder / ".claude-plugin/plugin.json").read_text())
        else:
            manifest = listing(entry["name"])
        if any(entry[key] != manifest[key] for key in ("version", "description", "author")):
            raise ValueError("Catálogo Claude divergente")
        if (root / other["source"]["path"]).resolve() != folder.resolve():
            raise ValueError("Caminho do catálogo Codex inválido")
    return reports


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--submission", action="store_true", help="Falha também se faltarem campos da listagem")
    parser.add_argument("--fix", action="store_true", help="Aplica as correções seguras antes de validar")
    args = parser.parse_args()
    if args.fix:
        for name in NAMES + INTERNAL:  # a completa é cópia da origem: corrige-se lá
            for change in autofix(ROOT / "plugins" / name):
                print(f"[{name}] corrigido: {change}")
    reports = validate_all()
    print(json.dumps(reports, ensure_ascii=False, indent=2))
    raise SystemExit(any(r["errors"] or (args.submission and r["missing_listing_fields"]) for r in reports))
