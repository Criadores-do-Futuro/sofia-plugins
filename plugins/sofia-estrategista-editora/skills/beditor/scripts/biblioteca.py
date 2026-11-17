"""A biblioteca de mídia da máquina: catálogo por CONTEÚDO, com o que a escolha precisa saber.

    python3 biblioteca.py catalogar [--so musicas,sfx,overlays,logos] [--forcar] [--paralelo N]
    python3 biblioteca.py listar <musicas|sfx|overlays|logos> [--clima X] [--texto q] [--alfa]
                                 [--max-eventos N] [--json]
    python3 biblioteca.py cama [--clima X] [--n 5] [--min-dur 90]
    python3 biblioteca.py sfx <marcador|cartao|pb|destaque|modo1>

As pastas vêm de `~/.config/beditor/config.json` (`oficina.pasta("musicas")` etc.);
sem configuração, o script para e manda rodar o setup — nunca inventa caminho.

Cada pasta recebe UM `catalogo.json` dentro dela: o catálogo viaja com a pasta
(copiar a biblioteca para outro disco leva as medições junto) e a chave de cada
item é a `oficina.identidade()` do arquivo, não o nome nem a data. Renomear não
invalida nada; trocar o conteúdo refaz só aquele item. Rodar `catalogar` de novo
com nada mudado custa o tempo de ler cabeça e cauda de cada arquivo.

Por que medir, em vez de confiar no nome:

  - A cama do formato `analise` «não pode ter nenhum evento que o espectador
    consiga contar» (`referencias/formato-analise.md`, seção «Som»). O nome da
    faixa não diz isso; a curva de loudness diz. Por isso cada áudio guarda,
    além do LUFS integrado e do LRA, um índice de EVENTO: quantas vezes por
    minuto o loudness momentâneo sobe 6 dB ou mais de uma janela de 1 s para a
    seguinte. Entrada de bateria, refrão, virada — tudo o que compete com a
    estrutura numerada do vídeo — aparece aí; um pad contínuo dá zero.
  - `logo_atras` (`cartao.py`) exige FUNDO TRANSPARENTE: «ícone chapado sobre o
    A-roll vira adesivo». Um PNG pode ser RGBA e mesmo assim ser chapado (alfa
    255 em todo pixel). Então `alfa` é medido pixel a pixel, não pelo modo.
  - Overlay com canal alfa compõe; sem alfa exige modo de mesclagem. O `pix_fmt`
    responde antes de abrir o arquivo no editor.

LICENÇA — e isto o catálogo registra POR FAIXA, porque a decisão é do dono:
as músicas são versões instrumentais/karaokê de obras comerciais, a maioria
baixada do YouTube (o «(youtube)» no nome). Não há licença conhecida e o
Content ID ao publicar é risco real. Cada faixa sai com `origem`, `licenca:
"desconhecida"` e `risco: "content-id"`, e `cama` repete o aviso na saída. O
script não apaga nem esconde nada; ele deixa a informação onde a escolha é feita.
"""
import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oficina  # noqa: E402

VERSAO_CATALOGO = 1
TIPOS = ("musicas", "sfx", "overlays", "logos")
AUDIO = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".aif", ".aiff"}
VIDEO = {".mp4", ".mov", ".webm", ".mkv", ".m4v"}
IMAGEM = {".png", ".webp", ".jpg", ".jpeg", ".gif", ".tif", ".tiff"}
IGNORAR = {"catalogo.json", "README.md", ".DS_Store"}

# O índice de evento: o ebur128 entrega o loudness momentâneo a cada 100 ms; ele é
# agrupado em janelas de 1 s (média) e conta-se cada salto ≥ 6 dB entre uma janela e
# a seguinte. Abaixo de PISO é silêncio digital (o ebur128 marca −120,7): a entrada da
# música depois do silêncio de cabeça não é evento da cama, é o começo do arquivo.
PASSO_S, JANELA_S, SALTO_DB, PISO_LUFS = 0.1, 1.0, 6.0, -70.0

