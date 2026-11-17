# Estilo visual — `demonstracao` (galeria: `techtok`)

Baseado em `medicoes.json` (1432 frames, 6 grupos por folha de contato) e leitura direta
das seis folhas de contato (g00 a g05, fora do plugin). As 222 fontes originais estão
classificadas nas 12 categorias do treinamento, com maior peso em
09-tela-dispositivo (49), 07-broll-cinematografico (42) e 05-arquivo-found-footage (31).

Paleta global medida: `#0C0C0D`, `#323633`, `#865B42`, `#5A6E78`, `#ABA89F`, `#EDEEEC`.
Y mediana global 61.4, saturação 0.246, temperatura +2.16 (levemente quente),
vinheta 0.259, contraste 53.4 — um estilo mais claro e menos contrastado que
o corpus `noturno` em média, porque metade dos frames são telas de UI muito brancas.

---

## Grupo g00 — telas e renders 3D em fundo claro (356 frames, o maior grupo)

**O que é.** Capturas de tela de apps/produtos e renders 3D de produto (fazenda
vertical robótica, racks, robôs de armazém) sobre fundo cinza-claro a branco quase
estúdio. Cartelas de texto grandes também entram aqui (manchete de produto
em duas linhas). Em vários frames aparece uma bolha circular pequena no canto superior
esquerdo com o rosto real do criador sobre o render — um "webcam bubble" de
picture-in-picture.

**Luz.** Luz de estúdio de produto: chapada, sem sombra dura, fundo em torno de
Y 223 (branco quase estourado, 1.3% acima de 235). Vinheta **negativa** (-0.128) —
ao contrário do resto do estilo, aqui as bordas ficam mais claras que o centro, não
mais escuras. Muito pouca cor na borda (2.47, a mais baixa de todos os grupos):
isso é luz de produto neutra, não rim colorido.

**Tipografia.** Sans-serif bold, branca, algumas palavras em itálico dentro da mesma
frase — mistura peso/itálico na mesma
linha, centralizada, sobre fundo claro (às vezes com leve sombra/contorno escuro
para separar do fundo branco).

**Movimento.** Renders 3D com pan/dolly lento (a câmera desliza sobre a fazenda
vertical, sobre os racks); screen recordings com cursor visível se movendo.

**Quando usar.** Abertura de vídeo (a cartela de título) e
qualquer trecho que mostre o produto/objeto em si — demonstração visual do que está
sendo falado, sem o rosto do criador dominando o quadro.

---

## Grupo g01 — talking-head em estúdio escuro + app no topo (204 frames)

**O que é.** O criador de meio-corpo, filmado com câmera frontal, falando e
gesticulando com as mãos, em ambiente escuro. Em cerca de metade dos frames o
quadro é dividido: metade superior é uma tela de app (editor de IA ou
gerador de vídeo), metade inferior é o busto do criador.

**Luz.** O grupo mais escuro do estilo: Y mediana 14, 83% dos pixels abaixo de 40,
branco só chega a 102 (nada estoura). Vinheta forte (0.481) e cor na borda a mais
alta do estilo (11.54) — a leitura de olho é luz de tela + rim quente/frio nas
bordas do rosto e ombros, não aberração óptica de lente: a cor concentra-se no
contorno do corpo e da tela, não em toda borda do quadro.

**Tipografia.** Legenda curta, uma ou duas palavras por corte, caixa baixa, em
amarelo/laranja sólido, sem caixa de fundo — texto solto sobre o fundo escuro,
alinhado perto da boca do criador.

**Movimento.** Plano estático de câmera (tripé), o movimento é do criador —
gestos de mão constantes enquanto fala. Corte é rápido, quase por frase.

**Quando usar.** Trechos de explicação direta ao espectador, principalmente quando
o criador está demonstrando uma ferramenta de tela ao vivo — a metade de tela
serve de prova visual do que ele descreve.

---

## Grupo g02 — talking-head em ambiente morno + telas de app claras (267 frames)

**O que é.** Mesmo formato de busto falando, mas em ambiente com parede de madeira
iluminada (mais quente e mais claro que g01) e telas de aplicativo predominantemente
claras/brancas (geradores de imagem, dashboards) intercaladas com renders 3D de
objeto (cristal/diamante rosa girando).

