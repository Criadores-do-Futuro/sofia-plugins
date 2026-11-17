# Tela dividida — o apoio em cima, quem fala embaixo

Veio da linha do Codex (`beditor-motion-noir`, `split-screen.md`, 2026-09-11) e
foi reescrita para a máquina daqui. Com uma correção: a regra de J-cut de lá
contradizia `sincronia.md`, e a daqui vale (ver "Ritmo e montagem"). O resto do
que está aqui saiu do **projeto 08** (`Projetos/08 - iPhone Duo Split Screen`),
editado no Codex em 2026-09-11 com três rodadas de correção do dono do canal.
As frases dele estão citadas onde viraram regra.

Use quando quem fala continua visível enquanto B-roll, captura de tela, motion
ou mídia gerada ocupa outra parte do quadro.

## O que a divisão está fazendo

A fala é a espinha. O apoio prova ou concretiza a ideia **deste instante**. A
divisão não é 50/50 por padrão: sai da trajetória da cabeça e do peso visual do
apoio.

## A geometria que funcionou

Em 1080×1920: **apoio 1080×840 em cima** (43,75%), **quem fala 1080×1080
embaixo** (56,25%), encostados em y 840 — 840 + 1080 fecha os 1920 exatos.

**Nenhuma linha visível entre os dois vídeos.** Pedido do dono, em 2026-09-11:
*"no modo tela dividida não crie linhas visíveis entre os vídeos"*. Nada de
faixa, régua, moldura, contorno, sombra projetada nem folga de fundo aparecendo
na junção: um quadro termina onde o outro começa. O que separa as duas regiões é
o conteúdo — enquadramento, luz e cor diferentes —, não um traço desenhado. Se
aparecer fresta de um pixel por arredondamento, o vídeo de cima sobrepõe um
pixel (`height: 841px` com o de baixo por cima), nunca se preenche com barra. O primeiro corte do
Codex foi 50/50 e o dono pediu: *"poderia ter deixado o vídeo um pouco mais pra
cima, cortar um pouco do topo do vídeo para poder encaixar a parte de cima da
montagem, mas preservando meu rosto"*. A faixa de partida é **36–46% para o
apoio e pelo menos 54% para quem fala**. Quem decide dentro dela é o
`enquadrar_rosto.py` (a caixa mínima que ele informa).

## A ordem de decisão

1. **O take tem de estar em SDR.** iPhone grava HLG; rode `sdr.py` antes de
   tudo (`SKILL.md`, etapa 0).
2. **Rastreie o rosto no trecho inteiro.** Nunca só no início, no meio e no
   fim. O dono avisou: *"como eu me mexo, eu começo no enquadramento depois
   saio depois volto"*.
   ```bash
   scripts/instalar_bin.sh                                   # uma vez por máquina
   ~/.beditor/bin/rastrear-rosto brutos/take.sdr.mov edicao/rosto.json
   python3 scripts/enquadrar_rosto.py edicao/rosto.json --video brutos/take.sdr.mov \
     --caixa 1080x1080 --saida edicao/enquadramento.json --js > edicao/enquadramento.js
   ```
   O `rastrear-rosto` roda o Vision localmente, uma amostra a cada 0,25 s. O
   `enquadrar_rosto.py` protege a faixa do cabelo ao queixo. A caixa do Vision
   vai da sobrancelha ao queixo, e o cabelo sobe **0,30 da altura dela** acima.
   Depois ele filtra a trajetória (mediana contra a detecção errada, média
   contra o tremor), mantém a janela dentro dos limites e devolve keyframes de
   `object-position` com tweens lineares. Quem sai do quadro fica com a última
   posição até voltar.
3. **Leia a caixa mínima antes de fixar a proporção.** Se a `caixaMinimaPx`
   cabe na faixa de 54–64%, aumente a região de quem fala e rode de novo. Se não
   cabe, a proporção fica, e os intervalos de `colisoes` vão para o matte.
4. **Reenquadre cortando primeiro teto, parede ou vazio.** Falta de espaço
   nunca se resolve cortando a cabeça.
5. **Aplique os keyframes no `object-position` vertical** do vídeo de quem fala
   (`--js` imprime os tweens GSAP). Nunca aplique a detecção crua: tremor de
   poucos pixels parece erro de câmera.
6. **Só então escolha o apoio.** Cada trecho corresponde a uma unidade de
   sentido da fala e entra **mudo**.

## Máscara Dividir com Suavizar (opcional)

Pedido do dono em 2026-09-14: *"adicionar o Dividir na máscara, horizontal, com
Suavizar em 30%, assim como fazem no capcut"*, na tela dividida e no vídeo solo,
*"e isso tem que ser opcional"*. **Desligada de fábrica.** Liga em `guia.mascara`
ou na aba Máscara da mesa:

