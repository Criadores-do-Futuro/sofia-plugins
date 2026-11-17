#!/usr/bin/env python3
"""
assets.py — resolve os assets do plano.json pela rota de cada tipo.

Rotas (referencias/ferramentas.md):
  cartela, dado, tela        codigo — nada a gerar, o Remotion desenha
  objeto, personagem, obra   imagem — Gemini se houver GEMINI_API_KEY
  arquivo                    acervo — so lista o que falta licenciar
  broll, hibrido, tvcrt      video  — fora do escopo automatico
  cotidiano, pessoa          filmar — nao se gera

Sem GEMINI_API_KEY o script NAO falha: escreve PROMPTS.md com os prompts prontos.
"""
import argparse, base64, json, mimetypes, os, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import estilos  # noqa: E402

MODELO = os.environ.get("BEDITOR_MODELO_IMAGEM", "gemini-2.5-flash-image")
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent"

# A grade da imagem e DO ESTILO, nao deste script. Ate 2026-09-12 havia aqui um
# bloco fixo, escrito para o `noturno`, colado depois da materia de QUALQUER
# estilo — e o prompt saia se contradizendo: "colagem de papel recortado sobre
# creme" e, logo abaixo, "pretos em 12/255, rim light ambar e ciano, vinheta
# pesada, cinematic, lonely". O gerador obedece o final. Foi assim que M02, M03
# e M08 sairam noir no meio de um video de papel. Agora cada estilo traz a sua.
GRADE = estilos.MOTION["noturno"]["grade"]
GRADE_ATUAL = GRADE          # main() troca pela grade do estilo do plano

# o Remotion desenha: texto, numero, interface e tipografia cinetica
CODIGO  = {"fala", "cartela", "dado", "tela", "palavras", "paper"}
IMAGEM  = {"objeto", "personagem", "obra", "arquivo"}
FILMAR  = {"cotidiano", "pessoa"}
VIDEO   = {"broll", "hibrido", "tvcrt"}
# rosto de pessoa real: licencia-se uma foto, nunca se gera uma parecida
RETRATO = {"retrato"}

def prompt_final(p):
    base = (p.get("prompt") or "").strip()
    if base.startswith("TODO"):
        base = base[5:].strip(": ")
    return f"{base}\n\n{GRADE_ATUAL}"

