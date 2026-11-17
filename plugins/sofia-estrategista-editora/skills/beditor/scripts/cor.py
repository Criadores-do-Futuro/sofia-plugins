#!/usr/bin/env python3
"""
cor.py — a correcao de cor do A-roll, num lugar so, com preferencia do canal.

Antes desta ficha a grade do A-roll era uma linha fixa dentro do `acabamento.py`
(`eq=contrast=1.15:gamma=1.02...`). Quando o dono do canal dizia "nao gostei da
cor", nao havia o que ajustar sem editar codigo, e a escolha se perdia no vidro
seguinte. Agora a grade e um dicionario de dez numeros, e ele vem de tres
lugares, nesta ordem — o mais especifico manda:

    1. `guia.cor`          a escolha deste video
    2. `~/.beditor/cor.json`  a preferencia do canal, que atravessa os videos
    3. `COR_PADRAO`        o que a skill traz de fabrica

Cada numero e 1.0 (ou 0) quando nao faz nada, entao uma ficha vazia devolve a
imagem gravada intacta. O filtro so cresce com o que foi realmente mexido: nao
adianta empilhar `eq` neutro, cada passada custa qualidade.
"""
import json
import os
from pathlib import Path

PREFERENCIA = Path.home() / ".beditor" / "cor.json"

# De fabrica: o que o canal usava antes desta ficha existir, para que nada mude
# sozinho em quem ja tinha um projeto no meio. `saturacao` e `gamaAzul` em 1.0
# sao de proposito — dessaturar de leve e empurrar o azul deixava a pele rosada.
COR_PADRAO = {
    "contraste": 1.15,    # eq=contrast   · 1.0 = neutro
    "gama": 1.02,         # eq=gamma      · meio-tom
    "saturacao": 1.00,    # eq=saturation
    "brilho": 0.00,       # eq=brightness · -1..1
    "gamaAzul": 1.00,     # eq=gamma_b
    "temperatura": 6500,  # colortemperature · <6500 esfria, >6500 esquenta
    "tonalidade": 0.00,   # colorbalance verde(-) / magenta(+) no meio-tom
    "preto": 0.000,       # curves: onde o preto assenta (0..0.2)
    "branco": 1.000,      # curves: onde o branco e segurado (0.8..1)
    "nitidez": 0.85,      # unsharp luma_amount · 0 desliga
}

# Limites de sanidade. Numero fora daqui e engano de digitacao ou de slider, e
# uma grade fora de faixa so se descobre no master — tarde demais.
FAIXAS = {
    "contraste": (0.5, 2.0), "gama": (0.5, 2.0), "saturacao": (0.0, 2.0),
    "brilho": (-0.3, 0.3), "gamaAzul": (0.7, 1.4), "temperatura": (3000, 10000),
    "tonalidade": (-0.3, 0.3), "preto": (0.0, 0.2), "branco": (0.8, 1.0),
    "nitidez": (0.0, 2.0),
}


def ler_preferencia(caminho=PREFERENCIA):
    if not Path(caminho).exists():
        return {}
    try:
        dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return dados.get("cor", dados) if isinstance(dados, dict) else {}


