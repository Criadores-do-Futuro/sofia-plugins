# Ponte local CapCut Desktop

Esta é uma rota **opcional e explícita** para a ponte MCP local existente do
bEditor. Ela cria um novo draft Desktop; o plugin oficial CapCut Web segue com
seu próprio fluxo. Não há conversão automática entre os dois.

## Preparar

Instale as dependências de `requirements-editorial.txt` para validar o plano e
`requirements-capcut-desktop.txt` para o cliente MCP Python. Também são
necessários Node, a ponte Desktop compilada, CapCut Desktop instalado e um
projeto vazio compatível com a versão instalada. A ponte exige CapCut fechado.
O SDK usado é o pacote Python `mcp` (faixa `>=2.3,<3`); a versão 2.3.0
estava instalada nesta máquina durante a verificação. A disponibilidade e a
instalação do SDK devem ser conferidas em cada ambiente de destino.
Esta máquina respondeu ao `status` da ponte, mas informou `ready=false`; não
foi criado nem modificado um projeto real nesta verificação.

## Criar pacote e consultar a ponte

```python
from pathlib import Path
from beditor.capcut_desktop import write_package, call_local_bridge

# `plan` é o plano editorial v1 já validado pelo projeto.
package = write_package(plan, Path('/caminho/absoluto/pacote-novo'))
# Caminho do arquivo compilado do servidor MCP fornecido pelo ambiente.
server = Path('/caminho/absoluto/ponte/dist/src/server.js')
status = await call_local_bridge(server, 'status')
prepared = await call_local_bridge(server, 'prepare', package, project_name='Meu vídeo')
preview = await call_local_bridge(server, 'preview', package)
```

O destino deve ser uma pasta nova, dentro de uma pasta existente. A mídia deve
ser local e permanecer disponível. `prepare` gera arquivos no pacote; `preview`
lê o que foi preparado. Confira a prévia e os bloqueios antes de criar o draft.
`status` pronto não prova que o material final ficou correto.

O commit é uma operação **separada**: o chamador passa à chamada `commit` o
`confirmation_token` exato retornado pela ponte, respeitando a autorização já
estabelecida pelo usuário. A ponte verifica o token e seus próprios pré-requisitos:

```python
result = await call_local_bridge(server, 'commit', package, confirmation_token=token_da_previa)
```

O retorno confirma apenas a operação relatada pela ponte. Abra e revise a timeline
no CapCut; exportação e arquivo final precisam de verificação independente.

## Escopo da tradução atual

Somente vídeos locais com áudio original explicitamente declarado, numa pista
contínua, sem lacunas e sem sobreposições; cada segmento tem pelo menos 200 ms.
O plano deve escolher `capcut` e passar a validação editorial. Áudio separado,
J/L cuts, imagens, várias pistas, legendas, lettering e outros efeitos são
recusados por esta tradução. A ponte possui outras capacidades, mas elas ainda
não estão mapeadas do contrato neutro; não devem ser descartadas silenciosamente.
Não há edição de um draft Desktop existente, execução de modelos generativos,
exportação automática ou teste audiovisual completo nesta rota.
