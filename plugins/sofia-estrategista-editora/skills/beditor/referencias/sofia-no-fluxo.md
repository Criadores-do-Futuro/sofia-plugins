# Sofia no fluxo — quem julga a ideia antes de ela virar pixel

## Direção atual: método Sofia, execução CapCut

Decisão do dono em 26/10/2026: os formatos criativos e o método continuam sendo
os da Sofia. As ideias de direção do Herk entram como aprimoramento da execução
do bEditor conectado ao CapCut. Leia [direcao-editorial.md](direcao-editorial.md)
para transformar o método em decisões de montagem.

### Onde consultar a Sofia

O método vem no próprio plugin, na skill `sofia-estrategista`
(`skills/sofia-estrategista/references/`). Com o conector ligado, `sofia_metodo`
devolve a versão do site, que vale mais. Peça só as peças da lista abaixo que a
etapa usa, uma vez por conversa, enquanto ainda estiverem nela (depois de um
resumo da conversa, peça de novo). Se o card já passou pelo
`sofia_preparar_escrita` nesta conversa, o pacote trouxe o formato, a estrutura
e os elementos do card, e não é preciso pedir essas de novo. O resumo de uma
peça não substitui a peça inteira. `scripts/localizar_sofia.py FORMATO`, na
raiz do plugin, devolve o caminho da ficha e dos princípios. Os caminhos abaixo
seguem o plugin Sofia antigo; procure o mesmo arquivo em
`skills/sofia-estrategista/references/`.

Leia seletivamente, conforme a etapa:

- `references/principios.md`: intenção e Psicologia Cognitiva do Engajamento;
- `references/formatos/README.md` e a ficha do formato escolhido: catálogo
  criativo e regras específicas;
- `knowledge/arquetipos-nichos-bolhas.md` e a estrutura escolhida em
  `references/estruturas-de-roteiro/`: ângulo e organização da ideia;
- `skills/critica/SKILL.md`: pertinência bloco a bloco e troca concreta;
- `skills/roteiro/SKILL.md`: quando o pedido inclui criar ou reescrever roteiro.

Não importe o processo inteiro de criação para uma simples edição. Para take
gravado, use o método para interpretar e dirigir o que existe. Se a Sofia não
estiver disponível, use as decisões já registradas do projeto e o treinamento
preservado do bEditor; informe a limitação se ela afetar uma escolha criativa.
Não invente formatos ou princípios e atribua à Sofia.

### O que a direção precisa preservar

Todo vídeo sustenta uma ideia. Identifique tema, bolha e contexto emocional;
escolha o formato a partir da intenção e dos recursos reais; use a ficha e a
estrutura escolhidas como referência. Familiaridade vem do repertório desse
público. As observações devem nomear apenas princípios efetivamente consultados
e aplicáveis ao bloco, sem transformar hipóteses sobre alcance em resultados.

Formato criativo Sofia, estilo visual e operação CapCut são dimensões distintas.
`dinamismo`, `analise`, `tela-dividida` e demais fichas não podem ser trocados por
presets de vídeos do Herk. O catálogo da Sofia é a fonte para novos formatos;
as referências do bEditor detalham a execução e as correções já aprendidas.

### Revisão editorial integrada

Compare fala, intenção e imagem com os tempos de cada momento. Verifique se a
imagem demonstra algo ou só desenha a palavra falada. Confira também momentos
sem motion: rosto e silêncio podem estar cumprindo um papel na história.

Se o áudio está gravado, declare isso na análise: não proponha reescrita como se
fosse um ajuste de imagem. Diferencie correção de montagem e sugestão de nova
gravação. Revise antes de gerar assets ou polir efeitos e depois na prévia real.

Use a crítica bloco a bloco da Sofia diretamente quando seus comandos/agentes
não estiverem expostos neste host. Não alegue consulta a agente não executada.
Delegação não é requisito desta adaptação; siga a autorização da sessão.
Um diagnóstico técnico passa pelo builder e pela validação do draft; o juízo
editorial continua separado e deve explicar o efeito sobre o espectador.

As sugestões antigas de hook/retenção do bEditor são repertório complementar.
Se prescreverem outra estrutura, cadência ou estética, prevalecem Sofia e as
decisões do dono. Não reescreva uma montagem aprovada para cumprir uma fórmula.

## Registro histórico preservado — pipeline local anterior

