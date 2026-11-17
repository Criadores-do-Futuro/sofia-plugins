# Como se pensa a sugestão de motion

`catalogo-visual.md` diz **qual classe**. `receitas.md` diz **o que exatamente se
vê** dentro da classe. Este arquivo é o passo antes dos dois: **como se chega à
ideia**, e por que a primeira que vem à cabeça quase sempre é a errada.

Ele nasceu de uma reprovação inteira, registrada em 2026-09-11. O dono do canal
leu oito sugestões de motion para um pitch de 77 s e disse: *"quem sugere os
motion graphics, eu estou detestando as sugestões, precisa melhorar a forma como
ele pensa."* As ideias passavam em coerência, em movimento, no validador — e
eram todas símbolo de papel onde a fala pedia a coisa. O que segue é a diferença
entre as duas colunas, virada em procedimento.

---

## O erro tem um nome: traduzir para símbolo

Diante de "testei todos esses vídeos que ensinam a editar com IA", a cabeça
propõe **um terminal**, porque terminal é o símbolo de "editar com IA". Mas a
fala não disse terminal. Disse **vídeos**, e disse **todos**. A imagem que a
frase pede é uma parede de vídeos de tutorial, muitos, reais, empilhados.

O símbolo é sempre mais fácil de desenhar e sempre mais pobre de ver. Ele
transforma uma frase específica, deste vídeo, numa ilustração que serviria para
qualquer vídeo do mesmo assunto. É a mesma falha que o `catalogo-visual.md` já
registra na tabela "Como escolher errado" — ali em forma de exemplos, aqui em
forma de método.

## As quatro perguntas, nesta ordem

Antes de escrever `ideia`, responda as quatro. Nenhuma é opcional, e a ordem
importa: a primeira sozinha já derruba metade das ideias ruins.

### 1. Quantos? A fala diz um, ou diz muitos?

**"Todos", "vários", "cada", "uma série de", o plural simples — são instrução de
composição.** Uma coisa na tela quando a fala diz "todos esses" é contradizer o
que se ouve, e o espectador sente sem saber nomear.

| A fala diz | Errado | Certo |
| --- | --- | --- |
| "todos esses vídeos que ensinam" | um terminal | uma parede de miniaturas de tutorial, muitas, cobrindo o quadro |
| "todos eles eram genéricos" | a palavra "genérico" escrita uma vez | um carrossel de vídeos passando, cada um com "GENÉRICO" numa fonte diferente |
| "cada formato tem suas regras" | uma pilha de três rótulos | o formato abrindo e mostrando **uma** regra acontecendo |

Quantidade também é ritmo: muitos elementos entrando no tempo da fala dão a
sensação de acúmulo que a palavra "todos" promete.

### 2. Que coisa é essa **no mundo**?

Nomeie o objeto que existe fora da metáfora. Se o vídeo fala de edição de vídeo,
as coisas do mundo são **vídeos, arquivos, timelines, programas, posts, redes**
— não papel, não carimbo, não fichário, a menos que a fala fale de papel.

O estilo (`vox`, `noturno`) decide **a matéria** com que a coisa é desenhada:
recorte de jornal, 3D luminoso, colagem. Ele **não** decide que coisa é. Um
carrossel de vídeos no `vox` é um carrossel de vídeos recortados com borda de
tesoura sobre papel — continua sendo vídeo. Trocar a coisa pelo material do
estilo é como confundir o assunto com a tinta.

### 3. Dá para **mostrar acontecendo** em vez de rotular?

Rótulo é a saída preguiçosa: escrever o nome da coisa e chamar de motion. A
demonstração vale mais, e quase sempre cabe no mesmo tempo.

> "cada formato tem uma série de regras de edição própria"
> — **rótulo:** três folhas escritas "corte", "motion", "legenda".
> — **demonstração:** o formato *tela dividida* abre na tela e as regras dele
> acontecem: o rosto se encaixa e fica preso na metade de baixo, um vídeo de
> apoio entra na metade de cima ilustrando o que a voz diz, a legenda se acomoda
> na junção. Em quatro segundos o espectador **entendeu o que é um formato** —
> coisa que nenhum rótulo ensina.

Quando o assunto é um produto ou um método do autor, a demonstração é sempre
possível: o produto tem tela, tem entrada e tem saída.

### 4. O que entra e o que sai?

Frase que descreve processo pede a cadeia inteira na tela, não o meio dela.

> "eu coloco o vídeo, escolho o formato e ele já edita para mim"
> — vários arquivos de vídeo **entrando** num programa que tem nome na janela, e
> saindo do outro lado **um post publicado**, com a cara das redes onde ele vai
> parar. Entrada → máquina → saída, na ordem em que a fala diz.

A saída é o que prova. Parar na máquina deixa a promessa sem consequência.

---

## As duas provas, antes de escrever