# Gatilho → SFX, transcrito da tabela «Os SFX» de formato-analise.md. Só dois gatilhos
# têm som; os outros três estão aqui para que a resposta «nenhum» venha com o motivo,
# em vez de a ausência parecer esquecimento.
GATILHOS = {
    "marcador": ("Hit", "o número do capítulo entra sobre o gesto: impacto curto e seco, sem cauda"),
    "cartao": ("Woosh Fast", "o cartão entra: whoosh curto, SÓ na primeira entrada de cada capítulo — "
                             "nas seguintes o corte é mudo"),
    "pb": (None, "a entrada em P&B é filtro / queda de banda na própria mistura, não efeito somado"),
    "destaque": (None, "a palavra em destaque já é o evento visual; somar som ali é redundante"),
    "modo1": (None, "cartão atrás do autor: ele não para de falar, e um efeito ali corta a frase ao meio"),
}

AVISO_LICENCA = ("!! licença desconhecida: versões instrumentais/karaokê de músicas comerciais, baixadas do "
                 "YouTube. Content ID ao publicar é provável. A decisão de usar é do dono; a faixa entra no "
                 "provas.json com tipo «trilha», título, autor e origem.")


# ---------------------------------------------------------------------------
# leitura de nomes — barata, roda sempre (não depende da identidade)
# ---------------------------------------------------------------------------
_RE_NUMERO = re.compile(r"^(\d{1,3})\s+")
_RE_CLIMA = re.compile(r"^(\S+_\S+)\s+")
_RE_YT_ID = re.compile(r"\s*\[[\w-]{11}\]")
_RE_VERSAO = re.compile(r"i\s?n\s?s\s?t\s?r\s?u\s?m\s?e\s?n\s?t\s?a\s?l|karaok|playback|backtrack"
                        r"|sem\s+voz|sem\s+vocal|without\s+voice|no\s+vocal", re.I)
_RE_GRUPO_VERSAO = re.compile(r"\s*[\(\[][^\)\]]*(instrumental|karaok|playback|backtrack|voz|vocal|voice"
                              r"|official|oficial|custom|lyrics|letra|hq)[^\)\]]*[\)\]]", re.I)
_RE_CAUDA_VERSAO = re.compile(r"(\s*[-_•]?\s*(official|oficial|som original|hq|instrumental|karaok\S*"
                              r"|playback|backtracking|sem vocal|sem voz|lyrics|letra)\s*)+$", re.I)
_RE_SEPARADOR = re.compile(r"\s+-\s+|\s*[—•]\s*")


def _limpar(s):
    # «Can_t Stop», «Won_t Let Go»: o apóstrofo virou sublinhado no download
    s = re.sub(r"(\w)_(\w)", r"\1'\2", s)
    return re.sub(r"\s{2,}", " ", s).strip(" _.-—•")


def tem_vocal(nome):
    """«vocal» no nome, exceto quando o nome diz que NÃO tem («sem vocal», «no vocal bleed»).

    A regra da cama é «sem vocal» e não é negociável; um nome que só diz «vocal»
    é suspeito. Mas metade das ocorrências no acervo são negações, e reprovar
    «Backtracking sem Vocal» por conter a palavra seria ler o nome ao contrário.
    """
    return bool(re.search(r"vocal", nome, re.I)) and not re.search(r"\b(sem|no|without)\s+vocal", nome, re.I)


def versao_do_nome(nome):
    m = _RE_VERSAO.search(nome)
    if not m:
        return None
    t = m.group(0).lower()
    if "karaok" in t:
        return "Karaokê"
    if "playback" in t:
        return "Playback"
    return "Instrumental"


