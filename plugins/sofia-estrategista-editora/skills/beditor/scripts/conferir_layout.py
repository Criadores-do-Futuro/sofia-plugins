#!/usr/bin/env python3
"""conferir_layout.py — mede a composicao num browser de verdade e acusa o torto.

Pedido do dono (2026-09-11): *"quero que sempre verifique se o destaque esta bem
posicionado, se o texto ta bem posicionado, porque e facil que as coisas fiquem
tortas neste estilo"*.

E facil mesmo, e por um motivo estrutural: a colagem posiciona coisas por
**numero calculado em Python** (a elipse da caneta cai em `ativo * 122`, a
largura do circulo sai de `len(texto) * 46`) enquanto quem decide a altura real
da linha e a largura real da palavra e o **navegador**, com a metrica da fonte.
Enquanto os dois concordam ninguem ve; quando o texto quebra em duas linhas, ou
a palavra e estreita, o destaque circula o lugar errado — e o quadro parado
continua bonito, o que faz o erro passar na revisao.

Ler o codigo nao resolve: so medindo. Este script abre a pagina no Chromium,
avanca a timeline ate o fim (`tl.progress(1)`, o estado em que tudo ja entrou) e
le `getBoundingClientRect()` de cada elemento. As regras abaixo sao de ERRO, nao
de gosto — cada uma falha so quando a composicao esta de fato quebrada.

    python3 conferir_layout.py                 # a bateria padrao
    python3 conferir_layout.py --estilo vox    # so um estilo
    python3 conferir_layout.py --json          # saida para outro programa
"""
import argparse
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hf  # noqa: E402

W, H = 1080, 1920
TOPO_MORTO, BASE_MORTA = 230, 1498      # linguagem-visual.md, areas seguras

# o que e conteudo (tem de caber e ser lido). Fora daqui ficam as camadas de
# acabamento — `.fibra` e 116% do quadro DE PROPOSITO (o fundo em movimento
# precisa de folga para deslocar), `.lente` e `.papel` cobrem o quadro inteiro.
CONTEUDO = (".ln, .pal, .titulo-q, .credito, .olho, .etiqueta, .rot, .tira span,"
            " .tira b, .item b, .laje-v, .barra span, .porta-recorte, .graf,"
            " .barras, .chamada, .regua")
TEXTO = (".ln, .pal, .titulo-q, .credito, .olho, .etiqueta, .rot, .tira span,"
         " .laje-v, .barra span")

MEDIR = """
() => {
  const box = el => { const r = el.getBoundingClientRect();
    return {x:r.x, y:r.y, w:r.width, h:r.height, right:r.right, bottom:r.bottom}; };
  const visivel = el => {
    const s = getComputedStyle(el);
    if (s.display === 'none' || s.visibility === 'hidden') return false;
    const r = el.getBoundingClientRect();
    return r.width > 0.5 && r.height > 0.5;
  };
  const colher = sel => [...document.querySelectorAll(sel)]
      .filter(visivel).map(el => ({sel: el.className.toString().trim() ||
                                        el.tagName.toLowerCase(),
                                   texto: (el.textContent || '').trim().slice(0, 40),
                                   ...box(el)}));
  // o grifo: a faixa <i> contra o texto que ela deveria cobrir
  const grifos = [...document.querySelectorAll('.grifo')].filter(visivel).map(g => {
    const i = g.querySelector('i');
    return {texto: (g.textContent || '').trim().slice(0, 40),
            palavra: box(g), faixa: i ? box(i) : null};
  });
  // a anotacao da caneta e o alvo que ela deveria circular
  const anots = [...document.querySelectorAll('.anot')].filter(visivel).map(a => box(a));
  const alvo = document.querySelector('.grifo') ?
        document.querySelector('.ln:has(.grifo), .laje-v.viva, .pal') : null;
  return {
    conteudo: colher(ARG_CONTEUDO),
    texto: colher(ARG_TEXTO),
    grifos, anots,
    alvo_do_grifo: alvo ? box(alvo) : null,
    tira_ativa: document.querySelector('.tira.agora') ?
                box(document.querySelector('.tira.agora')) : null,
  };
}
"""


