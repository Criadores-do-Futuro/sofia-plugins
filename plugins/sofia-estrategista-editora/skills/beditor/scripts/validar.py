#!/usr/bin/env python3
"""
validar.py — o que o guia nao pode ter.

O diretor escreve o guia a mao, e mao erra formato: deixa buraco, sobrepoe,
esquece o porque. Este script devolve a lista de erros em portugues, um por
linha com o id do momento, e o agente corrige ate zero. E a mesma trava que
faltou nas telas pretas — so que antes de existir plano.

Uso: validar.py guia.json [--contato contato.json]   (exit 1 se houver erro)
"""
import argparse, json, re, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import direcao, estilos, mascara  # noqa: E402

DECISOES = {"aroll", "motion", "aroll+motion", "cortar"}
COM_MOTION = {"motion", "aroll+motion"}
MIN_MOTION_MS = 2500
DENSIDADE = (40, 60)
FRASES_VAZIAS = ("aparece", "o texto entra", "mostra", "surge")
ENTRADAS = {"corte", "deslizar", "subir", "escalar"}
SAIDAS = {"corte", "varrer", "empurrar", "implodir", "apagar"}
CAMAS = {"sobe", "desce", "mantem", "some"}
# ideia de imagem que pede texto ou numero legivel: roteamento errado
PEDE_TEXTO = re.compile(
    r"\b(numerad[oa]s?|n[uú]meros?|algarismos?|texto leg[ií]vel|letras? leg[ií]v\w+|"
    r"escrit[oa]s?|r[oó]tulos?|placa com|palavra escrita)\b", re.I)
# planos que sao so tipografia: uteis, mas nao podem ser a metade do video
SO_TEXTO = {"palavras", "cartela"}
TETO_SO_TEXTO = 0.35
NEGA = re.compile(r"\b(n[aã]o|nunca|nem|jamais|nenhum[a]?)\b", re.I)


def _negadas(fala, palavras):
    """as palavras do plano que a fala NEGA. Escrever a palavra limpa enquanto a
    voz diz "elas nao sao inteligentes" inverte o sentido na tela: quem le sem
    som le a promessa, nao a acusacao. O risco existe para isso."""
    achadas = []
    for trecho in re.split(r"[./\n]", fala or ""):
        if not NEGA.search(trecho):
            continue
        alvo = trecho.casefold()
        for w in palavras:
            w = str(w).strip().casefold()
            # o radical evita perder "inteligentes" quando a fala diz "inteligente"
            if len(w) >= 5 and w[:-2] in alvo:
                achadas.append(w)
    return achadas


def _frase_de(contato, de_ms):
    """a frase do contato que comeca neste momento (tolerancia 400 ms)"""
    if not contato:
        return None
    for f in contato.get("frases", []):
        if abs(f["deMs"] - de_ms) <= 400:
            return f
    return None


# Conectores que EXIGEM um antecedente imediato: a frase que eles abrem so faz
# sentido contra a frase anterior. Se a anterior foi cortada, o conector fica
# apontando para o vazio e a fala muda de sentido — o espectador ouve uma
# contradicao que nao existe.
#
# Nao entram aqui os consecutivos ("entao", "por isso", "portanto"): esses
# seguem do argumento inteiro, nao de uma frase so, e sobrevivem a um corte
# vizinho. Cobrar deles daria alarme falso em corte legitimo.
ORFAOS = (
    # adversativos: negam o que veio imediatamente antes
    "so que", "só que", "mas ", "porem", "porém", "contudo", "entretanto",
    "no entanto", "apesar disso", "ainda assim", "por outro lado", "mesmo assim",
    # aditivos: somam a uma lista que precisa existir
    "alem disso", "além disso", "tambem", "também", "inclusive", "outra coisa",
    "fora isso", "e outra",
    # reformuladores: reescrevem uma frase que precisa ter sido dita
    "ou seja", "quer dizer", "alias", "aliás", "isso porque",
)


