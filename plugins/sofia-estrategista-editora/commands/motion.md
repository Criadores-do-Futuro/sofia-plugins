---
description: Do transcript ao MP4 — roda o fluxo completo do bEditor
allowed-tools: Read, Write, Edit, Bash, Glob
---

Uso: `/sofia-estrategista-editora:motion <arquivo .srt/.json> [pasta-do-projeto]`.

Rode o fluxo completo do bEditor sobre `$1`, entregando na pasta `$2` (padrão: `./motion`).

Siga a skill **bEditor** na ordem: ritmo → revisão do plano → assets → composição →
render → validação. Não pule a revisão do plano: é a etapa onde você decide *o que se vê*,
e o script só propõe.

Ao terminar, mostre: quantos planos, a distribuição por classe, o que ficou pendente
(asset, licença, fonte de número) e o caminho do MP4.
