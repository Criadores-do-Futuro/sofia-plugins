# Receitas — o que fazer quando o gatilho dispara

`catalogo-visual.md` responde "a frase diz X, qual é a classe?". Este arquivo responde a
pergunta seguinte, que é a difícil: **escolhida a classe, o que exatamente se vê?**

Cada receita traz o gatilho, o movimento em três tempos (o que entra, o que acontece, o
que sai), a duração mínima e a rota do asset. O diretor pode usar uma receita como está,
combinar duas, ou escrever a sua — mas escrever a sua exige dizer por que nenhuma serve.

**Regra que não muda:** texto, número e interface são desenhados em código. Nenhuma
receita manda um número ou uma palavra legível para o gerador de imagem.

---

## `paper` — o estudo existe

**Gatilhos:** "um estudo de", "o pesquisador", "em 1962", "o paper mostrou", qualquer
frase que empresta autoridade de uma publicação.

O `paper` é uma ficha tipográfica desenhada em código: título real, autores, veículo,
ano, DOI em corpo pequeno. Nunca é uma foto do PDF, e nunca inventa o título — o campo
vem do `enriquecedor`, com fonte verificada, ou o plano volta a ser `fala`.

| Receita | Movimento | Duração |
| --- | --- | --- |
| **ficha que entra** | a ficha sobe do rodapé e assenta; o DOI acende meio segundo depois do título | ≥ 2,5 s |
| **ficha que se corrige** | a ficha entra com o dado que a fala errou já certo; nada pisca, a correção é silenciosa | ≥ 3 s |
| **três fichas que se ligam** | uma ficha por vez, nas três aparições; na última, uma linha fina liga as três | ≥ 2,5 s cada |

**Combinação forte:** `paper` + `retrato` do pesquisador em sequência, nunca no mesmo
quadro. Primeiro quem descobriu, depois o que ele publicou — ou o contrário, se a fala
nomeia a pessoa antes do estudo.

**Imagem do estudo:** figura de paper com licença aberta (arXiv, PLOS, PubMed Central)
pode entrar como `arquivo`, recortada e rebaixada, com a fonte no canto. Sem licença
verificada, não entra: a ficha tipográfica já faz o trabalho.

---

## `retrato` — a pessoa por trás do estudo

**Gatilhos:** o nome próprio de um pesquisador, autor ou personagem histórico.

Rosto de pessoa real **nunca é gerado**. São duas rotas, nesta ordem:

| Receita | Movimento | Rota |
| --- | --- | --- |
| **ficha tipográfica** | nome em serifa, anos de vida e instituição em corpo pequeno; entra por corte, respira, sai por varredura | código, custo zero |
| **retrato licenciado** | foto em preto e branco com Ken Burns lento (push-in 4%), moldura de contato dupla | acervo com licença registrada |
| **colagem de jornal** | o recorte licenciado sobre papel envelhecido, rasgo de borda, meio-tom impresso visível, leve rotação | acervo + tratamento em código |

A colagem de jornal é o caminho quando a pessoa é **famosa e o tom é irônico ou
histórico**. Para um pesquisador citado com respeito, a ficha tipográfica é mais digna e
mais barata.

---

## `personagem` — alguém sente

**Gatilhos:** dor, hesitação, esquecimento, medo, decisão, multidão, "a gente faz isso",
"todo mundo já passou por".

A figura branca sem rosto é a imagem-assinatura do treino: 697 dos 2.623 frames. Não é um
personagem com personalidade, é um corpo vazio que o espectador ocupa. Sem rosto, sem
olhos, sem boca, sem textura de pele.

| Receita | Movimento | Quando |
| --- | --- | --- |
| **a figura que trava** | de costas num corredor, dá um passo e para; a luz continua andando sem ela | hesitação, bloqueio |
| **a multidão idêntica** | fileiras da mesma figura até o fundo escuro; uma só levanta a cabeça | "todo mundo", conformidade |
| **a que esquece** | a figura sentada, e atrás dela as próprias silhuetas se apagando uma a uma | memória, perda |
| **silhueta recortada** | contorno preto chapado sobre luz âmbar, sem volume — mais duro, mais barato | tom acusatório, sem empatia |

**Limite:** dois planos de `personagem` seguidos, no máximo. É a classe mais bonita e a
que mais satura. Alternar com `objeto` é o que mantém o ritmo.

