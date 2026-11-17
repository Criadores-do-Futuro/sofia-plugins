#!/usr/bin/env python3
"""setup.py — prepara uma máquina nova para o bEditor e gera o manual.

    python3 setup.py --verificar [--json]
    python3 setup.py --pastas projetos=~/Videos/Projetos musicas=~/Musica/Trilhas [--criar]
    python3 setup.py --canal nome="Meu canal" arroba=@meucanal
    python3 setup.py --instalar [--sim]
    python3 setup.py --atualizar [--sim]
    python3 setup.py --manual [~/.beditor/manual.html]
    python3 setup.py --tudo

Por que este script existe:

  - Até aqui o plugin sabia rodar numa máquina só: caminhos do SSD do autor
    estavam escritos nos scripts, e a lista de dependências morava na cabeça de
    quem o instalou. Outra pessoa que clonasse o repositório descobria o que
    faltava um Traceback por vez, no meio de um render.
  - A configuração da máquina (onde ficam projetos, entregas, músicas, SFX,
    overlays, logos, render e treinamento) já tem casa: `~/.config/beditor/config.json`,
    lida por `oficina.config()` / `oficina.pasta()`. Este script é quem escreve
    esse arquivo, e mescla em vez de sobrescrever: rodar de novo com uma pasta
    só não apaga as outras.
  - O manual (`docs/manual.html`) é um template com um marcador único; aqui ele
    recebe o JSON do estado real desta máquina (o que está ok, o que falta, as
    pastas, os comandos do plugin, as referências) e vira um arquivo só, que
    abre do disco ou publicado como artifact.

Só biblioteca padrão: este é o script que roda ANTES de qualquer `pip install`.
O `oficina.py` ao lado também é só stdlib, por isso pode ser importado daqui.

A chave da Gemini nunca é impressa — só «presente» ou «ausente».
"""
import argparse
import importlib.util
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oficina  # noqa: E402
import plataforma  # noqa: E402

# scripts/ → beditor/ → skills/ → raiz do repositório
RAIZ_PLUGIN = Path(__file__).resolve().parents[3]
CASA = Path.home() / ".beditor"
ENV_PADRAO = Path.home() / ".config" / "beditor" / "env"
TEMPLATE_MANUAL = RAIZ_PLUGIN / "docs" / "manual.html"
MANUAL_PADRAO = CASA / "manual.html"
MARCADOR = "/*__DADOS__*/{}"
PYTHON_MINIMO = (3, 10)
# pasta que tem um padrão sensato quando ninguém configura (marca.py usa ~/.beditor/marcas)
PASTAS_OPCIONAIS = ("marcas",)

# As fontes que `compor.py` carrega por caminho de arquivo. As demais (legenda,
# hook, HyperFrames) vêm do Google Fonts por CSS e só precisam de internet na
# hora do render — não há o que verificar em disco.
FONTES_LOCAIS = ("ArchivoBlack-Regular.ttf", "Inter.ttf", "IBMPlexMono-Medium.ttf", "Fraunces.ttf")
PASTA_FONTES = RAIZ_PLUGIN / "skills" / "beditor" / "public" / "fontes"

# O que cada pasta guarda — uma linha, a mesma que o `/sofia-estrategista-editora:setup` mostra ao
# perguntar, e a que o manual repete.
DESCRICAO_PASTAS = {
    "projetos": "uma pasta por vídeo: takes brutos, edicao/, oficina/ (cache). Dezenas de GB; fora do iCloud",
    "entregas": "masters e revisões prontos para assistir e publicar (entregar.py escreve aqui)",
    "musicas": "trilhas da biblioteca, por clima; o catálogo marca licença e procedência",
    "sfx": "efeitos sonoros curtos (whoosh, clique, impacto)",
    "overlays": "texturas, grão, vinhetas e outros vídeos de sobreposição",
    "logos": "marcas de produtos e canais citados (PNG com alpha)",
    "midia": "a midiateca: vídeos, imagens e áudios de terceiros baixados UMA vez e reusados entre projetos (midiateca.py)",
    "marcas": "opcional — uma subpasta por marca (sua, de cada cliente): manual, cores, fontes, escolhas de motion (marca.py). Sem ela, ~/.beditor/marcas",
    "render": "a oficina do HyperFrames: caminho curto, sem acento, ligado em ~/.beditor/render",
    "treinamento": "vídeos e frames de referência dos estilos aprendidos (2 GB e crescendo)",
}

