#!/usr/bin/env python3
"""
telemetria.py — quanto cada etapa do bEditor custa em tokens e em tempo.

Pedido do dono (2026-09-11): saber qual parte do processo consome mais tokens e
qual demora mais, com o motivo de cada uma.

Nada disso e estimado: os transcripts do Claude Code (`~/.claude/projects/**.jsonl`)
guardam, por mensagem, o `usage` do modelo e o timestamp. Este script varre os
transcripts que mencionam a skill, atribui cada mensagem a uma etapa (a ultima
marca vista: um comando `/sofia-estrategista-editora:*`, um script da skill, um agente) e soma:

- tokens de entrada, de cache criado, de cache lido e de saida;
- tempo de parede (soma dos intervalos entre mensagens, ignorando os maiores que
  `PAUSA_MAX`, que sao o editor fazendo outra coisa);
- quantas chamadas de cada ferramenta e quantas imagens entraram.

O motivo de cada etapa sai desses numeros, nao de opiniao: imagem lida custa
caro, cache criado significa material novo entrando no contexto, e ferramenta
que repete significa laco.

Uso: telemetria.py [--saida painel/telemetria.json] [--dias 120]
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ_TRANSCRIPTS = Path.home() / ".claude" / "projects"
PAUSA_MAX_S = 180          # intervalo maior que isto e o editor longe do teclado
CUSTO_IMAGEM = 1100        # tokens medios de uma folha de contato 1024 px
# token nao custa tudo igual: ler cache e barato, escrever e caro. Os pesos sao a
# razao de preco da API (cache lido 0,1x; cache criado 1,25x; saida 5x a entrada),
# e e por eles que a etapa mais cara e ordenada — somar tudo cru poe o cache lido
# na frente sempre, e cache lido e justamente o que quase nao se paga.
PESOS = {"entrada": 1.0, "cacheCriado": 1.25, "cacheLido": 0.1, "saida": 5.0}

# a marca que abre cada etapa, na ordem de prioridade, e o nome que sai no painel
ETAPAS = [
    ("aprender",  "Aprender estilo",     r"(?:beditor|sofia-estrategista-editora):aprender|scripts/aprender\.py"),
    ("branding",  "Branding",            r"(?:beditor|sofia-estrategista-editora):branding"),
    ("dirigir",   "Dirigir (guia)",      r"(?:beditor|sofia-estrategista-editora):dirigir|scripts/contato\.py|subagent_type.{0,20}diretor|'diretor'"),
    ("enriquecer", "Enriquecer fatos",   r"enriquecedor"),
    ("cortar",    "Cortar",              r"(?:beditor|sofia-estrategista-editora):cortar|--etapa corte|aplicar_decisoes\.py"),
    ("motion",    "Motion graphics",     r"(?:beditor|sofia-estrategista-editora):motion|--etapa motion|scripts/assets\.py|scripts/hf\.py"),
    ("finalizar", "Finalizar",           r"(?:beditor|sofia-estrategista-editora):finalizar|--etapa final|scripts/entregar\.py|acabamento\.py"),
    ("publicar",  "Publicar",            r"(?:beditor|sofia-estrategista-editora):publicar|scripts/publicacao\.py"),
    ("qa",        "QA",                  r"(?:beditor|sofia-estrategista-editora):qa|scripts/travas\.py"),
    ("skill",     "Mexer na própria skill",
     r"skills/beditor/(scripts|referencias|tests)|painel/(gerar|criterios|telemetria)"),
]
MARCAS = [(i, nome, re.compile(rx, re.I)) for i, nome, rx in ETAPAS]


def transcripts(dias):
    """os transcripts que falam da skill, do mais novo para o mais velho"""
    if not RAIZ_TRANSCRIPTS.exists():
        return []
    try:
        saida = subprocess.run(["grep", "-rl", "--include=*.jsonl", "-e", "beditor",
                                str(RAIZ_TRANSCRIPTS)],
                               capture_output=True, text=True, timeout=300, encoding="utf-8", errors="replace").stdout
    except Exception:
        return []
    limite = datetime.now().timestamp() - dias * 86400
    arqs = [Path(p) for p in saida.splitlines() if p.strip()]
    return sorted([a for a in arqs if a.exists() and a.stat().st_mtime >= limite],
                  key=lambda a: a.stat().st_mtime, reverse=True)


def _quando(d):
    t = d.get("timestamp")
    if not t:
        return None
    try:
        return datetime.fromisoformat(t.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def _marca(texto):
    for i, _nome, rx in MARCAS:
        if rx.search(texto):
            return i
    return None


def _blocos(m):
    c = m.get("content")
    return c if isinstance(c, list) else []


def zero():
    return {"entrada": 0, "cacheCriado": 0, "cacheLido": 0, "saida": 0,
            "ms": 0, "mensagens": 0, "imagens": 0, "ferramentas": {}, "sessoes": set()}


def ler(arq, acc):
    etapa, anterior = None, None
    sessao = arq.stem
    with arq.open(errors="ignore") as fh:
        for linha in fh:
            try:
                d = json.loads(linha)
            except ValueError:
                continue
            m = d.get("message") or {}
            texto_marcas = []
            for b in _blocos(m):
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "tool_use":
                    nome = b.get("name", "?")
                    texto_marcas.append(f"{nome} {json.dumps(b.get('input'), ensure_ascii=False)}")
                    if etapa:
                        acc[etapa]["ferramentas"][nome] = acc[etapa]["ferramentas"].get(nome, 0) + 1
                elif b.get("type") == "image" and etapa:
                    acc[etapa]["imagens"] += 1
                elif b.get("type") == "tool_result" and etapa:
                    dentro = b.get("content")
                    if isinstance(dentro, list):
                        acc[etapa]["imagens"] += sum(
                            1 for x in dentro if isinstance(x, dict) and x.get("type") == "image")
            if d.get("type") == "user" and isinstance(m.get("content"), str):
                texto_marcas.append(m["content"])
            nova = _marca("\n".join(texto_marcas)) if texto_marcas else None
            if nova:
                etapa = nova
            if not etapa:
                continue
            a = acc[etapa]
            a["sessoes"].add(sessao)
            u = m.get("usage") or {}
            if u:
                a["mensagens"] += 1
                a["entrada"] += int(u.get("input_tokens") or 0)
                a["cacheCriado"] += int(u.get("cache_creation_input_tokens") or 0)
                a["cacheLido"] += int(u.get("cache_read_input_tokens") or 0)
                a["saida"] += int(u.get("output_tokens") or 0)
            agora = _quando(d)
            if agora and anterior:
                delta = (agora - anterior).total_seconds()
                if 0 < delta <= PAUSA_MAX_S:
                    a["ms"] += int(delta * 1000)
            if agora:
                anterior = agora


def porques(e):
    """o motivo, tirado do que foi medido — nao de opiniao"""
    fora = []
    tot = e["tokens"]["total"]
    peso = e["pesado"]
    if not tot:
        return ["sem medição ainda: esta etapa não apareceu nos transcripts do período"]
    if e["imagens"]:
        custo = e["imagens"] * CUSTO_IMAGEM
        fora.append(f"{e['imagens']} imagem(ns) entraram no contexto "
                    f"(~{custo // 1000}k tokens, ~{100 * custo / tot:.0f}% do total): "
                    f"folha de contato e quadro de vídeo custam caro por unidade")
    if e["tokens"]["cacheCriado"] > 0.25 * tot:
        fora.append(f"{e['tokens']['cacheCriado'] // 1000}k de cache criado "
                    f"({100 * e['tokens']['cacheCriado'] / tot:.0f}%): material novo entrando — "
                    f"referências da skill, roteiro, transcript e guia")
    if e["tokens"]["cacheLido"] > 0.5 * tot:
        fora.append(f"{e['tokens']['cacheLido'] // 1000}k de cache lido "
                    f"({100 * e['tokens']['cacheLido'] / tot:.0f}% dos tokens, mas só "
                    f"{100 * 0.1 * e['tokens']['cacheLido'] / max(1, peso):.0f}% do custo): o contexto "
                    f"é relido a cada rodada — muitas idas e voltas curtas sobre o mesmo material")
    if 5 * e["tokens"]["saida"] > 0.3 * peso:
        fora.append(f"{e['tokens']['saida'] // 1000}k de saída escrita "
                    f"({100 * 5 * e['tokens']['saida'] / peso:.0f}% do custo): token escrito custa "
                    f"5× o lido — é código, guia e texto saindo daqui")
    ferr = sorted(e["ferramentas"].items(), key=lambda kv: -kv[1])[:2]
    if ferr:
        fora.append("ferramentas que mais rodaram: "
                    + ", ".join(f"{n} ({q}×)" for n, q in ferr))
    if e["mensagens"]:
        fora.append(f"{e['mensagens']} respostas do modelo, "
                    f"{e['tokens']['saida'] // max(1, e['mensagens'])} tokens de saída em média")
    return fora


def porques_tempo(e):
    fora = []
    if not e["ms"]:
        return ["sem tempo medido no período"]
    ferr = sorted(e["ferramentas"].items(), key=lambda kv: -kv[1])[:3]
    lentas = {"Bash": "render, ffmpeg e geração de imagem rodam aqui",
              "Read": "leitura de folhas de contato e de arquivo grande",
              "Agent": "um agente inteiro roda dentro desta etapa",
              "Skill": "carrega a skill e as referências"}
    for n, q in ferr:
        if n in lentas:
            fora.append(f"{n} rodou {q}× — {lentas[n]}")
    fora.append(f"{e['mensagens']} rodadas de modelo no total; "
                f"{e['ms'] / max(1, e['mensagens']) / 1000:.0f} s por rodada em média")
    return fora


def calcular(dias):
    acc = {i: zero() for i, _n, _r in ETAPAS}
    arqs = transcripts(dias)
    for a in arqs:
        ler(a, acc)
    etapas = []
    for i, nome, _rx in ETAPAS:
        a = acc[i]
        total = a["entrada"] + a["cacheCriado"] + a["cacheLido"] + a["saida"]
        e = {"id": i, "nome": nome,
             "tokens": {"entrada": a["entrada"], "cacheCriado": a["cacheCriado"],
                        "cacheLido": a["cacheLido"], "saida": a["saida"], "total": total},
             "pesado": round(sum(PESOS[k] * a[k] for k in PESOS)),
             "ms": a["ms"], "mensagens": a["mensagens"], "imagens": a["imagens"],
             "sessoes": len(a["sessoes"]),
             "ferramentas": dict(sorted(a["ferramentas"].items(), key=lambda kv: -kv[1])[:6])}
        e["porques"] = porques(e)
        e["porquesTempo"] = porques_tempo(e)
        etapas.append(e)
    etapas.sort(key=lambda e: -e["pesado"])
    vivas = [e for e in etapas if e["tokens"]["total"]]
    return {"gerado": datetime.now().astimezone().isoformat(timespec="seconds"),
            "dias": dias, "transcripts": len(arqs),
            "totalTokens": sum(e["tokens"]["total"] for e in etapas),
            "totalPesado": sum(e["pesado"] for e in etapas),
            "pesos": PESOS,
            "totalMs": sum(e["ms"] for e in etapas),
            "maisTokens": vivas[0]["id"] if vivas else None,
            "maisTempo": max(vivas, key=lambda e: e["ms"])["id"] if vivas else None,
            "etapas": etapas}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--saida", default=str(Path(__file__).resolve().parent / "telemetria.json"))
    ap.add_argument("--dias", type=int, default=120)
    a = ap.parse_args()
    dados = calcular(a.dias)
    Path(a.saida).write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8")
    if not dados["totalTokens"]:
        print("telemetria: nenhum transcript da skill no período", file=sys.stderr)
        return
    maior = dados["etapas"][0]  # ja ordenado por custo ponderado
    lenta = max(dados["etapas"], key=lambda e: e["ms"])
    print(f"tokens: {maior['nome']} lidera com {maior['tokens']['total'] // 1000}k de "
          f"{dados['totalTokens'] // 1000}k · tempo: {lenta['nome']} com "
          f"{lenta['ms'] / 3.6e6:.1f} h · {dados['transcripts']} transcript(s)",
          file=sys.stderr)


if __name__ == "__main__":
    main()
