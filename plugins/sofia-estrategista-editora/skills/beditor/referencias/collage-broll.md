# Collage B-roll no CapCut

Opção visual `collage-broll` do bEditor. Ative quando o usuário pedir collage
B-roll, colagem de papel, colagem editorial com retícula, ou citar
`gbro-collage-broll`. Um pedido para adicionar este estilo à skill não autoriza
gerar imagens, enviar mídia ou gastar créditos como demonstração.

## Origem e adaptação

Referência estudada: [pyang5166/gbro-collage-broll](https://github.com/pyang5166/gbro-collage-broll),
commit `a1a4ee2e2abf7d44e460026b706d0c72c2cf8a91`, consultado em 2026-10-26.
Direção e protocolo adaptados do `SKILL.md` sob MIT; aviso preservado em
[collage-broll.LICENSE](collage-broll.LICENSE). A licença é dessa referência,
não uma mudança de licença do bEditor nem autorização sobre assets de terceiros.

O projeto original usa imagem no Codex e vídeo Gemini Omni Flash. Aqui, tanto
quadros quanto animação usam `CapCut:generate-media`, e a inserção usa o builder
e a sessão colaborativa existentes. Não instale o repositório como outra skill,
não rode seus scripts de setup/Gemini, não peça `GEMINI_API_KEY`, não crie venv
Omni e não retorne a HyperFrames quando o modelo errar.

As duas revisões criativas abaixo pertencem a este estilo para evitar animar uma
ideia errada. Reutilize aprovações explícitas da conversa. Elas não substituem
cards de parâmetros ou confirmações de créditos exigidos pelo CapCut.

## Assinatura visual

- Uma frase/ideia visual por insert, geralmente em torno de 5 s, ligada à fala.
- Fundo plano de papel colorido, com textura fina de fibra; deixe área negativa.
- Recortes fotográficos em preto e branco com pontos de retícula visíveis.
- Cartolina colorida apenas para hierarquia e peças importantes; borda fina
  creme, corte nítido e sombras de contato suaves, com pouca opacidade.
- Em geral 3–6 grupos grandes e separáveis. Relação entre objetos explica o
  argumento; não ilustre cada substantivo com outro adesivo.
- Câmera fixa. Peças deslizam, encaixam e conectam em passos com ritmo de
  stop-motion. Começam num campo vazio e terminam na composição completa.
- Sem simples fade-in do cartaz inteiro, zoom lento, deriva de câmera, morphing
  contínuo, 3D brilhante ou cenário fotográfico realista.
- Sem texto, número, UI, marca d'água ou logo gerados dentro da colagem. Hook
  e legendas necessários pertencem a camadas editáveis do projeto.

Cor serve ao significado e à marca: laranja/vermelho pode apoiar urgência e
trabalho; amarelo, ferramenta ou alerta; verde, cognição; roxo, memória; teal,
cooperação. São possibilidades, não um dicionário obrigatório. Não use azul em
todas as cenas por inércia. Uma série compartilha textura e linguagem, com
variação de fundo quando fizer sentido. Marca aprovada prevalece.

## 1. Propor a metáfora

Sem gerar mídia, apresente por item: fala e intervalo-alvo, significado,
emoção, metáfora em uma frase, objetos, fundo/acentos e ordem de montagem.
Exemplo: para conhecimento que se perde a cada tarefa, fichas caem de uma
esteira para uma caixa furada; ao final resta uma única ficha. O movimento
precisa explicar perda, não apenas pôr uma caixa ao lado da palavra conhecimento.

Espere a confirmação da metáfora antes de gerar quadros, salvo se o usuário já
aprovou exatamente essa proposta. Num lote, avance somente os itens aprovados;
os demais permanecem em revisão. Pedido apenas de prompt termina no texto.

## 2. Preparar e revisar os quadros

Registre no guia local ou em `visual-spec.json`, quando houver projeto:
`id`, `fala`, `intervalo_alvo_ms`, `significado`, `metafora`, `proporcao`,
`fundo_hex`, `acentos`, `objetos` com função/posição/movimento, `ordem_montagem`,
`composicao_final`, `evitar` e aprovação por item. Não grave esses campos no
STDraft. Retenha versões de quadros e IDs de mídia já produzidos.

Leia `CapCut:generate-media` para imagens. Peça um quadro final por conceito
(`count:1`), na proporção do insert, com a metáfora aprovada, fundo, textura,
grupos, hierarquia e exclusões acima. Não peça contato de várias cenas dentro
da própria imagem de referência. O modelo é escolhido no card compatível do
plugin; um modelo explícito do usuário prevalece.

Abra exatamente um card de imagem por turno e encerre sem texto após o card.
Espere a interação para gerar, siga cobrança e polling, mostre o resultado.
Não chame `image_gen`, Gemini ou outro provedor para preencher esta etapa.

Prepare também a imagem de abertura: papel vazio na mesma proporção, cor e
textura, sem objetos. Reutilize um quadro vazio aprovado ou fornecido; se for
necessário gerá-lo pelo CapCut, trate-o como outra solicitação de imagem com
card próprio. Não invente URI nem considere um prompt de cor uma imagem pronta.
Conferir cor uniforme e ausência de peças é necessário antes de animar.

Apresente os quadros resultantes e identifique cada conceito. Revise clareza
da metáfora, grupos distinguíveis, recorte/retícula, cor, espaço vazio e ausência
de letras falsas. Espere aprovação dos quadros antes da animação. Um card
confirmado para gerar imagem não é aprovação do resultado nem do vídeo seguinte.
Revisões parciais preservam o que já foi aprovado.

Se houver arquivos locais e ferramenta de contato disponível, uma folha numerada
ajuda em lotes. Sem isso, use os resultados nativos identificados; não declare
que uma folha foi criada ou peça upload repetido de imagem já disponível.

## 3. Animar a montagem no CapCut

Leia `CapCut:generate-media` e sua referência de vídeo. Use os recursos reais
dos dois quadros: abertura como `first_frame`, composição aprovada como
`last_frame`, `reference_mode:"keyframes"`. Reutilize ImageX URIs existentes;
arquivos locais ainda não enviados seguem `CapCut:capcut-upload`. Não misture
keyframes com referências Omni no mesmo pedido.

Prefira 5 s, proporção do insert (9:16 quando não houver outra), `720p` e
`count:1`, usando um modelo compatível do catálogo CapCut. São valores iniciais
para o card, não garantias sobre o arquivo recebido. Não envie o nome Gemini
Omni Flash a uma ferramenta que só aceita modelos CapCut.

Escreva no prompt: plano único fixo; fundo inicial vazio; sequência específica
de entrada, encaixe, conexão e resultado para cada grupo; composição final
correspondente ao quadro aprovado; retenção final para leitura; mesma cor,
retícula, textura e bordas; sem objetos extras, cortes, zoom, morphing ou texto.
Peça ausência de som, mas confira o resultado: modelos 2.x do plugin podem
produzir áudio nativo, sem controle de desligamento no card.

Mostre um card de vídeo, encerre sem texto e espere. Aprovação dos quadros
permite preparar esse card, não confirmar cobrança pelo usuário. Preserve
`generate_id`, vínculo do card, chave retornada e tarefa lógica; acompanhe até
liquidação, renderize os resultados e reporte créditos reais. Não regenere
automaticamente uma série inteira para corrigir um item.

## 4. Inserir e conferir

Continue na sessão do projeto. O fluxo oficial de geração incorpora resultados
à timeline: retenha IDs dos segmentos de quadros e vídeo criados, para não
adicionar uma segunda cópia. Para inserir sobre a fala, use as funções oficiais
de posição/camada e áudio; preserve o A-roll e sua voz. Silencie o som do B-roll
na timeline quando necessário. Isso não prova que o arquivo fonte tem zero
trilhas de áudio.

Quadros usados só para preparar a animação não devem sobrar no corte final.
Remova/realoque apenas os segmentos temporários identificados deste fluxo,
preservando as fontes reutilizáveis e todo conteúdo anterior. Remover não faz
ripple automático: confira duração e lacunas. Não substitua o snapshot atual
por um seed antigo. Salve e entregue conforme `fluxo-capcut.md`.

Para tela dividida, o collage ocupa o apoio na região pedida; não transforme
toda a edição em tela cheia. O enquadramento e as legendas seguem o formato.
Um vídeo gerado é um clipe achatado; as peças internas não viram camadas
editáveis apenas porque ele foi importado no CapCut.

QA: examine início, pelo menos um momento de cada entrada e final. Com arquivo
local disponível, extraia frames para uma folha por segundo e compare a última
imagem ao quadro aprovado usando ferramentas de inspeção, sem mudar o motor de
geração. Sem acesso a frames, revise a prévia possível e informe o limite.

- Início vazio ou desvio explicitamente aceito; as peças entram uma a uma.
- Movimento e objeto comunicam a metáfora; sem fade global ou zoom substituto.
- Final preserva a relação aprovada. Variação pequena que não muda o sentido
  não exige nova geração; erro semântico volta à revisão do item.
- Sem letras falsas, logos, água ou 3D indevido; voz preservada na montagem.
- Confira duração, proporção, resolução e áudio reais. Não prometa 24 fps ou
  MP4 sem trilha de áudio: o plugin não expõe os controles equivalentes ao
  script original. Exportação e inspeção do arquivo são etapas distintas.

Esta opção adiciona direção visual e o fluxo de geração no CapCut. Não pressupõe
um resultado já renderizado/testado. Precisão absoluta de camadas ou keyframes
pode exigir uma etapa manual no editor; não troque de motor silenciosamente.