# Instruções de instalação por item. Ficam aqui, e não espalhadas nos checks,
# para que `--instalar` e a tabela digam exatamente a mesma coisa.
# O gerenciador e o pip certos de cada sistema saem de `plataforma.py`: brew no
# Mac, winget no Windows, apt no Linux.
BREW = plataforma.instalar_sistema(["ffmpeg", "yt-dlp", "node"])
PIP = f"{plataforma.pip()} install pillow numpy opencv-python pyyaml"
PIP_WHISPER = f"{plataforma.pip()} install " + plataforma.pacotes_python_da_maquina()[0]
PIP_MEDIAPIPE = f"{plataforma.pip()} install mediapipe"
PIP_PLAYWRIGHT = f"{plataforma.pip()} install playwright && python3 -m playwright install chromium"
XCODE = "xcode-select --install   # abre um diálogo do macOS; pede confirmação na tela"
BIN = f"zsh '{RAIZ_PLUGIN}/skills/beditor/scripts/instalar_bin.sh'"
# O context-mode é o que faz a sessão investigar sem despejar bytes na conversa
# (LEI Nº 1 da casa). Sem ele o plugin funciona, mas cada pergunta sobre um
# arquivo custa o arquivo inteiro em tokens — no vídeo 16 isso foi 23% do gasto.
# Duas linhas numa só porque `--instalar` roda cada item como um comando.
CTX = ("claude plugin marketplace add mksglu/context-mode && "
       "claude plugin install context-mode@context-mode")
CTX_ATUALIZAR = "claude plugin update context-mode@context-mode"
if plataforma.sistema() == "windows":
    # sem `ln -s` (pede administrador no Windows): a pasta configurada já basta
    RENDER = r"py setup.py --pastas render=C:\beditor\render --criar   # caminho curto, sem espaço nem acento"
    ENV = "setx GEMINI_API_KEY <sua chave>   # reabra o terminal depois"
else:
    RENDER = "python3 setup.py --pastas render=/caminho/sem/acento   # e: ln -s /caminho/sem/acento ~/.beditor/render"
    ENV = f"mkdir -p {ENV_PADRAO.parent} && echo 'export GEMINI_API_KEY=<sua chave>' > {ENV_PADRAO} && chmod 600 {ENV_PADRAO}"


def _item(id_, nome, estado, detalhe="", instalar="", grupo="binários"):
    return {"id": id_, "nome": nome, "estado": estado, "detalhe": detalhe,
            "instalar": instalar, "grupo": grupo}


def _tem_modulo(nome):
    """Só pergunta se o pacote está instalado, sem importar: importar `cv2` ou
    `mlx_whisper` carrega bibliotecas pesadas e pode demorar segundos."""
    try:
        return importlib.util.find_spec(nome) is not None
    except (ImportError, ValueError):
        return False


def _tem_acento(caminho):
    return any(ord(c) > 127 for c in str(caminho))


def _chave_gemini_presente(env=ENV_PADRAO):
    """Presente/ausente, nunca o valor. Aceita `export X=...` ou `X=...`; um
    valor vazio conta como ausente."""
    if "GEMINI_API_KEY" in os.environ and os.environ["GEMINI_API_KEY"].strip():
        return True, "no ambiente"
    if not env.is_file():
        return False, f"{env} não existe"
    for linha in env.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"\s*(?:export\s+)?GEMINI_API_KEY\s*=\s*(.*)$", linha)
        if m and m.group(1).strip().strip("'\"") and not m.group(1).strip().startswith("<"):
            return True, f"em {env}"
    return False, f"{env} existe mas não define GEMINI_API_KEY"


