---
description: Monta o vídeo a partir do guia aprovado — enriquecedor, corte, A-roll, voz, cama, planos, assets, preview medido.
---

Argumentos: `$ARGUMENTS` = caminho do take bruto. Pré-requisito: `guia/guia.json` validado e lido pelo editor.

1. Despache o agente `enriquecedor` com: "Leia `guia/guia.json`, confirme os momentos com `precisaDeFato` e as correções, escreva `guia/fatos.json`."
2. Se `edicao/motion` não existir, crie o projeto Remotion: `bash ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/projeto.sh edicao/motion`.
3. `python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/montar.py --guia guia/guia.json --fatos guia/fatos.json --take <take> --falas <take>.whisper.json --projeto edicao/motion --edicao edicao`
4. O `montar.py` termina com a medição. Se `FALHOU`, corrija a causa apontada (plano, asset, guia) e rode de novo; não mostre preview reprovado como pronto.
5. Entregue `edicao/motion/out/preview.mp4` e os avisos. O render final é decisão do editor:
   `python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/compor.py --projeto edicao/motion --escala 1.0 --crf 18 --out edicao/motion/out/master.mp4`
   (o compositor do plugin: Pillow + ffmpeg, sem navegador). Sempre com vigia: se o processo ficar 4 min sem escrever no log, mate e investigue — nunca espere.