---

## `objeto` — o conceito vira coisa

**Gatilhos:** a frase tem uma metáfora concreta — a chave, o muro, o nó, a porta, a peça
que falta.

A cena é fotográfica e sangra o quadro: mesa, sala, luz caindo, profundidade. O preto vem
da sombra, não de recorte. Objeto flutuando no vazio é a versão pobre da classe.

| Receita | Movimento | Duração |
| --- | --- | --- |
| **família de três estados** | o mesmo objeto em três momentos do vídeo, mudando de estado (fechado → entreaberto → aberto) | ≥ 2,5 s cada |
| **o que se costura** | peças soltas que se juntam sozinhas num bloco que não estava entre elas | ≥ 3 s |
| **o que evapora** | a pilha que some pela metade, sem ninguém tocar | ≥ 2,5 s |
| **o espelho de duas faces** | um lado revelado, o outro coberto; o pano sai quando a fala chega lá | ≥ 3 s |

**Família é o que faz o vídeo parecer dirigido.** Um objeto que volta três vezes mudando
de estado vale mais que três objetos diferentes bem feitos.

---

## `dado` — o número tem fonte

**Gatilhos:** uma comparação, uma proporção, uma curva. **Só entra com fonte real.**
Número sem fonte vira `objeto` ou volta para `fala`.

| Receita | Movimento | Estilo |
| --- | --- | --- |
| **a curva que se desenha** | a linha risca da esquerda para a direita no tempo da frase; o ponto final acende e fica | traço de caneta, corpo preenchido embaixo |
| **giz no quadro** | mesma curva, mas com textura de giz e poeira, sobre ardósia escura | quando o tom é de aula, não de laboratório |
| **a mesma curva, três estados** | a curva volta idêntica com outro rótulo: sua → de todo mundo → da máquina | prova visual sem a fala precisar dizer |
| **duas barras que se comparam** | as duas crescem juntas e uma para antes; a diferença fica marcada | contraste, "você vs." |

O desenho à mão (caneta ou giz) é o padrão do canal para gráfico: ele diz "isto é um
raciocínio", não "isto é um relatório". A escolha entre caneta e giz segue o branding do
momento — caneta para argumento pessoal, giz para explicação didática.

---

## `palavras` — a fala vira tipografia

**Gatilhos:** uma lista dita em voz alta, uma palavra que precisa ser lembrada depois,
uma negação ("eu não falei essa").

**Antes de escolher `palavras`, pergunte se a coisa dita pode ser DESENHADA.** Escrever
na tela a palavra que o espectador acabou de ouvir não ilustra: ele já ouviu. Se a fala
diz "galáxia", "camadas", "as três partes", existe um tipo que desenha aquilo — veja
`galaxia`, `camadas` e `indice` abaixo. `palavras` é para quando a palavra é mesmo o
objeto do plano: uma lista que acumula, um termo que precisa ficar de pé sozinho.

O validador recusa um guia em que mais de 35% dos planos de motion sejam `palavras` ou
`cartela`. Não é gosto: é a diferença entre ilustrar e narrar por escrito.

| Receita | Movimento | Duração |
| --- | --- | --- |
| **acúmulo** | cada palavra entra e as anteriores ficam, encolhendo e esmaecendo | ≥ 2,5 s |
| **varredura** | as do meio são comidas por uma faixa de luz; sobra o começo e o fim | ≥ 2,5 s |
| **a que acende** | uma palavra que nunca esteve na lista aparece em âmbar sobre as fantasmas | ≥ 3 s |
| **fantasmas** | a lista inteira volta a 15% de opacidade como fundo de outro plano | qualquer |
| **o risco** | `dados.riscar` desenha a linha por cima no tempo da negação | ≥ 2,5 s |

Uma palavra sozinha na tela preta não é `palavras`, é `cartela`.

### A regra da negação

Quando a fala nega — "elas **não** são inteligentes" — escrever INTELIGENTES limpo faz o
vídeo afirmar o que a voz nega. Quem assiste sem som lê a promessa, não a acusação. Duas
saídas, nesta ordem de preferência:

1. **Ilustrar o erro.** Uma falha concreta e conhecida prova a frase sem escrevê-la —
   a máquina que não conta os R de "strawberry", ou a que apaga o disco inteiro porque
   pediram espaço livre. Isso é `tela`, e é sempre melhor.
