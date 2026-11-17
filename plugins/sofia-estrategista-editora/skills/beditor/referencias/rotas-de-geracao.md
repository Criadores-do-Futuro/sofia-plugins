# Rotas de geração — quem desenha cada plano

Toda peça que entra na tela vem de uma destas cinco rotas. A escolha não é de
gosto: cada rota acerta uma coisa e erra outra, e escolher errado é o que produz
número inventado, glifo torto e tela preta.

| Rota | Acerta | Erra | Custo |
| --- | --- | --- | --- |
| **HyperFrames** (HTML, CSS, GSAP, SVG) | texto, número, interface, gráfico, movimento, textura procedural | fotografia, matéria, rosto | segundos, determinístico |
| **Claude Design** | layout, hierarquia tipográfica, paleta, composição de cartela e ficha | animação, tempo | minutos, é desenho, não render |
| **Gemini imagem** | matéria, luz, cena fotográfica, objeto, figura sem rosto | qualquer texto legível, número, rosto real, contagem exata | segundos por imagem, custo por chamada |
| **NotebookLM** | fundo coerente a partir das suas fontes, atmosfera do tema | precisão factual do desenho, tipografia | manual, fora do pipeline |
| **Acervo** (arquivo, obra, retrato) | prova real, peso histórico, rosto de pessoa real | disponibilidade, direitos | curadoria e risco jurídico |

---

## A regra que decide sozinha

**Se tem texto, número ou interface, é HyperFrames.** Sem exceção. O gerador de
imagem erra glifo, inventa cifra e desenha rótulo em idioma nenhum — está medido
em `ferramentas.md`, e foi a causa de um plano com dezesseis painéis rabiscados
quando o pedido era dez fichas.

**Se tem matéria — mesa, mão, papel, porta, corpo, sala — é Gemini.** Nenhum CSS
faz a luz cair numa superfície como uma foto faz.

**Se tem rosto de pessoa real, é acervo com licença.** Nunca se gera o rosto de
alguém que existe, nem "parecido com". Sem licença, a ficha tipográfica em
HyperFrames faz o trabalho com mais dignidade.

---

## As rotas em detalhe

### HyperFrames — o desenho que se move

É o renderizador padrão do plugin (`hf.py`). Cada plano vira um `index.html`
autocontido com GSAP em timeline pausada, e sai como MP4 de 1080×1920.

Serve: `cartela`, `palavras`, `paper`, `dado`, `tela`, `retrato` tipográfico, e
todo o acabamento analógico de qualquer plano — meio-tom, grão, vinheta, rims.

Também serve para **animar uma imagem gerada**: a foto do Gemini entra como
`<img>` e o HyperFrames faz o push-in, a máscara, o scanner e a saída. É assim
que as duas rotas se combinam, e é o padrão para `objeto`, `personagem`, `obra`,
`arquivo` e `cotidiano`.

**Cuidado registrado:** o `npx hyperframes` trava sem mensagem quando o diretório
de trabalho tem parênteses ou acentos. O `hf.py` já contorna isso renderizando
numa oficina de caminho neutro. Não mude isso.

**Determinismo, que o `hf.py` já cumpre e ninguém deve quebrar** (veio da linha
do Codex, `hyperframes-production.md`):

- a timeline GSAP nasce `paused: true` e fica registrada em `window.__timelines`;
- nada de `Date.now()`, `Math.random()` sem semente, nem `requestAnimationFrame`
  fora do runtime. O `hf.py` sorteia com `_rng(semente)`, e o grão do
  `feTurbulence` tem `seed` fixo;
- nenhuma mídia remota durante o render. Baixe antes, com autorização, e
  registre origem e hash;
- o HTML/CSS já é o quadro final certo, e o GSAP só descreve como chegar nele e
  sair dele. Em subcomposição, prefira `fromTo`;
- anime `transform` e `opacity`, nunca `top`, `left`, `width` ou `height`
  durante a captura; nada de dois tweens na mesma propriedade sem encadear
  (`overwrite: "auto"`).

| Intenção | Como se faz na web |
| --- | --- |
| track matte alfa/luma | SVG `mask`, CSS `clip-path` |
| câmera 2.5D | `perspective` + `transform-style: preserve-3d` |
| meio-tom | SVG `pattern` ou overlay CSS |
| grão | SVG `feTurbulence` com semente fixa |
| sombra de contato | duas camadas de `drop-shadow`, uma curta e densa, outra longa e macia |
| scanner | gradiente linear, blend `screen`, tween GSAP |
| CRT | máscara curva, scanlines, bloom e aberração controlada |
| objeto 3D | Three.js ou Canvas, só quando a geometria real se paga |