def parse_nome_musica(nome, clima=None):
    """Lê `NN Clima_Sub Artista - Título (Versão) - uploader (youtube).mp3`.

    O padrão é o do acervo instalado em 2026-09, e ele não é uniforme: há nome
    sem número, sem separador, com o título antes do artista, com «(youtube)»
    ou com o id do vídeo entre colchetes. Tudo aqui é heurística de leitura;
    nada que não dê certo derruba o catálogo — o item sai com o que foi lido e
    o nome inteiro continua em `arq`.

    `clima` vem da PASTA, que é a fonte de verdade da organização; o token
    `Clima_Sub` do nome é só descartado.
    """
    stem = Path(nome).stem
    d = {"numero": None, "clima": clima, "artista": "", "titulo": "", "versao": None, "canal": None,
         "origem": "desconhecida", "licenca": "desconhecida", "risco": "content-id", "vocal": tem_vocal(stem)}
    m = _RE_NUMERO.match(stem)
    if m:
        d["numero"] = int(m.group(1))
        stem = stem[m.end():]
    m = _RE_CLIMA.match(stem)
    if m:
        stem = stem[m.end():]
    if re.search(r"\(youtube\)", stem, re.I):
        d["origem"] = "youtube"
        stem = re.sub(r"\s*\(youtube\)", "", stem, flags=re.I)
    elif _RE_YT_ID.search(stem):
        d["origem"] = "youtube"
        stem = _RE_YT_ID.sub("", stem)
    d["versao"] = versao_do_nome(stem)

    segs = [_limpar(s) for s in _RE_SEPARADOR.split(stem) if _limpar(s)]
    # com origem YouTube e três ou mais partes, a última é quem subiu o vídeo
    if d["origem"] == "youtube" and len(segs) >= 3:
        d["canal"] = segs.pop()
    if len(segs) >= 2:
        art, tit = segs[0], segs[1]
        # «In the End (Instrumental) - Linkin Park»: o parêntese de versão marca o título
        if _RE_GRUPO_VERSAO.search(art) and not _RE_GRUPO_VERSAO.search(tit):
            art, tit = tit, art
    elif segs:
        art, tit = "", segs[0]
    else:
        art, tit = "", stem
    d["artista"] = _limpar(_RE_CAUDA_VERSAO.sub("", _RE_GRUPO_VERSAO.sub(" ", art)))
    d["titulo"] = _limpar(_RE_CAUDA_VERSAO.sub("", _RE_GRUPO_VERSAO.sub(" ", tit)))
    return d


_TOKENS_LOGO = {"logo", "logos", "icone", "icon", "ai", "pro", "resolve", "flash", "pagamento", "oficial",
                "official", "png", "webp", "jpg"}


def marca_do_nome(nome):
    """`logo-chatgpt-01.webp` → chatgpt; `kling-ai-logo.jpg` → kling; `logo-davinci-resolve` → davinci.

    Primeiro token do nome que não é «logo», sufixo de produto («ai», «pro»,
    «resolve», «flash») nem número. É o que o plano cita: a marca, não o arquivo.
    """
    toks = [t for t in re.split(r"[-_\s.]+", Path(nome).stem.lower()) if t]
    toks = [t for t in toks if t not in _TOKENS_LOGO and not t.isdigit()]
    return toks[0] if toks else Path(nome).stem.lower()


def pix_fmt_tem_alfa(pix_fmt):
    """Os formatos de pixel do ffmpeg com canal alfa. `yuv420p` (o de todo mp4 comum) não tem."""
    if not pix_fmt:
        return False
    return bool(re.match(r"^(yuva|rgba|bgra|argb|abgr|gbrap|ya\d|rgba64|bgra64|ayuv)", pix_fmt))


# ---------------------------------------------------------------------------
# medição — cara, roda uma vez por identidade
# ---------------------------------------------------------------------------
def eventos_por_minuto(serie, passo=PASSO_S, janela=JANELA_S, salto=SALTO_DB, piso=PISO_LUFS):
    """Saltos ≥ `salto` dB entre janelas consecutivas de `janela` s, por minuto de áudio.

    `serie` é o loudness momentâneo (LUFS) a cada `passo` s, como o ebur128
    entrega. A média por janela apaga o transiente de uma baqueta e deixa o que
    o ouvido conta: a entrada da bateria, o refrão, a virada. Janela vinda do
    silêncio (abaixo de `piso`) não conta — é o arquivo começando.
    """
    n = max(1, int(round(janela / passo)))
    minutos = len(serie) * passo / 60.0
    # o medidor começa vazio: as primeiras 3–4 amostras são −120,7 mesmo com som, e o
    # silêncio de cabeça de um arquivo também não é evento — a série começa no primeiro som
    ini = 0
    while ini < len(serie) and serie[ini] <= piso:
        ini += 1
    serie = serie[ini:]
    if len(serie) < 2 * n:
        return 0.0
    janelas = [sum(serie[i:i + n]) / n for i in range(0, len(serie) - n + 1, n)]
    saltos = sum(1 for a, b in zip(janelas, janelas[1:]) if a > piso and b - a >= salto)
    return round(saltos / minutos, 2) if minutos > 0 else 0.0


