# Analisar vídeo

O Piso e a linguagem de 8 anos do SKILL.md valem aqui também, na análise e na conversa.

**Com o conector ligado:** leia antes a peça `instrucoes/ler-videos` do `sofia_metodo`, que vale mais que esta página. Ao terminar, guarde o que serve: vídeo de outra pessoa vira referência (`referencia_salvar`, com até 20 comentários entre os mais curtidos, literais, sem @ e sem nome de quem escreveu), avaliação de perfil vai para `perfil_salvar_avaliacao`, e o que funcionou no perfil da pessoa pode ir para o cérebro (`cerebro_guardar`, camada `o-que-funcionou`), com o OK dela. Avise em uma linha o que salvou e onde ela vê. Fale de resultado contra o normal do perfil ("2 vezes o normal do perfil"). Vários vídeos no mesmo pedido viram uma análise só, comparando os vídeos.

## O que você consegue fazer

Você vê imagens. Um vídeo vira uma sequência de quadros em ordem, e cada quadro você abre, lê o texto na tela, vê o corte, o enquadramento e o gesto. O que às vezes falta é acesso ao arquivo: algumas redes bloqueiam o download em alguns lugares.

Nunca diga que não consegue analisar vídeo. Diga qual caminho está disponível e o que ele entrega.

## Escolha o caminho pela superfície

Olhe o que a superfície onde você está consegue fazer. Não tente um caminho que ela bloqueia, e não peça para a pessoa escolher o caminho técnico.

| Caminho | Onde costuma valer | O que entrega |
|---|---|---|
| A: rodar comandos | Claude Code, Claude Desktop com acesso a arquivos, outro terminal com acesso a arquivos | Quadros, fala e números. Análise completa |
| B: receber arquivo | Chat no navegador ou no celular | Com o vídeo enviado e uma ferramenta de rodar código, análise completa. Só com imagens, a análise dos prints que a pessoa mandar |
| C: abrir páginas | Superfícies com navegação na web | A capa, a legenda e o texto público da página |
| D: só texto | Qualquer superfície | A legenda, a transcrição ou o que a pessoa colar. Sem análise de imagem |

- **Claude Code ou outro terminal:** caminho A.
- **Claude no navegador ou no celular:** peça o upload do vídeo. Sem o arquivo, siga para o caminho C ou D e diga o que ficou de fora.
- **Outro chat:** se a conversa aceita o arquivo de vídeo e roda código, use o caminho A com o arquivo enviado. Se não, peça prints do começo, do meio e do fim do vídeo e, no YouTube, a transcrição que aparece embaixo do vídeo.

Muitos quadros: se a superfície limita quantas imagens cabem numa mensagem, mande em lotes numerados, em ordem, e só conclua depois de ver todos. Folha de contato serve para varrer a linha do tempo. Abra o quadro sozinho quando precisar ler texto, gesto, objeto ou corte. Em vídeo longo, faça uma passada ampla e depois volte só nos trechos que importam. Varredura com intervalo grande nunca vira "vi o vídeo inteiro".

## Caminho A: rodar comandos

1. Resolva `SKILL_DIR` como a pasta que contém o `SKILL.md` desta skill.
2. Confira se `ffmpeg` e `yt-dlp` existem. Se faltar algum, pergunte antes de instalar e diga em uma frase para que serve ("o yt-dlp baixa o vídeo público para eu ver os quadros"). Só instale com o OK.
3. Rode, com o arquivo ou com o link de um vídeo público:

```bash
python3 "${SKILL_DIR}/scripts/prepare-visual-analysis.py" "ARQUIVO_OU_LINK" --output "PASTA_TEMPORARIA/sofia-visual-IDENTIFICADOR"
```

4. Leia o `manifest.json` e abra todas as folhas de `contacts/`, na ordem.
5. Abra quadros de `frames/` e `scenes/` quando houver texto pequeno, corte rápido, gesto ou ação que não ficou clara.
6. Cruze os segundos do manifesto com a legenda, a transcrição e o `audio.mp3`. Sem legenda, transcreva o áudio com o Whisper, se ele estiver instalado ou se a pessoa deixar instalar.
7. Se um trecho decide a análise, rode de novo só nele: `--start SEGUNDO --end SEGUNDO --max-frames 40`.
8. Ao terminar, apague o vídeo, o áudio e os quadros baixados.

Se o script falhar, o `ffmpeg` resolve na mão:

