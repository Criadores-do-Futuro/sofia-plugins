# Análise visual com evidências

Leia [comportamento](../comportamento.md). Escolha pela ferramenta realmente disponível, sem presumir recursos pelo nome do aplicativo.

## Escolher a fonte

- Arquivo de vídeo com terminal e ferramenta de imagens: prepare amostras locais e inspecione os quadros.
- Transcrição sem vídeo: analise fala e ordem narrativa; não conclua sobre imagem, cortes, gestos ou tom de voz.
- Capa isolada: analise somente a capa. Métricas e comentários não provam o que aparece no restante do vídeo.
- Endereço sem acesso: informe a limitação e peça o arquivo ou a transcrição. Não descreva o conteúdo a partir do título.
- Serviço externo: use apenas ferramenta disponível e autorizada; confira o esquema e o preço atual antes de chamar. Não há preço fixo nem ferramenta de coleta garantida neste pacote.

## Preparar vídeo

A preparação roda `ffprobe` e `ffmpeg` diretamente; não exige chave, não transcreve fala e não reconhece efeitos automaticamente. Use uma pasta de saída nova e vazia, na pasta de trabalho da pessoa, nunca dentro da instalação do plugin. Substitua os caminhos do exemplo e os valores em maiúsculas antes de executar cada comando, e coloque cada caminho entre aspas.

1. Leia os dados técnicos e salve:

   ```sh
   mkdir -p "/pasta/da/pessoa/analise-01/frames" "/pasta/da/pessoa/analise-01/contacts"
   ffprobe -v error -show_entries format=duration:stream=codec_type,width,height,r_frame_rate -of json "/caminho/do/video.mp4" > "/pasta/da/pessoa/analise-01/metadata.json"
   ```

2. Pegue a duração `D` em segundos, escolha `N` quadros (no máximo 80) e calcule o intervalo `I = D / N`. Extraia os quadros:

   ```sh
   ffmpeg -nostdin -hide_banner -loglevel error -i "/caminho/do/video.mp4" -vf "fps=1/I,scale='min(960,iw)':-2" -frames:v N -q:v 3 "/pasta/da/pessoa/analise-01/frames/t-%05d.jpg"
   ```

   O quadro `k` fica perto de `(k − 1) × I` segundos. Trate esses tempos como aproximados, não como pontos exatos de corte.

3. Só se `metadata.json` mostrar uma faixa de áudio, extraia:

   ```sh
   ffmpeg -nostdin -hide_banner -loglevel error -i "/caminho/do/video.mp4" -vn -ac 1 -ar 16000 -c:a libmp3lame -b:a 64k "/pasta/da/pessoa/analise-01/audio.mp3"
   ```

4. Monte folhas de contato de 20 quadros cada:

   ```sh
   ffmpeg -nostdin -hide_banner -loglevel error -framerate 1 -i "/pasta/da/pessoa/analise-01/frames/t-%05d.jpg" -vf "scale=240:-2,tile=5x4:padding=8:margin=8" "/pasta/da/pessoa/analise-01/contacts/timeline-%03d.jpg"
   ```

Abra as folhas de contato em ordem e os quadros individuais relevantes. Para texto pequeno ou movimento ambíguo, prepare outra pasta vazia só para esse trecho: acrescente `-ss INICIO -to FIM` antes de `-i` no passo 2 e use um intervalo menor; os tempos passam a contar a partir de `INICIO`. Uma amostra não permite afirmar ausência de cortes entre os quadros. Áudio extraído não equivale a fala ouvida ou transcrita.

Para uma referência pública cujo uso foi autorizado, baixe só depois dessa autorização, com o endereço HTTPS do YouTube, Instagram ou TikTok; isso exige `yt-dlp`:

```sh
yt-dlp --ignore-config --no-playlist --no-progress --write-auto-subs --write-subs --sub-format "vtt/best" --merge-output-format mp4 -f "bv*+ba/b" -o "/pasta/da/pessoa/analise-01/video.%(ext)s" -- "https://www.youtube.com/watch?v=EXEMPLO"
```

O comando ignora configuração externa e não usa cookies. Uma falha de login pede o arquivo, não um contorno.

## Analisar e entregar

Identifique tema, ideia final, formato, estrutura e recurso editorial com evidência. Relacione imagem e fala só quando ambos foram inspecionados. Cite tempos observados, diferenciando-os de inferência sobre o intervalo. Para cada trecho, explique o efeito em uma ou duas frases, sem repetir a transcrição inteira.

Métricas ausentes são indisponíveis. Não calcule taxas com denominador zero nem compare vídeos sem identificar a base. Comentários entram apenas com texto e curtidas, sem nome ou identificador de autor. Não use reação de alguns comentários como pesquisa representativa.

Para vários vídeos, compare abertura, estrutura, métricas disponíveis, padrão comum e variável distinta em um painel consolidado. Inclua uma seção de limites: quais imagens, fala, áudio, comentários e métricas realmente foram acessados. Se pedirem somente uma resposta curta ou o ambiente não criar arquivos, entregue o resumo em texto.