def sondar(arq):
    """Streams e duração num ffprobe só. Devolve {"dur", "video": {...}|None, "audio": {...}|None}."""
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "stream=codec_type,width,height,pix_fmt,r_frame_rate,sample_rate,channels:format=duration",
                        "-of", "json", str(arq)], capture_output=True, text=True, check=True, encoding="utf-8", errors="replace")
    j = json.loads(r.stdout or "{}")
    out = {"dur": None, "video": None, "audio": None}
    try:
        out["dur"] = round(float(j["format"]["duration"]), 3)
    except (KeyError, ValueError, TypeError):
        pass
    for st in j.get("streams", []):
        if st.get("codec_type") == "video" and not out["video"]:
            num, _, den = (st.get("r_frame_rate") or "0/1").partition("/")
            fps = float(num) / float(den or 1) if float(den or 1) else 0.0
            out["video"] = {"w": st.get("width"), "h": st.get("height"), "fps": round(fps, 3),
                            "pix_fmt": st.get("pix_fmt")}
        elif st.get("codec_type") == "audio" and not out["audio"]:
            out["audio"] = {"sr": int(st["sample_rate"]) if st.get("sample_rate") else None,
                            "canais": st.get("channels")}
    return out


def medir_audio(arq):
    """LUFS integrado, LRA e a série momentânea, numa passada só do ffmpeg.

    O resumo («Integrated loudness … LRA») sai no stderr em nível info; a
    série de 100 ms sai pelo `ametadata=print:file=-` no stdout. O muxer `null`
    não escreve nada, então o stdout fica só com a série. Uma faixa de 4 min
    leva ~1 s; o ffmpeg já é multithread, por isso o laço acima usa threads.
    """
    cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-nostats", "-v", "info", "-i", str(arq), "-vn",
           "-af", "ebur128=metadata=1,ametadata=mode=print:key=lavfi.r128.M:file=-", "-f", "null", "-"]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg ebur128 falhou ({r.returncode}): {r.stderr[-400:]}")
    serie = []
    for m in re.finditer(r"lavfi\.r128\.M=(\S+)", r.stdout):
        try:
            v = float(m.group(1))
        except ValueError:
            v = -120.0
        serie.append(v if v > -1e6 else -120.0)
    mi = re.search(r"I:\s+(-?[\d.]+|-?inf)\s+LUFS", r.stderr)
    ml = re.search(r"LRA:\s+(-?[\d.]+)\s+LU", r.stderr)
    lufs = float(mi.group(1)) if mi and "inf" not in mi.group(1) else None
    lra = float(ml.group(1)) if ml else None
    return {"lufs": lufs, "lra": lra, "eventosMin": eventos_por_minuto(serie), "amostras": len(serie)}


def medir_imagem(arq):
    """Largura, altura e se há transparência DE VERDADE (algum pixel com alfa < 255)."""
    from PIL import Image
    with Image.open(arq) as im:
        w, h = im.size
        modo = im.mode
        alfa = False
        if modo in ("RGBA", "LA", "PA") or "transparency" in im.info:
            a = im.convert("RGBA").getchannel("A")
            alfa = a.getextrema()[0] < 255
    return {"w": w, "h": h, "modo": modo, "alfa": alfa}


# ---------------------------------------------------------------------------
# o catálogo de uma pasta
# ---------------------------------------------------------------------------
def _classe(tipo, arq):
    ext = arq.suffix.lower()
    if ext in AUDIO:
        return "audio"
    if ext in VIDEO:
        return "audio" if tipo == "musicas" else "video"
    if ext in IMAGEM:
        return "imagem"
    return None


def _arquivos(raiz, tipo):
    for p in sorted(raiz.rglob("*")):
        if not p.is_file() or p.name in IGNORAR or p.name.startswith("."):
            continue
        if _classe(tipo, p):
            yield p


