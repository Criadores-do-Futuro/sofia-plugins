# Sofia — plugins

Marketplace privado de plugins do Claude Code com a Sofia, a estrategista de roteiros para
vídeos curtos, em três idiomas.

| Plugin | Idioma | O que faz |
|---|---|---|
| `sofia` | Português | Pesquisa vídeos virais, analisa e escreve ou melhora roteiros. |
| `sofia-latam` | Espanhol | Analisa vídeos de TikTok, Instagram e YouTube e cria ou melhora roteiros. |
| `sofia-english` | Inglês americano | Revisa, analisa, escreve e reescreve roteiros pelo método CDF. |
| `cdf-equipe` | Português | A Sofia interna da equipe: liga o Claude ao console da plataforma de desafios (MCP) e traz as rotinas de gestão de comunidade. |

## Instalar

O repositório é privado: a sua conta do GitHub precisa ter sido convidada.

```
/plugin marketplace add bento-dev-ia/sofia-plugins
/plugin install sofia@sofia-plugins
```

Para as outras versões, troque `sofia` por `sofia-latam` ou `sofia-english`.

## Conteúdo pelo conector

Parte do conteúdo de cada Sofia, como a lista de módulos e aulas e as bases de
conhecimento, não fica nos plugins. Esse conteúdo vem do conector MCP `sofia-conteudo`.
Sem o conector, a Sofia avisa e trabalha com menos material. O contrato está em
[docs/conteudo-no-mcp.md](docs/conteudo-no-mcp.md). O que ficou para depois está em
[docs/pendencias.md](docs/pendencias.md).

## O que a Sofia pede antes de fazer

A Sofia pede o seu OK antes de:

- instalar qualquer programa;
- gastar créditos de serviços pagos, como o Apify.

Ela também:

- não usa os cookies do seu navegador e não contorna login;
- guarda o que aprende na sua pasta de trabalho, não na pasta do plugin.

## Licença

Todos os direitos reservados. Veja [LICENSE](LICENSE).
