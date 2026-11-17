#!/usr/bin/env python3
"""legenda_hf.py — a legenda e o hook desenhados em HyperFrames, com alpha.

Antes a legenda era Pillow escrevendo PNG quadro a quadro, com contorno preto de
4 px e a fonte carregada por caminho de arquivo — quando a pasta `public/fontes`
nao existia, o Pillow caia na bitmap padrao e a tipografia morria sem avisar.

Aqui a camada inteira e uma composicao HTML: fonte web, kerning, sombra macia,
entrada por grupo. Sai como WebM com transparencia (VP9/yuva420p), que o
`compor.finalizar` ja sabe sobrepor no lugar do antigo `legenda.mov`.

O hook e a mesma camada: as linhas grandes que abrem o video, escalonadas, na
cor da casa. Ele nao e motion graphics — nao entra no guia, nao ocupa momento,
nao interrompe o rosto. E tipografia por cima da primeira fala.

A tipografia do hook e da legenda vem da galeria de estilos (`estilos.py`):
`guia.estilos.hook` / `guia.estilos.legenda` escolhem o id, e o padrao da casa
e `vox` (`referencias/galeria-estilos.md`).

Uso: legenda_hf.py --projeto edicao/motion [--saida out/legenda.webm]
"""
import argparse, hashlib, html, json, os, shutil, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import compor, estilos  # noqa: E402  (compor reaproveita o agrupamento de frases)

FPS = 30
OFICINA = Path.home() / ".beditor" / "render" / "_legenda"

FONTES = ("https://fonts.googleapis.com/css2?"
          "family=Archivo+Black&"
          "family=Fraunces:opsz,wght,SOFT,WONK@9..144,600..700,0,0&"
          "family=Inter:wght@700;900&"
          "family=Montserrat:wght@600;700;800&display=swap")

DESCENDENTES = set("gjpqyçQ")


def _e(t):
    return html.escape(str(t), quote=True)


def _sombra(spec, s):
    """`spec` e (dy, blur, alpha) em px na escala 1920, ou uma LISTA dessas
    triplas — `s` reescala pra H real.

    Duas camadas existem porque legenda sem barra precisa aguentar fundo claro
    e fundo escuro no mesmo video (pedido do dono em 2026-09-12: "nao use essas
    barras pretas nas legendas, use apenas sombra"). Uma sombra so nunca resolve
    as duas: a de contato (dy pequeno, blur pequeno) da o piso da letra e morre
    sobre branco; o halo (dy 0, blur largo) escurece o fundo em volta do glifo e
    sozinho borra a letra. Empilhadas, a de contato define a forma e o halo
    separa do fundo.

    `dy` 0 e valido — e o que faz o halo ficar concentrico em vez de cair pra um
    lado. Por isso o piso aqui e 0, nao 1."""
    if not spec:
        return ""
    camadas = spec if isinstance(spec, (list, tuple)) and isinstance(spec[0], (list, tuple)) else [spec]
    partes = [f"0 {max(0, int(dy * s))}px {max(1, int(blur * s))}px rgba(0,0,0,{alpha})"
              for dy, blur, alpha in camadas]
    return f"text-shadow:{','.join(partes)};"


# legenda: distancia entre a linha da boca e o topo da legenda, e o ponto mais
# baixo onde ela ainda fica acima da faixa que o TikTok/Reels cobrem embaixo
FOLGA_BOCA = 0.035
TOPO_MAX_LEGENDA = 0.80


