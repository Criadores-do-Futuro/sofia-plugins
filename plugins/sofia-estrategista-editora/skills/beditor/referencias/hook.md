# Hook — escrever as palavras

`galeria-estilos.md` diz **como o hook é desenhado** (fonte, corpo, sombra, entrada).
Este arquivo diz **o que ele fala** — e é a parte que faltava: até 2026-09-13 o plugin
tinha o desenho medido e três linhas de critério de escrita em `retencao.md`, nada mais.

Base: estudo de uma aula pública sobre psicologia de hooks, reescrito com palavras e
exemplos próprios (a referência fica na procedência privada). O que lá dependia de
ferramenta paga está reescrito para o que esta máquina tem:
`yt-dlp` e o índice local.

---

## Por que o hook funciona

O feed é uma estrada. O polegar está em movimento e o olho vidrado. O hook existe para
forçar **um ponto de congelamento** — um segundo de parada — e isso não é retórica, é a
**resposta de orientação**: a reação involuntária do cérebro a um estímulo novo. O
"peraí, o que foi isso?" de quem vê um lobo atravessando o quintal.

E ela é previsível. O hook só precisa fazer o cérebro do espectador responder **duas
perguntas**:

1. **Do que é este vídeo?** → o assunto
2. **O que eu ganho se continuar?** → o resultado

Assunto e resultado. Um hook que responde os dois com clareza já prende. Um hook que
deixa qualquer um dos dois no ar, não.

## Os quatro S

Os ingredientes que fazem aquelas duas perguntas aparecerem. **Faltando um, o hook não
prende:**

| | |
| --- | --- |
| **Sujeito** | Pessoa, objeto, missão, lugar — o espectador tem de saber **na hora** de quem ou do que se trata. |
| **Stakes** (o que está em jogo) | O motivo para se importar. Em conteúdo educativo é o **resultado que ele quer**: mais views, mais tempo, mais clientes, menos trabalho. Sem motivo para se importar, não há congelamento. |
| **Speed** (compressão) | O sujeito e o que está em jogo no **menor número de palavras**. Não é falar rápido — fala apressada que o cérebro não absorve é hook não absorvido, que vale o mesmo que hook nenhum. É **compressão**, não velocidade. Oito palavras se seguram; vinte e oito, não. |
| **Super claro** | Uma única interpretação possível. Palavra simples, sem trocadilho, sem montagem esperta. **Se o espectador precisar pensar meio segundo no que você quis dizer, o polegar desce.** Confusão temporária não vale o tempo dele num mar de estímulo. |

---

## Os três hooks, e a trava que os liga

Já está em `retencao.md` como "gancho triplo". A aula acrescenta o **teste**, que é o que
faltava para virar trava:

> **Vendo só o visual, eu deveria conseguir adivinhar mais ou menos o que o texto diz.
> E vice-versa.** O mesmo entre o falado e os outros dois.

Os três componentes podem ser individualmente ótimos e ainda assim afundar o vídeo se não
apontarem para o mesmo lugar. É, segundo a fonte, o erro que aparece em **todo** cliente
dela: trabalha-se o hook falado e não se alinha os três.

Existe um quarto, que não desenhamos aqui mas que o `publicacao.py` escreve: **a primeira
linha da legenda do post**, acima da dobra. Ela influencia de forma subliminar quem fica.

---

# 1. Hook escrito — o texto na tela

**É o mais importante dos três**, e é contraintuitivo: o olho **caça texto** e identifica
palavra-chave mais rápido do que compreende a imagem. Não é a legenda palavra a palavra —
é o bloco de título, com tipografia própria.

## A substância

Uma fórmula, e ela é curta:

> **repetidor de assunto** + **um** destes três:
> **lembrete de dor** · **isca de resultado desejado** · **mudança de estado do mundo**

| Peça | O que é | Exemplo |
| --- | --- | --- |
| **Repetidor de assunto** | o nome próprio, o termo técnico, o jargão exato da coisa. Nome e termo são ímã de atenção, ainda mais em caixa alta. | `GEMINI OMNI` · `FORMATO ANÁLISE` |
| **Lembrete de dor** | lembra a dor que o vídeo vai resolver | `…sem errar o hook` |
| **Isca de resultado** | promete o resultado | `…que não dá pra pular` |
| **Mudança de estado** | algo aconteceu no campo que muda o futuro | `…acabou de mudar a edição de vídeo` |

