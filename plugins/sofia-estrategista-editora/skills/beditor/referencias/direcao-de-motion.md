# Direção de motion — o estilo do vídeo e o prompt de cada cena

Pedido do dono, em 2026-09-11: todo formato com motion graphics, antes de gerar,
**descreve o estilo do vídeo inteiro** e **escreve um prompt para cada cena**.
Vale para qualquer guia com um momento `motion` ou `aroll+motion`. O `dinamismo`,
que não tem motion, não leva nada disso.

O diretor escreve os campos no `guia.json`, o `validar.py` recusa o guia sem
eles, e o `montar.py` monta o prompt de cada cena no `GUIA.md`, no
`edicao/motion/CENAS.md` e no `plano.json` (`cenaPrompt`), que é o que quem
desenha lê.

## O estilo do vídeo: `direcaoMotion`, oito itens

Escrito uma vez, no cabeçalho do guia, e seguido em todas as cenas. Cada item
parte do `estilo` declarado (`estilos.md`), do `branding.md` e da referência de
estilo, quando houver (`aprender-estilo.md`). O objetivo não é inventar um estilo
por vídeo.

| chave | o que responde |
| --- | --- |
| `estiloAnimacao` | 2D, 3D, tipografia cinética, flat design, colagem |
| `movimento` | velocidade, easing, bounce; seco ou suave (curvas em `movimento.md`) |
| `transicoes` | cortes, wipes, morphs, zooms, e quando cada um entra |
| `paleta` | cores em hex e o fundo |
| `tipografia` | família, peso, caixa, e onde o texto fica no quadro |
| `camera` | parada, zoom, pan, shake; o que é padrão e o que é exceção |
| `climaRitmo` | clima e ritmo do vídeo, e onde ele acelera |
| `som` | whooshes, graves, risers e estilo da música |

## O prompt de cada cena: `motion.cena`, cinco itens

Uma cena é um momento `motion` ou `aroll+motion`. O texto de cada item é
específico da cena. Uma frase como "segue o estilo" não é prompt.

| chave | o que responde |
| --- | --- |
| `naTela` | o que aparece e como anima: o que entra, o que acontece, o que sai |
| `texto` | o texto exato na tela, **no máximo 6 palavras**; `""` quando a cena não tem texto |
| `visual` | cores, fundo e tipografia desta cena, dentro da paleta do vídeo |
| `cameraTransicao` | o movimento de câmera e a transição para a cena seguinte |
| `som` | os efeitos sonoros da cena e o clima da música por baixo |

O `texto` segue as regras de sempre: mostra o que a fala **não** diz e nunca
escreve limpa a palavra que a fala nega (`riscar`). Número só entra com fonte
(`procedencia.md`). Mais de 6 palavras significa que a cena está narrando por
escrito: o resto fica na fala.

A `cameraTransicao` de uma cena combina com a `entrada` da seguinte, porque a
saída de uma é a entrada da outra. O `som` segue `motion-editorial.md`: efeito
sonoro na palavra-chave, na ação ou na troca de classe, nunca em toda entrada.

## O prompt montado

O `direcao.prompt_da_cena` junta, num parágrafo só:

1. o id, a duração e o estilo de animação;
2. o que aparece na tela e como anima;
3. o texto exato entre «» (ou "sem texto na tela");
4. o visual da cena e o movimento do vídeo;
5. a câmera e a transição, com o nome da cena seguinte;
6. o som.

Assim o prompt nunca sai sem um dos itens, e ajustar uma cena é mexer em um
campo do guia, não reescrever o parágrafo.

## Exemplo

```json
"direcaoMotion": {
  "estiloAnimacao": "2D, tipografia cinética sobre fundo escuro",
  "movimento": "seco: entradas de 0,5 s em power4.out, sem bounce",
  "transicoes": "corte seco; varrida horizontal quando a lista se esvazia",
  "paleta": "fundo #160B10, texto creme #FFF6E7, destaque âmbar #F3B35C",
  "tipografia": "Fraunces display no terço de cima, nunca sobre o rosto",
  "camera": "parada; push-in de 4% só na palavra que acende",
  "climaRitmo": "tenso e contido, um acento por cena",
  "som": "whoosh curto na entrada, grave seco na virada, cama eletrônica baixa"
},
"motion": { "tipo": "palavras", "...": "...",
  "cena": {
    "naTela": "'segunda' sobe por baixo e 'longa' entra escalando, empurrando a primeira",
    "texto": "segunda longa",
    "visual": "fundo #160B10, palavras creme, 'longa' em âmbar, Fraunces display",
    "cameraTransicao": "parada; varre para fora na horizontal no fim",
    "som": "whoosh na entrada de 'longa', cama tensa mantida"
  }
}
```
