---
name: avisos-e-tarefas
description: "Cria, altera e confere os avisos e as tarefas agendadas do console (semanal, única ou antes do evento), sempre com prévia antes de salvar e aprovação antes de sair. Use quando a equipe disser 'cria um aviso toda segunda às 19h', 'muda o aviso de segunda para terça', 'o evento de segunda passou para terça', 'adia o aviso só dessa semana', 'pula o aviso de hoje', 'manda o lembrete agora', 'o que está agendado?', 'tem aviso aguardando aprovação?' ou 'aprova esse aviso'."
---

# Avisos e tarefas

Uma **tarefa** é um aviso agendado que o console publica sozinho em canais do Discord. Esta
skill é para quem tem o cargo `gestor_comunidade` (ou `admin`). Comece pela skill
`console-da-equipe` se ainda não chamou `equipe_quem_sou` nesta conversa.

Antes de prometer qualquer passo, confira se as ferramentas `console_tarefa_*` aparecem
na lista desta sessão. Se não aparecerem, diga que ainda não estão disponíveis.

## Como a tarefa é montada

- **Mercado:** `br`, `latam` ou `en`.
- **Canais:** destinos que o admin cadastrou. Veja com `console_canais_listar`. Não invente
  canal.
- **Texto:** um modelo. Variáveis aceitas: `{{evento.titulo}}`, `{{evento.descricao}}`,
  `{{evento.link}}`, `{{evento.data}}` e `{{evento.hora}}`. Data e hora saem no idioma do
  mercado e no fuso da tarefa. Variável desconhecida, ou variável de evento sem evento,
  bloqueia o envio e aparece como erro na prévia.
- **Menções:** `permitirMencoes` começa desligado. Só ligue se a pessoa pedir.
- **Agenda,** em três formas:
  - `semanal`: dias da semana (0 a 6), hora (HH:MM) e fuso;
  - `unica`: uma data e hora;
  - `antesDoEvento`: uma lista de antecedências em minutos (por exemplo 1440 e 60).
- **Evento ligado ao aviso:**
  - `proximo`: o próximo evento ativo do mesmo mercado;
  - `fixo`: um evento específico;
  - `todos`: todos os eventos do mercado, só com a agenda `antesDoEvento`;
  - nenhum, para aviso sem evento.
- **Aprovação:** com `exigeAprovacao`, o console prepara o aviso com o texto pronto 12 horas
  antes da hora de sair (`antecedenciaAprovacaoMin`, padrão 720) e ele fica
  `aguardando_aprovacao`. Sem aprovação até a hora, ele é pulado e o motivo fica registrado.
- Aviso atrasado em mais de 6 horas é pulado. O console não publica aviso velho.

## Antes de escrever qualquer texto: carregue os SOPs

O jeito de a equipe escrever avisos mora nos SOPs da área `avisos`. Siga este passo todas
as vezes, mesmo que você ache que já sabe.

1. Chame `console_sops_listar` com o mercado da tarefa, `area: "avisos"` e
   `estado: "ativo"`. Com um mercado, a lista já traz junto os SOPs de `todos`.
2. Rascunho e arquivado não valem, mesmo que apareçam em outra consulta.
3. Para cada SOP ativo, chame `console_sop_ver` e leia o corpo inteiro.
4. Escreva o texto seguindo esses SOPs. Se dois SOPs se contradisserem, mostre o conflito e
   pergunte. Não escolha em silêncio.
5. Se não houver SOP ativo da área `avisos` para o mercado, diga isso e pergunte se pode
   seguir com o seu melhor julgamento. Se a pessoa quiser registrar um jeito de fazer, você
   pode salvar um rascunho com `console_sop_rascunho_salvar`. Quem ativa é a pessoa, no
   console.

## Idioma do texto

- `br`: português do Brasil.
- `latam`: espanhol latino (es-419).
- `en`: inglês.

O seu diálogo com a equipe continua em português. Só o texto do aviso muda de idioma.
Nunca escreva um aviso de um mercado no idioma de outro.

