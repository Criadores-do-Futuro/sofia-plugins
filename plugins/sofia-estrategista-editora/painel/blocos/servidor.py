#!/usr/bin/env python3
"""
Editor de blocos do bEditor: mostra o plugin como blocos ligados (comandos,
agentes, skills, scripts, referências, template) e edita os arquivos de verdade.

Uso: python3 painel/blocos/servidor.py [--porta 4747] [--sem-navegador]

Só biblioteca padrão. Lê e grava apenas dentro do repositório, e só nos tipos de
arquivo que o plugin usa. Nada sai da máquina: o servidor escuta em 127.0.0.1.
"""
import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

RAIZ = Path(__file__).resolve().parents[2]
PAGINA = Path(__file__).with_name("blocos.html")
EXTENSOES = {".md", ".py", ".sh", ".swift", ".ts", ".tsx", ".json", ".yaml", ".yml", ".css", ".txt"}
IGNORAR = ("node_modules", "__pycache__", ".git", "treinamento", "docs/superpowers")

# ordem do fluxo: o que o editor roda, etapa por etapa
ETAPAS = {
    "dirigir": (0, "Dirigir"), "cortar": (1, "Cortar"), "motion-graficos": (2, "Motion"),
    "finalizar": (3, "Finalizar"), "publicar": (4, "Publicar"),
}


def rel(p):
    return p.relative_to(RAIZ).as_posix()


def ignorado(p):
    s = rel(p)
    return any(f"/{i}/" in f"/{s}/" or s.startswith(i) for i in IGNORAR)


def frontmatter(texto):
    """(campos escalares, corpo, linha onde o corpo começa)"""
    if not texto.startswith("---\n"):
        return {}, texto, 0
    fim = texto.find("\n---", 4)
    if fim < 0:
        return {}, texto, 0
    campos = {}
    for linha in texto[4:fim].splitlines():
        m = re.match(r"^([\w-]+):\s*(.*)$", linha)
        if m and m.group(2) and not m.group(2).startswith("#"):
            campos[m.group(1)] = m.group(2).split("  #")[0].strip()
    corpo = texto[fim + 4:].lstrip("\n")
    return campos, corpo, texto[: fim + 4].count("\n") + 1


def resumo_codigo(texto):
    m = re.search(r'^(?:#!.*\n)?(?:#.*\n)*\s*(?:"""|\'\'\')(.+?)(?:"""|\'\'\')', texto, re.S)
    if m:
        return " ".join(m.group(1).split())[:260]
    linhas = [l.lstrip("#/ ").strip() for l in texto.splitlines()[:12] if l.startswith(("#", "//")) and not l.startswith("#!")]
    return " ".join(linhas)[:260]


def tipo_de(caminho):
    if caminho == ".claude-plugin/plugin.json":
        return "plugin"
    if caminho.startswith("commands/"):
        return "comando"
    if caminho.startswith("agents/"):
        return "agente"
    if caminho.endswith("/SKILL.md"):
        return "skill"
    if "/referencias/" in caminho or caminho.endswith(("IDENTIDADE.md", "INSTALAR.md")):
        return "referencia"
    if "/scripts/" in caminho or "/lib/" in caminho or caminho.endswith("verificar.py"):
        return "script"
    if "/template/" in caminho:
        return "template"
    if caminho.startswith("painel/"):
        return "painel"
    if "/tests/" in caminho:
        return "teste"
    return "outro"


def passos(corpo, inicio):
    """Os passos numerados de um comando — cada um vira um bloco do fluxo."""
    linhas = corpo.splitlines()
    saida, atual = [], None
    for i, l in enumerate(linhas):
        m = re.match(r"^(\d+[a-z]?)\.\s+(.*)", l)
        if m:
            if atual:
                saida.append(atual)
            atual = {"n": m.group(1), "de": i, "ate": i, "texto": l}
        elif atual and (l.startswith((" ", "\t")) or (l == "" and i + 1 < len(linhas) and linhas[i + 1].startswith((" ", "\t")))):
            atual["ate"] = i
            atual["texto"] += "\n" + l
        elif atual and l.strip():
            saida.append(atual)
            atual = None
    if atual:
        saida.append(atual)
    for p in saida:
        p["linha"] = inicio + p["de"] + 1
    return saida


def git_status():
    try:
        out = subprocess.run(["git", "status", "--porcelain"], cwd=RAIZ, capture_output=True, text=True, timeout=10, encoding="utf-8", errors="replace").stdout
    except Exception:
        return {}
    return {l[3:].strip('"'): l[:2].strip() for l in out.splitlines()}


