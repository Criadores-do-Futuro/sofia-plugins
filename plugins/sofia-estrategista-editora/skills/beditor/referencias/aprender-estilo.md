# Aprender um estilo a partir de uma pasta de frames

A skill nasceu sabendo dois estilos porque alguém mediu um deles à mão, frame a frame.
Isto é essa medição virada ferramenta: aponte para uma pasta de referências e saia com um
preset utilizável.

```bash
python3 .../scripts/aprender.py --frames pasta/ --nome meu-estilo --out estilos/
python3 .../scripts/aprender.py --videos pasta/ --nome meu-estilo --out estilos/ --fps 2
```

## O que a máquina faz, e o que ela não faz

Ela **mede**: onde o preto assenta, onde o branco é segurado, saturação, contraste,
vinheta, grão dentro do preto, cor na borda, densidade de linha, temperatura e paleta.
Depois agrupa os frames por semelhança de **estilo** — cor, textura e distribuição de luz,
não assunto — e monta uma folha de contato por grupo.

Ela **não** diz o que aquilo significa. Tipografia, movimento de câmera, ritmo de corte,
o que cada grupo é e quando usar: isso é leitura, e leitura se faz olhando. O arquivo
`medicoes.json` traz um campo `confianca` separando as três coisas:

- `medido_direto` — número confiável, pode fixar
- `aproximado` — o número existe mas confunde causas (a "cor na borda" não separa
  aberração cromática de luz de contorno colorida)
- `so_olhando` — não tem número, tem que abrir a folha de contato

## A etapa que não dá para pular

Abra as folhas em `estilos/<nome>/folhas/` e **olhe**. Para cada grupo, escreva no
`medicoes.json`:

- `leitura` — o que aquilo é, em duas ou três frases. O que se repete, como a luz chega,
  o que nunca aparece.
- `quando_usar` — em que momento da fala aquele grupo entra.

Ou despache o agente **analista-de-estilo**, que faz isso abrindo as folhas.

## Do estilo medido ao vídeo

```bash
python3 .../scripts/plano.py --falas falas.srt --out motion/ --estilo estilos/meu/medicoes.json
```

A grade aprendida entra no `plano.json` como campo `grade` e sobrescreve o preset campo a
campo dentro do template. O que não foi medido cai no preset `noturno`.

## Quanto material é preciso

Cem frames já dão medida estável. Abaixo de trinta, os agrupamentos ficam instáveis e o
`preset_sugerido` vira chute. Frames quase idênticos são descartados automaticamente —
uma pasta de 700 frames de vídeo costuma render 600 distintos.

## Calibração — de onde vem a conversão

Duas conversões não são medida direta, são calibração contra o único corpus em que
existem os dois lados:

- **grão**: o canal de referência mede `grao_no_preto` 0,9 e usa opacidade 0,4 no
  template. Daí o fator 0,45.
- **aberração**: mede `cor_na_borda` 22,6 e usa 2–5 px. Por isso o campo se chama
  `aberracao_a_confirmar` — confirme na folha antes de fixar.

Rodando o aprendizado sobre o próprio corpus de referência, ele devolve fundo `#090909`,
grão 0,41 e vinheta 0,79 — contra `#0C0C0C`, 0,4 e 0,8 medidos à mão. É o teste de
sanidade da ferramenta, e vale repetir sempre que mexer nas fórmulas.

## Direitos

Frames de referência servem para **medir e estudar**. Medida não é obra: luminância,
paleta e vinheta são fato sobre a imagem, e reproduzir uma grade não reproduz o conteúdo
de ninguém. Mas os frames em si continuam sendo material de terceiro — não os publique,
não os use como asset no seu vídeo, e não copie composição ou personagem específicos.
Aprender a gramática é legítimo; copiar a frase, não.
