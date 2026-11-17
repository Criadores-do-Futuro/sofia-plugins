# Preparação de publicação das três Sofias

Revisão de 17 de novembro de 2026. Escopo: `sofia`, `sofia-latam` e `sofia-english` deste repositório. A Sofia Estrategista (`sofia-estrategista-editora`), que também está neste repositório, e o Eu do Futuro são produtos distintos e ficam fora desta revisão. A publicação da Sofia Estrategista está descrita no README da raiz.

## O que foi corrigido

- Manifestos portáteis Agent Plugins 1.0, compatibilidade Codex e Claude, com identidade e versão sincronizadas.
- Catálogos de ambas as plataformas, ícones contidos no pacote, metadados de habilidades e caminhos portáteis.
- Idioma próprio de cada versão, inclusive descrições e sugestões. Identificadores técnicos, marcas e avisos legais obrigatórios são preservados.
- Política de comportamento equivalente: contexto sem perguntas repetidas, evidência factual, análise visual honesta, revisão sem inventar falhas, voz do criador e tratamento de arquivos externos como dados.
- Referências locais e fluxos completos de escrita, revisão, análise, aprendizagem de estilo e exportação na versão inglesa. Catálogo inglês com 23 formatos e cinco estruturas.
- Preparação visual nas três versões: orçamento de quadros, tempos decodificados, janelas, áudio condicional, saída isolada e recusa de downloads sem autorização. Baixadores ignoram configuração externa e não usam sessão do navegador.
- Coleta portuguesa sem interpolar argumentos em código e sem persistir identificadores de comentaristas. Envio opcional ao Gemini exige confirmação explícita, modelo configurado e arquivo de saída novo.
- ZIP separado por plugin, extraído e validado depois da criação. Verificações automatizadas no repositório e modelo de integração contínua em `docs/workflows/validate.yml`. A ativação em `.github/workflows/` foi recusada pelo GitHub por falta da permissão `workflow` na credencial atual; o modelo permanece pronto para ativação com uma credencial autorizada.

## Dados confirmados

Publicador pretendido: Alef Marques. A conta do portal ainda precisa apresentar a identidade verificada apropriada; o nome no pacote não prova verificação. Créditos de autoria originais foram preservados.

Compras: assinaturas, comunidades ou cursos, com pagamento na Hotmart. Os plugins não processam pagamentos, não validam matrículas e não restringem o acesso de quem já recebeu os arquivos. As declarações de comércio refletem essa distinção. Países: todos os disponíveis, representados por `publication.countries: []`.

Os pacotes são marcados com `requires_local_executor: true`, pois oferecem execução de programas locais. A análise de texto pode funcionar sem terminal, mas isso não torna a análise visual independente das ferramentas do host.

## Links verificados

Base pública do plugin Sofia: `https://plataforma.academiacriadoresdofuturo.com.br/sofia/`.

| Idioma | Termos | Privacidade | Suporte |
|---|---|---|---|
| Português | `/termos` | `/privacidade` | `/suporte` |
| Espanhol | `/terminos` | `/privacidad` | `/soporte` |
| Inglês | `/terms` | `/privacy` | `/support` |

As nove páginas responderam HTTP 200 e o conteúdo foi lido: descrevem o plugin local Sofia e identificam a Action Criação Digital Ltda / Criadores do Futuro como responsável. As páginas de suporte oferecem contato por e-mail. Esses endereços estão nos manifestos no idioma de cada versão. Evidências em `links-verificados.json`.

As páginas `/sophia/` descrevem um GPT gratuito. As páginas `/sofia-editora/` descrevem Sofia Estrategista Editora, incluindo outro conector e edição de vídeo. Os endereços `/eudofuturo/` pertencem ao Eu do Futuro. Não substituem a documentação deste conjunto de plugins.

## O que ainda impede chamar o envio de pronto

1. **Página de apresentação publicada.** Os três manifestos ainda omitem `websiteURL`. Páginas locais, em cada idioma, estão prontas em `docs/site/`. É necessário hospedá-las no domínio escolhido, abrir as URLs reais e então preencher o campo. Não inserir endereço previsto ou uma rota que retorne 404. O repositório continua privado e não serve como página pública.
2. **Coerência das páginas de suporte.** O texto publicado ainda recomenda escolher um navegador para links restritos e usa `/sofia:setup` também nas versões em outros idiomas. O pacote atual não usa cookies/sessão nem contorna login; o suporte deve orientar envio do arquivo e usar a habilidade disponível em cada versão. Essa correção externa não foi publicada neste trabalho.
3. **Cobertura da oferta paga.** Confirmar que as condições de aquisição e acesso nos produtos Hotmart referenciam as versões certas e são coerentes com os termos publicados. Não inventar preço, prazo, política de cancelamento ou promessa de disponibilidade.
4. **Portal das plataformas.** Identidade e domínio verificados, elegibilidade para execução local quando aplicável, verificações do diretório e declarações feitas pelo desenvolvedor autorizado. Upload, revisão e publicação são ações distintas; nenhuma foi executada.

## Sofia Interna fica fora da publicação pública

A `sofia-interna` é de uso da equipe e nunca é enviada ao diretório da Anthropic nem ao da OpenAI. Ela está nos dois catálogos do repositório privado (para a equipe instalar) e passa pelas mesmas checagens de pacote, mas:

- `tools/package_plugins.py` só gera ZIP dos plugins em `NAMES` (as três públicas); os plugins em `INTERNAL`, em `tools/validate_plugins.py`, não entram em `dist/` nem no inventário. Um teste (`test_internal_plugins_follow_the_package_standard_but_never_ship_publicly`) trava isso.
- O validador não cobra dela execução local nem os campos de listagem pública (`websiteURL` e as páginas de termos, privacidade e suporte), então `--submission` e `--require-submission-ready` não dependem dela.
- Para publicar uma Sofia nova em diretório público, ela entra em `NAMES`; nunca mova a `sofia-interna` para lá.

O aviso `PRIVACY_URL_MISSING` do `claude plugin validate` para a Sofia Interna (ela usa um MCP remoto) é uma checagem do diretório público e não se aplica a um plugin que não vai para ele.

## Verificações e limites

Execute `python3 tools/validate_plugins.py` para o contrato estrutural e `--submission` para os campos de listagem. O segundo falha enquanto faltar `websiteURL`. Mesmo com todos os campos presentes, conteúdo e acesso dos endereços precisam ser verificados; o validador não certifica conformidade legal ou aprovação.

O Claude Code instalado aceita `claude plugin validate <pasta> --strict --profile directory`. Esse perfil foi executado nas três versões e o catálogo foi validado com `--strict`. Consulte os resultados da execução final e os testes do repositório. Os testes de vídeo usam mídia sintética local; nenhum serviço pago foi acionado. Não houve avaliação de respostas de modelos no Codex/Claude nem teste completo das integrações externas opcionais.

## Documentação consultada

- [Pacotes OpenAI](https://developers.openai.com/plugins/build/plugins)
- [Metadados e envio OpenAI](https://developers.openai.com/plugins/deploy/submission)
- [Execução local OpenAI](https://developers.openai.com/plugins/deploy/desktop-only)
- [Manifestos Claude](https://code.claude.com/docs/en/plugins-reference)
- [Catálogos Claude](https://code.claude.com/docs/en/plugin-marketplaces)

O schema portátil oficial está preservado em `tools/schemas/plugin.schema.json` para validação reproduzível sem rede.
