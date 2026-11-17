#!/usr/bin/env python3
"""
plano.py — transcript com timestamp -> plano.json + captions.json

Entrada aceita:
  .srt / .vtt                      legenda com tempo por bloco
  .json do Whisper                 words[] na raiz ou segments[].words[] (segundos)
  .json simples                    [{"text","startMs","endMs"}, ...]

Saída, dentro de --out:
  plano.json                       os planos, para você revisar e corrigir
  public/captions.json             Caption[] do @remotion/captions

O corte cai onde a voz respira. As regras de duração estão em referencias/ritmo.md;
este script as aplica, não as inventa.
"""
import argparse, json, os, re, sys
from pathlib import Path

# --- regras (referencias/ritmo.md) -----------------------------------------
RESPIRO_MS      = 180     # silencio que autoriza um corte
GANCHO_MS       = 1500    # o primeiro plano
MIN_MS          = 1200    # abaixo disso vira ruido
ALVO_MS         = 2400    # duracao de conforto
MAX_MS          = 3200    # acima disso arrasta
MAX_CLASSE_MS   = 4000    # a mesma classe nao passa disso seguida

# --- gatilhos por classe (referencias/catalogo-visual.md) -------------------
TEM_TEXTO_PROPRIO = {"cartela", "paper", "dado", "tela", "retrato"}

GATILHOS = [
    ("dado",      r"\b(\d{1,3}[.,]?\d*\s*%|por cento|em (19|20)\d{2}|\d+\s*(vezes|x)\b|pesquisa|estudo|dados?)\b"),
    ("arquivo",   r"\b(em (18|19)\d{2}|na época|antigamente|história|década|arquivo|registro)\b"),
    ("tela",      r"\b(app|aplicativo|tela|digita|clica|mensagem|chat|interface|botão|comando|/\w+)\b"),
    ("obra",      r"\b(arte|pintura|quadro|escultura|museu|clássic|renascen|barroc)\w*\b"),
    ("tvcrt",     r"\b(televisão|tv|desenho|infância|criança|passava na|lembrança)\b"),
    ("cotidiano", r"\b(pia|torneira|gaveta|porta|casa|cozinha|banho|café|cama|chave)\b"),
    ("pessoa",    r"\b(ele|ela|meu amigo|minha mãe|meu pai|essa pessoa|o cara)\b"),
    ("objeto",    r"\b(chave|muro|nó|peso|caixa|ponte|espelho|corda|bússola|relógio)\b"),
    ("broll",     r"\b(cidade|rua|noite|chuva|janela|estrada|silêncio|vazio)\b"),
    ("personagem",r"\b(você|sente|trava|evita|decide|medo|cansaç|sozinh|perde)\w*\b"),
]

# Gatilhos que casam com quase qualquer frase. Eles produzem o pior plano que
# existe: uma figura generica sem nada acontecendo. So valem quando NAO ha
# material filmado — com vídeo original, quem fala sustenta melhor o momento.
FRACOS = {"personagem", "broll"}

PADRAO = "cartela"        # sem vídeo original
PADRAO_COM_VIDEO = "fala" # com vídeo original: o padrao e a pessoa falando

def ms(t):  # "00:00:02,500" | "00:00:02.500"
    t = t.replace(",", ".")
    h, m, s = t.split(":")
    return int((int(h) * 3600 + int(m) * 60 + float(s)) * 1000)

