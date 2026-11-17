"""Quanto cada ETAPA custou em tokens e em tempo de sessão — lido do registro do Claude Code.

    python3 custos.py [--sessao <id|caminho|atual>] [--projeto <pasta>] [--desde <ISO>] [--ate <ISO>]
                      [--json] [--por-pedido]

Por que isto existe: `referencias/eficiencia.md` mediu os projetos 14 e 15 à mão,
uma vez, lendo o registro da conversa. O número que saiu (3 817 turnos relendo
1,25 bilhão de tokens) mudou o desenho do pipeline inteiro — mas ficou como uma
foto. O dono pediu o filme: «de forma determinística, registre quantos tokens
estão sendo gastos e quanto tempo tá levando cada etapa». Este script é a
segunda camada dessa medida (a primeira é `oficina.Cronometro`, os segundos de
máquina que os próprios scripts gravam em `edicao/oficina/telemetria.jsonl`).

Fonte: `~/.claude/projects/<cwd com cada caractere não alfanumérico trocado por "-">/<sessão>.jsonl`
mais `<sessão>/subagents/*.jsonl` (os subagentes, `isSidechain: true`). Formato
verificado lendo o arquivo, não a memória:

  - linhas `type: "assistant"` trazem `timestamp`, `requestId`, `message.usage`
    (`input_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`,
    `output_tokens`, `output_tokens_details.thinking_tokens`) e `message.content[]`
    com blocos `tool_use` (`name`, `input`, `id`). VÁRIAS linhas compartilham o
    mesmo `requestId` (um bloco por linha; 1 255 de 2 289 pedidos à API tinham
    mais de uma linha, até 9) e o `usage` é idêntico em todas — conta-se UMA vez.
  - linhas `type: "user"` são o pedido do dono (`message.content` string,
    `promptSource: typed|queued`, `origin.kind: human`) ou um `tool_result`
    (lista com `tool_use_id`). Notificações de tarefa (`promptSource: system`)
    e linhas `isMeta` não são pedidos.

ATRIBUIÇÃO DE ETAPA — determinística e explícita. O turno (um `requestId`) herda
a etapa do seu PRIMEIRO `tool_use`, casado por regex contra `name + " " +
json.dumps(input)`. A ordem da tabela é a precedência: a primeira linha que casa
vence. Um turno sem `tool_use` é «conversa».

    etapa        | padrão (regex)
    -------------|-----------------------------------------------------------
    transcrever  | transcrever\\.py
    cortar       | silencio\\.py | escutar\\.py | dados\\.json
    renderizar   | render_analise\\.py
    medir        | qa_analise\\.py
    provas       | plano\\.json | cartao\\.py | varrer\\.py | lupa\\.py | yt-dlp | acervo
    biblioteca   | biblioteca\\.py
    setup        | setup\\.py | manual
    publicar     | publicacao\\.py | zernio | metricool
    git          | "git " (o comando, com espaço)
    olhar        | Read de .jpg .jpeg .png .webp
    delegar      | Agent
    artifact     | Artifact
    editar       | Edit | Write | NotebookEdit
    investigar   | ctx_* | Grep | Glob | Read | Bash — quando nada acima casou
    outros       | qualquer outra ferramenta (ToolSearch, Monitor, MCP fora da lista)
    conversa     | turno sem tool_use

Por que o PRIMEIRO tool_use e não todos: um turno do modelo é uma decisão só
(«vou rodar o render»); o que vem junto no mesmo turno é acessório. Contar o turno
inteiro numa etapa é o que permite somar tokens sem dividir um `usage` em pedaços.

TEMPO DE PAREDE por etapa: soma dos intervalos entre eventos consecutivos
atribuídos àquela etapa (linhas do modelo e resultados de ferramenta), com TETO
de 120 s por intervalo. O teto é o que separa «o modelo esperou o render» de «o
dono foi almoçar»: um intervalo maior que dois minutos entre dois eventos da
mesma etapa é, quase sempre, espera do dono, e não custo da etapa.

CUSTO RELATIVO: % do total de tokens lidos da cache + criados na cache + saída —
as três colunas que a conta cobra. `entrada nova` fica de fora porque, com
cache, ela é quase sempre 1 ou 2 tokens.

DETERMINISMO: nenhum relógio de agora entra no resultado além do carimbo
`gerado_em`; a ordenação é total (tokens decrescentes, depois nome); o mesmo
arquivo produz a mesma tabela. `test_custos.py` tranca isto.
"""
import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

