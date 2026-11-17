"""A oficina: cache por CONTEÚDO, manifesto do que foi refeito, e trabalho em paralelo.

Tudo que os scripts do formato `analise` produzem e pode ser reaproveitado mora
em `edicao/oficina/`, com nome derivado do conteúdo que o gerou — nunca da
posição no vídeo nem da ordem em que foi pedido. A regra que já estava escrita
em `formato-analise.md` («o cache tem chave de conteúdo, nunca de posição»)
vale agora para o pipeline inteiro, não só para o clipe do cartão.

Por que isto existe — medido nos projetos 14 e 15:

  - o render do 15 (4 591 quadros) rodou 32 vezes; o do 14, 58. Cada pedido de
    ajuste («abaixa a música», «conserta o insert de 1:48») refazia os 4 591
    quadros e recodificava o vídeo inteiro: ~10 min de máquina por ajuste, e
    o dono esperando.
  - a composição era sequencial num processo só, numa máquina de 10 núcleos.
  - a transcrição do 15 rodou duas vezes inteira (7 min cada) porque nada
    guardava que o áudio não tinha mudado.

Cinco peças:

  chave(obj)          — hash estável de qualquer estrutura JSON-serializável
  identidade(arq)     — chave barata de um arquivo grande (tamanho + cabeça + cauda)
  paralelo(fn, itens) — o laço em processos ou threads, com erro nomeado
  Manifesto           — o registro de quais peças foram refeitas nesta rodada e por quê
  Cronometro          — quanto tempo de máquina cada etapa levou, linha a linha, no histórico

O manifesto é o que responde «o que este ajuste custou?» sem ninguém ler log.
O cronômetro é o que responde «quanto este PROJETO custou de máquina?» — e,
cruzado com `custos.py`, quanto custou de sessão e de tokens.
"""
import hashlib
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

FPS, W, H, SR = 30, 1080, 1920, 48000

# A configuração da MÁQUINA (não do projeto): onde ficam projetos, entregas e a
# biblioteca de músicas, SFX, overlays e logos. Escrita pelo `setup.py`; lida por
# qualquer script que precise de uma pasta que muda de pessoa para pessoa. Caminho
# padrão `~/.config/beditor/config.json`; `BEDITOR_CONFIG` aponta para outro.
CONFIG_PADRAO = Path.home() / ".config" / "beditor" / "config.json"
PASTAS = ("projetos", "entregas", "musicas", "sfx", "overlays", "logos", "midia", "marcas", "render", "treinamento")


def config(caminho=None):
    """Lê a configuração da máquina. Sem arquivo, devolve o esqueleto vazio.

    {"versao": 1, "pastas": {"musicas": "/…", …}, "canal": {"nome": …, "arroba": …}}
    Caminhos com `~` são expandidos na leitura; o arquivo guarda o que o usuário digitou.
    """
    p = Path(os.environ.get("BEDITOR_CONFIG") or caminho or CONFIG_PADRAO)
    cfg = {"versao": 1, "pastas": {}, "canal": {}}
    if p.exists():
        try:
            lido = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise SystemExit(f"!! {p} não é JSON válido: {e}")
        cfg.update(lido)
        cfg.setdefault("pastas", {})
        cfg.setdefault("canal", {})
    cfg["_arquivo"] = str(p)
    return cfg


def pasta(nome, obrigatoria=True, cfg=None):
    """A pasta configurada para `nome` (ver PASTAS), expandida. Falta → SystemExit com a
    instrução de rodar o setup — nunca um caminho inventado no disco interno."""
    cfg = cfg or config()
    bruto = cfg["pastas"].get(nome)
    if not bruto:
        if not obrigatoria:
            return None
        raise SystemExit(f"!! pasta «{nome}» não configurada. Rode `/sofia-estrategista-editora:setup` "
                         f"(ou `python3 setup.py --pastas {nome}=/caminho`); arquivo: {cfg['_arquivo']}")
    p = Path(os.path.expanduser(bruto))
    if not p.exists():
        if not obrigatoria:
            return None
        raise SystemExit(f"!! pasta «{nome}» = {p} não existe (disco desconectado?). "
                         f"Conecte o volume ou ajuste em {cfg['_arquivo']}.")
    return p


def chave(obj, n=16):
    """Hash estável (sha1) de uma estrutura JSON. Chaves ordenadas, floats como estão."""
    s = json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:n]


