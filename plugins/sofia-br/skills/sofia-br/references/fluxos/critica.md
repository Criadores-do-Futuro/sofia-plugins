# Fluxo: crítica e lapidar (grifos)

Quando usar: "critica meu roteiro", "avalia", "isso segura?", "lapidar", "o que melhorar", ou quando a pessoa escolhe uma versão e aceita a crítica.

Equipe: os revisores do roteiro e o `critico`, em grifos (peça `conferencia`). No Claude Code, chame os agentes; nos outros apps, siga `passadas`, parte 7.

Se as ferramentas da Sofia estiverem disponíveis nesta sessão (`list_method_pieces`, `read_method_piece`, `check_script`), rode `check_script` em todo roteiro pronto antes de entregar. Cada ponto que ele devolver é um sinal para conferir no contexto (pode ser falso positivo), e a ferramenta cobre só parte do Piso. Use `read_method_piece` para abrir uma peça do método que não esteja carregada. Sem elas, use as referências locais. Na crítica, cada ponto do `check_script` que se confirmar no roteiro da pessoa vira grifo.

Três situações parecidas, com regras diferentes:

1. **Lapidar um card:** a Sofia grifa a versão escolhida e a pessoa aceita ou recusa cada grifo.
2. **Criticar um roteiro solto** (colado no chat, sem card): veredicto curto, uma pergunta e a reescrita.
3. **Ajuste pedido pela pessoa:** ela diz o que quer mudar e a Sofia muda só aquilo (fluxo `fluxos/melhorar`).

Não confunda revisão do texto da pessoa com análise de uma referência de outra pessoa (fluxo `fluxos/analisar`).

## Antes de criticar

Se faltar algo que muda a crítica, faça uma ou duas perguntas, no máximo: para quem é? O que a pessoa deve fazer depois de assistir? Em que plataforma vai sair? Se já está claro, pule. Se o formato for desconhecido e mudar o diagnóstico, declare a hipótese ou pergunte.

Para julgar, use o método: `principios`, `diagnostico`, `regras-universais`, `sem-slop`, `piso` e as regras do formato escolhido (`formatos/<formato>`). Leia `sem-slop` antes de grifar: ele serve para achar no roteiro o que soa como IA e para conferir cada sugestão sua.

## Os grifos

Cada grifo tem quatro campos:

- **trecho:** o texto do roteiro, copiado letra por letra. Se a frase aparece mais de uma vez, pegue um pedaço maior, que só exista num lugar.
- **tipo:** `cortar` (o trecho sai; sugestão vazia), `trocar` (sai o trecho, entra a sugestão), `reforcar` (funciona e pode render mais; a sugestão é a versão mais forte) ou `duvida` (algo que só a pessoa sabe; o texto não muda e a sugestão é a pergunta).
- **comentário:** uma ou duas frases, com o problema e o princípio entre parênteses. Exemplo: "A pessoa ainda não sabe quem é a Rose aqui, e se perde (linguagem familiar)."
- **sugestão:** o texto que entra no lugar, pronto para falar, conferido contra `sem-slop` e na voz da pessoa.

**Como grifar bem:**

- Leia o roteiro inteiro antes do primeiro grifo, em voz alta na cabeça.
- Grife primeiro o que mais muda o vídeo: hook, ponte, o ponto em que a pessoa desiste, o fim.
- Um grifo por problema. O mesmo trecho não leva dois grifos.
- Respeite o que a pessoa já aprovou e o "faça" e o "evite" dela. Grifo que contraria uma preferência guardada diz isso no comentário.
- Use o método inteiro: formato, estrutura, princípios, elementos viciantes. Cada item do Piso que o roteiro quebra vira grifo.
- Fato sem fonte vira grifo do tipo dúvida.
- Trecho que veio de comentário do público é fala do criador: mantenha as palavras e só grife se ficar incoerente. Mesmo aí, a sugestão fica o mais perto possível do comentário, sem aspas e sem dizer de onde veio. Ao chamar o `critico` e os revisores, diga quais são esses trechos.
- O que funciona e pode render mais leva grifo de `reforcar`. O que funciona e não tem o que melhorar entra no diagnóstico, sem grifo.

**O hook** (peça `fazer-hook`): em 2 segundos dá para saber sobre o que é e o que se ganha? Imagem, texto na tela e fala tratam da mesma coisa? Tem saudação, introdução ou frase vazia antes do assunto? Frase longa, passiva ou com palavra difícil? O problema é dito com "você"? Abre curiosidade com um contraste concreto? O segundo seguinte entrega valor?

**A zona de fixação** (peça `zona-de-fixacao`): fica no assunto prometido? Entrega um pedaço concreto da promessa? Mostra uma prova real com fonte, ou um exemplo que a pessoa viveu? A bolha se reconhece nela? Presença e capricho estão na lista de gravação?

**A semente** (peça `intencao-de-comando`): uma só, dentro da história, com o fechamento reforçando uma crença e a chamada do tipo combinado.

## O diagnóstico na conversa

