# Sincronia — a lei que não se negocia

Esta página existe porque eu quebrei a sincronia dos três vídeos de um dia
inteiro de trabalho, entreguei os três como prontos, e o editor achou o erro
que dois scripts meus não acharam. O que está escrito aqui é o que eu deveria
saber antes.

## A lei

**A boca em quadro manda no áudio.** Enquanto o rosto de quem fala está na
imagem, a voz sai exatamente com ela — não 200 ms antes, não 40 ms depois.
Qualquer efeito de montagem que mexa no tempo da voz só é legítimo onde a boca
**não** está em quadro.

Não há tolerância a negociar. Um desencontro de 300 ms é visível para qualquer
pessoa, e o espectador não diz "está fora de sincronia": ele diz que o vídeo
está estranho e vai embora.

## Como o áudio se ancora quando a imagem é aparada

Ao aparar um clipe, o áudio dele não "flutua" — ele fica preso ao lado que
**não** foi mexido:

| O que foi aparado | Onde o áudio se ancora |
|---|---|
| Início do vídeo | O **fim** do áudio continua junto do fim do vídeo |
| Fim do vídeo | O **início** do áudio continua junto do início do vídeo |
| Os dois lados | Cada ponta segue a sua; o miolo é que encurta |

Dito de outro jeito: aparar a cabeça de um clipe joga fora o começo do áudio
junto; aparar a cauda joga fora o fim do áudio junto. O que sobra continua
casado quadro a quadro. Se, depois de aparar, foi preciso *deslocar* o áudio
para ele "caber", a conta está errada — e o erro vai aparecer como dublagem.

## J-cut é sobreposição, não deslocamento

Este é o ponto exato onde eu errei.

O J-cut correto: a voz do clipe que **entra** se estende para trás e toca por
cima da **cauda da imagem** de quem sai. O corpo dessa voz continua ancorado na
imagem dele. É uma sobreposição — dois sons no mesmo instante, um terminando e
outro começando.

O que eu fiz: montei a voz como uma única pista concatenada e dei a cada
segmento a duração `dur_k + N_k − N_(k+1)`. Isso não estende nada; **desloca o
segmento inteiro** `N_k` ms para trás. A voz do trecho inteiro passou a correr
à frente da boca, do primeiro ao último quadro dele.

**Consequência prática:** uma pista concatenada é incapaz de fazer **corte J**.
Dois sons ao mesmo tempo exigem duas pistas mixadas (`adelay` + `amix`, cada
clipe com o seu áudio ancorado na sua própria imagem, e só a cabeça estendida).
Se a implementação não tem mixagem, ela não tem corte J — tem erro de sincronia.

> **Mas tem o corte L, e ele não precisa de mixagem nenhuma.** No corte L quem
> se adianta é a IMAGEM, não o som: a pista de voz continua sendo uma só,
> intocada, e o que muda é de qual trecho do bruto os quadros daquela janela
> saem. Zero pistas novas, zero deslocamento de áudio, deriva exatamente zero.
>
> Em cabeça falante o L é, além disso, o único dos dois que nunca erra — a
> imagem que entra cedo é de boca fechada, enquanto o J poria voz sobre uma boca
> parada. Ver `formato-analise.md`, «O split edit — a emenda que o silêncio
> paga». A condição é medível: a folga removida tem de ser silêncio **e** a cauda
> do pedaço que sai tem de estar calada. Esqueci a segunda e a medição acusou.

## Onde o J-cut pode existir

Só onde a **cauda de quem sai** não mostra a boca de quem fala:

- a saída está coberta por motion, gráfico ou cartela;
- a saída é B-roll, tela, ou outro ângulo sem o rosto;
- a saída é um plano de escuta, sem fala.

Em vídeo de rosto na câmera do começo ao fim — o formato `dinamismo` inteiro —
**nenhuma** dessas condições acontece. Lá o J-cut não é uma escolha estética
que se possa fazer com cuidado; ele é impossível. `montar.py` verifica isso em
`_boca_em_quadro()` e zera o J-cut sozinho.

## O L-cut é o mesmo problema, do outro lado

No L-cut, a voz de quem **sai** continua tocando por cima da imagem que
**entra**. A regra é espelhada: só vale se a imagem que entra não mostra a boca
de quem fala dizendo outra coisa. Serve quando o que entra é motion, B-roll,
tela ou plano de escuta. Se o que entra é o mesmo rosto em outra frase, o L-cut
vira dublagem.

