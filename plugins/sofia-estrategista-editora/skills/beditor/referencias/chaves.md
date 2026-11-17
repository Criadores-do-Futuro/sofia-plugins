# Chaves e contas — o que cada formato exige, e o que não exige

Levantamento de 15/09/2026, feito no código (não de memória): toda leitura de
variável de ambiente com segredo, todo serviço externo chamado, todo ponto que
pede conta. A conclusão curta, porque ela surpreende:

> **Editar e renderizar não precisa de chave nenhuma.** O pipeline inteiro do
> `analise` — transcrever, cortar, compor, medir, montar o master — roda em
> máquina local, sem rede e sem conta. Chave só aparece em duas bordas: **gerar
> imagem** e **publicar**.

## A única chave que o código lê

| Variável | Onde | Quem usa | Obrigatória? |
| --- | --- | --- | --- |
| `GEMINI_API_KEY` (ou `GOOGLE_API_KEY` como alternativa) | `~/.config/beditor/env`, ou o ambiente | só `assets.py`, e só na rota **Gemini imagem** | **Não.** Sem ela o script não falha: escreve `PROMPTS.md` com os prompts prontos, para gerar à mão onde você quiser |

Nenhum outro script do plugin lê segredo. `BEDITOR_MODELO_IMAGEM`,
`BEDITOR_CONFIG`, `BEDITOR_AVISOS`, `BEDITOR_SEM_AVISO` e `BEDITOR_ENTREGAS`
são configuração, não credencial.

**A chave nunca aparece em lugar nenhum.** `setup.py --verificar` responde
«presente» ou «ausente», jamais o valor; há teste que falha se o segredo
vazar para o JSON do diagnóstico. O arquivo de env é criado com `chmod 600`.

## Por formato criativo

| Formato / etapa | Precisa de chave? | O quê |
| --- | --- | --- |
| **`analise`** (comentário sobre o vídeo de outra pessoa) | **Não** | A-roll seu + material da midiateca + cartões desenhados localmente. `yt-dlp` baixa sem conta (vídeo restrito por idade ou login é a exceção, e aí são cookies do navegador, não chave) |
| **`dinamismo`** (take de câmera) | **Não**, a menos que use a rota Gemini | Corte, cartões, cama e legenda são locais |
| **Assets por rota** | depende da rota | HyperFrames (HTML/GSAP) local · Claude Design pela sessão · **Gemini imagem: `GEMINI_API_KEY`** · NotebookLM manual, fora do pipeline · Acervo é curadoria, não chave |
| **`aprender`** (estilo novo a partir de frames) | **Não** | Medição local de frames |
| **`branding`** | só se gerar imagem | O mesmo `assets.py` |
| **Transcrição** | **Não** | Whisper roda local (mlx-whisper na GPU da Apple, ou faster-whisper) |
| **Publicar** | **Sim, mas não como chave no disco** | Zernio e Metricool entram por **MCP**, autenticado no Claude Code (`/mcp`). O plugin nunca guarda token dessas contas; ele escreve `zernio.json` com o corpo do post e a sessão faz a chamada |
| **Painel de revisão** | **Não** | É um artifact da sua conta Claude; a autenticação é a da sessão |

## O que isso significa para distribuir

Quem receber o bEditor consegue **editar um vídeo inteiro sem criar conta em
lugar nenhum**. As duas coisas que pedem conta são opcionais e de quem instala:

1. **Gemini**, para gerar imagem — grátis até um limite generoso no AI Studio;
   sem ela, o plugin entrega os prompts em vez da imagem;
2. **Zernio ou Metricool**, para agendar publicação — conectados como MCP, na
   conta de quem publica.

Nenhum dos dois é do autor do plugin: não há chave compartilhada, nem servidor
no meio, nem custo que passe por terceiro. É por isso que o repositório pode ir
para qualquer forma de distribuição sem revisão de segredo — o que não impede a
regra óbvia: **chave nunca entra em commit, log, prova ou mídia**
(`portoes-de-qualidade.md`).

## Se um dia entrar outra chave

Três coisas juntas, ou não entra: (1) o `setup.py --verificar` passa a acusá-la
no grupo certo, dizendo para que serve e como obtê-la; (2) o script que a usa
**degrada sem ela** em vez de quebrar, como `assets.py` faz; (3) um teste prova
que o valor não sai em nenhuma saída do plugin.