A curiosidade que isso gera não é truque: é **lacuna de conhecimento**. O que ele sabe
hoje, o resultado que quer amanhã, e a distância entre os dois.

## As seis regras duras

1. **Especificidade.** `22 dias` ganha de `algumas semanas`. `R$ 2.700` ganha de `alguns
   milhares`. `Ganhei R$ 97 mil em 13 dias` ganha de `ganhei uns milhares em umas semanas`.
2. **Palavras de força.** Feixes de uma a três palavras que funcionam como míssil
   teleguiado de atenção — `míssil teleguiado` é uma delas. Dizer "é muito bom para
   atenção" tem o mesmo sentido e nenhum efeito. A palavra de força **comprime uma frase
   inteira em duas palavras sem perder a carga.**
3. **Duas linhas, teto.** Com fonte de sistema, duas é limite absoluto. **Três linhas só
   com tipografia trabalhada e uma linha claramente dominante** — três linhas com o mesmo
   corpo ninguém lê.
4. **A quebra de linha cai onde a frase respira.** `O GEMINI ACABOU DE MUDAR / A EDIÇÃO DE
   VÍDEO` — porque "a edição de vídeo" se lê junto. Nunca `…MUDAR A EDIÇÃO / DE VÍDEO`.
5. **Sem pontuação**, exceto aspas e parênteses. (Já era regra em `retencao.md`.)
6. **Sem conectivo**: `e`, `ou`, `que`, `mas`, `portanto`. Não é frase — é palavra-gatilho.

## O tempo em tela

**Cerca de 3 segundos, e não menos.** O percurso do olho é medido: entra no vídeo, olha
nos olhos de quem fala, sobe para o texto, pega duas ou três palavras de força, desce para
entender a imagem, sobe de novo, e **só então** decide se fica. Cortar antes de 3 s tira o
efeito inteiro — o texto esteve lá e não foi lido.

## A posição

Terço superior, ou perto do meio, dependendo de como o quadro foi composto. Onde o olho
chega mais rápido **sem tapar nada**: se o rosto ocupa o quadro, o hook vai acima da
cabeça. **Nunca sobre os olhos nem sobre a boca.**

No `dinamismo` isto virou regra de código (pedidos do dono em 2026-09-27): o bloco
começa em 9% da altura (abaixo dos ~160 px que TikTok e Reels cobrem) e **termina
no máximo em 1/3** — se não couber, todas as linhas encolhem na mesma proporção,
para a diferença apoio:destaque sobreviver. E três exigências que o dono fez com
todas as letras e que o portão confere quadro a quadro:

- **Acentuação correta.** "Você", "vídeo", "é", "não", "número": o hook é texto
  escrito, não transcrição. Letra sem acento no hook é erro de digitação na tela.
- **Nenhuma letra cortada** — nem na borda, nem no acento de maiúscula (Ê, Ã, Ç),
  que é o que a entrelinha apertada come primeiro.
- **Estilo `impacto`** quando o dono mandar referência de apoio pequeno e
  destaque grande: Montserrat 800 caixa alta, apoio creme `#F7F5F0`, destaque
  âmbar `#FFB629` a 1,55× o corpo. A proporção e a paleta vieram da referência;
  a composição é nossa.

## Onde o bEditor já está certo

Vale registrar, porque três decisões nossas anteriores batem com a fonte e não precisam
mudar:

- `hook: { linhas: [...], destaque: n, ateMs: 3800 }` — **três linhas com uma em
  destaque** é exatamente o caso "tipografia trabalhada com uma linha dominante" da regra 3.
- `ateMs: 3800` está acima do piso de 3 s.
- Hook no terço superior e legenda logo abaixo da boca (`formatos.md`) separa os dois
  campos como a fonte manda.
- "Sem pontuação além de aspas ou parênteses" já estava em `retencao.md`.

---

# 2. Hook falado — o que sai da boca

Duas camadas: **o formato** e **as palavras de força**.

**Formato** é a estrutura gramatical da frase. Existe cerca de uma dúzia que rende em
vertical: pergunta, tutorial, problema-solução, revelação de segredo, comparação,
contagem. Achar qual funciona e remixar é o **nível 1** — todo mundo fala disso.

**Nível 2 são as palavras de força.** O exercício:

