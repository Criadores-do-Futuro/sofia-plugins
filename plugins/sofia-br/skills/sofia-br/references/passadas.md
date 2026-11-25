# Passadas: a equipe da Sofia onde não há agentes

No Claude Code, cada papel da equipe é um agente do plugin. No ChatGPT, no Claude do navegador e do celular e em qualquer app em que os agentes não abrem, o mesmo plano roda em **passadas**: você faz um papel por vez, na própria conversa, lendo as peças daquele papel na hora de usar. É assim que as revisões acontecem nesses apps.

O que cada papel lê e confere está na peça `conferencia`.

## Sumário

1. As regras de toda passada
2. Ideia, bolha e pesquisa
3. Pesquisa
4. Hook
5. Roteiro
6. Ajuste
7. Crítica e lapidar
8. Subagentes do Codex

## 1. As regras de toda passada

- **Escrever separado de conferir.** Primeiro escreva tudo, sem mostrar. Depois confira como revisor, com as regras do papel na frente. Só depois corrija.
- **Veredito antes da correção.** Para cada opção e cada código, escreva para você passa, falha ou não se aplica antes de mudar qualquer palavra. A correção vem da lista de falhas.
- **As regras mecânicas.** Se a ferramenta `check_script` estiver disponível, rode nela cada texto pronto (hook ou roteiro) e confira cada ponto que ela devolver no contexto: é um sinal automático, pode ser falso positivo, e a ferramenta cobre só parte do Piso. Sem ela, confira à mão as regras M da peça `conferencia`.
- **Ordem para juntar as falhas,** quando duas brigam: Piso; fatos; a voz da pessoa e o "como trabalhar" dela; hook (assunto e clareza antes de estilo); bolha; método.
- **No máximo 2 rodadas.** Na segunda, confira só os códigos que falharam. O que ainda falhar vai para a pessoa como observação curta.
- **Gerar muitos, mostrar poucos.** Hook: de 8 a 10 escritos, de 3 a 5 mostrados, com tipos diferentes e menos falhas.
- **Uma linha para a pessoa.** Depois da conferência, diga só que o texto passou pela conferência. A tabela dos vereditos fica para quando ela pedir.
- **Peça que falta.** Se uma peça do papel não estiver nesta conversa, abra o arquivo dela (ou, com as ferramentas da Sofia, `read_method_piece` com o id dela). Peça lida nesta conversa não precisa voltar, a não ser depois de um resumo da conversa.

## 2. Ideia, bolha e pesquisa

1. Leia as peças do `estrategista-de-ideias` e monte, sem mostrar, de 3 a 5 direções no modelo de ideia e até 5 perguntas, da que mais muda a direção para a que menos muda.
2. Leia as peças do `especialista-em-bolha` (modo propor) e monte 2 ou 3 bolhas candidatas com o plano de pesquisa de cada uma. Se já há tema, faça junto a primeira pesquisa, pela parte 3.
3. Converse: uma pergunta por vez, a mais valiosa primeiro. Guarde cada decisão no card (fluxo `fluxos/ideias`).
4. Se a resposta da pessoa mudar a direção, releia só as regras do papel afetado.
5. Fechar a ideia: confira cada ideia com os códigos do `revisor-de-estrutura` e do `especialista-em-bolha` (etapa ideia), dê o veredito, corrija e confira a regra M16.

## 3. Pesquisa

1. Com busca na web ou uma ferramenta de pesquisa conectada: pesquise pelas peças do `pesquisador`. Cada achado sai marcado (tipo, acesso, data, ressalva e link), os comentários como foram escritos, sem @, e o que ficou sem fonte vai para "Não verificado".
2. Sem como pesquisar: siga a peça `pesquisa-manual`, com o que buscar, onde, que prints tirar e como mandar.
3. Cada print que chegar vira comentário guardado como foi escrito, fato marcado com acesso "print" e a data que o print mostra, ou "Não verificado".

## 4. Hook

1. Leia as peças do `redator-de-hook`.
2. Escreva de 8 a 10 opções, sem mostrar: fala, texto na tela, primeiros 2 a 3 segundos, logo depois, tipo de hook e elementos, por que pega com esta bolha. Use as falas da pessoa nesta conversa como ela disse.
3. Rode `check_script` em cada opção, se estiver disponível, ou confira as regras M à mão. Corrija o que se confirmar como falha.
4. Confira com os códigos do `revisor-o-que-nao-fazer`, do `revisor-de-hook`, do `revisor-de-voz` e do `especialista-em-bolha`, etapa hook.
5. Veredito por código, para cada opção. Junte as falhas pela ordem da parte 1 e corrija. Rodada 2 só nos códigos que falharam.
6. Mostre de 3 a 5 e os estilos de gravação, com a linha da conferência.

## 5. Roteiro

Igual ao hook, com estas trocas:

- O escritor é o `roteirista`, com 2 ou 3 versões (uma, se a pessoa pediu).
- Rode `check_script` em cada versão inteira, se estiver disponível, e confira cada ponto que ele devolver no contexto (pode ser falso positivo).
- Revisores, equipe completa: `revisor-o-que-nao-fazer`, `revisor-de-hook` (só o hook e a zona de fixação), `revisor-de-voz`, `especialista-em-bolha`, `revisor-de-estrutura` e `revisor-de-fatos`. Com seis papéis, confira em dois grupos de três.
- Se a conversa estiver longa, a equipe econômica serve: `revisor-o-que-nao-fazer`, `revisor-de-estrutura` e `revisor-de-voz`. Diga à pessoa que foi a conferência curta.

## 6. Ajuste

- Mude só o trecho pedido. Rode `check_script` na versão nova inteira, se estiver disponível.
- Confira o trecho mudado com os códigos do `revisor-o-que-nao-fazer` e do `revisor-de-voz`, etapa ajuste.
- Quando o ajuste muda um bloco inteiro, escreva pelas peças do `roteirista`, etapa ajuste.

## 7. Crítica e lapidar

1. Rode `check_script` na versão, se estiver disponível, ou confira as regras M à mão. Cada ponto que se confirmar como falha vira grifo pronto, com o código M.
2. Confira com os códigos dos revisores do roteiro e do `critico`, etapa crítica (em dois grupos, se ficar grande). Cada falha vira grifo: trecho exato, tipo (cortar, trocar, reforçar ou dúvida), comentário em palavras simples com o princípio entre parênteses, sugestão e os códigos.
3. Tire os grifos repetidos e ordene do que mais muda o vídeo para o que menos muda.
4. Siga o fluxo `fluxos/critica` para mostrar e registrar as respostas.

## 8. Subagentes do Codex

O plugin do Codex não leva os arquivos de agente, mas o Codex pode abrir subagentes. Para cada papel do plano, abra um subagente com esta instrução:

> Você é o {papel} da Sofia, na etapa {etapa}. Leia na skill `sofia-br` a peça `conferencia` (a linha do {papel}) e as peças que ela lista. {o texto a conferir ou as notas da conversa}. Siga as regras do papel e devolva no formato da peça `conferencia`. Só leia e devolva: não grave nada.

Os revisores rodam juntos. Junte os vereditos como na parte 1. Se os subagentes não abrirem, siga as passadas desta página.
