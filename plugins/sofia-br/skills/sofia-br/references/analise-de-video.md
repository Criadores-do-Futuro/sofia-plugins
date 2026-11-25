# Ver um vídeo de verdade: comandos locais

Este é o caminho opcional para quem tem terminal (Claude Code, Codex ou outro ambiente que roda comandos). Sem terminal, a análise é de texto: a Sofia lê a transcrição, a legenda ou os prints e diz quais camadas não viu. O fluxo completo da análise está em `fluxos/analisar`.

## Antes de rodar

- Confira se `ffmpeg` e `ffprobe` existem. `yt-dlp` só é preciso para baixar um vídeo público, e o Whisper só para transcrever o áudio. Se faltar algum, pergunte antes de instalar e diga em uma frase para que serve ("o ffmpeg tira fotos do vídeo para eu ver o que aparece na tela"). Instale só com o OK, pelo caminho oficial do sistema da pessoa.
- Use uma pasta nova e vazia para cada vídeo, na pasta de trabalho da pessoa ou numa pasta temporária, nunca dentro da instalação do plugin.
- Troque os caminhos do exemplo e os valores em maiúsculas antes de rodar, e ponha cada caminho entre aspas.

## Preparar o vídeo

1. Leia os dados técnicos:

   ```sh
   mkdir -p "/pasta/analise-01/frames" "/pasta/analise-01/contacts"
   ffprobe -v error -show_entries format=duration:stream=codec_type,width,height,r_frame_rate -of json "/caminho/do/video.mp4" > "/pasta/analise-01/metadata.json"
   ```

2. Pegue a duração `D` em segundos, escolha `N` quadros (no máximo 80; um a cada 2 ou 3 segundos num vídeo curto) e calcule o intervalo `I = D / N`. Extraia os quadros:

   ```sh
   ffmpeg -nostdin -hide_banner -loglevel error -i "/caminho/do/video.mp4" -vf "fps=1/I,scale='min(960,iw)':-2" -frames:v N -q:v 3 "/pasta/analise-01/frames/t-%05d.jpg"
   ```

   O quadro `k` fica perto de `(k − 1) × I` segundos. Esses tempos são aproximados, não pontos exatos de corte.

3. Só se `metadata.json` mostrar uma faixa de áudio, extraia o áudio:

   ```sh
   ffmpeg -nostdin -hide_banner -loglevel error -i "/caminho/do/video.mp4" -vn -ac 1 -ar 16000 -c:a libmp3lame -b:a 64k "/pasta/analise-01/audio.mp3"
   ```

   Para ter a fala, transcreva o áudio com o Whisper, na língua da fala, se ele estiver instalado ou se a pessoa deixar instalar. Áudio extraído não é fala ouvida.

4. Monte folhas de contato de 20 quadros cada:

   ```sh
   ffmpeg -nostdin -hide_banner -loglevel error -framerate 1 -i "/pasta/analise-01/frames/t-%05d.jpg" -vf "scale=240:-2,tile=5x4:padding=8:margin=8" "/pasta/analise-01/contacts/timeline-%03d.jpg"
   ```

## Olhar

- Abra as folhas de contato em ordem, e o quadro sozinho quando precisar ler texto pequeno, gesto, objeto ou corte.
- Se a sessão limita quantas imagens cabem numa mensagem, abra em lotes numerados, em ordem, e só conclua depois de ver todos.
- Para um trecho que decide a análise, prepare outra pasta vazia só para ele: ponha `-ss INICIO -to FIM` antes de `-i` no passo 2 e use um intervalo menor. Os tempos passam a contar a partir de `INICIO`.
- Uma amostra não prova que não houve corte entre os quadros. Varredura com intervalo grande nunca vira "vi o vídeo inteiro".
- Ao terminar, apague o vídeo baixado, o áudio e os quadros, a não ser que a pessoa peça para guardar. Na referência, guarde no máximo um quadro como capa.

## Baixar um vídeo público

Só depois de a pessoa confirmar que pode usar aquela referência, com o link HTTPS:

```sh
yt-dlp --ignore-config --no-playlist --no-progress --write-auto-subs --write-subs --sub-format "vtt/best" --merge-output-format mp4 -f "bv*+ba/b" -o "/pasta/analise-01/video.%(ext)s" -- "LINK"
```

O comando ignora configuração externa e não usa cookies. Se o site pedir login, pare: peça o arquivo à pessoa ou siga por outro caminho.

## Números e comentários pelo yt-dlp

Testado com vídeos públicos, sem login (observação do método; as redes mudam):

- **TikTok:** `yt-dlp --ignore-config --dump-json --skip-download "LINK"` traz visualizações (`view_count`), curtidas (`like_count`), comentários (`comment_count`), compartilhamentos (`repost_count`) e salvos (`save_count`). O texto dos comentários o TikTok só mostra com login.
- **YouTube:** o mesmo comando traz visualizações, curtidas e comentários, sem compartilhamentos nem salvos. Os comentários mais curtidos vêm com `yt-dlp --ignore-config --skip-download --write-comments --extractor-args "youtube:comment_sort=top;max_comments=20,all,0" --dump-json "LINK"`, no campo `comments`, cada um com `text` e `like_count`.
- **Instagram:** costuma trazer curtidas e o número de comentários, sem as visualizações e sem o texto dos comentários.

Do JSON, leia só o título, os números públicos e, dos comentários, o texto e as curtidas. Perfil inteiro do TikTok e posts do Instagram costumam falhar: siga para os caminhos de `servicos-externos`.
