---
name: beditor
description: Edita takes, áudios e roteiros com a direção editorial do bEditor dentro do CapCut pelo plugin oficial no Codex. Use para decupagem, corte de silêncios e erros, montagem, motion narrativo, B-roll, collage b-roll (colagem editorial de papel e retícula), tela dividida, legendas e revisão de vídeo vertical. Verifica o plugin CapCut e instala ou conecta quando necessário e permitido. Não publica em redes sociais sem pedido explícito.
metadata:
  backend: CapCut
  legacy-claude-effort: high
---

# bEditor no CapCut

O bEditor dirige a edição; o plugin CapCut executa a montagem e mantém o rascunho
editável no CapCut Web. Preserve a voz, o argumento, a identidade do canal e as
decisões já aprovadas. O resultado padrão é um rascunho salvo e aberto para revisão;
um pedido de MP4 só termina quando o arquivo exportado for verificado.

A base criativa é o método e o catálogo de formatos da Sofia, em português
brasileiro. Leia [sofia-no-fluxo.md](referencias/sofia-no-fluxo.md) para dirigir uma
edição completa, planejar visuais ou avaliar narrativa. As ideias do Herk refinam
a execução editorial; não substituem Sofia, os formatos ou o treinamento do dono.

Esta entrada substitui o pipeline local anterior. HyperFrames, Remotion, Gemini,
comandos `/sofia-estrategista-editora:*`, agentes do Claude e a antiga mesa de decupagem não são
pré-requisitos nem rotas automáticas. Os scripts e documentos antigos foram
preservados para consulta e trabalhos que o usuário pedir explicitamente.

## 1. Pré-requisito: plugin CapCut instalado e conectado

Leia [conexao-capcut.md](referencias/conexao-capcut.md) antes da primeira operação
CapCut de cada trabalho. Reutilize uma consulta protegida que já tenha funcionado
neste chat; não abra OAuth em toda edição.

- Exija o plugin `CapCut@CapCut` e as skills que ele fornece. As dependências MCP
  em `agents/openai.yaml` declaram essa necessidade; não são um instalador.
- Se faltar, execute a instalação oficial conforme a referência, dentro das
  permissões e do pedido de edição. Não se limite a devolver comandos ao usuário.
- Se estiver instalado, preserve-o. Falta de ferramenta não é prova de falta de
  instalação: verifique conexão e carregamento antes de reinstalar.
- Use OAuth somente em `capcut_creation`; `capcut_creation_resource` não usa OAuth.
- A skill continua em direção e planejamento quando o host não permite instalar,
  conectar ou acessar mídia; explique a etapa bloqueada sem declarar edição pronta.

## 2. Entender a edição e retomar o estado real

Confirme pelos arquivos e contexto qual mídia, projeto e versão o usuário quer.
Não reabra projetos antigos nem escolha outro rascunho por semelhança de nome.
Quando houver um `CHECKLIST.md` do projeto, leia-o ao retomar e atualize somente
as etapas que efetivamente mudaram.

Use o formato e a marca pedidos, sem forçar uma escolha nova a cada mensagem:

| Pedido | Direção bEditor | Execução CapCut |
| --- | --- | --- |
| Só legenda, transcrição ou SRT | Manter vídeo, duração, ordem, velocidade e áudio | Reconhecimento e pós-edição; nunca AI Lab |
| Cortar, juntar takes ou reestruturar | Decupagem de fala, intenção e ritmo | Rough cut AI Lab; revisão e pós-edição depois |
| Ajustar texto, música, posição, filtro ou B-roll | Preservar a montagem aprovada | Builder atômico sobre o rascunho atual |
| `dinamismo` | Rosto e corte sustentam; sem motion, música ou grade extra salvo pedido | Cortes, hook e legenda discreta; zoom só na ênfase |
| `analise` | Autor e prova visual, com fonte e momento corretos | Composição e materiais conforme capacidade real |
| Motion a partir de fala ou roteiro | Cada visual explica uma ideia; voz contínua | Texto, materiais e mídia na timeline; geração só quando necessária |
| `collage-broll`, colagem de papel ou referência gbro | Uma metáfora por fala, recortes com retícula e montagem de peças sobre papel colorido | Ler [collage-broll.md](referencias/collage-broll.md); ideia → quadros aprovados → animação por keyframes no CapCut |
| Buscar template | Buscar inspiração conforme objetivo e ritmo | Skill `CapCut:search-templates`; cards nativos |