def _plugin_claude(nome, home):
    """Versão instalada de um plugin do Claude Code, ou None.

    Lê o registro do próprio Claude Code (`installed_plugins.json`), onde a
    chave é `plugin@marketplace`. Registro ausente ou corrompido conta como não
    instalado: o setup não pode quebrar porque um JSON de outro programa mudou.
    """
    arq = Path(home) / ".claude" / "plugins" / "installed_plugins.json"
    try:
        d = json.loads(arq.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    for chave, insts in (d.get("plugins") or {}).items():
        if chave.split("@")[0] == nome and insts:
            return insts[0].get("version") or "instalado"
    return None


def verificar(which=shutil.which, tem_modulo=_tem_modulo, cfg=None, home=None,
              conferir_dataless=True):
    """O estado da máquina, como estrutura. `which`, `tem_modulo` e `home` são
    parâmetros para o teste simular uma máquina crua sem mexer na de verdade."""
    home = Path(home) if home else Path.home()
    casa = home / ".beditor"
    cfg = cfg or oficina.config()
    itens = []

    # --- Python -----------------------------------------------------------
    v = sys.version_info[:3]
    ok = v[:2] >= PYTHON_MINIMO
    itens.append(_item("python", "Python ≥ %d.%d" % PYTHON_MINIMO, "ok" if ok else "falta",
                       "%d.%d.%d em %s" % (*v, sys.executable),
                       "" if ok else "brew install python@3.12", grupo="python"))

    # --- binários ---------------------------------------------------------
    for b, obrig, detalhe in (("ffmpeg", True, "corta, extrai áudio, codifica tudo"),
                              ("ffprobe", True, "mede duração, fps e resolução"),
                              ("yt-dlp", True, "baixa o vídeo analisado e o material de acervo"),
                              ("node", False, "Remotion: só o fluxo `motion`"),
                              ("npx", False, "Remotion: só o fluxo `motion`")):
        caminho = which(b)
        estado = "ok" if caminho else ("falta" if obrig else "opcional")
        itens.append(_item(b, b, estado, caminho or detalhe, "" if caminho else BREW))

    # --- visão: o motor desta máquina (ver visao.py) ------------------------
    # Mac com Xcode: Vision, pelos dois binários Swift. Os dois NÃO são enfeite:
    # `render_analise.py` rastreia o rosto de todo take antes de compor, e marcá-los
    # «opcional» fazia a máquina nova passar no setup e morrer no primeiro render.
    # Windows, Linux e Mac sem Xcode: o motor portátil (YuNet do OpenCV + Selfie
    # Segmenter do MediaPipe), que pede o pacote `mediapipe`.
    mac = platform.system() == "Darwin"
    xcrun = which("xcrun") if mac else None
    if mac:
        itens.append(_item("swiftc", "xcrun swiftc (Vision local, macOS)",
                           "ok" if xcrun else "opcional",
                           xcrun or "compila o Vision da Apple, o melhor recorte local; "
                                    "sem ele o plugin usa o motor portátil",
                           "" if xcrun else XCODE))
    if mac and xcrun:
        for nome, para_que in (("recorte", "matte de pessoa (cartão atrás de você)"),
                               ("rastrear-rosto", "enquadramento pelo rosto")):
            bin_ = casa / "bin" / nome
            ok = bin_.is_file() and os.access(bin_, os.X_OK)
            itens.append(_item(f"bin-{nome}", f"~/.beditor/bin/{nome}", "ok" if ok else "falta",
                               str(bin_) if ok else
                               f"{para_que} — obrigatório no formato `analise`: o render para sem ele",
                               "" if ok else BIN))
    else:
        tem = tem_modulo("mediapipe")
        itens.append(_item("py-mediapipe", "python: mediapipe (motor de visão portátil)",
                           "ok" if tem else "falta",
                           "instalado" if tem else
                           "recorte de pessoa nesta máquina — obrigatório no formato `analise`",
                           "" if tem else PIP_MEDIAPIPE, grupo="python"))

    # --- pacotes Python ---------------------------------------------------
    for mod, pacote, obrig, detalhe in (("PIL", "pillow", True, "cartões, folhas de contato, capa"),
                                        ("numpy", "numpy", True, "medições de áudio e imagem"),
                                        ("cv2", "opencv-python", True,
                                         "leitura de quadros e máscaras no fluxo motion (motion-vox) e no painel"),
                                        ("yaml", "pyyaml", True, "critérios do painel e configs"),
                                        ("playwright", "playwright", False,
                                         "conferir_layout.py: screenshot das cenas HTML")):
        tem = tem_modulo(mod)
        estado = "ok" if tem else ("falta" if obrig else "opcional")
        instalar = "" if tem else (PIP if obrig else PIP_PLAYWRIGHT)
        itens.append(_item(f"py-{mod}", f"python: {pacote}", estado,
                           detalhe if not tem else "instalado", instalar, grupo="python"))

    # o motor recomendado depende da máquina (plataforma.transcricao): mlx-whisper no
    # Apple Silicon, faster-whisper no resto. Ter só um mais lento instalado não é
    # falta — o vídeo sai —, mas o setup mostra o comando do mais rápido
    motores = [m for m in ("mlx_whisper", "faster_whisper", "whisper") if tem_modulo(m)]
    recomendado = plataforma.transcricao()["motor"]
    tem_rec = recomendado.replace("-", "_") in motores
    alvo = plataforma.transcricao()
    itens.append(_item("py-whisper", "motor de transcrição",
                       "ok" if tem_rec else ("opcional" if motores else "falta"),
                       (f"usa {recomendado} ({alvo['device']}, {alvo['compute']})" if tem_rec else
                        f"usa {motores[0].replace('_', '-')}; nesta máquina o mais rápido é {recomendado}")
                       if motores else f"nenhum instalado; nesta máquina o mais rápido é {recomendado}",
                       "" if tem_rec else PIP_WHISPER, grupo="python"))

    # --- Claude Code ------------------------------------------------------
    ctx = _plugin_claude("context-mode", home)
    itens.append(_item("context-mode", "plugin context-mode", "ok" if ctx else "falta",
                       f"versão {ctx}" if ctx else
                       "a sessão investiga lendo arquivo inteiro para dentro da conversa; "
                       "com ele, roda no sandbox e traz só a resposta",
                       "" if ctx else CTX, grupo="claude code"))

    # --- casa: render, env, fontes ----------------------------------------
    render = casa / "render"
    if render.is_symlink() and not render.exists():
        itens.append(_item("render", "~/.beditor/render", "falta",
                           f"link para {os.readlink(render)}, que não existe (disco desconectado?)",
                           "conecte o disco, ou refaça o link: " + RENDER, grupo="casa"))
    elif render.is_dir():
        alvo = render.resolve()
        acento = _tem_acento(alvo)
        itens.append(_item("render", "~/.beditor/render", "falta" if acento else "ok",
                           str(alvo) + (" — o caminho real tem acento; o HyperFrames tropeça nisso" if acento else ""),
                           RENDER if acento else "", grupo="casa"))
    else:
        itens.append(_item("render", "~/.beditor/render", "falta",
                           "não existe: é a oficina de render (caminho curto, sem acento, no SSD)",
                           RENDER, grupo="casa"))

    presente, onde = _chave_gemini_presente(home / ".config" / "beditor" / "env")
    itens.append(_item("gemini", "GEMINI_API_KEY", "ok" if presente else "opcional",
                       ("presente " + onde) if presente else
                       "ausente — só a geração de imagem precisa; sem ela `assets.py` escreve os prompts",
                       "" if presente else ENV, grupo="casa"))

    faltam = [f for f in FONTES_LOCAIS if not (PASTA_FONTES / f).is_file()]
    itens.append(_item("fontes", "fontes locais (skills/beditor/public/fontes)",
                       "falta" if faltam else "ok",
                       ("faltam: " + ", ".join(faltam)) if faltam else
                       f"{len(FONTES_LOCAIS)} arquivos que compor.py carrega por caminho; legenda e hook usam Google Fonts (precisam de internet no render)",
                       f"git -C '{RAIZ_PLUGIN}' checkout -- skills/beditor/public/fontes" if faltam else "",
                       grupo="casa"))

    # --- pastas configuradas ----------------------------------------------
    pastas = []
    for nome in oficina.PASTAS:
        bruto = cfg["pastas"].get(nome)
        p = Path(os.path.expanduser(bruto)) if bruto else None
        existe = bool(p and p.exists())
        reg = {"nome": nome, "caminho": bruto or "", "configurada": bool(bruto), "existe": existe,
               "livre_gb": None, "dataless": None, "descricao": DESCRICAO_PASTAS[nome]}
        if existe:
            try:
                reg["livre_gb"] = round(shutil.disk_usage(p).free / 1e9, 1)
            except OSError:
                pass
            # Só a pasta de projetos: é onde o render abre arquivo grande, e é
            # onde um take evictado pelo iCloud trava tudo sem erro (SKILL.md,
            # «Nunca em ~/Documents»). As outras são pequenas ou só leitura.
            if nome == "projetos" and conferir_dataless and platform.system() == "Darwin":
                try:
                    reg["dataless"] = len(oficina.dataless(p))
                except OSError:
                    pass
        pastas.append(reg)

    resumo = {e: sum(1 for i in itens if i["estado"] == e) for e in ("ok", "falta", "opcional")}
    resumo["pastas_configuradas"] = sum(1 for p in pastas if p["configurada"])
    resumo["pastas_existem"] = sum(1 for p in pastas if p["existe"])
    return {"quando": datetime.now().isoformat(timespec="seconds"),
            "sistema": f"{platform.system()} {platform.release()} {platform.machine()}",
            "itens": itens, "pastas": pastas, "resumo": resumo, "config": cfg.get("_arquivo", "")}


def imprimir_verificacao(v):
    marca = {"ok": "ok      ", "falta": "FALTA   ", "opcional": "opcional"}
    print(f"bEditor · {v['sistema']} · config: {v['config']}\n")
    grupo = None
    for i in v["itens"]:
        if i["grupo"] != grupo:
            grupo = i["grupo"]
            print(f"[{grupo}]")
        print(f"  {marca[i['estado']]}  {i['nome']:<44} {i['detalhe']}")
        if i["instalar"] and i["estado"] != "ok":
            print(f"            → {i['instalar']}")
    print("\n[pastas]")
    for p in v["pastas"]:
        if not p["configurada"]:
            rotulo = "opcional" if p["nome"] in PASTAS_OPCIONAIS else "FALTA   "
            print(f"  {rotulo}  {p['nome']:<12} não configurada — {p['descricao']}")
            continue
        estado = "ok      " if p["existe"] else "FALTA   "
        extra = ""
        if p["livre_gb"] is not None:
            extra += f"  {p['livre_gb']} GB livres"
        if p["dataless"]:
            extra += f"  !! {p['dataless']} arquivo(s) evictados pelo iCloud (dataless): render vai travar"
        elif p["dataless"] == 0:
            extra += "  sem dataless"
        print(f"  {estado}  {p['nome']:<12} {p['caminho']}{'' if p['existe'] else '  (não existe)'}{extra}")
    r = v["resumo"]
    print(f"\n{r['ok']} ok · {r['falta']} faltando · {r['opcional']} opcionais · "
          f"pastas: {r['pastas_existem']}/{len(oficina.PASTAS)} existem")


def comandos_instalacao(v):
    """Os comandos de instalação do que falta, sem repetir, na ordem em que
    aparecem. Opcionais entram também: quem roda `--instalar` quer a máquina
    inteira, e a tabela já disse o que é opcional."""
    vistos, out = set(), []
    for i in v["itens"]:
        if i["estado"] != "ok" and i["instalar"] and i["instalar"] not in vistos:
            vistos.add(i["instalar"])
            out.append(i["instalar"])
    return out


def instalar(v, executar=False):
    cmds = comandos_instalacao(v)
    if not cmds:
        print("nada a instalar.")
        return
    print("comandos de instalação do que falta:\n")
    for c in cmds:
        print("  " + c)
    if not executar:
        print("\n(nada foi executado — repita com --sim para rodar; comandos marcados com "
              "«pede confirmação na tela» ou que pedem caminho seu não rodam sozinhos)")
        return
    for c in cmds:
        # Comandos que precisam de uma decisão humana (um caminho, um diálogo do
        # sistema, uma chave) só se imprimem: rodá-los às cegas cria pasta errada
        # ou grava placeholder como se fosse chave.
        if "<" in c or "xcode-select" in c or "/caminho/" in c or "conecte o disco" in c:
            print(f"\n[manual] {c}")
            continue
        print(f"\n$ {c}", flush=True)
        r = subprocess.run(c, shell=True)
        if r.returncode:
            print(f"!! saiu com {r.returncode}; o resto continua")


def atualizar(executar=False, raiz=RAIZ_PLUGIN):
    """Põe o bEditor e o context-mode na versão de hoje, em um comando.

    Duas instalações, dois jeitos de atualizar, e o script escolhe sozinho: quem
    clonou o repositório atualiza pelo git; quem instalou pelo marketplace do
    Claude Code atualiza pelo `claude plugin update` (a cópia em `plugins/cache`
    não é um clone, e um `git pull` ali só erraria).

    `--ff-only` de propósito: se houver trabalho local não commitado ou um
    histórico divergente, o pull falha em vez de embaralhar o repositório de
    quem está no meio de uma edição. A mensagem do git já diz o que fazer.
    """
    proprio = (f"git -C '{raiz}' pull --ff-only" if (Path(raiz) / ".git").exists()
               else "claude plugin update sofia-estrategista-editora@sofia-editora")
    cmds = [proprio, CTX_ATUALIZAR]
    print("atualizando:\n")
    for c in cmds:
        print("  " + c)
    if not executar:
        print("\n(nada foi executado — repita com --sim)")
        return cmds
    for c in cmds:
        print(f"\n$ {c}", flush=True)
        r = subprocess.run(c, shell=True)
        if r.returncode:
            print(f"!! saiu com {r.returncode}; o resto continua")
    return cmds


ARTEFATOS = {
    "mesa": "a Mesa de decupagem (modelo: painel/mesa.html) — onde toda etapa vai para a tela",
    "painel": "o painel com banco (modelo: painel/index.html, gerado por painel/gerar.py) — pedidos, conversa, revisão",
}


def artefato(pedido, caminho=None):
    """`nome` → devolve o endereço gravado (ou ""); `nome=url` → grava.

    Cada pessoa tem a SUA mesa e o SEU painel: artifact só é atualizado pela
    conta dona, e um endereço fixo no plugin apontava todo mundo para os do
    autor. O endereço mora no config desta máquina, como as pastas."""
    nome, sep, url = pedido.partition("=")
    nome = nome.strip()
    if nome not in ARTEFATOS:
        raise SystemExit(f"!! artefato desconhecido «{nome}». Válidos: {', '.join(ARTEFATOS)}")
    cfg = oficina.config(caminho)
    arquivo = Path(cfg.pop("_arquivo"))
    if not sep:
        return (cfg.get("artefatos") or {}).get(nome, "")
    url = url.strip()
    if not url.startswith("https://"):
        raise SystemExit(f"!! «{url}» não é um endereço de artifact (https://…)")
    cfg.setdefault("artefatos", {})[nome] = url
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return url


def gravar_pastas(pares, criar=False, canal=None, caminho=None):
    """Mescla `nome=caminho` no config. Guarda o que o usuário digitou (com `~`
    se ele usou); a expansão acontece na leitura, em `oficina.pasta()`."""
    cfg = oficina.config(caminho)
    arquivo = Path(cfg.pop("_arquivo"))
    for par in pares or []:
        nome, _, valor = par.partition("=")
        nome, valor = nome.strip(), valor.strip()
        if nome not in oficina.PASTAS:
            raise SystemExit(f"!! pasta desconhecida «{nome}». Válidas: {', '.join(oficina.PASTAS)}")
        if not valor:
            raise SystemExit(f"!! `{par}`: faltou o caminho depois do «=»")
        p = Path(os.path.expanduser(valor))
        if criar:
            p.mkdir(parents=True, exist_ok=True)
        elif not p.exists():
            print(f"aviso: {nome} = {p} não existe ainda (use --criar para criar)")
        cfg["pastas"][nome] = valor
    for par in canal or []:
        chave, _, valor = par.partition("=")
        if chave.strip() not in ("nome", "arroba"):
            raise SystemExit(f"!! canal aceita nome=... e arroba=..., não «{chave}»")
        cfg["canal"][chave.strip()] = valor.strip()
    cfg["versao"] = cfg.get("versao") or 1
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"gravado em {arquivo}")
    for nome in oficina.PASTAS:
        print(f"  {nome:<12} {cfg['pastas'].get(nome, '(não configurada)')}")
    return arquivo