TETO_INTERVALO_S = 120
PROJETOS_CLAUDE = Path.home() / ".claude" / "projects"

# (etapa, regex) — a ORDEM é a precedência. Casado contra `name + " " + json.dumps(input)`.
ETAPAS = [
    ("transcrever", r"transcrever\.py"),
    ("cortar", r"silencio\.py|escutar\.py|dados\.json"),
    ("renderizar", r"render_analise\.py"),
    ("medir", r"qa_analise\.py"),
    ("provas", r"plano\.json|cartao\.py|varrer\.py|lupa\.py|yt-dlp|acervo"),
    ("biblioteca", r"biblioteca\.py"),
    ("setup", r"setup\.py|manual"),
    ("publicar", r"publicacao\.py|zernio|metricool"),
    ("git", r"\bgit "),
    ("olhar", r"^Read .*\.(?:jpe?g|png|webp)\""),
    ("delegar", r"^Agent\b"),
    ("artifact", r"^Artifact\b"),
    ("editar", r"^(?:Edit|Write|NotebookEdit)\b"),
    ("investigar", r"^(?:\S*ctx_\w*|Grep|Glob|Read|Bash)\b"),
    ("outros", r"."),
]
_ETAPAS_RE = [(nome, re.compile(padrao, re.S)) for nome, padrao in ETAPAS]
CONVERSA = "conversa"

CAMPOS_TOKENS = ("entradaNova", "cacheCriada", "cacheLida", "saida", "pensamento")


# ---------------------------------------------------------------------------
# localizar a sessão
# ---------------------------------------------------------------------------
def pasta_do_cwd(cwd=None):
    """A pasta do registro: o cwd com cada caractere fora de [A-Za-z0-9] virando "-".

    Verificado nos nomes reais: `~/.claude-mem` → `--claude-mem`, `Memória` → `Mem-ria`."""
    cwd = cwd or os.getcwd()
    return PROJETOS_CLAUDE / re.sub(r"[^A-Za-z0-9]", "-", cwd)


def localizar_sessao(sessao="atual", cwd=None):
    """`atual` = o .jsonl mais recente da pasta do cwd; um id procura em todas as pastas;
    um caminho existente é usado como está."""
    if sessao and sessao != "atual" and Path(sessao).is_file():
        return Path(sessao).resolve()
    pasta = pasta_do_cwd(cwd)
    if sessao in (None, "atual"):
        arqs = sorted(pasta.glob("*.jsonl"), key=lambda p: (p.stat().st_mtime, p.name))
        if not arqs:
            raise SystemExit(f"!! nenhum registro em {pasta}")
        return arqs[-1]
    cand = [pasta / f"{sessao}.jsonl"] + [Path(p) for p in sorted(glob.glob(str(PROJETOS_CLAUDE / "*" / f"{sessao}.jsonl")))]
    for c in cand:
        if c.is_file():
            return c.resolve()
    raise SystemExit(f"!! sessão «{sessao}» não encontrada em {PROJETOS_CLAUDE}")


def arquivos_da_sessao(principal):
    """O registro principal e os dos subagentes, em ordem estável."""
    principal = Path(principal)
    sub = principal.with_suffix("") / "subagents"
    return [principal] + sorted(sub.glob("*.jsonl"))


