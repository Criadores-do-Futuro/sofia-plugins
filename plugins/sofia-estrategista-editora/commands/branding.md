---
description: Define o branding de motion graphics de um canal ou cliente — pergunta, mostra opções animadas num artifact, escreve o motion.md da marca (fora do plugin)
allowed-tools: Read, Write, Artifact, AskUserQuestion, Bash, Glob
---

Regere o branding de motion graphics do canal — as escolhas que fazem o `diretor` parar
de decidir do zero, genericamente, a cada vídeo.

1. **Publique o laboratório de estilo.** Um artifact HTML com treze situações que se
   repetem em quase todo vídeo — personagem, estudos, pessoas famosas, categorias/partes/
   etapas/camadas, datas, comparação, preço, aviso/alerta, fofoca, truque, dica, legenda,
   hook visual — três opções **animadas** por situação (nunca estáticas: toda opção mostra
   entrada, o que acontece, saída). Use a paleta e a tipografia da marca (`marca.json`) quando houver; sem ela, as medidas em
   `referencias/linguagem-visual.md` (`#0C0C0C`, `#CCCAC8`, `#FFB067`, `#7FB4FF`,
   `#FFA33A`, `#C94850`; Archivo Black, Inter, IBM Plex Mono) — isto não é um moodboard
   genérico, é o próprio sistema visual do canal em miniatura.

2. **Pergunte, situação por situação**, em grupos de até quatro perguntas por vez
   (`AskUserQuestion`), pedindo a letra escolhida no artifact — ou uma resposta livre,
   quando o editor quiser combinar duas opções, adicionar uma rota extra, ou escrever a
   sua. Não avance para o próximo grupo sem terminar o atual; se uma pergunta for
   dispensada, pare e pergunte o que fazer em vez de assumir uma resposta.

3. **Escreva o `motion.md` da marca** com o resultado (a marca é pessoal e fica fora do
   plugin: `marca.py mostrar` diz qual vale e onde está; se é um canal ou cliente novo,
   `marca.py nova "<nome>"` cria a pasta, e `marca.py usar <nome> --projeto <projeto>`
   liga ao projeto), na gramática de
   `receitas.md`: para cada situação, o padrão escolhido, a receita concreta (entra →
   acontece → sai, com duração), e — quando a situação não corresponde a uma classe
   existente do `catalogo-visual.md` — a qual classe existente ela se prende (`cartela`,
   `objeto`, `dado`, `tela`) e por quê. Situações que continuam com mais de uma rota válida
   (ex.: retrato licenciado + colagem de jornal) registram as duas e o critério de escolha
   entre elas.

4. **Atualize a lista de referências obrigatórias em `agents/diretor.md`** se este arquivo
   ainda não estiver citado lá, e diga isso ao editor.

Este comando **regera o arquivo do zero** — é o retrato do canal hoje, não um histórico.
Rodar de novo substitui as escolhas anteriores. Mudança pontual de um vídeo específico não
entra aqui: vai no `porque` do `guia.json` daquele vídeo.
