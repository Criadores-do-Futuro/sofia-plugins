# Conteúdo que vem pelo MCP

Parte do conteúdo das Sofias não fica dentro dos plugins: quem instala recebe todos os
arquivos do plugin na própria máquina, e esse conteúdo não pode ficar lá. Entram aqui a
lista completa de módulos e aulas, os detalhes internos dos cursos, as transcrições
inteiras de vídeos de terceiros e tudo o que os termos do próprio produto proíbem copiar.

Esse conteúdo é carregado no contexto só na hora do uso, por um conector MCP. Os plugins
guardam apenas as instruções e, no lugar de cada peça retirada, um ponteiro para ela.

## Contrato que os plugins esperam

- **Servidor MCP:** `sofia-conteudo`
- **Ferramenta:** `carregar_conteudo`
- **Entrada:**
  - `plugin`: `sofia`, `sofia-latam` ou `sofia-english`;
  - `peca`: o id da peça, como aparece no ponteiro (ex.: `fcc-method`).
- **Saída:** o texto da peça, em markdown.
- **Erros:**
  - peça desconhecida: mensagem curta dizendo que a peça não existe;
  - usuário sem acesso: mensagem curta dizendo que o acesso não está liberado.

O texto padrão de cada ponteiro diz ao Claude o que fazer quando o conector não estiver
disponível: avisar o usuário e seguir sem a peça, sem inventar o conteúdo.

Se o nome do servidor ou da ferramenta mudar, troque nos ponteiros. Para achar todos:

```bash
grep -rn "sofia-conteudo" plugins/
```

## Onde estão as peças

As peças retiradas **não estão neste repositório**. Ficam com o dono, fora do Git, para
alimentar o MCP. Cada plugin tem um `MOVIDO.md` com a tabela de peças, com as colunas:

- id;
- caminho original;
- o que é;
- por que saiu.

## Quando o MCP estiver pronto

1. Publique o servidor e confirme que `carregar_conteudo` devolve cada id do `MOVIDO.md`.
2. Declare o servidor no `.mcp.json` de cada plugin (ou peça para o usuário conectar),
   sem chave nem token no repositório.
3. Teste cada plugin com e sem o conector ligado.