def de_srt(texto):
    palavras = []
    blocos = re.split(r"\n\s*\n", texto.strip())
    for b in blocos:
        linhas = [l for l in b.strip().split("\n") if l.strip()]
        tempo = next((l for l in linhas if "-->" in l), None)
        if not tempo:
            continue
        ini, fim = [p.strip() for p in tempo.split("-->")[:2]]
        ini, fim = ms(ini), ms(fim.split()[0])
        fala = " ".join(l for l in linhas if "-->" not in l and not l.strip().isdigit())
        toks = fala.split()
        if not toks:
            continue
        passo = max(1, (fim - ini) // len(toks))
        for i, w in enumerate(toks):
            a = ini + i * passo
            palavras.append({"text": w, "startMs": a, "endMs": min(fim, a + passo)})
    return palavras

def de_json(dados):
    if isinstance(dados, list) and dados and "startMs" in dados[0]:
        return [{"text": d["text"].strip(), "startMs": int(d["startMs"]), "endMs": int(d["endMs"])} for d in dados]
    palavras = []
    segs = dados if isinstance(dados, list) else dados.get("segments", [])
    por_segmento = [w for seg in segs for w in seg.get("words", []) or []]
    # o transcrever.py grava as palavras na raiz e deixa os segmentos sem `words`
    soltas = [] if isinstance(dados, list) else dados.get("words", [])
    for w in por_segmento or soltas:
        t = (w.get("word") or w.get("text") or "").strip()
        if not t:
            continue
        palavras.append({"text": t,
                         "startMs": int(float(w["start"]) * 1000),
                         "endMs": int(float(w["end"]) * 1000)})
    return palavras

def carregar(caminho):
    bruto = Path(caminho).read_text(encoding="utf-8")
    if caminho.lower().endswith((".srt", ".vtt")):
        return de_srt(re.sub(r"^WEBVTT.*?\n\n", "", bruto, flags=re.S))
    return de_json(json.loads(bruto))

def juntas(palavras):
    """indices onde a voz respira, com o tamanho do silencio"""
    out = []
    for i in range(len(palavras) - 1):
        gap = palavras[i + 1]["startMs"] - palavras[i]["endMs"]
        if gap >= RESPIRO_MS:
            out.append((i, gap))
    return out

def fatiar(palavras):
    """corta em planos: preferindo respiro, respeitando MIN/ALVO/MAX"""
    respiros = {i: g for i, g in juntas(palavras)}
    planos, ini = [], 0
    t0_total = palavras[0]["startMs"]
    while ini < len(palavras):
        alvo = GANCHO_MS if not planos else ALVO_MS
        t0 = palavras[ini]["startMs"]
        melhor, melhor_custo = None, None
        for j in range(ini, len(palavras)):
            dur = palavras[j]["endMs"] - t0
            if dur < MIN_MS:
                continue
            if dur > MAX_MS and melhor is not None:
                break
            # custo: distancia do alvo, com desconto para respiro largo
            custo = abs(dur - alvo) - min(respiros.get(j, 0), 600) * 1.5
            if melhor_custo is None or custo < melhor_custo:
                melhor, melhor_custo = j, custo
        if melhor is None:
            melhor = len(palavras) - 1
        planos.append((ini, melhor))
        ini = melhor + 1
    return planos, t0_total

ANCORA = re.compile(
    r"\b(pesquisador\w*|cientista|estudo|paper|experimento|publicou|universidade|"
    r"instituto|em (18|19|20)\d{2}|segundo (o|a)\b)", re.I)

def classificar(texto, tem_video=False):
    baixo = texto.lower()
    for tipo, padrao in GATILHOS:
        if tem_video and tipo in FRACOS:
            continue
        if re.search(padrao, baixo):
            return tipo
    return PADRAO_COM_VIDEO if tem_video else PADRAO

def alternar(tipos, planos, palavras, tem_video=False):
    """
    Nenhuma classe seguida por mais de MAX_CLASSE_MS.

    `fala` esta fora desta regra. Ela existe para que o mesmo tipo de GRAFICO
    nao se repita ate cansar; quem fala pode falar dez segundos seguidos sem
    cansar ninguem. Aplicar o limite ao vídeo original so faz o script picar
    o rosto em imagem generica de 4 em 4 segundos — o oposto do que se quer.
    """
    acum, anterior = 0, None
    for k, (a, b) in enumerate(planos):
        dur = palavras[b]["endMs"] - palavras[a]["startMs"]
        if tipos[k] == "fala":
            acum, anterior = 0, "fala"
            continue
        if tipos[k] == anterior:
            acum += dur
            if acum > MAX_CLASSE_MS:
                if tem_video:
                    # a saida do excesso e voltar para quem fala, nao empilhar texto
                    tipos[k] = "fala" if anterior != "fala" else "objeto"
                else:
                    tipos[k] = "cartela" if anterior != "cartela" else "objeto"
                acum, anterior = dur, tipos[k]
        else:
            acum, anterior = dur, tipos[k]
    return tipos

FALA_MAX_MS = 5000  # ate onde um bloco de vídeo original vai sem ponto de escolha

def juntar_fala(tipos, cortes, palavras):
    """
    Planos `fala` seguidos sao trechos contiguos do MESMO vídeo: entre eles
    nao existe corte visivel, so uma fronteira no JSON. Juntar devolve blocos
    inteiros, e o enriquecedor decide onde vale interromper. O teto de 5s
    existe para que ele ainda tenha onde encaixar um grafico.
    """
    novos_tipos, novos_cortes = [], []
    for tipo, (a, b) in zip(tipos, cortes):
        if (tipo == "fala" and novos_tipos and novos_tipos[-1] == "fala"):
            pa, pb = novos_cortes[-1]
            dur = palavras[b]["endMs"] - palavras[pa]["startMs"]
            if dur <= FALA_MAX_MS:
                novos_cortes[-1] = (pa, b)
                continue
        novos_tipos.append(tipo)
        novos_cortes.append((a, b))
    return novos_tipos, novos_cortes

def legenda(texto, limite=4):
    return " ".join(re.sub(r"[^\wÀ-ÿ\s'-]", "", texto).lower().split()[:limite])

def main():
    ap = argparse.ArgumentParser(description="transcript -> plano de motion")
    ap.add_argument("--falas", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--preset", default="noturno", choices=["noturno", "editorial"])
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--estilo", help="medicoes.json de um estilo aprendido (aprender.py)")
    ap.add_argument("--video", help="vídeo original da fala. Vira a imagem dos planos "
                                    "`fala` e a trilha de audio do vídeo inteiro.")
    ap.add_argument("--video-offset-ms", type=int, default=0,
                    help="quanto do original vem antes do t0=0 do transcript")
    a = ap.parse_args()

    palavras = carregar(a.falas)
    if not palavras:
        sys.exit("nenhuma palavra com timestamp encontrada em " + a.falas)

    tem_video = bool(a.video)
    cortes, _ = fatiar(palavras)
    tipos = [classificar(" ".join(w["text"] for w in palavras[i:j + 1]), tem_video)
             for i, j in cortes]
    tipos = alternar(tipos, cortes, palavras, tem_video)
    if tem_video:
        tipos, cortes = juntar_fala(tipos, cortes, palavras)

    planos = []
    for k, (i, j) in enumerate(cortes):
        fala = " ".join(w["text"] for w in palavras[i:j + 1])
        t0, t1 = palavras[i]["startMs"], palavras[j]["endMs"]
        planos.append({
            "id": f"P{k:02d}",
            "t0": t0, "t1": t1, "duracaoMs": t1 - t0,
            "tipo": tipos[k],
            "fala": fala,
            "texto": legenda(fala),
            "camera": "push-in" if tipos[k] in ("objeto", "personagem", "obra", "arquivo") else "estatico",
            "transicao": "corte",
            "asset": None,
            # desenhados em codigo ou vindos do material: nada a gerar
            "prompt": "" if tipos[k] in ("fala", "cartela", "dado", "tela", "palavras",
                                         "paper", "retrato") else f"TODO: {fala[:70]}",
            "fonte": "" if tipos[k] != "dado" else "TODO: fonte do numero",
            "licenca": "" if tipos[k] not in ("arquivo", "obra") else "TODO: licenca da obra E da foto",
            # onde o quadro ja tem texto, a legenda falada cala
            "legenda": tipos[k] not in TEM_TEXTO_PROPRIO,
            # ha nome, ano ou estudo aqui: vale pesquisar antes de ilustrar
            "pesquisar": bool(ANCORA.search(fala)),
        })

    fim = palavras[-1]["endMs"]

    # A timeline nao pode ter buraco. Cada plano nasce e morre nas palavras que
    # ele cobre, mas o silencio ENTRE duas falas — a pausa de quem respira —
    # nao pertence a plano nenhum, e sem dono ele vira tela preta. Cada plano
    # se estica ate o comeco do proximo; o ultimo vai ate o fim do material.
    for atual, seguinte in zip(planos, planos[1:]):
        if seguinte["t0"] > atual["t1"]:
            atual["t1"] = seguinte["t0"]
            atual["duracaoMs"] = atual["t1"] - atual["t0"]
    if planos:
        planos[0]["t0"] = 0
        planos[0]["duracaoMs"] = planos[0]["t1"]
        planos[-1]["t1"] = max(planos[-1]["t1"], fim)
        planos[-1]["duracaoMs"] = planos[-1]["t1"] - planos[-1]["t0"]

    plano = {
        "versao": 1, "preset": a.preset, "fps": a.fps,
        "largura": 1080, "altura": 1920,
        "duracaoMs": fim,
        "duracaoEmFrames": int(fim / 1000 * a.fps) + 1,
        "planos": planos,
    }

    out_prep = Path(a.out); (out_prep / "public").mkdir(parents=True, exist_ok=True)
    if tem_video:
        origem = Path(a.video).expanduser().resolve()
        if not origem.exists():
            sys.exit(f"vídeo não encontrado: {origem}")
        destino = out_prep / "public" / f"fonte{origem.suffix.lower()}"
        if not destino.exists() or destino.stat().st_size != origem.stat().st_size:
            import shutil
            shutil.copy2(origem, destino)
        plano["fonteVideo"] = destino.name
        plano["fonteOffsetMs"] = a.video_offset_ms

    if a.estilo:
        medido = json.loads(Path(a.estilo).read_text(encoding="utf-8"))
        sug = medido.get("preset_sugerido", medido)
        plano["grade"] = {k: v for k, v in {
            "fundo": sug.get("fundo"), "sujeito": sug.get("sujeito"),
            "grao": sug.get("grao"), "vinheta": sug.get("vinheta"),
            "aberracao": sug.get("aberracao", sug.get("aberracao_a_confirmar")),
        }.items() if v is not None}
        plano["estiloAprendido"] = medido.get("estilo", Path(a.estilo).parent.name)
        print(f"grade do estilo `{plano['estiloAprendido']}` embutida: {plano['grade']}")

    out = Path(a.out); (out / "public").mkdir(parents=True, exist_ok=True)
    (out / "plano.json").write_text(json.dumps(plano, ensure_ascii=False, indent=2), encoding="utf-8")
    caps = [{"text": (" " if i else "") + w["text"], "startMs": w["startMs"],
             "endMs": w["endMs"], "timestampMs": (w["startMs"] + w["endMs"]) // 2,
             "confidence": None} for i, w in enumerate(palavras)]
    (out / "public" / "captions.json").write_text(json.dumps(caps, ensure_ascii=False, indent=2), encoding="utf-8")

    dur_s = fim / 1000
    faixa = {15: (7, 9), 30: (12, 16), 60: (22, 30), 90: (30, 40)}
    ref = min(faixa, key=lambda k: abs(k - dur_s))
    lo, hi = faixa[ref]
    print(f"{len(planos)} planos em {dur_s:.1f}s  (faixa saudavel para ~{ref}s: {lo}-{hi})")
    if not lo <= len(planos) <= hi:
        print("  ^ fora da faixa: revise duracoes em plano.json antes de compor")
    from collections import Counter
    for t, n in Counter(p["tipo"] for p in planos).most_common():
        print(f"  {t:<12} {n}")
    if tem_video:
        n_fala = sum(1 for p in planos if p["tipo"] == "fala")
        prop = n_fala / len(planos)
        print(f"\n{n_fala}/{len(planos)} planos voltam para o vídeo original "
              f"({prop*100:.0f}%) · fonte: {plano['fonteVideo']}")
        if prop < 0.25:
            print("  ^ pouco material original. Motion graphics em quase tudo cansa:")
            print("    devolva para `fala` os planos que nao ilustram nada.")
        if prop > 0.8:
            print("  ^ quase nenhum motion graphics. Rode o enriquecimento para achar")
            print("    os momentos que pedem ilustracao.")
    ancoras = [p["id"] for p in planos if p["pesquisar"]]
    if ancoras:
        print(f"\nancoras verificaveis em {len(ancoras)} plano(s): {', '.join(ancoras)}")
        print("  rode o enriquecimento antes dos assets — ha material real para achar.")
    print(f"\nescrito: {out/'plano.json'} e {out/'public'/'captions.json'}")
    print("revise 'tipo', 'texto' e 'prompt' de cada plano antes de gerar assets.")

if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
