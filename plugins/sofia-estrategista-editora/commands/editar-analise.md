---
description: Edita um vídeo do formato `analise` (comentário sobre a peça de outra pessoa) em quatro chamadas com cache — transcrever, cortar, renderizar, medir — refaz só o que o ajuste tocou e fecha com o registro de custos
---

Argumentos: `$ARGUMENTS` = pasta do projeto (`Projetos/NN - Nome/`) com os takes
listados em `edicao/dados.json` (ou os caminhos dos takes, para um projeto novo).

Leia `referencias/formato-analise.md` (o formato) e `referencias/eficiencia.md`
(as regras de custo) antes. A regra deste comando: **uma etapa é um script do
plugin em uma chamada.** Nada de pipeline na pasta de rascunho.

1. **Transcrever** — uma vez por conteúdo de áudio; rodar de novo é grátis.
   `python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/transcrever.py edicao/oficina/transcricao <take1.mov> <take2.mov> ... --contexto "<nomes próprios que aparecem na fala>"`
2. **Decupar e cortar** — as decisões do diretor vão para `edicao/dados.json`
   no que é dele: `takes` (só `arq`), `momentos` com `take`, `localDeS`,
   `localAteS`, `decisao`, `porque`; `recusas`, `cortesInternos` (também em
   segundos locais), `correcoes`, `estrutura` (só `nome`, `de`, `ate`). O resto é
   conta, e `decupar.py` faz: offsets da linha virtual, palavras em ms, wav
   costurado. `silencio.py` carimba a tabela do corte (cabeça, miolo, cauda,
   folga). `decupar.py --estrutura` preenche as porcentagens dos blocos para
   conferir os portões sem assistir; `decupar.py --em 004:16.3` diz onde um
   segundo do take cai no corte (para comentar o vídeo em minutos do master).
   **O `de`/`ate` do `plano.json` é em segundos da LINHA VIRTUAL** (offset do
   take que o decupar imprimiu + segundo local da palavra), nunca do corte: o
   render converte, e um cartão escrito em segundo do corte cai fora e é pulado.
   `python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/decupar.py <projeto>`
   `python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/silencio.py edicao/dados.json <linha.wav que o decupar imprimiu>`
   `python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/decupar.py <projeto> --estrutura`
3. **Renderizar** — `edicao/plano.json` tem fontes, cartões, marcadores, hook e
   cama (formato na docstring de `render_analise.py`). A cama vem da biblioteca
   (`python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/biblioteca.py cama --clima <clima>`
   imprime o bloco `musicas` pronto para colar) e o aviso de licença de cada faixa
   vai junto para o `provas.json` — regras em `referencias/biblioteca.md`. Em
   segundo plano, com `Monitor` filtrando `segmentos|MASTER|Traceback|!!`.
   `python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/render_analise.py <projeto> --revisao`
   A primeira rodada paga tudo (rosto, A-roll, clipes, 100% dos segmentos). As
   seguintes refazem só o que mudou, e `edicao/oficina/manifesto.json` diz o quê.
   A chave do trecho inclui só as funções de desenho que ELE usa: mexer no título
   não refaz os trechos de legenda (medido no 16: 0 de 111 contra 111 de 111).
   Material de terceiro sai da midiateca, nunca de `edicao/acervo/`:
   `python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/midiateca.py buscar "<assunto>"`
   antes de procurar fora, e `midiateca.py baixar <url> --projeto <projeto>` quando
   não houver. No `plano.json` a fonte fica como `"arq": "midia:videos/…"`.
   Terminado o render, o vídeo vai para o painel (`painel/revisao.py`), não para um
   aviso de pasta — ver `/sofia-estrategista-editora:painel`.
   **E o dono é avisado.** O script já notifica a máquina (`avisar.py`, disparado no
   fim do render); a sessão manda o push para o celular com a ferramenta de
   notificação do harness, uma linha, dizendo o que ficou pronto e onde ver:
   «16 pronto para revisar no painel · 6 de 111 trechos refeitos». Só nestes dois
   momentos — pronto para **revisar** e pronto para **publicar** —, nunca a cada passo.
4. **Medir** — cinco números; imagem só se um número reprovar.
   `python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/qa_analise.py <projeto>`
   Com `--comparar edicao/master-aprovado.mp4` depois de um ajuste: prova que o
   resto não mudou. Com `--folha`: a folha de contato em 1 568 px, em `edicao/qa.jpg`.

5. **Custos** — fecha o registro do vídeo: tokens e tempo de sessão por etapa,
   cruzados com os segundos de máquina que os scripts gravaram em
   `edicao/oficina/telemetria.jsonl`; escreve `edicao/oficina/custos.json`.
   `python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/custos.py --projeto <projeto>`
   (`--por-pedido` abre por pedido do dono; `--desde <ISO>` recorta o dia.)

**Ajuste pedido pelo dono** («abaixa a música», «troca o insert de 1:48»): edite
`plano.json` (ou `dados.json`, se for corte), rode o passo 3 e o passo 4 com
`--comparar`. Não releia o vídeo inteiro; leia o manifesto e a comparação.

**Entrega**: escolhido o quadro limpo da capa (N) e escrito `publicacao.json`,
`render_analise.py <projeto> --entrega N` gera `edicao/entrega/master-final.mp4`
sem recodificar o corpo. Publicar segue `referencias/publicacao.md` — nunca sem
o sim explícito na conversa.
