# Plano de desenvolvimento

## 1. Reconstruir a base existente

Inventariar repositórios, clones duplicados, licenças e capacidades comprovadas.
Mapear o bEditor ativo, seu treinamento e a fonte Sofia sem mover projetos ativos.
Conflitos identificados: dinamismo usa legenda discreta e não adiciona música ou
motion por padrão; não importar as regras contrárias de versões antigas.
Selecionar ideias e componentes pelo benefício concreto para a timeline CapCut.

## 2. Provar a integração

Em um projeto de teste autorizado: enviar uma gravação, montar um corte simples,
aplicar legendas, salvar, reabrir e revisar a mesma timeline. Registrar limites
de materiais, keyframes, transições, máscaras e exportação efetivamente acessíveis.
Comparar a ponte MCP local já existente em `bEditor/mcp/capcut-bridge` com a rota
oficial Web. O README da ponte descreve criação de projeto novo com CapCut fechado;
validar separadamente o ciclo de alterar a mesma timeline e exportar.

## 3. Implementar o núcleo

Plano de edição versionado, tradução para operações CapCut, persistência de
sessão/versão, retomada segura e prevenção de elementos duplicados.

## 4. Implementar os dois percursos

- **Gravação pronta:** decupagem → montagem → legendas/visuais → revisão no CapCut.
- **Do zero:** briefing Sofia → roteiro → assets autorizados → montagem → revisão.

## 5. Empacotar e validar por host

Distribuir instruções e ferramentas com permissões e autenticação documentadas.
Testar instalação limpa em cada host antes de anunciar suporte.

## Critérios para declarar o produto funcional

- Uma gravação vira projeto editável salvo no CapCut, com fonte preservada.
- Um briefing gera materiais autorizados e os monta em um projeto CapCut.
- Um pedido de revisão altera os elementos corretos no mesmo draft.
- Mudanças feitas pelo usuário no editor sobrevivem à rodada seguinte.
- A inspeção confirma fala completa, sincronia, legenda e composição.
- MP4 só é anunciado quando a exportação e o arquivo forem verificados.
- Custos, operações não suportadas e compatibilidade têm evidência explícita.

## Aprendizado de estilo e animação

- Decodificar todos os quadros com PTS, guardar cobertura e falhas; analisar áudio
  completo e registrar evidências por tempo, sem confundir medições com semântica.
- Construir manual versionado com cortes, J/L-cut, legenda, lettering, cor,
  movimento, máscaras, transições e som: medido, inferido ou indisponível.
- Implementar fontes de motion/3D em JavaScript e geração por IA, preferindo
  elementos nativos editáveis quando disponíveis e mantendo fonte do clipe.
- Testar prévia, alterações e persistência em cada editor; contabilizar quais
  efeitos precisam ser renderizados e não prometer fidelidade perfeita.

Estado: o fluxo básico CapCut Web foi testado em draft sintético com vídeo,
lettering, áudio em pista própria e revisão salva. A análise técnica cobre quadros
e trilhas e permite transcrição local. Ainda faltam provar análise audiovisual
semântica abrangente, legendas e transições na nuvem, sincronização concorrente,
exportação e uso com material real; DaVinci permanece sem teste real nesta máquina.
