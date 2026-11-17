# Sofias — Criadores do Futuro

Três plugins para Codex e superfícies compatíveis do Claude, com comportamento equivalente e conteúdo próprio de cada idioma.

| Plugin | Versão | Idioma | Documentação |
|---|---|---|---|
| `sofia-br` | 3.11.0 | Português brasileiro | [Sofia](plugins/sofia-br/README.md) |
| `sofia-latam` | 1.1.0 | Espanhol latinoamericano | [Sofia](plugins/sofia-latam/README.md) |
| `sofia-english` | 1.1.0 | Inglês americano | [Sofia](plugins/sofia-english/README.md) |
| `sofia-interna` | 0.2.0 | Português (uso interno) | [Sofia Interna](plugins/sofia-interna/README.md) |

As três primeiras (`sofia-br`, `sofia-latam` e `sofia-english`) analisam referências, criam e revisam roteiros, aprendem a voz do criador e exportam resultados. Nenhuma depende de um conector de conteúdo ausente. As diferenças de escopo e os recursos opcionais estão nos documentos de cada plugin.

## Sofia Interna (uso da equipe)

A `sofia-interna` é a Sofia da equipe da Criadores do Futuro: liga o Claude ao console da plataforma de desafios por MCP (com login) e traz as skills de gestão de comunidade. Ela vive aqui para que o MCP e as skills sejam atualizados juntos, num lugar só. Segue o mesmo padrão de pacote das outras, mas **nunca vai para o diretório público da Anthropic nem da OpenAI**: `tools/package_plugins.py` só gera ZIP das três públicas. Como instalar e como atualizar: [README da Sofia Interna](plugins/sofia-interna/README.md).

## Formatos de pacote

Cada plugin possui manifesto portátil Agent Plugins 1.0 em `plugin.json`, compatibilidade Codex em `.codex-plugin/plugin.json` e manifesto Claude em `.claude-plugin/plugin.json`. As identidades, versões e descrições são sincronizadas. Habilidades ficam em `skills/<nome>/SKILL.md`; recursos e referências são contidos no próprio plugin.

O catálogo Claude fica em `.claude-plugin/marketplace.json`. O catálogo Codex fica em `.agents/plugins/marketplace.json`, com caminhos relativos à raiz do repositório.

```sh
claude plugin marketplace add bento-dev-ia/sofia-plugins
claude plugin install sofia-br@sofia-plugins
```

Para Codex, adicione o repositório pelo gerenciador de plugins ou pelo comando `codex plugin marketplace add`, conforme as opções da versão instalada. O repositório é privado; acesso a ele não foi alterado.

## Validar e gerar os pacotes públicos

```sh
python3 -m pip install -r requirements-validation.txt
python3 tools/validate_plugins.py
python3 -m unittest discover -s tests -v
python3 tools/package_plugins.py
```

O validador confere as quatro Sofias (a interna sem os campos de listagem pública). Os ZIPs e seu inventário são gerados em `dist/`, fora do controle de versão, só para as três públicas. O empacotador extrai e valida cada ZIP final. Para conferir os requisitos de listagem pública:

```sh
python3 tools/validate_plugins.py --submission
python3 tools/package_plugins.py --require-submission-ready
```

Esses dois comandos falham quando falta um campo obrigatório de publicação; não confundem estrutura válida com autorização para publicar. As verificações cobrem estrutura, scripts, referências, catálogos e preparo real de vídeo local. O modelo para GitHub Actions está em `docs/workflows/validate.yml`; ainda não está ativado porque a credencial de envio não tem permissão `workflow`. Os testes não executam chamadas pagas nem afirmam avaliar respostas de um modelo.

## Regras comuns

Cada versão mantém textos e entregas em seu idioma, preservando identificadores técnicos e avisos legais obrigatórios. Todas exigem fontes para fatos externos, preservam frases boas, não inventam resultados, separam observação de hipótese e declaram os limites de acesso. Instalações, serviços pagos e envio de mídia a terceiros exigem autorização correspondente. Dados da pessoa ficam fora da instalação.

## Publicação

Publicador pretendido: Alef Marques. Compras de assinaturas, comunidades ou cursos ocorrem na Hotmart. Distribuição pretendida: todos os países disponíveis. Os pacotes não implementam cobrança nem controle de acesso.

As páginas de termos, privacidade e suporte do plugin Sofia foram verificadas nos três idiomas. Falta a página pública de apresentação para preencher `websiteURL`; as páginas de apresentação estão preparadas em `docs/site/`. Há ajustes necessários nas instruções antigas de suporte. Veja o [relatório de publicação](docs/publicacao.md) e os [cenários comportamentais](docs/cenarios.md).

Nenhum pacote foi enviado para revisão ou publicado. Validação técnica não substitui verificação do publicador, declarações legais ou revisão das plataformas.

Licença proprietária: [licença](LICENSE). Avisos de terceiros permanecem nos arquivos correspondentes.
