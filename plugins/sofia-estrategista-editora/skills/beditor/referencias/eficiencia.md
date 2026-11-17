# Eficiência — onde o tempo e os tokens foram, e as regras que saíram disso

Medido na sessão que editou os projetos **14** e **15** (11 a 15 de setembro de
2026), lendo o registro completo da conversa, não a memória dela.

## O que a medição mostrou

| Medida | Valor |
| --- | --- |
| pedidos do dono | 110 |
| turnos do modelo | 3 817 |
| chamadas de ferramenta | 2 023 |
| tokens de contexto **relidos** (cache) | 1,25 bilhão |
| tokens escritos pelo modelo | 3,8 milhões |
| imagens lidas | 154 |
| chamadas `Bash` / minutos esperando por elas | 557 / 107 min |
| execuções do render do 15 / do 14 | 32 / 58 |
| execuções de `Edit` | 529 |

A leitura que importa: **cada turno relê ~330 mil tokens de contexto.** O
custo do trabalho não está no que o modelo escreve (3,8 M) — está nas 3 817
vezes em que ele releu a conversa inteira (1 250 M). Uma chamada de ferramenta
a mais custa mais que qualquer script inteiro. Isso muda a pergunta certa de
«como faço este passo mais rápido?» para **«como faço este passo em UMA
chamada, e nunca mais?»**

### Os cinco desperdícios, por tamanho

1. **Retrabalho no render.** Cada ajuste («abaixa a música 20%», «conserta o
   insert de 1:48») recompunha os 4 591 quadros num processo só, salvava 4 591
   PNGs e recodificava o vídeo inteiro: ~10 min de máquina, mais os turnos de
   vigiar. O render do 15 rodou 32 vezes; o do 14, 58. A entrega final do 14
   recodificou o corpo inteiro duas vezes (18 min) só para pôr a capa na frente.
2. **Pipeline reescrito por projeto.** `render14.py`, `render_full.py`,
   `render15.py`, `plano14.py`, `plano15.py`, `cortar15.py`, `qa14.py`,
   `qa15.py`, `entrega14.py`, `entrega15.py` — dez scripts na pasta de rascunho,
   cada um editado dezenas de vezes (529 `Edit`). O que aprendia num vídeo tinha
   de ser reescrito no seguinte, e cada reescrita trazia os erros de novo (a
   legenda perdida na fresta, o cartão que sumia na fronteira do corte).
3. **Olhar em vez de medir.** 154 imagens lidas — folhas de contato de 600 KB,
   várias com mais de 2 000 px, reduzidas a 1 568 px antes de chegar ao modelo.
   Cada leitura é um turno. Boa parte respondia a perguntas que um número
   responde («o split edit está no lugar?», «a cama está 20 dB abaixo?»).
4. **Transcrição repetida.** A do 15 (3 takes, 8,7 min de áudio) rodou duas
   vezes inteiras, 7 min cada, em FP32 na CPU, quando havia GPU e um motor
   para ela na máquina — porque nada guardava que o áudio não tinha mudado.
5. **Vigiar processo longo por turnos.** 445 s de `while … sleep`, 157 s de
   `until …`, `TaskOutput` de 120 s: turnos inteiros gastos esperando.

## As regras (para quem opera o plugin)

1. **Uma etapa, um script do plugin, uma chamada.** Não se escreve pipeline na
   pasta de rascunho. O formato `analise` tem `transcrever.py` →
   `silencio.py` → `render_analise.py` → `qa_analise.py`. O que faltar entra
   **no plugin**, com docstring do porquê, e é commitado — não some com a sessão.
2. **Ajuste é edição de JSON, e o render decide o que refazer.** Mudou o
   ganho da música: edite `plano.json` e rode `render_analise.py`. Ele refaz
   a mistura (3 s) e zero segmentos de imagem. Mudou um insert: refaz os
   segmentos daquele insert. O `manifesto.json` diz o que foi refeito; se ele
   diz que refez tudo, alguma chave está errada — investigue antes de esperar.
3. **Número antes de imagem.** `qa_analise.py` sem `--folha` primeiro. A folha
   entra quando um número reprova e é preciso ver ONDE, ou para a conferência
   final de um cartão novo. Uma imagem por pergunta, nunca uma por dúvida.
   `--comparar aprovado.mp4` prova que um ajuste pontual não mexeu no resto —
   sem olhar nada.
