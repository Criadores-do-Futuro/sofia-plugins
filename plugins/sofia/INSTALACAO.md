# Sofia 2.0 — Como Instalar

## O que precisa antes de começar

- Um computador (Mac ou Windows)
- Conexão com a internet
- Uma conta do GitHub com acesso ao repositório `bento-dev-ia/sofia-plugins` (ele é privado)

## Passo 1: Crie sua conta no Claude

1. Acesse **claude.ai** no navegador
2. Clique em **Sign up** e crie sua conta (pode usar email ou conta Google)
3. Depois de criar, baixe o **app Claude** no computador em **claude.ai/download**
4. Instale o app normalmente (arrastar para a pasta Aplicativos no Mac, ou clicar em Instalar no Windows)
5. Abra o app e faça login com a conta que você criou

## Passo 2: Instale a Sofia

Como o repositório é privado, o computador precisa estar autenticado no GitHub. Se você usa o GitHub CLI, rode `gh auth login` uma vez antes.

1. No app Claude, clique na **aba Code** (fica no topo da tela)
2. No campo de texto, cole este comando e aperte **Enter**:

```
claude plugin marketplace add https://github.com/bento-dev-ia/sofia-plugins
```

3. Espere aparecer uma mensagem de confirmação
4. Agora cole este **segundo comando** e aperte **Enter**:

```
claude plugin install sofia@sofia-plugins
```

5. Espere a confirmação de que o plugin foi instalado
6. **Feche o app Claude** e **abra de novo** — isso é necessário para ele reconhecer a Sofia

## Passo 3: Configure a Sofia

1. No app Claude (depois de reabrir), digite no campo de texto:

```
/sofia:setup
```

2. A Sofia te guia passo a passo e pede seu OK antes de cada coisa:
   - Confere o que falta no seu computador (yt-dlp, ffmpeg, Node.js), mostra o comando de instalação e só instala se você disser sim. O que pede senha de administrador ou aceite de termos você mesmo roda
   - Explica como ligar o Apify, se você quiser analisar Instagram/TikTok
   - Pergunta onde salvar seus arquivos
   - Faz um teste para confirmar que está tudo funcionando

### Sobre o Apify (opcional)

O Apify é um serviço pago por uso que pega os comentários com curtidas do Instagram e TikTok. Para YouTube, não precisa. A conta grátis vem com um crédito mensal, e a Sofia sempre mostra a estimativa de custo e pede seu OK antes de usar.

Se quiser configurar:
1. Crie uma conta em **console.apify.com/sign-up**
2. O jeito mais simples é instalar o conector oficial do Apify no Claude. Assim a Sofia usa o Apify sem ver a sua chave
3. Se preferir a chave: acesse **console.apify.com/account/integrations**, copie o token de "Personal API tokens" e guarde numa variável de ambiente chamada `APIFY_TOKEN` (o `/sofia:setup` mostra o comando). **Não cole o token no chat**

## Pronto!

A Sofia está instalada e configurada. Agora é só usar.

---

## Como atualizar a Sofia

Quando sair uma versão nova, abra o app Claude na **aba Code** e cole:

```
claude plugin update sofia@sofia-plugins
```

Depois, **feche o app Claude** e **abra de novo** para a atualização funcionar. Seus dados ficam em `~/.sofia/` e não são apagados na atualização.

---

## Como usar a Sofia

Você não precisa decorar nada. É só conversar com ela no app Claude.

### Analisar um vídeo viral

Cole o link de um vídeo público e peça para a Sofia analisar. Ela descobre o texto falado, os comentários mais curtidos e explica por que o vídeo funciona.

Exemplo: "Sofia, analisa esse vídeo: https://youtube.com/watch?v=XXXXX"

Funciona com YouTube, Instagram, TikTok e outros sites. Se o vídeo exigir login para ser visto, mande o arquivo do vídeo.

### Escrever um roteiro

Peça para a Sofia te ajudar a escrever um roteiro. Ela faz perguntas sobre seu tema e seu público, sugere aberturas e escreve 2-3 versões completas.

### Criticar um roteiro

Cole um roteiro (seu ou de outra pessoa) e peça uma crítica honesta. Ela avalia o que está bom e o que precisa melhorar.

### Melhorar um roteiro

Depois de uma crítica, peça para ela reescrever corrigindo os problemas.

---

## Modo recomendado de uso

1. **Analise** um vídeo viral que você admira
2. **Estude** a análise — entenda por que funciona
3. **Escreva** seu próprio roteiro sobre um tema parecido
4. **Peça uma crítica** honesta
5. **Melhore** com base na crítica
6. **Repita** — quanto mais você analisa e escreve, melhor a Sofia fica

**Dica:** analise pelo menos 3 vídeos virais do seu nicho antes de escrever seu primeiro roteiro.