def gerar(prompt, destino, chave):
    corpo = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    req = urllib.request.Request(
        ENDPOINT.format(m=MODELO),
        data=corpo,
        headers={"Content-Type": "application/json", "x-goog-api-key": chave},
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        dados = json.load(r)
    for cand in dados.get("candidates", []):
        for parte in cand.get("content", {}).get("parts", []):
            inline = parte.get("inlineData") or parte.get("inline_data")
            if inline and inline.get("data"):
                destino.write_bytes(base64.b64decode(inline["data"]))
                return True
    return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projeto", required=True)
    ap.add_argument("--so", default="", help="gerar so um plano (ex: P03)")
    ap.add_argument("--forcar", action="store_true", help="regerar assets que ja existem")
    # geracao de imagem e espera de rede, nao trabalho de CPU: cabe mais
    # simultaneo que o render. 6 e conservador para nao tomar 429 do gerador.
    ap.add_argument("--paralelo", type=int, default=6,
                    help="imagens geradas ao mesmo tempo (1 = uma a uma)")
    a = ap.parse_args()

    raiz = Path(a.projeto)
    arq = raiz / "plano.json"
    plano = json.loads(arq.read_text(encoding="utf-8"))
    global GRADE_ATUAL
    escolhido = estilos.escolher(plano, "motion")
    GRADE_ATUAL = (estilos.MOTION.get(escolhido) or {}).get("grade") or GRADE
    print(f"assets: grade de imagem do estilo `{escolhido}`", flush=True)
    destino = raiz / "public" / "assets"
    destino.mkdir(parents=True, exist_ok=True)
    chave = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    prompts, pendencias, gerados = [], [], 0
    a_gerar = []            # o que de fato vai ao gerador, decidido no laco abaixo
    for p in plano["planos"]:
        tipo = p["tipo"]
        if tipo in CODIGO:
            continue
        if tipo in FILMAR:
            pendencias.append(f"- **{p['id']}** `{tipo}` — filmar. {p['fala'][:70]}")
            continue
        if tipo in VIDEO:
            pendencias.append(f"- **{p['id']}** `{tipo}` — vídeo generativo ou acervo. {p['fala'][:70]}")
            prompts.append((p, prompt_final(p)))
            continue
        if tipo in RETRATO:
            lic = (p.get("licenca") or "").strip()
            if not lic or lic.startswith("TODO"):
                pendencias.append(
                    f"- **{p['id']}** `retrato` — foto de pessoa real. Não se gera: "
                    f"licencie a imagem e salve em `public/assets/{p['id']}.png`, "
                    f"ou deixe a ficha tipográfica desenhar sozinha.")
            continue
        if tipo == "arquivo" or tipo == "obra":
            lic = (p.get("licenca") or "").strip()
            if not lic or lic.startswith("TODO"):
                pendencias.append(f"- **{p['id']}** `{tipo}` — licença não registrada. Não entra no vídeo até registrar.")

        alvo = destino / f"{p['id']}.png"
        prompts.append((p, prompt_final(p)))
        if a.so and p["id"] != a.so:
            continue
        # A imagem so e reaproveitada se foi gerada para ESTE prompt. O id
        # (M34) sobrevive a uma nova direcao, a ideia nao: sem esta trava, um
        # espelho de outra direcao entra no lugar das duas portas de hoje.
        # Imagem licenciada (obra, arquivo) nunca e regerada. Imagem gerada
        # sem registro de prompt (anterior a esta trava) conta como velha.
        marca = alvo.with_suffix(".prompt.txt")
        mesmo_prompt = marca.exists() and marca.read_text(encoding="utf-8") == prompt_final(p)
        licenciada = tipo in ("obra", "arquivo")
        if alvo.exists() and not a.forcar and (mesmo_prompt or licenciada or not chave):
            p["asset"] = f"assets/{alvo.name}"
            continue
        if alvo.exists() and not a.forcar:
            print(f"  {p['id']} imagem de outro prompt — regerando", file=sys.stderr)
        if not chave or tipo in VIDEO:
            continue
        # Prompt vazio nunca vai ao gerador: ele recebe so o sufixo de estilo
        # e inventa qualquer coisa (um esqueleto no lugar de dez paineis de
        # papel). Sem ideia escrita, o plano volta para o vídeo original.
        if not (p.get("prompt") or "").strip():
            print(f"  {p['id']} sem prompt — nao gerado", file=sys.stderr)
            continue
        a_gerar.append((p, tipo, alvo, marca))

    # As imagens sao geradas em paralelo. Cada uma e uma espera de rede de ate
    # 180 s (`gerar`) que nao disputa nada com as outras — em fila, um video de
    # 40 cenas passava a maior parte do tempo so esperando resposta. A decisao
    # de O QUE gerar continua sequencial ali em cima, com o reaproveitamento
    # intacto: aqui so sai o que ja foi decidido.
    if a_gerar:
        def _uma(item):
            p, _tipo, alvo, _marca = item
            prompt = prompt_final(p)
            return prompt, gerar(prompt, alvo, chave)

        paralelo = max(1, min(a.paralelo, len(a_gerar)))
        if len(a_gerar) > 1:
            print(f"gerando {len(a_gerar)} imagens, {paralelo} por vez")
        with ThreadPoolExecutor(max_workers=paralelo) as pool:
            tarefas = {pool.submit(_uma, i): i for i in a_gerar}
            for t in as_completed(tarefas):
                p, tipo, alvo, marca = tarefas[t]
                try:
                    prompt, ok = t.result()
                except Exception as e:
                    # uma imagem que falha nao derruba as outras; o plano fica
                    # sem asset e cai no tratamento de `caiu`, logo abaixo.
                    print(f"  {p['id']} falhou: {e}", file=sys.stderr)
                    continue
                if ok:
                    marca.write_text(prompt, encoding="utf-8")
                    p["asset"] = f"assets/{alvo.name}"
                    gerados += 1
                    print(f"  {p['id']} {tipo} → {alvo.name}", flush=True)
                else:
                    print(f"  {p['id']} sem imagem na resposta", file=sys.stderr)

    # Nenhum "asset pendente" chega na tela. Se no fim da geracao um plano que
    # depende de imagem continua sem imagem, ele volta para o vídeo original —
    # um cartao de placeholder e sempre pior do que o rosto de quem fala.
    if plano.get("fonteVideo"):
        caiu = []
        for p in plano["planos"]:
            # com --so, os outros planos nem foram tentados: nao se rebaixa
            # o que nao se tentou
            if a.so and p["id"] != a.so:
                continue
            if p["tipo"] in (IMAGEM | FILMAR | VIDEO) and not p.get("asset"):
                caiu.append(f"{p['id']} ({p['tipo']})")
                p["tipo"] = "fala"
                p["prompt"] = ""
                p["legenda"] = True
        if caiu:
            print(f"\n{len(caiu)} plano(s) sem imagem voltaram para o vídeo original:")
            print("  " + ", ".join(caiu))

    arq.write_text(json.dumps(plano, ensure_ascii=False, indent=2), encoding="utf-8")
    pub = raiz / "public" / "plano.json"
    if pub.parent.exists():
        pub.write_text(json.dumps(plano, ensure_ascii=False, indent=2), encoding="utf-8")

    linhas = ["# Prompts dos assets", ""]
    if not chave:
        linhas += ["> `GEMINI_API_KEY` não está no ambiente. Nada foi gerado — os prompts",
                   "> abaixo colam em qualquer gerador. Salve o resultado como",
                   "> `public/assets/<ID>.png` e o Remotion pega sozinho.", ""]
    for p, pr in prompts:
        linhas += [f"## {p['id']} · `{p['tipo']}`", "", f"> {p['fala']}", "", "```", pr, "```", ""]
    if pendencias:
        linhas += ["## Pendências", ""] + pendencias + [""]
    (raiz / "PROMPTS.md").write_text("\n".join(linhas), encoding="utf-8")

    print(f"\n{gerados} asset(s) gerado(s) · {len(prompts)} prompt(s) em {raiz/'PROMPTS.md'}")
    if pendencias:
        print(f"{len(pendencias)} pendência(s) — veja o fim do PROMPTS.md")

if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