2. **Riscar.** `dados.riscar: true` (ou a lista de palavras negadas) desenha o risco
   vermelho por cima, no tempo da negação.

O validador acusa quando a fala nega uma palavra que o plano escreve sem riscar.

---

## `galaxia` — o céu, não a palavra CÉU

**Gatilhos:** a fala fala de espaço, distância, vizinhança, rota, caminho, constelação,
vértice — qualquer coisa em que a relação entre pontos seja o argumento.

Três cascas de estrelas em profundidade diferente com nebulosa ao fundo. As palavras do
plano viram vértices acesos, sempre no mesmo lugar do céu (a posição sai do nome, não da
ordem), ligadas pela constelação. `dados.galaxia.modo` escolhe o que acontece:

| Modo | O que acontece | Quando |
| --- | --- | --- |
| **campo** | o céu deriva, os vértices acendem um a um | apresentar o lugar, povoar |
| **rota** | a linha é traçada de vértice em vértice com um ponto de luz na ponta | calcular, escolher, ligar |
| **voo** | raias de velocidade abrem do centro e o céu atravessa a câmera | atravessar, mudar de região |

Sem `palavras` o plano é só o céu — legítimo para "imagina uma galáxia".

---

## `camadas` — a pilha, não a palavra CAMADA

**Gatilhos:** a fala enumera partes de uma coisa só, empilhadas ou em ordem —
"são quatro camadas", "a segunda etapa", "por baixo disso tem".

Lajes em perspectiva, uma por item. `dados.palavras` traz a pilha inteira em toda
aparição (use `— — —` para o que ainda não foi revelado) e `dados.acender` diz qual sobe
e acende nesta. `acender: "todas"` acende a pilha inteira — é o plano de fechamento,
quando o espectador vê pela primeira vez o conjunto que montou.

---

## `indice` — as partes do vídeo

**Gatilhos:** "vou te mostrar três coisas", "essa foi a parte 1", "falta a parte 3".

Lista numerada com o numeral grande em contorno; o item da vez fica cheio. Como no
`camadas`, a lista é sempre inteira, com `▨▨▨▨▨▨▨▨` no que ainda não foi revelado — é
isso que faz o espectador sentir o que falta.

---

## `cartela` — a frase É a informação

**Gatilhos:** a regra do experimento, a definição de um termo, a virada em uma linha.

Cartela não é fundo chapado. O padrão medido tem luminância mediana 35/255: é texto
grande sobre b-roll rebaixado ou sobre a cena anterior desfocada.

| Receita | Movimento |
| --- | --- |
| **regra dura** | duas linhas em caixa alta, entram por corte seco, saem por corte seco |
| **termo que nasce** | a palavra entra pequena e cresce até assentar; o resto do quadro escurece |
| **provocação final** | uma linha só, âmbar, sobre o último quadro do vídeo já parado |

---

## `tela` — o software na mão

**Gatilhos:** app, conversa, terminal, "digita", "a IA respondeu".

Interface é **sempre** desenhada em código: o gerador de imagem erra glifo e inventa
rótulo. Uma janela vazia é tela preta — se não há conteúdo escrito, o plano não é `tela`.

| Receita | Movimento |
| --- | --- |
| **conversa que responde** | as mensagens entram no ritmo da fala; a resposta da máquina chega com meio segundo de atraso |
| **terminal que digita** | o prefixo já está lá, o comando é digitado letra a letra, o cursor pisca |
| **a barra que encolhe** | a barra de contexto cai de cheia para quase vazia enquanto a fala explica por quê |
| **a resposta inventada** | o texto entra confiante e, dois segundos depois, uma linha fina o risca |

| **a página que se monta** | o esqueleto da página cai bloco a bloco na ordem em que a fala nomeia; o botão assenta por último, em âmbar |

**`dados.tela.modo` só tem três valores que o `compor.py` sabe desenhar: `chat`,
`terminal` e `pagina`.** Qualquer outro valor passa no validador e sai como terminal na
tela — o plano vira uma mentira silenciosa, que só aparece no render. Se a frase pede
uma interface que não é nenhuma das três (um painel, um carrinho, um feed), escreva
assim mesmo e **avise que o modo não existe ainda**: ou alguém escreve o modo novo
antes de gerar, ou o momento volta a ser `fala`. Nunca troque o plano certo por um modo
errado só para o validador ficar quieto.

