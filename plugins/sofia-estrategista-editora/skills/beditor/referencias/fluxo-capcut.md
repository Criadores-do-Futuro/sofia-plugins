# Executar a direção do bEditor no CapCut

As skills do plugin instalado são a autoridade para contratos, limites e funções.
Localize-as pelo catálogo do host e leia somente a rota atual. Não use caminhos
de uma versão fixa nem mantenha uma cópia paralela do SDK dentro do bEditor.

## Estado que atravessa as etapas

Retenha no contexto ou em `edicao/capcut-estado.json`, quando houver projeto:

| Estado | O que preservar |
| --- | --- |
| Fontes | Caminhos locais, nomes originais, dimensões, duração, ordem, VID/URI e origem |
| AI Lab | ID da tarefa de corte, último `next_event_id`, plano/card e resultado selecionado |
| Rascunho Web | ID da sessão, snapshot completo pareado com sua versão, URLs retornadas |
| Legendas | `unique_key`, parâmetros do lote, resultado completo, estado de liquidação e vínculos fonte→segmento |
| Geração | `generate_id`, vínculo exato do card e versão, chave emitida, tarefa lógica, spec e cobrança retornada |
| Revisão | O que foi aprovado, pendências e verificações realmente feitas |

Guarde apenas contexto reutilizável: não persista credenciais, tickets de upload,
capabilities de autorização, cookies ou cabeçalhos nesses arquivos. Cards com
capabilities opacas ficam no contexto estruturado do host pelo protocolo oficial.
Não grave esses registros como atributos customizados do STDraft.

IDs de tarefa AI Lab, sessão de rascunho, VID, recurso de workspace e segmento
são entidades distintas. Não deduza uma pelo valor de outra. Um link do editor
não basta para conectar um rascunho arbitrário a uma sessão gerenciada.

## Upload

Leia `CapCut:capcut-upload` e `references/codex-local.md` dessa skill.
Use `capcut_asset_upload_credential` com `version:2` e o uploader embarcado.
Não faça upload pelo navegador ou app desktop. Preserve ordem e nomes únicos.

Vídeo/áudio só termina com VID e `setPublic.success:true`; imagem exige URI.
Guarde os sucessos parciais e não reenvie bytes de arquivo já enviado. Falha de
finalização ou script é tratada na etapa correspondente, sem refazer OAuth.

## Corte e montagem

Leia `CapCut:video-editing` e `references/ai-rough-cut.md`. Antes de upload ou
envio, confirme ferramentas AI Lab e renderizadores nativos de plano, vídeo e
música. Submeta o guia editorial no `query` de `capcut_ailab_start_edit`, incluindo
o que preservar, duração desejada, formato e proibições pertinentes ao pedido.
Não prometa que uma instrução em linguagem natural já foi executada com precisão.

Retenha tarefa e cursor. Faça polling com `capcut_ailab_poll_edit_progress` e
processe os eventos em ordem, apresentando cards nativos com o input exato.
Respostas de plano vão uma vez a `capcut_ailab_submit_plan_response`; espere
o usuário quando o protocolo pedir decisão. Não invente percentuais ou narre
polls vazios. Respeite `poll_after_ms`.

Um resultado completo deve ser exibido por `video_preview`. Para legendas ou
acabamento adicionais solicitados, continue em pós-edição com o `stdraft` do
resultado escolhido. Esse seed pode ser só um vídeo achatado: examine o que
está editável e não invente camadas separadas. Sem seed válido, preserve o vídeo
e reporte a limitação. AI Lab não recebe automaticamente mudanças do editor Web.

## Legenda ou transcrição, sem novo corte

Leia `video-editing/references/auto-captions.md` e `references/post-editing.md`
do plugin. Não chame nenhum `capcut_ailab_*` para legenda isolada, nem como
fallback de transcrição truncada, aplicação falha ou rascunho ausente.

1. Reutilize VID/identidade real das fontes de fala e escolha a sessão de rascunho
   para `draft_session_id`, inclusive em reconhecimento sem aplicação.
2. Para um lote novo, crie uma chave estável e envie as fontes juntas a
   `auto_caption_submit`. Para lote existente, consulte a mesma chave primeiro.
3. Consulte `auto_caption_query` até `next_action=none`, respeitando o intervalo.
   Falha parcial não encerra tarefas ainda pendentes. `manual_recovery` interrompe
   tentativas automáticas. Não crie outra chave porque uma resposta demorou.