```json
"mascara": {"ligada": true, "onde": "split", "linhaPct": 43.75, "suavizarPct": 30}
```

A conta está em `scripts/mascara.py`: rampa = `suavizar × metade da altura`
(30% em 1920 = 288 px), centrada na linha, em smoothstep (rampa linear deixa
banda de Mach, que é a linha que não pode aparecer).

- **Tela dividida (`onde: split`).** A máscara vai no **apoio**. Ele desce meia
  rampa sobre quem fala e quem fala sobe meia rampa sob ele, então a junção vira
  dissolução. Em 1080×1920 com junção em 840: apoio `top 0, height 984`, quem fala
  `top 696, height 1224`.
  ```bash
  python3 scripts/mascara.py css --modo split --juncao 840 --suavizar 30
  ```
  imprime o CSS (`mask-image`) e a caixa nova. **Refaça o enquadramento com
  ela** (`enquadrar_rosto.py --caixa 1080x1224`): a região de quem fala cresceu,
  e o cabelo pode passar por baixo da rampa do apoio. Confira as colisões de novo.
- **Vídeo solo (`onde: solo`, linha 20%).** O `montador.py` sobrepõe um degradê
  preto no topo de cada trecho de A-roll, depois do reenquadramento: a linha fica
  parada enquanto o zoom troca. O motion de tela cheia não recebe, e hook e
  legenda vêm por cima. `--sem-mascara` ignora a máscara num render.
- Portão: a rampa não pode cobrir olho nem boca. Se cobrir, baixe a linha
  (solo) ou refaça o enquadramento (split).

## Quando o reenquadramento não basta: o matte

O pedido do dono, que virou padrão: *"se ainda assim ficar cortando minha
cabeça pode ser uma boa solução duplicar a camada do meu vídeo, e na camada
mais acima, remover o fundo automaticamente deixando somente meu rosto"*.

Nos intervalos que o `enquadrar_rosto.py` lista em `colisoes`:

1. duplique a camada de quem fala e mantenha a original como base;
2. tire um matte de pessoa ou de cabeça da cópia. O `recorte` do Vision roda
   local e não manda imagem para fora;
3. componha a cópia **por cima** do apoio, só nesses intervalos, com o cabelo
   invadindo a região de cima;
4. use feather mínimo e constante, sem comer fio de cabelo nem criar halo;
5. revise óculos, mão perto do rosto, motion blur e mudança de luz;
6. reprove flicker, borda pulsando ou contorno que denuncia o matte.

Tipo `rosto` nas colisões (sobrancelha a queixo não cabe) não se resolve com
matte: a região de quem fala está pequena demais. Não use o matte quando crop e
posição resolvem, porque remover fundo custa tempo e traz artefato.

**Falha registrada (projeto 08).** A revisão do Codex declarou *"cabelo,
olhos, boca e queixo inteiros nos dez frames"*, e o render mostra o topo da
cabeça cortado na junção em quatro quadros de quatro. Em 38,9 s o
`enquadrar_rosto.py` acha nove intervalos de colisão `cabelo`. O rosto chegava
a 914 px de altura e pedia uma caixa de 1304 px contra 1080. "Inteiro" sem
número passa em revisão cansada; a colisão medida não passa.

## De onde vem o apoio

Na ordem de preferência:

1. mídia oficial ou demonstrativa que o editor forneceu;
2. acervo local com origem e licença registradas (`procedencia.md`);
3. pesquisa licenciada;
4. mídia gerada, marcada como tal no manifesto (`producao-gemini.md`).

**Com material de referência fornecido, o topo é footage o tempo todo.** O dono
foi taxativo: *"não quero momento nenhum com motion graphics eu quero 100% do
tempo com trechos dos vídeos de referência, eu mandei vídeos oficiais que tem
ilustração pra tudo"*. Motion graphic só entra no trecho que o editor
**nomear** como exceção, ou onde o footage fornecido não mostra a coisa dita.
No projeto 08 a exceção foi o fluxo "clicar → roteiro pronto → vídeos → editado".
Um fluxo de aplicativo não se filma com o aparelho de outra marca.

Quando o motion é a exceção, ele sai no estilo `bento-ui` (`estilos.md`), não no
`noturno`. O pedido foi *"faça mais bonito, mais elegante, estilo bento
uiux"*.

Com o footage de terceiros:

- **Texto queimado sai.** Legenda, título ou tagline do vídeo de origem
  ("This is Duo.") é recortado ou mascarado. O único texto na tela é o hook e a
  legenda desta edição.
- **Um trecho por ideia**, reenquadrado e com push-in discreto, sem cartão,
  rótulo ou efeito por cima. Um trecho oficial preciso vale mais que muitas
  imagens genéricas trocando rápido.