def _campos_do_nome(tipo, raiz, arq):
    """O que se lê do nome e da pasta — recalculado sempre, porque é grátis e porque
    renomear o arquivo deve atualizar o catálogo sem remedir o áudio."""
    rel = arq.relative_to(raiz)
    if tipo == "musicas":
        clima = rel.parts[0] if len(rel.parts) > 1 else None
        return parse_nome_musica(arq.name, clima)
    if tipo == "logos":
        return {"marca": marca_do_nome(arq.name)}
    if tipo == "sfx":
        return {"nome": arq.stem}
    return {}


def _medir(tipo, arq, classe):
    """A parte cara. Devolve só o que depende do conteúdo."""
    d = {"bytes": arq.stat().st_size}
    if d["bytes"] == 0:
        # dois mp3 do acervo vieram assim: o download parou antes de gravar um byte
        raise RuntimeError("arquivo vazio (0 B) — download incompleto? baixe de novo ou apague")
    if classe == "imagem":
        d.update(medir_imagem(arq))
        return d
    s = sondar(arq)
    d["dur"] = s["dur"]
    if classe == "audio":
        if s["audio"]:
            d.update(s["audio"])
        d.update(medir_audio(arq))
    else:
        v = s["video"] or {}
        d.update({"w": v.get("w"), "h": v.get("h"), "fps": v.get("fps"), "pix_fmt": v.get("pix_fmt"),
                  "alfa": pix_fmt_tem_alfa(v.get("pix_fmt")), "audio": bool(s["audio"])})
    return d


def carregar_catalogo(raiz):
    p = Path(raiz) / "catalogo.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def catalogar_pasta(raiz, tipo, forcar=False, n=5):
    """Escreve `<raiz>/catalogo.json`. Devolve (catalogo, n_novos, erros).

    Incremental pela identidade: o item cujo conteúdo não mudou volta da versão
    anterior com os campos medidos intactos e só os campos de nome refeitos.
    Item cujo arquivo sumiu é descartado. Um arquivo que falha na medição entra
    com `erro` em vez de derrubar a pasta — o SVG disfarçado de PNG do acervo é
    exatamente esse caso.
    """
    raiz = Path(raiz)
    anterior = (carregar_catalogo(raiz) or {}).get("itens", {}) if not forcar else {}
    por_ident = {v.get("ident"): v for v in anterior.values() if v.get("ident")}
    arquivos = list(_arquivos(raiz, tipo))
    # a identidade lê até 16 MB por arquivo — é I/O, e 186 leituras em fila num disco
    # externo levaram 50 s; em threads o disco trabalha o tempo todo
    idents, _ = oficina.paralelo(oficina.identidade, arquivos, n=n, processos=False)
    itens, pendentes = {}, []
    for arq, ident in zip(arquivos, idents):
        rel = str(arq.relative_to(raiz))
        classe = _classe(tipo, arq)
        base = {"arq": rel, "ident": ident, "classe": classe, **_campos_do_nome(tipo, raiz, arq)}
        velho = por_ident.get(ident)
        if velho and not velho.get("erro"):
            medido = {k: v for k, v in velho.items() if k not in base and k not in ("arq", "ident", "classe")}
            itens[rel] = {**base, **medido}
        else:
            itens[rel] = base
            pendentes.append((rel, arq, classe))

    def um(p):
        rel, arq, classe = p
        return rel, _medir(tipo, arq, classe)

    saida, erros = oficina.paralelo(um, pendentes, n=n, processos=False, rotulo=lambda p: p[0])
    for r in saida:
        if r:
            rel, medido = r
            itens[rel].update(medido)
    for rel, msg in erros:
        itens[rel]["erro"] = msg[:200]

    catalogo = {"versao": VERSAO_CATALOGO, "tipo": tipo, "raiz": str(raiz),
                "quando": time.strftime("%Y-%m-%d %H:%M:%S"), "itens": itens}
    if tipo == "musicas":
        catalogo["aviso"] = AVISO_LICENCA.lstrip("! ")
    (raiz / "catalogo.json").write_text(json.dumps(catalogo, ensure_ascii=False, indent=1), encoding="utf-8")
    return catalogo, len(pendentes), erros


