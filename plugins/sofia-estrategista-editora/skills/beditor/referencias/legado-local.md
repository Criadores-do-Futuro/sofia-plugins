---
name: bEditor
description: Edita vídeo vertical 9:16 a partir de um take ou de fala com timestamp — decupagem, guia de edição, motion graphics narrativo, legenda e master, com a voz em sincronia com a boca. Use quando o pedido for "edita esse take", "corta os silêncios", "faz o motion desse roteiro", "ilustra o que estou falando", "gera os visuais desse áudio/transcrição", "monta o vídeo com os cortes e as cartelas", "anima essas imagens", "cria b-roll para esse trecho", "tela dividida com o apoio em cima", ou quando existir um SRT/JSON de palavras e o resultado esperado for vídeo com cartela, cutaway, objeto-símbolo, infográfico, colagem documental, whiteboard, B-roll gerado ou legenda queimada. Roteia cada plano entre HyperFrames (texto, dado, tempo exato) e Gemini (matéria, footage), com fatos confirmados e custo aprovado antes de gerar. NÃO corta vídeo longo em clipes (isso é a skill corte-viral) e NÃO copia a identidade visual de terceiros.
effort: high  # campo do Claude Code; o Codex ignora a chave, não a apague
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---

# bEditor — fala com timestamp → motion graphics

Você recebe **o que está sendo dito e quando**. Devolve **o que se vê enquanto isso é
dito**, renderizado, no ritmo certo, com o texto legível.

O trabalho tem uma ordem fixa. Cada etapa produz um artefato em disco. Não pule etapa e
não improvise fora do artefato — o que não está no `plano.json` não entra no vídeo.

```
falas.srt  ──1──▶  plano.json  ──2──▶  plano enriquecido  ──3──▶  assets/  ──4──▶  Remotion  ──5──▶  master.mp4
             ritmo              pesquisa do mundo real       rota por plano     composição        grade
```

## Antes de tudo: qual é o preset

Duas identidades fechadas. Escolha uma na primeira frase da conversa e não misture.

| Preset | Quando | Assinatura |
| --- | --- | --- |
| `noturno` | canal escuro, ensaio, tese, "isso tem nome:" | fundo 12/255, sujeito 200–210/255, aberração 2–5px, grão, vinheta forte |
| `editorial` | explicação, dado, história com fonte | papel `#D9D8D1`, tinta `#373639`, fita amarela, boil, sombra de contato |

O `editorial` já existe pronto e melhor na skill **motion-vox** (motor procedural em
PIL, fontes embarcadas). Se o pedido for editorial de papel, **use motion-vox** e pare
aqui. O bEditor existe para o `noturno` e para tudo que precisa de **código gerando
forma** — cartela, dado, UI, objeto-símbolo, parallax 2.5D.

Os números do `noturno` não são estimativa: saíram de 12 leituras independentes de
frames reais. Estão em `referencias/linguagem-visual.md` — leia antes de compor.

## 0. Dirigir — o guia decide, o plano desenha

