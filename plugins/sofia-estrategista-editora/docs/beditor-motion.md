# bEditor: motion, decupagem, finalização e publicação

> Esta é a parte que veio do plugin bEditor original e agora faz parte da Sofia
> Estrategista. Licença: [LICENSE](../LICENSE). Instalação do plugin inteiro:
> [README](../README.md).

Skills `beditor` e `motion-vox`, comandos e ajudantes que editam vídeo vertical 9:16 a partir de um take ou de **fala com
timestamp**: decupagem, guia de edição, motion graphics, legenda e master, com a voz em
sincronia com a boca. Cada etapa é um script em uma chamada, com cache pelo conteúdo.

## Requisitos

| O quê | Para quê | Instalar |
| --- | --- | --- |
| Python ≥ 3.10 | todos os scripts | `brew install python@3.12` |
| `ffmpeg`, `ffprobe` | cortar, medir, codificar | `brew install ffmpeg` |
| `yt-dlp` | baixar o vídeo analisado e acervo | `brew install yt-dlp` |
| Pillow, numpy, opencv-python, pyyaml | cartões, folhas, medições, configs | `pip3 install pillow numpy opencv-python pyyaml` |
| um motor de transcrição | `transcrever.py` | `pip3 install mlx-whisper` (Apple Silicon) ou `faster-whisper` |
| `node`/`npx` | opcional: Remotion, só o fluxo `motion` | `brew install node` |
| `xcrun swiftc` | opcional, macOS: matte de pessoa e rosto (Vision local) | `xcode-select --install`, depois `zsh skills/beditor/scripts/instalar_bin.sh` |
| `playwright` | opcional: screenshot das cenas HTML | `pip3 install playwright && python3 -m playwright install chromium` |
| `GEMINI_API_KEY` | opcional: geração de imagem; sem ela `assets.py` escreve os prompts | `~/.config/beditor/env` com `export GEMINI_API_KEY=...` |
| plugin `context-mode` | a sessão investiga sem despejar arquivo na conversa (23% do custo do vídeo 16) | `claude plugin marketplace add mksglu/context-mode && claude plugin install context-mode@context-mode` |
| um SSD (ou pasta fora do iCloud) | projetos, entregas, oficina de render | qualquer caminho; `render` sem acento |

`python3 skills/beditor/scripts/setup.py --verificar` confere tudo isso e diz o comando
de cada item que falta.

## Instalar

Instale o plugin Sofia Estrategista como diz o [README](../README.md).

Depois, no Claude Code: **`/sofia-estrategista-editora:setup`**. Ele confere as dependências (e diz o
comando de cada uma que falta), pergunta onde ficam as suas pastas — projetos,
entregas, músicas, SFX, overlays, logos, render, treinamento —, grava a configuração
e gera o manual em `~/.beditor/manual.html`.

Se preferir clonar em vez de instalar pelo marketplace (para mexer no código), o
plugin funciona igual: clone **fora de `~/Documents` e da Mesa** — o iCloud tira
arquivo grande do disco e o render trava esperando — e abra com
`claude --plugin-dir CAMINHO_DO_CLONE`.

Sem Claude, o mesmo por linha de comando, na raiz do plugin:

```bash
python3 skills/beditor/scripts/setup.py --verificar
python3 skills/beditor/scripts/setup.py --instalar          # mostra; --sim executa
python3 skills/beditor/scripts/setup.py --pastas projetos=/Volumes/SSD/Projetos entregas=/Volumes/SSD/Entregas --criar
python3 skills/beditor/scripts/setup.py --manual            # → ~/.beditor/manual.html
```

**Antes do primeiro vídeo, conecte o disco** das pastas configuradas. Se uma não
estiver montada, os scripts param e dizem qual, em vez de criar uma cópia no disco
interno.

## Mac, Windows e Linux

O plugin escolhe sozinho o caminho mais eficiente de cada máquina
(`python3 skills/beditor/scripts/plataforma.py` mostra o que vai usar):

| | Mac Apple Silicon | Windows / Linux |
| --- | --- | --- |
| transcrição | mlx-whisper, na GPU | faster-whisper em CUDA com NVIDIA; senão CPU |
| rosto e recorte de pessoa | Vision da Apple (`instalar_bin.sh`) | YuNet do OpenCV + MediaPipe, em CPU |
| prévia de revisão | VideoToolbox | NVENC, Quick Sync ou AMF, se funcionar; senão x264 |
| instalar | brew | winget (Windows), apt (Linux) |

O master sai em libx264 CRF 15 em todas — é o que permite montar o vídeo por
trechos sem recodificar.

## Marcas

Marca não vem com o plugin: é sua, e você pode ter várias (a sua e a de cada
cliente). `marca.py nova "<nome>"` cria, `marca.py usar <nome> --projeto <pasta>`
liga ao projeto, `marca.py mostrar` diz qual vale. Sem marca, vale o estilo da casa.

## Estilos aprendidos e os seus

O plugin traz o que foi aprendido nos estilos da casa — números medidos e a leitura
de cada um em `treinamento/<estilo>/` —, nunca o material de estudo: nenhum vídeo,
frame, folha de contato, nome de perfil ou link de post.

Para treinar o seu: `/sofia-estrategista-editora:aprender-motion <pasta de frames ou vídeos> <nome>`. O
material de referência e a procedência (de quem é, de onde veio) ficam na sua pasta
`treinamento`; o estilo vira opção da galeria.

## Primeiro vídeo