def grafo():
    arquivos = sorted(p for p in RAIZ.rglob("*") if p.is_file() and p.suffix in EXTENSOES and not ignorado(p))
    status = git_status()
    nos = {}
    for p in arquivos:
        c = rel(p)
        tipo = tipo_de(c)
        if tipo in ("outro", "teste") and c not in ("README.md",):
            continue
        if tipo == "painel" and p.name in ("estado.json", "telemetria.json", "index.html"):
            continue
        texto = p.read_text(encoding="utf-8", errors="replace")
        campos, corpo, inicio = frontmatter(texto) if p.suffix == ".md" else ({}, texto, 0)
        nome = campos.get("name") or (p.parent.name if p.name == "SKILL.md" else p.stem)
        if tipo == "comando":
            nome = "/sofia-estrategista-editora:" + p.stem
        if p.suffix == ".md":
            titulo = re.search(r"^#\s+(.+)$", corpo, re.M)
            desc = campos.get("description") or (titulo.group(1) if titulo else corpo.strip().split("\n")[0])
        else:
            desc = resumo_codigo(texto)
        no = {
            "id": c, "tipo": tipo, "nome": nome, "arquivo": p.name, "descricao": desc[:400],
            "campos": campos, "linhas": texto.count("\n") + 1, "git": status.get(c, ""),
            "grupo": c.split("/")[1] if c.startswith("skills/") else c.split("/")[0],
        }
        if tipo == "comando":
            no["etapa"] = ETAPAS.get(p.stem, (None, None))
            no["passos"] = passos(corpo, inicio)
        nos[c] = (no, texto)

    # índices para achar menções
    por_script = {}
    for c, (no, _) in nos.items():
        if no["tipo"] in ("script", "template"):
            por_script.setdefault(Path(c).name, []).append(c)
    refs = {c: c for c, (no, _) in nos.items() if no["tipo"] == "referencia"}
    agentes = {Path(c).stem: c for c, (no, _) in nos.items() if no["tipo"] == "agente"}
    comandos = {Path(c).stem: c for c, (no, _) in nos.items() if no["tipo"] == "comando"}
    skills = {Path(c).parent.name: c for c, (no, _) in nos.items() if no["tipo"] == "skill"}

    arestas, quebradas, externas = set(), [], {}
    for c, (no, texto) in nos.items():
        base = c.split("/referencias/")[0] if "/referencias/" in c else "/".join(c.split("/")[:2])

        def liga(alvo, motivo):
            if alvo and alvo != c:
                arestas.add((c, alvo, motivo))

        for nome in re.findall(r"([\w-]+\.(?:py|sh|swift|tsx?))\b", texto):
            alvos = por_script.get(nome, [])
            liga(next((a for a in alvos if a.startswith(base)), alvos[0] if alvos else None), "roda")
        if c.endswith(".py"):
            for mod in re.findall(r"^\s*(?:from|import)\s+(\w+)", texto, re.M):
                alvos = por_script.get(mod + ".py", [])
                liga(next((a for a in alvos if a.startswith(base)), alvos[0] if alvos else None), "importa")
        if c.endswith((".ts", ".tsx")):
            for mod in re.findall(r"""from\s+['"]\.{1,2}/(?:[\w-]+/)*([\w-]+)['"]""", texto):
                alvos = por_script.get(mod + ".tsx", []) + por_script.get(mod + ".ts", [])
                liga(alvos[0] if alvos else None, "importa")
        for m in re.finditer(r"(?:(skills/[\w-]+)/)?referencias/([\w-]+\.md)", texto):
            dono = m.group(1)
            cands = [r for r in refs if r.endswith("/referencias/" + m.group(2))]
            if dono:
                cands = [r for r in cands if r.startswith(dono)] or cands
            alvo = next((r for r in cands if r.startswith(base)), cands[0] if cands else None)
            if alvo:
                liga(alvo, "consulta")
            elif m.group(2) not in ("x.md",):
                quebradas.append({"de": c, "ref": m.group(0)})
        for nome, alvo in agentes.items():
            if re.search(rf"(?:agente\s+`?|`){re.escape(nome)}`", texto):
                liga(alvo, "despacha")
        for nome, alvo in comandos.items():
            if f"/sofia-estrategista-editora:{nome}" in texto:
                liga(alvo, "chama")
        for nome, alvo in skills.items():
            if nome != Path(c).parent.name and re.search(rf"\b{re.escape(nome)}\b", texto) and no["tipo"] in ("comando", "agente", "skill"):
                liga(alvo, "usa skill")
        for m in re.findall(r"`(sofia:[\w-]+|corte-viral|hyperframes(?:-cli)?|notebooklm|claude-design-hyperframes|remotion-to-hyperframes)`?", texto):
            externas.setdefault(m, set()).add(c)

    entrada = {}
    for a, b, _ in arestas:
        entrada[b] = entrada.get(b, 0) + 1
    lista = []
    for c, (no, _) in nos.items():
        no["entradas"] = entrada.get(c, 0)
        lista.append(no)
    return {
        "raiz": str(RAIZ),
        "nos": lista,
        "arestas": [{"de": a, "para": b, "motivo": m} for a, b, m in sorted(arestas)],
        "quebradas": quebradas,
        "externas": {k: sorted(v) for k, v in sorted(externas.items())},
    }