4. **Imagem que vai ser lida nasce em 1 568 px.** `oficina.folha()` já faz
   isso. Folha maior não chega maior ao modelo; chega borrada e custa o mesmo.
5. **Processo longo roda em segundo plano e avisa quando acaba.** `Bash` com
   `run_in_background`, ou `Monitor` filtrando as linhas que importam
   (`segmentos|MASTER|Traceback|!!`). Nunca `sleep` em turno.
6. **Batch onde as perguntas são vizinhas.** Um `ctx_batch_execute` com seis
   comandos e cinco queries custa um turno; seis `Bash` custam seis. O mesmo
   para `Read`: se três arquivos vão ser lidos, vão na mesma resposta.
7. **Cache tem chave de conteúdo — sempre.** Identidade do arquivo
   (`oficina.identidade`, tamanho + cabeça + cauda), hash da receita, hash do
   código que desenha. Chave por posição ou por nome de slot não é cache: é um
   erro adiado. Foi a regra do clipe do cartão; agora é a do pipeline inteiro.
8. **Paralelo onde não há estado compartilhado.** Segmentos de vídeo,
   extração de A-roll e de clipes, rastreio de rosto por take, imagens
   geradas. O teto (8 processos) é de memória, não de CPU. Transcrição fica
   em fila: dois modelos grandes numa máquina de 16 GB disputam memória.
9. **Antes de criar regra a partir de um defeito, meça o defeito.** (Já
   estava em `formato-analise.md`; vale também para desempenho: «está lento»
   não é diagnóstico. `manifesto.json` e o relógio do log são.)

## O que o pipeline novo faz por conta própria

| Peça | Antes | Agora |
| --- | --- | --- |
| composição | 1 processo, PNG por quadro, recodifica tudo | N processos, pipe direto ao ffmpeg, segmentos de 2 s com chave de conteúdo, master por concatenação sem recodificar |
| ajuste de música | render inteiro (~10 min) | só a mistura (~3 s) |
| ajuste de um insert | render inteiro | os segmentos daquele insert (~1–2 min) |
| entrega com capa | recodificar o corpo (18 min no 14) | capa vira segmento; concatenação (segundos) |
| A-roll | extraído por posição no corte | por quadro LOCAL do take: mudar o corte não invalida |
| transcrição | sempre do zero, CPU FP32 | cache por conteúdo; MLX na GPU quando existe |
| rosto (Vision) | por take, em fila, a cada render | uma vez por take, em paralelo, cacheado |
| QA | folha de 600 KB e olho | cinco números em texto; folha só a pedido, em 1 568 px; `--comparar` |
| prova do que foi refeito | nenhuma | `oficina/manifesto.json` |

O ganho não é só de relógio. É de **turnos**: um ajuste que antes eram
«editar o script → rodar → vigiar → ler a folha → corrigir → rodar de novo»
vira «editar o JSON → rodar → ler seis linhas».

## Como se mede, hoje

A tabela do topo foi feita uma vez, à mão. Agora a medida é contínua e
determinística (mesma entrada → mesma tabela), em duas camadas:

**Camada 1 — tempo de máquina, gravado pelos próprios scripts.**
`oficina.Cronometro` embrulha o trabalho principal de `transcrever.py`,
`silencio.py`, `render_analise.py`, `qa_analise.py` e `biblioteca.py catalogar`
e faz append de uma linha JSON em `edicao/oficina/telemetria.jsonl` (para
`catalogar`, que não tem projeto, em `~/.beditor/`): etapa, script, início, fim,
segundos, `rc` (1 se estourou — e a exceção segue), args e o que a etapa
produziu (palavras, emendas, segmentos refeitos/da cache). Append, nunca
sobrescrita: o histórico do projeto é o dado; o manifesto é só a última rodada.

**Camada 2 — tokens e tempo de sessão, lidos do registro do Claude Code.**
`custos.py` lê `~/.claude/projects/<cwd>/<sessão>.jsonl` (e os subagentes em
`<sessão>/subagents/`), conta o `usage` **uma vez por `requestId`** (o registro
tem uma linha por bloco da resposta) e atribui cada turno a uma etapa pelo seu
primeiro `tool_use`. Tempo de parede por etapa = soma dos intervalos entre
eventos consecutivos da etapa, com teto de 120 s por intervalo (acima disso é
espera do dono, não custo da etapa).

