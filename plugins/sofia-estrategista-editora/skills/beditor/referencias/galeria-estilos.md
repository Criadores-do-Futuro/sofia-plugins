# Galeria de estilos — hook, legenda, motion, música e SFX

## B-roll no fluxo CapCut

| id | Aparência e movimento | Quando usar |
| --- | --- | --- |
| `collage-broll` | Papel de cor chapada, recortes fotográficos P&B com retícula, detalhes de cartolina colorida, borda creme e sombra suave. As peças entram em sequência e constroem uma metáfora, com câmera fixa. | Ilustrar uma fala curta ou conceito abstrato; opção inspirada no projeto `gbro-collage-broll`. |

Leia [collage-broll.md](collage-broll.md) ao selecionar essa opção: contém direção,
etapas de revisão, adaptação para geração no CapCut e verificações de qualidade.
Registre `estilos.broll: "collage-broll"` apenas no guia editorial local; não é
um atributo do STDraft nem um ID aceito pelos validadores antigos. Este estilo
não exige Gemini, uma segunda skill instalada ou outro renderizador.

As seções abaixo preservam a galeria anterior. No fluxo CapCut, suas descrições
servem como direção; comandos e campos dos motores locais não são executados
automaticamente. A marca e o pedido atual continuam prevalecendo.

Pedido do dono, em 2026-09-11: *"de preferência pra mim no estilo vox style,
mas podendo trocar de estilo... uma galeria de estilos para hook visual, para
legendas, músicas, SFX etc, sempre deixando intuitivo e elegante."*

Cinco elementos — `hook`, `legenda`, `motion`, `musica`, `sfx` — cada um com
uma galeria de estilos nomeados. O guia escolhe no cabeçalho:

```json
"estilos": { "hook": "editorial", "legenda": "vox", "motion": "vox",
             "musica": "vox", "sfx": "vox" }
```

