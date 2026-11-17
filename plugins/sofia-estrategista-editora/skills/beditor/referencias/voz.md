# Voz: gravar bem e tratar sem esconder a palavra

A voz é o que se entende do vídeo. Filtro nenhum devolve energia que não foi
gravada, e música nenhuma pode tampar a consoante. Este arquivo tem as duas
metades: o que se pede **antes** de gravar e o que o bEditor faz **depois**.

## Antes de gravar — o que dizer a quem vai falar

Diga isto no fim do passo 5 do `/sofia-estrategista-editora:dirigir` quando o diretor apontar
energia baixa, fim de frase engolido ou voz variando de volume. Vale para o
**próximo** take: o atual já está gravado.

| Sintoma no take | O que pedir na próxima gravação | Por quê |
| --- | --- | --- |
| voz "sem vida", fala correta mas plana | **50% mais energia do que parece certo** — na hora soa exagerado; no vídeo, soa no ponto | quem fala se ouve também pelos ossos do crânio, que somam grave e volume. A gravação só tem o som pelo ar, então a voz parece mais fina e mais fraca do que parecia na hora, e a pessoa se contém |
| o fim da frase some (volume e clareza caem nas últimas palavras) | **uma frase por vez**: olhar o roteiro, decorar a linha, levantar o olhar, falar, e só então ir para a próxima | a memória compete com o fôlego. Com parágrafo decorado ou teleprompter, a cabeça já está lendo a próxima linha enquanto a boca termina esta, e o ar acaba antes da frase |
| frase longa que não cabe na memória | falar a primeira metade, **congelar as mãos**, olhar a segunda metade, continuar com as mãos de onde pararam | a emenda some no corte, porque o gesto segue contínuo |
| volume e timbre mudando no meio da fala | **corpo parado e no centro**, perto do microfone, na mesma distância o tempo todo | cada palmo a mais de distância muda o grave e o volume, e o compressor não desfaz a mudança de timbre |
| frases terminando "para cima", como pergunta | terminar em **1 a 2 sílabas descendo** | a entonação que desce diz "pensamento fechado"; a que sobe soa insegura |
| palavra tropeçada | parar e **refazer a linha inteira**, sem emendar correndo | fala acelerada para consertar vira fala embolada, e ela é pior que a pausa, que o corte tira |
| desânimo visível | mudar o estado antes de gravar (exercício, banho frio, respiração) | a energia da voz vem do estado de quem fala; não há filtro para isso |

Gravar a voz **separada da câmera** (interface de áudio com pré-amplificador,
direto no computador) dá mais corpo que o microfone da câmera. O bEditor
sincroniza pelo `.whisper.json` do take, então a voz precisa estar no mesmo
relógio que a imagem.

## Depois — o que o bEditor faz com a voz

`acabamento.cadeia_voz()`, nesta ordem:

1. **Corte de rumor** em 85 Hz: mesa, ar-condicionado, trânsito.
2. **Redução de chiado** leve.
3. **Barro** −2,5 dB em 240 Hz: o grave que abafa a consoante, em qualquer voz.
4. **Os cortes desta voz** (`voz.py`): até 4 ressonâncias estreitas, −3 a −4 dB
   e Q 4, onde esta voz, nesta sala, soa fanhosa ou estridente. O jeito de ouvido
   é subir uma banda estreita ao máximo e varrer o espectro, e o script faz a
   mesma varredura medindo o espectro médio da fala contra a tendência de 1
   oitava. Ficam fora da busca o que está abaixo de 250 Hz e a presença de 3,2 kHz.
5. **Presença** +3 dB em 3,2 kHz: é o que faz entender a palavra.
6. **Brilho**: shelf de +2 dB acima de 5,4 kHz. Mais que isso, o "s" chia e o
   ruído aparece.
7. **De-esser**, que segura o "s" que o brilho levantou.
8. **Compressor** (3:1), **limitador** e **−14 LUFS**.

Os cortes são medidos a cada take (~5 s), porque a ressonância que se ouve é a
voz somada à sala, ao microfone e à distância. Em quatro takes da mesma voz, só
um corte (~1,9 kHz) voltou em todos. A última medição fica guardada na marca:

```bash
python3 voz.py mostrar                    # os cortes guardados na marca
python3 voz.py medir take.mov             # só mede
python3 voz.py medir take.mov --fixar     # estúdio que não muda: a marca passa a mandar
python3 voz.py soltar                     # volta a medir cada take
```

## A música abre espaço para a voz

Voz e música disputam **3 a 7 kHz**, a faixa das consoantes. Baixar o volume
da música não resolve, porque o que tampa a palavra é a frequência. O bEditor
faz três coisas:

1. **Volume por LUFS**: a cama fica 18 dB abaixo da voz, medido, nunca chutado.
2. **Low pass de 3 kHz, 24 dB/oitava**, gravado na própria cama (`acabamento.CAMA`),
   para que os três renderizadores recebam a mesma música. Sozinha, ela soa
   "debaixo d'água"; atrás da voz, o embolado some.
3. **Ducking** (`acabamento.mistura_voz_cama`): a cama baixa ~4 a 6 dB enquanto
   há fala e volta nas pausas, com release longo para não "respirar" entre
   palavras. Só existe nas montagens por ffmpeg (`compor.py`, `montador.py`).

Subir o corte do low pass devolve brilho à música e tira clareza da fala. Suba
só no trecho em que a trilha é o assunto e ninguém está falando.
