# Preparação local de plano para CapCut Web

`beditor.capcut_web.apply_new_plan` adapta o plano editorial a um draft **novo e
vazio** por meio das funções públicas `apply_video` e `apply_text` da skill
oficial `capcut-stdraft-builder` instalada no host. Não copia o código do plugin
oficial, não efetua upload, não executa chamadas de rede, não autentica e não
salva ou abre timeline alguma. Um draft existente requer operações específicas
sobre seu snapshot, seguindo a skill oficial de edição colaborativa; esse
adaptador não o substitui nem reaplica o plano.

O chamador seleciona uma sessão, obtém os IDs de mídia por upload, confere a
versão antes de editar e fornece um draft inicial completo válido. Identificadores
de assets são mapeados a URIs `vid://`, `tos://` ou `asset://`; áudio também
aceita `sid://` quando retornado pelo catálogo. Pistas são mapeadas a layers
inteiros explícitos, em espaços separados para áudio e vídeo. Vídeo com `carries_source_audio` falso é inserido mudo;
a imagem é inserida como foto. Lettering simples usa o texto e a fonte padrão
do builder; o adaptador recusa legendas e lettering com estilo em vez de
descartá-los. Para áudio separado, o chamador informa por clipe o papel `fala`,
`musica` ou `efeito`, e pode fornecer volume entre 0 e 4 (padrão 1). O builder
oficial só expõe MUSIC e SOUND: fala é mapeada para SOUND e exige verificação de
reprodução no editor. Para evitar duplicidade, não se permite o mesmo trecho
de áudio em sobreposição ao áudio original do vídeo; silencie o vídeo se a fala
for inserida numa pista separada. J-cuts usam vídeo mudo e áudio independente com
intervalos próprios e preservam os tempos informados no plano. Legendas automáticas usam seu fluxo oficial próprio.
O builder pode indicar que a duração real da mídia não foi verificada; o chamador
precisa verificar. Todos os timestamps são milissegundos.

```python
import sys
from pathlib import Path
from beditor.capcut_web import apply_new_plan

# Localize a instalação oficial do host; não use caminho de outra versão.
sys.path.insert(0, str(Path(skill_root) / 'scripts'))
from apply_materials import apply_video, apply_audio, apply_text

result = apply_new_plan(
    baseline_vazio, plano, resources={'take': 'vid://VID_RETORNADO_NO_UPLOAD'},
    video_layers={'v1': 0}, text_layers={'t1': 1},
    apply_video=apply_video, apply_audio=apply_audio, apply_text=apply_text,
)
```

Quando o plano tiver áudio, acrescente por exemplo `audio_layers={"a1": 0}` e
`audio_roles={"voz": "fala"}` para o clipe de áudio `voz`; forneça os IDs e
pistas que realmente constam no plano.

O retorno tem o draft completo, mapa `video:<id>`/`audio:<id>`/`text:<id>` para IDs reais e
avisos. Examine o documento, então siga `web-collaborative-editing`: use o
baseline e package_id atuais, respeite conflitos, faça push do documento completo
e confirme o retorno e leitura do servidor antes de relatar sucesso. Se a resposta
do push for incerta, consulte a versão do servidor antes de tentar novamente;
não reexecute cegamente a montagem. Em 11 de novembro de 2026, um teste sintético fez upload, traduziu um plano
com vídeo e lettering, salvou um novo draft Web, leu a resposta do servidor e
confirmou visualmente as duas pistas e a prévia. Em uma segunda rodada, a versão atual foi consultada e o vídeo foi encurtado
para 1,5 segundo: a alteração foi salva, lida de volta e observada na timeline,
preservando o lettering. Estes testes não comprovam sincronização concorrente,
legendas, áudio separado, exportação nem comportamento com material real.

## Revisar um snapshot existente

`beditor.capcut_web_revision.prepare_revision` prepara mudanças sobre uma cópia
em memória de um snapshot completo e seu `package_id` não vazio. Use somente
IDs obtidos nesse snapshot. A operação `content` altera texto simples, `placement`
move ou redimensiona um segmento ligado à raiz, e `remove` remove somente um
segmento sem filhos. Legendas não são tratadas como texto simples; vídeo com
transições e remoções em cascata são recusados. Para texto com filhos PATCH de
estilo, a revisão aceita somente conteúdo com mesmo comprimento e faixas
verificáveis; alterações de tamanho exigem um tratamento específico. Colisões de layer são recusadas
pelo builder oficial. Mover um clipe pode exigir sincronização com áudio, e uma
remoção não fecha lacunas: revise os avisos e a timeline.

```python
from beditor.capcut_web_revision import prepare_revision
from manage_materials import update_material, update_placement, remove_material

result = prepare_revision(
    snapshot, package_id,
    [{'op': 'content', 'segment_id': id_texto, 'text': 'Novo título'}],
    update_material=update_material, update_placement=update_placement,
    remove_material=remove_material,
)
```

