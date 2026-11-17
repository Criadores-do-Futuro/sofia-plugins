# Aprendizado de estilo

Receba um ou mais vídeos ou links autorizados e preserve origem, licença,
identidade do arquivo, duração, taxa de quadros e limitações. Baixe quando
necessário com ferramenta disponível e sem contornar restrições de acesso.
Analise todos os quadros decodificados em ordem, incluindo timestamps reais;
registre contagens esperadas e processadas e interrupções. Vídeos longos exigem
processamento em lotes e cache por identidade, sem gerar milhares de imagens à toa.

Leia e escute também o áudio: cortes e J/L-cuts exigem comparar o som e a imagem;
analise falas, pausas, música, dinâmica e efeitos com as ferramentas realmente
disponíveis. Analise texto na tela, legenda e lettering separadamente. Compare
enquadramento, movimentos, cor, cortes, transições, máscaras e efeitos com
evidência temporal; retorne `não observado`, `hipótese` ou `não verificável`
quando apropriado. Quadros isolados não revelam automaticamente fonte exata,
projeto original, camadas, intenção, direitos ou configurações do editor.

Um manual útil contém amostras com tempo e fonte, regras recorrentes e exceções,
medidas verificadas, exemplos de abertura, cortes, movimentos, tipografia,
legenda, cor, áudio e ritmo; diferencie características comuns das exclusivas
de cada referência. Inclua confiança e lacunas. Compare uma prévia do novo vídeo
com os exemplos e itere nos desvios relevantes, sem prometer igualdade perfeita.
Preserve identidade do usuário e não copie marcas, textos ou provas como se fossem
dele. Guarde feedback aprovado no projeto; alterar regras globais requer pedido.

O script `scripts/analisar_quadros.py`, relativo à pasta da skill,
mede luminosidade, saturação e mudança visual por quadro
com FFmpeg; é apenas uma camada quantitativa, não uma análise semântica completa.

## O que oferecer ao usuário

Diga que ele pode enviar um ou mais vídeos de referência, links acessíveis ou,
quando houver, o projeto original do editor. Inventarie e processe cada quadro
decodificado e a trilha completa; analise visualmente e auditivamente em blocos,
com cobertura e evidências temporais. Se o projeto e ferramentas permitirem,
inspecione as pistas, parâmetros e keyframes originais sem alterá-los.

No guia, registre exemplos e exceções com tempo, duração, critérios e confiança:
cortes e J/L cuts; transições; composição, divisão de tela, tela verde e máscaras;
câmera, tracking, zoom e movimento dos elementos; legendas e mudanças de posição;
lettering, fontes, entradas e saídas; cor e sombras; ritmo; música e efeitos
sonoros, seus momentos e critérios de uso. Diferencie fatos medidos, hipóteses e
itens não verificáveis; nenhum processador atual entende automaticamente todos
esses aspectos. Compare múltiplas referências sem apagar divergências.

Guarde nome, descrição, capa, referências e manual em uma biblioteca de estilos
do projeto; preserve origem e direitos informados e não exponha credenciais.
Mostre capa e descrição ao listar; carregue o manual escolhido durante a direção.
Sugira estilos relevantes quando nenhum for escolhido e respeite a opção de não
utilizar estilo. Não use um estilo diferente como se tivesse sido escolhido.

O script `scripts/detectar_mudancas_visuais.py` produz candidatos de mudança
a partir da análise por quadro; eles exigem revisão e não são cortes confirmados.

No checkout completo, `python3 scripts/biblioteca_estilos.py --raiz PASTA
cadastrar --id ID --nome NOME --manual MANUAL.json --capa CAPA.png` cadastra
um manual v1 validado e a capa opcional; `listar --json` lista inclusive caminhos
das capas e `mostrar ID --manual` carrega o manual se íntegro. A raiz também pode
ser fornecida pela variável `BIBLIOTECA_ESTILOS_RAIZ`. Os vídeos de origem não
são copiados por esse comando: guarde sua localização e origem no manual e use
somente fontes acessíveis e autorizadas. A biblioteca é local, não sincroniza
automaticamente entre máquinas, e ainda não tem interface de galeria própria.

No checkout completo, siga `docs/analise-de-estilo.md` para processar múltiplas
referências locais em um comando e gerar relatórios, manual inicial e capa antes
do cadastro. O pipeline mede todas as trilhas de áudio em relatórios separados; o manual
inicial incorpora somente a primeira. Não executa interpretação semântica; não trate a medição como análise completa de estilo.

Para links públicos individuais, `docs/download-referencia.md` descreve como
baixar com yt-dlp sem cookies nem sobrescrever e depois analisar o arquivo local.
Para inspeção visual em blocos, `scripts/gerar_pranchas_quadros.py` gera pranchas
de todos os quadros decodificados e registra a cobertura; ler pranchas não prova
que a IA compreendeu todos os detalhes ou ouviu a trilha sonora.

Quando disponível um modelo Whisper já existente e confiável, a transcrição
local opcional em `docs/transcricao-local.md` registra a fala e tempos estimados
por palavra; revise ouvindo a referência. Para outras trilhas, execute por índice.

Após a revisão visual e auditiva, `docs/enriquecer-manual-estilo.md` descreve
como acrescentar observações e evidências temporais em uma nova versão do manual.
A validação confirma referências e intervalos, não a veracidade da interpretação.