**Luz.** Meio-tom: Y mediana 97, contraste é o mais alto do estilo (70.3) —
quadro com parede clara atrás e criador relativamente escuro na frente, ou
tela branca cortando para busto escuro. Temperatura mais quente do grupo (+2.93).

**Tipografia.** Legendas em formato de "pill"/etiqueta colorida com cantos
arredondados (verde, laranja, roxo) e texto branco bold dentro — cor da pill muda
por frase, sempre no terço inferior sobre o peito do criador. Nas telas de app
aparecem títulos institucionais bold sans.

**Movimento.** Estático em câmera, corte por frase; objeto 3D (cristal) gira
lentamente em loop.

**Quando usar.** Comparação de ferramentas/produtos, trechos de "olha o que essa
IA faz" — mistura tela de app com reação do criador.

---

## Grupo g03 — broll cinematográfico e found footage, com legenda serifada (106 frames)

**O que é.** O grupo mais variado tematicamente: fábrica/linha de montagem,
alunissagem (Terra vista da Lua, módulo lunar, astronauta), transmissão esportiva,
still de jogo/cinema, mesa de pôquer, cartela de texto isolada de uma palavra. Aparece de
novo a bolha de rosto no canto (picture-in-picture) sobre o broll.

**Luz.** Meio-tom com maior saturação do estilo (0.298) e o menor grão no preto
(2.48) — imagens de arquivo/renderizadas, não filmadas pelo criador, então sem o
grão de câmera do resto. Vinheta moderada (0.183).

**Tipografia.** A única do estilo em **itálico serifado**, branco, sem caixa de
fundo — uma palavra como cartela isolada, ou duas palavras como legenda
elegante sobre a imagem, mais discreta que as pills bold dos grupos de talking-head.
Também há caixas pretas retangulares com texto branco simples sobre o rodapé da imagem, mais sóbrias que as pills coloridas.

**Movimento.** Pans lentos e órbitas em CG (Lua), cortes de arquivo estático,
corte relativamente lento comparado aos grupos de talking-head.

**Quando usar.** Momentos de metáfora ou abertura de segmento — broll que ilustra
um conceito abstrato antes de voltar ao criador falando.

---

## Grupo g04 — broll cinematográfico frio, textura de laboratório/indústria (275 frames)

**O que é.** Estádio lotado, mãos robóticas (prótese), laboratório
(neurônios humanos em frasco), braço robótico azul em cozinha industrial,
maquinário de precisão, floresta em split-screen com borda roxa. Bolha de
rosto no canto reaparece aqui também.

**Luz.** Vinheta mais forte de todo o estilo (0.668) — cantos bem escurecidos,
centro exposto. Temperatura a mais fria do estilo (-0.851, único grupo com viés
azul) — condiz com os frames de céu/laboratório/metal. Contraste alto (57.6).

**Tipografia.** Também itálico serifado branco, mesmo padrão do g03 — grupo
irmão de g03 no uso de tipografia, mas com paleta mais fria e assunto mais técnico.

**Movimento.** Câmera em plano fixo ou leve tracking em footage de arquivo/stock;
zoom lento em objetos de laboratório.

**Quando usar.** Prova técnica/científica de uma afirmação — quando o roteiro cita
um dado ou avanço concreto ("neurônios reais", "mão com tendões").

---

## Grupo g05 — split-screen escuro: app + talking-head (224 frames)

**O que é.** Metade superior é screen recording de app com acento magenta/roxo
(chat de IA, dashboard), metade inferior é o busto do criador em estúdio escuro
falando e apontando.

**Luz.** Segundo grupo mais escuro (Y mediana 30.5, 65.5% abaixo de 40), branco não
passa de 119 — nunca estoura. Vinheta baixa (0.179), pouca cor de borda (9.43).

**Tipografia.** Legendas em caixa vermelha sólida com texto branco bold caixa alta
curto — a mesma
lógica de pill do g02, mas aqui é sempre vermelho e sempre no meio do quadro, na
linha de corte entre tela e rosto.