def _resumo(tipo, catalogo, novos, erros, seg):
    itens = catalogo["itens"]
    lufs = [v["lufs"] for v in itens.values() if v.get("lufs") is not None]
    partes = [f"{tipo}: {len(itens)} itens · {novos} medidos agora"]
    if lufs:
        partes.append(f"LUFS {min(lufs):.1f} … {max(lufs):.1f}")
    if any(v.get("classe") == "imagem" for v in itens.values()):
        com = sum(1 for v in itens.values() if v.get("classe") == "imagem" and v.get("alfa"))
        partes.append(f"{com} imagens com alfa")
    if erros:
        partes.append(f"{len(erros)} com erro")
    partes.append(f"{seg:.0f}s")
    return " · ".join(partes)


# ---------------------------------------------------------------------------
# consultas
# ---------------------------------------------------------------------------
def _catalogo_ou_sai(tipo):
    raiz = oficina.pasta(tipo)
    cat = carregar_catalogo(raiz)
    if not cat:
        raise SystemExit(f"!! {raiz / 'catalogo.json'} não existe. Rode `biblioteca.py catalogar --so {tipo}`.")
    return raiz, cat


def _mmss(s):
    if s is None:
        return "  --:--"
    s = int(round(s))
    return f"{s // 60:3d}:{s % 60:02d}"


def _f(v, fmt="{:6.1f}", vazio="     -"):
    return fmt.format(v) if isinstance(v, (int, float)) else vazio


def linha_item(tipo, v):
    """Uma linha por item, colunas fixas por tipo — para caber num terminal e num olho."""
    if tipo == "musicas":
        return (f"{_mmss(v.get('dur'))} {_f(v.get('lufs'))} LUFS  LRA {_f(v.get('lra'), '{:4.1f}', '   -')}  "
                f"{_f(v.get('eventosMin'), '{:4.1f}', '   -')} ev/min  {'VOCAL ' if v.get('vocal') else '      '}"
                f"{(v.get('versao') or '?')[:12]:<12} {(v.get('clima') or '')[:22]:<22} "
                f"{v.get('artista') or '?'} — {v.get('titulo') or v['arq']}"
                + (f"  [{v['erro'][:40]}]" if v.get("erro") else ""))
    if tipo == "sfx":
        if v.get("classe") == "video":
            return (f"{_mmss(v.get('dur'))} {v.get('w')}x{v.get('h')} {_f(v.get('fps'), '{:5.1f}', '    -')}fps "
                    f"{v.get('pix_fmt') or '?':<10} {'alfa' if v.get('alfa') else '    '}  {v['arq']}")
        return (f"{_mmss(v.get('dur'))} {_f(v.get('lufs'))} LUFS  LRA {_f(v.get('lra'), '{:4.1f}', '   -')}  "
                f"{_f(v.get('eventosMin'), '{:4.1f}', '   -')} ev/min  {v['arq']}")
    if tipo == "overlays":
        if v.get("classe") == "imagem":
            return f"  imagem {v.get('w')}x{v.get('h')} {'alfa' if v.get('alfa') else '    '}  {v['arq']}"
        return (f"{_mmss(v.get('dur'))} {v.get('w')}x{v.get('h')} {_f(v.get('fps'), '{:5.1f}', '    -')}fps "
                f"{v.get('pix_fmt') or '?':<10} {'alfa' if v.get('alfa') else 'SEM alfa'} "
                f"{'+audio' if v.get('audio') else '      '}  {v['arq']}")
    if tipo == "logos":
        return (f"{(v.get('marca') or '?'):<12} {str(v.get('w') or '?'):>5}x{str(v.get('h') or '?'):<5} "
                f"{(v.get('modo') or '?'):<5} {'alfa' if v.get('alfa') else 'SEM alfa'}  {v['arq']}"
                + (f"  [{v['erro'][:50]}]" if v.get("erro") else ""))
    return json.dumps(v, ensure_ascii=False)


def _sem_acento(s):
    """«tensao» tem de achar «TENSÃO SUSPENSE»: quem digita no terminal não põe acento."""
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()