## "Só 2 a 4 quadros" também é dessincronia

A linha do Codex (`split-screen.md`) mandava antecipar o áudio 2 a 4 quadros
"quando houver cobertura segura". A 30 fps, isso dá 67 a 133 ms de voz antes da
boca. O espectador percebe voz adiantada a partir de 45 ms (ITU-R BT.1359).
Não existe J-cut "pequeno o bastante" sobre o rosto: o tamanho seguro é zero.
Na tela dividida (`tela-dividida.md`), quem fala está sempre em quadro, e
portanto nunca há cobertura para a voz dele.

## Corte de áudio se faz em PCM, por amostra — nunca em codec com quadro

A causa de deriva mais fácil de não ver, porque o código parece certo:

```python
# ERRADO — cada pedaço vira AAC e os 30 são concatenados
for t in tabela:
    ffmpeg(-ss t.brutoDe, -t dur, "-c:a", "aac", f"a{i}.m4a")
ffmpeg("-f", "concat", "-c", "copy", "voz.m4a")
```

AAC codifica em quadros de **1024 amostras** (≈21 ms a 48 kHz) e carrega atraso
de codificador. Um pedaço de duração arbitrária é arredondado para cima até
fechar o quadro, e o excedente entra como padding. Um pedaço só: erro
imperceptível. **Trinta pedaços: o erro soma**, e a voz vai se afastando da
imagem ao longo do vídeo.

O sintoma é característico e denuncia a causa: **o desencontro cresce com o
tempo**. No projeto 14 a medição do split edit acusou fala onde devia haver
silêncio em 17 emendas, e todas as flagradas estavam na segunda metade. Não era
o split edit: era a pista de voz escorregando por baixo dele.

```python
# CERTO — decodifica uma vez, fatia por índice de AMOSTRA, codifica uma vez
bruto = decodifica_tudo(take, SR)              # f32, (n, 2)
voz = np.concatenate([bruto[int(t.brutoDe/1000*SR):int(t.brutoAte/1000*SR)]
                      for t in tabela])
codifica(voz)                                  # uma única vez, no fim
```

Duas regras que saem daí:

> **Todo corte de áudio acontece em PCM. A codificação acontece uma vez, no fim.**

> **A mistura também.** Misturar a trilha contra a voz já codificada obriga a
> decodificar e recodificar a voz, e reabre pela porta dos fundos o problema que
> o corte por amostra acabou de fechar. Some os arrays, codifique o resultado.

O teste é de uma linha e tem de dar zero exato, não "quase":
`len(voz) − int(duracao_do_corte * SR)`.

## O teste que me enganou, e o que testar no lugar

Eu conferi que a soma das durações dos segmentos de voz batia com a duração do
vídeo: 125163 ms contra 125163 ms. Bateu. E eu chamei isso de "deriva zero".

**Soma igual não prova sincronia.** Prova só que não há deriva acumulada *no
fim*. Um áudio inteiro adiantado 300 ms tem exatamente a mesma soma de um áudio
em sincronia. O teste media a coisa errada com precisão perfeita.

O que testar de verdade, na ordem:

1. **Contra o bruto, não contra si mesmo.** Para cada trecho mantido, o
   deslocamento entre a posição da voz na montagem e a posição dela no take tem
   de ser o mesmo do vídeo. Se os dois números divergem em qualquer trecho, há
   desencontro — e o script já sabe disso antes de renderizar.
2. **Olhar uma consoante plosiva.** Extraia os quadros de um "p", "b" ou "t" e
   veja se os lábios fecham no quadro em que o som acontece. É o teste barato
   que pega o que a matemática deixou passar.
3. **No meio e no fim, não só no começo.** O desencontro do 05 começava aos
   45,8 s: quem conferisse só a abertura assinaria embaixo.

## Palavra inteira também é sincronia

Imagem e áudio podem estar matematicamente casados e a emenda ainda destruir a fala.
Os timestamps do ASR delimitam a palavra de forma aproximada; eles não incluem com
confiabilidade a inspiração, o ataque consonantal e a soltura do último fonema.

