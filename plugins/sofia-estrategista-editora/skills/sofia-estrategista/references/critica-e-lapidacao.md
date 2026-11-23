# Crítica, lapidação e ajustes

Três situações parecidas, com regras diferentes:

1. **Lapidar um card:** a Sofia grifa o roteiro e a pessoa aceita ou recusa cada grifo.
2. **Criticar um roteiro solto** (colado no chat, sem card): veredicto curto, uma pergunta e a reescrita.
3. **Ajuste pedido pela pessoa:** ela diz o que quer mudar, e a Sofia muda só aquilo.

Com o conector ligado, leia antes a peça `instrucoes/critica` do `sofia_metodo`. Ela vale mais que esta página.

## 1. Lapidar com grifos

Lapidar faz parte do caminho: quando a pessoa escolhe a versão do roteiro, diga em uma frase por que vale e ofereça começar. Se ela quiser pular, respeite. Quando ela aceitar, pedir para lapidar ou jogar o card em Lapidar, o trabalho é grifar. Não reescreva o roteiro inteiro.

Antes do primeiro grifo, chame `sofia_preparar_escrita` com `tipo: "critica"`. O pacote traz a versão escolhida, as regras e o que a pessoa já recusou, e termina com um selo. Mande esse selo no campo `selo` de `sofia_grifos`. Sem ele, `sofia_grifos` não grava os seus grifos e devolve o pacote. Mover o card para Lapidar sem grifos também não move: devolve o pacote da crítica. Se a conversa já tem partes de um pacote anterior deste card (o método, o perfil, o cérebro, a pesquisa, a base), diga quais em `ja_tenho` e mande o selo desse pacote: elas não voltam, a não ser que tenham mudado, e as regras da crítica vêm sempre.

**Cada grifo tem:**
- **Trecho:** o pedaço exato do roteiro, copiado letra por letra, para o site achar e marcar.
- **Tipo:** cortar, trocar, reforçar ou dúvida.
- **Comentário:** por que mudar, em palavras simples, com o princípio entre parênteses. Exemplo: "A pessoa ainda não sabe quem é a Rose aqui, e se perde (linguagem familiar)."
- **Sugestão:** a frase nova, pronta para colar.

**Como grifar bem:**
- Leia o roteiro inteiro antes do primeiro grifo, em voz alta na cabeça.
- Grife o que mais muda o vídeo primeiro: hook, ponte, o ponto em que a pessoa desiste, o fim.
- Um grifo por problema. Não repita um grifo que já existe na versão, nem grife o mesmo trecho duas vezes.
- Respeite o que a pessoa já aprovou e o "faça" e o "evite" dela. Grifo que contraria uma preferência guardada precisa dizer isso no comentário.
- Use o método inteiro: formato, estrutura, princípios, elementos viciantes e a lista "Antes de entregar" do SKILL.md. Cada item do Piso que o roteiro quebra vira um grifo.
- Fato sem fonte vira grifo do tipo dúvida.
- Trecho que veio de comentário é fala da pessoa: mantenha as palavras e só grife se ficar incoerente. Ao chamar o ajudante `critico`, diga quais são esses trechos.

**Como mostrar:** salve com `sofia_grifos` e mostre numa tabela, para a pessoa ver tudo de uma vez.

| Nº | Trecho | Por que mudar | Sugestão |
|---|---|---|---|
| 1 | "a Rose fechou" | Ninguém sabe quem é a Rose (contexto antes do nome) | "a dona da padaria, a Rose, fechou" |

Exemplo inventado, só para mostrar a forma.

Depois da tabela, diga em uma linha como responder: "Me diz quais você aceita, tipo 'aceito 1 e 3, recuso 2', ou responda na página de lapidar do card."

**Respostas:** registre cada resposta do chat com `sofia_grifos`, pelo número. Quando todos estiverem respondidos, o servidor monta a versão nova. Leia com `sofia_video` e confirme para a pessoa qual versão ficou escolhida.

### Grifos da própria pessoa

A pessoa também grifa: no site, em qualquer etapa do card, ou ditando para você. O grifo dela é um pedido (cortar, trocar ou só comentar) e não recebe aceito nem recusado. Em `sofia_video` eles vêm numa lista separada, "Grifos do aluno".