```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/custos.py --sessao atual --por-pedido --desde 2026-09-15T00:00
python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/custos.py --projeto <projeto>      # + edicao/oficina/custos.json e a tabela máquina × sessão
```

Atribuição (a ordem é a precedência; a tabela completa está no topo de `custos.py`):

| etapa | casa com |
| --- | --- |
| transcrever · cortar · renderizar · medir | `transcrever.py` · `silencio.py`/`escutar.py`/`dados.json` · `render_analise.py` · `qa_analise.py` |
| provas | `plano.json`, `cartao.py`, `varrer.py`, `lupa.py`, `yt-dlp`, acervo |
| biblioteca · setup · publicar | `biblioteca.py` · `setup.py`/manual · `publicacao.py`/zernio/metricool |
| git · olhar · delegar · artifact | `git ` · `Read` de imagem · `Agent` · `Artifact` |
| editar · investigar · outros | `Edit`/`Write` · `ctx_*`/`Grep`/`Glob`/`Read`/`Bash` que não casou acima · qualquer outra ferramenta |
| conversa | turno sem ferramenta |

O que a primeira leitura real (15/09, projeto 16) já mostrou: das 14 etapas,
**investigar** (23%), **provas** (22%), **editar** (11%) e **olhar** (11%)
levaram 69% dos tokens; as quatro etapas do pipeline (`transcrever`, `cortar`,
`renderizar`, `medir`) juntas, 15%. O custo está em volta do pipeline, não dentro.

## Auditoria de 15/09 — o que já está otimizado e o que não estava

Varredura de todos os scripts atrás de trabalho repetido, paralelismo, cache e
lote. O resultado curto: **a máquina está bem; o gasto é de conversa.**

| Frente | Situação |
| --- | --- |
| paralelismo | `oficina.paralelo` é a única porta: processos para compor segmentos (8 nesta máquina: 10 núcleos − 2, teto de memória), threads para o que é I/O (extrair quadros, transcrever takes, catalogar biblioteca). Erro de um item não derruba o lote. |
| cache | por conteúdo em sete camadas — transcrição, rosto, A-roll, clipe, matte, segmento, áudio — e a do segmento é por **função de desenho usada** (`oficina.assinatura`). |
| trabalho repetido | o A-roll extrai só a janela usada da take (com a folga do split edit) e nomeia por quadro **local**: mudar o corte não invalida nada. O master é concatenação `-c copy` — o corpo nunca recodifica, nem na entrega com capa. |
| lote | `ctx_batch_execute` para investigar; `--comparar` no QA em vez de reler o vídeo; `midiateca.py buscar` antes de sair baixando. |
| scripts em vez de conversa | as quatro etapas são um script cada, com saída de seis linhas. |

Três pontos que **não** estavam resolvidos, e o que se fez:

1. **Ninguém avisava quando terminava.** Um render de 8 min terminava no
   silêncio; ou o dono vigiava o terminal, ou descobria meia hora depois.
   Agora `avisar.py` notifica a máquina no fim do render, e a sessão empurra
   para o celular (regra em `/sofia-estrategista-editora:editar-analise` e `/sofia-estrategista-editora:painel`).
2. **A cache não prestava contas.** Ela funcionava, mas a prova era o relógio.
   Agora cada rodada imprime qual função de desenho mudou e quantos trechos
   isso custou, e grava em `oficina/assinaturas.json`.
3. **O gasto real é de leitura, não de CPU.** 212 M de tokens lidos contra
   35 min de máquina no último vídeo. Dá para cortar onde mais dói:
   - **provas (22%)** — uma folha de contato de 1 568 px responde o que dez
     frames soltos respondem; imagem só quando um número reprova;
   - **investigar (23%)** — **pergunta que pode ser agrupada, agrupa**:
     `ctx_batch_execute(commands, queries)` e `ctx_search(queries: [...])`
     aceitam listas, e uma chamada com cinco perguntas custa uma ida e volta,
     não cinco. Nunca `cat`/`grep` para ler com os próprios olhos.
   - **olhar (11%) fica como está.** Decisão do dono em 15/09: assistir ao
     vídeo é o trabalho, não o desperdício. Não economize aqui.
