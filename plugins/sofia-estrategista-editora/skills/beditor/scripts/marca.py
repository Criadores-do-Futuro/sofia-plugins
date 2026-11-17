#!/usr/bin/env python3
"""As marcas de quem usa o plugin — uma por canal ou cliente, nunca dentro do plugin.

    python3 marca.py listar
    python3 marca.py nova <nome> [--manual guia.md] [--motion escolhas.md] [--padrao]
    python3 marca.py usar <nome> [--projeto <pasta>]     # sem --projeto: a padrão da máquina
    python3 marca.py mostrar [--projeto <pasta>] [--json]

Por que não viaja com o plugin: marca é de uma pessoa, e uma pessoa pode ter
vários clientes, cada um com a sua. O plugin traz só o estilo da casa (a
galeria em `estilos.py`); identidade, paleta, fonte, logotipo e as escolhas de
motion de cada canal ficam na máquina de quem edita.

Onde ficam: a pasta `marcas` do config (`setup.py --pastas marcas=<caminho>`),
ou `~/.beditor/marcas` se não houver. Uma subpasta por marca:

    <marcas>/<nome>/
      marca.json   nome, arroba, site, cores, fontes, estilos padrão (hook, legenda, motion…)
      manual.md    a identidade verbal e visual, para gente e para o diretor lerem
      motion.md    as escolhas de motion do canal (o que `/sofia-estrategista-editora:branding` escreve)
      logos/  fontes/

Qual marca vale, nesta ordem: `BEDITOR_MARCA`; a `marca` do projeto
(`projeto.json`, ou `edicao/dados.json`, ou `guia/guia.json`); a `marcaPadrao`
do config. Nenhuma → o estilo da casa, sem inventar identidade.
"""
import argparse
import json
import os
import re
import shutil
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oficina  # noqa: E402

MARCA_VAZIA = {
    "nome": "", "arroba": "", "site": "",
    # cores em hex; o que faltar cai no estilo da casa
    "cores": {"fundo": "", "texto": "", "destaque": "", "sombra": ""},
    # arquivo em <marca>/fontes/ ou nome de família instalada
    "fontes": {"display": "", "texto": ""},
    # id da galeria de `estilos.py` por elemento: hook, legenda, motion, musica, sfx
    "estilos": {},
}