# ---------------------------------------------------------------------------
# ler
# ---------------------------------------------------------------------------
def _ts(s):
    """ISO com Z → datetime com fuso. Sem fuso → hora local da máquina."""
    if s is None:
        return None
    d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    return d if d.tzinfo else d.astimezone()


def etapa_de(ferramentas):
    """A etapa do turno a partir da lista [(name, input), …]; sem ferramenta → conversa."""
    if not ferramentas:
        return CONVERSA
    nome, entrada = ferramentas[0]
    alvo = f"{nome} {json.dumps(entrada, ensure_ascii=False, sort_keys=True, default=str)}"
    for etapa, rx in _ETAPAS_RE:
        if rx.search(alvo):
            return etapa
    return "outros"  # inalcançável (a última linha casa tudo), mas explícito


def _texto_do_pedido(conteudo):
    if isinstance(conteudo, str):
        t = conteudo
    else:
        t = " ".join(b.get("text", "") for b in conteudo if isinstance(b, dict) and b.get("type") == "text")
    return re.sub(r"\s+", " ", t).strip()


def _eh_pedido(e):
    if e.get("isMeta") or e.get("isSidechain"):
        return False
    origem = e.get("origin") or {}
    return e.get("promptSource") in ("typed", "queued") or origem.get("kind") == "human"


def ler_sessao(principal):
    """Lê o registro e devolve turnos, pedidos e eventos — a matéria-prima, sem agregar.

    turnos: {requestId: {ts, agente, modelo, ferramentas:[(name,input)], ids:{tool_use_id}, tokens{…}}}
    pedidos: [{ts, texto}]  eventos: [(ts, requestId)] — uma entrada por linha do modelo e
    por resultado de ferramenta, ambos apontando para o turno a que pertencem."""
    turnos, pedidos, eventos, dono = {}, [], [], {}
    ultimo_ts = None
    for i_arq, arq in enumerate(arquivos_da_sessao(principal)):
        with open(arq, encoding="utf-8") as fh:
            for n, linha in enumerate(fh):
                try:
                    e = json.loads(linha)
                except json.JSONDecodeError:
                    continue
                tipo = e.get("type")
                if tipo not in ("assistant", "user"):
                    continue
                ts = _ts(e.get("timestamp"))
                if ts is None:
                    continue
                ultimo_ts = max(ultimo_ts, ts) if ultimo_ts else ts
                msg = e.get("message") or {}
                if tipo == "assistant":
                    rid = e.get("requestId") or e.get("uuid")
                    t = turnos.get(rid)
                    if t is None:
                        t = turnos[rid] = {"ts": ts, "ordem": (ts, i_arq, n), "agente": bool(e.get("isSidechain")),
                                           "modelo": msg.get("model"), "ferramentas": [], "ids": set(),
                                           "tokens": None}
                    t["ts"] = min(t["ts"], ts)
                    u = msg.get("usage")
                    if u and t["tokens"] is None:
                        t["tokens"] = {
                            "entradaNova": int(u.get("input_tokens") or 0),
                            "cacheCriada": int(u.get("cache_creation_input_tokens") or 0),
                            "cacheLida": int(u.get("cache_read_input_tokens") or 0),
                            "saida": int(u.get("output_tokens") or 0),
                            "pensamento": int((u.get("output_tokens_details") or {}).get("thinking_tokens") or 0),
                        }
                    for b in msg.get("content") or []:
                        if isinstance(b, dict) and b.get("type") == "tool_use":
                            t["ferramentas"].append((b.get("name") or "", b.get("input") or {}))
                            if b.get("id"):
                                t["ids"].add(b["id"])
                                dono[b["id"]] = rid
                    eventos.append((ts, rid))
                else:
                    c = msg.get("content")
                    if isinstance(c, list):
                        for b in c:
                            if isinstance(b, dict) and b.get("type") == "tool_result":
                                rid = dono.get(b.get("tool_use_id"))
                                if rid:
                                    eventos.append((ts, rid))
                    if _eh_pedido(e):
                        txt = _texto_do_pedido(c)
                        if txt:
                            pedidos.append({"ts": ts, "texto": txt})
    for t in turnos.values():
        t["etapa"] = etapa_de(t["ferramentas"])
        if t["tokens"] is None:
            t["tokens"] = dict.fromkeys(CAMPOS_TOKENS, 0)
    pedidos.sort(key=lambda p: p["ts"])
    eventos.sort(key=lambda x: x[0])
    return {"turnos": turnos, "pedidos": pedidos, "eventos": eventos, "fim": ultimo_ts}


