# Saída dos cutaways

Corte seco de uma composição cheia direto para o rosto lê como tranco. E **repetir a
mesma saída** em todas as cenas vira tique. Três tipos, alternados, nunca dois iguais
seguidos:

| Tipo | O que acontece | Quando |
| --- | --- | --- |
| `slide` | a mesa é puxada para fora do quadro e o vídeo aparece atrás | padrão |
| `wipe` | uma folha atravessa a lente; atrás dela o vídeo já está lá | quando se quer o "clarão" |
| `push` | a câmera acelera para dentro e o corte cai na velocidade | fecho de ideia |

13 frames a 29,97fps (~0,43s), com aceleração (`ease_in`, t^2.4).

## O quarto tipo: travelling contínuo

Os três acima **marcam** a passagem. Há um caso em que se quer o contrário — encadear
duas cenas de motion seguidas sem que o corte apareça. A Vox resolve com um movimento
que **atravessa o corte**: a câmera já vinha recuando antes, e continua recuando depois,
na mesma direção e na mesma velocidade.

O que vende o efeito não é o movimento, é o **desfoque com pico exatamente no corte**:

- a rampa de escala é **longa** — cobre as duas cenas, ~20 frames de cada lado, com
  `ease` só nas pontas e velocidade constante no meio;
- o desfoque é **curto**: sobe e desce em ~6 frames, com o máximo caindo no frame do
  corte. Some antes de o espectador registrar que existiu.

Desfoque tão longo quanto o movimento lê como erro de foco. A assimetria entre os dois
é o efeito inteiro.

**Só entre duas cenas de motion, nunca de volta para o rosto.** Atravessar o corte com
escala e desfoque exigiria reprocessar o plate ao vivo, e a montagem por sobreposição
(`SKILL.md`, etapa 7) não permite. Para voltar ao rosto, use os três de cima.

Como ele não marca a passagem, **não conta na alternância** — duas cenas ligadas por
travelling ainda precisam de saídas diferentes quando enfim voltarem ao rosto.

## Por que não flash branco nem whip pan

A Style Bible §13 lista os dois entre o que **mata o estilo**, junto com glitch e
"transições de template". Quando pedirem flash, entregue o `wipe`: dá o mesmo clarão,
mas **material** — é o "papel que cruza a lente" que o pack indica
(`09_TRANSITION_MAP §2`). Quando pedirem efeito de câmera, entregue o `push`, que é o
"zoom na prova" do mesmo documento.

Vale dizer isso ao diretor uma vez, e seguir. É o tipo de conflito que se resolve com
um equivalente, não com recusa.

## Implementação

Os cutaways renderizam em **RGBA**: a área que a mesa liberou fica transparente e o
`overlay` do ffmpeg deixa o vídeo original passar por baixo. O `push` é a exceção — o
quadro segue opaco e quem esconde o corte é a aceleração.

A folha do `wipe` usa um papel **diferente** do fundo da mesa (cartão de algodão frio
contra marfim), senão a passagem não lê.
