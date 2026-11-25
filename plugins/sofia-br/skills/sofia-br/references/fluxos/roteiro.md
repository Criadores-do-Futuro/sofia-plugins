# Fluxo: hook e roteiro

Quando usar: "escreve um roteiro", "me dá hooks", "abertura", "roteiro sobre X", "lista de gravação", ou um card com ideia e pesquisa pronto para escrever.

Equipe: no hook, `redator-de-hook` escreve e `revisor-o-que-nao-fazer`, `revisor-de-hook`, `revisor-de-voz` e `especialista-em-bolha` conferem. No roteiro, `roteirista` escreve e a equipe completa confere (peça `conferencia`). No Claude Code, chame os agentes; nos outros apps, siga `passadas`, partes 4 e 5.

Se as ferramentas da Sofia estiverem disponíveis nesta sessão (`list_method_pieces`, `read_method_piece`, `check_script`), rode `check_script` em todo roteiro pronto antes de entregar. Cada ponto que ele devolver é um sinal para conferir no contexto (pode ser falso positivo), e a ferramenta cobre só parte do Piso. Use `read_method_piece` para abrir uma peça do método que não esteja carregada. Sem elas, use as referências locais.

## Regras durante toda a escrita

- O tema é a decisão mais importante. Valide antes de tudo.
- Nada inventado: personagem, história, dado ou número. Pessoa real só com fonte que dê para conferir. Achado sem fonte fica em "Não verificado" e fora do roteiro.
- Escreva como a pessoa fala: frases curtas, verbo de ação, detalhe específico no lugar de adjetivo. "E", "Aí" e "Mas" podem abrir frase.
- Use a linguagem da bolha. A moral conecta com a vida do público.
- Siga a voz salva (`voz-da-pessoa`). O Piso e `sem-slop` valem por cima de tudo.
- Leia em voz alta, de cabeça. Se não soa natural, reescreva.
- O que falta de uma etapa não trava a seguinte. Ao chegar aqui, veja o que falta (pesquisa do assunto, da bolha, comentários, referências), diga em uma frase por que aquilo melhora o vídeo e ofereça fazer junto. Se a pessoa quiser seguir sem, siga.

## 0. A voz

Veja se existe voz salva (`voz-da-pessoa`). Com voz: "Vou escrever no seu jeito de falar." Sem voz: ofereça aprender uma vez (fluxo `fluxos/voz`); se ela recusar, use `como-escrever-bem` como guia.

## 1. Entender (se não veio do fluxo de ideias)

Use o que já está na conversa e no card: público, tema, ideia final, objetivo, duração, amostra de voz. Pergunte no máximo duas coisas por mensagem e só o que muda o roteiro. Não exija histórias ou resultados que a pessoa não tem: use os fatos que existem ou marque a lacuna. Se faltar pesquisa, ofereça o fluxo `fluxos/pesquisa`.

## 2. A referência (quando houver)

Se a pessoa trouxer um vídeo ou roteiro de referência, leia pelo fluxo `fluxos/analisar` e separe três coisas:

- **partes do autor:** nomes, casos, números, bordões, a história pessoal dele;
- **mecanismo:** o hook literal, a estrutura em blocos e o princípio ativado em cada bloco;
- **molde:** o texto com as partes que variam trocadas por `{variáveis}` (`{nicho}`, `{dor do publico}`, `{numero verificado}`).

Da referência, copie o mecanismo. Nome, caso, número e frase do autor ficam com ele. Número da referência sem fonte vira variável, nunca fato. Pergunte: **mais fiel à referência ou mais criativo?** Fiel mantém a ordem dos blocos, o ritmo e o tipo de frase do molde. Criativo usa só o mecanismo.

## 3. Formato e estrutura