def identidade(arq, janela=8 << 20):
    """Chave de um arquivo grande sem ler o arquivo inteiro.

    Tamanho + os primeiros e últimos 8 MB. Um .mov de 6 GB custa ~20 ms; um
    sha1 completo custaria meio minuto por take e seria pago a cada rodada.
    Troca de conteúdo muda a cauda (o moov está lá) ou a cabeça; troca de nome
    não muda nada — e é isso que se quer: renomear o take não invalida a cache.
    """
    p = Path(arq)
    if p.is_dir():
        itens = sorted(x.name + str(x.stat().st_size) for x in p.iterdir() if x.is_file())
        return hashlib.sha1("".join(itens).encode()).hexdigest()[:16]
    st = p.stat()
    h = hashlib.sha1(str(st.st_size).encode())
    with open(p, "rb") as fh:
        h.update(fh.read(min(janela, st.st_size)))
        if st.st_size > janela:
            fh.seek(-janela, os.SEEK_END)
            h.update(fh.read(janela))
    return h.hexdigest()[:16]


def versao_do_codigo(*modulos):
    """Hash dos arquivos .py que desenham o pixel. Mudou o código, muda a cache."""
    h = hashlib.sha1()
    for m in modulos:
        p = Path(getattr(m, "__file__", m))
        h.update(p.read_bytes())
    return h.hexdigest()[:12]


_ASSINATURAS = {}


