# Arquitetura proposta

## Núcleo editorial

Briefing, público/bolha, ideia central, formato Sofia, análise da fala, planejamento
por momento, justificativas de corte/imagem/som e revisão de pertinência.
O treinamento existente do bEditor é a origem; deve ser inventariado antes de
ser migrado. Não reescrever preferências aprovadas por uma estética genérica.

## Plano de edição independente do host

Um plano versionado representa fontes e intervalos, destino na montagem, camadas,
texto e estilo, assets e procedência, intenção editorial e estado de revisão.
IDs de fonte e do draft precisam de mapeamento explícito. Alterar cortes invalida
os tempos dependentes de legenda, gráficos e som.

O plano é domínio do bEditor; não deve ser enviado como se fosse um contrato
nativo do CapCut. O adaptador traduz apenas operações realmente suportadas.

## Adaptador CapCut

Responsável por sessão, uploads reutilizáveis, montagem, legendas, materiais,
sincronização de versões, gravação, read-back e abertura do projeto editável.
Usar capacidades oficiais disponíveis e validar os contratos atuais.
Não copiar credenciais, pacotes autenticados, SDKs privados ou scripts do plugin
oficial para redistribuição sem permissão/licença correspondente.

Reconhecimento isolado de legendas usa seu fluxo específico. AI Lab só entra
quando o pedido envolve cortar, reestruturar ou montar imagens/vídeos.
Mudanças do usuário no draft precisam ser reconciliadas antes de salvar.

## Adaptador DaVinci Resolve

Usar o MCP registrado somente quando o Resolve e sua API estiverem disponíveis.
Descobrir e verificar operações, timeline e persistência. A configuração MCP
sozinha não comprova edição real; a instalação local do Resolve ainda não foi
encontrada. Descrever diferenças entre o editor e o plano sem apagar informação.

## Geração de materiais

Uma entrada “do zero” produz roteiro/decupagem, especificações de assets e plano
de som. Modelos autorizados geram imagens, vídeos ou áudio, que entram como
materiais na timeline escolhida. Disponibilidade, preço e direitos são registrados.
Motion e 3D em JavaScript podem produzir assets ou uma peça inteira sem geração
de vídeo por IA. Quando a integração não suportar elementos nativos editáveis,
o clipe importado é achatado e mudanças internas exigem novo render. A montagem
final continua no editor escolhido; prévia em tempo real precisa ser comprovada.

## Distribuição por host

O alvo é um núcleo reutilizável com interfaces adequadas a cada ambiente:

| Ambiente | Integração a estudar | Evidência exigida |
| --- | --- | --- |
| Codex | Skill e ferramentas CapCut disponíveis no host | Instalação limpa e edição real |
| Claude Code | Skill/plugin e acesso autorizado ao CapCut | Autenticação, ferramentas e edição real |
| Outro host compatível | Adaptador de ferramentas ou MCP autorizado | Descoberta de capacidades e fluxo completo |

A presença do protocolo MCP não concede acesso automático à conta ou ao backend
do CapCut. A viabilidade de distribuição é uma etapa aberta.

## Qualidade

Revisar separadamente pertinência editorial, integridade de fala/sincronia,
leitura no celular e persistência no CapCut. Uma chamada bem-sucedida não prova
o resultado visual. Registrar a prévia observada e limites de inspeção.