O relato abaixo registra o treinamento e exemplos originais. Seus comandos,
agentes, arquivos JSON e renderizadores são históricos; não substituem o fluxo
atual do CapCut nem autorizam delegação ou uma nova rodada de aprovações.

Decisão do dono em 2026-09-12, depois de ver o resultado da primeira consulta:

> "quero que o padrão do bEditor seja usar a sofia pra fazer vídeos melhores"

O bEditor tem validador, medidor e laudo. Nenhum dos três responde à única pergunta
que decide se o vídeo presta:

> **A imagem acrescenta informação que a fala não dá, ou só repete a fala em desenho?**

`validar.py` recusa cartela sem texto, buraco na linha do tempo, número sem fonte,
J-cut onde a boca aparece. Tudo isso é **integridade**. Nada disso é **pertinência**.
Uma cena pode passar em todos os testes e ainda ser o ícone da palavra que acabou de
ser dita — e foi exatamente o que aconteceu no pitch: três dos oito planos eram
ilustração redundante.

## Onde ela entra

| etapa | quando | o que ela lê |
| --- | --- | --- |
| `/sofia-estrategista-editora:dirigir` | passo 4b, depois do `GUIA.md`, antes de mostrar ao editor | arco, estrutura, o que fica e o que sai, a ideia de motion de cada momento |
| `/sofia-estrategista-editora:motion-graficos` | passo 1b, **antes de gastar geração e render** | a fala e a `motion.ideia` de cada plano, lado a lado |

Antes do render, sempre. Depois do render a crítica custa uma rodada inteira de
geração de imagem e oito clips de navegador; antes, custa uma edição de JSON.

## Como briefar

Três coisas que a Sofia não adivinha e sem as quais a crítica sai errada:

1. **O áudio está congelado.** O take já foi gravado. Sem isso ela critica a escrita da
   fala, que não é o que está em julgamento — o que se pode mudar é a imagem.
2. **Fala e ideia lado a lado, com o tempo de cada plano.** É a comparação que revela a
   redundância. Ideia solta parece sempre boa.
3. **Público, objetivo, plataforma e formato de gravação.** O formato muda a regra: em
   `tela dividida`, por exemplo, rosto permanente numa das metades é regra do formato, e
   um bloco de 12 s sem rosto é uma violação que o editor nota.

Diga também onde estão os trechos **sem** motion: a crítica mais útil que veio na
primeira rodada foi sobre um momento que não tinha imagem nenhuma e era justamente
onde a dor do espectador estava sendo nomeada.

## Como usar o que volta

`sofia:critica` dá o diagnóstico. Vale despachar junto, em paralelo, os dois agentes —
eles leem o mesmo material com olhos diferentes:

- **`sofia:analista-de-principios`** — bloco a bloco, com o princípio nomeado. É quem
  diz *por que* funciona, e o que **falta**.
- **`sofia:critico`** — o que derruba primeiro, onde o espectador desiste, e a troca
  concreta. É quem dá o veredito.

**Onde os dois divergem é informação, não empate.** Na primeira rodada eles discordaram
em três planos; em um deles (a fala nomeava duas ferramentas, a tela mostrava três
redes) bastou conferir o plano para ver que o crítico estava factualmente certo.

Leve as trocas ao editor **antes** de executar. Cada uma vira `motion.ideia` no
`guia.json` — e, quando muda o desenho e não só a descrição, também `motion.tipo` e
`dados` —, seguida de `validar.py` até zero erros.

## O que ela achou na primeira vez

Fica aqui porque são os erros que o pipeline repete sozinho se ninguém olhar:

- **Ilustrar em vez de provar.** Era um pitch de ferramenta de edição sem um único
  frame de edição boa acontecendo.
- **O ícone da palavra falada.** A voz diz "porcaria", a tela desenha um selo de recusa.
  Nada foi acrescentado. O conserto foi mostrar o defeito e deixar o espectador condenar
  junto.
- **Tempo morto na janela em que a plataforma decide.** 6,4 s parados numa palavra, aos
  14 s de vídeo.
- **Escrever a regra em vez de mostrá-la.** O plano mais importante — o único em que a
  ferramenta podia se demonstrar dentro do formato que ela vende — virou três linhas de
  texto. O guia **já dizia** para mostrar acontecendo; a implementação é que traiu a
  direção. Crítica de quem lê só o resultado pega isso; validador nenhum pega.
- **Imagem e voz apontando para coisas diferentes no mesmo segundo.** Custa
  credibilidade justamente num vídeo que vende automação.
