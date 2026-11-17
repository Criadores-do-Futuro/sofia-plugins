---
description: Só o plano de ritmo — transcript vira plano.json revisado, sem render
allowed-tools: Read, Write, Edit, Bash, Glob
---

Uso: `/sofia-estrategista-editora:plano <arquivo .srt/.json> [pasta-do-projeto]`.

Gere e **revise** o plano de motion de `$1` em `$2` (padrão: `./motion`).

Rode `scripts/plano.py`, depois leia `referencias/catalogo-visual.md` e
`referencias/ritmo.md` e corrija cada plano: `tipo`, `texto` (2–4 palavras, caixa baixa,
a coisa dita e não um resumo), `camera` e `prompt`.

Pare aí. Não gere assets nem renderize. Mostre a tabela final: id, tempo, tipo, texto —
e diga onde você discordou da proposta do script e por quê.