def boca_pct(rosto_json):
    """altura da boca (fracao do quadro, a partir do topo) no video inteiro, a
    partir do `rosto.json` do rastreamento. A caixa do Vision vai da testa a
    abaixo do queixo; a boca fica em ~79% dela (medido no 20, 2026-09-27).
    Usa o percentil 75: a legenda tem que passar por baixo da boca na maior
    parte do video, nao so na media."""
    try:
        r = json.loads(Path(rosto_json).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    bocas = sorted(a["top"] + 0.79 * (a["bottom"] - a["top"]) for a in r
                   if a.get("confidence", 1) > 0.5 and "top" in a and "bottom" in a)
    if len(bocas) < 10:
        return None
    return round(bocas[int(0.75 * (len(bocas) - 1))], 3)


# topo do bloco do hook: abaixo dos ~160 px que o TikTok e o Reels cobrem com a
# propria interface, e o bloco termina no maximo em 1/3 da altura
HK_TOPO = 0.09


def _hook_html(hook, W, H, tok):
    """as linhas grandes da abertura, no estilo escolhido em `tok` (uma entrada
    de `estilos.HOOK`). Corpo fixo em % da largura — a linha so encolhe se nao
    couber; cada uma e uma so (`nowrap`), porque quebra automatica aqui e
    desastre ('Como fazer' virou 'Como' em cima de 'fazer').

    `hook.destaque` e o indice da linha em destaque (padrao: a primeira, quando
    ha mais de uma; `null` deixa todas na cor normal)."""
    linhas = [str(L).strip() for L in (hook.get("linhas") or []) if str(L).strip()]
    if not linhas:
        return "", ""
    # caixa alta pesada (Archivo Black/Inter 900) e mais larga por glifo, e a
    # barra de fundo ainda come ~meio caractere de cada lado — por isso a
    # margem util encolhe e o comprimento ganha uma folga extra so pra ela
    maiusc = tok["maiusculas"]
    util = W * (0.82 if maiusc else 0.88)
    largura_glifo = 0.66 if maiusc else 0.54
    folga_barra = 1 if maiusc else 0
    destaque = hook.get("destaque", 0 if len(linhas) > 1 else None)
    # O bloco inteiro mora no TERCO SUPERIOR — pedido do dono em 2026-09-27:
    # "o hook visual nao tem que ficar na frente da minha cara, tem que ficar no
    # terco superior da tela". Tres linhas no corpo cheio desciam ate ~47% da
    # altura, em cima do rosto. Do topo do bloco (HK_TOPO) ate 1/3 da altura
    # cabe o que cabe; se nao couber, TODAS as linhas encolhem na mesma
    # proporcao (a diferenca apoio:destaque e o que faz o hook, entao ela fica).
    tamanhos = []
    for i, L in enumerate(linhas):
        dest = destaque is not None and i == int(destaque)
        alvo = W * tok["corpo_pct"] * (tok["destaque_escala"] if dest else 1)
        cabe = util / max(1, (len(L) + folga_barra) * largura_glifo)
        tamanhos.append(min(alvo, cabe))
    altura_util = H * (1 / 3 - HK_TOPO)
    altura_bloco = sum(tamanhos) * max(1.0, tok["entrelinha"]) * 1.06
    reduz = min(1.0, altura_util / max(1, altura_bloco))
    corpo = []
    for i, L in enumerate(linhas):
        dest = destaque is not None and i == int(destaque)
        # O hook e CENTRALIZADO — pedido do dono em 2026-09-12. O desalinho por
        # linha (o `recuo` escalonado que existia aqui) so faz sentido em bloco
        # alinhado a esquerda; com as linhas centradas ele vira torto, nao
        # composto. Zero recuo, e a largura util volta a ser a margem inteira.
        recuo = 0.0
        tam = int(tamanhos[i] * reduz)
        # entrelinha apertada so funciona se a linha de cima nao tem perna
        # descendo; se tem ('pov:', 'guia'), a de baixo desce o que falta
        folga = 0.14 if i and tok["entrelinha"] < 1 and DESCENDENTES & set(linhas[i - 1]) else 0.0
        # (o desalinho e proposital: as linhas nunca partem da mesma margem)
        classe = "hk dest" if dest else "hk"
        corpo.append(f'<div class="{classe}" id="hk{i}" '
                     f'style="font-size:{tam}px;margin-left:{recuo * 100:.0f}%;'
                     f'margin-top:{folga:.2f}em"><span class="chip">{_e(L)}</span></div>')
    corpo = ['<div class="hkwrap">'] + corpo + ["</div>"]
    fim = float(hook.get("ateMs") or 3800) / 1000
    ent, sai = tok["entrada_dur"], tok["saida_dur"]
    js = [f"var HK_FIM={fim:.2f};"]
    for i in range(len(linhas)):
        t = 0.10 + i * (ent + 0.06)
        js.append(
            f"tl.fromTo('#hk{i}',{{opacity:0,yPercent:26,scale:0.9}},"
            f"{{opacity:1,yPercent:0,scale:1,duration:{ent:.2f},"
            f"ease:'{tok['entrada_ease']}'}},{t:.2f});")
        js.append(
            f"tl.to('#hk{i}',{{opacity:0,yPercent:-14,duration:{sai:.2f},"
            f"ease:'{tok['saida_ease']}'}},HK_FIM+{i * 0.06:.2f});")
    return "\n".join(corpo), "\n".join(js)


def html_legenda(grupos, hook, W, H, dur, guia=None):
    """`guia` e o `guia.json` inteiro (so pra ler `guia.estilos.hook` e
    `guia.estilos.legenda` — a galeria em `estilos.py`; sem escolha, o padrao
    da casa e `vox`)."""
    s = H / 1920
    hk = estilos.tokens(guia, "hook")
    lg = estilos.tokens(guia, "legenda")
    cfg = (guia or {}).get("configLegenda") or {}
    # A posição pode ser ajustada por vídeo sem deslocar projetos antigos.
    # Os limites mantêm o texto dentro da zona segura de Reels/TikTok.
    # Sem `topoPct` no guia, a legenda senta LOGO ABAIXO DA BOCA, medida no
    # rastreamento do rosto (`bocaPct`, ver `boca_pct`). Pedido do dono em
    # 2026-09-27: "a legenda ficou na frente da minha boca, eu gostaria que
    # ficasse um pouco abaixo da minha boca [...] as legendas nao devem se mover
    # com o tracking". Por isso e UMA altura para o video inteiro, nao uma por
    # quadro. Sem rastreamento, 0.62 (0.70 ficava "muito embaixo").
    padrao = 0.62
    if (guia or {}).get("bocaPct"):
        padrao = float(guia["bocaPct"]) + FOLGA_BOCA
    topo_pct = max(0.35, min(TOPO_MAX_LEGENDA, float(cfg.get("topoPct", padrao))))
    # 0.78: a coluna de botoes do TikTok/Reels ocupa a direita da tela; com 0.88
    # a ponta da linha passava por baixo dela (dono, 2026-09-27)
    largura_pct = max(0.60, min(0.92, float(cfg.get("maxLarguraPct", 0.78))))
    blocos, js = [], []
    for i, (t0, t1, texto) in enumerate(grupos):
        blocos.append(f'<div class="lg" id="lg{i}"><span class="chip">{_e(texto)}</span></div>')
        a, b = t0 / 1000, t1 / 1000
        # Todas as legendas ocupam o MESMO lugar na tela. Se uma ainda esta
        # saindo quando a proxima entra, as duas se sobrepoem e viram borrao
        # ilegivel — aconteceu. O fim de cada grupo e cortado no comeco do
        # seguinte, com uma folga de dois quadros para a troca nao piscar.
        if i + 1 < len(grupos):
            b = min(b, grupos[i + 1][0] / 1000 - 2 / FPS)
        b = max(b, a + 0.1)
        js.append(f"tl.fromTo('#lg{i}',{{opacity:0,scale:0.965,yPercent:10}},"
                  f"{{opacity:1,scale:1,yPercent:0,duration:{lg['entrada_dur']:.2f},"
                  f"ease:'{lg['entrada_ease']}'}},{a:.3f});")
        js.append(f"tl.to('#lg{i}',{{opacity:0,duration:0.08,ease:'none'}},{b:.3f});")
    hk_html, hk_js = _hook_html(hook or {}, W, H, hk)

    hk_eixos = f"font-variation-settings:{hk['eixos']};" if hk["eixos"] else ""
    hk_maiusc = "text-transform:uppercase;" if hk["maiusculas"] else ""
    hk_chip = (f"background:{hk['barra_normal']};padding:0.08em 0.22em;"
               f"border-radius:0.06em;" if hk["barra_normal"] else "")
    hk_chip_dest = (f"background:{hk['barra_destaque']};padding:0.08em 0.22em;"
                    f"border-radius:0.06em;" if hk["barra_destaque"] else "")
    lg_maiusc = "text-transform:uppercase;" if lg["maiusculas"] else ""
    lg_chip = (f"background:{lg['barra']};padding:0.16em 0.4em;border-radius:0.1em;"
               if lg["barra"] else "")

    return f"""<!doctype html>
<html lang="pt-BR" data-resolution="portrait">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width={W}, height={H}"/>
<title>legenda e hook</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTES}" rel="stylesheet">
<style>
  *{{margin:0;padding:0;box-sizing:border-box}}
  /* fundo transparente: esta camada existe para ser sobreposta ao A-roll */
  html,body{{width:{W}px;height:{H}px;overflow:hidden;background:transparent}}
  #root{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:transparent}}
  .lg{{position:absolute;left:0;right:0;top:{topo_pct * 100:.1f}%;display:flex;justify-content:center;opacity:0}}
  /* sem barra, o `padding` do chip some e a linha passa a encostar na borda —
     o max-width devolve a margem que a barra dava de graca */
  .lg .chip{{{lg_maiusc}max-width:{largura_pct * 100:.1f}%;
    font-family:{lg['fonte']};font-weight:{lg['peso']};
    font-size:{max(10, int(H * lg['tamanho_pct']))}px;line-height:1.18;
    letter-spacing:{lg['tracking']};text-align:center;color:{lg['cor_texto']};
    {lg_chip}{_sombra(lg['sombra'], s)}}}
  /* o hook da abertura: coluna, para as linhas nunca se montarem umas nas
     outras — cada uma cresce ate a margem e nenhuma quebra */
  /* o topo sai de HK_TOPO (abaixo da interface do TikTok/Reels) e o bloco
     termina no maximo em 1/3 da altura, acima do rosto — ver _hook_html */
  .hkwrap{{position:absolute;left:4%;right:4%;top:{HK_TOPO * 100:.0f}%;display:flex;
    flex-direction:column;align-items:center;text-align:center}}
  .hk{{opacity:0;white-space:nowrap;
    font-family:{hk['fonte']};font-weight:{hk['peso']};{hk_eixos}{hk_maiusc}
    line-height:{hk['entrelinha']};letter-spacing:{hk['tracking']};color:{hk['cor_texto']}}}
  .hk .chip{{{hk_chip}{_sombra(hk['sombra'], s)}}}
  .hk.dest{{color:{hk['cor_destaque_texto']}}}
  .hk.dest .chip{{{hk_chip_dest}}}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{dur:.3f}"
     data-width="{W}" data-height="{H}" data-fps="{FPS}">
{hk_html}
{chr(10).join(blocos)}
</div>
<script>
  var DUR = {dur:.3f};
  window.__timelines = window.__timelines || {{}};
  var tl = gsap.timeline({{paused:true}});
  window.__timelines["main"] = tl;
{hk_js}
{chr(10).join(js)}
  tl.to({{}}, {{duration:DUR}}, 0);
</script>
</body>
</html>
"""


def render(projeto, saida=None, escala=1.0, resolucao=None, so_hook=False):
    """`so_hook` desenha SO o gancho da abertura, sem a legenda palavra a palavra.

    E o que a etapa `motion` usa. O hook e a coisa mais importante do video e
    ficava invisivel ate o `finalizar`, duas etapas depois: o editor aprovava o
    motion sem nunca ter visto a abertura que o publico vai ver. Pedido do dono
    em 2026-09-12: *"o hook visual deve ser apenas com texto, e eu tenho que
    aparecer no inicio"* — decisao que so da para tomar vendo."""
    projeto = Path(projeto)
    plano = json.loads((projeto / "plano.json").read_text(encoding="utf-8"))
    captions = json.loads((projeto / "public" / "captions.json").read_text(encoding="utf-8"))
    W, H = int(plano["largura"] * escala), int(plano["altura"] * escala)
    dur = plano["duracaoMs"] / 1000
    grupos = [] if so_hook else compor.grupos_legenda(plano, captions)
    pagina = html_legenda(
        grupos, plano.get("hook"), W, H, dur,
        guia={
            "estilos": plano.get("estilos"),
            "configLegenda": plano.get("configLegenda"),
            "bocaPct": boca_pct(projeto / "out" / "rosto.json"),
        },
    )

    destino = Path(saida) if saida else projeto / "out" / "legenda.webm"
    destino.parent.mkdir(parents=True, exist_ok=True)
    # o webm e funcao pura da pagina + resolucao: se nada disso mudou (so o
    # zoom, o corte de imagem ou a grade mudaram), o de antes serve inteiro
    impressao = hashlib.sha256(f"{resolucao}\n{pagina}".encode("utf-8")).hexdigest()
    marca = destino.with_name(destino.name + ".sha256")
    if destino.exists() and marca.exists() and marca.read_text().strip() == impressao:
        print(f"{'hook' if so_hook else 'legenda'}: reaproveitada, nada mudou ({destino.name})",
              flush=True)
        return destino
    marca.unlink(missing_ok=True)

    # o hyperframes trava em caminho com parenteses ou acento (ver hf.py)
    if OFICINA.exists():
        shutil.rmtree(OFICINA)
    # ~/.beditor/render costuma ser link para o SSD. Se o destino sumiu (disco
    # remontado, pasta limpa), o mkdir tropeca no link quebrado com um
    # FileExistsError que nao diz nada. Recria o destino do link.
    base = OFICINA.parent
    if base.is_symlink() and not base.exists():
        Path(base.readlink()).mkdir(parents=True, exist_ok=True)
    OFICINA.mkdir(parents=True)
    (OFICINA / "index.html").write_text(pagina, encoding="utf-8")

    (destino.parent / "legenda.html").write_text(pagina, encoding="utf-8")  # para inspecao
    # versão fixa do CLI (HeyGen); BEDITOR_HYPERFRAMES troca, por exemplo "hyperframes@0.9.60"
    hyperframes = os.environ.get("BEDITOR_HYPERFRAMES", "hyperframes@0.9.58")
    cmd = ["npx", "--yes", hyperframes, "render", "--format", "webm", "-o", "legenda.webm", "--quiet"]
    if resolucao:
        # a composicao continua em 1080x1920; o Chrome desenha num DPR maior e o
        # quadro sai na resolucao pedida. Texto vetorial fica nitido, e custa
        # muito menos que montar a pagina inteira em 4K.
        #
        # `--low-memory-mode` nao e paranoia: em 4K o modo normal grava cada
        # quadro em disco antes de codificar, e uma legenda de dois minutos pede
        # ~124 GB de temporario. Em streaming ele passa quadro a quadro para o
        # codificador. Custa tempo (um worker so) e cabe em qualquer disco.
        cmd += ["--resolution", resolucao, "--low-memory-mode"]
    print(("hook: só o gancho da abertura, alpha em WebM" if so_hook else
           f"legenda: {len(grupos)} grupo(s), {dur:.1f}s, alpha em WebM")
          + (f", saida {resolucao}" if resolucao else ""), flush=True)
    r = subprocess.run(cmd, cwd=OFICINA, capture_output=True, text=True, timeout=7200, encoding="utf-8", errors="replace")
    feito = OFICINA / "legenda.webm"
    if r.returncode != 0 or not feito.exists():
        raise RuntimeError(f"hyperframes falhou na legenda\n{r.stdout[-1200:]}{r.stderr[-1200:]}")
    destino.write_bytes(feito.read_bytes())
    marca.write_text(impressao)
    shutil.rmtree(OFICINA, ignore_errors=True)
    print(f"pronto: {destino} ({destino.stat().st_size // 1024} KB)")
    return destino


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projeto", required=True)
    ap.add_argument("--saida")
    ap.add_argument("--escala", type=float, default=1.0)
    ap.add_argument("--resolucao", help="preset do hyperframes (ex: portrait-4k) — "
                                        "a pagina e desenhada em DPR maior e o quadro sai "
                                        "maior, sem redesenhar a composicao")
    ap.add_argument("--so-html", action="store_true")
    ap.add_argument("--so-hook", action="store_true",
                    help="desenha só o gancho da abertura, sem a legenda "
                         "palavra a palavra (é o que a etapa motion usa)")
    a = ap.parse_args()
    if a.so_html:
        projeto = Path(a.projeto)
        plano = json.loads((projeto / "plano.json").read_text(encoding="utf-8"))
        captions = json.loads((projeto / "public" / "captions.json").read_text(encoding="utf-8"))
        W, H = int(plano["largura"] * a.escala), int(plano["altura"] * a.escala)
        grupos = compor.grupos_legenda(plano, captions)
        destino = projeto / "out" / "legenda.html"
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(html_legenda(grupos, plano.get("hook"), W, H,
                                        plano["duracaoMs"] / 1000,
                                        guia={"estilos": plano.get("estilos"),
                                              "configLegenda": plano.get("configLegenda"),
                                              "bocaPct": boca_pct(projeto / "out" / "rosto.json")}),
                           encoding="utf-8")
        print(f"html: {destino}")
        return
    render(a.projeto, a.saida, a.escala, a.resolucao, a.so_hook)


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