def gravar_preferencia(cor, caminho=PREFERENCIA, nota=""):
    """A preferencia do canal, que vale para os proximos videos."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    ficha = {"cor": resolver(cor), "nota": nota}
    caminho.write_text(json.dumps(ficha, ensure_ascii=False, indent=2), encoding="utf-8")
    return caminho


def resolver(*fichas):
    """Junta as fichas na ordem dada (a ultima manda) sobre o padrao, e prende
    cada numero na sua faixa."""
    cor = dict(COR_PADRAO)
    for ficha in fichas:
        for k, v in (ficha or {}).items():
            if k in cor and isinstance(v, (int, float)):
                cor[k] = v
    for k, (lo, hi) in FAIXAS.items():
        cor[k] = max(lo, min(hi, cor[k]))
    return cor


def da_ficha(guia=None, preferencia=None):
    """A ordem que vale no pipeline: padrao < preferencia do canal < guia."""
    pref = ler_preferencia() if preferencia is None else preferencia
    do_guia = (guia or {}).get("cor") if isinstance(guia, dict) else None
    return resolver(pref, do_guia)


def _quase(a, b, tol=1e-3):
    return abs(a - b) < tol


def filtro(cor=None):
    """A cadeia de filtros do ffmpeg. So entra o que foi mexido."""
    c = resolver(cor) if cor is not None else da_ficha()
    partes = []

    eq = []
    if not _quase(c["contraste"], 1.0):
        eq.append(f"contrast={c['contraste']:.3f}")
    if not _quase(c["gama"], 1.0):
        eq.append(f"gamma={c['gama']:.3f}")
    if not _quase(c["saturacao"], 1.0):
        eq.append(f"saturation={c['saturacao']:.3f}")
    if not _quase(c["brilho"], 0.0):
        eq.append(f"brightness={c['brilho']:.3f}")
    if not _quase(c["gamaAzul"], 1.0):
        eq.append(f"gamma_b={c['gamaAzul']:.3f}")
    if eq:
        partes.append("eq=" + ":".join(eq))

    if not _quase(c["temperatura"], 6500.0, 1.0):
        # `mix=1` deixa o filtro fazer o que o numero diz; abaixo disso o
        # resultado nao corresponde ao kelvin escolhido no painel.
        partes.append(f"colortemperature=temperature={int(c['temperatura'])}:mix=1")

    if not _quase(c["tonalidade"], 0.0):
        # verde x magenta no meio-tom: o eixo que sobra depois do kelvin, e o
        # que conserta pele esverdeada de luz de LED barata.
        t = c["tonalidade"]
        partes.append(f"colorbalance=gm={-t:.3f}:rm={t / 2:.3f}:bm={t / 2:.3f}")

    if not (_quase(c["preto"], 0.0) and _quase(c["branco"], 1.0)):
        partes.append(f"curves=all='0/{c['preto']:.3f} 1/{c['branco']:.3f}'")

    if not _quase(c["nitidez"], 0.0):
        # chroma em 0: nitidez em cor vira franja colorida na borda do rosto.
        partes.append("unsharp=luma_msize_x=5:luma_msize_y=5"
                      f":luma_amount={c['nitidez']:.2f}:chroma_amount=0.0")

    return ",".join(partes) or "null"


def css(cor=None):
    """A mesma grade em CSS, para o painel do artifact mostrar ao vivo.

    E uma aproximacao: `filter` do navegador nao tem curva nem kelvin, e a
    ordem das operacoes difere. Serve para ESCOLHER; quem decide o pixel e o
    ffmpeg. Por isso o painel confere a escolha num quadro re-renderizado de
    verdade antes de salvar."""
    c = resolver(cor) if cor is not None else da_ficha()
    k = (c["temperatura"] - 6500) / 3500.0          # -1 frio .. +1 quente
    return " ".join([
        f"contrast({c['contraste']:.3f})",
        f"saturate({c['saturacao']:.3f})",
        f"brightness({(1 + c['brilho']) * (2 - c['gama']) ** 0.5:.3f})",
        f"sepia({max(0, k) * 0.35:.3f})",
        f"hue-rotate({(-k * 8 + c['tonalidade'] * 40):.1f}deg)",
    ])


def resumo(cor=None):
    """Uma linha para o log: so o que difere da grade de fabrica, para o editor
    ver na hora se a preferencia dele pegou ou se rodou no padrao."""
    c = resolver(cor) if cor is not None else da_ficha()
    mexidos = [f"{k} {c[k]:g}" for k in COR_PADRAO if not _quase(c[k], COR_PADRAO[k], 1e-3)]
    return " · ".join(mexidos) if mexidos else "de fabrica"


def main():
    import argparse
    p = argparse.ArgumentParser(description="grade de cor do A-roll")
    p.add_argument("--guia", help="guia.json (le guia.cor)")
    p.add_argument("--salvar", help="JSON com a ficha de cor, para virar preferencia do canal")
    p.add_argument("--nota", default="", help="por que esta grade foi escolhida")
    p.add_argument("--mostrar", action="store_true", help="imprime a ficha e o filtro")
    a = p.parse_args()

    if a.salvar:
        ficha = json.loads(Path(a.salvar).read_text(encoding="utf-8"))
        onde = gravar_preferencia(ficha.get("cor", ficha), nota=a.nota)
        print(f"preferencia do canal gravada em {onde}")

    guia = json.loads(Path(a.guia).read_text(encoding="utf-8")) if a.guia else None
    cor = da_ficha(guia)
    print(json.dumps(cor, ensure_ascii=False, indent=2))
    print(f"\nffmpeg -vf \"{filtro(cor)}\"")
    if os.environ.get("BEDITOR_CSS"):
        print(f"css: {css(cor)}")


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
