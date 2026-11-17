# Movimento — o vocabulário que o template executa

A pior coisa que pode acontecer com um motion graphics é não ter motion: uma
sequência de cartelas de texto trocando. Isso é uma apresentação de slides com grão
por cima. O feed passa direto.

**Todo plano tem movimento.** Não "quase todo". Todo. Se você não consegue dizer em uma
frase o que se move naquele plano, o plano ainda não existe — existe um layout.

## As três camadas de movimento

Um plano bom tem as três. Um plano fraco tem só a primeira.

1. **Câmera** — o quadro inteiro se aproxima, recua ou desliza. É o mínimo, e sozinho
   não sustenta.
2. **Conteúdo** — algo dentro do quadro entra, cresce, se acumula, quebra, some.
3. **Transição** — o plano sai de um jeito que **significa alguma coisa** em relação ao
   próximo. O corte seco é uma escolha; varrer o quadro para revelar o vazio é outra.

## Câmera — `camera`

```
push-in    1,00 → 1,06 na duração do plano   padrão, quase todo plano
pull-out   1,08 → 1,00                       revelação de contexto
parallax   camadas a 100% / 70% / 40%        imagem gerada, dá profundidade real
estatico   só o grão vive                    peso, dado, cartela dura
```

Um movimento por plano, nunca dois.

## Entrada — `entrada`

```
corte      já está lá                        o padrão
deslizar   entra pela direita                continuidade com o anterior
subir      entra por baixo                   acréscimo, item de lista
escalar    chega de 1,14 assentando em 1     ênfase, revelação
```

## Saída — `saida`

A saída acontece **por cima do plano seguinte**: a sequência se estende por 13 frames
(0,43 s) e o que sai revela o que já está embaixo. É por isso que a saída carrega
sentido.

```
corte      substituição seca                 o padrão
varrer     o conteúdo é empurrado para fora  "isso acabou, sumiu, não voltou"
empurrar   escala até 1,34 e sai por cima    "isso te engoliu"
implodir   recolhe ao centro e some          "isso encolheu até virar nada"
apagar     desaparece no lugar               "isso se dissolveu"
```

**Não** use flash branco nem whip pan: os dois lavam o preto levantado, que é a base da
identidade, e o quadro seguinte volta chapado.

## `palavras` — tipografia cinética

O plano para quando a fala **enumera**. "Cama. Descanso. Cansaço. Acordar." não é uma
cartela: é um **acúmulo**. As palavras entram uma a uma, no ritmo em que são ditas, e
ficam na tela empilhando. As mais antigas recuam de corpo e de opacidade; a que acabou
de entrar é a maior.

```json
{ "tipo": "palavras", "palavras": ["cama","descanso","cansaço","acordar"],
  "saida": "varrer", "movimento": "as dez palavras se acumulam e são varridas para fora" }
```

O acúmulo na tela é uma **promessa**. O plano seguinte existe para quebrá-la: as palavras
são varridas, e o que aparece embaixo é a pessoa que não lembrou de nenhuma. Sem o
acúmulo, essa quebra não acontece — o espectador não tem o que perder.

## Como pensar cada plano

Três perguntas, nesta ordem:

1. **O que entra?** O que aparece que não estava antes.
2. **O que acontece?** O que muda enquanto o plano dura. Se nada muda, o plano é um
   pôster.
3. **O que sai, e como?** A saída é a ponte para a próxima ideia.

Escreva a resposta no campo `movimento`, em uma frase. Se a frase for "o texto aparece",
volte e pense de novo.

## O que conta como movimento fraco

- Texto que entra com fade e fica parado até o corte.
- Push-in em cima de uma imagem que já é estática, sem mais nada acontecendo.
- Três planos seguidos com a mesma entrada e a mesma saída.
- Movimento que ilustra a palavra em vez do argumento: a fala diz "crescimento" e uma
  seta sobe. Isso é ícone animado, não motion graphics.

## Teste do movimento

Pegue qualquer janela de 2 segundos do vídeo. Se nela **nada muda além do grão e de um
zoom lento**, aquele trecho falhou. Não é rigor excessivo: é literalmente o critério
pelo qual o feed decide se continua rodando.

## Curvas, durações e onde o push-in não entra

Veio da linha do Codex (`visual-system.md`). Não contradiz nada acima: diz
**com que curva** o movimento acontece.

```
entrada controlada   0,4–0,7 s   power4.out ou expo.out     (o hf.py usa power4.out)
revelação por máscara            power3.inOut
leitura antes da troca  1,2–2,2 s                          (ritmo.md: nunca < 1,2 s fora de batida)
```

- Nada de easing linear no elemento principal. A exceção é o **enquadramento
  de quem fala** (`enquadrar_rosto.py`), em que a curva já vem suavizada e o
  linear é o que garante que a cabeça não sai da caixa.
- **O corte seco é o idioma dominante.** Máscara, glitch e transição elaborada
  só com mudança de ideia, de mídia ou de época.
- **O push-in de câmera não é automático em toda classe.** `arquivo` se move por
  zoom documental e destaque localizado, `cotidiano` pela câmera humana do
  celular, `pessoa` por plano estável e sustentado, `obra` por Ken Burns lento.
  Continua valendo que todo plano tem movimento; o que muda é que, nessas quatro
  classes, o movimento é o da própria classe (`catalogo-visual.md`), não o
  push-in sintético.
- **Um acento dominante por cena**, e destaque em uma ou duas unidades de
  sentido no máximo. Quando tudo acende, nada acende.

