# Análise visual com evidências

Leia [comportamento](../comportamento.md). Escolha pela ferramenta realmente disponível, sem presumir recursos pelo nome do aplicativo.

## Escolher a fonte

- Arquivo de vídeo com terminal e ferramenta de imagens: prepare amostras locais e inspecione os quadros.
- Transcrição sem vídeo: analise fala e ordem narrativa; não conclua sobre imagem, cortes, gestos ou tom de voz.
- Capa isolada: analise somente a capa. Métricas e comentários não provam o que aparece no restante do vídeo.
- Endereço sem acesso: informe a limitação e peça o arquivo ou a transcrição. Não descreva o conteúdo a partir do título.
- Serviço externo: use apenas ferramenta disponível e autorizada; confira o esquema e o preço atual antes de chamar. Não há preço fixo nem ferramenta de coleta garantida neste pacote.

## Preparar vídeo

Identifique o caminho absoluto da raiz que contém `plugin.json`. Substitua os caminhos descritivos abaixo antes de executar; não dependa de variáveis específicas do Claude. Use uma pasta de saída nova e vazia.

```sh
python3 "/caminho/absoluto/do/plugin/scripts/prepare-visual-analysis.py" "/caminho/do/video.mp4" --output "/pasta/da/pessoa/analise-01" --max-frames 80
```

O preparador usa Python 3.10 ou posterior, `ffmpeg` e `ffprobe`. Não exige chave, não transcreve fala e não reconhece efeitos automaticamente. Para uma referência pública cujo uso foi autorizado, acrescente `--allow-download` e use seu endereço HTTPS; isso exige `yt-dlp`. O baixador ignora configuração externa e não usa cookies. Uma falha de login pede o arquivo, não um contorno.

Leia `manifest.json`; os campos técnicos indicam arquivo, intervalo analisado, caminhos e tempos de quadros decodificados. Abra as folhas de contato em ordem e os quadros individuais relevantes. Para texto pequeno ou movimento ambíguo, prepare uma segunda pasta com `--start` e `--end`, aumentando a densidade apenas nesse trecho. Uma amostra não permite afirmar ausência de cortes entre os quadros. Áudio extraído não equivale a fala ouvida ou transcrita.

## Analisar e entregar

Identifique tema, ideia final, formato, estrutura e recurso editorial com evidência. Relacione imagem e fala só quando ambos foram inspecionados. Cite tempos observados, diferenciando-os de inferência sobre o intervalo. Para cada trecho, explique o efeito em uma ou duas frases, sem repetir a transcrição inteira.

Métricas ausentes são indisponíveis. Não calcule taxas com denominador zero nem compare vídeos sem identificar a base. Comentários entram apenas com texto e curtidas, sem nome ou identificador de autor. Não use reação de alguns comentários como pesquisa representativa.

Para vários vídeos, compare abertura, estrutura, métricas disponíveis, padrão comum e variável distinta em um painel consolidado. Inclua uma seção de limites: quais imagens, fala, áudio, comentários e métricas realmente foram acessados. Se pedirem somente uma resposta curta ou o ambiente não criar arquivos, entregue o resumo em texto.