def assinatura(modulo, nomes):
    """Hash só do código que `nomes` usam dentro de `modulo` — não do arquivo inteiro.

    `versao_do_codigo` jogava fora a cache inteira a cada linha mudada no módulo:
    no vídeo 16, subir UM título («o seu movimento») recompôs os 111 segmentos,
    porque a chave era o `cartao.py` todo. Aqui a chave de um segmento é o fecho
    de dependências das funções que as receitas dele chamam: a função, as
    funções e constantes de topo que ela cita, e as que essas citam, pelo AST.
    Mexer em `frase_hook` invalida só os segmentos com frase; a legenda, o hook
    e os cartões ficam na cache.

    O que isto NÃO enxerga: outro módulo importado (continua na chave de quem
    chama) e estado mudado em tempo de execução (ex.: `BASE_MODO1`, `TIPOGRAFIA`)
    — esses entram na chave pelas receitas, não pelo código.
    """
    import ast
    arq = Path(getattr(modulo, "__file__", modulo))
    fonte = arq.read_text(encoding="utf-8")
    idx = _ASSINATURAS.get(arq)
    if idx is None or idx[0] != fonte:
        arvore = ast.parse(fonte)
        defs = {}
        for no in arvore.body:
            if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                defs.setdefault(no.name, []).append(no)
            elif isinstance(no, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                alvos = no.targets if isinstance(no, ast.Assign) else [no.target]
                for t in alvos:
                    for n in ast.walk(t):
                        if isinstance(n, ast.Name):
                            defs.setdefault(n.id, []).append(no)
        idx = (fonte, defs)
        _ASSINATURAS[arq] = idx
    _, defs = idx
    vistos, pilha = set(), [n for n in nomes if n in defs]
    while pilha:
        n = pilha.pop()
        if n in vistos:
            continue
        vistos.add(n)
        for no in defs[n]:
            for sub in ast.walk(no):
                ref = sub.id if isinstance(sub, ast.Name) else None
                if ref and ref in defs and ref not in vistos:
                    pilha.append(ref)
    faltam = [n for n in nomes if n not in defs]
    if faltam:
        raise KeyError(f"{arq.name} não define {faltam}")
    h = hashlib.sha1()
    for n in sorted(vistos):
        for no in defs[n]:
            h.update(n.encode())
            h.update(ast.dump(no, include_attributes=False).encode())
    return h.hexdigest()[:12]


def nucleos(teto=8, reserva=2):
    """Quantos trabalhadores: os núcleos menos dois para o sistema, até o teto.

    O teto é de MEMÓRIA, não de CPU: cada trabalhador segura alguns quadros
    1080×1920 em RGBA (8 MB cada) mais o ffmpeg dele. Oito processos numa
    máquina de 16 GB ficam abaixo de 4 GB. Acima disso o vigia de memória do
    macOS mata o render — foi o que aconteceu no 15 com um processo só carregando
    600 s de áudio em float.
    """
    return max(1, min(teto, (os.cpu_count() or 4) - reserva))


def paralelo(fn, itens, n=None, processos=True, initializer=None, initargs=(), rotulo=None):
    """Roda fn(item) para cada item, em paralelo, preservando a ordem dos resultados.

    Erros não derrubam o lote: cada um sai no fim, nomeando o item. Se um só
    item falha, o chamador decide se o resultado parcial serve.
    """
    n = n or nucleos()
    itens = list(itens)
    if not itens:
        return [], []
    if n == 1 or len(itens) == 1:
        if initializer:
            initializer(*initargs)
        out, erros = [], []
        for it in itens:
            try:
                out.append(fn(it))
            except Exception as e:      # noqa: BLE001 — o erro é reportado, não engolido
                out.append(None)
                erros.append((rotulo(it) if rotulo else str(it)[:80], repr(e)))
        return out, erros
    Pool = ProcessPoolExecutor if processos else ThreadPoolExecutor
    kw = {"max_workers": min(n, len(itens))}
    if processos and initializer:
        kw.update(initializer=initializer, initargs=initargs)
    elif initializer:
        initializer(*initargs)
    out, erros = [None] * len(itens), []
    with Pool(**kw) as ex:
        futs = {ex.submit(fn, it): i for i, it in enumerate(itens)}
        for f in as_completed(futs):
            i = futs[f]
            try:
                out[i] = f.result()
            except Exception as e:      # noqa: BLE001
                erros.append((rotulo(itens[i]) if rotulo else str(itens[i])[:80], repr(e)))
    return out, erros


class Manifesto:
    """O que foi refeito nesta rodada, o que veio da cache, e quanto tempo levou.

    Salvo em `oficina/manifesto.json`; a linha de resumo é o que se mostra ao
    dono («12 de 84 segmentos refeitos · 41 s»). Sem isto, a única prova de que
    a cache funcionou seria o relógio.
    """

    def __init__(self, caminho):
        self.caminho = Path(caminho)
        self.t0 = time.time()
        self.etapas = {}

    def etapa(self, nome, feitos, cache, extra=None, t0=None):
        self.etapas[nome] = {"refeitos": feitos, "daCache": cache,
                             "segundos": round(time.time() - (t0 or self.t0), 1),
                             **(extra or {})}
        self.t0 = time.time()

    def fechar(self, **extra):
        d = {"quando": time.strftime("%Y-%m-%d %H:%M:%S"), "etapas": self.etapas, **extra}
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        self.caminho.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        return d

    def resumo(self):
        partes = []
        for k, v in self.etapas.items():
            tot = v["refeitos"] + v["daCache"]
            partes.append(f"{k}: {v['refeitos']}/{tot} refeitos em {v['segundos']}s")
        return " · ".join(partes)


class Cronometro:
    """Mede uma etapa de script e grava UMA linha em `<pasta>/telemetria.jsonl`.

        with oficina.Cronometro(pasta_oficina, "transcrever", args={"takes": 3}) as c:
            ...
            c.extra["palavras"] = 337        # o que a etapa produziu, se souber

    Por que uma linha por execução, e não um número no manifesto: o manifesto é
    o retrato da ÚLTIMA rodada — sobrescrito a cada render, por desenho. A
    pergunta «quanto de máquina este vídeo custou?» precisa do histórico inteiro:
    as 32 rodadas do render do 15, não só a última. Então aqui é append, nunca
    sobrescrita, e o arquivo é o dado. Quem agrega é `custos.py`, que cruza estes
    segundos de máquina com os tokens e o tempo de sessão do registro do Claude
    Code, etapa a etapa.

    Determinístico: a linha só tem o que aconteceu (etapa, script, início, fim,
    segundos, rc, args, extra). Nada de contexto ambiente que varie sem a etapa
    variar. `rc` é 0 ou 1 — 1 quando saiu por exceção — e a exceção CONTINUA
    propagando: medir não é engolir. A pasta é criada se não existir, porque em
    projeto novo o cronômetro roda antes de qualquer outra coisa gravar nela.
    """

    ARQUIVO = "telemetria.jsonl"

    def __init__(self, pasta, etapa, args=None):
        self.pasta = Path(pasta)
        self.etapa = etapa
        self.args = args or {}
        self.extra = {}
        self.script = os.path.basename(sys.argv[0]) if sys.argv and sys.argv[0] else ""

    def __enter__(self):
        self._t0 = time.time()
        self._inicio = datetime.now().astimezone()
        return self

    def __exit__(self, tipo, exc, tb):
        fim = datetime.now().astimezone()
        linha = {"etapa": self.etapa, "script": self.script,
                 "inicio": self._inicio.isoformat(timespec="seconds"),
                 "fim": fim.isoformat(timespec="seconds"),
                 "segundos": round(time.time() - self._t0, 2),
                 "rc": 0 if tipo is None else 1,
                 "args": self.args, **self.extra}
        self.pasta.mkdir(parents=True, exist_ok=True)
        with open(self.pasta / self.ARQUIVO, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(linha, ensure_ascii=False, default=str) + "\n")
        return False  # nunca engole a exceção


def ffmpeg(*args, entrada=None, saida_bytes=False, check=True):
    """ffmpeg silencioso. `entrada` vai pelo stdin; `saida_bytes` devolve o stdout."""
    cmd = ["ffmpeg", "-y", "-nostdin", "-v", "error", *map(str, args)]
    r = subprocess.run(cmd, input=entrada, capture_output=True, check=False)
    if check and r.returncode != 0:
        raise RuntimeError(f"ffmpeg falhou ({r.returncode}): {' '.join(cmd)[:300]}\n"
                           f"{r.stderr.decode(errors='replace')[-600:]}")
    return r.stdout if saida_bytes else None


def sonda(arq):
    """duração (s), largura, altura, fps do primeiro vídeo — uma chamada só."""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=width,height,r_frame_rate:format=duration",
                        "-of", "json", str(arq)], capture_output=True, text=True, check=True, encoding="utf-8", errors="replace")
    j = json.loads(r.stdout)
    st = (j.get("streams") or [{}])[0]
    num, _, den = (st.get("r_frame_rate") or "30/1").partition("/")
    return {"dur": float(j["format"]["duration"]), "w": st.get("width"), "h": st.get("height"),
            "fps": float(num) / float(den or 1)}