def filtrar(itens, clima=None, texto=None, alfa=False, max_eventos=None):
    out = []
    for v in itens.values():
        if clima and _sem_acento(clima) not in _sem_acento(v.get("clima") or ""):
            continue
        if texto and _sem_acento(texto) not in _sem_acento(json.dumps(v, ensure_ascii=False)):
            continue
        if alfa and not v.get("alfa"):
            continue
        if max_eventos is not None and (v.get("eventosMin") is None or v["eventosMin"] > max_eventos):
            continue
        out.append(v)
    return out


def escolher_cama(itens, clima=None, n=5, min_dur=90.0):
    """As N músicas mais parecidas com uma cama do `analise`.

    Filtro duro: duração ≥ `min_dur` (uma cama que acaba antes do capítulo vira
    troca a mais), sem «vocal» no nome, medida sem erro. Ordem: menos eventos
    por minuto, depois menor LRA — a faixa que menos muda ganha. Não se olha o
    LUFS para escolher: o nível é resolvido pelo `ganho` do plano, não pela faixa.
    """
    cands = [v for v in filtrar(itens, clima=clima)
             if v.get("classe") == "audio" and not v.get("erro") and not v.get("vocal")
             and (v.get("dur") or 0) >= min_dur and v.get("eventosMin") is not None]
    cands.sort(key=lambda v: (v["eventosMin"], v.get("lra") if v.get("lra") is not None else 99, -(v.get("dur") or 0)))
    return cands[:n]


def _id_cama(v, usados):
    base = re.sub(r"[^a-z0-9]+", "", (v.get("titulo") or Path(v["arq"]).stem).lower())[:12] or "trilha"
    cand, k = base, 2
    while cand in usados:
        cand, k = f"{base}{k}", k + 1
    usados.add(cand)
    return cand


def bloco_plano(raiz, escolhidas):
    """O trecho `"musicas": {...}` do plano.json, com caminho absoluto, no formato que
    `render_analise.py` lê (ver a docstring dele). `src` é 0.0: o ponto de entrada na
    faixa é decisão de escuta, não do catálogo."""
    usados, d = set(), {}
    for v in escolhidas:
        d[_id_cama(v, usados)] = {
            "arq": str(Path(raiz) / v["arq"]), "src": 0.0,
            "titulo": v.get("titulo") or Path(v["arq"]).stem, "autor": v.get("artista") or "desconhecido",
            "tipo": "trilha", "versao": v.get("versao"), "origem": v.get("origem"),
            "canal": v.get("canal"), "url": "", "licenca": v.get("licenca", "desconhecida"),
            "risco": v.get("risco", "content-id")}
    return {"musicas": d}


def sfx_para(gatilho, itens=None, raiz=None):
    """(arquivo|None, motivo). Procura o SFX pelo nome no catálogo; sem catálogo, na pasta."""
    if gatilho not in GATILHOS:
        raise SystemExit(f"!! gatilho «{gatilho}» não existe. Gatilhos: {', '.join(GATILHOS)}")
    nome, motivo = GATILHOS[gatilho]
    if nome is None:
        return None, motivo
    if itens:
        for v in itens.values():
            if v.get("classe") == "audio" and Path(v["arq"]).stem.lower() == nome.lower():
                return (Path(raiz) / v["arq"]) if raiz else Path(v["arq"]), motivo
    if raiz:
        for p in Path(raiz).iterdir():
            if p.is_file() and p.stem.lower() == nome.lower() and p.suffix.lower() in AUDIO:
                return p, motivo
    return None, f"{motivo} — mas «{nome}» não está na pasta de SFX"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def cmd_catalogar(a):
    tipos = [t.strip() for t in (a.so or ",".join(TIPOS)).split(",") if t.strip()]
    for t in tipos:
        if t not in TIPOS:
            raise SystemExit(f"!! tipo «{t}» não existe; use {', '.join(TIPOS)}")
    # não há projeto aqui: a telemetria vai para a pasta da MÁQUINA, `~/.beditor/`
    with oficina.Cronometro(Path.home() / ".beditor", "catalogar",
                            args={"tipos": tipos, "forcar": a.forcar, "paralelo": a.paralelo}) as cron:
        cron.extra.update(novos={}, erros=0)
        for t in tipos:
            raiz = oficina.pasta(t)
            t0 = time.time()
            cat, novos, erros = catalogar_pasta(raiz, t, forcar=a.forcar, n=a.paralelo)
            cron.extra["novos"][t] = novos
            cron.extra["erros"] += len(erros)
            print(_resumo(t, cat, novos, erros, time.time() - t0), flush=True)
            for rel, msg in erros:
                print(f"   erro: {rel}: {msg[:120]}", flush=True)
            if t == "musicas" and cat["itens"]:
                print("   " + AVISO_LICENCA, flush=True)


