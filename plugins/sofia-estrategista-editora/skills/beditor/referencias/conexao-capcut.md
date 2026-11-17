# Pré-requisito e conexão do CapCut

O bEditor exige o plugin oficial `CapCut@CapCut` para executar edições no CapCut.
Não exige Gemini, Claude, HyperFrames, app desktop CapCut ou uma chave de API
colada no chat. A conta é conectada pelo OAuth do plugin. Não prometa gratuidade:
legendas e geração têm elegibilidade e cobrança determinadas pelo serviço.

## Identificar o ambiente e a instalação

Use a lista de skills carregadas para localizar o plugin instalado, sem fixar
um caminho de cache nem escolher a versão mais alta por nome de pasta. As skills
necessárias são `mcp-auth`, `capcut-upload`, `video-editing`,
`web-collaborative-editing`, `capcut-stdraft-builder` e, quando aplicável,
`generate-media` ou `search-templates`.

Opcionalmente execute `scripts/capcut_status.py` a partir da pasta desta skill:

```sh
python3 <beditor>/scripts/capcut_status.py
```

O script é somente de leitura: identifica o CLI nativo, inventaria o plugin e os
dois servidores e verifica os helpers gerenciados. Não inicia OAuth, não baixa
arquivos, não altera configuração e não lê credenciais. `--codex-cli` permite
informar o executável absoluto confirmado como pertencente ao host ativo.
`ready` indica instalação local verificada, **não** conta autorizada nem teste
de edição. Um CLI encontrado apenas no PATH exige confirmar que é o do host
Desktop antes de passá-lo explicitamente. Não use WSL para instalar no Windows.

Ausência no catálogo de ferramentas do chat pode ser apenas catálogo desatualizado.
Use descoberta nativa pelo sufixo exato da ferramenta necessária; ferramentas
diretamente expostas também contam. Um inventário local de um executor pode ser
incompleto. Não reinstale para consertar o catálogo de um chat.

## Se o plugin não estiver instalado

O pedido de usar o bEditor no CapCut autoriza preparar essa dependência quando
o host e suas permissões permitirem. Siga o instalador oficial, sem implementar
um segundo instalador nem registrar servidores manualmente:

1. Confirme que a execução é na mesma máquina do Codex Desktop. Sem acesso local
   ao host, entregue o planejamento e a orientação exata para continuar no Desktop.
2. Crie um diretório temporário único do sistema. Baixe por HTTPS e leia **inteiro**:
   [SKILL.md oficial de instalação](https://sf16-sg.tiktokcdn.com/obj/eden-sg/962370eh7nupenuhbo/capcut_codex_plugin/SKILL.md).
   Mantenha a cópia somente nesse temporário. Não instale esta skill remota como
   uma segunda skill local nem fixe a URL/versionamento de um ZIP aqui.
3. Execute o runbook lido: inventário antes de download, staging, preservação da
   instalação anterior, registro com CLI absoluto, verificação e rollback quando
   necessário. Respeite a política do host; não use sudo nem contorne permissões.
4. Termine a autorização e teste protegido; limpe os temporários do instalador.
   Retome a edição original em vez de oferecer onboarding ou abrir rascunho vazio.

Se o plugin já estiver instalado, use a skill `CapCut:mcp-auth` para versão e
recuperação. Um upgrade encontrado durante recuperação não autoriza substituir
a instalação sem o acordo específico exigido por essa skill. Não desinstale
plugins com outro marketplace nem modifique arquivos do plugin oficial.

## Confirmar conexão

Se uma ferramenta protegida já funcionou neste chat, reutilize essa evidência.
Caso contrário, prefira a busca de leitura que o usuário já pediu. Sem outra
consulta útil, `search_capcut_material(type="font", prompt="font", top_n=1)` é
um teste de leitura, sem geração ou alteração de rascunho.

Se a ferramenta faltar ou falhar por autenticação, leia `CapCut:mcp-auth` e use
seus helpers instalados. `check-connection.mjs --codex-cli <cli-absoluto>` verifica
a conexão sem iniciar login; não confunda `codex mcp get` ou status enabled com
autorização. Use o CLI absoluto escolhido para todo o fluxo.

Quando login for necessário, execute `capcut-login.mjs` conforme a skill oficial.
Abra apenas a URL exata emitida pelo helper no navegador interno do Codex; deixe
login e consentimento ao usuário. Mantenha o mesmo processo vivo e acompanhe-o
com esperas de até 60 s. Leia a página para detectar erros. Só reporte sucesso
com `event=completed`, `success=true` e saída 0; silêncio ou página aberta não
comprovam conexão. Cancelamento encerra o helper e seu listener.

Não abra OAuth para `capcut_creation_resource`. Não peça cookies, códigos,
tokens, cabeçalhos ou acesso ao armazenamento do navegador. Não use o login
do app desktop nem `codex mcp login` como substitutos do helper.

Siga as recuperações específicas da skill oficial para callback recusado,
`unknown client`, token expirado e HTTP 502. Não converta erro de upload local
em erro OAuth nem entre em um ciclo de reinstalação/login.

## Ferramentas ausentes com conta conectada

Siga o handoff definido por `CapCut:mcp-auth`, dentro da autorização do usuário
e das regras do host para chats. Preserve objetivo, arquivos, fontes, rascunho,
versão, tarefas, cursores, lotes e cards. Se autorizado, faça fork no mesmo
diretório, envie o pedido e progresso e abra o filho. Não repita upload, edição,
legenda ou geração já enviados. Se o host exigir autorização que a conversa não
forneceu, peça apenas essa autorização; uma skill não amplia permissões.

Não anuncie handoff concluído antes de enviar a continuação e abrir o filho.
Se já existir um filho, recupere-o; não crie forks repetidos. Quando indisponível,
informe a limitação e forneça o pedido de continuação completo.