def dataless(raiz):
    """Arquivos que o iCloud tirou do disco (0 B reais). Abrir um deles trava o render."""
    r = subprocess.run(["find", str(raiz), "-type", "f", "-flags", "+dataless"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return [l for l in r.stdout.splitlines() if l]


def folha(imagens, saida, cols=8, larg_max=1568, rotulos=None, fundo=(14, 14, 16)):
    """Folha de contato que CABE no orçamento de leitura.

    O modelo lê imagem por área: uma folha de 2 400 px de largura custa o mesmo
    que a de 1 568 (o teto em que ela é reduzida antes de ser lida), só que a
    versão grande gasta disco e o ajuste de escala borra o texto. Aqui a folha
    já nasce no teto, com o rótulo desenhado no tamanho que sobrevive à redução.
    Nos projetos 14 e 15 foram 154 imagens lidas; várias com 600 KB e 2 000+ px
    que chegavam ao modelo com a mesma resolução desta.
    """
    from PIL import Image, ImageDraw, ImageFont
    imagens = list(imagens)
    if not imagens:
        raise ValueError("folha sem imagens")
    cols = min(cols, len(imagens))
    lw = larg_max // cols
    prop = imagens[0].height / imagens[0].width
    lh = int(lw * prop)
    rot = 18 if rotulos else 0
    lin = (len(imagens) + cols - 1) // cols
    fol = Image.new("RGB", (cols * lw, lin * (lh + rot)), fundo)
    dr = ImageDraw.Draw(fol)
    try:
        f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 13)
    except OSError:
        f = ImageFont.load_default()
    for i, im in enumerate(imagens):
        x, y = (i % cols) * lw, (i // cols) * (lh + rot)
        fol.paste(im.convert("RGB").resize((lw, lh)), (x, y))
        if rotulos:
            dr.text((x + 4, y + lh + 2), str(rotulos[i]), fill=(240, 220, 120), font=f)
    Path(saida).parent.mkdir(parents=True, exist_ok=True)
    fol.save(saida, quality=82)
    return saida


def quadro_em(video, segundo):
    """Um quadro do vídeo em `segundo`, como PIL.Image, sem arquivo intermediário."""
    import io
    from PIL import Image
    b = ffmpeg("-ss", f"{segundo:.3f}", "-i", str(video), "-frames:v", "1",
               "-f", "image2pipe", "-vcodec", "mjpeg", "-q:v", "2", "-", saida_bytes=True)
    return Image.open(io.BytesIO(b)).convert("RGB")
