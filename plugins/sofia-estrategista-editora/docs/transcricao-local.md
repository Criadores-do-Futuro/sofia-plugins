# Transcrição local de uma referência

A transcrição opcional usa `ffprobe`, `ffmpeg`, o comando `whisper` da biblioteca
OpenAI Whisper e um arquivo de modelo `.pt` já existente no computador. O caminho
do modelo é obrigatório e passado diretamente ao Whisper; este fluxo não busca
nem baixa modelos. Use somente modelos obtidos de origem confiável: modelos `.pt`
podem conter dados serializados que exigem confiança na origem.

```sh
python3 scripts/transcrever_referencia.py /caminho/referencia.mp4 \
  --modelo /caminho/modelo-local.pt --saida /caminho/transcricao-nova.json
```

Sem `--trilha`, usa a primeira trilha de áudio. Para escolher outra, informe seu
índice absoluto mostrado no `ref-N-trilhas-audio.json`, por exemplo `--trilha 2`.
O idioma padrão é português (`--idioma pt`). O script extrai áudio mono temporário
para 16 kHz e o remove depois, juntamente com o JSON intermediário do Whisper.
O arquivo final não sobrescreve um existente.

Cada segmento contém texto, início e fim; quando o Whisper fornece palavras com
marcação temporal, elas são preservadas com sua probabilidade quando disponível.
Se o início do áudio e do contêiner forem conhecidos, os tempos são deslocados
para o referencial do contêiner; caso contrário, são relativos ao início da
trilha e o JSON marca essa limitação. A transcrição é uma estimativa: confira
palavras, nomes e sincronia escutando a referência. Ela não reconhece música,
efeitos sonoros, intenção ou todos os detalhes da edição. A transcrição não é
adicionada automaticamente ao manual ou à timeline; consulte-a junto aos
relatórios gerados por `analisar_referencias_estilo.py`.

Para registrar os intervalos de fala como inferências no manual existente:

```sh
python3 scripts/adicionar_transcricao_ao_manual.py manual.json transcricao.json \
  --referencia ref-1 --saida manual-com-fala.json
```

O comando verifica a origem e os tempos, preserva o manual original e não inclui
as palavras por padrão. Use `--incluir-texto` somente quando quiser guardar a
transcrição no manual, pois ela pode conter informações privadas. A identificação
automática precisa de revisão auditiva e não determina a intenção editorial.