Campo ausente = o padrão da casa: **`editorial` no hook** (pedido do dono em
2026-09-11, depois de ver o vox no hook: *"o hook visual prefiro como estava
antes do vox, quero vox pra motion"*) e **vox no resto**. `scripts/estilos.py`
é a fonte única dos valores — este arquivo só descreve o que já está lá, para
gente escolher sem ler código. `validar.py` recusa um id que não existe na
galeria.

**A regra que nenhum estilo pode quebrar:** contraste real sobre o rosto e o
fundo, no máximo duas cores por camada, uma curva de movimento só — nunca
easing misto no mesmo elemento —, e nada que precise de legenda pra ser lido.
Elegante aqui é sinônimo de legível; um estilo que exige esforço pra ler não
entra na galeria, por mais bonito que seja parado.

**Quando a marca já fixou algo:** o `motion.md` da marca do projeto (gerado
por `/sofia-estrategista-editora:branding`, fora do plugin) e os `estilos` do `marca.json` podem já
ter decidido a tipografia do hook para aquele canal ou cliente. Onde ele fala, ele decide antes desta galeria: o diretor escreve a
decisão da marca direto em `guia.estilos`, e o padrão `vox`
daqui só vale pros canais e formatos que ainda não fixaram nada.

## Hook

| id | o que é | quando usar |
| --- | --- | --- |
| `vox` | Archivo Black em caixa alta, tracking apertado. Cada linha carrega uma barra de cor sólida atrás — a linha de destaque em âmbar `#F0B95B` com texto tinta `#211315`, o resto em tinta translúcida `#211315` a 82% com texto creme `#FFF6E7`. Sem sombra: o contraste vem da barra, não do véu. Entra com um leve estouro (`back.out`), sai rápido. | O padrão. Cartaz, direto, lê em qualquer fundo — inclusive vídeo claro e ocupado, porque a barra garante o contraste sozinha. |
| `editorial` (padrão) | Montserrat 800 em caixa alta (a mesma voz da legenda `editorial`), duas cores sem barra — destaque em âmbar `#F3B35C`, resto em creme `#EFE7D6` — só um véu de sombra. Entrelinha apertada, entrada suave (`power4.out`). | Quando o vídeo já é quieto e composto (retrato parado, luz mole) e uma barra sólida brigaria com a imagem. A composição foi a referência aprovada pelo dono em 2026-09-11 (quadro *"pov: / Life with"*); a fonte era Fraunces serif até 2026-09-12, quando o dono pediu *"use montserrat no hook visual"* — hook e legenda estavam discordando. |
| `minimal` | Inter 900 caixa alta, sem barra, corpo menor (7,5% da largura). Só um véu leve de sombra. | Quando o hook não pode competir com o resto da composição — telas divididas com muito conteúdo, ou um `M01` que já é gráfico por si. |
| `explicativo` | Montserrat 900 caixa alta, corpo grande (12,5% da largura), tracking bem fechado (`-0.02em`), branco puro com o destaque em **amarelo-limão `#E8FF3A`**. Sem barra: **sombra em duas camadas**, contato duro `(2, 6, 0.85)` e halo largo `(0, 18, 0.55)`. Entra rápido com quique curto (`back.out(2.4)`, 0,16 s). | O par do `dinamismo` no estilo `explicativo`. O hook é a mesma voz tipográfica da legenda, porque neste estilo tipografia é o único grafismo que existe. |

## Legenda (a leitura do corpo do vídeo)

| id | o que é | quando usar |
| --- | --- | --- |
| `vox` (padrão) | Archivo Black caixa alta, barra de tinta translúcida atrás da linha inteira, entrada com estouro curto. | O padrão: lê rápido, funciona sobre qualquer fundo sem depender de sombra. |
| `editorial` | Montserrat 700, sem barra, só sombra macia — o preset descrito em `formatos.md` para o `dinamismo`. | Quando a barra da legenda competiria com a barra do hook na mesma composição, ou o canal já usa este preset (ver o `motion.md` da marca do projeto). |
| `ilustrativo` | A `vox` sem a barra: mesma Archivo Black caixa alta, mesmo creme `#FFF6E7`, mesmo corpo, mesma entrada. No lugar da barra, **sombra em duas camadas** — contato `(3, 8, 0.62)` e halo `(0, 26, 0.5)`. | O par da legenda com o motion `ilustrativo`. Pedido do dono em 2026-09-12: *"não use essas barras pretas nas legendas, use apenas sombra, pode manter a fonte e a cor"*. |
| `explicativo` | Montserrat 900 caixa alta, **corpo grande: 7,2% da altura** contra 5,2% da `vox`. Branco puro, sem barra, com a mesma sombra de duas camadas do hook `explicativo` — contato `(2, 6, 0.85)` e halo `(0, 18, 0.55)`. | O par obrigatório do formato `dinamismo` no estilo `explicativo`. Ela é grande porque **é o único grafismo do vídeo**: sem motion, o que segura o olho entre um corte e o próximo é a palavra que entra. |

**Por que a `explicativo` é maior que todas as outras.** Nos outros estilos a
legenda divide o quadro com motion, cartela ou gráfico, e crescer demais seria
brigar. No `dinamismo` não há com quem brigar: o quadro é rosto do primeiro ao
último segundo. A legenda deixa de ser a leitura do que é dito e passa a ser a
*batida* — é ela que marca o ritmo que o motion marcaria em outro formato. Daí
o corpo grande, o tracking fechado e a entrada com quique curto: ela tem de
chegar antes de a próxima palavra ser dita.

**Por que duas camadas de sombra, e não uma.** O fundo aqui é pele e madeira, e
a medição do corpus diz por quê: 43% do quadro abaixo de 40/255, mas com 3%
acima de 235 — a janela atrás da cabeça. Uma sombra só não resolve os dois: o
contato curto e duro dá o piso da letra sobre a testa iluminada, e o halo largo
a separa da madeira escura. É a mesma solução da `ilustrativo`, por um motivo
diferente — lá o problema era creme sobre creme, aqui é um fundo que tem as duas
pontas ao mesmo tempo.

**Por que duas camadas de sombra, e não uma.** Uma barra dá contraste sobre
qualquer fundo de graça; sombra não. A de **contato** (deslocada pra baixo,
blur curto) desenha o piso da letra e some sobre branco. O **halo** (`dy` 0,
blur largo) escurece o fundo em volta do glifo e, sozinho, borra a forma.
Juntas, uma define a letra e a outra separa do fundo — que no estilo
`ilustrativo` é creme `#F2EFE8`, onde legenda creme com sombra fraca
desaparece. `_sombra()` no `legenda_hf.py` aceita a tripla de sempre **ou uma
lista de triplas**; estilo antigo com uma tripla só continua idêntico.

**O que sai junto com a barra:** o `padding` do chip, que era a margem lateral
de fato. Sem ele a linha encosta na borda do quadro, então `.lg .chip` ganhou
`max-width:88%` — inofensivo para quem tem barra, necessário para quem não tem.

### Os dois registros do formato `analise`

O formato `analise` não usa os ids da tabela acima: ele tem registros próprios, que
valem para a legenda, para a palavra em destaque e para o marcador de capítulo ao mesmo
tempo. Escolhidos em `dados.estilos.legenda`; sem o campo, `minusculo`.

| id | o que é | quando usar |
| --- | --- | --- |
| `minusculo` (padrão) | Caixa baixa em tudo. Legenda de diálogo em Montserrat variável 500, 46 px, branco puro, só sombra difusa. Destaque e marcador em **duas vozes**: sans geométrica negrito grande como apoio, Fraunces Italic menor encostada por baixo como a palavra. | O padrão desde **2026-09-15**, quando o dono mandou as duas capturas de referência: *"use legendas assim quando for ilustrar pontos, partes, etapas, e use legendas assim para os diálogos"*. Vídeo novo do formato entra aqui. |
| `explicativo` | O registro anterior: caixa alta, Arial Bold, creme, sombra dura, contraste de **corpo** (palavra em destaque a 143 px contra ~54 px do apoio). | Vídeo já aprovado neste registro — 14 e 15. Rerenderizar um deles sem gravar `explicativo` faz o master mudar sozinho na próxima rodada. |

**Onde isso mora.** A descrição completa dos dois registros, com as medidas de cada um,
está em `formato-analise.md`, seção "Tipografia — três papéis, dois registros". O desenho
está em `cartao.py`: `tipografia()` lê e define o registro, `sans()` e `serifa_italica()`
abrem as fontes variáveis no peso pedido, `titulo_duas_vozes()` desenha as duas vozes, e
`legenda()`, `frase_hook()` e `marcador()` bifurcam nos dois registros.

## Motion — o vídeo desenhado inteiro

Este é o estilo do motion graphics: a paleta e as fontes das composições
(`hf.py`), o acabamento analógico por cima delas, e a **matéria** que entra em
todo prompt de imagem (`assets.py`) — é ela que faz a imagem **gerada** sair no
mesmo estilo da composição, em vez de sair genérica e brigar com ela.

Cada entrada diz de onde veio: quem mudar um valor confere na referência, não
no gosto do dia.

| id | o que é | de onde veio |
| --- | --- | --- |
| `vox` (padrão) | **Colagem, não paleta trocada.** O estilo tem composições próprias (`hf_vox.py`): papel creme com grade técnica de milimetrado e fibra no grão; manchete em serifa de jornal com **grifo de marca-texto amarelo** que avança *aos pedaços*, como mão que passa o marcador; **anotação vermelha à mão** (elipse, seta, sublinhado) que aparece *desenhando*; recorte de foto em **preto e branco com borda de tesoura**, colado torto com fita crepe; rótulo em máquina de escrever e linha de chamada tracejada. | `Treinamento/youtube-knowledge/LiQPU7_5v68` — *"Create Motion Graphics with Claude (Vox-style & More)"*, 16 folhas de contato e a transcrição, mais o quadro de templates que o dono mandou em 2026-09-11 |
| `noturno` | 3D branco luminoso sobre preto frio, rim light âmbar e ciano, destaque ouro, vinheta fechada, meio-tom e grão de luz. É o estilo medido do canal, e os números são exatamente os de antes da galeria existir. | `Treinamento/tiktok-julianealborna` — 2.623 frames em 12 categorias |
| `techtok` | Imagem filmada ocupando o quadro inteiro, sem grafismo desenhado; grade neutra e fria, chip vermelho `#E63A2E` na palavra que a legenda destaca, apresentador em janela pequena. A lição do corpus é editorial antes de gráfica: a imagem é a coisa, filmada. | `Treinamento/tiktok-kanekallaway` — 1.455 frames de 61 vídeos |
| `ilustrativo` | **Composição editorial 2D — página de revista que se move.** Composições próprias (`hf_ilustrativo.py`): camadas planas sobre material citado, cartela creme `#F2EFE8` com textura gravada de cédula e vinco de papel, ou campo editorial `#0D0D0D` para diagrama. **Um acento por quadro** — amarelo Vox `#FFE01B`, rosa `#FF5A7E` ou ardósia `#2E4257` —, escolhido pelo id do plano para não repetir no vizinho. Serifa didone nos numerais (40–60% da altura), itálica minúscula no subtítulo, versalete espaçado nos rótulos, grotesca condensada com algarismo tabular no dado. **As duas leis de movimento: nada quica e nada fica parado** — o texto estala em 4 quadros `power3.out` e trava, e quem se move é o fundo, em deriva contínua de 2–5% do primeiro ao último quadro. `back.out` aqui é erro, não estilo. | Direção escrita pelo dono em 2026-09-12, a partir de vídeo-aula de motion no padrão Vox |
| `gravacao` | **Nem 2D nem 3D: motion design de gravação de tela.** Composições próprias (`hf_gravacao.py`): branco puro `#FFFFFF` contínuo por baixo de tudo — sem horizonte, sem sala, sem textura —, e prints e UI de app como **cards de canto arredondado com sombra real** flutuando nele. Cor só da UI nativa: azul iMessage `#007AFF`, cromo azul-acinzentado do iOS, vermelho do Instagram. Tudo entra em **escala crescente com overshoot curto** (~0,25 s, `back.out`); nada faz deriva lenta. **Nenhum corte duro no miolo**: o card sai em escala enquanto o próximo entra, sobre o mesmo branco. Traz o **Grow Effect** (o print cresce para além da própria moldura), cards empilhados que se separam lateralmente, balão de iMessage subindo com mola, e **título de display com extrusão** e cópia fantasma cinza que desliza até o registro. Terço inferior sempre vazio, para a legenda queimada. | Referência do dono decupada em 2026-09-12: 42 s, **0 cortes duros** no miolo (limiar 0,3), 0 trechos de silêncio a −40 dB, um conceito a cada 4–6 s |

Cada estilo traz quatro coisas, e o `estilos.py` guarda as quatro:

- **`corpos`** — quando o estilo desenha um tipo de plano de outro jeito, a
  composição é dele: `hf_vox.py` tem cartela, palavras, dado, índice, camadas e
  imagem em linguagem de colagem. O `hf.py` só cai no desenho genérico onde o
  estilo não tem o próprio. **Trocar só a cor não faz estilo** — foi a lição de
  2026-09-11.
- **`tokens`** — as cores e as fontes das composições (fundo, texto, cartão,
  janela, borda, halo, destaque…). Trocar o estilo troca a página inteira.
- **`acabamento`** — vinheta, meio-tom, grão, grade e bokeh. São do estilo
  porque vinheta preta sobre papel claro come o quadro, e meio-tom branco sobre
  papel some.
- **`materia`** — a frase que descreve o acabamento da imagem gerada, e que
  entra em todo prompt.
- **`grade`** — o bloco técnico que fecha o prompt de imagem (enquadramento,
  luz, textura, o que não pode aparecer). Até 2026-09-12 existia **uma grade
  fixa** dentro do `assets.py`, escrita para o `noturno`, e ela era colada
  depois da matéria de qualquer estilo: o prompt saía se contradizendo — papel
  creme claro seguido de *"blacks at 12/255, rim light, heavy vignette,
  cinematic, lonely"* — e o gerador obedece o final. Agora a grade é do estilo.
- **`camera`** (opcional) — como o plano inteiro se move. A casa faz push-in em
  Z com décimos de grau de rotação; o `gravacao` troca por escala pura, porque
  ali não existe câmera: o que empurra é o canvas.
- **`transicao`** (opcional) — como uma cena emenda na outra. Sem este campo o
  montador corta seco. Com ele, costura em `xfade`: `entre_rosto` para dois
  reenquadramentos do mesmo take (dissolve curto, que costura o jump cut) e
  `com_motion` para a entrada e a saída de um gráfico (empurrão lateral).

  **A armadilha, e ela é fatal quando passa:** `xfade` **sobrepõe**. Duas faixas
  de 3 s emendadas com 0,2 s dão 5,8 s, não 6. Num vídeo com voz gravada a
  imagem encurta e o áudio não, e a dessincronia acumula a cada emenda. Por
  isso cada pedaço é renderizado com sobra e o deslocamento de cada emenda é a
  **soma limpa das durações nominais** — sem descontar a emenda, sem somar a
  sobra. Confira sempre a duração do master contra a do áudio antes de
  entregar.

---

## O que o montador faz sozinho, e que não é do estilo

Três comportamentos que valem para qualquer estilo e nasceram do pitch de
2026-09-12. Estão no `montador.py`, não na galeria, porque são de **montagem**,
não de aparência:

- **Reenquadramento.** Take de rosto na câmera é plano único: uma tomada, um
  tamanho, e o vídeo fica parado. O montador reparte o A-roll em planos de no
  máximo 3,4 s, cada um num tamanho diferente do anterior (1,0 / 1,30 / 1,15 /
  1,45). É jump cut, e é de propósito — sem segunda câmera, o corte é de escala.
  Levou o pitch de 9,8 para 19 cortes por minuto.
- **O recorte segue o rosto.** `rastrear-rosto` (Vision, local — o rosto não sai
  da máquina) dá a caixa a cada 0,25 s, e `enquadrar_rosto.py` — que já existia
  para a faixa da tela dividida — protege cabelo e queixo. O enquadramento é
  **constante dentro do plano**, pela mediana das amostras do trecho: crop que
  persegue rosto quadro a quadro lê como câmera na mão. Sem rastreamento, cai
  no centro com teto de topo.
- **O acento sonoro só na emenda deslizante.** Swoosh sintetizado (ruído rosa
  em passa-banda que sobe e desce, envelope sem ataque, ~−20 dBFS), e **só onde
  entra ou sai um gráfico**. Emenda de reenquadramento não leva nada: são dez
  delas em 47 s, e um swoosh em cada viraria tique — *"sparse and restrained,
  not a whoosh-fest"*.
- **`moldes`** (opcional) — o tratamento próprio do estilo para um tipo de
  plano. O `personagem` do `noturno` é o boneco branco 3D; o do `vox` é uma
  silhueta de papel azul recortada. O molde genérico (`montar.MOLDES`) diz só a
  **composição** — o que ocupa o quadro e como está enquadrado.

### Os gestos menores do `vox`

Composição resolve o quadro **parado**. O que separa a colagem animada do
gráfico de template é o que acontece no intervalo — e são quatro gestos
pequenos, todos em `hf_vox.py`, nenhum deles um efeito grande:

| gesto | o que faz | onde |
| --- | --- | --- |
| **cadência em passos** | a entrada segura o valor por 2 frames em vez de correr lisa — o 12fps da Vox, caráter de stop motion. Vale para rótulo, número e tipografia de apoio; a **manchete em serifa não**, porque corpo grande travado lê como falha de render. | `passos()` |
| **revelação mordida** | o marca-texto avança aos pedaços desiguais (`0 → 18% → 22% → 55% → 61% → 100%`) e segura entre eles. Progresso linear devolve o wipe de template que a colagem quer evitar. | `mordida()` |
| **fundo em movimento** | a fibra do papel desloca ~2,5 vezes por segundo, o bastante para o plano longo não morrer e de menos para disputar com a fala. Desloca a camada já rasterizada — resemear a turbulência custaria um recálculo de ruído em 1080×1920 por passo. | `_base_js()` |
| **borda de lente** | desfoque e franja de cor **só no anel externo**, miolo limpo. Tira a planura do recorte 2D. Efeito de lente é do olho que olha, não do objeto olhado — no quadro inteiro vira filtro. | `verniz()` |

A regra que amarra os quatro: **movimento acompanha raciocínio**. Traço de mão
(a caneta desenhando, a linha do gráfico) é o único movimento contínuo da cena;
o resto é papel sendo posto, e papel não desliza.

A mesma decupagem, na versão em PIL da skill irmã, está em
`skills/motion-vox/referencias/gestos-menores.md`. As duas pontas do vox
precisam concordar: quem mudar um gesto aqui confere lá.

## Música e SFX

A cama é sempre sintetizada (`trilha.py` — sem biblioteca de terceiro, sem
licença a cumprir). O `estilo` muda a **forma do envelope**, não troca
instrumento: mesmo acorde, mesma cor por `musica.clima`, ataque e corte
diferentes.

| id | o que é | quando usar |
| --- | --- | --- |
| `musica: vox` (padrão) | Ataque curto (40% do normal), corte rápido (55%), pulso 60% mais presente, tensão mais marcada, ganho levemente menor — a cama sobe rápido, pontua e sai do caminho da voz. | O padrão: acompanha corte rápido sem lavar a fala. |
| `musica: editorial` | Ataque e corte no tempo cheio, quase sem pulso — sustentado, respiro longo. | Quando o momento pede espaço, não pontuação — uma revelação lenta, um silêncio armado. |
| `musica: explicativo` | Cama baixa e constante: ganho a 70%, pulso pela metade, sobe e desce encurtados, tensão um pouco mais marcada. | No `dinamismo`, onde a música nunca é o argumento — ela só impede que o silêncio entre dois cortes secos soe como falha. O ritmo já vem do corte e da palavra que entra. |

**SFX ainda não tem execução — falta a biblioteca de efeitos na máquina** (o
painel marca essa falta). `sfx: vox`/`sfx: editorial` só registram a *intenção*
no guia hoje, pro dia em que a etapa existir ler a mesma escolha:

| id | a intenção |
| --- | --- |
| `sfx: vox` (padrão) | Stab seco na palavra-chave, whoosh curto no corte. |
| `sfx: editorial` | Quase nenhum; efeito só quando o momento realmente pede. |
| `sfx: explicativo` | Whoosh curto a cada palavra que entra na legenda, baque grave na virada de argumento. |

## Onde isso mora

- `scripts/estilos.py` — os valores concretos e o validador.
- `scripts/legenda_hf.py` — desenha o hook e a legenda a partir do estilo escolhido.
- `scripts/hf.py` — `aplicar_estilo()` troca a paleta, as fontes e o acabamento
  de todas as composições de motion de uma vez.
- `scripts/montar.py` — leva a `materia` e os `moldes` do estilo para dentro de
  cada prompt de imagem, e o estilo escolhido para dentro do `plano.json`.
- `scripts/trilha.py` — sintetiza a cama com o envelope do estilo escolhido.
- `agents/diretor.md` — escolhe o estilo de cada elemento no cabeçalho do guia.
