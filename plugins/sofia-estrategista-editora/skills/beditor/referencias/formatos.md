# Formatos — o mesmo estilo, ritmos diferentes

O **estilo** (`estilos.md`) diz como cada classe aparece. O **formato** diz o que o
vídeo é: quantos planos ele tolera, se há motion, se há música, como a abertura
prende. Um canal tem um estilo e vários formatos.

O formato é declarado no cabeçalho do guia:

```json
{ "formato": "dinamismo", "estilo": "noturno" }
```

---

## `dinamismo` — o rosto sustenta, o corte carrega

**Quando é este.** O vídeo é o autor contando algo em primeira pessoa: bastidor,
processo, opinião, convite. Sem tese a demonstrar, sem número a provar, sem
mecanismo a explicar. A energia vem da fala e do ritmo do corte, não de gráfico.

**Como se reconhece na gravação:** take único de celular, rosto na câmera do
primeiro ao último segundo, nenhuma tela para mostrar, nenhum dado a citar.

### As regras

**Motion: nenhum.** Todo momento é `aroll`. Não é economia — é a decisão do
formato. Gráfico aqui interrompe a única coisa que está segurando o vídeo, que é
a pessoa falando. Se o diretor sentir falta de motion, o material provavelmente
não é `dinamismo`; é outro formato mal identificado.

**Silêncio: apertado até doer um pouco, e não além.** As pausas saem — as de
respiro entre frases e as emendas entre takes. Um vídeo de 2:29 gravado vira
2:05 no corte, e é o corte que dá o nome ao formato. A mesa faz isso com `R`; o
respiro que sobra em cada ponta é o que impede o corte de ficar ofegante.

Dois limites existem porque apertar sem eles gagueja, e o editor ouviu isso:
**um corte precisa comprar tempo suficiente para pagar o solavanco** (buraco
menor que 300 ms não paga) e **o que sobra dos dois lados precisa ser um plano**
(pedaço menor que 1,2 s não é plano, é lampejo). O `montar.py` desfaz sozinho o
corte que não passa nos dois — junta de volta e devolve o material. Medido no
05: oito pedaços curtos, um deles de 852 ms entre dois cortes secos, no meio de
uma frase contínua. Custou 2,6 s desfazer, e o vídeo respira.

**J-cut de voz: nenhum.** Isto foi aprendido do jeito caro — três masters entregues,
os três com o áudio fora de sincronia, e o editor achando o erro antes de mim.
O J-cut adianta a voz de quem entra sobre a cauda de quem sai. Se o que sai é o
rosto de quem fala, a voz corre à frente da boca — e não só na emenda: dura o
trecho inteiro. Em `dinamismo` a imagem é rosto do primeiro ao último segundo,
então **não existe lugar onde o J-cut caiba.** O `audioAntesMs` fica em 0, e a
voz sai do próprio A-roll, quadro a quadro com a imagem.

O que tira a monotonia da sequência de cortes aqui é o corte em si — onde ele
cai, no meio da palavra ou depois dela — e o hook. Não é o áudio adiantado.

A regra geral do J-cut, para quando um formato com motion existir, está em
`sincronia.md`.

**Quando o dono pede "jcut" aqui, o que ele quer é a emenda sutil — e ela é o
split edit tipo L.** Pedido de 2026-09-27 (vídeos 19 e 20): *"quero jcut nos
cortes pra ficar mais sutil e fluido, e quero que tenha cuidado para nao
dessincronizar o áudio"*. A resposta que foi aprovada e publicada: a **imagem**
do pedaço que entra adianta **6 quadros (200 ms)**, e só em corte cuja folga
removida foi silêncio medido **e** cuja cauda do pedaço que sai está calada. A
voz não se move um quadro — continua uma pista só, cortada em PCM. Não chame de
"J-cut de voz" nem mova áudio: é a imagem que entra cedo, sobre boca fechada.

**Zoom: só em ênfase, e só sai num corte.** Pedido de 2026-09-27: *"tem que dar
zoom somente em enfases [...] avaliando o roteiro por inteiro e o volume da minha
voz [...] e um zoom out só quando tiver um corte, após o zoom in"*. Nada de
quantidade de zoom por minuto, nada de repartir o A-roll em pedaços de tamanho
fixo girando uma lista de escalas — isso é zoom "fora do lugar" e o dono vê na
hora. O `montador.py` acha o pico de volume que salta ≥ 8 dB sobre 6 s de
vizinhança e está acima do percentil 88 do take inteiro; plano sem pico real
fica 1,0× do início ao fim. O zoom só desce num corte de verdade (inclusive o
de silêncio). E o take de celular **já chega vertical e em close**: escala
máxima baixa — editar como se fosse horizontal (1,45×) estoura o rosto e corta
a tela que o dono aponta.

**Hook: tipografia, não gráfico.** Três linhas curtas, entrando escalonadas
nos primeiros 4 s por cima do rosto, com margens que não se alinham. Ele viaja
no guia como `hook`, não como momento:

