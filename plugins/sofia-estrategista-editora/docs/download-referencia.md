# Baixar referência para estudo de estilo

O download é opcional e destinado a um vídeo individual acessível sem login,
com `yt-dlp` e `ffprobe` disponíveis. Ele respeita as restrições de acesso do
site; não lê cookies, sessão do navegador ou configuração pessoal do yt-dlp.
Playlists são recusadas. Use apenas referências que você tenha autorização para
baixar e analisar; a ferramenta não determina direitos de uso.

```sh
python3 scripts/baixar_referencia.py --url-stdin --saida /caminho/pasta-nova
```

Forneça o link pela entrada padrão; o comando imprime apenas o caminho local,
tamanho e hash, que podem ser usados no fluxo de análise de estilo. A pasta de
saída precisa ser nova, e nenhum vídeo existente é sobrescrito. O link e seus
parâmetros não são escritos no relatório nem em arquivo de metadados persistente
pelo script. O site e os processos necessários para o download podem receber o
link em memória; arquivos temporários de download são removidos ao fim. Use a
entrada padrão para evitar colocar o link nos argumentos do próprio script ou
no histórico do shell. Não publique logs, link assinado ou mídia sem necessidade.

A rede e as páginas acessadas dependem do provedor e do yt-dlp instalado. O
script rejeita hosts locais e endereços IP privados explícitos, mas não é uma
barreira de rede contra redirecionamentos ou resolução DNS interna: use apenas
links confiáveis. A análise posterior mede os quadros e o áudio; ela não garante
reconstruir parâmetros, efeitos ou edição original apenas pelo vídeo exportado.
