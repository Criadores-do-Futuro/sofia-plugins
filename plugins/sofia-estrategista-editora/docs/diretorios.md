# Enviar aos diretórios da Anthropic e da OpenAI

O que o repositório já cumpre e o que só o dono da conta pode fazer. Conferido em 16/11/2026 contra a documentação oficial (links no fim).

## Diretório de plugins da Anthropic

### Já cumprido no repositório

| Exigência | Como está |
|---|---|
| `plugin.json` válido, nome em minúsculas com hífen | `sofia-estrategista-editora`, versão `0.4.0`; `claude plugin validate --strict --profile directory` passa na pasta do `.zip` |
| Cabeçalhos de skills, comandos e agentes | YAML válido; skills e comandos só com os campos aceitos no envio (`tests/test_pacote.py`) |
| Ícone | `assets/icon.png`, 512 × 512, em `icon` (Claude) e em `composerIcon` e `logo` (Codex) |
| README com 40 palavras ou mais, fora de bloco de código | `README.md` |
| Licença | `LICENSE` e `"license": "LicenseRef-Proprietary"` |
| Política de privacidade e termos | `privacyPolicyUrl` e `termsOfServiceUrl` no `plugin.json`; páginas em português, espanhol e inglês (tabela no README) |
| Contato e suporte | `author.email` e `author.url` |
| Conector só em https | `https://plataforma.criadorestrategista.com.br/api/mcp` |
| Nada de `npx`/`uvx` sem versão | o CLI do HyperFrames roda como `hyperframes@0.9.58`; o Remotion vem do `package.json` do modelo, com versões fixas |
| Sem `.DS_Store`, links simbólicos, caminhos que saem do plugin e segredos | conferido nos arquivos rastreados |
| Caminhos só com letra sem acento, número, ponto, hífen e sublinhado (o envio recusa `[`, `,`, espaço e acento com "Zip file contains path with invalid characters") | `scripts/empacotar.sh` para antes de fechar o `.zip`, e `tests/test_pacote.py` confere os arquivos rastreados |
| README diz o que o plugin roda, envia e baixa | seção "O que o plugin roda, envia e baixa" |
| Instalar programa só com o sim da pessoa | `setup.py --instalar` e `--atualizar` só executam com `--sim` |
| Até 512 arquivos | o pacote fica abaixo disso (`scripts/empacotar.sh` mostra a conta) |

### Vai para revisão manual (não bloqueia)

- **Fontes acima de 256 KiB.** São 10 arquivos de fonte livre (OFL), alguns repetidos entre `skills/beditor/public/fontes/` e `skills/motion-vox/fontes/`. Ficaram porque o render de motion depende deles nos dois lugares.
- **Instalação de pacotes.** O `setup` sugere `brew`, `pip` e `npm`, e o projeto de motion roda `npm install`. Tudo isso está no README.

### O que só o dono faz

1. Em claude.ai, conectar a conta do GitHub que pode dar push em `bento-dev-ia/sofia-estrategista-editora`.
2. Instalar o Claude GitHub App no repositório. Com o repositório privado, o portal pede para confirmar o envio do código para a verificação automática.
3. No portal do diretório, validar e enviar o plugin. O conector Sofia Estrategista é enviado à parte, como conector, se ainda não estiver no diretório.
4. Para publicar, deixar o repositório público e clicar em **Check for new commits** na página do plugin. Enquanto ele for privado, a revisão anda, mas a publicação espera.
5. Conferir que o plano e o papel na organização permitem enviar.

## Diretório de plugins da OpenAI (Codex)

### Já cumprido no repositório

| Exigência | Como está |
|---|---|
| Manifesto `.codex-plugin/plugin.json` | nome, versão `0.4.0`, autor, site, repositório, licença, skills e conector |
| Ficha da loja | `interface`: nome de exibição, descrições curta e longa, categoria `Productivity`, capacidades, três sugestões de pedido, ícone e logo |
| Privacidade, termos e suporte | `privacyPolicyURL`, `termsOfServiceURL` e `supportURL` (páginas em inglês) |
| 5 casos positivos e 3 negativos | `extensions.com.openai.review.test_cases`, com as ferramentas reais do conector |
| Notas da versão | `extensions.com.openai.publication.release_notes` |
| Só no computador | `"requires_local_executor": true` no topo do manifesto, como pede a documentação para o formato `.codex-plugin` |
| Conector remoto | http, sem servidor local (servidor MCP local exige parceria aprovada) |

### O que só o dono faz

1. Pedir acesso de envio e verificar a identidade da empresa (Action Criação Digital Ltda) na plataforma da OpenAI.
2. Criar uma **conta de teste** no curso, com dados de exemplo, sem verificação em duas etapas nem código por e-mail, e informar login e senha em **Review information → Review details**. A conta precisa ter cards no planejamento para os casos de teste.
3. Rodar os 8 casos de teste com essa conta e **gravar o vídeo de demonstração**; colar o link no portal.
4. Gerar o ZIP (`scripts/empacotar.sh` gera `dist/sofia-estrategista-editora.zip`) e enviar. O portal da OpenAI não aceita pacote com hooks: para enviar ao diretório, gere uma cópia sem `hooks/` e sem o campo `types` do manifesto do Claude.
5. Conferir no portal a categoria e os países. A categoria foi escolhida aqui, sem consulta à lista do painel.
6. Testar a instalação num Codex desktop limpo antes de enviar, como pede a documentação.

## Antes de cada envio

```sh
python3 -m unittest discover -s tests -v
claude plugin validate .
node scripts/conferir-ferramentas.mjs CAMINHO_DO_WEBAPP
scripts/empacotar.sh
```

Suba a versão nos dois manifestos e atualize as notas da versão no `.codex-plugin/plugin.json`.

## Fontes

- [Anthropic: checklist antes de enviar um plugin](https://claude.com/docs/plugins/pre-submission-checklist)
- [Anthropic: enviar um plugin](https://claude.com/docs/plugins/submit)
- [OpenAI: enviar plugins do Codex](https://developers.openai.com/codex/submit-plugins)
- [OpenAI: diretrizes de plugins](https://developers.openai.com/plugins/plugin-guidelines)
- [OpenAI: plugins só para desktop](https://developers.openai.com/plugins/deploy/desktop-only)