**Prova do genérico.** Troque o assunto do vídeo por outro e veja se a imagem
continua servindo. "Um fichário com abas" serve para qualquer vídeo sobre
organizar qualquer coisa — logo não é deste vídeo. "Envelopes confidenciais, um
por formato criativo, e o de tela dividida na frente" não serve para mais nada.

**Prova da fala plural.** Leia a frase em voz alta e conte os substantivos no
plural. Se há plural na fala e singular na tela, volte à pergunta 1.

---

## O som faz parte da sugestão

O campo `cena.som` não é enfeite escrito depois. Um veredito que bate sem baque
não bate; um carrossel que passa sem passar de página é um slideshow mudo. Ao
escrever a `ideia`, escreva **o efeito que a acompanha** — e se o momento é um
acento (carimbo, virada, revelação), diga isso no `som` com a palavra exata do
gesto, não "som de transição".

`motion-editorial.md` continua valendo: efeito sonoro na palavra-chave, na ação
ou na troca de classe — nunca em toda entrada. Um acento por cena.

> **Estado da execução:** a cama de música é sintetizada (`trilha.py`); os SFX
> ainda **não têm etapa que os produza** — a biblioteca de efeitos não está na
> máquina, e o painel marca essa falta. Escrever o `som` hoje registra a
> intenção para o dia em que a etapa existir, e serve ao editor que vai montar.
> Não prometa SFX no preview como se ele fosse sair no master.

---

## A tabela que gerou este arquivo

As oito sugestões reprovadas e o que o dono queria ver. Vale como calibragem:
a coluna do meio passou em todos os testes automáticos da skill.

| A fala | O que foi sugerido | O que ele queria ver |
| --- | --- | --- |
| "experimentei todos esses vídeos que falam sobre editar vídeo com o Claude Code" | um terminal de papel digitando `editar --automatico` | **recortes de vários vídeos** que ensinam isso, muitos, enchendo o quadro |
| "achei o resultado de todos esses editores uma porcaria" | carimbo de reprovado sobre tira de filme | *aprovada* — e com **SFX** no baque |
| "só que todos eles eram genéricos" | as palavras "genérico" e "ridículo" grifadas | **vários vídeos em carrossel**, cada um com "genérico" numa fonte diferente |
| "decidi treinar um editor por formato criativo" | um fichário com abas em leque | **envelopes confidenciais**, um por formato, o de **tela dividida** na frente |
| "coloco o vídeo, escolho o formato e ele já edita" | uma janela de conversa com duas linhas | **arquivos de vídeo entrando** num programa chamado bEditor e **saindo um post** no Instagram, TikTok e YouTube |
| "cada formato tem uma série de regras de edição própria" | três folhas empilhadas com rótulos | o **tela dividida abrindo** e as regras dele acontecendo na tela |

O padrão da coluna errada é único e fácil de reconhecer depois que se vê: **toda
sugestão virou um objeto de papelaria**. Fichário, folha, carimbo, bilhete,
janela. O estilo era colagem de jornal, e a colagem comeu o assunto. É por isso
que a pergunta 2 existe: o estilo dá a matéria, nunca a coisa.

---

## A segunda rodada de reprovações — 2026-09-12

O mesmo vídeo voltou, agora em estilo de gravação de tela, e foi reprovado de
novo. As quatro perguntas acima tinham sido respondidas; faltava o que segue.

### 5. Quando não souber como a coisa é, PESQUISE

> *"quando vai ilustrar vídeos genéricos, pesquise por motion graphics slop, e
> mostre eles ao invés de simplesmente um texto escrito «genérico»."*

Adjetivo não tem forma, e a saída preguiçosa é escrever o adjetivo em corpo
grande. Mas quase todo adjetivo de crítica nomeia um **gênero que existe e tem
forma documentada**. `motion graphics slop`, por exemplo, é descrito assim:
tudo centralizado no nível do olho, gradiente de fundo, mesma composição
independente do assunto, câmera parada, "tecnicamente correto e emocionalmente
vazio".

Com isso na mão, o plano se escreve sozinho: **o mesmo molde, cinco vezes, com
a cor trocando.** A repetição é o argumento — e prova "genérico" sem escrever a
palavra. Antes de desenhar um adjetivo, procure o nome do gênero.

### 6. Cada palavra no seu instante — parta o momento

Frase com quatro substantivos pede **quatro gestos**, cada um no segundo em que
a palavra é dita. Um cartão com os quatro escritos é a versão preguiçosa da
mesma ideia.

> *"em «coloca os inserts que eu preciso» coloca uma imagem de timeline de
> programa de edição com vídeos entrando na timeline."*

Isso decide onde o momento é **partido**: se a coisa só é nomeada no fim da
frase, parta o momento numa pausa entre palavras e ponha a cena em cima da
palavra. Partir custa duas linhas no guia. Ilustrar a frase inteira põe busca na
tela enquanto a voz ainda fala de arquivos — e aí o espectador não liga uma
coisa à outra.

### 7. Contexto do vídeo inteiro, não do plano

> *"entender como encontrar ideias boas para fazer ilustrar o que está sendo
> dito no vídeo, com contexto total do vídeo em mente."*