def _normal(t):
    import unicodedata
    t = unicodedata.normalize("NFD", (t or "").strip().lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def _conectores_orfaos(ms):
    """corte que deixa um conector apontando para o vazio.

    Regra nascida do pitch de 2026-09-12: cortar «Tudo bem que um ou outro era
    até mais ou menos interessante» deixou «…uma porcaria. SÓ QUE todos eles
    eram genéricos», e o «só que» passou a contrastar com nada. O dono ouviu
    na hora: *"tem um corte ou outro que prejudicou a fala"*.

    O conserto quando isto aparece nao e devolver o momento anterior: e aparar
    a CABECA do momento que ficou, cortando o conector junto (um momento
    `cortar` de meio segundo antes dele). A frase segue inteira, sem a costura
    solta."""
    erros = []
    for a, b in zip(ms, ms[1:]):
        if a.get("decisao") != "cortar" or b.get("decisao") == "cortar":
            continue
        fala = _normal(b.get("fala"))
        for c in ORFAOS:
            if fala.startswith(_normal(c)):
                erros.append(
                    f"{b['id']}: comeca com «{(b.get('fala') or '')[:len(c)+6].strip()}…» "
                    f"e o momento anterior ({a['id']}) foi cortado — o conector fica "
                    f"orfao e a frase muda de sentido. Apare a cabeca do {b['id']} "
                    f"cortando o conector junto, ou devolva o {a['id']}.")
                break
    return erros


# a soltura de uma palavra dura mais que o timestamp do ASR; abaixo disto o
# ouvido registra "cortou no meio" mesmo sem saber por que
RESPIRO_MIN_MS = 140


def _bordas_sem_respiro(ms, contato):
    """emenda sem silencio de um lado: a palavra sai decepada.

    Vale so onde ha CORTE de verdade depois (o momento seguinte e `cortar`).
    O fim do video e outra coisa: la nao ha emenda, ha o ultimo quadro, e o
    compositor resolve a cauda com 80 ms de fade.

    Nasceu de 2026-09-12: o M10 terminava exatamente no fim de «propria» e o
    dono ouviu a palavra decepada. O montador agora empurra a saida sozinho
    quando ha silencio para isso — esta regra pega o caso em que NAO ha, e que
    portanto so uma pessoa pode resolver."""
    erros = []
    frases = (contato or {}).get("frases") or []
    if not frases:
        return erros
    vivos = [i for i, m in enumerate(ms) if m.get("decisao") != "cortar"]
    ultimo_vivo = vivos[-1] if vivos else None
    for i, m in enumerate(ms):
        if m.get("decisao") == "cortar" or i == ultimo_vivo:
            continue
        prox = ms[i + 1] if i + 1 < len(ms) else None
        if prox is None or prox.get("decisao") != "cortar":
            continue
        fim = m["ateMs"]
        casa = next((f for f in frases if abs(f["ateMs"] - fim) <= 120), None)
        if casa is not None:
            if int(casa.get("pausaDepoisMs") or 0) < RESPIRO_MIN_MS:
                erros.append(
                    f"{m['id']}: corta {int(casa.get('pausaDepoisMs') or 0)} ms depois de "
                    f"«{casa['texto'].split()[-1]}» e o momento seguinte sai — nao ha "
                    f"silencio para a palavra soltar. Mova a fronteira ou mantenha o "
                    f"{prox['id']}.")
            continue
        dentro = next((f for f in frases if f["deMs"] < fim < f["ateMs"]), None)
        if dentro is not None:
            erros.append(
                f"{m['id']}: a fronteira cai DENTRO da frase «{dentro['texto'][:44]}…» "
                f"e o momento seguinte sai — emenda no meio de palavra falada. "
                f"Leve a fronteira para o fim de uma frase.")
    return erros


def validar(guia, contato=None):
    erros = []
    ms = guia.get("momentos") or []
    dur = (guia.get("take") or {}).get("duracaoMs") or (contato or {}).get("takeMs")
    if not ms:
        return ["guia sem momentos"]
    if not (guia.get("arco") or "").strip():
        erros.append("cabecalho: `arco` vazio — sem arco em tres linhas, nao ha video")

    # cobertura
    if ms[0]["deMs"] != 0:
        erros.append(f"{ms[0]['id']}: primeiro momento comeca em {ms[0]['deMs']}, tem de ser 0")
    for a, b in zip(ms, ms[1:]):
        if b["deMs"] > a["ateMs"]:
            erros.append(f"{a['id']}→{b['id']}: buraco de {b['deMs']-a['ateMs']} ms (tela preta)")
        elif b["deMs"] < a["ateMs"]:
            erros.append(f"{a['id']}→{b['id']}: sobreposicao de {a['ateMs']-b['deMs']} ms")
    if dur and ms[-1]["ateMs"] != dur:
        erros.append(f"{ms[-1]['id']}: termina em {ms[-1]['ateMs']}, o fim do take e {dur}")

    erros += _conectores_orfaos(ms)
    erros += _bordas_sem_respiro(ms, contato)

    tempo_motion = 0
    for i, m in enumerate(ms):
        mid = m.get("id", f"#{i}")
        d = m.get("decisao")
        if d not in DECISOES:
            erros.append(f"{mid}: decisao `{d}` invalida (aroll, motion, aroll+motion, cortar)")
            continue
        if not (m.get("porque") or "").strip():
            erros.append(f"{mid}: sem `porque` — sem porque nao ha como discordar")
        if (m.get("musica") or {}).get("cama") not in CAMAS:
            erros.append(f"{mid}: musica.cama tem de ser sobe/desce/mantem/some")
        antes_audio = int(m.get("audioAntesMs") or 0)
        if antes_audio:
            fa = _frase_de(contato, m["deMs"])
            if fa is not None and antes_audio > fa.get("pausaAntesMs", 0):
                erros.append(f"{mid}: audioAntesMs {antes_audio} maior que a pausa antes da "
                             f"frase ({fa['pausaAntesMs']} ms) — o audio entraria em cima da "
                             f"palavra anterior")
        tem = bool(m.get("motion"))
        if d in COM_MOTION and not tem:
            erros.append(f"{mid}: decisao `{d}` exige o objeto `motion`")
        if d not in COM_MOTION and tem:
            erros.append(f"{mid}: decisao `{d}` nao pode ter `motion`")
        if d not in COM_MOTION or not tem:
            continue

        mo = m["motion"]
        dur_m = m["ateMs"] - m["deMs"]
        tempo_motion += dur_m
        if dur_m < MIN_MOTION_MS:
            erros.append(f"{mid}: motion com {dur_m} ms — abaixo de {MIN_MOTION_MS}, pisca em vez "
                         f"de comunicar; funda com o vizinho ou vire aroll")
        mov = (mo.get("movimento") or "").strip().lower()
        if not mov or any(mov == v or mov.startswith(v) for v in FRASES_VAZIAS) or len(mov.split()) < 6:
            erros.append(f"{mid}: `movimento` nao responde 'o que entra, o que acontece, o que sai'")
        if not (mo.get("ideia") or "").strip():
            erros.append(f"{mid}: motion sem `ideia`")
        if mo.get("entrada", "corte") not in ENTRADAS:
            erros.append(f"{mid}: entrada `{mo.get('entrada')}` invalida")
        if mo.get("saida", "corte") not in SAIDAS:
            erros.append(f"{mid}: saida `{mo.get('saida')}` invalida")
        antes = int(mo.get("entraAntesMs") or 0)
        f = _frase_de(contato, m["deMs"])
        if f is not None and antes > f.get("pausaAntesMs", 0):
            erros.append(f"{mid}: entraAntesMs {antes} maior que a pausa antes da frase "
                         f"({f['pausaAntesMs']} ms) — o grafico entraria em cima da palavra anterior")
        dados = mo.get("dados") or {}
        t = mo.get("tipo")
        if t == "tela" and not (dados.get("tela") or {}).get("modo"):
            erros.append(f"{mid}: `tela` sem dados.tela.modo — janela vazia e tela preta")
        if t == "palavras" and not dados.get("palavras"):
            erros.append(f"{mid}: `palavras` sem dados.palavras")
        # a galaxia fica de fora: um ceu sem vertice nenhum e um plano legitimo
        # ("imagina uma galaxia"), enquanto laje e item de lista sem nome sao vazios
        if t in ("camadas", "indice") and not dados.get("palavras"):
            erros.append(f"{mid}: `{t}` sem dados.palavras — sao elas que viram "
                         f"laje ou item da lista")
        # a fala nega, a tela afirma: o erro que fez o video dizer INTELIGENTES
        # enquanto a voz dizia "elas nao sao inteligentes"
        if dados.get("palavras") and dados.get("riscar") in (None, False):
            neg = _negadas(m.get("fala"), dados["palavras"])
            if neg:
                erros.append(f"{mid}: a fala nega {', '.join(sorted(set(neg)))} e o plano "
                             f"escreve a palavra limpa — falta `dados.riscar`, ou o "
                             f"momento pede a ilustracao do erro em vez da palavra")
        if t == "cartela" and not (dados.get("texto") or "").strip():
            erros.append(f"{mid}: `cartela` sem dados.texto — cartela sem texto e tela preta")
        if t == "dado" and not (dados.get("curva") or dados.get("serie")):
            erros.append(f"{mid}: `dado` sem curva nem serie — numero solto nao e grafico")
        # Texto, numero e interface sao desenhados em codigo; gerador de imagem
        # erra glifo e alucina numero (ferramentas.md). Uma `ideia` de imagem
        # que pede numero ou texto legivel e roteamento errado, nao ideia ruim.
        if t in ("objeto", "personagem", "obra", "arquivo", "cotidiano") and \
                PEDE_TEXTO.search(mo.get("ideia") or ""):
            erros.append(f"{mid}: `{t}` pede numero ou texto legivel na imagem — isso e "
                         f"codigo (palavras, cartela, dado, tela), nao gerador")
        if mo.get("familia") and not (mo.get("estado") or "").strip():
            erros.append(f"{mid}: motion com `familia` exige `estado` (o que mudou nesta aparicao)")
        # mesmo tipo seguido
        ant = ms[i - 1] if i else None
        if ant and ant.get("decisao") in COM_MOTION and (ant.get("motion") or {}).get("tipo") == t \
                and not mo.get("familia"):
            pq = (m.get("porque") or "").lower()
            if "repet" not in pq and "mesma peca" not in pq and "mesma peça" not in pq:
                erros.append(f"{mid}: segundo `{t}` seguido sem familia — o porque precisa assumir a repeticao")

    fams = Counter((m.get("motion") or {}).get("familia") for m in ms if (m.get("motion") or {}).get("familia"))
    for fam, n in fams.items():
        if n < 2:
            erros.append(f"familia `{fam}` usada por um momento so — familia e peca que volta")

    # Um plano de motion que so escreve a palavra dita e a saida mais barata, e
    # por isso a mais frequente. Ela tem lugar; nao tem o video inteiro. Acima do
    # teto, o guia esta narrando por escrito em vez de ilustrar.
    tipos = Counter((m.get("motion") or {}).get("tipo")
                    for m in ms if m.get("decisao") in COM_MOTION)
    n_motion = sum(tipos.values())
    n_texto = sum(n for t, n in tipos.items() if t in SO_TEXTO)
    # abaixo de meia duzia de planos a proporcao nao mede nada: um guia com dois
    # momentos de motion, os dois de texto, nao esta narrando por escrito.
    if n_motion >= 6 and n_texto / n_motion > TETO_SO_TEXTO:
        erros.append(f"so-texto: {n_texto} de {n_motion} planos de motion sao "
                     f"{'/'.join(sorted(SO_TEXTO))} ({100*n_texto/n_motion:.0f}%, teto "
                     f"{100*TETO_SO_TEXTO:.0f}%) — escrever a palavra dita nao e ilustrar; "
                     f"veja galaxia, camadas, indice, tela, dado e as rotas de imagem")

    # a densidade e medida sobre o que FICA no video (momentos `cortar` fora)
    total = sum(m["ateMs"] - m["deMs"] for m in ms if m.get("decisao") != "cortar")
    pct = 100.0 * tempo_motion / max(1, total)
    dens = guia.get("densidade") or {}
    alvo = dens.get("alvoPct") or list(DENSIDADE)
    if not (alvo[0] <= pct <= alvo[1]) and not (dens.get("justificativa") or "").strip():
        erros.append(f"densidade: {pct:.0f}% de motion, fora de {alvo[0]}–{alvo[1]}% sem justificativa")
    # formato com motion descreve o estilo do video e o prompt de cada cena
    erros += direcao.validar(guia)
    # guia.estilos so pode apontar pra id que existe na galeria (estilos.py)
    erros += estilos.validar(guia)
    # a mascara Dividir e opcional; so o que foi escrito e conferido
    erros += mascara.validar(guia)
    return erros


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("guia")
    ap.add_argument("--contato")
    a = ap.parse_args()
    guia = json.loads(Path(a.guia).read_text(encoding="utf-8"))
    contato = json.loads(Path(a.contato).read_text(encoding="utf-8")) if a.contato else None
    erros = validar(guia, contato)
    for e in erros:
        print("·", e)
    print(f"{len(erros)} erro(s)")
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