Havendo take filmado, o pipeline começa pelo **diretor**, não pelo `plano.py`.
Antes dele, **o take sai do HDR**: iPhone grava HLG, e o sinal HLG copiado para
H.264 de 8 bits deixa a pele pálida e amarelada. Foi o que aconteceu nos
proxies e revisões dos projetos 05 e 07. O `sdr.py` converte pelo `avconvert`
da Apple (este ffmpeg não tem `zscale`), devolve o áudio original sem
recompressão, confere o relógio, e o `montar.py` recusa take HDR:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/sdr.py brutos/take.mov   # → brutos/take.sdr.mov
/sofia-estrategista-editora:dirigir         brutos/take.sdr.mov   # folhas de contato → agente diretor → guia validado → GUIA.md
/sofia-estrategista-editora:cortar          brutos/take.sdr.mov   # etapa 1: decupagem + J-cut, para o editor revisar
/sofia-estrategista-editora:motion-graficos brutos/take.sdr.mov   # etapa 2: motion sobre o corte aprovado
/sofia-estrategista-editora:finalizar       brutos/take.sdr.mov   # etapa 3: cama, legenda, grade, master
/sofia-estrategista-editora:montar          brutos/take.sdr.mov   # tudo de uma vez (quando o editor não quer revisar por etapa)
/sofia-estrategista-editora:publicar        entrega/master.mp4    # etapa 4: título, descrição e capa para busca e clique; um agendamento para todas as redes
/sofia-estrategista-editora:painel                                # lê a fila do painel (pedidos, conversa, fontes de B-roll) e refaz só o pedaço pedido
```

**Investigar é com o context-mode, sempre que der.** Editar um vídeo é ler
muito mais do que escrever: transcrição, plano, manifesto, log de render, JSON
de prova. Ler isso com `cat`, `grep` ou `Read` põe o arquivo inteiro dentro da
conversa e o custo fica lá até o fim da sessão — foi 23% do gasto do vídeo 16.
Então:

| Intenção | Ferramenta |
| --- | --- |
| investigar (rodar comando e perguntar da saída) | `ctx_batch_execute(commands, queries)` |
| perguntar sobre o que já foi indexado | `ctx_search(queries: [...])` |
| filtrar, contar, medir, transformar | `ctx_execute` / `ctx_execute_file` |
| buscar uma página | `ctx_fetch_and_index` |
| escrever ou editar arquivo | `Write` / `Edit` — nunca por subprocesso |
| mudar estado (git, ffmpeg, render, mkdir) | `Bash` |

**Pergunta que pode ser agrupada, agrupa**: `commands` e `queries` são listas, e
cinco perguntas numa chamada custam uma ida e volta, não cinco. Sem o plugin
instalado (`setup.py --verificar` acusa), o trabalho continua — só mais caro.

**A revisão sai numa mesa só, e ela já existe.** Toda etapa que for para a tela
entra na **Mesa de decupagem** desta conta — o endereço sai de
`setup.py --artefato mesa` (vazio na primeira vez: publique o modelo
`painel/mesa.html` uma vez e grave o endereço) — lida antes, editada em cima do
que voltou, e republicada **no mesmo URL**. Publicar
artifact novo joga fora as ferramentas de edição que estão lá dentro (roda de
precisão, lâmina com ripple, silêncios, J-cut com trava, cor com ffmpeg, hook).
Regra e procedimento em `referencias/mesa-de-decupagem.md`.

**O trabalho é entregue por partes, e cada parte é aprovada antes da
seguinte.** Julgar corte, desenho e acabamento no mesmo preview mistura três
conversas: o editor diz "não gostei" e ninguém sabe de qual das três camadas.
Por isso a etapa 1 não tem motion, a etapa 2 não tem música, legenda nem
grade, e a etapa 3 é a única que fecha. Cada aprovação vira um arquivo em
`edicao/aprovado/` (`corte`, `motion`), e o que já foi aprovado não é refeito:
o corte só é recortado de novo se a tabela mudou, e a imagem de um momento só
é regerada se a ideia mudou. Ajuste sempre no `guia/guia.json` — nunca no
vídeo, nunca no `plano.json` à mão.

A regra do pipeline: **o diretor decide, o enriquecedor confirma, a skill
executa.** O `guia/guia.json` é a fonte de verdade; `plano.json` é derivado
dele pelo `montar.py`. Nada é declarado pronto sem `medir.py` passar (preto,
cobertura, loudness). Os scripts: `sdr.py` (take HDR → SDR, antes de tudo),
`contato.py` (frases com medidas + folhas de contato 9:16), `validar.py`
(regras do guia), `gerar_guia_md.py`, `direcao.py` (estilo de motion do vídeo e prompt de cada cena), `estilos.py` (a galeria de estilos de hook, legenda, música e SFX), `montar.py`, `compor.py` (o
renderizador: Pillow desenha, ffmpeg compõe — sem navegador), `medir.py`,
`travas.py`, `acabamento.py`, `cor.py` (a grade do A-roll em dez números, com
preferência do canal), `trilha.py`, `publicacao.py` (etapa 4: valida
título e texto por rede, desenha a capa, monta um agendamento para todas as
redes), `enquadrar_rosto.py` (tela
dividida: rastreamento do rosto → keyframes de enquadramento e intervalos de
matte). As ferramentas Swift (`recorte`, `rastrear-rosto`) rodam o Vision
localmente e são compiladas por `scripts/instalar_bin.sh` em `~/.beditor/bin`.
Testes: `python3 -m unittest discover -s skills/beditor/tests`.

**O transcript mente sobre gagueira.** O Whisper limpa disfluência de propósito,
e nenhum parâmetro desliga isso: uma frase começada, travada e recomeçada chega
ao texto como se tivesse sido dita uma vez só — num take medido, 2,8 s de fala,
pausa e retomada viraram a palavra `«treinar»`. Por isso `escutar.py` procura no
**áudio**, não no texto: palavra longa demais com dois blocos de voz dentro é
falsa partida, e o corte proposto vai do início da tentativa até a retomada.
O `contato.py` roda isso sozinho e põe o resultado no topo do `fala.md` e em
`guia/escuta.json`; o diretor transforma cada achado num momento `cortar`.
Anáfora não conta (frase que fechou com ponto chegou onde queria).

**O transcript também engole trechos inteiros.** No 22 (2026-09-28), 13 s de
fala viraram duas palavras (`inteligência` com 7,9 s, `artificial` com 5,5 s) —
a legenda ficaria parada e o texto sumiria. Depois de transcrever, liste as
palavras com mais de 2 s; em cada uma, recorte só aquele trecho (±2 s), rode o
`transcrever.py` nele e costure as palavras no json (guarde o original em
`*.whisper.orig.json`). Nomes que o Whisper não conhece (ex.: "JEV") ficam como
falados e vão para a pergunta ao dono na prévia.

**Correção de cor.** A grade do A-roll são dez números (`cor.py`), e eles vêm de
três lugares — o mais específico manda: `guia.cor` (este vídeo), depois
`~/.beditor/cor.json` (a preferência do canal, que atravessa os vídeos), depois
a grade de fábrica. O editor ajusta na mesa de decupagem da etapa 1 e marca se
quer guardar como preferência; gravar de fora é
`python3 scripts/cor.py --salvar ficha.json --nota "por quê"`. O painel mostra a
grade ao vivo por aproximação em CSS e, ao lado, quadros renderizados de verdade
— **quem decide o pixel é o ffmpeg**, e é neles que se confere antes de salvar.

**Renderizador.** O padrão é **HyperFrames** (`hf.py`): cada plano vira um HTML
autocontido com GSAP, na gramática medida do treinamento — meio-tom, grão,
vinheta, rims âmbar e ciano, revelação por máscara, curvas `power4.out`. O
`montador.py` costura os clipes com o A-roll: no modo storytelling o motion toma
a tela inteira, então cada faixa de tempo tem um dono só, sem canal alpha.

A alternativa é `compor.py` (`--renderizador pillow`): desenha quadro a quadro
com Pillow e aplica a grade no ffmpeg. Não precisa de Node nem navegador — é o
caminho de conserto quando o HyperFrames falha. O Remotion saiu do caminho
padrão: travava em bundling neste ambiente.

**Armadilha registrada:** o `npx hyperframes` trava sem mensagem quando o
diretório de trabalho tem parênteses ou acentos, e todo projeto de vídeo tem. O
`hf.py` renderiza numa oficina de caminho neutro e copia o MP4 de volta.

Todo render roda com vigia: processo sem progresso por 4 min é morto e
investigado, nunca esperado.

As cenas renderizam **em paralelo** (`--paralelo`, padrão: núcleos até o teto de 4).
Cada cena tem oficina própria e sobe o próprio browser, então não há nada
compartilhado entre elas — o laço era sequencial por construção, não por
necessidade, e num vídeo de 40 cenas eram 40 subidas de browser em fila. O teto de 4
é de memória, não de CPU: quatro páginas 1080×1920 é o que uma máquina de edição
aguenta sem paginar. Uma cena que falha não derruba as outras; o erro sai no fim,
nomeando quem falhou.

**Prompt de imagem.** A ideia do diretor vira prompt pelo molde da classe em
`referencias/prompts-assets.md` — cena fotográfica de quadro cheio, com lente,
luz e sombra, não ícone flutuando no preto. A mão que segura a ficha, a
plateia inteira, a parede de fichários: é isso que a linguagem pede. Texto,
número e interface nunca vão ao gerador (ele erra glifo e inventa cifra) —
são desenhados em código. Cada imagem gerada guarda o prompt que a gerou em
`<ID>.prompt.txt`; mudou a ideia, a imagem é refeita sozinha.

O caminho abaixo, por `plano.py`, continua existindo para áudio **sem** take
(100% motion) — o diretor ainda não cobre esse caso.

## 1. Ritmo — do transcript ao plano

> Com take filmado, use a seção 0. Esta é a rota legada para áudio sem vídeo.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/plano.py \
  --falas falas.srt --preset noturno --out projeto/ \
  --video original.mp4
```

