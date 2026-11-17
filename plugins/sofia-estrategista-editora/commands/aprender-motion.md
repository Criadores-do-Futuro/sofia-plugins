---
description: Aprende um estilo novo de motion graphics a partir de uma pasta de frames ou vídeos
allowed-tools: Read, Write, Edit, Bash, Glob, Agent
---

Uso: `/sofia-estrategista-editora:aprender-motion <pasta> <nome-do-estilo>`.

Aprenda o estilo visual de `$1` e registre-o como `$2`.

Rode `scripts/aprender.py` (use `--videos` se a pasta tiver vídeos, `--frames` se tiver
imagens). Depois **abra as folhas de contato e olhe** — ou despache o agente
`analista-de-estilo`, que faz a leitura e preenche o `medicoes.json`.

Ao terminar, mostre: onde o preto assenta, onde o branco é segurado, vinheta, grão,
paleta, quantos grupos saíram e o que cada um é. Diga explicitamente quais números são
medida direta e quais são aproximação — o campo `confianca` do JSON separa os dois.

Termine com o comando pronto para usar o estilo:
`plano.py --falas <arquivo> --out motion/ --estilo estilos/$2/medicoes.json`