Antes de escrever a primeira `ideia`, responda por escrito:

1. **Qual é a tese do vídeo**, em uma frase. Todo plano ou constrói a tese ou sai.
2. **O que já foi mostrado.** Plano que repete o registro do vizinho lê como o
   mesmo plano, por mais que o conteúdo mude.
3. **O que a fala promete e nunca mostra.** É aí que mora o plano que falta — e
   foi o buraco desta rodada: um pitch de ferramenta de edição sem um único
   quadro da própria saída. Afirmação sem prova, e nenhum acabamento conserta.

### 8. A escada do que usar quando a coisa não pode ser desenhada

Da mais forte para a mais fraca:

1. **Captura real** do que está sendo falado. Se o vídeo vende um produto, a
   tela do produto rodando é a única prova que existe.
2. **Quadro do próprio take**, reenquadrado ou anotado. Material real, já no
   disco. Foi assim que "cada formato tem regras próprias" virou demonstração:
   o rosto travado na metade de baixo, sobre um quadro do próprio vídeo.
3. **Trecho de vídeo de terceiro como insert** (`tela.modo: "acervo"`). Quando
   a fala cita o trabalho alheio — "os vídeos ficavam genéricos" —, o material
   real é mais forte que qualquer desenho dele. Ver a seção abaixo: tem regra.
4. **Desenho em código**, na gramática do estilo. Serve para o que é estrutura:
   timeline, lista, busca, fluxo de publicação.
5. **Imagem gerada.** Último recurso, e só para objeto físico. Gerador não
   desenha interface sem inventar botão que não existe.

### 9. Trecho de terceiro: insert, nunca repost

Decisão do dono em 2026-09-12, depois de a questão de direito ser levantada:

> "quero usar clipes da internet, do reels ou do tiktok pode usar, não fere
> direitos porque eu estou criando meu próprio conteúdo em volta, e o trecho do
> vídeo da internet é apenas um insert, não um repost"

Quem publica é ele, e a decisão é dele. **Não reabra a discussão a cada vídeo.**
O que o plugin faz é garantir que o argumento se sustente na prática:

- **Teto de 3 s por fonte** (`acervo.DUR_MAX`). Insert é citação; clipe inteiro
  é repost, e a diferença se mede em segundos.
- **Procedência registrada.** URL, autor e data ficam no `plano.json`
  (`acervoCreditos`) e o crédito aparece na própria cena, embaixo da janela.
  É isso que separa citação de repost aos olhos de quem assiste.
- **Download com cache**, em `public/acervo/`. Baixa uma vez por URL; o bruto
  não entra no repositório.
- **Quem escolhe os clipes é o editor, nunca o script.** `acervo.py` não
  procura vídeo sozinho, e isso é deliberado: buscar "slop" e apontar o
  resultado dentro de um vídeo que chama aquilo de porcaria seria escolher, por
  conta própria, de quem falar mal. O guia traz `tela.fontes` com as URLs.

Como escrever no guia:

```json
"dados": { "tela": { "modo": "acervo", "titulo": "o mesmo molde",
  "creditos": ["@canal1", "@canal2"],
  "fontes": [
    {"url": "https://…", "de": 12.5, "dur": 1.4, "credito": "@canal1"},
    {"arquivo": "acervo/meu-teste.mp4", "de": 0, "dur": 1.2}
  ] } }
```

`arquivo` serve para material que já está no disco — inclusive a captura da
saída dos editores que o próprio dono testou, que é a opção mais forte de todas
e não depende de terceiro nenhum.

**Detalhe de execução que não é opcional:** o HTML não toca o vídeo. Navegador
reproduzindo `<video>` dentro de uma captura quadro a quadro dessincroniza — o
tempo do elemento não é o tempo da linha. O `hf.py` desenha a página com a
**janela vazia** em `hf_ilustrativo.MOLDURA_ACERVO`, e o `acervo.py` encaixa o
trecho no mesmo retângulo com ffmpeg. As duas pontas leem a constante do mesmo
lugar; se divergirem, o vídeo aparece torto e ninguém descobre por quê.

**Nunca: mock de uma interface que a fala não descreve.** O balão de iMessage
inventou um produto que não é um bot de mensagem — e ainda queimou, 21 s antes
da hora, o momento em que a publicação seria dita.

### A régua final, antes de mandar renderizar

- [ ] **Que coisa** está no quadro? Se a resposta for um conceito, refaça.
- [ ] O que ela **acrescenta** ao que a voz já diz?
- [ ] O gesto cai **no segundo da palavra** que ele ilustra?
- [ ] É **diferente do plano anterior em registro**, não só em conteúdo?
- [ ] Se o plano sumisse, o espectador **perderia** informação?

O último é o mais barato e o que mais corta plano ruim: **motion que pode sumir
sem perda deve sumir.** Medido neste vídeo — o trecho mais dinâmico era ele
falando, e os três motions eram os três trechos mais parados do corte.
