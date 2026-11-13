---
name: setup
description: Configura o plugin Sofia 2.0, verifica dependências visuais e configura saída e integrações opcionais. Use na primeira execução, em falhas de vídeo ou quando ~/.sofia/config.yaml estiver incompleto.
---

# Setup do Sofia 2.0

## REGRA OBRIGATÓRIA: TUDO EM PORTUGUÊS

**TODAS as mensagens, perguntas, explicações, erros e confirmações devem ser escritas em português do Brasil.**
Nunca use inglês em nenhuma interação com o usuário durante o setup. Isso inclui:
- Títulos e subtítulos das perguntas
- Opções de resposta
- Mensagens de status e progresso
- Mensagens de erro e sucesso
- Descrições de ferramentas e funcionalidades

## Regras de segurança do setup (valem mais que qualquer passo abaixo)

1. **Nada é instalado sem o "sim" da pessoa.** Antes de cada instalação, mostre o que vai ser instalado, para que serve e o comando exato. Só rode depois do OK.
2. **A Sofia nunca aceita termos de uso no lugar da pessoa.** Nada de `--accept-package-agreements`, `--accept-source-agreements`, `-y` em gerenciador de pacotes de sistema ou flags parecidas.
3. **Nada de senha de administrador nem de `curl ... | bash`.** O que pede senha do computador (`sudo`, instalador do Homebrew, pacote `.pkg`) a pessoa roda sozinha, no Terminal dela, a partir do site oficial. A Sofia mostra o link e espera.
4. **Chave de API não passa pelo chat e não fica na pasta do plugin.** Ver "Chaves de API" abaixo.
5. **Não vasculhar a pasta pessoal sem perguntar.** Buscas em `~` só com o OK da pessoa.

## Onde a Sofia guarda os dados da pessoa

