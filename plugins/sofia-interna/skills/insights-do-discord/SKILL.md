---
name: insights-do-discord
description: "Roda a rotina semanal de insights do Discord: lê a atividade e as mensagens da semana de um mercado, separa dores, pedidos, dúvidas repetidas, elogios e críticas, e salva o resultado no console. Use quando a equipe disser 'faz os insights da semana', 'o que a comunidade falou no Discord?', 'quais as dúvidas que mais se repetem?', 'o que estão reclamando?', 'quem anda ajudando quem?', 'resumo do Discord do LATAM' ou 'prepara o relatório da comunidade'."
---

# Insights do Discord

Os insights mostram o que a comunidade anda dizendo, para a equipe agir. A rotina é
semanal, por mercado. Serve para o cargo `gestor_comunidade` (ou `admin`). Comece pela skill
`console-da-equipe` se ainda não chamou `equipe_quem_sou` nesta conversa.

Antes de começar, confira se `console_discord_atividade`, `console_discord_mensagens` e
`console_insights_salvar` aparecem na lista de ferramentas da sessão. Se algum faltar, diga
qual falta e pare. Hoje só os canais do BR e do LATAM estão mapeados. Se o mercado pedido
não tiver canal mapeado, diga isso. Não invente dado.

## Passo a passo

1. **Defina o recorte.** Mercado (`br`, `latam` ou `en`) e período. Sem outra instrução, use
   os últimos 7 dias fechados (segunda a domingo). Confirme o mercado com a pessoa se ela
   atua em mais de um.
2. **Veja os números.** Chame `console_discord_atividade` para o mercado e o período.
   Anote: mensagens por canal, por categoria e por semana, e o que subiu ou caiu em
   relação à semana anterior.
3. **Escolha onde ler.** Os canais com mais atividade, os que mudaram muito e os de dúvida e
   de resultados vêm primeiro.
4. **Leia as mensagens.** Chame `console_discord_mensagens` por canal e período. Leia com
   calma. Anote o que se repete. Se a lista vier cortada, peça a próxima página.
5. **Procure estes sinais:**
   - **dores:** o que trava as pessoas;
   - **pedidos:** o que elas querem que exista (aula, evento, formato, ajuda);
   - **dúvidas repetidas:** a mesma pergunta feita por pessoas diferentes;
   - **elogios:** o que funcionou e por quê;
   - **críticas e reclamações:** o que incomodou, inclusive com a equipe;
   - **quem ajuda quem:** membros que respondem os outros e viram apoio da comunidade.
6. **Cruze com o que a equipe já fez.** Se uma dúvida repetida já tem aula ou aviso, diga:
   o problema pode ser de achar, não de falta. Você pode consultar `console_insights_listar`
   para não repetir o insight da semana passada, e `console_metricas` para ver o contexto.
7. **Escreva os insights** no formato abaixo.
8. **Mostre à pessoa** antes de salvar.
9. **Salve** com `console_insights_salvar`, com o sim da pessoa. Em rotina agendada sem
   ninguém para responder, salve direto: é só um registro, não publica nada.

## Como citar comentários

Esta regra vale sempre.

- Cite com **as palavras exatas** da pessoa, **entre aspas**, do jeito que ela escreveu:
  gíria, erro de digitação, caixa alta, pontuação, emoji. **Não corrija, não resuma, não
  traduza, não junte dois comentários.**
- Cite **sem @ e sem o nome** de quem escreveu.
- Se precisar cortar um trecho, corte inteiro e marque com `[...]`. Não troque palavras.
- Comentário em outro idioma fica no idioma original. Se ajudar, ponha a tradução à parte,
  depois da citação, marcada como tradução.
- **Anonimato:** as mensagens de quem pediu anonimato não chegam pelo MCP. Se aparecer
  qualquer sinal de que alguém pediu anonimato, não use o nome nem a fala. Nunca tente
  descobrir quem é.
- Em "quem ajuda quem", use o nome exibido só se a ferramenta o devolveu e a pessoa não
  pediu anonimato. Na dúvida, escreva "um membro".

## Formato do insight

Título curto que diga o achado principal. Corpo em markdown:

```
## O que mais apareceu
(3 a 5 pontos, o mais forte primeiro; cada um com 1 ou 2 citações literais)

## Dúvidas que se repetem
(a dúvida, quantas vezes apareceu, onde, e se já existe resposta)

## Pedidos
## Elogios
## Críticas
## Quem está ajudando
## O que fazer esta semana
(2 a 4 ações, cada uma com quem pode agir)
## Números da semana
(mensagens por canal e a variação)
```

Corte as seções que ficarem vazias. Insight vazio não ajuda ninguém.

Ao chamar `console_insights_salvar`: mercado, período (de e até), título e corpo. A fonte é
o Discord. Se a ferramenta pedir o autor, mande o da pessoa; em rotina agendada, o autor é a
rotina.

## Regras

- Não invente número nem citação. Se não achou, escreva que não achou.
- Número sem fonte não entra. Cada número vem de `console_discord_atividade` ou
  `console_metricas`.
- Não conclua uma decisão a partir de número. Diga o que os números mostram e deixe a
  decisão com a equipe.
- Se o dado contradisser algo que a equipe disse antes, mostre o conflito e pergunte.
- Insight não é publicado para a comunidade. Fica no console, para a equipe.