- **Acelerar para caber na frase é legítimo** (a abertura do aparelho entrou a
  1,55× para fechar o gesto dentro de "ela finalmente inovou").
- Download do YouTube chega em **AV1**, e o verificador do HyperFrames trava sem
  erro decodificando AV1. Faça cópias de trabalho em H.264 (`h264_videotoolbox`,
  sem áudio, mesmo timecode) e deixe o original intacto. Ver `rotas-de-geracao.md`.
- Afirmação da fala sobre o produto passa pelo `fatos.json`, como qualquer
  outra. "Bateria que dura mais de 30 horas" virou `ATÉ 31 h*` com a nota da
  condição da fonte oficial. "Você abre e tem um mini iPad" é metáfora: mostra a
  tela interna e não afirma que é um iPad. O fluxo de edição com um clique
  aparece como ilustração, sem selo de recurso do aparelho.

## Hook e legenda nesta forma

- **O hook atravessa a junção.** O texto fica centrado em y 840, metade
  em cada região. Foi o pedido: *"letras amarelas, com sombras, e posicionadas
  no meio entre ambos os vídeos"*. No projeto 08 o hook usou amarelo `#FFD83D`,
  Montserrat 900, tracking apertado e profundidade por cópias deslocadas, não
  por contorno grosso. Desde 2026-09-11 a fonte e as cores do hook são as de
  `formatos.md` (Fraunces display, âmbar e creme); desta forma ficam só a
  posição na junção e a profundidade.
- **Legenda no fim da região de cima, nunca sobre o rosto.** A caixa começa em
  y 682 e assenta a base logo acima da junção. Usa o preset de `formatos.md`:
  Montserrat 700, branco quente `#FFF8EC`, sombra
  `0 5px 14px rgba(0,0,0,.92), 0 2px 3px rgba(0,0,0,.96)`, sem caixa nem
  contorno, **até quatro palavras por vez**, sem sobreposição entre blocos.
  Foram 64 px e tracking −1,8 px a 1080 de largura.
- **Sem legenda durante o hook.** O texto do hook já está na tela, e duas
  camadas de texto brigam.

## Ritmo e montagem

- Decupe e aprove o corte antes de montar a divisão (é a etapa 1 de sempre).
- Troque o apoio em fronteira de sentido, de ação ou de evidência, nunca em
  intervalo arbitrário.
- **A imagem do apoio pode chegar 4–7 quadros antes da palavra-chave**
  (133–233 ms). Isso é antecipação de imagem, e a voz não se move: a regra de
  `sincronia.md` fala do som, e aqui o som fica colado na boca.
- Quem fala fica contínuo embaixo o vídeo inteiro. Só o topo troca.
- O gancho pode quebrar a grade por um instante, desde que a legibilidade e a
  intenção sejam deliberadas.
- **Sem J-cut na voz de quem está em quadro.** A linha do Codex mandava
  "antecipar o áudio 2–4 quadros quando houver cobertura segura". Na tela
  dividida quem fala **está sempre em quadro**, então a cobertura segura não
  existe. A 30 fps, 2 a 4 quadros são 67 a 133 ms de voz antes da boca, e o
  limite perceptível é 45 ms (`sincronia.md`). A gramática do app do Codex
  (`FormatEditorialGrammar.splitScreen`, `prefersJCut: true`) ainda carrega a
  regra antiga. Antecipar só vale para o som do **apoio**, e só quando o apoio
  tem som, o que em geral não tem.
- Trilha opcional. No projeto 08 a voz foi a única trilha, e SFX só no abrir do
  hook, se ajudasse.

## Portões desta forma

- `enquadrar_rosto.py` sem colisão, ou com cada intervalo de colisão coberto
  pelo matte. Afirmar "cabelo inteiro" sem essa medida não conta.
- Tracking sem tremor, salto de crop ou atraso perceptível quando a cabeça muda
  de posição.
- O apoio nunca cobre o rosto por acidente.
- **Nenhuma linha, barra ou sombra na junção dos dois vídeos.** Confira num
  quadro parado, ampliado em y 830–850: as duas imagens se tocam.
- O apoio corresponde ao que está sendo dito naquele instante.
- Nenhum texto queimado do footage de origem na tela.
- Texto e elemento importante respeitam as áreas seguras (`linguagem-visual.md`).
- Nenhum áudio de B-roll concorre com a voz.
- Matte, quando usado, sem halo, flicker ou perda visível de cabelo.
- Nenhum trecho oficial preto no preview. Bloco de footage é composição de vídeo
  pura, sem camada escondida por cima (`rotas-de-geracao.md`).
- Quadros do início, meio, clímax e fim vistos a olho, não só medidos.