# ---------------------------------------------------------------------------
# agregar
# ---------------------------------------------------------------------------
def parede(tempos, teto=TETO_INTERVALO_S):
    """Soma dos intervalos entre eventos consecutivos, cada um limitado ao teto."""
    tempos = sorted(tempos)
    return sum(min(teto, (b - a).total_seconds()) for a, b in zip(tempos, tempos[1:]))


def _zero():
    return {"turnos": 0, "agentes": 0, "chamadas": 0, **dict.fromkeys(CAMPOS_TOKENS, 0)}


def _soma(acc, t):
    acc["agentes" if t["agente"] else "turnos"] += 1
    acc["chamadas"] += len(t["ferramentas"])
    for k in CAMPOS_TOKENS:
        acc[k] += t["tokens"][k]


def _custo(acc):
    return acc["cacheLida"] + acc["cacheCriada"] + acc["saida"]


def analisar(sessao, desde=None, ate=None):
    """Agrega por etapa e por pedido do dono. Filtro por janela [desde, ate] no timestamp."""
    turnos = {rid: t for rid, t in sessao["turnos"].items()
              if (desde is None or t["ts"] >= desde) and (ate is None or t["ts"] <= ate)}
    pedidos = [p for p in sessao["pedidos"]
               if (desde is None or p["ts"] >= desde) and (ate is None or p["ts"] <= ate)]
    eventos = [(ts, rid) for ts, rid in sessao["eventos"] if rid in turnos]

    # por etapa
    por_etapa, tempos = {}, {}
    for t in turnos.values():
        acc = por_etapa.setdefault(t["etapa"], _zero())
        _soma(acc, t)
    for ts, rid in eventos:
        tempos.setdefault(turnos[rid]["etapa"], []).append(ts)
    total = _zero()
    for acc in por_etapa.values():
        for k in acc:
            total[k] += acc[k]
    custo_total = _custo(total) or 1
    etapas = []
    for nome, acc in por_etapa.items():
        etapas.append({"etapa": nome, **acc, "paredeS": round(parede(tempos.get(nome, [])), 1),
                       "custoPct": round(100 * _custo(acc) / custo_total, 1)})
    etapas.sort(key=lambda e: (-_custo(e), e["etapa"]))
    total_linha = {"etapa": "TOTAL", **total, "paredeS": round(sum(e["paredeS"] for e in etapas), 1),
                   "custoPct": 100.0 if por_etapa else 0.0}

    # por pedido: cada prompt humano abre um bloco; o turno cai no último pedido anterior a ele
    blocos = []
    if pedidos:
        for i, p in enumerate(pedidos):
            prox = pedidos[i + 1]["ts"] if i + 1 < len(pedidos) else (sessao["fim"] or p["ts"])
            blocos.append({"quando": p["ts"].astimezone().isoformat(timespec="seconds"),
                           "texto": p["texto"][:60], "ateProximoS": round((prox - p["ts"]).total_seconds(), 1),
                           **_zero()})
        marcos = [p["ts"] for p in pedidos]
        antes = {"quando": None, "texto": "(antes do primeiro pedido da janela)", "ateProximoS": 0.0, **_zero()}
        for t in sorted(turnos.values(), key=lambda t: t["ordem"]):
            i = _ultimo_menor_ou_igual(marcos, t["ts"])
            _soma(blocos[i] if i >= 0 else antes, t)
        if antes["turnos"] or antes["agentes"]:
            blocos.insert(0, antes)
    for b in blocos:
        b["tokens"] = _custo(b)

    return {"etapas": etapas, "total": total_linha, "pedidos": blocos,
            "filtro": {"desde": desde.isoformat(timespec="seconds") if desde else None,
                       "ate": ate.isoformat(timespec="seconds") if ate else None},
            "tetoIntervaloS": TETO_INTERVALO_S}