def _frontmatter(texto):
    m = re.match(r"---\n(.*?)\n---", texto, re.S)
    out = {}
    if not m:
        return out
    for linha in m.group(1).splitlines():
        k, sep, v = linha.partition(":")
        if sep and not linha.startswith((" ", "\t")):
            out[k.strip()] = v.strip()
    return out


def comandos_do_plugin(raiz=RAIZ_PLUGIN):
    """Nome, descrição e argumentos de cada `commands/*.md`, lidos do frontmatter
    — a mesma fonte que o Claude Code lê, para o manual nunca listar um comando
    que não existe."""
    out = []
    for f in sorted((raiz / "commands").glob("*.md")):
        fm = _frontmatter(f.read_text(encoding="utf-8"))
        out.append({"nome": f.stem, "descricao": fm.get("description", ""),
                    "argumentos": fm.get("argument-hint", "")})
    return out


def referencias_do_plugin(raiz=RAIZ_PLUGIN):
    out = []
    for f in sorted((raiz / "skills" / "beditor" / "referencias").glob("*.md")):
        titulo = next((l[2:].strip() for l in f.read_text(encoding="utf-8").splitlines()
                       if l.startswith("# ")), f.stem)
        out.append({"arquivo": f.name, "titulo": titulo})
    return out


def versao_do_plugin(raiz=RAIZ_PLUGIN):
    v = {"versao": "", "commit": "", "repo": str(raiz)}
    pj = raiz / ".claude-plugin" / "plugin.json"
    if pj.is_file():
        try:
            v["versao"] = json.loads(pj.read_text(encoding="utf-8")).get("version", "")
        except json.JSONDecodeError:
            pass
    try:
        r = subprocess.run(["git", "-C", str(raiz), "log", "-1", "--format=%h %cs"],
                           capture_output=True, text=True, timeout=10, encoding="utf-8", errors="replace")
        v["commit"] = r.stdout.strip() if r.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        pass
    return v


