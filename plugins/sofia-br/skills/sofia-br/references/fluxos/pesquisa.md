# Fluxo: pesquisa do assunto e da bolha

Quando usar: "pesquisa isso", "tem fonte?", "o que estão comentando", "confere esse fato", ou antes do hook e do roteiro, quando faltam fatos ou as palavras do público.

Equipe: `pesquisador` escreve; `revisor-de-fatos` confere no roteiro (peça `conferencia`). No Claude Code, chame o agente; nos outros apps, siga `passadas`, parte 3.

Diga em uma frase por que vale: o roteiro fica bom quando tem fato com fonte e as palavras do público. São duas pesquisas, sem ordem entre elas; às vezes são a mesma.

## O assunto

1. Leia no arquivo do perfil o que a pessoa já ensinou sobre pesquisa (fontes em que confia ou que recusa, o tipo de achado que ela usa).
2. Veja se a base do assunto (`conhecimento/<assunto>.md`) já tem o fato. O item que serve vai para o card sem pesquisar de novo. Fato com data antiga é conferido de novo.
3. Busque o que falta em fonte primária: o documento, a decisão, a fala gravada, o dado oficial. A ordem e os cuidados estão em `fatos-e-fontes`.
4. Marque cada achado: o tipo (fato confirmado, acusação, versão de uma parte, opinião, hipótese), o acesso (assistiu, leu, print, só link), a data da informação e a ressalva. Achado que corrige outro diz qual substitui.
5. Guarde na seção "Pesquisa" do card: fatos-chave, contexto, crenças erradas, curiosidades, casos reais, citações. O que ficou sem fonte vai para "Não verificado" e fica fora do roteiro.
6. Quando a pessoa aprovar ou recusar uma fonte ou um tipo de achado, pergunte se guarda isso para as próximas pesquisas (`comportamento`, "Aprender com a pessoa").

Se o assunto veio de um vídeo de referência, cada afirmação do vídeo é conferida em fonte primária, e o vídeo pode ser anterior ao fato mais novo: o hook novo parte do fato mais recente.

## A bolha

Siga `pesquisa-de-bolha`, um passo por vez: buscar como a bolha busca, abrir os vídeos que pegaram, ler os comentários mais curtidos (o método sugere de 10 a 15 vídeos, como guia e sem mínimo), anotar o vocabulário e o que mexe com a bolha, separar as referências e conversar sobre o que chamou a atenção dela. Essa conversa costuma dar a ideia.

## Sem como pesquisar

Sem busca na web nem ferramenta de pesquisa conectada, siga `pesquisa-manual`: o que buscar, onde, que prints tirar e como mandar. Você lê os prints, e cada um vira comentário guardado como foi escrito, fato marcado com acesso "print" e a data que o print mostra, ou "Não verificado". Ferramenta paga só se a própria pessoa pedir, com o OK dela e a estimativa de custo (`servicos-externos`).

## Entregar

- Os achados agrupados, cada um com o link da fonte que você abriu.
- No fim, duas listas: "Fontes" (com links) e "Não verificado" (com o motivo em poucas palavras).
- Os comentários como foram escritos, com as curtidas, sem @ nem nome.
- Com acesso a arquivos, guarde no card e diga em uma linha o que entrou e onde.

O que foi guardado entra na prova da zona de fixação, nas palavras da bolha na abertura e nas falas que vieram de comentário.
