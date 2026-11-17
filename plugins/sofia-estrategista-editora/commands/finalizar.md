---
description: Etapa 3 — cama musical, legenda, grade e master. Entrega o vídeo pronto para o editor decidir se posta.
allowed-tools: Read, Write, Edit, Bash, Glob
---

Argumentos: `$ARGUMENTS` = caminho do take bruto. Pré-requisito: `edicao/aprovado/motion`
existe (etapa 2 aprovada).

1. `python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/montar.py --etapa final --guia guia/guia.json --fatos guia/fatos.json --take <take> --falas <take>.whisper.json --projeto edicao/motion --edicao edicao`
   Isto acrescenta ao que já foi aprovado: cama por momento (`trilha.py`, volume calculado
   por LUFS), legenda, e a grade da identidade (bloom, aberração, vinheta, grão, curva).
2. O script termina medindo (`medir.py`: preto, cobertura, loudness, separação da cama).
   Se `FALHOU`, corrija a causa e rode de novo — nunca mostre preview reprovado como pronto.
3. Entregue `edicao/motion/out/preview.mp4` com o resultado da medição.

   **Todo render que o editor vai assistir vai para o SSD**, não fica só na pasta de
   trabalho — `edicao/` guarda proxy, pedaços e passadas, que ninguém quer ver:
   `python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/entregar.py --arquivo <render> --projeto "<nome da pasta do projeto>" --etapa corte|motion|preview|master`
   Vai para `<SSD>/Entregas/<projeto>/revisao/`, datado. Se o volume não estiver
   montado o script para e diz — nunca escreva num caminho de volume ausente, que
   cria uma pasta parecida no disco interno e o arquivo some da vista.
4. Ajustes desta etapa:
   - "a música está alta/baixa" → `musica.cama` do momento (`sobe`/`desce`/`mantem`/`some`)
     ou o clima em `trilha.py`; o volume base sai do LUFS medido, não do palpite.
   - "a legenda atrapalha aqui" → `legenda: false` no momento.
   - "quero mais/menos grão, menos vinheta" → a grade em `compor.py`, que é a mesma de
     `referencias/linguagem-visual.md`; mudar ali muda a identidade, avise antes.
5. Aprovado para postar, renderize o master em qualidade máxima.

   **Master 4K** (só quando o take chega em 2160×3840 — acima disso é ampliação):
   monte a cadeia na altura cheia antes, senão o A-roll de 1920 é reaproveitado e
   o "4K" é upscale disfarçado:
   `montar.py --etapa final --altura 3840 --sem-preview …`
   `legenda_hf.py --projeto edicao/motion --escala 0.5 --resolucao portrait-4k`
   `compor.py --projeto edicao/motion --escala 1.0 --crf 18 --out edicao/motion/out/master.mp4`

   Em 1080×1920 basta a última linha, com a legenda em `--escala 1.0`.

   Só depois do editor aprovar **o master**, e não o preview, ele vai para o espaço
   dos finais:
   `entregar.py --arquivo edicao/motion/out/master.mp4 --projeto "<projeto>" --etapa master --aprovado`
   → `<SSD>/Entregas/_APROVADOS/`. Sem `--aprovado` ele fica em `<projeto>/master/`,
   que é onde mora master ainda não julgado. **`_APROVADOS` é só do que foi aprovado
   em voz alta** — encher aquela pasta de candidato tira dela a única coisa que ela
   tem de útil, que é ser confiável.
   e entregue o arquivo. Se o editor disser que não posta, volte à etapa que ele apontar.

Sempre com vigia: processo sem progresso por 4 min é morto e investigado, nunca esperado.