**`--video` muda o vídeo inteiro, e é a opção certa quase sempre.** Com material
filmado, o padrão de cada plano passa a ser `fala` — você na tela — e o motion graphics
só entra onde ilustra alguma coisa. Sem `--video`, tudo vira motion graphics: só faça
isso quando a entrada for áudio puro, sem imagem de quem fala.

O vídeo original também vira a **trilha de áudio** da composição inteira, contínua por
baixo dos cortes. Os planos de motion graphics entram por cima sem picotar a voz.

Se o transcript não começa no segundo zero do original, informe `--video-offset-ms`.

Aceita `.srt`, `.vtt`, ou JSON do Whisper com `words[]`. Emite:

- `projeto/plano.json` — a lista de planos com `t0/t1`, tipo, texto e prompt
- `projeto/public/captions.json` — `Caption[]` do `@remotion/captions`, palavra a palavra

O script corta **onde a voz respira** (silêncio ≥ 180 ms), nunca onde a gramática fecha.
Depois **você revisa o plano** — é aqui que a inteligência entra, não no script:

1. Abra `plano.json`. Para cada plano, pergunte: *o que esta frase pede que se veja?*
2. Corrija `tipo` (as 12 classes estão em `referencias/catalogo-visual.md`).
3. Escreva `texto` — 2 a 4 palavras, caixa baixa, a **coisa** dita, não um resumo dela.
4. Escreva `prompt` só para os tipos que precisam de imagem.
5. Regra dura: **nenhuma classe visual se repete por mais de 4 segundos seguidos.**

As regras de duração, gancho e densidade estão em `referencias/ritmo.md`. Elas são o
que separa "bonito" de "prende" — leia antes de mexer no plano.

O script marca `pesquisar: true` nos planos com âncora verificável — nome, ano, estudo,
instituição. Se houver algum, **a próxima etapa não é opcional.**

## 2. Enriquecimento — o que existe no mundo sobre isso

O plano sabe *quando* mostrar. Não sabe *o que existe*. Quando a fala menciona uma
pesquisa, um pesquisador ou um ano, existe material real lá fora — e material real vale
mais que qualquer render bonito.

Despache o agente **enriquecedor** (Sonnet) com o plano, salve a resposta e aplique:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/aplicar.py \
  --projeto projeto/ --enriquecimento enriquecimento.json