## Criar uma tarefa

1. Confirme com a pessoa: mercado, canal, quando sai, se está ligada a um evento e se
   exige aprovação antes de sair. Em aviso novo, sugira que exija.
2. Carregue os SOPs (seção acima) e escreva o texto.
3. Rode `console_tarefa_previa` com a proposta. Mostre à pessoa o texto final já com
   data e hora preenchidas, as próximas ocorrências, e qualquer erro de variável. Corrija
   o que a prévia apontar.
4. Pergunte: "Posso salvar?". Só com o sim, chame `console_tarefa_criar`.
5. Mostre o que ficou salvo (`console_tarefa_ver`), com a próxima execução.

## Alterar uma tarefa

1. Ache a tarefa com `console_tarefas_listar` e abra com `console_tarefa_ver`.
2. Diga o que vai mudar, antes e depois.
3. Se mudar o texto ou a agenda, rode `console_tarefa_previa` e mostre.
4. Com o sim da pessoa, chame `console_tarefa_alterar`.

## Caso-modelo: "o evento de segunda passou para terça"

Primeiro descubra **o que mudou de fato**.

**O evento mudou de dia?** Altere o evento, não os avisos.

1. Ache o evento com `console_eventos_listar`.
2. Mostre a data antiga e a nova. Peça o sim.
3. Chame `console_evento_alterar`.
4. Os avisos da agenda `antesDoEvento` acompanham sozinhos: se o evento muda de data, sai
   um aviso novo com a data nova. Confirme com `console_tarefa_ver` (próxima execução) ou
   `console_tarefa_previa`.
5. Avisos que **não** são "antes do evento" (por exemplo, um semanal fixo) não acompanham.
   Se houver algum que fale desse evento, mostre e pergunte se muda também.

**Só o aviso muda, o evento continua?** Mova a ocorrência.

1. Abra a tarefa com `console_tarefa_ver` e ache a ocorrência.
2. Se a mudança vale só desta vez, chame `console_tarefa_mover_ocorrencia` com a nova data
   (ou para pular, sem nova data).
3. Se a mudança vale daqui para a frente (por exemplo, o aviso semanal passa a sair na
   terça), altere a agenda da tarefa com `console_tarefa_alterar`.

Na dúvida entre as duas, pergunte: "O evento mudou de dia ou só o horário do aviso?".

## Aprovar o que está esperando

- `console_aprovacoes_pendentes` lista o que aguarda a pessoa.
- Mostre o texto pronto, o canal e a hora de saída.
- Só com o sim claro da pessoa, chame `console_execucao_aprovar`. A ferramenta pede um
  **código de confirmação**: siga o que ela devolver, na ordem em que ela pedir, e não
  invente o código.
- Para recusar, use `console_execucao_recusar` e registre o motivo.

## Executar agora

É o único caminho em que o aviso sai na hora. Trate com mais cuidado.

1. Rode `console_tarefa_previa` e mostre o texto final, o mercado e o canal.
2. Pergunte: "Isso vai sair agora para o canal X. Confirma?".
3. Chame `console_tarefa_executar_agora`. **São duas chamadas**: a primeira devolve um
   código de confirmação; a segunda repete o pedido com esse código.
4. Entre as duas chamadas, mostre o código à pessoa e peça o sim de novo. Nunca use o
   código sem o sim dela.
5. Depois, confirme o resultado em `console_tarefa_historico`.

## Conferir o histórico

`console_tarefa_historico` mostra as últimas 8 semanas: no prazo, com atraso (enviada mais
de 15 minutos depois), pulada e falhou. Se uma execução falhou, leia o motivo e diga à
pessoa, sem repetir o envio por conta própria.

## Regras

- Nunca salve, aprove nem execute sem o sim da pessoa.
- Nunca ligue `permitirMencoes` por conta própria.
- Nunca escreva texto de aviso sem antes carregar os SOPs ativos da área `avisos` do mercado.
- Se uma ferramenta devolver erro, mostre o erro com as palavras dele e diga o que fazer.
