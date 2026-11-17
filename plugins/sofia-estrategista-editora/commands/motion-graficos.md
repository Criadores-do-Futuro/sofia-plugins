---
description: 'Etapa 2 — motion graphics sobre o corte aprovado. Sem música, sem legenda, sem grade: o editor julga a ideia e o timing.'
allowed-tools: Read, Write, Edit, Bash, Glob, Task
---

Argumentos: `$ARGUMENTS` = caminho do take bruto. Pré-requisito: `edicao/aprovado/corte`
existe (etapa 1 aprovada). Se não existir, avise e pergunte antes de gastar geração.

1. Se `guia/fatos.json` não cobre os momentos com `precisaDeFato` do guia atual, despache
   o agente `enriquecedor`: "Leia `guia/guia.json`, confirme os momentos com
   `precisaDeFato` e as correções, escreva `guia/fatos.json`."

1b. **Sofia lê as ideias antes de gastar render.** Esta etapa é padrão desde
   2026-09-12, por decisão do dono: *"quero que o padrão do bEditor seja usar a sofia
   pra fazer vídeos melhores"*. Invoque a skill `sofia:critica` passando, de cada
   momento com motion, **a fala e a `motion.ideia` lado a lado**, mais os trechos que
   ficaram só com rosto e os buracos sem rosto. Peça o diagnóstico e, em paralelo,
   despache os agentes `sofia:analista-de-principios` (bloco a bloco, princípio
   nomeado) e `sofia:critico` (o que derruba, primeiro). O material precisa incluir:
   público, objetivo, plataforma, duração de cada plano e o fato de que **o áudio está
   congelado** — só as imagens mudam.

   A pergunta que a Sofia responde, e que nenhum validador responde: *a imagem
   acrescenta informação que a fala não dá, ou só repete a fala em desenho?* Uma ideia
   que pode ser descrita com as mesmas palavras do áudio não está ilustrando, está
   legendando — e legenda o vídeo já tem.

   Leve as trocas ao editor **antes** de renderizar: cada uma vira `motion.ideia` (e,
   quando muda o desenho, `motion.tipo` e `dados`) no `guia.json`, seguida de
   `validar.py`. O ganho medido na primeira vez que isso rodou: três dos oito planos do
   pitch eram ilustração redundante, um contradizia a fala (a voz dizia Metricool e
   Zernio, a tela mostrava Instagram, TikTok e YouTube) e o plano mais importante do
   vídeo escrevia a regra em vez de mostrá-la acontecendo. Como briefar e o que fazer
   com o que volta: `referencias/sofia-no-fluxo.md`.
2. `python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/montar.py --etapa motion --guia guia/guia.json --fatos guia/fatos.json --take <take> --falas <take>.whisper.json --projeto edicao/motion --edicao edicao`
   (a chave de imagem vem do ambiente: `set -a && source ~/.config/beditor/env && set +a`
   antes de rodar; ela nunca aparece na conversa nem em log.)
   O corte aprovado é reaproveitado: `aroll.mp4`, `fonte.mp4` e `voz.m4a` só são refeitos
   se a tabela de corte mudou.
3. Entregue `edicao/motion/out/motion.mp4`, a direção de motion do vídeo e o prompt de
   cada cena (`edicao/motion/CENAS.md`, também no fim do `guia/GUIA.md`). Diga o que ficou pendente: asset que falhou, retrato sem licença,
   número sem fonte.
4. Ajustes por momento, executados no guia e regerando **só o que mudou**:
   - "a imagem do M43 não é isso" → reescreva `motion.ideia` do M43 e rode
     `assets.py --projeto edicao/motion --so M43` (a imagem antiga é descartada sozinha:
     cada asset guarda o prompt que o gerou em `M43.prompt.txt`).
   - "o M34 devia ser uma cena, não um ícone" → a ideia descreve a cena inteira
     (`referencias/prompts-assets.md`: cena fotográfica com lente e luz, quadro cheio).
   - "entra cedo demais" / "sai antes da hora" → `entraAntesMs`, `entrada`, `saida`.
   - "esse momento não precisa de motion" → `decisao` vira `aroll`.
   - "o texto do M12 é outro" / "essa cena pede whoosh" / "sem zoom aqui" → o campo
     da `motion.cena` do M12 (`texto`, `som`, `cameraTransicao`); o prompt é remontado.
   - "o vídeo inteiro está lento demais" → `direcaoMotion.movimento` ou `climaRitmo`.
   Depois: `validar.py` até zero erros e rode a etapa de novo.
5. Aprovado: `touch edicao/aprovado/motion`. Só então `/sofia-estrategista-editora:finalizar`.

Sempre com vigia: processo sem progresso por 4 min é morto e investigado, nunca esperado.
