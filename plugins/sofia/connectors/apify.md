# Conector: Apify

## O que é
Apify é uma plataforma paga por uso, com actors prontos para extrair dados públicos de redes sociais.

## Por que precisa
- Instagram e TikTok não têm API pública para extrair comentários com curtidas e métricas completas
- O Apify oferece actors especializados que fazem isso de forma confiável
- É opcional: sem ele, a Sofia segue com o que é grátis (yt-dlp) e diz o que ficou de fora

## Regra de custo: OK antes de gastar
Cada chamada consome crédito da conta da pessoa. Antes de rodar qualquer actor:

1. Diga quantos vídeos, o que vai buscar (dados do post, comentários) e a estimativa de custo do lote.
2. Espere o "sim". Sem o OK, siga só com o que é grátis.

Exemplo: "Para trazer os 20 comentários mais curtidos destes 3 Reels, vou usar o Apify. Custa por volta de US$ 0,10 no total, descontado do seu crédito. Posso?"

## Como configurar

### 1. Criar conta
- Acesse https://apify.com e crie a conta
- O plano grátis vem com um crédito mensal (confira o valor atual em https://apify.com/pricing)

### 2. Ligar à Sofia (escolha um caminho)
A chave nunca vai para dentro da pasta do plugin e nunca é colada no chat.

1. **Conector oficial do Apify (recomendado).** Instale o MCP do Apify no Claude Code. A Sofia usa as ferramentas `mcp__Apify__*` e não precisa ver a chave.
2. **Variável de ambiente.** Em Settings → Integrations → Personal API Tokens, copie o token e rode você mesmo no terminal:
   - macOS/Linux: `echo 'export APIFY_TOKEN="COLE_SEU_TOKEN_AQUI"' >> ~/.zshrc` (ou `~/.bashrc`) e abra um terminal novo
   - Windows: `setx APIFY_TOKEN "COLE_SEU_TOKEN_AQUI"` e abra um terminal novo
3. **Arquivo fora do plugin.** Crie `~/.sofia/chaves.env` com a linha `APIFY_TOKEN=COLE_SEU_TOKEN_AQUI` e proteja com `chmod 600 ~/.sofia/chaves.env`.

## Actors utilizados

Valores estimados por execução; o preço real está na página de cada actor.

### Instagram
| Actor | Uso | Estimativa |
|-------|-----|-------------|
| `apify/instagram-scraper` | Dados do post (legenda, métricas) | ~US$ 0,01 |
| `apify/instagram-comment-scraper` | Comentários com curtidas | ~US$ 0,02 |

### TikTok
| Actor | Uso | Estimativa |
|-------|-----|-------------|
| `clockworks/tiktok-video-scraper` | Dados do vídeo | ~US$ 0,01 |
| `clockworks/tiktok-comments-scraper` | Comentários com curtidas | ~US$ 0,02 |

## Custo estimado
- 1 análise completa (post + comentários): ~US$ 0,03
- 100 análises por mês: ~US$ 3,00
- Uso moderado costuma caber no crédito grátis, mas a estimativa é mostrada antes de cada lote

## Comentários
Guarde só o texto literal, as curtidas e a data. Nunca o @, o nome ou a foto de quem comentou, mesmo que o actor traga esses campos.

## Uso via MCP (Claude Code)
Se o MCP do Apify está instalado, depois do OK:
```
mcp__Apify__fetch-actor-details(actor)          # confere o esquema de entrada
mcp__Apify__call-actor(actor, input)            # roda o actor
mcp__Apify__get-dataset-items(datasetId)        # lê o resultado
```

## Uso via CLI (outros ambientes)
Depois do OK, com o token na variável de ambiente (nunca escrito no comando):
```bash
curl -X POST "https://api.apify.com/v2/acts/apify~instagram-scraper/runs" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"directUrls": ["URL"], "resultsLimit": 1}'
```