Por isso, uma remoção automática precisa deixar 600 ms de proteção acústica depois da
palavra mantida à esquerda e antes da palavra mantida à direita. Se o trecho que se
quer remover encosta em fala dos dois lados — caso típico de falsa partida — ele não é
um silêncio e deve permanecer até existir uma edição fonética ou aprovação humana.

Depois do corte, extraia a emenda com contexto, ouça em 1× e 0,75× e transcreva de
novo. Preservar a ordem das palavras no JSON não prova que a pronúncia sobreviveu. Se
a retranscrição perder sílabas ou trocar a palavra, restaure a pausa inteira; não tente
adivinhar outra borda até a palavra “parecer” aceitável.

## O que os vídeos 19 e 20 ensinaram (2026-09-27)

Quatro desvios, cada um achado só porque alguém mediu o arquivo certo.

**1. A imagem também escorrega — pela grade de quadros.** A voz saiu perfeita
(0,8 ms), e mesmo assim o master do 20 tinha a imagem até 5 quadros atrás. As
faixas de zoom caem nos picos de ênfase, que ficam entre quadros (20,88 s é o
quadro 626,4), e cada pedaço cortado com `-ss/-to` arredonda a própria contagem
de quadros. Arredondamento pequeno × dezenas de pedaços = deriva. Regra: **toda
fronteira de pedaço de imagem é quantizada na grade de 30 fps antes de cortar**
(`montador._na_grade`), cada faixa começa exatamente onde a anterior terminou, e
o pedaço sai por contagem (`-frames:v`), nunca por tempo. A mesma lei do áudio
em PCM, aplicada à imagem: fatia-se por índice, não por relógio.

**2. O teste de imagem tem de rodar no master, e não por pixel.** A prévia
aprovada estava certa; o master não. Comparar pixel do master com a montagem
crua não funciona (grade e zoom achatam a correlação — deu "3 quadros" num
master certo). O teste que decide é `scripts/conferir_movimento.py`: energia de
movimento, invariante a cor e escala, janelas de 10 s, 0 quadro em todas as
válidas. O `montar.py --etapa final` já roda e reprova sozinho.

**3. Tempo negativo no bruto é silêncio.** O take do 20 tinha trilhas com
carimbo antes do zero. Um `brutoDe` negativo virava índice negativo de amostra,
e o NumPy fatiava do fim — a abertura da prévia saiu muda (−91 dB) e o dono
perguntou se o erro era dele. Regra: **`brutoDe` é travado em ≥ 0** antes de
fatiar, e o primeiro teste de uma prévia é o volume dos 5 primeiros segundos.

**4. A cadeia de voz atrasa.** O tratamento de voz (13 filtros; o `afftdn`
sozinho, 25 ms) empurra a voz ~30 ms para trás. Abaixo do limiar de 45 ms, mas
soma com qualquer outro erro. O `acabamento.tratar_voz()` mede a latência da
própria cadeia e a compensa; não remova isso para "simplificar".

**5. Juntar takes é a primeira emenda — e `concat -c copy` erra nela.** No 21
(2026-09-28), três takes do iPhone juntados com `ffmpeg -f concat -c copy`: o
take 2 tinha o áudio começando 14 ms depois da imagem, o take 1 tinha áudio
11 ms mais curto que a imagem, e o arquivo junto saiu com a imagem começando em
42 ms. O concat empilha cada pista pelo próprio relógio, então cada emenda
desloca a voz do take seguinte. Regra: **a imagem se junta por cópia; a voz se
junta em PCM, take a take, com o início deslocado pelo `start_time` do áudio
contra o do vídeo e o comprimento cravado em `quadros × 1600` amostras** (30 fps,
48 kHz), e só então as duas se juntam num `.mov`. Confira: amostras = quadros ×
1600, exato. Isso é o `scripts/juntar_takes.py <brutos> IMG_a.sdr.mov IMG_b.sdr.mov …`
(escreve `lista.txt` e `take.sdr.mov` e imprime o fim de cada take em ms, que
vira as fronteiras de `estrutura`/`momentos` no guia). Nunca junte takes à mão.

## O que isto muda no portão de qualidade

`portoes-de-qualidade.md`, eixo 2, tem a linha "sem descasamento labial
introduzido pela montagem". Ela estava lá o tempo todo. O que faltou foi um
teste que pudesse reprová-la — e a disciplina de não aceitar um número
conveniente como prova de uma coisa que ele não mede.
