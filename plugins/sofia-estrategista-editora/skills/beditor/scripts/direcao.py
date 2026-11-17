#!/usr/bin/env python3
"""
direcao.py — a direcao de motion do video inteiro e o prompt de cada cena.

Pedido do dono (2026-09-11): todo formato com motion graphics descreve, antes
de gerar, o estilo do video em oito itens e, para CADA cena, um prompt com
cinco. O diretor escreve os campos no guia; este modulo confere se estao todos
la e monta o prompt de cada cena, que vai para o GUIA.md, para o plano e para
quem desenha (`referencias/direcao-de-motion.md`).

Um guia sem nenhum momento de motion (o formato `dinamismo`) nao leva nada disso.
"""

# (chave no guia, rotulo) — a ordem e a do pedido
DIRECAO = [
    ("estiloAnimacao", "Estilo de animação (2D, 3D, tipografia cinética, flat)"),
    ("movimento",      "Como as coisas se movem (velocidade, easing, bounce, seco ou suave)"),
    ("transicoes",     "Transições (cortes, wipes, morphs, zooms)"),
    ("paleta",         "Paleta e fundo"),
    ("tipografia",     "Tipografia e onde o texto aparece"),
    ("camera",         "Câmera (parada, zoom, pan, shake)"),
    ("climaRitmo",     "Clima e ritmo"),
    ("som",            "Som (whooshes, graves, estilo de música)"),
]
CENA = [
    ("naTela",          "O que aparece e como anima"),
    ("texto",           "Texto exato na tela"),
    ("visual",          "Cores, fundo e tipografia"),
    ("cameraTransicao", "Câmera e transição para a próxima cena"),
    ("som",             "SFX e clima da música"),
]
MAX_PALAVRAS_TEXTO = 6
COM_MOTION = {"motion", "aroll+motion"}


def tem_motion(guia):
    return any(m.get("decisao") in COM_MOTION and m.get("motion")
               for m in guia.get("momentos") or [])


def _vazio(v):
    return not str(v or "").strip()


def validar(guia):
    """erros de direcao e de cena; vazio quando o guia nao tem motion"""
    if not tem_motion(guia):
        return []
    erros = []
    d = guia.get("direcaoMotion") or {}
    faltam = [k for k, _ in DIRECAO if _vazio(d.get(k))]
    if faltam:
        erros.append("direcaoMotion: faltam " + ", ".join(f"`{k}`" for k in faltam)
                     + " — formato com motion descreve o estilo antes de gerar")
    for m in guia["momentos"]:
        if m.get("decisao") not in COM_MOTION or not m.get("motion"):
            continue
        mid, cena = m["id"], (m["motion"].get("cena") or {})
        if not cena:
            erros.append(f"{mid}: motion sem `cena` — cada cena leva o seu prompt")
            continue
        faltam = [k for k, _ in CENA if k != "texto" and _vazio(cena.get(k))]
        if "texto" not in cena:
            faltam.insert(1, "texto")
        if faltam:
            erros.append(f"{mid}: cena sem " + ", ".join(f"`{k}`" for k in faltam))
        n = len(str(cena.get("texto") or "").split())
        if n > MAX_PALAVRAS_TEXTO:
            erros.append(f"{mid}: texto da cena com {n} palavras — o máximo é "
                         f"{MAX_PALAVRAS_TEXTO}; o resto é da fala, não da tela")
    return erros


def prompt_da_cena(guia, m, seguinte=None):
    """um paragrafo so, com os cinco itens da cena e o estilo do video"""
    d = guia.get("direcaoMotion") or {}
    c = (m.get("motion") or {}).get("cena") or {}
    texto = str(c.get("texto") or "").strip()
    dur = f"{(m['ateMs'] - m['deMs']) / 1000:.1f}".replace(".", ",")
    ponto = lambda t: t if t.endswith((".", "!", "?", "»")) else t + "."
    partes = [
        f"Cena {m['id']} ({dur} s), {str(d.get('estiloAnimacao', '')).strip()}.",
        f"Na tela: {str(c.get('naTela', '')).strip()}",
        f"Texto na tela, exatamente: «{texto}»." if texto else "Sem texto na tela.",
        f"Visual: {str(c.get('visual', '')).strip()}",
        f"Movimento: {str(d.get('movimento', '')).strip()}",
        ponto(f"Câmera e transição: {str(c.get('cameraTransicao', '')).strip()}")
        + (f" Passa para {seguinte['id']}." if seguinte else " É a última cena."),
        f"Som: {str(c.get('som', '')).strip()}",
    ]
    return " ".join(ponto(p) for p in partes)


def cenas(guia):
    """[(momento, prompt)] na ordem do video"""
    ms = [m for m in guia.get("momentos") or []
          if m.get("decisao") in COM_MOTION and m.get("motion")]
    return [(m, prompt_da_cena(guia, m, ms[i + 1] if i + 1 < len(ms) else None))
            for i, m in enumerate(ms)]


def markdown(guia):
    """as duas secoes do GUIA.md: a direcao do video e um prompt por cena"""
    if not tem_motion(guia):
        return []
    d = guia.get("direcaoMotion") or {}
    L = ["## Direção de motion", ""]
    L += [f"- **{rot}:** {d.get(k) or '—'}" for k, rot in DIRECAO]
    L += ["", "## Prompt de cada cena", ""]
    for m, p in cenas(guia):
        L += [f"**{m['id']}**", "", p, ""]
    return L
