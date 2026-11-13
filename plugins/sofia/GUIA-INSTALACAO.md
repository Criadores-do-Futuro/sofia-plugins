# Sofia 2.0 — Guia de Instalação e Uso

> O passo a passo mais detalhado da instalação está em `INSTALACAO.md`.

---

## O que é a Sofia?

A Sofia é uma assistente que vive dentro do Claude. Ela faz duas coisas:

1. **Pesquisa** — você manda o link de um vídeo viral e ela descobre por que aquele vídeo funcionou, frase por frase
2. **Escrita** — ela te ajuda a escrever roteiros para vídeos virais, fazendo perguntas e sugerindo ideias

---

## Passo 1: Crie suas contas

Antes de instalar, crie contas nestes serviços:

### Claude (obrigatório)

É onde a Sofia vive. Crie sua conta em [claude.ai](https://claude.ai).

Depois, baixe o app Claude no computador: [claude.ai/download](https://claude.ai/download) (Mac ou Windows).

### GitHub (obrigatório)

A Sofia é distribuída por um repositório privado. Sua conta do GitHub precisa ter acesso a `bento-dev-ia/sofia-plugins`, e o computador precisa estar autenticado no GitHub (por exemplo, com `gh auth login`).

### Apify (opcional, para Instagram/TikTok)

Serviço pago por uso que coleta comentários com curtidas do Instagram e TikTok. Crie sua conta em [apify.com](https://www.apify.com).

- A conta grátis vem com um crédito mensal; a Sofia mostra a estimativa de custo e pede seu OK antes de cada uso
- Para YouTube não precisa — o yt-dlp (grátis) já faz tudo

---

## Passo 2: Instale a Sofia

1. Abra o **app Claude** no seu computador
2. Vá na **aba Code**
3. Cole o primeiro comando e aperte **Enter**:

```
claude plugin marketplace add https://github.com/bento-dev-ia/sofia-plugins
```

4. Espere aparecer uma mensagem de confirmação
5. Agora cole o segundo comando e aperte **Enter**:

```
claude plugin install sofia@sofia-plugins
```

6. Espere aparecer a confirmação de que o plugin foi instalado

Pronto. A Sofia está instalada.

7. Agora **feche o app Claude** e **abra de novo**. Isso é necessário para o Claude reconhecer o plugin novo.

---

## Passo 3: Configure a Sofia

Depois de reabrir o Claude, digite:

```
/sofia:setup
```

A Sofia vai te guiar passo a passo e pedir seu OK antes de cada ação:

1. **Verifica o yt-dlp, o ffmpeg e o Node.js** — se faltar algo, mostra o comando de instalação e só instala se você disser sim
2. **Explica como ligar o Apify** — pelo conector oficial ou por variável de ambiente. A chave nunca é colada no chat. Se você não quiser, pula (YouTube funciona sem)
3. **Configura onde salvar** — pergunta onde fica sua pasta de saída (por exemplo, um vault do Obsidian). Só procura no computador se você autorizar
4. **Faz um teste** — extrai um vídeo curto para confirmar que tudo funciona
5. **Confirma** — mostra os comandos disponíveis

Depois do setup, você está pronto para usar.

---

## Como usar

### `/sofia:analisar` — Analisar um vídeo

Cole o link de um vídeo público e a Sofia busca tudo: texto falado, comentários mais curtidos, números, capa. Depois analisa frase por frase por que o vídeo funciona.

```
/sofia:analisar https://youtube.com/watch?v=XXXXX
/sofia:analisar https://instagram.com/reel/XXXXX
/sofia:analisar https://tiktok.com/@usuario/video/XXXXX
```

Funciona com YouTube, Instagram, TikTok e muitos outros sites. Se o vídeo exigir login, mande o arquivo.

### `/sofia:roteiro` — Escrever um roteiro

A Sofia faz perguntas sobre seu tema, público e o que as pessoas estão comentando. Depois sugere aberturas e escreve 2-3 versões do roteiro completo.

### `/sofia:critica` — Criticar um roteiro

Cole um roteiro (seu ou de outra pessoa) e ela avalia com honestidade.

### `/sofia:melhorar` — Melhorar um roteiro

Depois de uma crítica, ela reescreve corrigindo os problemas.

### `/sofia:dashboard` — Ver painel visual

Gera uma página com a análise completa do vídeo.

### `/sofia:exportar` — Exportar

Exporta análises e guarda o que a Sofia aprendeu na sua pasta de dados (`~/.sofia/`).

---

## Fluxo recomendado

```
1. Analise um vídeo viral que você admira
   /sofia:analisar + link do vídeo
         ↓
2. Estude a análise — entenda por que funciona
         ↓
3. Escreva seu próprio roteiro
   /sofia:roteiro
         ↓
4. Peça uma crítica honesta
   /sofia:critica
         ↓
5. Melhore com base na crítica
   /sofia:melhorar
         ↓
6. Repita! Quanto mais você analisa e escreve,
   melhor a Sofia fica
```

---

## Perguntas frequentes

### "Preciso pagar alguma coisa?"
Para YouTube, a extração é grátis. O Claude tem planos próprios. Para Instagram/TikTok, o Apify é opcional, pago por uso, e a conta grátis vem com crédito mensal. A Sofia pede seu OK antes de gastar.

### "Funciona no celular?"
Você pode despachar tarefas pelo celular usando o app Claude, mas a instalação precisa ser feita no computador.

### "Funciona no navegador (claude.ai)?"
Não. O navegador não suporta plugins. Use o app Claude ([claude.ai/download](https://claude.ai/download)).

### "Preciso usar o Terminal?"
Não. O app Claude tem interface visual. O Terminal é opcional.

### "Com quais sites a Sofia funciona?"
YouTube, Instagram, TikTok, Twitter/X, Reddit, Facebook, Twitch, Vimeo e muitos outros, desde que o vídeo seja público.

### "Preciso do Apify?"
Para YouTube: não. Para Instagram/TikTok: é recomendado. Sem ele, a Sofia não consegue pegar os comentários com curtidas e avisa o que ficou de fora.

### "Onde ficam meus dados?"
Na pasta `~/.sofia/` (configuração, estilos e aprendizados) e na pasta de saída que você escolher (análises e roteiros). Nada fica dentro da pasta do plugin.