4. Retenha o resultado estruturado completo; exibição truncada não é transcrição
   completa. Recupere pela mesma consulta, sem nova cobrança. Preserve timestamps
   de origem em ms e vínculos verificados da fonte aos segmentos.
5. Confira nomes, palavras longas, omissões, acentos e ritmo. Para aplicação,
   deixe o builder mapear trims e velocidade; não aplique deslocamento global.

Sem rascunho e com pedido de legendar o original, prepare o DRAFT inicial pelo
protocolo documentado e `apply_video` com duração/dimensões reais e áudio original.
Depois aplique as legendas. Isso não autoriza reconstruir uma timeline existente.
Reconhecimento/SRT apenas termina na entrega dos recursos, sem salvar um vídeo.

## Aplicar materiais e salvar

Leia `CapCut:capcut-stdraft-builder`, seu `reference/application.md` e
`CapCut:web-collaborative-editing`. Adquira legendas/materiais antes do bloqueio
de edição. Use funções atômicas oficiais para adicionar, atualizar, reposicionar
ou remover; não escreva segmentos/Merge patches à mão nem copie o builder.

Uma rodada de edição segue:

1. Reutilize a sessão correta. Crie outra só para um novo rascunho solicitado.
2. Imediatamente antes da alteração, `check_stdraft_state` com a versão retida.
   Se estiver stale ou faltar baseline, leia `get_stdraft_snapshot`.
3. Revalide alvos na baseline atual. Encadeie os `result["draft"]` das funções,
   respeitando warnings e validação. Corrigir legenda existente não significa
   reaplicar todo o lote nem empilhar outra legenda.
4. Faça um `push_stdraft_snapshot` com o documento completo e a versão-base.
   Em conflito, preserve a edição Web e siga a recuperação oficial; não force
   sobrescrita. Resultado incerto exige consultar estado antes de reenviar.
5. Retenha o snapshot/versão lidos de volta pelo servidor. Sem read-back,
   busque uma baseline antes da próxima edição; o documento enviado não é prova
   do que a conversão preservou. Abra/reutilize o editor desta sessão e entregue
   o link Web retornado com seu rótulo original.

Novas fontes usam `vid://` e `tos://`; preserve `asset://`, `sid://` e `vimo://`
existentes. Caminho local ou URL pública não substitui mídia importada. Adicionar
um vídeo sobre intervalo ocupado pode empilhá-lo; não equivale a ripple/append.
Remover um segmento não fecha automaticamente o buraco nem limpa transições.

## Visual e geração

Busque fontes, música, SFX, efeitos, filtros e transições com
`search_capcut_material`. Ele não busca footage nem imagens. Use mídia fornecida,
fontes licenciadas ou geração pedida para B-roll. Fonte desejada, como Montserrat,
precisa existir como recurso válido; sem ela, informe a alternativa.

Use `CapCut:generate-media` para imagens/vídeos. Uma sequência de geração começa
no card autenticado de parâmetros; referências anexadas sobem antes do primeiro
card. Após o card, encerre sem texto e espere. Não envie geração nos bastidores
de uma proposta de motion nem confirme créditos pelo usuário. Preserve todas as
chaves e seleções, acompanhe a tarefa até liquidação (`next_action=none`), mostre
os resultados pelo renderer oficial e reporte `actual_credits` quando fornecido.
Siga a skill para incorporar resultados à sessão escolhida; não os coloque em
um rascunho separado do projeto por conveniência.

Paywall de legendas e de geração são fluxos diferentes: siga o dono da operação,
mostre o link `benefit_check_label`/`benefit_check_url` devolvido e não compre ou
confirme pagamentos. Abertura de página não prova pagamento.

## Limites e exportação

Consulte funções disponíveis antes de assumir suporte a máscaras, keyframes,
tracking de rosto, cortes fonéticos, mistura de áudio ou composições antigas.
Operação sem função documentada vira limitação ou orientação manual no CapCut,
nunca automação de UI ou troca silenciosa para outro motor.

Os contratos atuais de sessão salvam rascunhos; não oferecem aqui uma ferramenta
genérica de exportação de toda pós-edição. Use uma exportação apenas quando uma
ferramenta realmente a fornecer ou quando o usuário a concluir no editor. Não
entregue o vídeo antigo do rough cut como se incluísse o acabamento recém-salvo.