```json
"hook": { "linhas": ["pov:", "terminei o e-book", "em uma tarde"], "destaque": 0, "ateMs": 3800 }
```

A fonte, a cor e o tamanho vêm da galeria de estilos (`galeria-estilos.md`,
`scripts/estilos.py`), escolhida em `guia.estilos.hook`. O padrão da casa é
`vox`; `editorial` (Fraunces, âmbar sobre creme) é a referência aprovada pelo
dono em 2026-09-11 e continua disponível como alternativa — escreva no
`porque` quando trocar do padrão.

Vale a mesma regra do gancho falado, em qualquer estilo: o hook escrito nomeia
o que o vídeo entrega, não convida a ficar. "Como fazer dinheiro usando Claude"
funciona; "você não vai acreditar" não.

**Legenda: também da galeria** (`guia.estilos.legenda`, padrão `vox`). Sem
caixa dura, sem contorno grosso em qualquer estilo. Uma por vez — grupo que
ainda está saindo quando o próximo entra vira borrão, porque todos ocupam o
mesmo lugar.

**Posição: logo abaixo da boca, fixa.** Pedidos de 2026-09-27, na ordem em que
vieram: *"a legenda precisa ficar menor, com sombra e mais acima pra nao ser
tampada pela UI da rede social"*, e depois *"ficou na frente da minha boca [...]
um pouco abaixo da minha boca, pode usar facetracking [...] mas as legendas nao
devem se mover com o tracking"*. O `legenda_hf.py` faz isso sozinho: mede a boca
no `rosto.json` (percentil 75 do vídeo inteiro), soma 3,5% de folga e usa **uma
altura para o vídeo todo**; nunca abaixo de 80% (a faixa que TikTok/Reels cobrem)
e com largura máxima de 78% (a coluna de botões à direita). Corpo 4,4% da
largura (~84 px) e sombra em duas camadas — contato duro + halo largo — para
não sumir em fundo claro. Os antigos 70% ficavam "muito embaixo".

**Cor: nenhuma.** Sem a grade de identidade. Contraste e nitidez leves na
luminância, sombra um pouco mais fechada, e nada mais. Nada de aberração
cromática, bloom, vinheta, grão ou dessaturação — em rosto com luz de janela isso
soma em pele rosada, e foi recusado com todas as letras.

**Música: nenhuma.** A cama sintética em fala seca não vira música, vira chiado
atrás da voz. `"semMusica": true` no guia.

### O que sobra para o diretor decidir

Com motion, música e cor fora, restam três decisões, e são elas que fazem o
vídeo: **o que fica e o que sai**, **onde o corte aperta**, e **as três linhas do
hook**. É pouca coisa e é tudo — um `dinamismo` bom e um ruim se separam aí.

### Densidade

A trava de densidade de motion (40–60%) **não se aplica**. Um guia `dinamismo`
com 0% de motion está certo, e o validador não deve ser convencido do contrário
com gráfico de enfeite.

---

## `analise` — o vídeo é sobre o vídeo de outra pessoa

**Quando é este.** O autor escolhe um criador nomeado, afirma que aquele perfil
domina alguma coisa, e prova a afirmação com os posts do próprio analisado. Uma
aula em que o material didático é o trabalho de um terceiro.

**Como se reconhece na gravação:** take único de rosto na lente, como o
`dinamismo` — a diferença não está no bruto, está no que entra por cima dele.

Tem espinha fixa (prova → veredito → credencial → promessa numerada → três
capítulos em 20%, 47% e 70% → objeção do espectador → CTA falado), quatro
registros de imagem (A-roll, cartão de prova, preto e branco, tipografia), cama
musical sem evento e SFX por evento, não por corte. **Não leva motion graphics,
não leva grade de cor e não leva cartela de encerramento**; a trava de densidade
de motion também não se aplica.

Duração medida: **2 a 2 min 40** — é longo de propósito, porque três provas não
cabem em um minuto.

O vídeo do analisado entra de **três modos**, e a escolha entre eles não é
estética — é a pergunta de quem tem a voz naquele segundo: o autor falando põe o
cartão **atrás** dele (recortado, clipe mudo); o clipe falando põe o cartão **na
frente**, com o autor apagado atrás de um fundo em P&B e desfocado.

A especificação inteira, com as medidas tiradas de quatro reels do corpus, está
em **[`formato-analise.md`](formato-analise.md)**: os três modos com geometria,
os seis critérios de escolha do trecho, a aproximação lenta (2–4% por segundo,
sem a legenda acompanhar), as transições contadas, os três registros de
tipografia com números, o critério de música e de SFX, e o contrato do que o
editor entrega e do que o bEditor busca sozinho.

---

## Os outros formatos

Ainda não escritos. Quando um terceiro formato aparecer, ele entra aqui com o
mesmo recorte: quando é este, as regras, e o que sobra para o diretor decidir.
Um guia sem `formato` declarado segue o comportamento antigo — motion decidido
caso a caso.
