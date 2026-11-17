# Criar um guia de estilo a partir de referências

Para executar medição, criação de capa e cadastro em uma única etapa, com
transcrição opcional por modelo local, use:

```sh
python3 scripts/preparar_estilo.py /caminho/referencia.mp4 --nome "Meu estilo" \
  --id meu-estilo --analise /caminho/analise-nova --biblioteca /caminho/biblioteca \
  --modelo /caminho/modelo-local.pt
```

Omitir `--modelo` pula a transcrição. O comando não inclui o texto da fala no
manual por padrão, mas gera o arquivo de transcrição na pasta de análise; guarde
essa pasta como dado privado. A pasta de análise deve ser nova. O resultado é
uma medição inicial e exige revisão audiovisual.

Para executar as etapas separadamente, com FFmpeg e ffprobe no PATH:

```sh
python3 scripts/analisar_referencias_estilo.py "/caminho/referencia-1.mp4" "/caminho/referencia-2.mp4" --nome "Meu estilo" --saida "/caminho/analise-nova"
python3 scripts/biblioteca_estilos.py --raiz "/caminho/biblioteca" cadastrar --id meu-estilo --nome "Meu estilo" --manual "/caminho/analise-nova/manual.json" --capa "/caminho/analise-nova/capa.jpg"
python3 scripts/biblioteca_estilos.py --raiz "/caminho/biblioteca" listar --json
python3 scripts/biblioteca_estilos.py --raiz "/caminho/biblioteca" mostrar meu-estilo --manual
```

Cada vídeo deve ser um arquivo local diferente e a pasta de saída deve ser nova;
a pasta superior já deve existir. Os vídeos originais não são copiados nem
alterados. Se a análise falhar, os arquivos parciais ficam nessa pasta para
inspeção e não são um resultado concluído; use outra pasta para nova tentativa.

Para cada referência, o pipeline mede quadros decodificados e verifica o total
quando disponível, mede cada trilha de áudio ou registra sua ausência,
identifica candidatos de mudança visual e calcula SHA-256 antes e depois para
identificar mudança da fonte durante a análise. O resultado inclui relatórios
por referência, manual inicial, capa extraída da primeira referência e
`analise.json` com fontes, hashes e limites. Registre esse manual na biblioteca
com o segundo comando; ele não é cadastrado automaticamente. A capa é um quadro
selecionado no meio do vídeo, não uma capa desenhada ou validada editorialmente.

Isso é uma **medição técnica inicial**, não entendimento semântico de cada
quadro nem de todos os sons: transcrição, reconhecimento de legendas e fontes,
tracking, máscaras, efeitos, critérios de sound effects, além de inspeção do
projeto original, ainda precisam de análise audiovisual e ferramentas próprias.
Movimentos e flashes podem causar falsos candidatos de corte, e mudanças sutis
podem não ser detectadas. A ausência de marcador não prova ausência de efeito.
O manual inicial incorpora somente a primeira trilha; os relatórios separados
contêm as medições das demais trilhas. Consulte as evidências e revise em imagem, áudio e timeline antes de
reutilizar o estilo.
