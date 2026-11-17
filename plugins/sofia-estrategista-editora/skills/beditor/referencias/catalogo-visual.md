# As classes — e o gatilho de cada uma

> **`fala` vem primeiro.** Havendo vídeo original (`plano.py --video`), todo plano é
> `fala` até que alguém escreva o que a ilustração mostra e o que muda nela. Motion
> graphics interrompe o contato com quem fala; a interrupção só se paga quando mostra
> algo que a fala não mostra. Uma figura genérica parada é sempre pior que o rosto.

Saíram de 2.623 frames agrupados por embedding e depois lidos um a um. A pergunta que
esta tabela responde é: **a frase diz X, o que se vê?**

| `tipo` | Gatilho na fala | O que aparece |
| --- | --- | --- |
| `fala` | **o padrão**: nada aqui pede ilustração | o vídeo original, você falando na câmera |
| `personagem` | alguém sente, decide, trava, evita | figura branca sem rosto num vazio preto |
| `objeto` | um conceito vira coisa: a chave, o muro, o nó | um objeto isolado, luz de estúdio, fundo preto |
| `cartela` | a frase É a informação | legenda queimada grande sobre b-roll rebaixado |
| `dado` | número com fonte | gráfico desenhado em código, rótulo verdadeiro |
| `arquivo` | "em 1962", "na época", origem histórica | material de acervo, grão e instabilidade de época |
| `obra` | referência a arte, ao clássico, ao belo | pintura/gravura licenciada, Ken Burns lento |
| `broll` | atmosfera, lugar, tempo passando | plano cinematográfico, DOF raso, sem gente falando |
| `cotidiano` | metáfora doméstica: a pia entope, a gaveta trava | você mesmo filmando com celular e luz de janela |
| `tela` | app, mensagem, interface, "digita /compact" | UI desenhada em HTML, corner pin numa tela filmada |
| `tvcrt` | memória, infância, o que passava na TV | animação livre com simulação de CRT por cima |
| `hibrido` | o abstrato invade o real | render 3D com shadow catcher sobre placa filmada |
| `pessoa` | o assunto é uma pessoa concreta, distante | filmagem real noturna, 8–15 m, 50–85 mm |

## Como escolher errado

O erro clássico é ilustrar a **palavra** em vez do **argumento**. A fala diz "memória"
e você põe um cérebro. Ninguém para por um cérebro. A fala diz "memória" no contexto de
"o meio da conversa some" — o plano é uma fita cortada no meio, ou uma figura de costas
num corredor cujo centro está escuro. Ilustre a consequência, não o substantivo.

O segundo erro é escolher `personagem` para tudo. É a classe mais bonita e a mais cara,
e quatro planos dela seguidos matam o ritmo (ver `ritmo.md`).

O terceiro é o mais difícil de enxergar de dentro, porque parece caprichado: **inventar
um sistema abstrato e depois narrar o sistema em vez da fala.** Lajes que ganham nome,
uma pilha que cresce laje a laje, um muro que se ergue tijolo a tijolo — o guia fica
coerente consigo mesmo e some do que a voz está dizendo. Registrado em campo, num guia
inteiro recusado pelo editor:

| A fala diz | O sistema desenhou | O que o editor queria ver |
| --- | --- | --- |
| "aprendi sobre técnica de venda, sobre produto" | duas lajes ganhando nome | alguém vendendo, alguém fazendo produto, o dinheiro trocando de mão |
| "aprendi tudo sobre IA, treinar modelos, modelos locais" | duas lajes de máquina na pilha | uma pessoa cercada de livros, virando página |
| "vou fazer a página de venda, a de captura" | duas peças assentando no muro | as próprias páginas se montando |
| "conteúdo no TikTok, no Instagram, no Facebook" | quatro nomes empilhando no muro | uma manchete de jornal por rede, caindo conforme ele fala |

A regra que sai daí: **quando a fala nomeia uma ação humana, o plano mostra a ação
acontecendo.** Vender é alguém vendendo. Estudar é alguém estudando. Construir uma
página é a página se construindo. O abstrato serve quando a fala é abstrata — "o meio
da conversa some", "o token acaba" — não quando ela já é concreta e o guia a traduz
para geometria.

Repare no que as quatro recusas têm em comum: em todas, o plano escrito era **a lista
dita, arrumada em desenho**. Enumeração na voz vira enumeração na tela, e a tela não
acrescenta nada — o espectador já ouviu os quatro nomes. Uma lista falada é o convite
mais forte que existe para ilustrar em vez de transcrever.

Três aparições de uma mesma peça é `familia`, e `familia` é legítima. O que não é
legítimo é **fabricar** a peça só para ter o que repetir: se a progressão (vazia →
montando → acesa → encadernada) não estava na fala, ela é enfeite do guia, e o editor
corta. Antes de escrever a terceira aparição de uma peça inventada, pergunte se cada
uma delas sobreviveria sozinha, sem as outras duas. Se a resposta for não, o que você
tem é um sistema, não três planos — e derrubar uma laje derruba o vídeo inteiro, porque
os planos vizinhos passam a citar uma coisa que não existe mais.