1. Junte os hooks falados dos vídeos que performaram — os seus e os dos vizinhos de nicho.
2. Leia de cima para baixo procurando **feixes de duas ou três palavras com carga**.
3. Quando o mesmo feixe aparece em dois dos seus melhores, você tem validação dupla.
4. **Não repita o feixe — torça.** `cientificamente impossível de pular` vira
   `neuroquimicamente impossível de pular`, `psicologicamente impossível de ignorar`.
   Mesma psicologia, palavras deslocadas.
5. Combine formato torcido com palavra de força torcida. **Isso é escrever hook novo com
   lastro de dado**, em vez de copiar e colar, que é o que todo mundo faz e não funciona
   duas vezes.

**Como montar esse corpus aqui.** A aula usa uma ferramenta paga. Nós já temos as peças:
`yt-dlp --flat-playlist` lista os posts de um perfil com curtidas; as legendas automáticas
dão o hook falado dos primeiros segundos sem baixar vídeo; `ctx_index` guarda e
`ctx_search` consulta. É a mesma pipeline que o `analise.py` vai precisar — vale construir
uma vez e servir aos dois.

---

# 3. Hook visual — e por que ele é o menos importante

A própria fonte diz: dá para ganhar grande só com texto e fala bem afiados. A prova são os
*yappers* — gente sentada no quarto falando, sem nada acontecendo, que funciona porque os
outros dois hooks estão no ponto.

As cinco categorias:

| | |
| --- | --- |
| **Gráfico ou texto sobreposto** | pôr grafismo por cima da base que já existe |
| **Quebra de padrão / troca visual** | trocar de você para outra coisa — efeito de choque |
| **Movimento do sujeito** | você entra ou sai do quadro |
| **Efeito ou transição** | efeito por cima da footage |
| **Seleção visual** | escolher uma imagem que congela por si |

**O 80/20, e é o que se recomenda começar fazendo:** mexa o corpo no quadro, mexa a
imagem no quadro, ou mexa o texto sobre a imagem. Só isso.

**O aviso, que importa mais que a lista:** hook visual sai cafona quando quem faz ainda
não pegou o jeito. Não exagere. Um movimento pequeno — inclinar para a frente, um gesto,
prender o cabelo — já dá o solavanco. Concentre o esforço no texto e na fala e acrescente
**um** movimento pequeno.

---

# 4. A zona de travamento — os 5 a 10 s depois do hook

A parte que quase ninguém escreve, e que a fonte argumenta ser **mais importante que o
hook**. O hook só interrompe a rolagem e compra uma chance. **A zona de travamento — as
duas a quatro frases seguintes — é onde a atenção é ganha de verdade.** Se o hook é a
entrada, é isto que faz ficar para a refeição inteira.

Psicologicamente só acontecem duas coisas ali, e as duas sempre:

**1. Confirmar a alegação do hook.** O mesmo que confirmar título e capa na abertura de um
vídeo longo. Serve para garantir que não houve isca e troca — você não prendeu num assunto
para falar de outro.

**2. Avaliação rápida de confiança.** E aqui está a ideia mais contrária ao senso comum da
aula inteira: **no estado atual da internet, uma alegação forte no hook não basta.** O
espectador também precisa acreditar que **você** não vai desperdiçar o tempo dele. As duas
a quatro frases depois do hook são um teste de admissão.

Quatro alavancas, em ordem crescente de importância:

| Alavanca | O que é |
| --- | --- |
| **Aparência** | quanto a pessoa em quadro atrai o olho. A fonte é direta a respeito; o que dá para transformar em regra útil é: cuidado com a imagem soma, e desleixo desconta. |
| **Embalagem** | qualidade do enquadramento, do set, da luz, do **áudio**, do acabamento. Não é set caro: é polimento. Cuidado visível vira confiança, porque cuidado é sinal de que você se importa. |
| **Semelhança** | quanto o mensageiro parece com o espectador, ou com o personagem que ele esperava para aquele assunto. Quem fala de IA para a geração Z tem de parecer daquela geração; quem fala de contabilidade ganha parecendo contador. |
| **Prova — a âncora de confiança** | **a mais importante de todas.** Prova concreta, ali, nos primeiros dez segundos: um número, um estudo, um caso, uma captura de tela, uma referência de terceiro. |

