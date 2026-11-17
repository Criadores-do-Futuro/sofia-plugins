#!/bin/bash
# Mostra ao agente quais atores do Apify usar para Instagram e TikTok.
# Não chama o Apify e não gasta crédito: só imprime a instrução.
# Uso: ./apify-social.sh <instagram|tiktok> <url>
#
# A chave NUNCA fica na pasta do plugin. Ordem de busca:
#   1. variável de ambiente APIFY_TOKEN
#   2. arquivo ~/.sofia/chaves.env (linha APIFY_TOKEN=...), criado pela pessoa
# Com o conector oficial do Apify (ferramentas mcp__Apify__*), a chave nem é necessária aqui.
# O script nunca imprime a chave nem um pedaço dela.

PLATFORM="$1"
URL="$2"

if [ -z "$PLATFORM" ] || [ -z "$URL" ]; then
  echo "Uso: ./apify-social.sh <instagram|tiktok> <URL>"
  echo ""
  echo "Exemplos:"
  echo "  ./apify-social.sh instagram https://www.instagram.com/reel/ABC123/"
  echo "  ./apify-social.sh tiktok https://www.tiktok.com/@user/video/123456"
  exit 1
fi

TOKEN_OK="não"
if [ -n "$APIFY_TOKEN" ]; then
  TOKEN_OK="sim (variável de ambiente)"
elif [ -f "$HOME/.sofia/chaves.env" ] && grep -qE '^APIFY_TOKEN=.+' "$HOME/.sofia/chaves.env"; then
  TOKEN_OK="sim (~/.sofia/chaves.env)"
fi

echo "--- INSTRUÇÃO PARA O AGENTE ---"
echo "1. ANTES de chamar qualquer ator: confira o esquema e o preço atuais,"
echo "   diga à pessoa quantos vídeos, quais dados e a estimativa total e espere a autorização."
echo "2. Dos comentários, guarde só o texto literal, as curtidas e a data. Nada de @, nome ou foto de quem comentou."
echo ""

case "$PLATFORM" in
  instagram)
    echo "Instagram — URL: $URL"
    echo "Conteúdo do post:"
    echo "  Ator: apify/instagram-scraper"
    echo "  Input: { \"directUrls\": [\"$URL\"], \"resultsLimit\": 1 }"
    echo "Comentários:"
    echo "  Ator: apify/instagram-comment-scraper"
    echo "  Input: { \"directUrls\": [\"$URL\"], \"resultsLimit\": 20 }"
    ;;

  tiktok)
    echo "TikTok — URL: $URL"
    echo "Conteúdo do vídeo (mesmo ator da skill analisar):"
    echo "  Ator: clockworks/tiktok-video-scraper"
    echo "  Input: { \"postURLs\": [\"$URL\"], \"shouldDownloadVideos\": true, \"shouldDownloadCovers\": true, \"downloadSubtitlesOptions\": \"DOWNLOAD_SUBTITLES\" }"
    echo "Comentários:"
    echo "  Ator: clockworks/tiktok-comments-scraper"
    echo "  Input: { \"postURLs\": [\"$URL\"], \"commentsPerPost\": 20 }"
    ;;

  *)
    echo "Plataforma não suportada: $PLATFORM"
    echo "Use: instagram ou tiktok"
    exit 1
    ;;
esac

echo ""
echo "Token do Apify configurado: $TOKEN_OK"
if [ "$TOKEN_OK" = "não" ]; then
  echo "Sem token e sem conector do Apify: rode /sofia:setup (passo 'Chaves de API')."
fi
