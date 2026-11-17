#!/usr/bin/env python3
"""A midiateca: UMA pasta de mídia para todos os projetos, consultada antes de baixar.

    python3 midiateca.py buscar "z fold vinco" [--tipo videos] [--json]
    python3 midiateca.py baixar URL [--tags a,b] [--projeto PASTA] [--titulo T --autor A --data D --licenca L]
    python3 midiateca.py importar ARQUIVO [--url U --titulo T --autor A --data D --licenca L --tags a,b]
    python3 midiateca.py migrar PROJETO [--sim]        # sem --sim só mostra o que faria
    python3 midiateca.py resolver midia:videos/x.mp4

Pedido do dono, 2026-09-15: *"ao invés de em cada projeto montar pastas
gigantescas com áudios, vídeos, imagens, monte uma biblioteca … e consulte e
alimente ela, porque alguns recursos podem ser usados em vários outros projetos,
assim economiza tempo, espaço e dinheiro."*

Medido antes: `edicao/acervo/` tinha 262 MB no 14, 263 MB no 15 e 682 MB no 16,
e o 16 ainda guardava 49 MB de transcrição do material de terceiros. O anúncio da
Apple, o Galaxy Fold, as ilustrações do Pexels servem a qualquer vídeo sobre o
mesmo assunto — e cada projeto baixava, transcrevia e olhava tudo de novo.

Como funciona:

- **Onde:** a pasta `midia` do `~/.config/beditor/config.json` (o setup cria;
  padrão `bEditor/Biblioteca/Midia`), com `videos/`, `imagens/`, `audios/`,
  `transcricoes/` e UM `catalogo.json`.
- **Chave por conteúdo:** `oficina.identidade()`. O mesmo arquivo baixado em dois
  projetos com nomes diferentes (`trailer2.mp4`, `hquqycKEpgM.mp4`) vira UM item.
  A URL também é chave: baixar de novo uma URL catalogada devolve o arquivo que
  já existe, sem rede.
- **Referência no projeto:** `"arq": "midia:videos/<nome>"`. O render resolve pela
  configuração; o projeto não carrega cópia. Copiar a pasta `midia` para outro
  disco leva catálogo e transcrições juntos.
- **Procedência viaja no catálogo:** url, título, autor, data, licença e em quais
  projetos o item entrou. O `provas.json` do projeto continua sendo o crédito do
  vídeo; o catálogo é o que permite reusar sem pesquisar a fonte de novo.
- **Busca:** título, descrição, tags, autor, projetos e a TRANSCRIÇÃO. Achar «vinco»
  dentro da fala de um vídeo já baixado custa um grep, não um download.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oficina  # noqa: E402

PREFIXO = "midia:"
VIDEO = {".mp4", ".mov", ".webm", ".mkv", ".m4v"}
IMAGEM = {".png", ".webp", ".jpg", ".jpeg", ".gif"}
AUDIO = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}
PULAR = {".json", ".DS_Store", ".part", ".ytdl"}


# ------------------------------------------------------------------ catálogo
def raiz(obrigatoria=True):
    return oficina.pasta("midia", obrigatoria=obrigatoria)


def carregar(r):
    p = r / "catalogo.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"versao": 1, "itens": {}}


def salvar(r, cat):
    tmp = r / "catalogo.json.tmp"
    tmp.write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(r / "catalogo.json")


def tipo_de(p):
    p = Path(p)
    if p.is_dir():
        return "imagens"          # pasta de PNG (pop-ups de manchete, comentários)
    suf = p.suffix.lower()
    if suf in VIDEO:
        return "videos"
    if suf in IMAGEM:
        return "imagens"
    if suf in AUDIO:
        return "audios"
    return None


def slug(s, n=48):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s[:n].strip("-") or "item"


def resolver(arq, r=None):
    """`midia:videos/x.mp4` → caminho absoluto. Qualquer outra coisa volta como veio."""
    s = str(arq)
    if not s.startswith(PREFIXO):
        return Path(s)
    return (r or raiz()) / s[len(PREFIXO):]


def por_url(cat, url):
    for k, it in cat["itens"].items():
        if url and it.get("url") == url:
            return k, it
    return None, None


# ------------------------------------------------------------------ entrada
def _guardar(r, cat, origem, meta, mover):
    """Põe `origem` na midiateca (movendo ou copiando) e cataloga. Devolve (chave, item, novo)."""
    origem = Path(origem)
    tipo = tipo_de(origem)
    if not tipo:
        raise ValueError(f"tipo não reconhecido: {origem.name}")
    ident = oficina.identidade(origem)
    if ident in cat["itens"]:
        it = cat["itens"][ident]
        for campo in ("url", "titulo", "autor", "data", "licenca"):
            if meta.get(campo) and not it.get(campo):
                it[campo] = meta[campo]
        it["tags"] = sorted(set(it.get("tags", [])) | set(meta.get("tags", [])))
        return ident, it, False
    nome = f"{slug(meta.get('titulo') or origem.stem)}-{ident[:8]}{'' if origem.is_dir() else origem.suffix.lower()}"
    destino = r / tipo / nome
    destino.parent.mkdir(parents=True, exist_ok=True)
    (shutil.move if mover else (shutil.copytree if origem.is_dir() else shutil.copy2))(str(origem), str(destino))
    it = {"arq": f"{tipo}/{nome}", "tipo": tipo, "entrou": date.today().isoformat(),
          "projetos": [], "tags": sorted(set(meta.get("tags", [])))}
    for campo in ("url", "titulo", "autor", "data", "licenca", "descricao", "fontePrevia"):
        if meta.get(campo):
            it[campo] = meta[campo]
    if tipo == "videos":
        try:
            s = oficina.sonda(destino)
            it.update(dur=round(s["dur"], 2), w=s["w"], h=s["h"], fps=round(s["fps"], 2))
        except Exception:        # noqa: BLE001 — sem sonda o item ainda serve
            pass
    cat["itens"][ident] = it
    return ident, it, True


def meta_do_info(info_json):
    """Campos de procedência a partir do `.info.json` do yt-dlp."""
    j = json.loads(Path(info_json).read_text(encoding="utf-8"))
    d = j.get("upload_date") or ""
    return {"url": j.get("webpage_url"), "titulo": j.get("title"), "autor": j.get("channel") or j.get("uploader"),
            "data": f"{d[:4]}-{d[4:6]}-{d[6:]}" if len(d) == 8 else None,
            "descricao": (j.get("description") or "")[:600], "tags": [t.lower() for t in (j.get("tags") or [])[:12]]}


def baixar(url, meta=None, r=None):
    """Baixa UMA vez por URL. Se a URL já está no catálogo, não toca a rede."""
    r = r or raiz()
    cat = carregar(r)
    k, it = por_url(cat, url)
    if it:
        return k, it, False
    tmp = r / ".baixando"
    tmp.mkdir(parents=True, exist_ok=True)
    subprocess.run(["yt-dlp", "--no-playlist", "--write-info-json", "-f", "bv*[height<=1080]+ba/b[height<=1080]/b",
                    "--merge-output-format", "mp4", "-o", str(tmp / "%(id)s.%(ext)s"), url], check=True)
    infos = sorted(tmp.glob("*.info.json"), key=lambda p: p.stat().st_mtime)
    if not infos:
        raise SystemExit(f"!! yt-dlp não escreveu info.json para {url}")
    info = infos[-1]
    base = info.name[: -len(".info.json")]
    arquivo = next(p for p in tmp.iterdir() if p.name.startswith(base + ".") and p.suffix.lower() not in PULAR)
    m = {**meta_do_info(info), **{k: v for k, v in (meta or {}).items() if v}}
    m["url"] = url
    k, it, novo = _guardar(r, cat, arquivo, m, mover=True)
    info.unlink(missing_ok=True)
    salvar(r, cat)
    return k, it, novo


def usar(r, cat, chave, projeto):
    it = cat["itens"][chave]
    nome = Path(projeto).name
    if nome not in it["projetos"]:
        it["projetos"].append(nome)


# ------------------------------------------------------------------ busca
def _sem_acento(s):
    return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()


def buscar(texto, tipo=None, r=None):
    """Itens em que TODAS as palavras aparecem em título, descrição, tags, autor, projetos ou fala."""
    r = r or raiz()
    cat = carregar(r)
    termos = _sem_acento(texto).split()
    achados = []
    for k, it in cat["itens"].items():
        if tipo and it["tipo"] != tipo:
            continue
        campos = " ".join([it.get("titulo", ""), it.get("descricao", ""), it.get("autor", ""),
                           " ".join(it.get("tags", [])), " ".join(it.get("projetos", [])),
                           " ".join(u.get("porque", "") for u in it.get("usos", []))])
        fala, trechos = "", []
        for u in it.get("usos", []):
            if any(t in _sem_acento(u.get("porque")) for t in termos):
                trechos.append((u.get("src") or 0, f"[usado em {u['projeto']} {u['momento']}] {u['porque'][:140]}"))
        tr = it.get("transcricao")
        if tr and (r / tr).exists():
            segs = json.loads((r / tr).read_text(encoding="utf-8")).get("segments", [])
            fala = " ".join(s.get("text", "") for s in segs)
            for s in segs:
                if any(t in _sem_acento(s.get("text")) for t in termos):
                    trechos.append((round(s.get("start", 0), 1), s.get("text", "").strip()))
        tudo = _sem_acento(campos + " " + fala)
        if all(t in tudo for t in termos):
            achados.append({"chave": k, **it, "ref": PREFIXO + it["arq"], "trechos": trechos[:5]})
    return achados


# ------------------------------------------------------------------ migração
def migrar(projeto, sim=False, r=None):
    """Leva `edicao/acervo/` e `oficina/transcricao-acervo/` do projeto para a midiateca.

    Troca, em todo JSON do projeto (menos `oficina/`), o caminho antigo pela
    referência `midia:`. Arquivo que já está na midiateca com o mesmo conteúdo
    não é copiado de novo: a cópia do projeto sai.
    """
    r = r or raiz()
    P = Path(projeto).resolve()
    acervo = P / "edicao" / "acervo"
    cat = carregar(r)
    jsons = [p for p in P.rglob("*.json") if "oficina" not in p.parts and "acervo" not in p.parts]
    refs_fontes, usos = {}, {}
    for j in jsons:
        try:
            dado = json.loads(j.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(dado, dict):
            continue
        chave_de = {}
        for grupo in ("fontes", "musicas"):
            for nome_f, f in (dado.get(grupo) or {}).items():
                if isinstance(f, dict) and f.get("arq"):
                    refs_fontes[Path(f["arq"]).name] = f
                    chave_de[nome_f] = Path(f["arq"]).name
        # o USO de cada fonte no plano: o segundo exato e o porquê — é isso que
        # outro vídeo sobre o mesmo assunto reaproveita sem reassistir a fonte
        for momento, cartoes in (dado.get("plano") or {}).items():
            for c in cartoes if isinstance(cartoes, list) else []:
                nome_arq = chave_de.get(c.get("fonte")) if isinstance(c, dict) else None
                if nome_arq:
                    usos.setdefault(nome_arq, []).append(
                        {"projeto": P.name, "momento": momento, "src": c.get("src"), "dur": c.get("dur"),
                         "porque": c.get("porque", "")})
    relatorio, trocas = [], {}
    if acervo.exists():
        for p in sorted(acervo.iterdir()):
            if p.name.startswith(".") or p.suffix in PULAR or not tipo_de(p):
                continue
            info = p.with_suffix(".info.json")
            meta = meta_do_info(info) if info.exists() else {}
            f = refs_fontes.get(p.name, {})
            for campo in ("url", "titulo", "autor", "data"):
                if f.get(campo):
                    meta[campo] = f[campo]
            if f.get("tipo"):
                meta["tags"] = sorted(set(meta.get("tags", [])) | {f["tipo"]})
            if "pexels" in (meta.get("url") or ""):
                meta["licenca"] = "Pexels"
            ident = oficina.identidade(p)
            ja = ident in cat["itens"]
            tam = sum(x.stat().st_size for x in p.rglob("*") if x.is_file()) if p.is_dir() else p.stat().st_size
            relatorio.append((p.name, tam, "já na midiateca" if ja else "entra"))
            if sim:
                k, it, novo = _guardar(r, cat, p, meta, mover=True)
                if not novo:
                    shutil.rmtree(p) if p.is_dir() else p.unlink()
                info.unlink(missing_ok=True)
                usar(r, cat, k, P)
                vistos = {(u["projeto"], u["momento"], u["src"]) for u in it.get("usos", [])}
                it["usos"] = it.get("usos", []) + [u for u in usos.get(p.name, [])
                                                   if (u["projeto"], u["momento"], u["src"]) not in vistos]
                trocas[p.name] = PREFIXO + it["arq"]
                # transcrição do material de terceiro: guarda UMA vez, por conteúdo
                stem = p.stem
                tr = P / "edicao" / "oficina" / "transcricao-acervo" / f"{stem}.whisper.json"
                if tr.exists() and not it.get("transcricao"):
                    dest = r / "transcricoes" / f"{k}.whisper.json"
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(tr), str(dest))
                    it["transcricao"] = f"transcricoes/{k}.whisper.json"
    if sim:
        # fontes que JÁ apontam para a midiateca (projeto migrado antes, ou item reusado):
        # registra o uso deste projeto no item, para a busca achar pelo porquê
        por_nome = {Path(it["arq"]).name: k for k, it in cat["itens"].items()}
        mudou = False
        for nome_arq, lista in usos.items():
            k = por_nome.get(nome_arq)
            if not k or nome_arq in trocas:
                continue
            it = cat["itens"][k]
            vistos = {(u["projeto"], u["momento"], u["src"]) for u in it.get("usos", [])}
            novos = [u for u in lista if (u["projeto"], u["momento"], u["src"]) not in vistos]
            if novos:
                it["usos"] = it.get("usos", []) + novos
                usar(r, cat, k, P)
                mudou = True
        if mudou and not trocas:
            salvar(r, cat)
    if sim and trocas:
        for j in jsons:
            txt = j.read_text(encoding="utf-8")
            novo = txt
            for nome, ref in trocas.items():
                novo = re.sub(r'"(?:[^"]*/)?acervo/' + re.escape(nome) + '"', f'"{ref}"', novo)
            if novo != txt:
                j.write_text(novo, encoding="utf-8")
        salvar(r, cat)
        if acervo.exists() and not any(x for x in acervo.iterdir() if x.name != ".DS_Store"):
            shutil.rmtree(acervo)
    return relatorio


# ------------------------------------------------------------------ CLI
def main(argv=None):
    ap = argparse.ArgumentParser(description="midiateca: mídia compartilhada entre projetos")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("buscar")
    b.add_argument("texto")
    b.add_argument("--tipo", choices=["videos", "imagens", "audios"])
    b.add_argument("--json", action="store_true")
    d = sub.add_parser("baixar")
    d.add_argument("url")
    i = sub.add_parser("importar")
    i.add_argument("arquivo")
    i.add_argument("--url")
    i.add_argument("--mover", action="store_true")
    for x in (d, i):
        for campo in ("titulo", "autor", "data", "licenca", "tags", "projeto"):
            x.add_argument(f"--{campo}")
    m = sub.add_parser("migrar")
    m.add_argument("projeto")
    m.add_argument("--sim", action="store_true", help="executa (sem isto, só mostra)")
    rs = sub.add_parser("resolver")
    rs.add_argument("ref")
    a = ap.parse_args(argv)

    if a.cmd == "resolver":
        print(resolver(a.ref))
        return
    r = raiz()
    if a.cmd == "buscar":
        achados = buscar(a.texto, a.tipo, r)
        if a.json:
            print(json.dumps(achados, ensure_ascii=False, indent=1))
            return
        for it in achados:
            print(f"{it['ref']}  ·  {it.get('titulo', '')}  ·  {it.get('autor', '')}  ·  {it.get('dur', '')} s  ·  "
                  f"usado em {', '.join(it['projetos']) or '—'}")
            for t, txt in it["trechos"]:
                print(f"    {t:7.1f}s  {txt}")
        print(f"{len(achados)} item(ns)")
        return
    meta = {k: getattr(a, k) for k in ("titulo", "autor", "data", "licenca") if getattr(a, k, None)}
    meta["tags"] = [t.strip().lower() for t in (getattr(a, "tags", None) or "").split(",") if t.strip()]
    if a.cmd == "baixar":
        k, it, novo = baixar(a.url, meta, r)
    elif a.cmd == "importar":
        cat = carregar(r)
        if a.url:
            meta["url"] = a.url
        k, it, novo = _guardar(r, cat, a.arquivo, meta, mover=a.mover)
        salvar(r, cat)
    if a.cmd in ("baixar", "importar"):
        if a.projeto:
            cat = carregar(r)
            usar(r, cat, k, a.projeto)
            salvar(r, cat)
        print(f"{'novo' if novo else 'já estava'}: {PREFIXO}{it['arq']}")
        return
    if a.cmd == "migrar":
        rel = migrar(a.projeto, sim=a.sim, r=r)
        total = sum(t for _, t, _ in rel)
        for nome, t, estado in rel:
            print(f"  {t/1e6:8.1f} MB  {estado:16}  {nome}")
        print(f"{len(rel)} item(ns), {total/1e6:.0f} MB{'' if a.sim else '  (simulação — rode com --sim)'}")


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