## O que cada classe custa

```
cartela, dado, tela        código puro          minutos, custo zero, reproduzível
objeto, personagem         IA + upscale         segundos por imagem, custo por chamada
broll, hibrido             IA de vídeo          caro, lento, enquadramento incerto
arquivo, obra              acervo + licença     tempo de curadoria, risco jurídico
cotidiano, pessoa          filmar               tempo seu, resultado insuperável
```

Quando duas classes servem à mesma frase, **escolha a mais barata**. Um `objeto` bem
iluminado resolve 80% do que um `personagem` resolveria, por uma fração do trabalho.

## Armadilhas registradas

- `cartela` **não** é fundo chapado. O padrão real tem luminância mediana 35/255: é
  legenda sobre b-roll rebaixado, não texto no vazio.
- `dado` é raro de verdade. Se você tem mais de 2 gráficos num vídeo de 60 s, provavelmente
  dois deles são `objeto` com legenda.
- `cotidiano` é **uma cena inteira**, não um banco de planos. Uma pia entupindo, do
  começo ao fim, vale mais que dez planos soltos de cozinha.
- `arquivo` sintético (b-roll moderno com textura de época) funciona visualmente mas
  **não pode ser apresentado como documento real**.
- `obra` carrega dois direitos: o da obra e o da fotografia dela.

## Como cada classe falha, e o número que a constrói

Veio da linha do Codex (`category-grammar.md`). As receitas dizem o que se vê;
esta tabela diz como cada classe dá errado, para o diretor reconhecer a falha
antes do editor.

| `tipo` | Construção medida | Falha típica |
| --- | --- | --- |
| `personagem` | humanoide marfim fosco, fundo preto frio, recorte de luz quente de um lado e fria do outro, lente de 35–85 mm; respiração mínima, inclinação ou push-in | manequim genérico de frente, plástico brilhante, sem contato com o chão, gesto teatral |
| `objeto` | **um** objeto dominante, material tátil, recorte de luz, scanner ou bloom; rotação lenta ou revelação de detalhe | objeto escolhido pela estética, ou vários símbolos disputando o quadro |
| `cartela` | preto levantado ou still dessaturado, texto curto e grande, glow discreto; **sentence case** é válido e frequente; entrada seca, com tempo real de leitura | parágrafo, CAPS LOCK automático, contorno preto grosso, fundo preto sem textura |
| `dado` | uma ou duas séries, sem grade inútil, texto de 62–78 px a 1080 de largura, laterais acima de 110 px; barra em 0,5–0,7 s ease-out | dashboard genérico, três séries ou mais, gráfico gerado como imagem sem rastro |
| `arquivo` | documento, jornal, foto ou vídeo real, tratado sem perder a natureza; crop, zoom documental, destaque localizado | material dramático sem relação causal, origem desconhecida, fabricado passando por real |
| `obra` | crop respeitoso, 2.5D opcional, movimento lento | upscale que inventa pincelada, meio-tom forte, crop que destrói a narrativa da obra |
| `broll` | uma fonte de luz principal, contraste alto, sujeito entre 35% e 80% da altura; estático ou push-in de 2–5% em 3–5 s | stock bonito sem relação com a frase, luz chapada, movimento rápido gratuito |
| `cotidiano` | celular, luz disponível, imperfeição preservada, ação contínua | banco genérico de rotina, polido como comercial |
| `tela` | legível no momento certo, reflexo e mão plausíveis; dados pessoais anonimizados | interface ilegível, dado privado, marca não autorizada, tela que não prova nada |
| `tvcrt` | CRT grafite dos anos 1990, vidro curvo, scanline fina, bloom, aberração; conteúdo próprio, licenciado ou domínio público | filtro de scanline num retângulo plano, TV sem volume, trecho protegido |
| `hibrido` | placa dessaturada, figura branca a 18–32% da altura, oclusão, sombra, spill, grão e vinheta comuns | adesivo luminoso flutuando, perspectiva ou luz divergentes, sem oclusão |
| `pessoa` | pequena no espaço, através de porta ou janela; plano estável, sustentado mais que um insert | reenquadrar como talking head, luz de estúdio, cortar antes de a distância significar |

Pela função da fala, as candidatas de partida (também do `category-grammar.md`
do Codex). É ponto de partida, não fórmula, e `fala` continua sendo o padrão:

| Função do momento | Classes candidatas |
| --- | --- |
| gancho psicológico ou nostálgico | `personagem`, `tvcrt` |
| metáfora ou conceito | `objeto`, `dado` |
| evidência externa ou histórica | `arquivo`, `obra`, `tela` |
| escalada emocional, atmosfera | `broll`, `cotidiano` |
| clímax, virada | `hibrido` |
| conclusão ou respiro | `cartela`, `pessoa` |

Para cada troca de plano, a pergunta do Codex que vale guardar: **o que esta
imagem faz a fala significar ou sentir que a anterior não fazia?** Se a
resposta é "fica bonito", a troca sai.