Plano novo, ou template novo, passa pelo ciclo da skill `hyperframes-cli`
antes de entrar no catálogo: lint estrutural; inspect nas amostras de entrada,
pico de ocupação e saída; overflow, oclusão, contraste e área segura; render dos
quadros representativos, **vistos a olho**; render completo e QC de duração,
fps, áudio e arquivo ausente. Não silencie alerta de layout no atacado: anote
só o elemento decorativo que transborda de propósito e corrija o resto.

**Footage dentro do HyperFrames** (projeto 08, 2026-09-11):

- **AV1 trava o verificador sem erro.** O download do YouTube chega em AV1, e a
  checagem do HyperFrames parou por mais de três minutos na preparação das
  fontes, sem mensagem. Faça uma cópia de trabalho em H.264 (`ffmpeg -i
  origem.mp4 -map 0:v:0 -an -c:v h264_videotoolbox -b:v 10M -pix_fmt yuv420p
  -movflags +faststart origem-h264.mp4`), com o mesmo timecode. O original fica
  intacto e é ele que o `SOURCES.md` cita.
- **Bloco de footage é composição de vídeo pura.** Cartão, rótulo ou camada
  escondida (`opacity: 0`) na mesma subcomposição deixou trechos oficiais
  **pretos** no preview. O vídeo entra sozinho, com `object-fit: cover`,
  `object-position` de enquadramento, `muted` e, se preciso,
  `data-playback-rate`.
- **O rosto rastreado anima `object-position`.** É a exceção à regra de só
  animar `transform`: os keyframes do `enquadrar_rosto.py` (`--js`) viram tweens
  lineares no vídeo de quem fala, e esse vídeo é mudo porque a voz vai num
  `<audio>` separado da mesma fonte.
- **Legenda e hook anotam a sobreposição no próprio elemento**
  (`data-layout-allow-overlap` na legenda, `data-layout-allow-occlusion` na
  camada). Nunca na composição inteira.

### Claude Design — quando o layout ainda não existe

Use quando a peça é tipográfica e você ainda **não sabe como ela deve parecer**:
uma ficha nova, uma cartela de abertura, um painel comparativo. O Claude Design
resolve hierarquia, escala e paleta; o resultado vira um template HyperFrames que
o plugin passa a instanciar sozinho.

Não use para repetir uma peça que já existe no catálogo — para isso o template já
está escrito e o custo é zero.

### Gemini — a matéria

Prompt pelo molde da classe em `prompts-assets.md`: cena fotográfica de quadro
cheio, com lente, luz e sombra. Nunca "um objeto só, centrado, fundo liso" — isso
produz ícone flutuando, que é a versão pobre da linguagem.

O prompt de cada imagem fica gravado ao lado dela em `<ID>.prompt.txt`. Mudou a
ideia, a imagem é refeita sozinha; não mudou, ela é reaproveitada. É o que impede
uma imagem de uma direção antiga de entrar no lugar da nova.

Qual modelo para cada papel (imagem rápida, imagem mestre, vídeo Omni ou Veo),
o manifesto que se aprova antes de gastar, e o que fazer com upload, custo e
retenção estão em `producao-gemini.md`.

### NotebookLM — o fundo que sabe do assunto

Rota manual, para quando o vídeo precisa de um fundo coerente com o material de
origem (o paper, o livro, a transcrição). Alimente o caderno com as fontes e a
matriz de categorias, peça a imagem de fundo do momento, salve em
`public/assets/<ID>.png` e registre a origem.

O que o NotebookLM **não** decide: o corte, o tempo, o tipo do plano. Ele é fonte
de imagem, não diretor.

### Acervo — a prova

`arquivo`, `obra` e `retrato` licenciado. Duas travas que não se negociam: o
áudio de material de terceiros nunca entra no vídeo, e a licença fica registrada
no plano antes de a peça entrar.

---

## Como o diretor escolhe

Na hora de escrever o guia, para cada momento:

1. A frase tem texto, número ou interface? → HyperFrames, e o campo de dados vem
   escrito no guia.
2. A frase pede matéria? → Gemini, e a `ideia` descreve a cena inteira.
3. A frase nomeia uma pessoa real ou um fato histórico? → acervo, e o
   `enriquecedor` verifica antes.
4. Nada disso? → é `fala`. O rosto de quem fala é melhor que uma ilustração
   genérica, sempre.