def _ultimo_menor_ou_igual(marcos, ts):
    i = -1
    for j, m in enumerate(marcos):
        if m <= ts:
            i = j
        else:
            break
    return i


# ---------------------------------------------------------------------------
# camada 1: telemetria dos scripts
# ---------------------------------------------------------------------------
def ler_telemetria(caminho, desde=None, ate=None):
    """`telemetria.jsonl` (o que `oficina.Cronometro` grava) → segundos e execuções por etapa."""
    caminho = Path(caminho)
    if not caminho.is_file():
        return []
    acc = {}
    with open(caminho, encoding="utf-8") as fh:
        for linha in fh:
            try:
                e = json.loads(linha)
            except json.JSONDecodeError:
                continue
            ini = _ts(e.get("inicio")) if e.get("inicio") else None
            if ini and ((desde and ini < desde) or (ate and ini > ate)):
                continue
            a = acc.setdefault(e.get("etapa", "?"), {"etapa": e.get("etapa", "?"), "execucoes": 0,
                                                     "falhas": 0, "segundosMaquina": 0.0})
            a["execucoes"] += 1
            a["falhas"] += 1 if e.get("rc") else 0
            a["segundosMaquina"] += float(e.get("segundos") or 0)
    saida = sorted(acc.values(), key=lambda a: (-a["segundosMaquina"], a["etapa"]))
    for a in saida:
        a["segundosMaquina"] = round(a["segundosMaquina"], 1)
    return saida


def cruzar(resultado, maquina):
    """Lado a lado: segundos de máquina (camada 1) e tempo de sessão (camada 2) da mesma etapa."""
    sessao = {e["etapa"]: e["paredeS"] for e in resultado["etapas"]}
    return [{**m, "paredeSessaoS": sessao.get(m["etapa"], 0.0)} for m in maquina]


# ---------------------------------------------------------------------------
# apresentar
# ---------------------------------------------------------------------------
def _n(v):
    """Milhar com espaço, como em `eficiencia.md` («3 817»)."""
    if isinstance(v, float):
        return f"{v:,.1f}".replace(",", " ")
    return f"{int(v):,}".replace(",", " ")


def _hms(s):
    s = int(round(s))
    h, m, sec = s // 3600, (s % 3600) // 60, s % 60
    if h:
        return f"{h}h {m:02d}min"
    if m:
        return f"{m}min {sec:02d}s"
    return f"{sec}s"


def _tabela(cabecalho, linhas, alinhar_esq=(0,)):
    larg = [len(c) for c in cabecalho]
    for l in linhas:
        for i, c in enumerate(l):
            larg[i] = max(larg[i], len(c))

    def fmt(l):
        return "  ".join(c.ljust(larg[i]) if i in alinhar_esq else c.rjust(larg[i]) for i, c in enumerate(l))
    sep = "  ".join("-" * w for w in larg)
    return "\n".join([fmt(cabecalho), sep] + [fmt(l) for l in linhas])


