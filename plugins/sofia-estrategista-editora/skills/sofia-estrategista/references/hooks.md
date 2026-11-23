# Hook

O hook é a primeira frase do vídeo, a que faz a pessoa parar de rolar. Com o conector ligado, o método do hook vem no pacote do `sofia_preparar_escrita` com `tipo: "hook"`, ou em `sofia_metodo` com `hook/<formato>` quando ainda não há card. Siga a ordem e os tipos que o conector mandar: esta página é o apoio para quando ele não está ligado e o porquê das regras.

## O que um hook bom tem

- **É concreto.** Tem uma pessoa, um número, um objeto, um lugar. Quem ouve consegue ver a cena.
- **Deixa uma pergunta na cabeça de quem ouve.** Quem, quanto, como, o que aconteceu depois. Na observação do método, as dúvidas de "quem", "como" e "quanto" rendem mais que a de "por quê". O hook deixa a dúvida com uma afirmação, sem fazer a pergunta em voz alta.
- **É verdade.** Choque, número e notícia só com fonte. Opinião vale quando é a opinião sincera de quem fala e o vídeo prova.
- **O vídeo paga.** Antes de sugerir, aponte em que bloco o roteiro responde a pergunta do hook. Se o corpo não prova, o hook não serve.
- **Combina com o formato.** Cada formato pede um tipo de abertura (veja o arquivo do formato em `formatos/`).
- **Junta dois ou três elementos.** No método, os hooks mais fortes misturam, por exemplo, curiosidade com algo familiar, ou conflito com um número.

## Os tipos de hook

| Tipo | O que faz | Molde | Formatos que pedem |
|---|---|---|---|
| Choque de crença | Contraria o que o público acredita e diz o que ele queria que fosse verdade | "Pare de {coisa que todo mundo faz}." / "{Regra sagrada} foi a pior dica que eu recebi." | Palestrinha, Lo-Fi, Conversa de Bar, Trivial |
| Declaração de consequência | Entrega o resultado antes da causa e deixa a dúvida de como aconteceu | "E foi assim que {pessoa} {resultado surpreendente}." | Bastidores, Tela Dividida, Tela Verde, Storytelling Visual, Narrado, Dinamismo, Vlog |
| Provocação direta | Desafia uma crença ou um hábito de quem assiste | "Se você {hábito comum}, {consequência que dói}." | Palestrinha, Caixinha Polêmica, Lo-Fi, Diálogo |
| Cena imersiva | Põe a pessoa dentro de um momento antes de qualquer contexto | "{Lugar}, {hora}. {Pessoa} {ação no meio da cena}." | Cine, Narrado, Conflito Situacional, Analogia, Vlog, Tela Dividida |
| Contraste inesperado | Junta duas coisas que não deviam estar juntas | "{Coisa comum} {fez algo absurdo} e {consequência na sua vida}." | Comparação, Diálogo, Narrador, The Office, Criativo Preguiçoso, Analogia, Formato Combinado |
| Curiosidade numérica | Um dado concreto que cria dúvida na hora | "{Coisa conhecida} tem {número verificado} de {algo que assusta}." | Dinamismo, Experimento Social |
| Clipe do analisado | Uma fala de quem é analisado, de até 4 segundos, que se entende sozinha, seguida de um rótulo exagerado que vira elogio | Clipe + "{Nome} tem {o X mais Y} da internet, na minha opinião." | Análise |

### Choque de crença, passo a passo

O método da Sofia está testando a hipótese de que o hook que mais prende cria um conflito na cabeça: contraria o que a pessoa acredita e, ao mesmo tempo, diz algo que ela gostaria que fosse verdade.

1. Escreva em uma linha o que o público acredita sobre o tema.
2. Escreva em uma linha o que ele gostaria que fosse verdade (em geral: menos trabalho, menos custo, menos culpa).
3. O hook afirma o item 2 contra o item 1, com o menor número de palavras, como ordem, confissão ou consequência absurda.
4. Aponte onde o vídeo paga o choque.

Limites: o choque tem de ser verdade. Promessa de resultado ("vai crescer", "vai faturar") não entra. Ordem de parar entra. E o choque costuma puxar para o molde "não é X, é Y": troque por uma ordem direta.

Se o conector disser que a opção 1 é sempre um choque de crença, siga. Se o cérebro do perfil mostrar que outro tipo funciona melhor com esse público, mostre isso à pessoa junto com as opções.

## Como mostrar as opções

Antes de escrever, junte tudo o que você sabe: o método do hook, o formato e a estrutura do card, a bolha (o vocabulário, o que mexe com ela, os comentários bem curtidos) e o que o cérebro diz desta pessoa (os hooks que funcionaram e os ajustes que ela já fez em hooks seus).

Mostre de 3 a 5 hooks de tipos diferentes. O número segue a preferência da pessoa guardada em `como-trabalhar` ou o que o pacote do conector pedir. Sem preferência guardada, mostre 3 e pergunte se ela prefere ver mais (até 5); com o OK dela, guarde a resposta com `cerebro_preferencia`. Cada hook vem assim:

```
1. "{o hook}"
   Tipo: {tipo}. Prende porque {uma linha}. O vídeo paga em {bloco}.
```

Junto, mostre 2 estilos de gravação que combinam com o formato, cada um em uma linha: o enquadramento, o corte e o texto na tela. Depois pergunte qual hook e qual estilo a pessoa prefere, e diga que dá para misturar dois hooks.

## A ponte

A ponte é a frase logo depois do hook, que liga a abertura ao resto. Ela é curta: uma frase, no máximo duas. Ponte longa gasta os segundos em que a pessoa decide se fica.

## Quando a pessoa quer conversar sobre o hook

- Converse só sobre o hook. O resto do roteiro espera.
- Pergunte, ou leia na mensagem dela, qual pedaço ela gostou. Esse pedaço fica.
- O hook costuma se perder no fim da frase. Proponha variações do fim, mantendo o começo.
- Se ela disser que falta polêmica ou curiosidade, mexa no que está em jogo: quem perde, quanto, o que ninguém esperava. Mais adjetivo não resolve.
- Com o hook fechado, salve no card e só então siga para o roteiro.

## Padrões que costumam funcionar

- "{Rótulo provocativo} + {resultado surpreendente}": debate e curiosidade.
- "{Pessoa conhecida} {ação surpreendente}.": o nome conhecido diminui o esforço de entrar.
- "{Afirmação forte sobre um conflito que todo mundo vive}": debate na hora.
- "{Dado com fonte que assusta sobre algo do dia a dia}": medo, curiosidade e familiaridade juntos.

Na observação do método, hook com dado concreto (número, nome, fato) segura mais que hook só emocional. Teste com o público da pessoa antes de tratar como regra.

## O que não é hook

- Comentário de vídeo nunca vira hook automático. Ele entra no meio, como fala do próprio criador (prova, virada, exemplo, reação). Só abre o vídeo se a pessoa escolher.
- Pergunta retórica no lugar da afirmação.
- "Neste vídeo você vai ver", "Você sabia que", "Fica até o final": anunciam em vez de mostrar.
- Notícia inventada ou exagerada sem fonte.

## Como medir

Quando der, grave o hook atual e o novo com o mesmo corpo. Compare quanto da audiência fica nos três primeiros segundos e as views em 48 horas. Guarde o resultado no cérebro do perfil (`o-que-funcionou` ou `o-que-nao-funcionou`).