def cmd_listar(a):
    raiz, cat = _catalogo_ou_sai(a.tipo)
    itens = filtrar(cat["itens"], clima=a.clima, texto=a.texto, alfa=a.alfa, max_eventos=a.max_eventos)
    if a.tipo == "musicas":
        itens.sort(key=lambda v: ((v.get("clima") or ""), v.get("numero") or 0))
    if a.json:
        print(json.dumps({"raiz": str(raiz), "itens": itens}, ensure_ascii=False, indent=1))
        return
    for v in itens:
        print(linha_item(a.tipo, v))
    print(f"— {len(itens)} de {len(cat['itens'])} · {raiz}")


def cmd_cama(a):
    raiz, cat = _catalogo_ou_sai("musicas")
    esc = escolher_cama(cat["itens"], clima=a.clima, n=a.n, min_dur=a.min_dur)
    if not esc:
        raise SystemExit("!! nenhuma faixa passou no filtro (duração, vocal, medição). Afrouxe --min-dur ou "
                         "confira o clima.")
    for i, v in enumerate(esc, 1):
        print(f"{i}. {v.get('clima')} · {v.get('artista') or '?'} — {v.get('titulo')}  ·  {_mmss(v.get('dur')).strip()}  "
              f"{v.get('lufs')} LUFS · LRA {v.get('lra')} · {v.get('eventosMin')} ev/min · "
              f"{v.get('versao') or 'versão?'} · origem {v.get('origem')}")
        print(f"   {Path(raiz) / v['arq']}")
    print()
    print(AVISO_LICENCA)
    print()
    print("Para o plano.json (ajuste `src` ouvindo; `ganho` fica no nível do plano):")
    print(json.dumps(bloco_plano(raiz, esc), ensure_ascii=False, indent=1))


def cmd_sfx(a):
    raiz = oficina.pasta("sfx")
    cat = carregar_catalogo(raiz) or {"itens": {}}
    arq, motivo = sfx_para(a.gatilho, cat["itens"], raiz)
    if arq is None:
        print(f"nenhum — {motivo}")
    else:
        print(f"{arq}\n   {motivo}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("catalogar", help="varre as pastas e escreve catalogo.json em cada uma")
    c.add_argument("--so", help="só estes tipos, separados por vírgula (musicas,sfx,overlays,logos)")
    c.add_argument("--forcar", action="store_true", help="ignora o catálogo anterior e remede tudo")
    c.add_argument("--paralelo", type=int, default=5, help="threads de medição (o ffmpeg já é multithread)")
    c.set_defaults(fn=cmd_catalogar)

    l = sub.add_parser("listar", help="uma linha por item, ou --json")
    l.add_argument("tipo", choices=TIPOS)
    l.add_argument("--clima")
    l.add_argument("--texto", help="substring em qualquer campo")
    l.add_argument("--alfa", action="store_true", help="só itens com canal alfa de verdade")
    l.add_argument("--max-eventos", type=float, help="só áudio com eventos/min até este valor")
    l.add_argument("--json", action="store_true")
    l.set_defaults(fn=cmd_listar)

    m = sub.add_parser("cama", help="as N músicas mais adequadas a cama do formato analise")
    m.add_argument("--clima")
    m.add_argument("--n", type=int, default=5)
    m.add_argument("--min-dur", type=float, default=90.0)
    m.set_defaults(fn=cmd_cama)

    s = sub.add_parser("sfx", help="o SFX de um gatilho do formato, ou «nenhum» com o motivo")
    s.add_argument("gatilho", choices=sorted(GATILHOS))
    s.set_defaults(fn=cmd_sfx)

    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
