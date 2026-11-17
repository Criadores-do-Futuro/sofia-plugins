---
description: Dirige a edição de um take — folhas de contato, agente diretor, guia validado, GUIA.md para leitura. Para antes de qualquer render.
---

Argumentos: `$ARGUMENTS` = caminho do take bruto (`.mov`/`.mp4`). O transcript
por palavra fica ao lado, com sufixo `.whisper.json`; o roteiro em
`roteiro/*.md` na raiz do projeto, se houver.

0. `python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/sdr.py <take>` — take de iPhone é HLG, e HLG copiado para H.264 de 8 bits sai com a pele lavada. O script converte uma vez (ou só confirma que já é SDR) e imprime o caminho a usar: **daqui em diante, em todos os comandos, `<take>` é esse caminho** (`brutos/take.sdr.mov`). O `.whisper.json` do bruto vale para ele, porque o relógio é o mesmo, e o script deixa o link `take.sdr.whisper.json` pronto.
1. `python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/contato.py --take <take> --falas <take>.whisper.json [--roteiro roteiro/<arquivo>.md] --out guia/`
2. Despache o agente `diretor` com: "Leia `guia/` (todas as folhas `contato-NN.jpg` com Read) e `roteiro/`, escreva `guia/guia.json` e rode o validador até zero erros."
3. `python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/validar.py guia/guia.json --contato guia/contato.json` — se falhar, devolva os erros ao agente; três rodadas sem convergir, mostre `guia/PENDENTE.md` ao editor e pare.
4. `python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/gerar_guia_md.py guia/guia.json --out guia/GUIA.md`
4b. **Sofia lê o guia antes do editor.** Padrão desde 2026-09-12, por decisão do dono: *"quero que o padrão do bEditor seja usar a sofia pra fazer vídeos melhores"*. Invoque a skill `sofia:critica` com o `GUIA.md` — arco, estrutura, o que fica e o que sai, e a ideia de motion de cada momento. Diga a ela que o take **já está gravado**: o que está em julgamento é o corte e a escolha de imagem, não a escrita da fala. As trocas que valerem a pena vão junto no passo 5, para o editor decidir uma vez só em vez de descobrir na revisão do master.
5. Mostre ao editor: arco, estrutura, densidade, correções suspeitas, o `GUIA.md` e o que a Sofia apontou. Se o take tiver energia baixa, fim de frase engolido ou voz mudando de volume, junte as dicas de `skills/beditor/referencias/voz.md` (seção "Antes de gravar"), para valerem no **próximo** take. **Pare aqui.** Nada é renderizado antes de o editor ler o guia. Mudanças pedidas no chat entram no `guia.json` e o `GUIA.md` é gerado de novo.
