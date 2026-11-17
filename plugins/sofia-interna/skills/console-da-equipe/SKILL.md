---
name: console-da-equipe
description: "Explica o console da equipe da Criadores do Futuro, os cargos (admin, analista, gestor de comunidade, editor), os mercados (BR, LATAM, EN) e a regra de operação: a máquina prepara, uma pessoa aprova. Use no começo de qualquer trabalho da equipe com o console ou com o MCP sofia-interna, e quando alguém disser 'o que eu posso fazer aqui?', 'qual é o meu cargo?', 'quais mercados eu enxergo?', 'como o console funciona?' ou 'por que não aparece essa ferramenta?'."
---

# Console da equipe

O console é o lugar único da equipe da Criadores do Futuro para operar as comunidades de
três mercados. Você acessa o console pelo MCP `sofia-interna`, com as mesmas regras que a
pessoa teria na tela.

Cada mercado tem a sua base. O BR fica no Firebase nacional; LATAM e EN, no internacional.
As bases não se misturam. O cargo de alguém num mercado vem da base daquele mercado. Se
uma ferramenta responder que a fonte de um mercado não está configurada, diga isso em uma
linha e siga com os outros mercados.

## Comece sempre por `equipe_quem_sou`

Antes de qualquer outra coisa na conversa, chame `equipe_quem_sou`. Ela diz:

- quem é a pessoa;
- quais cargos ela tem;
- em quais mercados ela atua.

Guarde a resposta. Use-a para decidir o que oferecer. Se a chamada falhar ou pedir login,
diga isso em uma linha e pare. Não tente contornar.

Se a pessoa pedir algo fora do cargo ou do mercado dela, diga que o cargo dela não alcança
isso e quem pode ajudar (o admin). Cada ferramenta confere cargo e mercado de novo na
chamada, então a negativa do servidor vale mais que qualquer palpite seu.

## Cargos

| Cargo | O que alcança |
|---|---|
| `admin` | Tudo nos mercados em que é admin. O admin vale por base: o admin do BR não é admin de LATAM e EN, e o contrário também vale. LATAM e EN dividem a base internacional, então quem é admin lá é admin dos dois. Também vê quem tem qual cargo (`console_equipe_listar`). |
| `analista` | A fila de análise e o aprendizado da Sofia. |
| `gestor_comunidade` | Eventos, tarefas agendadas, canais, insights do Discord, SOPs, demandas e depoimentos. |
| `editor` | O catálogo de mídia e as demandas que vierem para edição (`console_demandas_listar` e `console_demanda_mover`, só as dele). |

Gestor e editor são dados mercado a mercado: a mesma pessoa pode ser gestora no LATAM e
editora no EN, e cada cargo vale só no mercado em que foi dado. Sem cargo num mercado, ela
não enxerga nada dele. Nunca ofereça dado de um mercado que não
apareceu em `equipe_quem_sou`.

## Mercados

| Código | Comunidade | Idioma dos textos publicados |
|---|---|---|
| `br` | Brasil | português do Brasil (pt-BR) |
| `latam` | América Latina | espanhol latino (es-419) |
| `en` | Estados Unidos e inglês | inglês |

O console em si é em português. Os textos que saem para as comunidades seguem o idioma do
mercado. Quando a pessoa pedir um texto, confirme o mercado antes de escrever.

## A regra de operação

**A máquina prepara. Uma pessoa aprova.**

- Você prepara: rascunha, simula, monta a prévia, sugere.
- A pessoa aprova: nada sai para uma comunidade sem o sim dela.
- Toda mudança, feita pelo console ou pelo MCP, fica registrada em `console_auditoria`
  (quem, por onde, o quê, antes e depois). Por isso, não faça "teste" em dado real.
- Um processo (SOP) só vale depois que alguém o ativa no console. Rascunho não vale.
- Um depoimento só vai a público com a autorização registrada.

Em caso de dúvida entre agir e perguntar, pergunte. Mostre o que vai mudar, antes e depois,
e espere o sim.

## Ferramentas por cargo

Os nomes abaixo são os do servidor. A lista que você realmente tem depende do cargo e do
que já está em produção. **Antes de prometer uma ação, confira a lista de ferramentas
disponíveis nesta sessão.** Se uma ferramenta não aparecer, diga que ela ainda não está
disponível e não invente um caminho.

- Todos da equipe: `equipe_quem_sou`.
- Gestor de comunidade:
  - eventos e canais: `console_eventos_listar`, `console_evento_criar`,
    `console_evento_alterar`, `console_evento_desativar`, `console_canais_listar`;
  - tarefas: `console_tarefas_listar`, `console_tarefa_ver`, `console_tarefa_criar`,
    `console_tarefa_alterar`, `console_tarefa_mover_ocorrencia`, `console_tarefa_previa`,
    `console_tarefa_executar_agora`, `console_tarefa_historico`;
  - aprovações: `console_aprovacoes_pendentes`, `console_execucao_aprovar`,
    `console_execucao_recusar`;
  - Discord e métricas: `console_discord_atividade`, `console_discord_mensagens`,
    `console_insights_salvar`, `console_insights_listar`, `console_metricas`;
  - SOPs: `console_sops_listar`, `console_sop_ver`, `console_sop_rascunho_salvar`;
  - demandas e depoimentos: `console_demandas_listar`, `console_demanda_criar`,
    `console_demanda_mover`, `console_depoimentos_listar`, `console_depoimento_salvar`.
- Editor: `console_demandas_listar`, `console_demanda_mover`.
- Admin: tudo isso e `console_equipe_listar`.

## Para cada tipo de pedido, use a skill certa

| A pessoa quer... | Skill |
|---|---|
| criar, mudar ou conferir aviso e tarefa agendada | `avisos-e-tarefas` |
| saber o que a comunidade anda dizendo no Discord | `insights-do-discord` |
| transformar a ata de uma reunião em tarefas | `demandas-e-reunioes` |
| achar e guardar depoimentos | `depoimentos` |
| deixar algo rodando sozinho toda semana | `rotinas-agendadas` |

## O que o console não faz

- O WhatsApp está fora por enquanto. O destino de um aviso é só canal do Discord.
- Ativar ou arquivar um SOP é só no console, por gestor ou admin. Pelo MCP você salva
  rascunho.
- Cargos e mercados se dão pelo admin, fora do MCP. Você pode listar, não conceder.