O `pagina` recebe `dados.tela.paginas`: uma lista de `{nome, blocos}`, cada bloco um
rótulo curto (`promessa`, `campo de e-mail`, `botao`). O **último bloco de cada página
vira o botão** — em âmbar, mais estreito, assentando por último. É esqueleto, não
maquete: quem assiste tem de ver a estrutura nascer, não ler uma página inteira em
quatro segundos.

---

## `arquivo` — isto já aconteceu

**Gatilhos:** "em 1962", "na época", um fato conhecido, um momento histórico, um nome que
o espectador reconhece.

Material de terceiros: filmagem antiga, gravura, recorte de jornal, registro documental.
Preto e branco sujo, grão pesado, contraste estourado.

| Receita | Movimento | Cuidado |
| --- | --- | --- |
| **o recorte** | jornal de época com push-in lento; a manchete fica ilegível de propósito | licença registrada |
| **trecho baixado** | 1,5 a 3 s de um vídeo conhecido, **sempre mudo**, rebaixado e granulado | áudio nunca entra; direitos verificados |
| **colagem** | dois ou três recortes sobrepostos com rasgo de borda e meio-tom | funciona bem com `retrato` |

**Áudio de material de terceiros nunca entra no vídeo.** Nem baixo, nem de fundo. A cama
musical do projeto cobre o trecho inteiro.

`arquivo` sintético — b-roll novo com textura de época — é bonito e legítimo como
atmosfera, mas **não pode ser apresentado como documento real**.

---

## `obra` — o peso cultural

**Gatilhos:** filosofia, moral, culpa, perdão, beleza, o clássico.

Escultura ou pintura com chiaroscuro, Ken Burns lento (push-in 4% e rotação de 1,5°),
dupla sombra de contato. A obra carrega séculos de significado que a fala não precisa
explicar.

Dois direitos: o da obra e o da fotografia dela. Domínio público da pintura não torna a
foto dela livre.

---

## `cotidiano` — o choque de realidade

**Gatilhos:** a metáfora doméstica — a pia entope, a gaveta trava, o cabo embola.

Filmado com celular e luz de janela, cru, sem correção. É o contraste que faz funcionar:
depois de dois planos 3D limpos, a pia real acorda o espectador.

`cotidiano` é **uma cena inteira**, do começo ao fim. Uma pia entupindo vale mais que dez
planos soltos de cozinha.

---

## `hibrido` — o clímax

**Gatilhos:** o abstrato invade o real; a frase junta os dois lados do vídeo.

A figura branca dentro da cena filmada, com sombra de contato no chão real. É o plano mais
caro do vídeo e por isso é **um só, no ponto de virada**. Dois híbridos num vídeo de cinco
minutos significa que nenhum é o clímax.

---

## `tvcrt` — memória e ironia

**Gatilhos:** infância, o que passava na TV, nostalgia usada contra o tema adulto.

Tubo curvado, scanlines, aberração da lente, cantos pretos. Serve quase sempre no gancho,
raramente no meio.

---

## `pessoa` e `fala` — você

`fala` é o padrão: você na câmera. Todo plano é `fala` até que alguém escreva o que a
ilustração mostra e o que muda nela.

`pessoa` é o oposto do talking head: você visto de longe, 8 a 15 metros, por uma janela
iluminada no escuro. A fala vira segredo observado. Um por vídeo, no máximo — e quase
sempre na abertura ou no fecho.

---

## Como o vídeo se monta com isto

A fórmula de retenção medida nos 17 vídeos do treino, adaptada para peça longa:

| Momento | Função | Classes que servem |
| --- | --- | --- |
| abertura | o gancho | `personagem`, `tvcrt`, `pessoa` |
| primeiro terço | a metáfora | `objeto`, `dado` |
| meio | a âncora — isto é real | `paper`, `retrato`, `arquivo`, `obra` |
| virada | o clímax | `hibrido`, `objeto` da família fechando |
| fecho | a provocação | `cartela`, `fala` |

Duas travas que valem mais que a fórmula: **nunca a mesma classe três vezes seguidas**, e
**toda peça que aparece três vezes tem de mudar de estado** — senão é repetição, não
família.