**Movimento.** Câmera estática, cursor se move na metade de tela, corte no ritmo da
fala (uma pill por frase).

**Quando usar.** Explicação passo a passo de um workflow dentro de um app — a
metade de tela mostra a ação, a legenda vermelha resume em uma frase o que está
acontecendo.

---

## Leitura global

O `demonstracao` é o estilo de um criador que aparece com o próprio rosto o tempo
todo — seja em busto completo falando, seja como uma bolha pequena de
picture-in-picture sobre broll e renders 3D — e que constrói o vídeo alternando
três blocos: **tela de aplicativo** (a prova do que está sendo demonstrado),
**busto falando** (a explicação) e **broll/found footage/CG** (a ilustração ou
metáfora). A luz vai de estúdio de produto muito clara (g00) a estúdio de talking-
head bastante escuro (g01/g05), sem um piso de preto único como no
`noturno` — a amplitude de exposição é maior porque metade do material é
UI branca e a outra metade é ambiente escuro de gravação. A tipografia tem duas
famílias fixas: **pills coloridas bold sans** (laranja/verde/roxo/vermelho) para os
trechos de fala/demonstração de app, e **itálico serifado sem caixa** para os
trechos de broll cinematográfico — a troca de família tipográfica é, ela mesma,
um sinalizador de que tipo de imagem está na tela. O que nunca aparece: silhueta
anônima ou avatar sem rosto (o oposto do outro criador), fundo perfeitamente
preto, e grão de câmera pesado — a textura aqui vem de compressão de screen
recording e de vinheta, não de grão simulado.

## Aberração óptica — confirmação visual

`preset_sugerido.aberracao_a_confirmar` estava em 0 no `medicoes.json`. Olhando as
bordas nas folhas (especialmente g01, que tem o maior `cor_na_borda` do estilo,
11.54), a cor não se separa em franjas vermelho/ciano nas bordas do quadro — ela se
concentra no contorno do corpo do criador e no brilho da tela ao fundo, como luz de
ambiente/tela refletida, não como aberração cromática de lente. **Confirmo 0**: não
há aberração cromática estilizada neste material, o que existe é vinheta + reflexo
de tela colorida nas bordas.

## O que este criador faz que o outro não faz

- **Rosto real, sempre.** O `noturno` usa avatar branco sem rosto sobre fundo
  `#0B0B0E`; aqui o criador é filmado de verdade — busto completo falando ou uma
  bolha de picture-in-picture com o rosto sobre broll/render 3D. Nunca há silhueta
  anônima.
- **Split-screen fixo tela+pessoa.** Um formato de composição que não existe no
  outro estilo: metade superior do quadro é screen recording, metade inferior é o
  busto do criador, com a legenda pill exatamente na linha de corte entre as duas
  (grupos g01, g02, g05 — mais de 300 dos 1432 frames medidos).
- **Duas famílias tipográficas com função narrativa distinta.** Pills bold coloridas
  (laranja/verde/roxo/vermelho, com fundo sólido) para tela/demonstração e itálico
  serifado sem caixa para broll/found footage — o outro criador usa um único
  registro tipográfico consistente; aqui a tipografia muda para sinalizar o tipo de
  imagem.
- **Amplitude de exposição muito maior entre grupos.** De Y mediana 14 (g01,
  estúdio escuro) a Y mediana 121 (g00, telas/renders quase brancos) — o outro
  estilo mantém um piso de preto mais uniforme; aqui a claridade do quadro é ela
  mesma informação sobre que tipo de conteúdo está na tela (produto/UI = claro,
  pessoa falando = escuro).
- **Vinheta invertida em um grupo.** g00 tem vinheta negativa (-0.128): bordas mais
  claras que o centro, típico de estúdio de produto com fundo infinito, algo que não
  aparece em nenhum grupo do outro criador.
- **Sem grão de câmera simulado.** O grão que existe aqui é ruído de screen
  recording/compressão (mais visível em g00, `grao_no_preto` 16.86, o maior do
  estilo) e não uma textura de grão de filme aplicada de propósito como no outro
  estilo.