- **Formato.** Leia `formatos/README` ("Como escolher" e a tabela de arquétipo com formato) e sugira 2 ou 3 formatos que combinem com o tema e que a pessoa consegue gravar, cada um em uma linha. Escolhido, leia `formatos/<formato>`: as regras de escrita dele valem até o fim. Se existir `exemplos-analisados/<formato>`, leia também.
- **Arquétipo e estrutura.** Leia `knowledge/arquetipos-nichos-bolhas` e `estruturas-de-roteiro/README`. Sugira 2 ou 3 estruturas, cada uma em uma linha. Escolhida, leia `estruturas-de-roteiro/<estrutura>` e distribua os achados da pesquisa nos blocos, em tópicos curtos, ainda sem texto falado. Com referência, o molde guia a distribuição.
- Formato, estrutura, elementos viciantes e princípios combinam entre si. Com acesso a arquivos, guarde o formato, a estrutura e os blocos no card.

Se a pessoa pediu um roteiro direto, escolha você o formato e a estrutura, diga a hipótese em uma linha e siga.

## 4. O hook

Leia `fazer-hook`, `zona-de-fixacao`, `knowledge/hooks-que-funcionam` e a seção "Tipo de hook" do formato.

1. Escreva de 8 a 10 opções, sem mostrar, com tipos diferentes. Use tudo junto: o método, o formato e a estrutura do card, a pesquisa, a bolha (vocabulário, o que mexe com ela, comentários bem curtidos) e o perfil.
2. Cada opção: a fala (de 1 a 3 frases curtas, o assunto e o ganho, ou a dor, nas primeiras palavras, sem saudação nem introdução, com "você" quando o assunto é um problema), o texto na tela (de 3 a 5 palavras, até 2 linhas), o que aparece nos primeiros 2 a 3 segundos e o logo depois (a primeira frase da zona de fixação). Imagem, texto e fala tratam da mesma coisa: confira sem som e só ouvindo.
3. A opção 1 é sempre um choque de crença: crença, desejo e onde o vídeo paga.
4. Todo hook é a abertura do escorregador (`furar-bolha`): identificação ou conflito, nas palavras da bolha. Um comentário de conflito com muitas curtidas pode ser uma das opções, como fala do criador.
5. Confira (conferência da etapa hook) e mostre de 3 a 5 (3 se ela não disse quantas prefere), no bloco:

```
Hook 1: [a fala, de 1 a 3 frases curtas]
Texto na tela: [de 3 a 5 palavras, até 2 linhas]
Abertura: [o que aparece nos primeiros 2 a 3 segundos e o movimento]
Assunto e ganho: [sobre o que é] / [o que a pessoa ganha]
Usa: [princípios e elementos viciantes]
Por que funciona: [tipo], [uma linha]. O vídeo paga em [bloco].
```

6. Se o card ainda não tem estilo de gravação, mostre junto dois estilos que combinam com o formato, cada um em uma linha (enquadramento, corte, texto na tela).
7. Espere a escolha. Ela pode escolher, combinar ou escrever uma versão melhor. Guarde o hook e o estilo no card. Hook ou estilo recusado vai em "Recusas". Se ela ajustar o hook escolhido, pergunte se guarda o jeito dela.

Se ela disser que quer conversar sobre o hook, converse só sobre o hook (`knowledge/hooks-que-funcionam`, "Quando a pessoa quer conversar sobre o hook"). Se ela pediu um roteiro direto, escolha um hook, diga a hipótese em uma linha e siga sem pedir outra aprovação.

## 5. O roteiro

Leia `principios`, `regras-universais`, `elementos-viciantes/README`, `como-escrever-bem`, `linguagem-simples` e `sem-slop` (uma vez por conversa).

Escreva 2 ou 3 versões (uma só, se a pessoa pedir), cada uma com estrutura ou abordagem diferente, com começo, meio e fim, e uma linha dizendo o foco.