> **Isto explica, de fora para dentro, por que o formato `analise` funciona.** A credencial
> que ele põe entre 9 e 19 s — *"a Gabi Jacinto tem 4 milhões de seguidores e uma média de
> 2 milhões de views"* — é exatamente a âncora de confiança caindo exatamente na zona de
> travamento. E o cartão de prova com a interface intacta (`formato-analise.md`) é a
> captura de tela que a fonte pede. Duas análises independentes chegando à mesma peça é o
> melhor sinal de que a peça é real.

**Consequência para o guia:** o `M01` não termina no hook. O diretor escreve o hook **e a
primeira frase depois dele**, e essa frase confirma a alegação e planta a prova. Um guia
que gasta o hook e entrega a zona de travamento ao acaso desperdiça o hook.

---

# 5. O procedimento: três opções, sempre

Pedido do dono em 2026-09-13: *"fazer o melhor hook possível, ou oferecer 3 ótimas
opções"*. Três opções, e não uma, porque a escolha depende de quem ele quer alcançar
naquele post — e isso não está no take.

**As três não são três redações da mesma ideia.** Se as três dizem a mesma coisa com
palavras diferentes, não há escolha nenhuma a fazer. Cada uma usa **um mecanismo de
substância diferente** da fórmula do hook escrito:

| Opção | Mecanismo | Serve quando |
| --- | --- | --- |
| **A** | repetidor de assunto + **lembrete de dor** | o público já sente o problema e não sabe que tem solução |
| **B** | repetidor de assunto + **isca de resultado** | o público quer o resultado e está comparando caminhos |
| **C** | repetidor de assunto + **mudança de estado** | há novidade real no campo — ferramenta, mudança de plataforma, número novo |

Cada opção chega completa, com os três hooks alinhados e a primeira frase da zona de
travamento:

```json
"hookOpcoes": [
  {
    "id": "A",
    "mecanismo": "dor",
    "linhas": ["EDITAR UM VÍDEO", "DE 1 MINUTO", "CUSTA 5 HORAS"],
    "destaque": 2,
    "ateMs": 3800,
    "falado": "Editar um vídeo de um minuto custa cinco horas, e não é porque você é lento.",
    "visual": "ele levanta a mão aberta na palavra CINCO — movimento do sujeito",
    "travamento": "Eu cronometrei os meus últimos onze vídeos: a média foi 4h52.",
    "prova": "a planilha dos onze vídeos",
    "porque": "a dor é a queixa mais repetida nos comentários do canal"
  }
]
```

Campos e o que cada um cobra:

| Campo | Trava |
| --- | --- |
| `linhas` | máximo 3, uma dominante via `destaque`; sem pontuação; sem conectivo; quebra onde a frase respira |
| `ateMs` | **≥ 3000** |
| `falado` | sujeito e resultado sem saudação e sem "hoje eu vou falar sobre" |
| `visual` | um movimento, dos três do 80/20 — e tem de deixar adivinhar o texto |
| `travamento` | a frase que confirma a alegação, com a prova dentro |
| `prova` | a âncora de confiança. **Sem ela a opção não é apresentada** |
| `porque` | por que esta opção, para este público, neste post |

**A recusa.** Se as três opções não conseguirem carregar uma prova concreta, o problema
não é o hook — é o roteiro, e é ele que precisa mudar antes da edição. Diga isso em vez de
entregar três promessas sem lastro.

---

# 6. Portão do hook

Antes de compor, os oito:

1. O hook responde **do que é** e **o que eu ganho**?
2. Os quatro S estão todos lá — sujeito, o que está em jogo, compressão, uma interpretação só?
3. **Teste do alinhamento:** tapando o texto, o visual deixa adivinhar o que está escrito?
4. Máximo 3 linhas, com uma dominante? Sem pontuação? Sem conectivo?
5. A quebra de linha cai onde a frase se lê junto?
6. Fica **3 segundos ou mais** na tela, no terço superior, sem tapar olhos nem boca?
7. Tem pelo menos uma palavra de força — e ela é torcida, não copiada de outro criador?
8. **A primeira frase depois do hook confirma a alegação e planta a prova?**

E o teste de campo, que vale por todos: **leia o hook em voz alta para alguém que não viu
o vídeo.** Se a pessoa perguntar "como assim?", ele falhou no quarto S, e nenhum ajuste de
tipografia conserta.