def slug(nome):
    s = unicodedata.normalize("NFD", nome.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "marca"


def raiz(cfg=None):
    cfg = cfg or oficina.config()
    bruto = cfg["pastas"].get("marcas")
    return Path(os.path.expanduser(bruto)) if bruto else Path.home() / ".beditor" / "marcas"


def listar(cfg=None):
    r = raiz(cfg)
    return sorted(p.name for p in r.iterdir() if (p / "marca.json").is_file()) if r.is_dir() else []


def _marca_do_projeto(projeto):
    if not projeto:
        return None
    p = Path(projeto)
    for rel in ("projeto.json", "edicao/dados.json", "guia/guia.json"):
        arq = p / rel
        if arq.is_file():
            try:
                nome = json.loads(arq.read_text(encoding="utf-8")).get("marca")
            except (json.JSONDecodeError, AttributeError):
                continue
            if nome:
                return nome
    return None


class Marca:
    def __init__(self, pasta):
        self.pasta = Path(pasta)
        self.nome = self.pasta.name
        dados = json.loads((self.pasta / "marca.json").read_text(encoding="utf-8"))
        self.dados = {**MARCA_VAZIA, **dados}
        self.manual = self.pasta / "manual.md"
        self.motion = self.pasta / "motion.md"

    def cor(self, chave, padrao):
        """(r, g, b) da marca, ou `padrao`."""
        h = (self.dados.get("cores") or {}).get(chave) or ""
        h = h.lstrip("#")
        if len(h) != 6:
            return padrao
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    def fonte(self, papel):
        """Caminho do arquivo de fonte da marca para `papel` (display, texto), ou None."""
        f = (self.dados.get("fontes") or {}).get(papel)
        if not f:
            return None
        for c in (self.pasta / "fontes" / f, Path(os.path.expanduser(f))):
            if c.is_file():
                return c
        return None

    def estilo(self, elemento):
        return (self.dados.get("estilos") or {}).get(elemento)

    def resumo(self):
        return {"nome": self.nome, "pasta": str(self.pasta),
                "manual": str(self.manual) if self.manual.is_file() else None,
                "motion": str(self.motion) if self.motion.is_file() else None,
                "marca": self.dados}


def resolver(projeto=None, nome=None, cfg=None):
    """A marca que vale agora, ou None. Pedida e inexistente é erro, não silêncio."""
    cfg = cfg or oficina.config()
    escolhida = (nome or os.environ.get("BEDITOR_MARCA") or _marca_do_projeto(projeto)
                 or cfg.get("marcaPadrao"))
    if not escolhida:
        return None
    pasta = raiz(cfg) / escolhida
    if not (pasta / "marca.json").is_file():
        existentes = ", ".join(listar(cfg)) or "nenhuma"
        raise SystemExit(f"!! marca «{escolhida}» não existe em {raiz(cfg)} (existem: {existentes}).\n"
                         f"Crie com `marca.py nova {escolhida}` ou escolha outra com `marca.py usar`.")
    return Marca(pasta)


def nova(nome, manual=None, motion=None, padrao=False, cfg=None):
    cfg = cfg or oficina.config()
    pasta = raiz(cfg) / slug(nome)
    if (pasta / "marca.json").exists():
        raise SystemExit(f"!! a marca «{pasta.name}» já existe em {pasta}")
    for sub in ("logos", "fontes"):
        (pasta / sub).mkdir(parents=True, exist_ok=True)
    dados = json.loads(json.dumps(MARCA_VAZIA))
    dados["nome"] = nome
    (pasta / "marca.json").write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n",
                                      encoding="utf-8")
    for origem, destino in ((manual, "manual.md"), (motion, "motion.md")):
        if origem:
            shutil.copyfile(origem, pasta / destino)
    if padrao:
        usar(pasta.name, cfg=cfg)
    return pasta


def usar(nome, projeto=None, cfg=None):
    """Grava a escolha: no projeto (`projeto.json`) ou como padrão da máquina."""
    cfg = cfg or oficina.config()
    if not (raiz(cfg) / nome / "marca.json").is_file():
        raise SystemExit(f"!! marca «{nome}» não existe em {raiz(cfg)}")
    if projeto:
        arq = Path(projeto) / "projeto.json"
        d = json.loads(arq.read_text(encoding="utf-8")) if arq.is_file() else {}
        d["marca"] = nome
        arq.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return arq
    arquivo = Path(cfg["_arquivo"])
    bruto = json.loads(arquivo.read_text(encoding="utf-8")) if arquivo.is_file() else {"versao": 1}
    bruto["marcaPadrao"] = nome
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(json.dumps(bruto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return arquivo


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("listar")
    n = sub.add_parser("nova")
    n.add_argument("nome")
    n.add_argument("--manual")
    n.add_argument("--motion")
    n.add_argument("--padrao", action="store_true")
    u = sub.add_parser("usar")
    u.add_argument("nome")
    u.add_argument("--projeto")
    m = sub.add_parser("mostrar")
    m.add_argument("--projeto")
    m.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.cmd == "listar":
        cfg = oficina.config()
        nomes = listar(cfg)
        print(f"{raiz(cfg)}: " + (", ".join(nomes) if nomes else "nenhuma marca"))
        if cfg.get("marcaPadrao"):
            print(f"padrão: {cfg['marcaPadrao']}")
    elif a.cmd == "nova":
        print(f"marca criada: {nova(a.nome, a.manual, a.motion, a.padrao)}")
    elif a.cmd == "usar":
        print(f"gravado em {usar(a.nome, a.projeto)}")
    else:
        mc = resolver(a.projeto)
        if a.json:
            print(json.dumps(mc.resumo() if mc else None, ensure_ascii=False, indent=2))
        elif not mc:
            print("nenhuma marca escolhida: vale o estilo da casa")
        else:
            r = mc.resumo()
            print(f"marca: {r['nome']} ({r['pasta']})")
            print(f"manual: {r['manual'] or '—'}")
            print(f"motion: {r['motion'] or '—'}")


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
