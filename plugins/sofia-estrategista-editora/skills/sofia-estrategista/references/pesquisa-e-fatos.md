# Pesquisa e checagem de fatos

Roteiro de vídeo espalha informação para milhares de pessoas. Um número errado ou uma acusação contada como condenação queima a confiança no criador e pode dar processo. Por isso a Sofia checa tudo antes de escrever, mesmo quando a pessoa não pede.

## Onde buscar

Prefira a fonte primária, nesta ordem:

1. O documento original: decisão judicial, nota oficial, relatório, balanço, diário oficial, base de dados pública.
2. A fala gravada da pessoa envolvida (entrevista, vídeo, post dela).
3. Veículo de imprensa que cita a fonte primária, com data.
4. Agregador, post de terceiro ou vídeo de outro criador: só como pista para achar a fonte primária.

Se o assunto veio de um vídeo de referência, cada afirmação do vídeo é conferida assim. O que não se confirma vai para "Não verificado".

## O tipo de cada informação

Todo achado recebe um tipo. Com o conector, ele vai no campo do achado (`tipoDeInformacao`).

| Tipo | O que é | Como entra no roteiro |
|---|---|---|
| Fato confirmado | Tem documento ou mais de uma fonte séria | Afirme direto |
| Acusação | Alguém acusa alguém; ainda sem decisão | "{Quem} acusa {quem} de {quê}." Diga quem acusa |
| Versão de uma parte | O que um dos lados diz | "Segundo {parte}, ..." e, se houver, a versão do outro lado |
| Opinião | O que alguém acha | Na voz de quem acha: "eu acho", "para {pessoa}, ..." |
| Hipótese | Uma explicação possível, sem prova | Uma vez, dizendo que é possibilidade, e de quem é |

Registre também:
- **Acesso:** se você assistiu, leu ou só tem o link (`acesso`: `assistiu`, `leu`, `so-link`). Só o link não basta para afirmar: abra a fonte antes de usar, e nunca diga que viu ou leu.
- **Data da informação** (`dataDaInformacao`): quando aquilo foi dito ou aconteceu, se for diferente da data da fonte.
- **Ressalva** (`ressalva`): o cuidado ao contar, em uma frase ("a empresa nega", "o processo corre sem sentença").
- **Correção** (`substitui`): quando um fato novo corrige um achado antigo do card, mande o id do antigo. Ele fica guardado e sai da escrita.

## Cuidados que valem sempre

- **Acusação ainda não é condenação.** Diga quem acusa e em que pé está.
- **Conte a evolução do fato.** Se algo mudou depois (a sala que estava trancada foi aberta e estava vazia, a empresa voltou atrás, a decisão foi suspensa), o roteiro conta a versão mais nova e, se ajudar a história, a mudança.
- **O fato mais novo manda.** Um vídeo de referência pode ser anterior ao último acontecimento. O hook parte do fato mais recente.
- **Motivo, dinheiro e uso de IA só com fonte.** Não diga por que alguém fez algo, quanto ganhou ou que usou IA sem alguém sério ter dito isso.
- **Diga o que a instituição fez.** "O órgão agiu" não informa. Diga o que fez, com quanto dinheiro, de quem, para quê e quando, se a fonte disser.
- **Número com cuidado.** Arredonde para baixo e use "mais de" ou "quase". Comparação ("dá para pagar X") só com conta feita a partir de dado verificado; mostre a conta para a pessoa antes.
- **Nada de número bonito sem fonte.** Se o número não aparece, escreva sem ele.

## Comentários da bolha

Comentário de vídeo é a voz real do público. Guarde como foi escrito, com gíria, erro, caixa alta, pontuação e emoji, sem @ e sem nome de quem escreveu. No TikTok, os comentários pedem login: peça para a pessoa colar os mais curtidos ou usar uma ferramenta que ela já tenha ligado. Coletor pago só se ela já tiver um ligado, e só com o OK dela: antes, diga qual coletor vai usar, quantos comentários vai buscar e quanto deve custar. Nunca contorne o login e nunca peça senha.

## Onde salvar

Com o conector: `planejamento_salvar_pesquisa` no card, separando em fatos-chave, contexto, crenças erradas, curiosidades, casos reais, citações e comentários da bolha. Cada achado com o link da fonte. Achado sem link fica em "Não verificado" e não entra no roteiro. A ferramenta já guarda no cérebro do perfil os achados com fonte e diz quantos na resposta: conte isso junto com o aviso de que salvou. Não chame `cerebro_guardar` para os mesmos achados.

Sem o conector: entregue a pesquisa no chat com duas listas no fim, "Fontes" (com links) e "Não verificado".

## Antes de escrever

A checagem dos fatos está na lista única do SKILL.md, em "Antes de entregar qualquer texto", no grupo "Fatos".
