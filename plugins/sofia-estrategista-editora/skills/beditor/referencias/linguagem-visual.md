# Linguagem visual — os números

Tudo aqui foi **medido** em frames reais, por 12 leituras independentes que não viram o
trabalho uma da outra. Quando 12 leituras isoladas convergem no mesmo valor, o valor é
a identidade, não um chute. Trate como especificação, não como sugestão.

## Preset `noturno`

```yaml
canvas: 1080x1920
fps: 30
fundo:            12/255      # preto levantado, nunca 0 puro
sujeito:          200-210/255 # branco osso, nunca estourar em 255
dessaturacao:     -20%
aberracao:        2-5px       # laranja/ciano, cresce em direcao as bordas
grao:             0.4         # constante, visivel inclusive dentro do preto
vinheta:          -0.8        # cantos quase pretos
bloom:            raio grande, threshold 0.85
```

O erro mais comum é o preto ir a zero. Fundo em `#000000` mata o grão, mata a vinheta e
o quadro fica chapado de vídeo digital. **12/255 é `#0C0C0C`.**

O segundo erro é o branco estourar. O corpo/objeto lê como cinza-branco `#CCCAC8`. Se
foi a 255, perdeu o volume e vira recorte.

### Cores de apoio

```
rim quente   #FFB067
rim frio     #7FB4FF
alerta       #C94850
âmbar (2026) #FFA33A
```

Luz **só de trás e de cima**. Nada de frontal — é o que faz a silhueta existir.

### Variante 2026

Os vídeos mais recentes do conjunto de referência abandonaram o render 3D: passaram a
usar **recorte fotográfico com glow âmbar, grade fina de linhas e halftone** sobre o
mesmo preto. Mesmo DNA, execução mais barata e mais rápida. Se o pedido é "parecido com
os últimos", é esta variante — e ela é toda alcançável em CSS/Remotion, sem Blender.

## Preset `editorial`

```yaml
papel:       #D9D8D1
papel_claro: #F4F0E8
tinta:       #373639
carvao:      #29292B
amarelo:     #DBD653
azul:        #2E82F7
vermelho:    #C94850
fita:        #BFBBAE
grao: 0.050  vinheta: 0.06  chroma: 1  saturacao: 0.92   # sobre mesa de papel
grao: 0.028  vinheta: 0.02  chroma: 0  saturacao: 1.00   # sobre video
```

Implementado na skill motion-vox. O bEditor só o reproduz quando o plano mistura os dois.

## Tipografia

| Função | Fonte | Peso | Licença |
| --- | --- | --- | --- |
| legenda falada | Inter | 700 | OFL |
| manchete condensada | Archivo Narrow | 700 | OFL |
| impacto | Archivo Black / Anton | regular | OFL |
| número editorial | Fraunces | 800 | OFL |
| dado técnico, UI | IBM Plex Mono | Medium | OFL |
| etiqueta manual | Permanent Marker | regular | Apache 2.0 |

Todas livres e redistribuíveis. Os arquivos estão em
`skills/motion-vox/fontes/` (dentro do plugin) — o `projeto.sh` copia de lá. Nunca use fonte da
Apple (DIN Condensed, Bradley Hand, Helvetica Neue): prende a identidade a uma máquina.

### Corpo da legenda a 1080 de largura

```
corpo:     80px    (glifo ~57px)
ênfase:    168px   (2,1x o corpo)
tracking:  -0.022em
largura máxima da linha: 86% do quadro
máximo: 2 linhas de 3-4 palavras
```

A legenda recebe **o mesmo glow e a mesma aberração cromática** do resto do quadro. Se
ela estiver limpa e o fundo texturizado, ela parece colada por cima — e parece.

## Áreas seguras — 1080×1920

```
0     ┌──────────────┐
      │  12% morto   │  ← @, seguir, som: nunca ponha texto
230   ├──────────────┤
      │              │
883   │ ...legenda...│  ← 46% da altura: a faixa da legenda
      │              │
1498  ├──────────────┤
      │  22% morto   │  ← descrição, botões, barra de comentário
1920  └──────────────┘
```

Assunto do quadro entre **35% e 80%** da altura. Terço superior vazio para a legenda,
base morrendo em sombra. Rosto centralizado no meio do 9:16 briga com a legenda e perde.

## Cadeia de pós — na ordem

A ordem importa. Trocar duas linhas muda o resultado.

1. **Bloom** — threshold 0.85, raio grande
2. **Aberração cromática** — dispersão 0.008–0.02
3. **Vinheta** — máscara elíptica invertida, blur alto, ×0,45 nos cantos
4. **Grão** — overlay de ruído 0.03–0.06 (AE: Add Grain 0,4–0,7)
5. **Curva** — preto até 12/255, branco segurado em 235
6. **Halftone** (só na variante 2026) — por cima de tudo, opacidade baixa

Grão **depois** da vinheta, senão a vinheta lava o grão dos cantos. Curva **por último**,
senão o bloom estoura o branco que você acabou de segurar.