O canvas padrão é 9:16 para Reel/Short; preserve outra proporção quando pedida
ou quando a tarefa for somente legendar a fonte. Não acrescente música, efeitos,
B-roll, cor ou geração a um pedido que só autoriza corte ou legenda.

Estilo visual e formato são escolhas distintas: `collage-broll` pode ilustrar um
trecho de `analise`, motion ou tela dividida, sem trocar o formato inteiro. É uma
opção explícita, não o B-roll padrão de todo vídeo nem um acréscimo automático
ao `dinamismo`. Referência ao repositório `gbro-collage-broll` seleciona essa opção.

## 3. Dirigir sem perder a fala

Em edição completa, leia [direcao-editorial.md](referencias/direcao-editorial.md).
Converta a intenção da Sofia em decisões por trecho, com justificativa, tempos
de origem e de montagem e execução possível no CapCut. Em corte ou legenda
isolados, preserve a estrutura e dispense planejamento criativo adicional.

Antes de cortar, examine duração, dimensões, áudio, orientação e cor da fonte.
HDR exige atenção à prévia; não converta todo vídeo de iPhone por suposição.
Use ferramentas locais para inspeção quando útil, sem torná-las outro renderizador.
Para transcrições, JSONs, logs e medições grandes, prefira context-mode quando
disponível e retorne apenas os trechos necessários. Sua ausência não bloqueia edição.

Registre no projeto, quando houver um, um `edicao/guia-capcut.json` com objetivo,
formato, canvas, fontes, intervalos de origem, cortes propostos, texto, visuais,
marca, restrições e estado de aprovação. Para ajustes simples, o contexto do chat
basta. Guarde os IDs e o progresso conforme [fluxo-capcut.md](referencias/fluxo-capcut.md).

- Transcrição não prova onde cortar: reconhecedores podem omitir gagueiras,
  falsas partidas e frases inteiras. Confira o áudio nos trechos suspeitos.
- Preserve palavras completas e respiração. Para remoção automática de erros,
  mantenha a proteção acústica de 600 ms em cada lado da fala preservada; sem
  espaço suficiente, mantenha o trecho para revisão em vez de cortar fonemas.
  Isso não impõe pausas de 1,2 s entre todas as frases.
- Palavra com duração acima de 2 s é um sinal para ouvir e revisar o trecho,
  não prova automática de erro. Confira nomes próprios e preserve o original
  ao corrigir a transcrição; não invente o texto omitido.
- Boca visível exige áudio e vídeo da mesma ação no mesmo tempo. J/L-cut apenas
  onde a imagem de quem fala não denuncia o deslocamento. Nenhum offset global
  para disfarçar uma emenda ruim.
- No `dinamismo`, zoom responde a ênfase real da voz, é moderado e só se desfaz
  num corte. Não distribua zooms por uma quota por minuto.

Leia [sincronia.md](referencias/sincronia.md) para o critério acústico e
[formatos.md](referencias/formatos.md) para direção por formato. Nessas referências,
comandos de render e mecânicas de scripts são legado; execute no CapCut apenas o
que o plugin representar e descreva limitações sem prometer equivalência.

## 4. Montar, legendar e aplicar visuais

Leia [fluxo-capcut.md](referencias/fluxo-capcut.md) e somente as skills oficiais
necessárias à operação. Não copie SDKs ou scripts do plugin para o bEditor.