def texto(resultado, por_pedido=False, maquina=None, cabeca=None):
    partes = []
    if cabeca:
        partes.append(cabeca)
    cab = ["etapa", "turnos", "agentes", "chamadas", "entrada nova", "cache criada", "cache lida",
           "saída (pensamento)", "parede", "custo %"]

    def linha(e):
        return [e["etapa"], _n(e["turnos"]), _n(e["agentes"]), _n(e["chamadas"]), _n(e["entradaNova"]),
                _n(e["cacheCriada"]), _n(e["cacheLida"]), f"{_n(e['saida'])} ({_n(e['pensamento'])})",
                _hms(e["paredeS"]), f"{e['custoPct']:.1f}"]
    linhas = [linha(e) for e in resultado["etapas"]] + [linha(resultado["total"])]
    partes.append("POR ETAPA (parede = intervalos entre eventos da etapa, teto de "
                  f"{resultado['tetoIntervaloS']} s cada)\n" + _tabela(cab, linhas))

    if por_pedido:
        cab2 = ["hora", "pedido do dono", "turnos", "agentes", "chamadas", "cache lida", "saída",
                "tokens", "até o próximo"]
        linhas2 = [[(b["quando"] or "")[11:16], b["texto"], _n(b["turnos"]), _n(b["agentes"]), _n(b["chamadas"]),
                    _n(b["cacheLida"]), _n(b["saida"]), _n(b["tokens"]), _hms(b["ateProximoS"])]
                   for b in resultado["pedidos"]]
        partes.append("POR PEDIDO DO DONO (tokens = cache lida + criada + saída)\n"
                      + _tabela(cab2, linhas2, alinhar_esq=(0, 1)))

    if maquina:
        cab3 = ["etapa", "execuções", "falhas", "máquina (scripts)", "sessão (modelo)"]
        linhas3 = [[m["etapa"], _n(m["execucoes"]), _n(m["falhas"]), _hms(m["segundosMaquina"]),
                    _hms(m["paredeSessaoS"])] for m in maquina]
        partes.append("MÁQUINA × SESSÃO (telemetria.jsonl dos scripts, lado a lado com o tempo de parede da etapa)\n"
                      + _tabela(cab3, linhas3))
    return "\n\n".join(partes) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _iso_local(s):
    if not s:
        return None
    return _ts(s)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--sessao", default="atual", help="id, caminho do .jsonl, ou «atual» (padrão)")
    ap.add_argument("--projeto", default=None, help="pasta do projeto: escreve edicao/oficina/custos.json e cruza com telemetria.jsonl")
    ap.add_argument("--desde", default=None, help="ISO (hora local se sem fuso)")
    ap.add_argument("--ate", default=None, help="ISO (hora local se sem fuso)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--por-pedido", action="store_true")
    a = ap.parse_args(argv)

    principal = localizar_sessao(a.sessao)
    desde, ate = _iso_local(a.desde), _iso_local(a.ate)
    sessao = ler_sessao(principal)
    res = analisar(sessao, desde, ate)
    res["sessao"] = str(principal)
    res["arquivos"] = [str(p) for p in arquivos_da_sessao(principal)]
    res["gerado_em"] = datetime.now().astimezone().isoformat(timespec="seconds")

    maquina = None
    if a.projeto:
        of = Path(a.projeto).resolve() / "edicao" / "oficina"
        res["telemetria"] = str(of / "telemetria.jsonl")
        maquina = cruzar(res, ler_telemetria(of / "telemetria.jsonl", desde, ate))
        res["maquina"] = maquina
        of.mkdir(parents=True, exist_ok=True)
        (of / "custos.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")

    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return
    cabeca = (f"sessão {principal.stem} · {len(res['arquivos']) - 1} subagente(s) · "
              f"janela {res['filtro']['desde'] or 'início'} → {res['filtro']['ate'] or 'fim'} · gerado em {res['gerado_em']}")
    sys.stdout.write(texto(res, por_pedido=a.por_pedido, maquina=maquina, cabeca=cabeca))
    if a.projeto:
        print(f"escrito: {Path(a.projeto).resolve() / 'edicao' / 'oficina' / 'custos.json'}")


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