```

Ele devolve dois tipos novos e melhora todo o resto:

- **`paper`** — a ficha bibliográfica real: título, autores, periódico, ano, DOI. Ficha é
  fato e pode aparecer; **fac-símile da página, não**. Uma citação curta por vídeo.
- **`retrato`** — a pessoa citada em preto e branco de papel de jornal. Só com licença
  livre verificada. **Sem imagem livre, o componente cai sozinho na ficha tipográfica** —
  nunca se gera o rosto de uma pessoa real.

E para **todo** plano escreve `movimento`: o que entra, o que acontece, o que sai. Um
vídeo em que os planos só trocam de texto não é motion graphics — é slide com grão, e o
feed passa direto. O vocabulário que o template executa está em
`referencias/movimento.md`, incluindo o tipo `palavras`, de tipografia cinética, para
quando a fala enumera.

Escreve também uma `ideia` por plano: que imagem específica aquele momento pede. "Um objeto simbólico" não é ideia; "uma fita cassete com o meio da
fita puxado para fora e enrolado" é.

O `aplicar.py` não confia no agente: rebaixa `paper` sem título, derruba `retrato` sem
licença para a ficha tipográfica, e apaga a segunda citação do vídeo. As regras completas
estão em `referencias/enriquecimento.md`.

> **Leia sempre o campo `observacoes`.** É onde o agente registra erro de atribuição no
> roteiro — ano trocado, autor errado, paper errado. Se ninguém ler, o vídeo vai ao ar
> com o erro.

## 3. Assets — cada tipo tem uma rota

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/assets.py --projeto projeto/
```

O script lê o `plano.json` e resolve cada plano pela rota do tipo dele. Sem
`GEMINI_API_KEY` no ambiente ele **não falha**: escreve `projeto/PROMPTS.md` com os
prompts prontos para colar em qualquer gerador e segue.

As imagens saem **6 por vez** (`--paralelo`). Gerar imagem é espera de rede, não
trabalho de processador: uma a uma, um vídeo de 40 cenas passava a maior parte do
tempo só aguardando resposta. O que decide *o que* gerar continua sequencial, com o
reaproveitamento de asset intacto — só a espera é que virou simultânea. Uma imagem
que falha não derruba as outras: aquele plano volta para o vídeo original, como já
era a regra.

A regra que decide a rota está em `referencias/ferramentas.md`. Em uma linha:

> **Texto, número e interface são desenhados em código. Matéria, luz e corpo são
> gerados ou filmados. Obra e arquivo são licenciados.**

Gerador de imagem erra glifo, erra acento, alucina rótulo de gráfico e não repete o
mesmo personagem entre gerações. Isso não é opinião — é o achado repetido dos 12
laudos. Nunca peça texto legível a um gerador de imagem.

