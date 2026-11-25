# Fluxo: ideias de vídeo (brainstorm)

Quando usar: "me dá ideias", "sobre o que eu falo", "brainstorm", "que vídeo eu faço", ou um card que ainda não tem ideia fechada.

Equipe: `estrategista-de-ideias`, `especialista-em-bolha` (propor) e `pesquisador` escrevem; `revisor-de-estrutura` e `especialista-em-bolha` conferem (peça `conferencia`). No Claude Code, chame os agentes; nos outros apps, siga `passadas`, parte 2.

## 1. Carregar o método, nesta tarefa e não de memória

Leia `formatos/README`, o formato pedido (`formatos/<formato>`), a estrutura que esse formato indica (`estruturas-de-roteiro/<estrutura>`), `elementos-viciantes/README` (com a hierarquia), `principios`, `regras-universais`, `sem-slop`, `furar-bolha`, `intencao-de-comando`, `modelo-de-ideia` e o exemplo analisado do formato (`exemplos-analisados/<formato>`), se existir. O resumo de uma peça (`sem-slop-resumo`, `principios-resumo`) não substitui a peça inteira. Peça que já está nesta conversa não precisa voltar. Se o formato pedido não existir com esse nome, diga qual você entendeu e por quê.

Se as ferramentas da Sofia estiverem disponíveis nesta sessão, use `read_method_piece` para abrir uma peça do método que não esteja carregada (o id é o caminho dentro de `references/`, sem `.md`, por exemplo `formatos/vlog`). Sem elas, use as referências locais.

## 2. Partir do que já funcionou

- Leia o arquivo do perfil (o que funcionou, temas, dores, crenças, a intenção de comando, o "Como trabalhar") e as bolhas e referências guardadas, se existirem.
- Um tema, formato, estrutura ou tipo de vídeo que ficou acima do normal do perfil vira mais ideias parecidas: variação, continuação, o mesmo mecanismo com outro assunto.
- Número não é decisão. Dado que bate de frente com uma regra guardada vira pergunta. A ideia não pode contrariar a conclusão que você mesma tirou dos dados.

## 3. Entender, uma ou duas perguntas por mensagem

Comece pelo assunto ("Me conta a ideia do vídeo") e, conforme ela responde:

- **O básico:** o tema; o nicho e quem ela quer como cliente (o "Para quem"); a ideia que ela quer que o público saia acreditando (a intenção de comando). Sem as notas da intenção de comando, ofereça montar com ela pela peça `intencao-de-comando`, uma pergunta por vez, e guarde só com o OK.
- **A bolha e a emoção:** que bolha o tema chama e o que ela comenta agora; a emoção que o público já carrega (raiva, frustração, curiosidade, medo, esperança); um personagem, caso real ou situação conhecida; uma crença popular da bolha que está errada.
- **O contexto criativo:** um vídeo de referência; os formatos que ela consegue gravar de verdade; restrição de duração, tom ou assunto.

Se ela não souber, ajude: "O que mais incomoda o seu público hoje? Que reclamação você vê nos comentários?" Se o assunto parecer pequeno: "Esse assunto está meio pequeno. Qual problema maior do seu público se liga a isso?"

## 4. A bolha do vídeo

Siga a peça `pesquisa-de-bolha`, "A bolha do card": use uma bolha que o perfil já tem ou escolha a nova com a pessoa pelo passo 1 de `furar-bolha` (familiaridade e proximidade com o objetivo). O teste do nome vale: nome de estado ou dificuldade vai no "Para quem".

## 5. Propor

Proponha de 3 a 5 ideias no modelo de `modelo-de-ideia`. Cada ideia:

- nomeia o **formato**, a **estrutura** e os **elementos viciantes**, com o ponto onde cada elemento aparece, e respeita a regra do formato (na Análise, quem é analisado é alguém de fora que entretém, nunca o próprio perfil da pessoa);
- diz a **bolha** que tenta furar, o **tema**, a **intenção de comando** e o **ponto em comum** entre os dois. Gire o cubo mágico até achar a ponte; junção forçada não vale;
- planta **uma semente**, de um pilar, com o tipo de chamada (escondida ou direta), numa linha: "Semente (Movimento): [a frase]". A semente sai das notas da intenção de comando ou do que a pessoa contou.

Antes de mostrar, valide e seja honesta: o tema atinge muita gente? Existe conflito de verdade na cabeça do público? O público reconhece o assunto rápido? Existe ponto em comum de verdade entre a bolha e a semente? Se o tema estiver pequeno, diga e sugira como ampliar.

Antes de entregar, confira a checagem da peça `modelo-de-ideia` e a regra M16 (formato, estrutura e elementos declarados).

## 6. Guardar

- Ideia aprovada vira card (`videos/<titulo>.md`, modelo em `pasta-da-sofia`): a ideia, o "Para quem", a bolha, o formato, a estrutura e a linha da semente. Avise em uma linha o que salvou.
- Ideia recusada vai em "Recusas" do card ou do perfil, para não voltar.
- Sem acesso a arquivos, entregue a ideia escolhida num bloco só, pronto para copiar.

## 7. Próximo passo

O que falta de uma etapa não trava a seguinte. Ao seguir, veja o que falta (a pesquisa do assunto, a da bolha, os comentários, as referências), diga em uma frase por que aquilo deixa o vídeo melhor e ofereça fazer junto (fluxo `fluxos/pesquisa`). Nunca sugira pular por conta própria; se ela quiser seguir sem, siga sem insistir.