- **Ela dita os grifos:** salve com `sofia_grifos` e `doAluno: true`. O trecho é copiado do texto da versão, e o comentário vai nas palavras dela, sem reescrever.
- **Ela pede a versão nova com os grifos dela** ("use os meus grifos da versão 3"): chame `sofia_preparar_escrita` (ajuste), escreva a versão aplicando cada pedido, mostre e salve com `sofia_salvar` (parte roteiro), `nasceuDe` igual ao número da versão grifada e o selo do pacote do ajuste. Pedido que você não seguiu, diga qual e por quê em uma linha.
- Não confunda com os seus grifos: os da pessoa não entram na tabela de aceito e recusado.
- Ao ir para Gravar, o corte e a troca que ela grifou já entram na versão que vai. Comentário sozinho não muda o texto.

A pessoa também edita o texto à mão no site. Antes de escrever, leia o card de novo (`sofia_video`): a versão mais nova pode ser dela, marcada como feita pela pessoa, e você parte dela.

## 2. Criticar um roteiro solto

Sem card (ou sem conector), a crítica é curta e vai rápido para a sugestão.

1. Pergunte o que falta para julgar: o público, onde vai postar, como vai gravar. Se souber o formato, confira as regras de escrita dele em `formatos/`; regra quebrada costuma ser a causa do roteiro não funcionar.
2. Dê o veredicto:
   - A abertura segura: sim, mais ou menos, não.
   - A pessoa assiste até o fim: sim, mais ou menos, não.
   - A pessoa compartilharia: sim, mais ou menos, não.
   - **Problema principal:** uma frase.
   - **O que está bom:** uma frase.
   - **Para melhorar:** de 2 a 3 sugestões, cada uma com o que fazer e o efeito em uma frase.
3. Antes de reescrever, faça uma pergunta só, sobre o problema principal, se a resposta depender da pessoa:
   - Assunto fraco: "Qual é a maior frustração do seu público com isso?"
   - Abertura fraca: "Qual é a coisa mais surpreendente desse assunto?"
   - Previsível: "Tem algum dado ou caso real que contradiz o óbvio?"
   - Sem curiosidade: "Qual é a revelação principal? Dá para segurar para depois?"
   - Repete demais: "Qual é a mensagem em uma frase?"
   - Fala difícil: "Como o seu público fala disso no dia a dia?"
   - Sem lição: "O que a pessoa deveria pensar diferente depois de assistir?"
4. Reescreva preservando o que funciona e usando o material que a pessoa deu. Entregue a versão nova e de 2 a 3 linhas do que mudou.

Para um diagnóstico mais completo, princípio por princípio, use [diagnostico.md](diagnostico.md).

## 3. Ajuste pedido pela pessoa

Ajuste mexe pouco, no lugar certo.

- Mude só o trecho pedido. O resto fica palavra por palavra, inclusive o que você mudaria se fosse seu.
- Nunca encurte nem resuma o roteiro sem pedido. Se achar que está longo, diga em uma linha e pergunte.
- Antes de mexer, chame `sofia_preparar_escrita` com `tipo: "ajuste"`. Salve a versão nova com o selo do fim desse pacote.
- Mostre só o que mudou, no formato "antes → depois", com o número do bloco.
- Se o ajuste mexe em outra parte (trocou um nome no hook, e o nome aparece de novo no fim), avise e ajuste as duas, mostrando as duas.
- Salve como versão nova: `sofia_salvar` com `nasceuDe` igual ao número da versão de origem. Versão que perde mais de 30% das palavras só é salva com `pediuCorte: true`, quando ela pediu o corte. Diga qual versão é a escolhida agora. Cada versão precisa ser rastreável: o que mudou e por quê.
- Se a mensagem mistura trecho do roteiro com comentário dela, separe antes: "Entendi que isto é texto do roteiro: ... e isto é o seu comentário: ...". Na dúvida, pergunte.

## Quando a pessoa está lendo

Muita gente lê o roteiro em voz alta para testar. Se ela disser que está lendo, espere. Não mande versão nova no meio da leitura. Quando ela voltar, pergunte onde travou: o ponto em que a língua enrola é o ponto a mexer.

O passo de mandar para Gravar está no SKILL.md, em "Gravar".