- **O escorregador.** Abre com a bolha (o hook), desliza pelo ponto em comum no meio da estrutura sem que quem assiste perceba o corte de tema, e fecha com a moral, a semente e a chamada combinada.
- **A zona de fixação.** Logo depois do hook, de 2 a 4 frases (os 5 a 10 segundos seguintes) que confirmam a promessa sem mudar de assunto, entregam um pedaço concreto dela e mostram uma prova real com fonte, ou um exemplo concreto que a pessoa viveu. Prova inventada fica fora. Presença e capricho vão para a lista de gravação.
- **A semente.** A da ideia do card, de um pilar (`intencao-de-comando`). Autenticidade e movimento entram dentro da história, sem pausa para propaganda; o fechamento reforça uma crença do movimento. Chamada escondida na maioria dos vídeos, numa história que aconteceu; direta em cerca de 2 a cada 10.
- **O comentário.** Entra como fala do criador, sem aspas e sem metalinguagem, com as palavras o mais perto possível do original (`comportamento`, "Comentários do público").

Cada versão leva:

- **Título** e a linha do foco ("Versão 1: estrutura [nome], foco em [princípio dominante]");
- **Hook:** só a fala do hook escolhido (é o que vai para o teleprompter);
- **Como abre:** o que aparece nos primeiros 2 a 3 segundos e o texto na tela;
- **Roteiro:** o texto falado inteiro, por bloco, com as sugestões visuais à parte;
- **Princípios:** trecho, princípio e por quê;
- **Lacunas:** onde cada lacuna abre e onde fecha;
- **O que precisa ser real:** o que a pessoa precisa ter vivido, mostrar ou comprovar para gravar;
- **Duração estimada** pela leitura (sem dizer que mediu).

## 6. Conferir e entregar

1. Rode `check_script` em cada versão, se estiver disponível, e confira cada ponto que ele devolver no contexto (pode ser falso positivo). Sem ele, confira as regras M de `conferencia` à mão.
2. Confira com a equipe da etapa roteiro (agentes ou passadas) e corrija pela ordem de `conferencia`. No máximo 2 rodadas.
3. Passe pela lista "Antes de entregar" do SKILL e dê o placar de `sem-slop`; abaixo de 35 de 50, reescreva.
4. Mostre as versões e, em duas linhas, onde a pessoa deve prestar atenção. Uma linha diz que passou pela conferência.
5. Fora do roteiro: as fontes, o "Não verificado" e de qual comentário e vídeo veio cada trecho que entrou como fala.
6. Com acesso a arquivos, guarde cada versão no card. Nenhuma é apagada.

Quando pedirem só as falas, entregue só as falas, com fontes e lacunas essenciais à parte.

## 7. Escolha, crítica e gravação

- Pergunte qual versão ela prefere e se quer ajustar algo. Ajuste segue o fluxo `fluxos/melhorar`.
- Quando ela escolher, diga em uma frase por que vale lapidar (um olhar de fora pega o que quem escreveu não vê) e ofereça a crítica (fluxo `fluxos/critica`). Se ela quiser pular, siga para a gravação.
- **Lista de gravação:** cada cena com a fala, o que mostrar e onde gravar, e no fim o texto corrido para o teleprompter. A primeira cena é o hook: a fala, o que aparece nos primeiros 2 a 3 segundos e o texto na tela. Presença e capricho da zona de fixação entram aqui. Antes, confira se o hook do card, o roteiro e a versão escolhida batem entre si; se não baterem, mostre a diferença e pergunte.
- Nunca marque como gravado nem como postado sem a pessoa pedir. Para priorizar o que gravar, siga `pasta-da-sofia`, "O que gravar primeiro".

## Depois de postar

Só quando a pessoa pedir: anote no card o link e os números que ela mandar (ou que uma ferramenta de métricas que ela conectou trouxer). Fale do resultado contra o normal do perfil ("2 vezes o normal do perfil", "perto do normal"). Quando o vídeo funcionou ou ela elogiar o card, ofereça guardar no perfil o que vale a longo prazo e, à parte, o que serve para reaproveitar (hooks, trechos, estilos, achados). Mostre a proposta nos dois lados e guarde só o que ela aprovar.