O package_id retornado identifica **a base da revisão**, não é verificação de
que ela continua atual. Imediatamente antes da edição, confira o estado com
`check_stdraft_state`; em caso de mudança, recupere o snapshot novo e reconcilie
as alterações com a do usuário. Envie o draft completo com o package_id da base;
um conflito exige recuperar e reconciliar, nunca sobrescrever. O código local não
consulta o servidor nem executa push, leitura posterior ou revisão audiovisual.

Em um teste adicional, uma faixa SOUND sintética foi salva na mesma timeline e
apareceu como pista separada; a reprodução audível e o mapeamento de fala ainda
não foram comprovados. O servidor reordenou índices de camada no read-back.
Portanto, para qualquer revisão, use os IDs e o draft retornados pelo servidor,
não presuma que os índices enviados permaneceram idênticos.

## Aplicar legendas reconhecidas

O reconhecimento continua exclusivamente no fluxo oficial de legendas: crie ou
reutilize a sessão de edição, submeta o batch de `auto_caption_submit` e consulte
`auto_caption_query` com a mesma chave até `next_action=none`. Preserve o resultado
estruturado completo; uma exibição truncada não é uma transcrição completa. Não
use AI Lab para um pedido que apenas reconhece ou aplica legendas. Em falha,
paywall ou recuperação manual, preserve o batch e siga a skill oficial.

`beditor.capcut_captions.apply_recognized` recebe o resultado já completo, o
snapshot e `package_id`, além de vínculos explícitos entre cada VID ou par
workspace/resource e IDs dos segmentos. Um segmento `vid://` deve coincidir com
o VID reconhecido. Para `asset://`, o chamador deve fornecer uma comprovação
obtida anteriormente com o vínculo da fonte, versão, URI e origem da evidência;
o snapshot não fornece esse mapeamento e o código não o inventa.

```python
from beditor.capcut_captions import apply_recognized
from apply_captions import apply_captions

result = apply_recognized(
    snapshot, package_id, resultado_completo,
    [{'resource': {'vid': vid_original}, 'segment_ids': [id_video]}],
    apply_captions=apply_captions, complete_query_result=True,
)
```

O helper oficial mapeia tempos da fonte ao corte e velocidade constantes. Ele
recusa curva de velocidade/reverso e não pode recortar uma frase sem tempos por
palavra. Recursos de workspaces diferentes são aplicados separadamente, mesmo
quando têm `resource_id` igual. O resultado preserva avisos e verificações do
builder; falhas parciais e recursos sem vínculo não são ocultados. Se já houver
qualquer legenda no snapshot, esta aplicação é recusada para impedir duplicatas:
use as operações oficiais de revisão, substituição ou preenchimento de lacunas.

A aplicação local não garante que texto ou posicionamento estejam corretos e não
salva o draft. Confira o resultado e então siga `web-collaborative-editing` para
verificar a versão, salvar e obter leitura do servidor. Após push de resultado
incerto, verifique o estado do servidor antes de reaplicar; nunca reenvie a
transcrição paga apenas porque a aplicação ou gravação falhou.

## Aplicar transições

Depois de pesquisar uma transição no catálogo oficial, use a `stdraft_uri`
`vimo://...` fornecida pelo resultado e os IDs dos vídeos do snapshot atual.
`beditor.capcut_transitions.prepare_transitions` utiliza `apply_transition` do
builder oficial para transições entre vídeos contíguos na mesma camada. Ela
verifica limites de duração e impede transições de entrada e saída que ultrapassem
a duração do clipe intermediário, sem deslocar nem cortar os vídeos. Esta versão
recusa snapshots com transições existentes para evitar substituições implícitas.

```python
from beditor.capcut_transitions import prepare_transitions
from apply_materials import apply_transition

result = prepare_transitions(snapshot, package_id, [{
    'from_segment_id': id_video_anterior,
    'to_segment_id': id_video_seguinte,
    'source': uri_retornada_pela_busca,
    'duration_ms': 300,
}], apply_transition=apply_transition)
```

Revise o efeito visual e a continuidade audiovisual. O resultado é um draft
completo local, baseado no `package_id` informado: confira a versão atual e
utilize a skill `web-collaborative-editing` para salvar ou reconciliar conflitos.
Os testes locais não demonstram disponibilidade do efeito nem renderização no
CapCut; a URI vem do catálogo, não de identificadores inventados.

`beditor.capcut_readback.compare` compara o plano com um snapshot lido do
servidor e vínculos atuais. A comparação cobre fonte, cortes, duração, volume e
lettering; mudanças de layer são avisos porque o CapCut pode renumerá-las. A
identidade de `asset://` requer comprovação específica, e reprodução, aparência
e sincronismo percebido continuam exigindo revisão no editor.

Em 12 de novembro de 2026, um teste com um vídeo real de aproximadamente
cinco segundos foi montado pelo adaptador em dois segmentos contíguos com o
áudio da fonte e um lettering. O draft foi salvo, reaberto e as imagens, os
segmentos e o lettering foram observados no editor. A reprodução auditiva,
a qualidade da emenda, a exportação e as demais funcionalidades não foram
confirmadas por esse teste.