def saude():
    bins = {b: bool(shutil.which(b)) for b in ("python3", "node", "npx", "ffmpeg", "ffprobe", "git", "swiftc", "yt-dlp", "whisper")}
    swift = {n: (Path.home() / ".beditor/bin" / n).exists() for n in ("recorte", "rastrear-rosto")}
    pymods = {}
    for mod, pacote in (("PIL", "Pillow"), ("numpy", "numpy"), ("cv2", "opencv-python"), ("yaml", "PyYAML"),
                        ("faster_whisper", "faster-whisper"), ("huggingface_hub", "huggingface_hub"), ("playwright", "playwright")):
        pymods[pacote] = importlib.util.find_spec(mod) is not None
    env = (Path.home() / ".config/beditor/env").exists()
    return {"binarios": bins, "swift": swift, "python": pymods, "chaveGemini": env}


def seguro(caminho):
    p = (RAIZ / caminho).resolve()
    if RAIZ not in p.parents or p.suffix not in EXTENSOES or ".git" in p.parts:
        raise ValueError("caminho fora do plugin ou tipo não editável")
    return p


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def responder(self, dados, codigo=200, tipo="application/json"):
        corpo = dados if isinstance(dados, bytes) else json.dumps(dados, ensure_ascii=False).encode()
        self.send_response(codigo)
        self.send_header("Content-Type", tipo + "; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self):
        url = urlparse(self.path)
        q = parse_qs(url.query)
        try:
            if url.path == "/":
                return self.responder(PAGINA.read_bytes(), tipo="text/html")
            if url.path == "/api/grafo":
                return self.responder(grafo())
            if url.path == "/api/saude":
                return self.responder(saude())
            if url.path == "/api/arquivo":
                p = seguro(q["caminho"][0])
                return self.responder({"caminho": rel(p), "conteudo": p.read_text(encoding="utf-8", errors="replace")})
            if url.path == "/api/diff":
                p = seguro(q["caminho"][0])
                out = subprocess.run(["git", "diff", "--", rel(p)], cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
                return self.responder({"diff": out})
            self.responder({"erro": "não existe"}, 404)
        except Exception as e:
            self.responder({"erro": str(e)}, 400)

    def do_POST(self):
        url = urlparse(self.path)
        # só aceita chamadas da própria página
        if self.headers.get("X-Blocos") != "1":
            return self.responder({"erro": "origem recusada"}, 403)
        try:
            dados = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            if url.path == "/api/arquivo":
                p = seguro(dados["caminho"])
                if dados.get("novo") and p.exists():
                    raise ValueError("já existe um arquivo com esse nome")
                if not dados.get("novo") and not p.exists():
                    raise ValueError("arquivo não existe")
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(dados["conteudo"], encoding="utf-8")
                return self.responder({"ok": True, "caminho": rel(p)})
            if url.path == "/api/testes":
                r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "skills/beditor/tests"],
                                   cwd=RAIZ, capture_output=True, text=True, timeout=600, encoding="utf-8", errors="replace")
                saida = r.stderr.strip().splitlines()
                falhas = [l for l in saida if l.startswith(("FAIL:", "ERROR:"))]
                return self.responder({"ok": r.returncode == 0, "resumo": "\n".join(saida[-3:]), "falhas": falhas})
            self.responder({"erro": "não existe"}, 404)
        except Exception as e:
            self.responder({"erro": str(e)}, 400)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--porta", type=int, default=4747)
    ap.add_argument("--sem-navegador", action="store_true")
    a = ap.parse_args()
    srv = ThreadingHTTPServer(("127.0.0.1", a.porta), Handler)
    url = f"http://127.0.0.1:{a.porta}/"
    print(f"editor de blocos em {url}  (Ctrl+C para sair)")
    if not a.sem_navegador:
        webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