def _sobrepoe(a, b):
    """area da interseccao entre duas caixas"""
    dx = min(a["right"], b["right"]) - max(a["x"], b["x"])
    dy = min(a["bottom"], b["bottom"]) - max(a["y"], b["y"])
    return max(0.0, dx) * max(0.0, dy)


def _regras(m, rotulo):
    """as regras de ERRO. Cada uma acusa composicao quebrada, nunca gosto."""
    problemas = []

    # 1. nada de conteudo pode vazar o quadro
    for e in m["conteudo"]:
        if e["x"] < -1 or e["y"] < -1 or e["right"] > W + 1 or e["bottom"] > H + 1:
            problemas.append(
                f"{rotulo}: '{e['sel']}' vaza o quadro "
                f"(x {e['x']:.0f}–{e['right']:.0f}, y {e['y']:.0f}–{e['bottom']:.0f})")

    # 2. texto na zona morta da interface
    for e in m["texto"]:
        if e["y"] < TOPO_MORTO or e["bottom"] > BASE_MORTA:
            problemas.append(
                f"{rotulo}: texto '{e['texto'][:24]}' fora da area segura "
                f"(y {e['y']:.0f}–{e['bottom']:.0f}, seguro {TOPO_MORTO}–{BASE_MORTA})")

    # 3. o grifo tem de cobrir a palavra que ele destaca. E o erro mais provavel
    #    do estilo: a faixa e desenhada por CSS relativo ao span, mas rotacao e
    #    clip-path podem deixa-la curta numa palavra estreita.
    for g in m["grifos"]:
        if not g["faixa"]:
            problemas.append(f"{rotulo}: grifo '{g['texto'][:24]}' sem a faixa <i>")
            continue
        p, f = g["palavra"], g["faixa"]
        if p["w"] < 1:
            continue
        coberto = max(0.0, min(p["right"], f["right"]) - max(p["x"], f["x"])) / p["w"]
        if coberto < 0.92:
            problemas.append(
                f"{rotulo}: grifo cobre so {coberto*100:.0f}% de '{g['texto'][:24]}' "
                f"(faixa x {f['x']:.0f}–{f['right']:.0f}, palavra {p['x']:.0f}–{p['right']:.0f})")
        # a faixa tem de ficar ATRAS da palavra, nao deslocada para cima/baixo
        desvio = abs((f["y"] + f["h"] / 2) - (p["y"] + p["h"] / 2))
        if desvio > p["h"] * 0.35:
            problemas.append(
                f"{rotulo}: grifo de '{g['texto'][:24]}' deslocado {desvio:.0f}px "
                f"na vertical")

    # 4. a caneta tem de circular o alvo, nao o vizinho. Aqui mora o `ativo*122`
    #    do indice e o `acesa*114` da cartela: numero em Python contra metrica
    #    de fonte no navegador.
    alvo = m["tira_ativa"] or m["alvo_do_grifo"]
    if alvo and m["anots"]:
        for a in m["anots"]:
            if _sobrepoe(a, alvo) <= 0:
                problemas.append(
                    f"{rotulo}: a anotacao nao toca o alvo "
                    f"(anot y {a['y']:.0f}–{a['bottom']:.0f}, "
                    f"alvo y {alvo['y']:.0f}–{alvo['bottom']:.0f})")
            else:
                centro = a["y"] + a["h"] / 2
                if not (alvo["y"] - alvo["h"] * 0.6 <= centro <= alvo["bottom"] + alvo["h"] * 0.6):
                    problemas.append(
                        f"{rotulo}: a anotacao esta centrada fora do alvo "
                        f"(centro y {centro:.0f}, alvo {alvo['y']:.0f}–{alvo['bottom']:.0f})")

    # 5. dois textos nao podem se sobrepor de forma significativa
    t = m["texto"]
    for i in range(len(t)):
        for j in range(i + 1, len(t)):
            a, b = t[i], t[j]
            menor = min(a["w"] * a["h"], b["w"] * b["h"]) or 1
            if _sobrepoe(a, b) / menor > 0.25:
                problemas.append(
                    f"{rotulo}: '{a['texto'][:18]}' e '{b['texto'][:18]}' se sobrepoem")
    return problemas