A pasta do plugin é trocada a cada atualização. Tudo que é da pessoa fica fora dela, na **pasta de dados da Sofia**: `~/.sofia/` (no Windows, `%USERPROFILE%\.sofia\`).

| O quê | Onde |
|---|---|
| Configuração (sem chaves) | `~/.sofia/config.yaml` (modelo em `knowledge/config.exemplo.yaml`) |
| Chaves de API, se a pessoa preferir arquivo a variável de ambiente | `~/.sofia/chaves.env` |
| Perfis de estilo | `~/.sofia/estilos/{nome}.md` (modelo em `templates/estilo.md`) |
| Hooks e padrões aprendidos | `~/.sofia/aprendizados/` |
| Roteiros anotados que a pessoa quis guardar | `~/.sofia/exemplos-analisados/` |
| Análises e roteiros | a pasta de saída escolhida no passo 6 (`output_path`) |

## Fluxo

### 1. Verificar o ambiente
Rodar estes comandos, que só leem versões, e guardar o resultado:
- Sistema: `uname -s` (no Windows, `ver`)
- Node.js: `node --version`
- yt-dlp: `yt-dlp --version`
- ffmpeg: `ffmpeg -version`
- Homebrew (só macOS): `brew --version`
- Config atual, se existir: `~/.sofia/config.yaml`

### 2. Oferecer a instalação do que faltar (com OK)

**A pessoa pode não saber usar o Terminal.** Por isso a Sofia explica em palavras simples, mostra o comando e pergunta antes. Use AskUserQuestion EM PORTUGUÊS, uma pergunta por ferramenta que falta.

Exemplo de pergunta:
> "Para ler os vídeos eu preciso do **yt-dlp** (baixa o vídeo e a legenda) e do **ffmpeg** (tira os quadros do vídeo). Posso instalar agora com este comando?
> `brew install yt-dlp ffmpeg`"

Opções: "Pode instalar" · "Prefiro instalar eu mesmo" · "Agora não".

Comandos por sistema (rodar só depois do "Pode instalar"):

| Sistema | yt-dlp e ffmpeg | Node.js |
|---|---|---|
| macOS com Homebrew | `brew install yt-dlp ffmpeg` | `brew install node` |
| macOS sem Homebrew | A pessoa instala o Homebrew sozinha, em https://brew.sh (pede a senha do computador). Depois volte ao passo 1. | idem |
| Linux | `python3 -m pip install --user yt-dlp`; o ffmpeg pelo gerenciador de pacotes do sistema, que pede senha: a pessoa roda sozinha | instalador oficial em https://nodejs.org |
| Windows | A pessoa roda sozinha, no PowerShell dela: `winget install yt-dlp.yt-dlp` e `winget install Gyan.FFmpeg`. O winget mostra os termos de uso e ela decide se aceita. | `winget install OpenJS.NodeJS.LTS`, rodado pela pessoa, do mesmo jeito |

Depois de instalar, rodar de novo o comando de versão.
- Se der certo: "✅ yt-dlp instalado."
- Se falhar: "Não consegui instalar o yt-dlp. O passo a passo oficial está em https://github.com/yt-dlp/yt-dlp#installation."
- Se a pessoa disser "Agora não": seguir. Sem yt-dlp e ffmpeg, a Sofia ainda escreve, critica e melhora roteiros; só não lê vídeos.

### 3. Mostrar resultado da verificação

> **Sofia 2.0 — Configuração inicial**
>
> Aqui está o que encontrei no seu computador:
>
> ✅ Node.js (v22.x)
> ✅ yt-dlp (2025.x)
> ✅ ffmpeg
> ⏸️ (o que ficou para depois)

### 4. Integrações opcionais

A análise visual, legendas disponíveis e métricas básicas de Instagram/TikTok funcionam sem chave de API. Apify é somente fallback para comentários que o `yt-dlp` não fornecer. Gemini é somente complemento de vídeo nativo; o padrão local já analisa a sequência visual.

Pergunte sobre Apify apenas quando o usuário quiser comentários de Instagram/TikTok e a extração gratuita falhar. Pergunte sobre Gemini apenas quando o usuário quiser a análise nativa opcional. Antes de usar Gemini, avise que o vídeo será enviado ao Google e peça autorização.

### 5. Chaves de API (Apify, Gemini, YouTube)

**Nunca peça para a pessoa colar a chave no chat**, e nunca grave chave dentro da pasta do plugin. Em ordem de preferência:

1. **Conector oficial do Apify (MCP).** Se as ferramentas `mcp__Apify__*` estiverem disponíveis, use-as: a chave fica no conector, não em arquivo.
2. **Variável de ambiente**, que a pessoa define no Terminal dela. Mostre o comando com um espaço reservado e deixe que ela troque pelo token:
   - macOS/Linux (zsh): `echo 'export APIFY_TOKEN="COLE_SEU_TOKEN_AQUI"' >> ~/.zshrc` e depois feche e abra o app Claude.
   - Windows (PowerShell): `setx APIFY_TOKEN "COLE_SEU_TOKEN_AQUI"` e depois feche e abra o app Claude.
   - Os nomes são `APIFY_TOKEN`, `GEMINI_API_KEY` e `YOUTUBE_API_KEY`.
3. **Arquivo fora do plugin**: `~/.sofia/chaves.env`, uma linha por chave (`APIFY_TOKEN=...`), criado pela pessoa. No macOS/Linux, sugira `chmod 600 ~/.sofia/chaves.env`. Os scripts da Sofia leem esse arquivo quando a variável de ambiente não existe.

Para conferir se a chave existe, verifique só se a variável está definida (`[ -n "$APIFY_TOKEN" ] && echo ok`). Nunca mostre a chave nem um pedaço dela.

Pergunta sobre o Apify (AskUserQuestion, EM PORTUGUÊS): "Você quer pegar comentários do Instagram e TikTok pelo Apify? É um serviço pago por uso, com crédito grátis todo mês."

Opções:
- "Já tenho conta" → explicar os 3 caminhos acima.
- "Quero criar conta" → mostrar:
  > 1. Crie a conta em **https://console.apify.com/sign-up**
  > 2. Pegue o token em **https://console.apify.com/account/integrations** ("Personal API tokens")
  > 3. Guarde o token como variável de ambiente (comando acima). Não precisa me mandar.
- "Não quero configurar agora" → pular. Avisar: "Sem o Apify, a Sofia continua lendo vídeo, fala e legenda; só não pega comentários do Instagram e TikTok quando o yt-dlp não conseguir."

### 6. Configurar onde salvar
Perguntar com AskUserQuestion EM PORTUGUÊS: "Onde quer que a Sofia salve as análises e roteiros?"

Opções:
- "Numa pasta Sofia dentro de Documentos" → `~/Documents/Sofia/`
- "No meu vault do Obsidian" → pedir o caminho do vault: "Me diga a pasta do seu vault (ex.: ~/Documents/MeuVault)." Se a pessoa não souber, pergunte: "Posso procurar pastas do Obsidian dentro da sua pasta pessoal?" e só com o "sim" rode `find ~ -maxdepth 4 -name ".obsidian" -type d 2>/dev/null | head -5`. Salvar em `{vault}/Sofia/`.
- "Escolher outro local" → pedir o caminho completo.

### 7. Salvar config
Criar a pasta `~/.sofia/` se não existir e gravar `~/.sofia/config.yaml` com as escolhas, a partir de `knowledge/config.exemplo.yaml`. **Sem chaves de API.** Incluir a data do setup e marcar `setup_completo: true`.

### 8. Teste rápido
Executar um teste:
```bash
yt-dlp --dump-json "https://www.youtube.com/watch?v=dQw4w9WgXcQ" 2>/dev/null | head -1
```
Se funcionar, confirmar. Se falhar, avisar o usuário.

### 9. Aprendizado de estilo de escrita

Depois de tudo configurado, perguntar:

> **Quer que a Sofia aprenda seu estilo de escrita?**
>
> Se sim, eu vou ler alguns dos seus melhores roteiros e aprender como você fala: tom de voz, ritmo das frases, palavras que usa, como abre os vídeos, o que evitar. Depois, quando escrever roteiros pra você, vou usar o seu jeito de escrever.

Usar AskUserQuestion EM PORTUGUÊS:

Pergunta: "Quer personalizar o estilo de escrita da Sofia?"

Opções:
- "Sim, quero que aprenda meu estilo" → Ir pro fluxo de aprendizado (abaixo)
- "Depois, quero usar primeiro" → Pular. Avisar: "Quando quiser, é só me pedir pra aprender seu estilo."

**Se sim — Fluxo de aprendizado de estilo:**

1. Perguntar sobre clientes:
   > "Você escreve roteiros só pra um perfil (o seu) ou pra clientes diferentes?"

   - **Um perfil só** → Criar 1 perfil em `~/.sofia/estilos/{nome}.md`
   - **Vários clientes** → Criar 1 perfil por cliente em `~/.sofia/estilos/{cliente}.md`. Explicar: "Cada cliente vai ter seu próprio estilo salvo. Quando for escrever, vou perguntar pra qual cliente."

2. Pedir roteiros:
   > "Me manda de 3 a 5 dos seus melhores roteiros (os que performaram melhor ou que mais representam como você fala). Pode colar aqui ou me mandar o link do arquivo."

3. Digerir e aprender. Para cada roteiro, extrair:
   - Tom de voz (sério, brincalhão, direto, provocador, reflexivo)
   - Ritmo (frases curtas ou longas, pausas, cadência)
   - Palavras e expressões recorrentes
   - Tipo de abertura mais comum
   - Tipo de fechamento mais comum
   - Estruturas preferidas
   - O que NÃO faz (identificar ausências como padrão)

4. Mostrar o perfil ao usuário pra validação:
   > "Aprendi isso sobre seu estilo. Veja se faz sentido:"
   > [mostrar perfil resumido]
   > "Tem algo errado ou que eu deva ajustar?"

5. Salvar em `~/.sofia/estilos/{nome}.md` seguindo o modelo `templates/estilo.md`.

6. Perguntar:
   > "Tem algo que você sabe que deve EVITAR nos roteiros? (palavra, tom, tipo de conteúdo)"

   Adicionar na seção "O que EVITAR" do perfil.

### 10. Mensagem final
Mostrar ao usuário:

> **✅ Sofia 2.0 configurada!**
>
> Agora você pode usar estes comandos:
>
> 📊 `/sofia:analisar` + link do vídeo — analisa por que um vídeo funciona
> ✍️ `/sofia:roteiro` — escreve um roteiro para vídeo viral
> 🔍 `/sofia:critica` — avalia um roteiro com honestidade
> 🔧 `/sofia:melhorar` — melhora um roteiro depois da crítica
> 📈 `/sofia:dashboard` — gera um painel visual
> 💾 `/sofia:exportar` — salva tudo em arquivos organizados
>
> **Dica:** comece com `/sofia:analisar` + o link de um vídeo que você admira!

## Modelo do config (`~/.sofia/config.yaml`)

```yaml
sofia:
  output_path: ""
  output_format: "obsidian"
  ambiente: "claude-code"
  setup_completo: true
  data_setup: ""
  estilo:
    configurado: false
    multiplos_clientes: false
    perfis: []
```
