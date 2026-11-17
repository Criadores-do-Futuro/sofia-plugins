---
name: rotinas-agendadas
description: "Explica como deixar uma rotina do Claude agendada com o MCP da equipe (por exemplo, os insights da semana toda segunda de manhã) e quando usar uma tarefa do console (aviso fixo) em vez de uma rotina do Claude. Use quando a equipe disser 'quero isso rodando sozinho toda semana', 'agenda os insights do Discord', 'cria uma rotina', 'o Claude pode fazer isso toda segunda?', 'qual a diferença entre rotina e tarefa?', 'isso vai no console ou numa rotina?' ou 'como faço o lembrete semanal?'."
---

# Rotinas agendadas

Há dois jeitos de deixar algo rodando sozinho. Escolha o certo antes de montar.

## Tarefa do console ou rotina do Claude?

| | Tarefa do console | Rotina do Claude |
|---|---|---|
| **O que é** | Um aviso fixo, agendado no próprio console | Um pedido que o Claude executa em um horário, com o MCP |
| **Quem roda** | O relógio do console | O Claude |
| **Pede julgamento?** | Não: o texto é um modelo com data e hora | Sim: o Claude lê, pondera e escreve |
| **Exemplos** | Aviso toda segunda às 19h; lembrete 24 h e 1 h antes de cada encontro | Ler o Discord da semana e escrever os insights; separar depoimentos novos |
| **Aprovação** | Pode exigir aprovação antes de sair | Não publica nada na comunidade; só salva registros |
| **Skill** | `avisos-e-tarefas` | esta |

Regra prática:

- O texto é sempre o mesmo, só mudam data e hora? **Tarefa do console.** É previsível,
  tem histórico (no prazo, atrasada, pulada) e pode exigir aprovação.
- Precisa ler, comparar ou decidir o que escrever? **Rotina do Claude.**
- Quer que saia para a comunidade? **Tarefa do console, com aprovação.** Uma rotina do
  Claude não deve publicar aviso nem usar `console_tarefa_executar_agora` sozinha.
- Quer os dois (por exemplo, um aviso que cita o insight da semana)? A rotina salva o
  insight e propõe o texto. Uma pessoa cria a tarefa do console e aprova.

## Como deixar uma rotina do Claude agendada

Antes de começar, confira três coisas:

1. **O conector `cdf-equipe` está ativo** na conta onde a rotina vai rodar e a pessoa já
   fez o login da plataforma. Sem isso, a rotina não alcança o console.
2. **A pessoa tem o cargo certo** (gestor de comunidade ou admin) e os mercados da rotina.
   A rotina roda com o acesso da pessoa que a criou, e nunca com mais que isso.
3. **As ferramentas que a rotina usa aparecem na lista.** Para os insights, são
   `console_discord_atividade`, `console_discord_mensagens` e `console_insights_salvar`. Se
   alguma não estiver em produção ainda, diga e espere.

Depois:

1. No Claude Code, peça: "agende esta rotina" e cole o texto da seção abaixo, ou use o
   comando `/schedule`. No app do Claude, crie uma tarefa agendada com o mesmo texto.
2. Escolha o dia e a hora (por exemplo, toda segunda às 9h, no fuso de Brasília).
3. **Rode uma vez na hora** para testar. Veja se salvou o insight no console
   (`console_insights_listar`) e se o texto está certo.
4. Só depois deixe valendo. Combine com a equipe quem lê o resultado e quando.

Cada execução fica registrada na auditoria do console.

## Texto pronto: insights da semana

Cole assim, trocando só o mercado. Uma rotina por mercado.

```
Você é a Sofia interna da equipe da Criadores do Futuro. Rode a rotina semanal de
insights do Discord do mercado BR.

1. Chame equipe_quem_sou. Se eu não tiver o mercado BR, pare e avise.
2. Use a skill insights-do-discord, do plugin cdf-equipe, do começo ao fim.
3. Período: os 7 dias fechados antes de hoje (segunda a domingo).
4. Chame console_insights_listar e leia o último insight de BR, para não repetir o que já
   foi dito e para dizer o que mudou.
5. Cite comentários com as palavras exatas da pessoa, entre aspas, sem corrigir e sem nome
   nem @. Não use nada de quem pediu anonimato.
6. Salve com console_insights_salvar (mercado BR, fonte Discord, período, título e corpo).
7. Não publique nada na comunidade e não crie nem execute tarefas de aviso.
8. Termine com um resumo de 3 linhas: o achado principal, a dúvida que mais se repetiu e
   a ação que eu faria esta semana. Se alguma ferramenta falhar, diga qual e o erro.
```

Para o LATAM, troque BR por LATAM. O texto do insight continua em português, para a
equipe; as citações ficam no espanhol original. Para o EN, só use se houver canal mapeado:
hoje só BR e LATAM têm.

## Outros textos úteis

**Depoimentos da semana** (salva com autorização pendente):

```
Rode a skill depoimentos, do plugin cdf-equipe, para o mercado BR. Procure no canal de
Resultados do Discord os depoimentos dos últimos 7 dias. Salve cada um com o texto
literal e autorizacao pendente. Nunca marque autorizado. Termine com quantos salvou, por
tema.
```

**Quadro de demandas atrasadas** (só lê, não muda nada):

```
Chame console_demandas_listar e liste as demandas com prazo vencido e as paradas há mais
de 7 dias na mesma coluna, por responsável. Não mova nem crie nada. Termine com as 3 que
mais precisam de atenção.
```

## Regras

- Toda rotina nasce com um teste na hora, antes de ficar valendo.
- Rotina que escreve registro (insight, depoimento pendente) pode salvar sozinha.
  Rotina que publica ou muda o que a comunidade vê **não existe**: isso é tarefa do
  console, com aprovação.
- Se a rotina falhar duas semanas seguidas, avise a equipe em vez de insistir em silêncio.
- Rotina não guarda segredo no texto. Login e chaves ficam no conector.