def dados_do_manual(verificacao=None, cfg=None, raiz=RAIZ_PLUGIN):
    cfg = dict(cfg or oficina.config())
    cfg.pop("_arquivo", None)
    return {"gerado_em": datetime.now().isoformat(timespec="seconds"),
            "plugin": versao_do_plugin(raiz),
            "config": cfg,
            "descricao_pastas": DESCRICAO_PASTAS,
            "verificacao": verificacao or verificar(cfg=oficina.config()),
            "comandos": comandos_do_plugin(raiz),
            "referencias": referencias_do_plugin(raiz)}


def gerar_manual(destino=None, dados=None, template=TEMPLATE_MANUAL):
    """Substitui o marcador único do template pelo JSON. `</` vira `<\\/` para
    que nenhum texto do JSON feche o <script> por acidente."""
    if not template.is_file():
        raise SystemExit(f"!! template não encontrado: {template}")
    html = template.read_text(encoding="utf-8")
    if MARCADOR not in html:
        raise SystemExit(f"!! o template não tem o marcador {MARCADOR}")
    js = json.dumps(dados or dados_do_manual(), ensure_ascii=False).replace("</", "<\\/")
    destino = Path(os.path.expanduser(destino or MANUAL_PADRAO))
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(html.replace(MARCADOR, js, 1), encoding="utf-8")
    return destino


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--verificar", action="store_true", help="checa dependências, pastas e a casa")
    ap.add_argument("--json", action="store_true", help="com --verificar: sai como JSON")
    ap.add_argument("--pastas", nargs="+", metavar="nome=caminho", help="grava/mescla pastas no config")
    ap.add_argument("--artefato", metavar="nome[=url]",
                    help="mesa ou painel: sem =url imprime o endereço desta conta (vazio se não há); com =url grava")
    ap.add_argument("--criar", action="store_true", help="com --pastas: cria a pasta se não existir")
    ap.add_argument("--canal", nargs="+", metavar="nome=...|arroba=...")
    ap.add_argument("--instalar", action="store_true", help="imprime os comandos do que falta")
    ap.add_argument("--sim", action="store_true", help="com --instalar/--atualizar: executa os comandos")
    ap.add_argument("--atualizar", action="store_true",
                    help="puxa a versão nova do plugin e do context-mode")
    ap.add_argument("--manual", nargs="?", const=str(MANUAL_PADRAO), metavar="caminho",
                    help=f"gera o manual (padrão: {MANUAL_PADRAO})")
    ap.add_argument("--tudo", action="store_true", help="--verificar e --manual")
    ap.add_argument("--sem-dataless", action="store_true",
                    help="não varre a pasta de projetos atrás de arquivos evictados (mais rápido)")
    a = ap.parse_args(argv)

    if a.artefato:
        print(artefato(a.artefato))
        return
    if a.pastas or a.canal:
        gravar_pastas(a.pastas, criar=a.criar, canal=a.canal)

    precisa_verificar = a.verificar or a.instalar or a.tudo or a.manual is not None
    v = verificar(conferir_dataless=not a.sem_dataless) if precisa_verificar else None

    if a.verificar or a.tudo:
        if a.json:
            print(json.dumps(v, ensure_ascii=False, indent=2))
        else:
            imprimir_verificacao(v)
    if a.instalar:
        instalar(v, executar=a.sim)
    if a.atualizar:
        atualizar(executar=a.sim)
    if a.manual is not None or a.tudo:
        destino = gerar_manual(a.manual if a.manual is not None else None,
                               dados_do_manual(verificacao=v))
        print(f"\nmanual: {destino}")
    if not (a.pastas or a.canal or precisa_verificar or a.atualizar):
        ap.print_help()


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