## 4. Composição — Remotion

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/projeto.sh projeto/    # copia o template e instala
cd projeto && npx remotion studio                            # preview ao vivo
```

O template já traz a grade do preset, as áreas seguras do TikTok, a legenda palavra a
palavra e um componente por tipo de plano. Você edita `src/planos/*.tsx` quando o plano
pede algo que ainda não existe — nunca o CSS da grade, que é a identidade.

Áreas seguras, sempre: **12% do topo** e **22% da base** ficam livres de texto (UI do
app, botões, barra de comentário). A legenda vive na faixa de 46% da altura.

**Onde o quadro já tem texto, a legenda cala.** Cartela, paper, gráfico, interface e
retrato carregam o próprio texto; sobrepor a legenda falada ali faz ler a mesma coisa
duas vezes. O template resolve sozinho pelo campo `legenda` de cada plano.

## 5. Render e grade

```bash
cd projeto && npx remotion render Video out/master.mp4 --props=plano.json
bash ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/grade.sh out/master.mp4 out/final.mp4 noturno
```

O `grade.sh` é uma segunda passada opcional de ffmpeg — grão, aberração e vinheta que
ficam melhores em pixel do que em CSS. Se o vídeo já saiu certo do Remotion, pule.

## Aprender um estilo novo

A skill nasceu sabendo dois estilos porque alguém mediu um deles à mão. Para ensinar um
terceiro, aponte para uma pasta de referências:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/aprender.py \
  --frames referencias/ --nome meu-estilo --out estilos/
```

Ele mede onde o preto assenta, onde o branco é segurado, saturação, contraste, vinheta,
grão dentro do preto, cor na borda, temperatura e paleta; agrupa os frames por semelhança
de **estilo** — cor, textura e luz, não assunto — e monta uma folha de contato por grupo.

**Aí você olha.** Abra as folhas e escreva o que a máquina não mede: tipografia, movimento
de câmera, ritmo de corte, o que cada grupo é e quando usar. Ou despache o agente
`analista-de-estilo`, que abre as folhas e preenche. O `medicoes.json` traz um campo
`confianca` separando o que é medida direta do que é aproximação do que não tem número.

Depois, o estilo entra num vídeo assim:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/plano.py \
  --falas falas.srt --out motion/ --estilo estilos/meu-estilo/medicoes.json
```

A grade aprendida vira o campo `grade` do `plano.json` e sobrescreve o preset campo a
campo. O que não foi medido cai no `noturno`.

> Frames de referência servem para medir e estudar. Medida não é obra — luminância,
> paleta e vinheta são fato sobre a imagem. Os frames em si continuam sendo material de
> terceiro: não publique, não use como asset, não copie composição ou personagem.
> Detalhes em `referencias/aprender-estilo.md`.

## Validação antes de entregar

Não entregue sem passar por isto:

- [ ] **Teste do mudo.** Assista sem som. Dá para saber do que se trata? Se não, os
      planos estão ilustrando palavras em vez do argumento.
- [ ] **Teste do polegar.** Congele em 1,0 s. Essa imagem parada faz alguém parar?
- [ ] **Teste da legenda.** Nenhum texto invade os 12% do topo nem os 22% da base.
- [ ] **Teste do histograma.** No preset `noturno`, um pico grande abaixo de 40 (o
      fundo) e um pico estreito acima de 235. Se o meio estiver cheio, a grade não pegou.
- [ ] **Teste do dado.** Todo número no vídeo tem fonte escrita no `plano.json`.
- [ ] **Teste do movimento.** Em nenhuma janela de 2 segundos o quadro fica parado com
      só grão e zoom lento.
- [ ] **Teste da dupla leitura.** Em nenhum frame há legenda falada por cima de um plano
      que já mostra texto.
- [ ] **Teste da atribuição.** As `observacoes` do enriquecedor foram lidas e o roteiro
      corrigido, ou o erro foi assumido conscientemente.
- [ ] **Teste da palavra inteira.** Cada emenda de decupagem preserva 600 ms depois da
      palavra anterior e antes da próxima; foi ouvida em 1× e 0,75×; falsa partida sem
      silêncio suficiente permaneceu no vídeo.
- [ ] **Direitos.** Nenhum asset de acervo entra sem a licença registrada no plano.

## Limites que a skill respeita

- Não gera semelhança de pessoa real, nem imita conta ou marca de terceiro.
- Não apresenta b-roll moderno com textura de arquivo como se fosse documento real.
- Obra de acervo carrega **dois** direitos: o da obra e o da fotografia dela. Os dois
  vão registrados no plano ou o asset não entra.
- Número sem fonte não vira gráfico.

## Onde ficam as coisas

Nenhum caminho sai do código: as pastas vêm de `~/.config/beditor/config.json`,
escrito por `/sofia-estrategista-editora:setup` (`scripts/setup.py --pastas nome=caminho`) e lido por
`oficina.config()` / `oficina.pasta(nome)`. Pasta não configurada para e pede o
setup, nunca inventa um caminho no disco interno. O manual gerado
(`setup.py --manual`) mostra o que está configurado e o que falta na máquina.

| O quê | Onde | Por quê |
| --- | --- | --- |
| o plugin | onde o `claude plugin install` pôs, ou o clone | é o que o Claude carrega |
| treinamento (vídeos, frames, folhas de contato, procedência) | pasta `treinamento` do config | material de terceiros: fica na máquina de quem treinou, **nunca no plugin** |
| o que foi aprendido (`ESTILO.md`, `medicoes.json`) | no plugin, em `treinamento/<estilo>/` | números e leitura, sem imagem, sem nome de perfil, sem link |
| marcas | pasta `marcas` do config | de quem edita, uma por canal ou cliente |
| oficina de render | `~/.beditor/render` → link para a pasta `render` | caminho curto e sem acento para o HyperFrames |
| projetos de vídeo, brutos, renders | pasta `projetos` | dezenas de GB por vídeo — e **fora do iCloud** |
| masters prontos | pasta `entregas` | o que sai para publicar |

Regra prática: **o que a skill lê vai para o plugin; o que a skill produz, e todo
material de terceiros, fica nas pastas da máquina.** O `.gitignore` impede vídeo,
frame e folha de contato de entrarem por engano, e `tests/test_terceiros.py` para
se um nome de perfil, link de post ou imagem de treinamento entrar.

**Pasta em disco externo não montado para o fluxo.** Monte o disco e reabra a
sessão; o script diz qual pasta faltou.

**Nunca em `~/Documents` nem na Mesa.** As duas pastas sincronizam com o iCloud, e
o macOS tira do disco o que é grande e não foi aberto há pouco: o arquivo continua
listado, com o tamanho certo, mas ocupa 0 B (`stat -f %Sf` mostra `dataless`).
Qualquer `open()` nele espera o download — sem erro, com 0% de CPU, por minutos.
Um dia inteiro de render travado parecia disco lento, memória, antivírus, pipe;
era isso. Antes de rodar qualquer etapa, confira:

```bash
find <projeto> -type f -flags +dataless
```

Se sair algo, o projeto está no lugar errado. Traga para o SSD o que está local;
o que só existe no iCloud se reconstrói de um original local e **se prova** —
duração ao milissegundo contra o `contato.json` e envelope de áudio contra um
derivado que ainda esteja no disco (foi assim que o take do 05 voltou dos seis
arquivos do AirDrop, com correlação 1,000 nas cinco emendas).

**Brutos que chegam em Downloads (AirDrop) vão para o SSD antes de qualquer
etapa.** Pedido do dono em 2026-09-27: *"se já foi pro SSD pode sair de
Downloads"* — o Mac não tem espaço para guardar duas cópias. Crie
`NN - Nome/brutos/` na pasta `projetos` (NN = próximo número), copie com `cp -p`,
confira com `cmp` e só então mova o original de Downloads para a Lixeira.
Vale também para o reel que foi para Downloads só para subir: se há cópia
idêntica no projeto, sai.

**Edite só o que o dono mandou editar.** Pedido de 2026-09-27: *"só pedi para
editar vídeos cujos arquivos brutos foram gravados e baixados hoje"*. Quando ele
diz "os últimos N vídeos do AirDrop", são os N arquivos mais recentes de
Downloads (pela data de chegada), juntos, **na ordem de gravação** — um vídeo
só. Projeto antigo não se reabre por conta própria.

**O padrão de um vídeo de rosto na câmera (`dinamismo`), aprendido nos 19 e 20
— para acertar de primeira:** corte de silêncio com as travas de `formatos.md`;
zoom só em ênfase de voz medida, desfeito só num corte, escala baixa (o take de
celular já é vertical); split edit tipo L de 6 quadros quando ele pedir "jcut";
hook no terço superior com acentuação conferida e nenhuma letra cortada;
legenda menor, com sombra, fixa logo abaixo da boca; aprovação pela **prévia
viva** com o vídeo aparecendo e a linha do tempo arrastável, nunca por render de
30 minutos; master conferido com `conferir_movimento.py`; post com legenda de
SEO tirada do conteúdo (`publicacao.md`). Duração: todos os trechos usados
somados — se ficar longo, explique que é a soma dos takes, antes que pareça erro.

**`projetos/CHECKLIST.md` acompanha tudo.** Três seções — *Em edição* (com as
etapas marcadas), *Editado, falta postar* e *Publicado*. Atualize a cada etapa
que muda: projeto criado, preview entregue, aprovado, publicado. É a primeira
coisa a ler ao retomar uma sessão.

## Referências

| Arquivo | Para quê |
| --- | --- |
| `referencias/linguagem-visual.md` | a grade medida, tipografia, áreas seguras |
| `referencias/ritmo.md` | duração, gancho, densidade, onde cortar |
| `referencias/catalogo-visual.md` | as 12 classes e o gatilho de cada uma |
| `referencias/ferramentas.md` | qual ferramenta para qual plano, e o custo |
| `referencias/prompts-assets.md` | prompts prontos por classe |
| `referencias/aprender-estilo.md` | como ensinar um estilo novo a partir de frames |
| `referencias/movimento.md` | o que entra, o que acontece, o que sai — e o que é movimento fraco |
| `referencias/enriquecimento.md` | o que pesquisar, o que pode aparecer, o que não pode |
| `referencias/sugestao-de-motion.md` | **como se chega à ideia** — as quatro perguntas (quantos? que coisa é no mundo? dá para mostrar em vez de rotular? o que entra e o que sai?), as duas provas, e a tabela de sugestões reprovadas que gerou a regra |
| `referencias/receitas.md` | **escolhida a classe, o que exatamente se vê** — gatilho, movimento em três tempos, duração |
| `referencias/rotas-de-geracao.md` | quem desenha cada plano: HyperFrames, Claude Design, Gemini, NotebookLM, acervo |
| `referencias/estilos.md` | `noturno` e `demonstracao` — o mesmo sistema em dois sotaques medidos — e `bento-ui`, a marca do dono para o plano de interface |
| `referencias/formatos.md` | o que o vídeo **é**: `dinamismo` não leva motion, música nem cor; `analise` é sobre o vídeo de outra pessoa |
| `referencias/formato-analise.md` | **o formato `analise` medido**: a espinha em porcentagem, os **quatro modos** de entrada do cartão (atrás · sobreposto · máximo · janela), por que a geometria muda com a orientação da fonte, o reenquadramento pelo rosto onde não há cartão, o hook de 3 s como provocação, o critério de música e de SFX, e o procedimento de busca que já roda |
| `scripts/cartao.py` | **o cartão de prova, composto**: os quatro modos com a geometria por orientação, a abertura e minimização da janela, a legenda creme sem barra, o enquadramento pelo rosto suavizado, e o hook de três faixas com a divisa **dissolvida** (o insert inteiro em cima, o autor abaixo da parte opaca). Mais os quatro registros que nasceram no 15: `marcador` (o número do capítulo, obliquo, no alto à esquerda), `triptico` (três provas lado a lado, entrando em sequência, para a frase que cita três casos), `frase_hook` (a promessa no registro do hook, fora do hook) e `logo_atras` (a marca de um produto citado, subindo por trás de quem fala e saindo com a frase). Mais os **dois registros de tipografia**: `tipografia()` lê e define qual está em vigor (`minusculo` · `explicativo`), `sans()` e `serifa_italica()` abrem as fontes variáveis de `public/fontes/` no peso pedido, `titulo_duas_vozes()` desenha o título das duas vozes (a sans grande é o apoio, a serifa itálica menor é a palavra, encostada por baixo), e `legenda()`, `frase_hook()` e `marcador()` bifurcam nos dois |
| `tests/test_cartao_tipografia.py` | os dois registros tipográficos sem render de vídeo: o interruptor `tipografia()`, as duas fontes variáveis presentes e na família certa, o eixo de peso chegando na letra, a caixa normalizada nos dois sentidos, o título das duas vozes dentro do quadro, a linha longa encolhendo e o marcador não estourando a borda |
| `scripts/acervo.py` | trecho de vídeo de terceiro dentro de uma cena: baixa uma vez por URL e cacheia, corta e compõe por cima do clipe já renderizado. Teto de **3 s por fonte**, procedência (URL, autor, data) obrigatória, e o script **não procura vídeo sozinho**. As decisões do dono ficam no cabeçalho: 2026-09-12 (inserts de Reels e TikTok) e 2026-09-15 (a ilustração do `analise` pode vir de YouTube e TikTok, não só de banco de imagens) |
| `scripts/silencio.py` | **corte de silêncio nas três posições** — cabeça (voz − 120 ms), miolo (buraco ≥ 500 ms vira pausa de 250 ms) e cauda, que **não é duração e sim evento**: vai até o som cair, mais 180 ms, com piso de 150 ms depois da palavra e teto de 450. Cauda fixa encostava na guarda de cabeça da emenda seguinte e deixava 21 buracos acima de meio segundo. Carimba `folgaMs`/`folgaLimpa`, medida **onde o split edit a gasta** (os últimos 600 ms antes da voz que entra), não no buraco inteiro |
| `scripts/varrer.py` | **tira de contatos de um clipe de acervo**, um quadro por segundo com o tempo escrito — obrigatória antes de fixar `src`/`dur` de um insert: título de vídeo não é laudo do trecho, e às vezes nem do vídeo. Responde «onde no vídeo»; **`lupa.py` responde «em que segundo»**, e a segunda pergunta não é opcional: 84,5 s e 85,2 s do mesmo trailer são planos diferentes, e a tira grossa mostra os dois dentro do mesmo quadro amostrado |
| `scripts/lupa.py` | **a tira fina de uma JANELA do clipe**, um quadro a cada 0,4–0,5 s com o segundo escrito: `lupa.py <saida/> <clipe.mp4> <de> <ate> [passo]`. É a segunda das três perguntas da escolha — onde no vídeo (`varrer`) · em que segundo (`lupa`) · aguenta o quadro (o olho). E olhe o **último** quadro da janela: é nele que o cartão congela quando o trecho da origem acaba antes do cartão |
| `referencias/eficiencia.md` | **onde o tempo e os tokens foram nos projetos 14 e 15, medido** — 3 817 turnos relendo 1,25 bilhão de tokens; render refeito 32 e 58 vezes; 154 imagens lidas — e as nove regras que saíram disso: uma etapa é um script do plugin em uma chamada, ajuste é edição de JSON e o render decide o que refazer, número antes de imagem, processo longo em segundo plano, cache com chave de conteúdo em tudo |
| `scripts/oficina.py` | a oficina: `chave()` (hash de estrutura), `identidade()` (chave barata de arquivo grande), `paralelo()` (processos ou threads, erro nomeado), `Manifesto` (o que foi refeito e quanto custou), `folha()` (folha de contato que já nasce nos 1 568 px que o modelo lê), `quadro_em()`, `dataless()` |
| `scripts/transcrever.py` | transcrição palavra a palavra com **cache pelo conteúdo do áudio** (rodar de novo com o mesmo take custa 0,1 s) e o motor mais rápido da máquina — MLX na GPU, depois faster-whisper, depois whisper. `--contexto` leva os nomes próprios que o modelo erra sem ajuda |
| `scripts/render_analise.py` | **o master do `analise`, por segmentos, em paralelo, com cache de conteúdo.** Lê `edicao/dados.json` + `edicao/plano.json`; parte a linha do tempo em segmentos de 2 s que quebram onde uma camada muda; cada segmento tem chave = hash da receita (o que decide cada pixel) + hash do código; N processos compõem e entregam ao ffmpeg por pipe; o master é concatenação **sem recodificar**. Áudio com cache próprio (voz pela tabela; mistura pela cama). `--entrega N` põe a capa como segmento e não recodifica o corpo. `--revisao`, `--limpar`, `--recodificar`. Escreve `oficina/manifesto.json` |
| `scripts/decupar.py` | **da decisão do diretor ao `dados.json` completo**: o diretor escreve takes, momentos em segundos LOCAIS do take, recusas, cortes internos e a estrutura por ids; o script calcula os offsets da linha do tempo virtual, as `palavras` em ms virtuais, `deMs`/`ateMs`, a tabela inicial e o wav costurado (chave de conteúdo) que o `silencio.py` escuta. `--estrutura` preenche as porcentagens dos blocos depois do corte; `--em take:segundo` diz onde um segundo do take cai no corte, para escrever o plano sem errar por meio segundo |
| `scripts/custos.py` | quanto cada ETAPA custou em tokens e tempo de sessão, lido do registro do Claude Code (`~/.claude/projects/<cwd>/<sessão>.jsonl` mais subagentes), determinístico: usage uma vez por `requestId`, etapa atribuída pela ferramenta chamada; `--projeto` escreve `edicao/oficina/custos.json` e cruza com `telemetria.jsonl` (o `oficina.Cronometro` que cada script grava); `--por-pedido` abre por pedido do dono; `--desde/--ate` recortam |
| `scripts/qa_analise.py` | as cinco medidas em texto (split edit, sincronia, buraco de voz, cama, densidade) mais a linha do manifesto; `--folha` só a pedido, em 1 568 px; `--comparar aprovado.mp4` diz QUAIS trechos mudaram entre dois masters — a prova de que o ajuste pontual não mexeu no aprovado |
| `referencias/biblioteca.md` | **a biblioteca de mídia da máquina** (músicas por clima, SFX, overlays, logos) e o `catalogo.json` que viaja com cada pasta: o que se mede (LUFS, LRA, **eventos/min**, a tradução medível de «a cama não pode ter evento que se conte»; alfa pixel a pixel nos logos), como escolher cama para o `analise`, a tabela gatilho→SFX, por que o `analise` não usa overlay, o que `logo_atras` exige do arquivo, e o **aviso de licença**: as músicas são instrumentais de obras comerciais baixadas do YouTube, licença desconhecida, risco de Content ID; a decisão é do dono e toda faixa vai ao `provas.json` como `trilha` |
| `scripts/biblioteca.py` | `catalogar` (incremental por `oficina.identidade`, threads, um `catalogo.json` dentro de cada pasta; rodar de novo é grátis), `listar <tipo> [--clima --texto --alfa --max-eventos --json]`, `cama [--clima --n]` (as N faixas com menos eventos/min e menor LRA, ≥ 90 s, sem vocal, com o bloco `"musicas"` pronto para o `plano.json` e o aviso de licença) e `sfx <gatilho>` (Hit para `marcador`, Woosh Fast para `cartao`, «nenhum» com motivo para `pb`, `destaque`, `modo1`) |
| `referencias/publicacao.md` | depois do master: palavra-chave tirada da fala, título e texto por rede, capa dentro da área que a grade não corta, e um agendamento só (Zernio ou Metricool) — nunca sem o sim do editor |
| `referencias/chaves.md` | **o que exige chave e o que não exige, por formato** — editar e renderizar não pedem conta nenhuma; só a rota Gemini (`GEMINI_API_KEY`, e sem ela o script entrega os prompts) e a publicação (Zernio/Metricool por MCP, token na sessão e nunca no disco do plugin) |
| `referencias/direcao-de-motion.md` | formato com motion: o estilo do vídeo em oito itens (`direcaoMotion`) e um prompt por cena com cinco (o que aparece e anima, texto exato de até 6 palavras, cores/fundo/tipografia, câmera e transição, som) — o validador recusa sem eles |
| `referencias/galeria-estilos.md` | estilos nomeados de hook, legenda, **motion**, música e SFX, medidos nos corpus de `Treinamento/`; `guia.estilos` escolhe, `scripts/estilos.py` guarda os valores (paleta, acabamento, matéria da imagem gerada) |
| `referencias/procedencia.md` | **de onde veio, de que direito, e quem manda** — a hierarquia de instruções, a ficha de cada asset, e por que chave nenhuma entra no repo |
| `referencias/voz.md` | **a voz**: o que pedir antes do próximo take (energia, uma frase por vez, distância do microfone, fim de frase descendo), a cadeia de tratamento na ordem, os cortes medidos de cada voz (`scripts/voz.py`, guardados na marca) e por que a música leva low pass e ducking |
| `referencias/sincronia.md` | **a boca em quadro manda no áudio** — onde o J-cut pode existir, como o áudio se ancora ao aparar, e o teste que não engana |
| `referencias/portoes-de-qualidade.md` | **os seis portões antes de dizer que está pronto**, e a ordem da inspeção: script primeiro, olho depois |
| `referencias/motion-editorial.md` | o style bible do projeto, as cinco perguntas de cada momento, os registros (colagem, cartoon, whiteboard, híbrido) e a continuidade entre planos |
| `referencias/producao-gemini.md` | qual modelo para cada papel, o manifesto aprovado antes de gastar, upload, custo, retenção e o que fazer quando falha |
| `referencias/tela-dividida.md` | apoio em cima, quem fala embaixo: o rosto rastreado vira keyframes de enquadramento, o matte cobre as colisões medidas, o topo é footage fornecido, legenda e hook em torno da junção — que não leva linha visível —, e por que ali não há J-cut |
| `referencias/hook.md` | **escrever as palavras do hook** (o desenho está em `galeria-estilos.md`): as duas perguntas, os quatro S, a fórmula de substância do texto na tela, palavras de força, a zona de travamento com a âncora de prova, e o procedimento das **três opções por mecanismo diferente** |
| `referencias/mesa-de-decupagem.md` | **a mesa é uma só e tem URL fixo** — ler o artifact publicado, editar em cima dele e republicar no mesmo endereço. Nunca publicar mesa nova |
| `treinamento/<estilo>/ESTILO.md` | a leitura das folhas de contato que originou cada estilo (as folhas ficam fora do plugin) |
| `scripts/setup.py` | **preparar uma máquina nova**: `--verificar` (binários, pacotes Python, motor de transcrição, `~/.beditor/render` sem acento, chave da Gemini só como presente/ausente, fontes locais, pastas configuradas com espaço livre e contagem de `dataless`), `--pastas nome=caminho [--criar]` e `--canal` (mescla no `config.json`), `--instalar [--sim]` (os comandos do que falta; só executa com o sim), `--manual` (o manual desta máquina) e `--tudo` |
| `docs/manual.html` | o template do manual interativo: começar, saúde da máquina, fluxos, comandos, pastas e biblioteca, referências, glossário. Arquivo único; o `setup.py` troca o marcador `/*__DADOS__*/{}` pelo JSON e grava em `~/.beditor/manual.html` |

**Uma skill só, para o Claude e para o Codex.** Esta pasta vem no plugin Sofia
Estrategista, que o Claude e o Codex carregam (no Codex, com
`agents/openai.yaml`). A linha antiga do Codex,
`beditor-motion-noir`, foi fundida aqui em 2026-09-11 e não se edita mais:
aprendizado novo entra neste repositório. No Codex, o que depende do Claude
(comandos `/sofia-estrategista-editora:*`, os agentes `diretor` e `enriquecedor`, a mesa como
Artifact) não existe; os scripts de `scripts/` e as referências valem igual.

Skills vizinhas: **corte-viral** entrega o vertical limpo que entra aqui;
**motion-vox** faz a identidade editorial de papel; **hyperframes** e
**hyperframes-cli** são o renderizador padrão; **claude-design-hyperframes**
desenha uma peça nova quando o catálogo não tem; **notebooklm** gera fundo a
partir das suas fontes. **A marca não é skill do plugin:** é de quem edita, uma
por canal ou cliente, e mora fora dele — `scripts/marca.py` (`listar`, `nova`,
`usar --projeto`, `mostrar`) diz qual vale em cada projeto.
