# Serviço opcional: YouTube

Leia [comportamento](../comportamento.md). Para analisar uma referência, prefira o arquivo ou a transcrição fornecida. Dados públicos podem ser coletados com `yt-dlp` apenas para material cujo uso foi autorizado; o programa deve ignorar configurações externas e não usar cookies nem sessão do navegador.

Os comandos de preparação visual e de download autorizado estão na [análise visual](../references/analise-de-video.md). Para metadados e comentários de um vídeo autorizado, use `yt-dlp --ignore-config --no-playlist --skip-download --write-info-json --write-comments` com o endereço HTTPS e leia do JSON só título, métricas públicas e, dos comentários, texto e curtidas.

A YouTube Data API é uma alternativa opcional quando houver uma ferramenta autorizada disponível. Confira as cotas e os custos atuais na documentação do provedor; não prometa acesso gratuito ilimitado nem uma quantidade fixa de análises. A ordem por relevância não é a mesma que uma ordenação estrita por curtidas.

A credencial fica no conector oficial que a pessoa instalou. Não leia chaves do ambiente ou de arquivos da máquina; nunca as peça na conversa, imprima ou salve no plugin. Retenha somente os campos necessários à análise; dos comentários, apenas texto literal e curtidas. Não transforme um erro de acesso em resultado vazio ou transcrição inventada.
