# Serviço opcional: YouTube

Leia [comportamento](../comportamento.md). Para analisar uma referência, prefira o arquivo ou a transcrição fornecida. Dados públicos podem ser coletados com `yt-dlp` apenas para material cujo uso foi autorizado; o programa deve ignorar configurações externas e não usar cookies nem sessão do navegador.

O preparador visual está em `scripts/prepare-visual-analysis.py`. A coleta de metadados e comentários sem dados do autor está em `scripts/collect-public.py`. Ambos recebem argumentos por lista, recusam endereços não permitidos e exigem `--allow-download` para coleta pela rede. Os atalhos de extração antigos encaminham para esses programas; use as opções indicadas em `--help`, não um argumento posicional de idioma.

A YouTube Data API é uma alternativa opcional quando houver uma ferramenta autorizada disponível. Confira as cotas e os custos atuais na documentação do provedor; não prometa acesso gratuito ilimitado nem uma quantidade fixa de análises. A ordem por relevância não é a mesma que uma ordenação estrita por curtidas.

A pessoa configura a credencial no provedor ou no ambiente. Nunca a peça na conversa, imprima ou salve no plugin. Retenha somente os campos necessários à análise; dos comentários, apenas texto literal e curtidas. Não transforme um erro de acesso em resultado vazio ou transcrição inventada.
