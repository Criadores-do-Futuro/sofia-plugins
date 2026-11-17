#!/usr/bin/env python3
"""
Gera o painel do bEditor: o estado de cada formato criativo, critério por
critério, contra o estado desejável.

Uso: python3 painel/gerar.py [--saida painel]

Lê `painel/criterios.yaml`, confere cada evidência no próprio repositório e
escreve `painel/estado.json` e `painel/index.html` (autocontido, abre direto no
navegador). O nível declarado no yaml é teto, não verdade: a célula cai até o
nível que as evidências sustentam, e evidência que sumiu aparece como quebrada.
Assim o painel acompanha o código — apagou o teste, a célula desce sozinha.
"""
import argparse
import fnmatch
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
REGRA = ("skills/beditor/referencias/", "agents/", "commands/", "skills/beditor/SKILL.md")
MAQUINA = ("skills/beditor/scripts/",)
TESTE = ("skills/beditor/tests/",)


def classe(caminho):
    if caminho.startswith("entrega:"):
        return "entrega"
    if caminho.startswith(TESTE):
        return "teste"
    if caminho.startswith(MAQUINA):
        return "maquina"
    if caminho.startswith(REGRA):
        return "regra"
    return "outro"


def conferir(evidencia, raiz=RAIZ, entregas=None):
    """{'texto', 'classe', 'ok', 'motivo'}"""
    tipo = classe(evidencia)
    if tipo == "entrega":
        padrao = evidencia.split(":", 1)[1]
        if not entregas or not Path(entregas).is_dir():
            return {"texto": evidencia, "classe": tipo, "ok": None,
                    "motivo": "pasta de entregas não montada — não conferido"}
        achou = [p.name for p in Path(entregas).rglob("*") if fnmatch.fnmatch(p.name, padrao)]
        return {"texto": evidencia, "classe": tipo, "ok": bool(achou),
                "motivo": achou[0] if achou else "nenhuma entrega com esse nome"}
    caminho, _, trecho = evidencia.partition("#")
    arq = raiz / caminho
    if not arq.exists():
        return {"texto": evidencia, "classe": tipo, "ok": False, "motivo": "arquivo não existe"}
    if trecho and trecho not in arq.read_text(encoding="utf-8", errors="replace"):
        return {"texto": evidencia, "classe": tipo, "ok": False,
                "motivo": "o arquivo não contém mais o trecho"}
    return {"texto": evidencia, "classe": tipo, "ok": True, "motivo": ""}


def provado(conferidas):
    """o maior nível que as evidências sustentam"""
    ok = {c["classe"] for c in conferidas if c["ok"]}
    if not ok:
        return 0
    nivel = 1
    if "regra" in ok:
        nivel = 2
        if {"maquina", "teste"} <= ok:
            nivel = 3
            if "entrega" in ok:
                nivel = 4
    return nivel


def celula(crit, fmt, raiz, entregas):
    base = crit["base"]
    propria = (fmt.get("celulas") or {}).get(crit["id"]) or {}
    herdada = "nivel" not in propria
    fonte = base if herdada else propria
    declarado = int(fonte.get("nivel", 0))
    conferidas = [conferir(e, raiz, entregas) for e in fonte.get("evidencias") or []]
    teto = 4 if fmt.get("reconhecido") or not herdada else 1
    prova = provado(conferidas)
    efetivo = min(declarado, prova, teto)
    motivo = []
    if herdada:
        motivo.append("herdado da base do critério"
                      + ("" if teto == 4 else "; limitado a 1 porque o guia não conhece o formato"))
    if prova < declarado:
        motivo.append(f"declarado {declarado}, as evidências sustentam {prova}")
    return {
        "desejado": propria.get("desejado") or "",
        "declarado": declarado,
        "efetivo": efetivo,
        "herdada": herdada,
        "motivo": "; ".join(motivo),
        "falta": propria.get("falta") or (base.get("falta") if herdada else "") or "",
        "nota": propria.get("nota") or (base.get("nota") if herdada else "") or "",
        "evidencias": conferidas,
    }


# a linha de producao de cada video: o que existe no disco diz em que etapa ele
# esta. Marca em `edicao/aprovado/` e o editor tendo aprovado aquela etapa.
ETAPAS_PROJETO = [
    ("dirigir",   "Dirigir",   ["guia/guia.json"],                      None),
    ("cortar",    "Cortar",    ["edicao/corte.json",
                                "edicao/corte-revisao.mp4"],            "corte"),
    ("motion",    "Motion",    ["edicao/motion/out/motion.mp4"],        "motion"),
    ("finalizar", "Finalizar", ["edicao/out/preview.mp4",
                                "edicao/motion/out/preview.mp4"],       "final"),
    ("publicar",  "Publicar",  ["entrega/publicacao/agendado.json",
                                "entrega/publicacao.json"],             None),
]


def _quando(p):
    return datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec="minutes")


