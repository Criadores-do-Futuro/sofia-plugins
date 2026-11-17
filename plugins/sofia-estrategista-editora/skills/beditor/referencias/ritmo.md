# Ritmo — o que faz prender

Motion bonito com ritmo errado não segura ninguém. Esta é a parte que o gerador de
imagem não resolve e o editor humano acerta por instinto. Aqui está o instinto escrito.

## A unidade é a respiração, não a frase

O corte de **plano** acontece onde a voz respira, não onde a gramática fecha. Na
prática, silêncio ≥ **180 ms** entre palavras é uma junta visual legítima. O
`plano.py` marca todas e escolhe entre elas; você reescolhe se o sentido pedir.

Remover tempo na **decupagem** é outra operação e exige mais espaço: preserve no
mínimo **600 ms depois da palavra anterior** e **600 ms antes da palavra seguinte**.
Depois dessas margens, o buraco efetivamente removido ainda precisa ter pelo menos
300 ms; se não tiver, o ganho de ritmo não paga o risco fonético nem o solavanco.
Timestamp do ASR é uma estimativa da palavra, não autorização para cortar exatamente
na borda.

Falsa partida colada à retomada não tem junta segura. Se “está na minha… está pau a
pau” não contém silêncio suficiente entre as duas tentativas, preserve a falsa partida.
Não sacrifique a última vogal da frase anterior nem o ataque da retomada para deixar o
texto mais limpo.

Cortar no meio de uma oração é normal e frequentemente melhor — a frase continua na
imagem seguinte e o espectador é puxado junto.

## Duração dos planos

```
gancho (0 → 1,5s)     1 plano só, a imagem mais forte que você tem
corpo                 1,6s a 3,2s por plano
batida de impacto     0,4s a 0,8s  (revelação, número, contradição)
respiro               até 4,0s, no máximo 1 por vídeo, e nunca antes dos 15s
```

**Nunca** um plano abaixo de 1,2 s fora de batida de impacto — vira ruído, o olho não
resolve a imagem e a pessoa sai.

**Nunca** a mesma classe visual por mais de 4 s seguidos. Dois planos 3D em sequência
contam como 1 classe: troque para cartela, arquivo, b-roll. A troca de *classe* é o que
o feed lê como movimento, não a animação dentro do plano.

## Os primeiros 1,5 segundos

O gancho não é o texto mais interessante — é a **imagem** mais interessante. Regras:

- Já comece **dentro** da ação. Nada de fade-in, nada de logo, nada de "hoje eu vou".
- O primeiro quadro tem que funcionar **congelado**. Teste: pause em 1,0 s e olhe.
- Se a primeira frase é uma pergunta, a imagem tem que ser a **consequência**, não a
  pergunta ilustrada.
- Movimento de câmera já em curso no frame 1 (push-in começando em 1,04, não em 1,00).

## Densidade

| Duração do vídeo | Planos | Trocas de classe |
| --- | --- | --- |
| 15 s | 7 a 9 | 5 a 6 |
| 30 s | 12 a 16 | 8 a 11 |
| 60 s | 22 a 30 | 15 a 20 |
| 90 s | 30 a 40 | 20 a 26 |

Abaixo da faixa o vídeo arrasta. Acima, cansa — e a retenção cai no meio, não no fim.

## Legenda

**Onde o motion graphics já tem texto na tela, a legenda cala.** Cartela, paper, gráfico,
interface e retrato carregam o próprio texto — sobrepor a legenda falada ali faz o
espectador ler a mesma coisa duas vezes, divide a atenção e não soma nada. O template
faz isso sozinho: cada plano tem `legenda: true|false`, derivado do tipo, e as páginas
que caem sobre um plano mudo simplesmente não são renderizadas.

A legenda existe para os planos que são **só imagem** — objeto, personagem, b-roll,
arquivo, obra, híbrido. Nesses, ela é a única via de texto e precisa estar lá.

- **2 a 4 palavras por página**, trocando no ritmo da fala.
- Caixa baixa. Caixa alta lê como grito e come largura.
- Entrada: escala 0,92 → 1,0 em **0,10 s**. Nada mais longo. Nada de fade de 0,3 s.
- Sem saída animada: a página seguinte substitui a anterior no mesmo frame.
- Palavra ativa destacada só quando a fala é rápida; em fala pausada, destaque cansa.
- A legenda é **queimada** e vive a 46% da altura — não na faixa padrão de baixo.

Ênfase (2,1× o corpo) em **uma palavra por página, no máximo**, e só quando a voz
realmente carrega nela. Ênfase em tudo é ênfase em nada.

## Movimento dentro do plano

Cada plano tem **um** movimento, não dois. Escolha:

```
push-in    1,00 → 1,06 na duração do plano   (padrão, quase todo plano)
pull-out   1,08 → 1,00                       (revelação de contexto)
parallax   camadas a 100% / 70% / 40%        (imagem gerada, 2.5D)
estático   só o grão vive                    (peso, dado, cartela dura)
```

Push-in de 6% em 2 s é imperceptível conscientemente e muda tudo na sensação. Push-in de
20% é enjoativo e denuncia o truque.

## Saída de cutaway

Corte seco é o padrão. Quando precisar de transição, use as três que a identidade aceita:

- **slide** — a placa sai para a esquerda em ~0,43 s, além da largura, limpando o quadro
- **wipe** — folha varrendo, mesma duração
- **push** — a placa escala até 1,34 e sai por cima

**Não** use flash branco nem whip pan: os dois lavam o preto levantado, que é a base da
identidade, e o quadro seguinte volta chapado.

## Áudio manda no corte

Se houver trilha, o corte de classe cai na batida — não no meio dela. Um corte 80 ms
antes da batida lê como erro; 0 ms lê como intenção. Quando não houver trilha, a
respiração da voz é a batida.

## Audição obrigatória da emenda

Toda remoção de tempo precisa de um clipe de auditoria com pelo menos 1 s antes e 1 s
depois da emenda. Ouça em velocidade normal e novamente em 0,75×. Reprove se houver:

- consoante, vogal ou respiração amputada;
- duas palavras coladas com prosódia impossível;
- mudança brusca de ruído ambiente;
- transcrição posterior diferente da sequência preservada no bruto.

O teste automático elimina emendas obviamente perigosas; a audição e a retranscrição
são o portão final. Margens de 250 ms e de 400 ms já falharam em produção: o ASR marcou
o início de “Definitivamente” tarde demais e os cortes devolveram “...amente” e
“E, efetivamente”. A pausa inteira só foi aprovada quando a palavra voltou completa.