- Upload pelo `CapCut:capcut-upload`, reutilizando VIDs e URIs existentes.
- Cortes e estrutura pelo `CapCut:video-editing`, cenário AI rough cut. Preserve
  tarefa, cursor e cards; uma revisão de texto não inicia outro rough cut.
- Legendas pelo reconhecimento automático e builder: reconhecer, conferir,
  aplicar e salvar são etapas diferentes. Não use AI Lab para legenda isolada.
- Texto, legenda, materiais e disposição pelo `CapCut:capcut-stdraft-builder`.
  Atualize elementos existentes em vez de empilhar duplicatas.
- Salvar e abrir a versão atual pelo `CapCut:web-collaborative-editing`; o que
  o usuário salvou no editor prevalece sobre uma cópia local antiga.
- Geração de imagens/vídeos pelo `CapCut:generate-media`. Abra um único card de
  parâmetros e encerre o turno sem texto após o card bem-sucedido. Espere a
  interação; preserve os vínculos, a sessão e as confirmações de créditos.

Para motion, descreva objeto, ação, entrada, desenvolvimento e saída de cada
visual. Texto, números e UI legíveis ficam em elementos editáveis sempre que
possível; imagem gerada não é fonte para fatos ou gráficos. Não gere mídia
apenas para testar conexão nem para preencher automaticamente toda pausa.

Use [hook.md](referencias/hook.md), [galeria-estilos.md](referencias/galeria-estilos.md),
[linguagem-visual.md](referencias/linguagem-visual.md) e
[sugestao-de-motion.md](referencias/sugestao-de-motion.md) somente quando o pedido
envolver essa direção. Aproveite critérios e valores medidos; chamadas a scripts,
renderizadores e agentes nesses textos não substituem o fluxo CapCut.
Leia [procedencia.md](referencias/procedencia.md) para fontes e integridade.

O plugin não garante todas as composições, keyframes, máscaras, tracking e
transições do motor antigo. Confira a função documentada antes de prometer um
efeito; ofereça uma alternativa suportada ou a etapa manual no CapCut. Não
automatize o app desktop ou a interface Web para contornar função ausente.

## 5. Revisar e entregar com evidência

Leia [qualidade-capcut.md](referencias/qualidade-capcut.md). Em uma edição completa,
revise primeiro corte, depois visuais e acabamento, preservando as aprovações já
recebidas. Pedido direto de ajuste ou legenda não exige um novo ciclo de aprovação.
Cards de plano e de cobrança seguem o protocolo próprio do plugin.

Revise também a pertinência segundo Sofia: o público entende a ideia, a imagem
acrescenta algo e a promessa encontra entrega no material? Validação estrutural
não responde a isso. Registre a correção no projeto; para transformá-la em regra
durável da skill, use apenas autorização explícita do usuário, preservando escopo
por formato e distinguindo preferência, observação e hipótese de desempenho.

Após salvar, abra/reutilize o editor da sessão e descreva o que mudou e o que foi
verificado. Termine cada entrega de rascunho salvo com o link `web_editor_url`,
usando o rótulo `web_editor_text` devolvido, sem inventar URLs. Rascunho salvo
não é MP4 exportado; sem exportação comprovada, declare esse estado claramente.

Não publique, agende, apague originais ou mova arquivos para a Lixeira como
consequência de editar. A antiga automação de limpeza de Downloads não se aplica
ao novo fluxo. Use pastas existentes em `~/.config/beditor/config.json` para
artefatos grandes; se o disco externo não estiver montado, peça a montagem e não
crie um substituto no disco interno. Não guarde credenciais nos registros.

## Recursos preservados

[legado-local.md](referencias/legado-local.md) guarda integralmente a entrada
anterior, inclusive alterações locais anteriores à migração. Consulte apenas para
recuperar decisões editoriais ou quando o usuário pedir o fluxo local. Os demais
scripts, templates, testes e referências continuam no lugar; não são evidência
de que o plugin CapCut implementa aqueles recursos. A revisão padrão passa a
acontecer no editor colaborativo do CapCut.