def projeto(pasta, entregas=None):
    # o master aprovado nao mora no projeto: ele vai para a pasta de entregas,
    # com o mesmo nome. Sem olhar la, `finalizar` ficaria vazio num video pronto.
    entregue = []
    if entregas and (Path(entregas) / pasta.name).is_dir():
        entregue = sorted((Path(entregas) / pasta.name).rglob("*.mp4"))
    etapas = {}
    for eid, nome, arquivos, marca in ETAPAS_PROJETO:
        feitos = [pasta / a for a in arquivos if (pasta / a).exists()]
        if eid == "finalizar" and entregue:
            feitos = entregue + feitos
        aprovado = bool(marca) and (pasta / "edicao/aprovado" / marca).exists()
        etapas[eid] = {
            "nome": nome,
            "estado": "aprovado" if aprovado else "feito" if feitos else "vazio",
            "arquivo": feitos[0].name if feitos else "",
            "quando": _quando(feitos[0]) if feitos else "",
        }
    fluxo = any(e["estado"] != "vazio" for e in etapas.values())
    return {"id": pasta.name, "nome": pasta.name, "caminho": str(pasta),
            "etapas": etapas, "noFluxo": fluxo,
            "hyperframes": (pasta / "hyperframes.json").exists()}


def projetos(caminho, entregas=None):
    raiz = Path(caminho).expanduser() if caminho else None
    if not raiz or not raiz.is_dir():
        return []
    return [projeto(p, entregas) for p in sorted(raiz.iterdir())
            if p.is_dir() and not p.name.startswith(("_", "."))]


def git(*args):
    try:
        return subprocess.run(["git", "-C", str(RAIZ), *args], capture_output=True,
                              text=True, check=True, encoding="utf-8", errors="replace").stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def contar_testes(raiz):
    return sum(t.read_text(encoding="utf-8").count("    def test_")
               for t in (raiz / "skills/beditor/tests").glob("test_*.py"))


def pasta_da_maquina(nome, dados):
    """Entregas e projetos são da máquina: vêm do config do setup, não do yaml versionado."""
    if dados.get(nome):
        return dados[nome]
    sys.path.insert(0, str(RAIZ / "skills/beditor/scripts"))
    try:
        import oficina
        bruto = oficina.config()["pastas"].get(nome)
    except (ImportError, OSError, KeyError, ValueError, SystemExit):
        return None
    return str(Path(bruto).expanduser()) if bruto else None


def calcular(dados, raiz=RAIZ):
    entregas = pasta_da_maquina("entregas", dados)
    crits = dados["criterios"]
    formatos = []
    for f in dados["formatos"]:
        cels = {c["id"]: celula(c, f, raiz, entregas) for c in crits}
        soma = sum(c["efetivo"] for c in cels.values())
        formatos.append({
            "id": f["id"], "nome": f["nome"], "automacao": f.get("automacao", ""),
            "reconhecido": bool(f.get("reconhecido")), "resumo": f.get("resumo", ""),
            "celulas": cels, "pct": round(100 * soma / (4 * len(crits))),
        })
    colunas = {c["id"]: round(100 * sum(f["celulas"][c["id"]]["efetivo"] for f in formatos)
                              / (4 * len(formatos))) for c in crits}
    projs = projetos(pasta_da_maquina("projetos", dados), entregas)
    tele_arq = RAIZ / "painel/telemetria.json"
    tele = json.loads(tele_arq.read_text(encoding="utf-8")) if tele_arq.exists() else None
    etapas = []
    for e in dados.get("etapas") or []:
        conf = [conferir(x, raiz, entregas) for x in e.get("evidencias") or []]
        etapas.append({**e, "evidencias": conf,
                       "efetivo": min(int(e.get("nivel", 0)), provado(conf))})
    quebradas = sum(1 for f in formatos for c in f["celulas"].values()
                    for ev in c["evidencias"] if ev["ok"] is False)
    total = sum(f["pct"] for f in formatos) / len(formatos) if formatos else 0
    return {
        "gerado": datetime.now().isoformat(timespec="minutes"),
        "commit": git("rev-parse", "--short", "HEAD"),
        "commitMsg": git("log", "-1", "--pretty=%s"),
        "commitData": git("log", "-1", "--pretty=%cd", "--date=format:%Y-%m-%d %H:%M"),
        "testes": contar_testes(raiz),
        "escala": {int(k): v for k, v in dados["escala"].items()},
        "criterios": [{k: c[k] for k in ("id", "nome", "pergunta")} for c in crits],
        "formatos": formatos,
        "colunas": colunas,
        "etapas": etapas,
        "projetos": projs,
        "telemetria": tele,
        "quebradas": quebradas,
        "total": round(total),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--saida", default=str(RAIZ / "painel"))
    a = ap.parse_args()
    dados = yaml.safe_load((RAIZ / "painel/criterios.yaml").read_text(encoding="utf-8"))
    estado = calcular(dados)
    rev = RAIZ / "painel" / "revisao.json"      # escrito por painel/revisao.py a cada render
    estado["revisao"] = json.loads(rev.read_text(encoding="utf-8")) if rev.exists() else None
    saida = Path(a.saida)
    saida.mkdir(parents=True, exist_ok=True)
    texto = json.dumps(estado, ensure_ascii=False, indent=1)
    (saida / "estado.json").write_text(texto + "\n", encoding="utf-8")
    modelo = (RAIZ / "painel/modelo.html").read_text(encoding="utf-8")
    (saida / "index.html").write_text(
        modelo.replace("/*ESTADO*/null", json.dumps(estado, ensure_ascii=False)),
        encoding="utf-8")
    print(f"painel: {estado['total']}% do desejável · {estado['quebradas']} evidência(s) "
          f"quebrada(s) · {saida / 'index.html'}", file=sys.stderr)


if __name__ == "__main__":
    main()
