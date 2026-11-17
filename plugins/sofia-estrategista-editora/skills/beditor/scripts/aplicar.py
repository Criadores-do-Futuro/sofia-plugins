#!/usr/bin/env python3
"""
aplicar.py — funde o enriquecimento no plano.json, validando direitos.

O agente enriquecedor devolve um JSON com pesquisa real (ficha de paper, ficha de
pessoa, ideias e prompts). Este script aplica esse JSON sobre o plano, campo a
campo, e RECUSA o que viola as regras de referencias/enriquecimento.md:

  - retrato com status "encontrado" mas sem licenca  -> vira "sem-imagem-livre"
  - mais de uma citacao no video inteiro             -> mantem a primeira
  - paper sem titulo                                  -> plano volta ao tipo anterior

Uso:  aplicar.py --projeto motion/ --enriquecimento enriquecimento.json
"""
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import travas  # noqa: E402

TEM_TEXTO_PROPRIO = travas.TEM_TEXTO_PROPRIO
# Classes que so se justificam com uma ideia visual escrita. Sem ideia, viram
# figura generica parada — e o vídeo original faz melhor esse trabalho.
SEM_IDEIA_VOLTA_PARA_FALA = {"personagem", "objeto", "broll", "cotidiano", "hibrido"}

MIN_GRAFICO_MS = 2500   # abaixo disso o grafico pisca em vez de comunicar
MIN_VIZINHO_MS = 1400   # o que sobra para o plano ao lado nunca fica menor

