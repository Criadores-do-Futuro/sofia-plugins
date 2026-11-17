---
name: dashboard
description: Organiza análises em um painel HTML em português brasileiro, consolidando vários vídeos e preservando evidências e limites.
---

# Criar painel

Leia [comportamento](../../comportamento.md). Escreva um único arquivo HTML autocontido, sem scripts nem recursos externos: `lang="pt-BR"`, a meta de viewport e a Content-Security-Policy `default-src 'none'; img-src 'self' data:; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'`. Abaixo do título, uma linha diz que só entram dados observados e que métricas ausentes aparecem como indisponíveis. Não use dados de demonstração.

Inclua material inspecionado, três achados principais, tabela comparativa quando houver vários vídeos, seção por vídeo com fontes, momentos observados, leitura editorial e limitações. Métricas não fornecidas são indisponíveis, não zero. Sem imagem inspecionada, omita conclusões visuais.

Gere um único painel por pedido quando houver criação de arquivos. No painel acumulativo, preserve entradas anteriores e atualize por endereço ou identificador. Escape todo texto externo; use `textContent` para dados, não `innerHTML`, e não injete transcrições em código executável. Não carregue serviços de rastreamento nem publique o arquivo automaticamente.

Salve na pasta escolhida, com referências relativas a imagens existentes. Confira se abre, se os dados são os mesmos da análise e se os links e imagens existem. Sem ferramenta de arquivos, entregue a análise em texto. Mostre o arquivo e três achados, sem afirmar que publicou.
