---
name: depoimentos
description: "Acha depoimentos da comunidade (por exemplo no canal de Resultados do Discord) e guarda o texto literal no console, com a autorização pendente. Use quando a equipe disser 'acha depoimentos', 'o que os alunos falaram de resultado?', 'salva esse depoimento', 'quais depoimentos já temos?', 'tem prova social do LATAM?', 'essa pessoa autorizou usar a fala?' ou 'separa os melhores resultados da semana'."
---

# Depoimentos

Depoimento é uma fala da comunidade que a equipe pode usar como prova social. Esta skill
acha, guarda e organiza. Serve para `gestor_comunidade` e `admin`. Comece pela skill
`console-da-equipe` se ainda não chamou `equipe_quem_sou`.

Confira se `console_depoimento_salvar` e `console_depoimentos_listar` aparecem na lista de
ferramentas da sessão. Se não aparecerem, diga que ainda não estão disponíveis.

## A regra que não se quebra

**Nunca marque um depoimento como `autorizado` sem um registro explícito de autorização.**

- Registro explícito é uma mensagem, e-mail ou formulário em que a própria pessoa autoriza o
  uso da fala, e que a equipe consegue apontar (link, print, data).
- "Ela postou no canal público" **não** é autorização. "Provavelmente não se importa" **não**
  é autorização.
- Ao salvar, o padrão é sempre `autorizacao: pendente`.
- Se a pessoa da equipe disser que a autorização existe, peça onde está (o link ou o
  registro) e anote essa fonte no registro. Só depois marque `autorizado`. Sem o registro,
  continua `pendente`.
- Se a pessoa disse que **não** autoriza, marque `negado` e não use a fala em lugar nenhum.
- Um depoimento só vira `pronto` com `autorizado`.

## Achar depoimentos

1. **Defina o mercado e o período.** Confirme com a pessoa.
2. **Escolha a fonte.** O principal é o canal de Resultados do Discord do mercado. Veja os
   canais com `console_discord_atividade` e leia com `console_discord_mensagens`. Também
   valem outras fontes que a pessoa trouxer (Hotmart, Instagram, WhatsApp, e-mail), se ela
   colar o texto ou o link.
3. **Procure falas que contam um resultado.** Bons sinais: um número ou um fato concreto
   (primeira venda, mais seguidores, um vídeo que passou de uma marca), antes e depois, o
   que mudou na rotina, elogio ao método ou ao atendimento.
4. **Descarte** pergunta, pedido de ajuda sem resultado, fala sem conteúdo concreto e
   qualquer mensagem de quem pediu anonimato.
5. **Cheque duplicidade** com `console_depoimentos_listar` antes de salvar.

## Salvar

Para cada depoimento, chame `console_depoimento_salvar` com:

- **texto:** o texto **literal**, do jeito que a pessoa escreveu, entre aspas na hora de
  mostrar. Não corrija erro, não tire gíria, não troque palavra, não junte mensagens, não
  traduza. Se precisar tirar um trecho que não serve, tire o trecho inteiro e marque
  `[...]`. Emoji, caixa alta e pontuação ficam.
- **autor:** o nome exibido da pessoa, se a ferramenta devolveu. Sem @.
- **fonte:** `discord`, `hotmart`, `instagram`, `whatsapp`, `email` ou `outro`.
- **link:** o link da mensagem, quando existir.
- **mercado:** `br`, `latam` ou `en`.
- **produto:** se der para saber, o produto de que a pessoa fala.
- **tema:** `resultado`, `transformacao`, `didatica`, `atendimento` ou `critica`.
- **sentimento:** positivo, neutro ou negativo.
- **autorizacao:** `pendente`.

Críticas também valem salvar (tema `critica`): ajudam a equipe. Elas não vão para uso
público.

Mostre a lista antes de salvar, com o texto literal, o tema e a fonte. Com o sim da
pessoa, salve. Em rotina agendada sem ninguém para responder, salve com `pendente`: não
publica nada.

## O que fazer depois

- Entregue um resumo: quantos salvou, por tema, e quantos estão com autorização pendente.
- Se a pessoa quiser pedir a autorização, ajude a escrever a mensagem para o aluno, no
  idioma do mercado. Quem envia é a pessoa da equipe. Você não envia.
- Para ver o que já está pronto para uso, liste com `console_depoimentos_listar` e filtre
  por `autorizado`.

## Regras

- Não use depoimento `pendente` ou `negado` em roteiro, post ou anúncio.
- Não invente depoimento, número nem resultado. Se não achou, diga que não achou.
- Ao citar um depoimento em qualquer texto, use as palavras da pessoa, entre aspas, e só
  mude o que não dá para ler em voz alta (emoji, link, @).