# a bateria: casos normais E os que costumam quebrar (texto longo que quebra
# linha, palavra estreita, lista cheia). O caso facil nunca achou bug nenhum.
BATERIA = [
    ("cartela curta", {"tipo": "cartela", "linhas": ["o dado", "que importa"],
                       "acender": "importa", "fonte": "IBGE 2026"}),
    ("cartela linha longa", {"tipo": "cartela",
                             "linhas": ["uma primeira linha bem mais longa que o normal",
                                        "e a que importa de verdade aqui"],
                             "acender": "importa", "fonte": "Fonte: IBGE, 2026"}),
    ("cartela palavra estreita", {"tipo": "cartela", "linhas": ["era", "ili"],
                                  "acender": "ili", "fonte": "x"}),
    ("cartela acende a primeira", {"tipo": "cartela",
                                   "linhas": ["a que importa", "segunda", "terceira"],
                                   "acender": "importa", "fonte": "y"}),
    ("palavras cheia", {"tipo": "palavras",
                        "palavras": ["primeiro", "segundo", "terceiro", "quarto", "quinto"],
                        "acender": "terceiro"}),
    ("indice primeiro ativo", {"tipo": "indice",
                               "palavras": ["um", "dois", "tres", "quatro", "cinco"],
                               "acender": "um"}),
    ("indice ultimo ativo", {"tipo": "indice",
                             "palavras": ["um", "dois", "tres", "quatro", "cinco"],
                             "acender": "cinco"}),
    ("indice texto longo", {"tipo": "indice",
                            "palavras": ["uma parte com nome comprido demais",
                                         "outra parte tambem comprida", "curta"],
                            "acender": "curta"}),
    ("camadas", {"tipo": "camadas", "palavras": ["base", "meio", "topo"],
                 "acender": "topo"}),
    ("dado curva", {"tipo": "dado", "texto": "a curva que importa",
                    "curva": [0.1, 0.4, 0.35, 0.9], "fonte": "IBGE 2026"}),
    ("dado barras", {"tipo": "dado", "texto": "as barras",
                     "serie": [{"rotulo": "a", "valor": 0.3},
                               {"rotulo": "b", "valor": 0.8}], "fonte": "IBGE"}),
]


def conferir(estilo="vox", casos=None, mostrar=False):
    """devolve a lista de problemas medidos no navegador (vazia = tudo certo)"""
    from playwright.sync_api import sync_playwright

    casos = casos or BATERIA
    hf.aplicar_estilo(estilo)
    achados = []
    medir = (MEDIR.replace("ARG_CONTEUDO", json.dumps(CONTEUDO))
                  .replace("ARG_TEXTO", json.dumps(TEXTO)))
    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as pw:
        nav = pw.chromium.launch()
        pag = nav.new_page(viewport={"width": W, "height": H})
        for rotulo, base in casos:
            p = {"id": "M1", "t0": 0, "t1": 4000, "texto": base.get("texto", "uma linha")}
            p.update(base)
            arq = Path(tmp) / "index.html"
            arq.write_text(hf.html_do_plano(p, W, H), encoding="utf-8")
            pag.goto(arq.as_uri())
            # o estado que interessa e o FIM: tudo ja entrou e parou no lugar.
            # Medir no meio da entrada acusaria torto o que ainda esta chegando.
            pag.wait_for_function("() => typeof tl !== 'undefined'", timeout=15000)
            pag.evaluate("() => tl.progress(1)")
            m = pag.evaluate(medir)
            achados += _regras(m, f"[{estilo}/{rotulo}]")
            if mostrar:
                print(f"  {rotulo}: {len(m['conteudo'])} elementos medidos")
        nav.close()
    return achados


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--estilo", default="vox", help="estilo do motion (padrao: vox)")
    ap.add_argument("--json", action="store_true", help="saida em JSON")
    ap.add_argument("-v", "--verboso", action="store_true")
    a = ap.parse_args()

    problemas = conferir(a.estilo, mostrar=a.verboso)
    if a.json:
        print(json.dumps(problemas, ensure_ascii=False, indent=2))
    elif problemas:
        print(f"{len(problemas)} problema(s) de posicionamento:\n")
        for x in problemas:
            print(f"  - {x}")
    else:
        print(f"layout do '{a.estilo}': tudo no lugar "
              f"({len(BATERIA)} composicoes medidas no navegador)")
    return 1 if problemas else 0


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    sys.exit(main())
