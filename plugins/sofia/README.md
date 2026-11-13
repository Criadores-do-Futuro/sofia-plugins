# Sofia 2.0

Sistema de pesquisa e escrita de roteiros para conteúdo viral, guiado por princípios de Psicologia Cognitiva do Engajamento.

## Instalação

O marketplace `sofia-plugins` fica num repositório privado do GitHub. Para instalar, sua conta do GitHub precisa ter acesso a ele, e o git do computador precisa estar autenticado (por exemplo, com `gh auth login`).

### Pelo terminal

```bash
claude plugin marketplace add https://github.com/bento-dev-ia/sofia-plugins
claude plugin install sofia@sofia-plugins
```

### Dentro do Claude Code

```
/plugin marketplace add bento-dev-ia/sofia-plugins
/plugin install sofia@sofia-plugins
```

Depois de instalar, feche e abra o Claude de novo. O passo a passo para quem nunca usou terminal está em `INSTALACAO.md`.

### Atualizar

```bash
claude plugin update sofia@sofia-plugins
```

### Setup

Na primeira vez, digite `/sofia:setup`. A Sofia vai:
1. Verificar as dependências (yt-dlp, ffmpeg, Node.js) e, se faltar alguma, mostrar o comando e pedir seu OK antes de instalar
2. Oferecer integrações opcionais (Apify para comentários com curtidas; Gemini para análise do vídeo inteiro)
3. Configurar a pasta de saída
4. Testar a extração com um vídeo curto

## Conteúdo que vem pelo conector

Alguns exemplos analisados e a base de assuntos que já deram resultado não vêm dentro do plugin. Eles chegam pelo conector de conteúdo da Sofia (MCP `sofia-conteudo`). Sem o conector, a Sofia avisa e segue sem essas peças.

## Onde a Sofia guarda os seus dados

Nada é gravado dentro da pasta do plugin, que é trocada a cada atualização.

| O quê | Onde |
|---|---|
| Configuração | `~/.sofia/config.yaml` (no Windows, `%USERPROFILE%\.sofia\config.yaml`) |
| Perfis de estilo de escrita | `~/.sofia/estilos/` |
| Aprendizados (hooks, padrões, insights) | `~/.sofia/aprendizados/` |
| Exemplos que você guardou | `~/.sofia/exemplos-analisados/` |
| Análises, roteiros, dashboard e exportações | a pasta de saída (`output_path` no config) |

### Chaves de API

As chaves (Apify, Gemini, YouTube) nunca ficam na pasta do plugin e nunca são coladas no chat. Use, nesta ordem de preferência:
1. O conector oficial do serviço (por exemplo, o MCP do Apify)
2. Variáveis de ambiente: `APIFY_TOKEN`, `GEMINI_API_KEY`, `YOUTUBE_API_KEY`
3. O arquivo `~/.sofia/chaves.env`, criado por você e protegido com `chmod 600`

O `/sofia:setup` explica cada caminho.

## Uso rápido

### Analisar vídeo
> "Analisa esse vídeo: [link]"

O sistema baixa o vídeo público, inspeciona visualmente cenas e linha do tempo, cruza imagem com fala e comentários, e analisa quais princípios estão sendo aplicados. YouTube, Instagram e TikTok seguem o mesmo fluxo. Se a plataforma exigir login para ver o vídeo, a Sofia não contorna: ela pede que você mande o arquivo do vídeo.

### Análise visual

- Padrão: local, sem chave de API, com `yt-dlp` + `ffmpeg` e leitura dos quadros pelo Claude.
- Opcional: vídeo completo enviado ao Gemini quando `GEMINI_API_KEY` estiver configurada e você autorizar o envio.
- TikTok: aceita links completos e links curtos `vm.tiktok.com`/`vt.tiktok.com`.
- Apify é pago por uso: a Sofia mostra a estimativa de custo e pede seu OK antes de cada lote.

### Escrever roteiro
> "Quero escrever um roteiro sobre [tema] para [nicho]"

O sistema faz perguntas, sugere hooks, oferece estruturas, escreve versões e oferece crítica.

### Crítica de roteiro
> "Faz uma crítica desse roteiro: [texto]"

Avaliação honesta de quais princípios estão funcionando e quais falharam.

## Onde funciona

| Plataforma | Suporte |
|---|---|
| App Claude (Code) | Sim |
| App Claude (Cowork) | Sim |
| Claude Code (Terminal) | Sim |
| Claude.ai (navegador) | Não |

## Princípios-guia (hierarquia)

1. **Tema** — O tamanho do mundo que pode se importar
2. **Familiaridade** — Reconhecimento que reduz custo de entrada
3. **Conflito e Mudança** — Transições que geram emoção
4. **Curiosidade e Debate Mental** — Lacunas que sustentam atenção
5. **Aha e Ausência Deliberada** — Recompensa ou externalização

## Estrutura

```
agents/          — 6 agentes especializados
skills/          — 7 skills conversacionais
references/      — princípios, formatos, estruturas, elementos viciantes
scripts/         — extração de dados (YouTube, Instagram, TikTok)
checklists/      — pré-escrita, pós-escrita, análise
templates/       — formatos de saída e modelo de perfil de estilo
knowledge/       — base inicial de conhecimento (só leitura) e config.exemplo.yaml
connectors/      — como ligar Apify, YouTube e Obsidian
```

## Licença

Software proprietário. Todos os direitos reservados. Veja o arquivo `LICENSE` na raiz do repositório `sofia-plugins`.

`references/sem-slop.md` adapta material de terceiros sob licença MIT; o aviso de licença está no próprio arquivo.
