---
name: demandas-e-reunioes
description: "Transforma a ata ou a transcrição de uma reunião em demandas com responsável e prazo no quadro do console, e move as demandas entre as colunas (produção, aprovação, execução, concluído). Use quando a equipe disser 'transforma essa reunião em tarefas', 'cria as demandas dessa ata', 'o que ficou combinado na reunião?', 'move a demanda para aprovação', 'conclui essa demanda', 'pede ajustes nessa demanda', 'o que está em produção?' ou 'o que está atrasado no quadro?'."
---

# Demandas e reuniões

O quadro de demandas tem quatro colunas: `producao`, `aprovacao`, `execucao` e `concluido`.
Cada demanda tem título, descrição, mercado, responsável, prazo (se houver) e o histórico de
quem moveu e quando. Serve para `gestor_comunidade` e `admin`; o `editor` vê e move só as
demandas dele, e não aprova nem pede ajuste. Comece pela skill `console-da-equipe` se ainda
não chamou `equipe_quem_sou`.

Por enquanto, uma demanda só se cria e se move. Ainda não há ferramenta para mudar título,
descrição, responsável ou prazo de uma demanda que já existe; se for preciso, diga isso e
sugira que o gestor ajuste pelo console quando a tela permitir.

Confira se `console_demanda_criar`, `console_demandas_listar` e `console_demanda_mover`
aparecem na lista de ferramentas da sessão. Se não aparecerem, diga que ainda não estão
disponíveis.

## Da ata para as demandas

1. **Pegue a ata.** A pessoa cola o texto, aponta um arquivo ou uma reunião gravada que
   você consiga ler com as ferramentas que já tem. Leia inteira.
2. **Extraia o que foi combinado.** Procure frases de compromisso: "fulano vai...",
   "precisamos...", "até sexta...". Cada compromisso vira uma demanda. Discussão sem
   compromisso não vira demanda.
3. **Para cada demanda, defina:**
   - **título:** um verbo no começo, curto (ex.: "Atualizar o aviso de terça");
   - **descrição:** o que fazer e o que é "pronto", em uma ou duas frases;
   - **mercado:** `br`, `latam` ou `en`. Se a reunião falou de mais de um, crie uma demanda por
     mercado;
   - **responsável:** o e-mail da pessoa que se comprometeu na ata. Ela precisa ser
     editor, gestor ou admin daquele mercado. Se a tarefa é sua (do Claude), o responsável
     é `claude`. Se a ata não diz, deixe o campo vazio e pergunte; sem responsável, só o
     gestor vê a demanda;
   - **prazo:** o dia dito na ata, no formato `AAAA-MM-DD` (ex.: `2026-11-20`). Se não
     houve prazo, não invente: pergunte ou deixe sem.
4. **Cheque duplicidade.** Chame `console_demandas_listar` e veja se já existe demanda igual.
   Se existir, não crie outra: mostre a existente.
5. **Mostre a lista antes de criar.** Uma tabela com título, responsável, prazo e mercado.
   Marque o que você deduziu e o que a ata diz com clareza. Aponte as dúvidas.
6. **Com o sim da pessoa, crie** cada demanda com `console_demanda_criar`, passando
   `origem: "reuniao"`. Sem esse campo, a demanda fica registrada como criada pelo MCP.
7. **Entregue o resumo:** quantas demandas criou, de quem, para quando, e o que ficou sem
   responsável ou prazo.

Não crie demanda para pessoa fora da equipe, nem prometa prazo em nome de alguém.

## Mover no quadro

- `console_demandas_listar` mostra o quadro. Filtre por coluna, mercado ou responsável.
- `console_demanda_mover` muda a demanda de coluna. Mostre à pessoa de onde para onde
  antes de mover e espere o sim, exceto quando ela mesma pediu o movimento.
- Sequência normal: `producao` → `aprovacao` → `execucao` → `concluido`.
- Aprovar é do gestor. O editor manda a demanda para `aprovacao`, mas não a tira de lá e
  não pula de `producao` direto para `execucao`. O servidor recusa esses movimentos.
- O histórico guarda quem moveu e quando, então não mova demanda de outra pessoa sem a
  pessoa pedir.

## Pedir ajustes

"Pedir ajustes" quer dizer: a demanda estava em aprovação e **não foi aprovada**.

1. Pergunte qual é a instrução do ajuste, se a pessoa não disse. Anote com as palavras dela.
2. Mova a demanda de volta para `producao` com `console_demanda_mover`, com a instrução no
   campo `instrucao`, para o responsável ver o que mudar. Sem a instrução, o servidor
   recusa o pedido de ajuste. Ela fica guardada com as palavras exatas.
3. Confirme: "Voltei para produção com a instrução: ...".

Só o gestor (ou o admin) pede ajuste. Não escreva a instrução em outro lugar.

## Concluir

Mova para `concluido` só quando a pessoa disser que está pronto ou quando a descrição de
"pronto" foi cumprida e você consegue verificar. Não conclua demanda por achismo.

## Para o editor

Quem tem o cargo `editor` só lista e move as demandas que são dele. Ele não aprova e não
pede ajuste, então as regras de aprovação e de ajuste acima não valem para ele. Se pedir
algo além disso (criar, ver as dos outros, aprovar), diga que o cargo não alcança e que o
gestor pode ajudar.