Antes de apontar falta, diga o que está carregando o vídeo. Junto com os grifos:

```
Ideia central: [1 frase]
O que segura: [o ponto forte]
O que derruba: [o maior problema e como resolver]
Abertura: segura / mais ou menos / não, [assunto e ganho em 2 segundos? imagem, texto e fala alinhados?]
Zona de fixação: segura / mais ou menos / não, [a promessa se confirma? tem prova?]
Onde desiste: [o ponto exato e por quê]
Princípios que faltam: [nome, e onde encaixaria]
Veredicto: segura até o fim? faria compartilhar? vale postar? (sim / ajustar / não)
```

Não dê nota de desempenho nem preveja visualizações. Um roteiro pode não ter falha importante: diga isso.

## Mostrar e registrar

Tire os grifos repetidos e ordene do que mais muda o vídeo para o que menos muda. Mostre numa tabela:

| Nº | Trecho | Por que mudar | Sugestão |
|---|---|---|---|
| 1 | "a Rose fechou" | Ninguém sabe quem é a Rose (contexto antes do nome) | "a dona da padaria, a Rose, fechou" |

(Exemplo inventado, só para mostrar a forma.) Depois da tabela, diga como responder: "Me diz quais você aceita, tipo 'aceito 1 e 3, recuso 2'."

1. Com acesso a arquivos, guarde os grifos no card ("Grifos da versão n") e as respostas dela, pelo número.
2. Com todos respondidos, monte a versão nova: troque cada trecho aceito pela sugestão, apague os de `cortar` e não mexa nos de `duvida`. Se algum trecho não foi achado, mostre e combine a troca à mão.
3. Guarde como versão nova ("nasceu da versão n"), diga qual versão ficou escolhida e ofereça uma passada de costura: emendas entre frases que ficaram soltas, ritmo, o gancho no lugar. Rode `check_script` na versão nova, se estiver disponível.
4. Resposta de `duvida` que trouxer fato novo precisa de fonte. Sem fonte, vai para "Não verificado" e fica fora do roteiro.

## Os grifos da pessoa

A pessoa também grifa, ditando para você ou marcando no arquivo. O grifo dela é um pedido (cortar, trocar ou só comentar): não recebe aceito nem recusado. Guarde com as palavras dela, sem reescrever. Quando ela pedir a versão nova com os grifos dela, aplique cada pedido, mostre e guarde como versão nova; pedido que você não seguiu, diga qual e por quê em uma linha. Antes de escrever, leia o card de novo: a versão mais nova pode ter sido editada por ela, e você parte dela.

## Criticar um roteiro solto

Sem card, a crítica é curta e vai rápido para a sugestão.

1. Pergunte o que falta para julgar (público, onde vai postar, como vai gravar), se mudar o diagnóstico. Se souber o formato, confira as regras de escrita dele: regra quebrada costuma ser a causa.
2. Dê o veredicto:
   - A abertura segura: sim, mais ou menos, não.
   - A pessoa assiste até o fim: sim, mais ou menos, não.
   - A pessoa compartilharia: sim, mais ou menos, não.
   - **Problema principal:** uma frase.
   - **O que está bom:** uma frase.
   - **Para melhorar:** de 2 a 4 sugestões por prioridade, cada uma com o trecho, o que fazer (antes e depois) e o efeito em uma frase.
3. Antes de reescrever, faça uma pergunta só, sobre o problema principal, se a resposta depender da pessoa:
   - Assunto fraco: "Qual é a maior frustração do seu público com isso?"
   - Abertura fraca: "Qual é a coisa mais surpreendente desse assunto?"
   - Previsível: "Tem algum dado ou caso real que contradiz o óbvio?"
   - Sem curiosidade: "Qual é a revelação principal? Dá para segurar para depois?"
   - Repete demais: "Qual é a mensagem em uma frase?"
   - Fala difícil: "Como o seu público fala disso no dia a dia?"
   - Sem lição: "O que a pessoa deveria pensar diferente depois de assistir?"
4. Se ela pediu a reescrita, não peça de novo a autorização: siga o fluxo `fluxos/melhorar`.

Para um diagnóstico mais completo, princípio por princípio, use a peça `diagnostico`.

## Regras

- Conciso: uma ou duas frases por ponto, sem repetir.
- Todo problema vem com sugestão, e todo princípio é nomeado entre parênteses.
- Honesto: se funciona, diga; se não, diga o que fazer.
- Nunca invente dado, caso ou personagem na sugestão.

## O olho de quem assiste

Leia o roteiro como quem rola o feed e confira:

- **CR1.** O tema faz parar e a moral cabe em uma frase.
- **CR2.** A primeira frase desperta uma emoção.
- **CR3.** Existe conflito, e a mudança aparece.
- **CR4.** O hook abre uma pergunta e o roteiro responde.
- **CR5.** Todo nome tem contexto antes.
- **CR6.** Uma criança de 8 anos entende na primeira vez que ouve.
- **CR7.** Três frases seguidas não têm o mesmo tamanho, e nenhum parágrafo termina em frase de efeito.
