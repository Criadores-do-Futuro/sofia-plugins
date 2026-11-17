---
description: Etapa 4 — título, descrição e capa otimizados para busca e clique, e um agendamento só para todas as redes (Zernio ou Metricool). Nada é publicado sem o sim do editor.
---

Argumentos: `$ARGUMENTS` = o master aprovado (`entrega/…mp4`). Pré-requisito: `/sofia-estrategista-editora:finalizar` concluído e aprovado. Leia `${CLAUDE_PLUGIN_ROOT}/skills/beditor/referencias/publicacao.md` antes de escrever qualquer texto.

1. Escreva `entrega/publicacao.json` a partir de `guia/GUIA.md`, do transcript e de `guia/fatos.json`: `video` (o master), `fonteCapa` (o A-roll sem legenda, `edicao/aroll.mp4`), `palavraChave`, `capa` (`t`, `linhas`, `destaque`), `redes` (uma entrada por rede que o editor usa, com `titulo`/`descricao`/`tags` no YouTube e `legenda` nas outras) e `agendamento` (`quando`, `fuso`, `contas`). Se não souber quais redes e contas, pergunte uma vez.
2. `python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/publicacao.py entrega/publicacao.json --capa` — erro para e se corrige no json; aviso vai para o editor junto com a proposta.
3. Mostre ao editor: a capa (`entrega/publicacao/capa.jpg`), o título, a primeira linha de cada rede, o horário e o provedor. Ofereça de uma a duas alternativas de título. **Pare aqui.**
4. Com o sim explícito, publique pelo MCP disponível:
   - **Zernio:** envie o vídeo e a capa uma vez (upload de mídia) e troque `{{URL_DO_VIDEO}}`, `{{URL_DA_CAPA}}` e os `{{CONTA_*}}` no `entrega/publicacao/zernio.json`. Se houver TikTok, rode antes com `dryRun`. Depois crie **um** post com esse corpo e um `x-request-id` fixo.
   - **Metricool:** leia o schema da ferramenta de agendamento. Se ela aceita várias redes num post, é uma chamada só; se não aceita, diga ao editor quantas chamadas serão antes de fazer.
   - Nenhum dos dois conectado: entregue `publicacao.json`, `zernio.json` e a capa para o editor agendar à mão, e diga que o MCP não está conectado.
5. Registre em `entrega/publicacao/agendado.json` o id devolvido, as redes, o horário e o provedor.
