# Conector: YouTube

## Estratégia econômica

### Prioridade 1: yt-dlp (GRÁTIS)
Para a maioria dos casos, yt-dlp resolve sem precisar de API key:
- Extrai transcrição (legendas automáticas/manuais)
- Extrai metadados (título, canal, views, likes, data)
- Extrai comentários (com --write-comments)

### Prioridade 2: YouTube Data API v3 (grátis com quota)
Apenas se yt-dlp não conseguir extrair comentários ordenados:
- 10.000 unidades/dia grátis
- `commentThreads.list` com `order=relevance`: 1 unidade por request
- Suficiente para ~200+ análises/dia

## Instalação do yt-dlp

A Sofia só instala com o OK da pessoa (ver `/sofia:setup`). Comando que pede senha de administrador ou aceite de termos a pessoa roda ela mesma.

### macOS
```bash
brew install yt-dlp
```

### Linux
```bash
python3 -m pip install --user yt-dlp
```

### Windows (a pessoa roda no terminal)
```bash
winget install yt-dlp.yt-dlp
```

### Verificar
```bash
yt-dlp --version
```

## YouTube Data API (opcional)

### Como ativar
1. Acesse https://console.cloud.google.com
2. Crie novo projeto ou selecione existente
3. APIs & Services → Enable APIs → YouTube Data API v3
4. Credentials → Create API Key
5. Copie a key

### Configurar na Sofia
A chave nunca vai para dentro da pasta do plugin e nunca é colada no chat. A pessoa escolhe um caminho e faz ela mesma:
- Variável de ambiente `YOUTUBE_API_KEY` (macOS/Linux: `echo 'export YOUTUBE_API_KEY="COLE_SUA_CHAVE_AQUI"' >> ~/.zshrc`; Windows: `setx YOUTUBE_API_KEY "COLE_SUA_CHAVE_AQUI"`), ou
- Linha `YOUTUBE_API_KEY=COLE_SUA_CHAVE_AQUI` em `~/.sofia/chaves.env`, protegido com `chmod 600`

### Uso para comentários
```bash
curl "https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId=VIDEO_ID&order=relevance&maxResults=20&key=$YOUTUBE_API_KEY"
```

Guarde só o texto literal, as curtidas e a data de cada comentário. Nunca o nome, o @ ou a foto de quem comentou.

## Quando usar cada um

| Necessidade | Ferramenta | Custo |
|-------------|-----------|-------|
| Transcrição | yt-dlp | Grátis |
| Metadados | yt-dlp | Grátis |
| Comentários (básico) | yt-dlp | Grátis |
| Comentários (ordenados por relevância) | YouTube API | Grátis (quota) |
| Thumbnail | yt-dlp ou API | Grátis |