| Você tem | Comando |
| --- | --- |
| um take de câmera falando | `/sofia-estrategista-editora:cortar take.mov` — e depois `/sofia-estrategista-editora:motion-graficos`, `/sofia-estrategista-editora:finalizar` |
| um comentário sobre o vídeo de outra pessoa | `/sofia-estrategista-editora:editar-analise "Projetos/01 - Nome/"` |
| o master pronto e quer publicar | `/sofia-estrategista-editora:publicar entrega/master.mp4` |
| dúvida sobre o que existe | `~/.beditor/manual.html` — aba Fluxos, cada passo com o comando que roda |

Cada etapa entrega um arquivo em disco e para para você aprovar. Nada é publicado
sem o seu sim explícito na conversa.

## Atualizar

Um comando põe o plugin e o context-mode na versão de hoje:

```bash
python3 skills/beditor/scripts/setup.py --atualizar --sim
```

Quem instalou pelo marketplace atualiza pelo próprio marketplace
(`claude plugin update sofia-estrategista-editora@sofia-editora`); o `--atualizar`
serve para quem trabalha num clone.

Sem `--sim` ele só mostra o que faria. O `git pull` é `--ff-only`: havendo
trabalho local não commitado, ele para em vez de embaralhar o repositório.

## Onde a configuração fica

`~/.config/beditor/config.json` (ou o arquivo apontado por `BEDITOR_CONFIG`):

```json
{"versao": 1,
 "pastas": {"projetos": "...", "entregas": "...", "musicas": "...", "sfx": "...",
            "overlays": "...", "logos": "...", "render": "~/.beditor/render", "treinamento": "..."},
 "canal": {"nome": "...", "arroba": "..."}}
```

Escrito por `setup.py --pastas` (mescla, não sobrescreve), lido por `oficina.config()` e
`oficina.pasta(nome)`. **Tudo que era caminho da máquina do autor agora vem daqui**;
pasta não configurada para com a instrução de rodar o setup, nunca inventa um caminho.
A chave da Gemini fica em `~/.config/beditor/env` e nunca aparece em log nem no manual.

## O que está aqui

```
skills/beditor/SKILL.md      o procedimento — leia primeiro
skills/beditor/referencias/  a grade medida, o ritmo, as classes, os formatos, as rotas, os prompts
skills/beditor/scripts/      setup.py, transcrever.py, silencio.py, render_analise.py, qa_analise.py,
                             montar.py, compor.py, plano.py, assets.py, entregar.py, oficina.py ...
skills/beditor/template/     projeto Remotion completo (grade, legenda, movimento, tipos de plano)
agents/                      diretor, enriquecedor, analista-de-estilo
commands/                    /sofia-estrategista-editora:setup, analise, dirigir, cortar, motion-graficos, finalizar,
                             publicar, motion, plano, aprender, qa, branding, painel, montar
docs/manual.html             o template do manual interativo que o setup preenche
```

## Fluxos

**Take de câmera, em etapas aprovadas uma a uma:** `/sofia-estrategista-editora:dirigir take.mov` (guia) →
`/sofia-estrategista-editora:cortar` (decupagem) → `/sofia-estrategista-editora:motion-graficos` → `/sofia-estrategista-editora:finalizar` →
`/sofia-estrategista-editora:publicar`. Cada etapa entrega algo para você ver antes da seguinte.

**Formato `analise`** (comentário sobre a peça de outra pessoa): `/sofia-estrategista-editora:editar-analise
<projeto>` roda transcrever → cortar (`dados.json`, `silencio.py`) → renderizar
(`plano.json`, `render_analise.py`) → medir (`qa_analise.py`) → entrega, e um ajuste
refaz só o que tocou.

**Do transcript ao MP4 em Remotion:**

```bash
BED="CAMINHO_DO_PLUGIN/skills/beditor"
python3 $BED/scripts/plano.py --falas falas.srt --out motion/          # 1. ritmo: transcript -> plano
python3 $BED/scripts/aplicar.py --projeto motion/ --enriquecimento enriquecimento.json   # 2. agente enriquecedor
python3 $BED/scripts/assets.py --projeto motion/                       # 3. imagens, ou os prompts
bash $BED/scripts/projeto.sh motion/ && cd motion && npx remotion render Video out/master.mp4  # 4-5
```

Para ensinar um estilo novo a partir de referências:

```bash
python3 $BED/scripts/aprender.py --frames referencias/ --nome meu-estilo --out estilos/
python3 $BED/scripts/plano.py --falas falas.srt --out motion/ --estilo estilos/meu-estilo/medicoes.json
```

Dentro do Claude Code: `/sofia-estrategista-editora:motion falas.srt`, `/sofia-estrategista-editora:plano falas.srt`,
`/sofia-estrategista-editora:aprender-motion referencias/ meu-estilo`, `/sofia-estrategista-editora:qa out/master.mp4`,
`/sofia-estrategista-editora:branding` (define o padrão visual do canal para as situações que se repetem).

## De onde vieram os números

A grade do preset `noturno` não foi escolhida: foi medida em 2.623 frames de referência,
por 12 leituras independentes que convergiram nos mesmos valores. Está em
`referencias/linguagem-visual.md` e é reproduzida pelo template.

## Vizinhança

`corte-viral` entrega o vertical limpo · `motion-vox` faz a identidade editorial de papel
· `remotion-to-hyperframes` leva a composição para render hospedado.

## Onde o código mora

O plugin fica onde o Claude ou o Codex o instalou; um clone para desenvolver fica onde
você quiser, fora do iCloud. A regra é uma: **o que a skill lê vai
para o repo; o que ela produz vai para o SSD** (as pastas do `config.json`). A tabela
completa está em `skills/beditor/SKILL.md`, seção "Onde ficam as coisas".
