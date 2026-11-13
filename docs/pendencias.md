# Pendências

Lista do que ficou para depois. Serve para retomar o trabalho com uma IA.

**Regra usada na revisão:**
- O que era **claramente** um problema (sensível, contra os termos do produto ou vazamento)
  saiu do plugin. Agora vem pelo MCP (`docs/conteudo-no-mcp.md`) ou foi apagado.
- O que **não estava claro** ficou como estava e não conta como problema.

Cada item diz o plugin, o que falta e como resolver.

## Todos os plugins

- [ ] **Conector `sofia-conteudo`.** O MCP ainda não existe.
  - Quando existir, declare-o no `.mcp.json` de cada plugin, sem chave nem token.
  - Confira se cada id dos ponteiros (`grep -rn "sofia-conteudo" plugins/`) devolve a peça.
- [ ] **Ícone.** Os três têm um ícone provisório em `.claude-plugin/icon.png`:
  - 1024 px, letra S e selo do idioma.
  - Troque pela arte final quando houver. A arte antiga da Sophia estava em português e
    saiu.
- [ ] **Versões.** Ao mudar um plugin, suba a versão no `plugin.json` dele **e** no
  `.claude-plugin/marketplace.json`. As duas precisam bater.

## sofia-english

- [ ] **Base de conhecimento.** Agora vem só pelo MCP. Sem o conector, a Sophia trabalha
  limitada.
  - Peças: `execution-guide`, `quality-rules`, `personality`, `narrative-techniques`,
    `fcc-method`, `anti-repetition`, `spoken-language`.
- [ ] **Parâmetros do conector.** O `SKILL.md` cita o plugin e o id da peça. O nome exato
  dos parâmetros de `carregar_conteudo` é definido pelo MCP. Ajuste o texto se mudar.
- [ ] **Autor.** O autor é Alef Marques. Confirme com ele a distribuição e a licença.

## sofia-latam

- [ ] **Exemplos com criador real.** Saíram para o MCP: `ejemplo-estructura-analisis` e
  `ejemplos-especificidad`. No plugin ficaram exemplos genéricos.
- [ ] **Termos das plataformas.**
  - Baixar vídeo do TikTok, do Instagram ou do YouTube ainda pode violar os termos delas.
  - O que já foi feito:
    - o caminho padrão virou o envio do arquivo;
    - o download vale só para conteúdo sobre o qual o usuário tem direito;
    - há um aviso de responsabilidade.
  - Revise se quiser tirar o download de vez.
- [ ] **Método.**
  - Formatos, estruturas, elementos e princípios ficaram no plugin.
  - Não está claro se reproduzem apostilas do curso. Se reproduzirem, mova-os para o MCP
    com ponteiro, como nos outros.