CAMPOS = ("tipo", "texto", "ideia", "movimento", "prompt", "camera", "entrada", "saida",
          "palavras", "paper", "retrato", "serie", "curva", "conversa", "apagarMeio",
          "tela", "fonte", "licenca")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projeto", required=True)
    ap.add_argument("--enriquecimento", required=True)
    a = ap.parse_args()

    raiz = Path(a.projeto)
    arq = raiz / "plano.json"
    plano = json.loads(arq.read_text(encoding="utf-8"))
    enr = json.loads(Path(a.enriquecimento).read_text(encoding="utf-8"))

    por_id = {p["id"]: p for p in enr.get("planos", [])}
    avisos, citacoes = [], 0
    tem_video = bool(plano.get("fonteVideo"))

    for p in plano["planos"]:
        novo = por_id.get(p["id"])
        if not novo:
            continue
        anterior = p["tipo"]

        for c in CAMPOS:
            if c in novo and novo[c] not in (None, ""):
                p[c] = novo[c]

        # paper sem ficha nao e paper
        if p["tipo"] == "paper":
            d = p.get("paper") or {}
            if not d.get("titulo"):
                p["tipo"] = anterior if anterior != "paper" else "objeto"
                p.pop("paper", None)
                avisos.append(f"{p['id']}: paper sem titulo — voltou para `{p['tipo']}`")
            else:
                if d.get("citacao"):
                    citacoes += 1
                    if citacoes > 1:
                        d["citacao"] = ""
                        avisos.append(f"{p['id']}: segunda citacao removida — uma por video")
                if d.get("verificado") is False:
                    avisos.append(f"{p['id']}: ficha marcada como NAO verificada — confira antes de publicar")

        # retrato sem licenca cai na ficha tipografica
        if p["tipo"] == "retrato":
            r = p.get("retrato") or {}
            if not r.get("nome"):
                p["tipo"] = anterior if anterior != "retrato" else "objeto"
                p.pop("retrato", None)
                avisos.append(f"{p['id']}: retrato sem nome — voltou para `{p['tipo']}`")
            elif r.get("status") == "encontrado" and not (r.get("licenca") and r.get("imagemUrl")):
                r["status"] = "sem-imagem-livre"
                avisos.append(f"{p['id']}: retrato sem licenca ou sem URL — cai na ficha tipografica")
            elif r.get("status") == "sem-imagem-livre":
                avisos.append(f"{p['id']}: sem imagem livre de {r['nome']} — ficha tipografica (nenhum rosto foi gerado)")

        # O enriquecedor tende a aninhar tudo, porque `paper` e `retrato` sao
        # objetos. `dado` nao e: serie/curva/fonte moram na raiz do plano.
        # Aceitar as duas formas evita perder o trabalho por causa do formato.
        aninhado = novo.get("dado")
        if isinstance(aninhado, dict):
            if aninhado.get("fonte") and not p.get("fonte", "").strip().startswith("Murdock"):
                p["fonte"] = aninhado["fonte"]
            if aninhado.get("serie") and not p.get("serie"):
                p["serie"] = aninhado["serie"]
            if aninhado.get("curva") and not p.get("curva"):
                p["curva"] = aninhado["curva"]

        # Grafico sem numero nao e grafico. O componente ja se recusa a desenhar,
        # mas recusar em tela e pior do que nao ter escolhido `dado`: vira um
        # cartao de erro no meio do video.
        if p["tipo"] == "dado" and not (p.get("serie") or p.get("curva")):
            p["tipo"] = "fala" if tem_video else "cartela"
            fonte_ok = (p.get("fonte") or "").strip()
            if not fonte_ok or fonte_ok.startswith("TODO"):
                p["fonte"] = ""
            avisos.append(f"{p['id']}: `dado` sem serie nem curva — virou `{p['tipo']}`. "
                          f"Um numero solto nao e grafico.")

        # Uma `tela` sem interface descrita cai no cartao generico: uma janela
        # quase vazia, quase da cor do fundo, que o espectador le como tela
        # preta. Interface e o que a fala NAO diz — sem esse conteudo, o vídeo
        # original ilustra melhor.
        if p["tipo"] == "tela" and not (p.get("tela") or p.get("conversa")):
            p["tipo"] = "fala" if tem_video else "cartela"
            avisos.append(f"{p['id']}: `tela` sem `tela.modo` nem `conversa` — "
                          f"virou `{p['tipo']}`. Janela vazia e tela preta.")

        # palavras sem lista nao e palavras
        if p["tipo"] == "palavras" and not p.get("palavras"):
            p["tipo"] = tem_video and "fala" or "cartela"
            avisos.append(f"{p['id']}: plano `palavras` sem lista — virou `{p['tipo']}`")

        # onde o quadro ja tem texto, a legenda cala
        p["legenda"] = p["tipo"] not in TEM_TEXTO_PROPRIO

    # Motion graphics sem ideia visual e pior do que nao ter motion graphics:
    # uma figura generica parada rouba o plano de quem esta falando. Havendo
    # material filmado, esses planos voltam para o vídeo original.
    if tem_video:
        for p in plano["planos"]:
            if p["tipo"] not in SEM_IDEIA_VOLTA_PARA_FALA:
                continue
            if (p.get("ideia") or "").strip() or (p.get("movimento") or "").strip():
                continue
            p["tipo"] = "fala"
            p["asset"] = None
            p["prompt"] = ""
            p["legenda"] = True
            avisos.append(f"{p['id']}: sem ideia nem movimento — voltou para o vídeo original")

    for p in plano["planos"]:
        p.setdefault("legenda", p["tipo"] not in TEM_TEXTO_PROPRIO)

    # As invariantes de plano (buraco, tela sem interface, palavra repetida,
    # palavras vazio, grafico curto) moram em travas.py — o mesmo codigo que
    # o montar.py usa. Uma licao, um lugar.
    avisos += travas.aplicar_todas(plano)

    if enr.get("observacoes"):
        plano["observacoes"] = enr["observacoes"]

    saida = json.dumps(plano, ensure_ascii=False, indent=2)
    arq.write_text(saida, encoding="utf-8")
    pub = raiz / "public" / "plano.json"
    if pub.parent.exists():
        pub.write_text(saida, encoding="utf-8")

    from collections import Counter
    print(f"{len(por_id)} plano(s) enriquecido(s)")
    for t, n in Counter(p["tipo"] for p in plano["planos"]).most_common():
        print(f"  {t:<12} {n}")
    cartelas = sum(1 for p in plano["planos"] if p["tipo"] == "cartela")
    if cartelas > 3:
        avisos.append(f"{cartelas} cartelas no video — o limite e 3. Isso e slide com grao, nao motion.")
    parados = [p["id"] for p in plano["planos"]
               if not p.get("movimento") and p["tipo"] not in ("palavras", "fala")]
    if parados:
        avisos.append("sem campo `movimento`: " + ", ".join(parados))
    mudos = sum(1 for p in plano["planos"] if not p.get("legenda", True))
    print(f"legenda calada em {mudos} de {len(plano['planos'])} planos (quadro ja tem texto)")
    if avisos:
        print("\navisos:")
        for w in avisos:
            print("  ·", w)
    if plano.get("observacoes"):
        print("\nobservacoes do enriquecedor:\n  " + plano["observacoes"].replace("\n", "\n  "))

if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