```bash
ffprobe -v error -show_entries format=duration -of csv=p=0 video.mp4
mkdir -p frames && ffmpeg -i video.mp4 -vf fps=1/3 frames/f_%03d.jpg -hide_banner -loglevel error
ffmpeg -i video.mp4 -vn -acodec libmp3lame audio.mp3 -hide_banner -loglevel error
```

Depois abra os `.jpg` de verdade. Não descreva quadro que você não olhou.

Fala e números de um vídeo público:

```bash
yt-dlp --write-auto-sub --sub-lang pt,en --skip-download --write-info-json -o "PASTA_TEMPORARIA/sofia-%(id)s" "LINK"
```

- O `yt-dlp` aceita links do YouTube e do TikTok (`tiktok.com`, `vm.tiktok.com`, `vt.tiktok.com`). Perfil inteiro do TikTok e posts do Instagram costumam falhar.
- Se o site pedir login, pare. Nunca use cookies ou sessão do navegador, nunca contorne login nem captcha e nunca peça senha. Peça o arquivo à pessoa ou siga para outro caminho.
- Falhou por rede ou por bloqueio: troque de caminho e diga em uma linha o que mudou.

## Caminho B: receber arquivo

- **Vídeo enviado e ferramenta de rodar código:** siga o caminho A com o arquivo.
- **Só imagens:** peça prints do começo, do meio e do fim, com o segundo de cada um. Analise só o que os prints mostram.
- **YouTube:** a pessoa pode copiar a transcrição que aparece embaixo do vídeo.

## Caminho C: abrir páginas

Abra o link e leia o que é público: título, legenda, números e capa, se aparecerem. Separe o que você leu do que você supõe, diga a limitação e ofereça o upload. Título, capa e trecho de busca nunca viram análise do corpo do vídeo.

## Caminho D: só texto

Analise a fala pela legenda, pela transcrição ou pelo que a pessoa colou. Diga que a parte visual ficou de fora e como fechar (o arquivo ou prints).

## Comentários

Pegue os comentários pelo caminho que existir, nesta ordem:

1. A página aberta, quando os comentários aparecem sem login.
2. O navegador da pessoa (por exemplo, o Claude no Chrome), só com o OK dela e só para ler.
3. Uma ferramenta de métricas que a própria pessoa ligou ao Claude, para os perfis dela.
4. Um coletor pago de dados públicos, para qualquer perfil, se a pessoa já tiver um ligado. Diga qual coletor vai usar, quantos comentários vai buscar e quanto deve custar (confira o preço na página do coletor, porque ele muda), e espere o OK.
5. Os comentários que a pessoa colar.

Guarde até 20 entre os mais curtidos: ordene pelas curtidas, porque a ordem da lista que chega nem sempre segue a popularidade. Guarde só o texto, as curtidas e a data. Nunca guarde o nome, o @ ou o identificador de quem escreveu. Copie o texto como foi escrito, sem corrigir.

## Coletor pago, quando a pessoa deu o OK

Para o TikTok, prefira um coletor que traga vídeo, capa, números e transcrição na mesma chamada, e um de comentários. Para o Instagram, use o coletor de Instagram que a ferramenta dela já tenha.

- Chame uma vez por link, para cada resultado ficar ligado ao vídeo certo.
- Prefira a legenda que o vídeo já tem. Transcrição feita pelo coletor custa mais.
- Números úteis: views, curtidas, comentários, compartilhamentos e salvos.
- Capa e transcrição podem voltar como registro guardado no próprio coletor. Leia pelas ferramentas dele. Baixar esses links por fora costuma falhar.
- Sem o arquivo de vídeo, diga uma vez: "Consegui ver a capa e ler a transcrição, os números e os comentários. Os quadros do meio ficaram de fora. Para ver cortes, gestos e texto na tela, preciso do arquivo do vídeo." Não descreva edição nem gesto que você não viu.

## Antes de analisar, pergunte

- Se o vídeo é do nicho dela e qual é o público.
- Se ela quer entender alguma parte específica.

Se vieram dois ou mais vídeos, ou o contexto já responde, pule as perguntas e entregue.

## Quando são dois vídeos ou mais

Compare. É a análise mais útil.

Trate todos os links da mesma mensagem como um lote só. Prepare cada vídeo numa pasta temporária própria e gere o painel só quando todos estiverem prontos.

- Monte a tabela de números lado a lado.
- Calcule curtidas divididas por views em cada um. Se a proporção é parecida, o que foi mal perdeu no assunto ou na abertura. Se é diferente, o problema está dentro do vídeo.
- Compare as capas lado a lado.
- Aponte a principal coisa que mudou entre eles. Uma só.

## Frase a frase, em uma linha

Toda frase do roteiro ganha a sua análise, e cada análise é curta.

- Cada frase do roteiro vira um bloco separado.
- Uma frase de análise por frase do roteiro.
- Diga o que essa frase faz com quem assiste. O principal, uma coisa só.
- Nenhuma frase fica de fora.

Formato:

> "Trecho do roteiro"

O que faz: {uma frase curta}.

---

Exemplo inventado, só para mostrar a forma:

> "A padaria da esquina dobrou o preço do pão."

Joga um fato que vai contra o esperado. A pessoa quer saber o que aconteceu com a fila.

---

> "No dia seguinte, a fila dobrou junto."

O contraste vira a expectativa. Agora ela precisa do motivo.

---

> "Mas o dono não mexeu no pão. Mexeu na placa."

O "mas" puxa o tapete e abre a próxima dúvida.

---

Use `> "texto"` para o roteiro, texto normal para a análise e `---` entre os blocos.

## Como o vídeo foi feito

Antes do resumo, diga em 3 linhas curtas:
- **Jeito de gravar:** o formato, de `references/formatos/`. Se mistura dois, diga qual conduz.
- **Ordem da história:** a estrutura, de `references/estruturas.md`.
- **O que acertou ou errou nesse jeito de gravar:** uma frase, comparando com as regras de escrita do formato.

Com os quadros vistos (caminhos A e B com vídeo), acrescente:
- **Hook visual:** o que aparece nos primeiros segundos e por que segura.
- **Edição:** cortes, câmera, texto na tela, gestos e mudanças de ritmo, com o segundo de cada um.
- **Imagem e fala:** onde se reforçam e onde se contradizem.

Sem os quadros (caminhos C e D, ou só a capa), troque por:
- **A capa:** o que ela mostra e o que o texto dela promete.
- **Capa e primeira frase:** se prometem a mesma coisa.
- **Sinais indiretos:** o que os números e os comentários dizem sobre onde prendeu ou soltou.

Nunca invente um segundo que você não viu.

## Abertura

- O que faz parar: uma frase.
- Nota de 0 a 10.

## Resumo em 3 linhas

1. A ideia central em uma frase.
2. O que carrega o vídeo: o princípio que faz o trabalho pesado, em palavras simples.
3. O que daria para melhorar: uma sugestão prática ligada a um princípio.

## Painel da análise

- **Com o conector ligado:** salve a análise no conector (referência ou avaliação de perfil) e mande o link da página do site. Monte painel no chat só se a pessoa pedir.
- Sem o conector, numa superfície que mostra páginas (Artifacts, Canvas), crie a página da análise na conversa.
- No Claude Code ou em outra superfície sem isso, use `templates/dashboard.html` e salve em `Sofia/Analises/dashboard.html`, na pasta de trabalho. Se a pessoa pedir um arquivo separado, use `Sofia/Analises/{titulo-do-lote}/index.html`.
- Um pedido gera um painel. Com um vídeo, o painel tem um item. Com dois ou mais, tem todos.
- No lote, ponha no topo: visão geral, tabela de números lado a lado, ranking das aberturas, o padrão em comum e a principal coisa que mudou. Depois, uma seção completa para cada vídeo.
- Cada vídeo tem: título, link original, diagnóstico, nota e explicação da abertura, números, roteiro anotado, comentários (só o texto e as curtidas), aprendizados e limitações.
- Com os quadros vistos: quadros com o segundo, linha do tempo e a relação entre imagem e fala. Só quadros que você abriu. Amostra nunca vira o vídeo inteiro.
- Sem os quadros: ponha a capa, se você viu, e tire os blocos de quadro.
- O bloco de limitações é obrigatório: o que ficou de fora e como fechar.
- Ao atualizar `Sofia/Analises/dashboard.html`, mantenha as análises que já existem e acrescente ou atualize os vídeos pelo link. Não repita o mesmo vídeo.
- Entregue o painel e, na conversa, mostre só um resumo curto com os três achados principais.

## Depois, pergunte

> "Quer escrever um roteiro com base nisso, melhorar um que você já tem, ou entender alguma parte melhor?"
