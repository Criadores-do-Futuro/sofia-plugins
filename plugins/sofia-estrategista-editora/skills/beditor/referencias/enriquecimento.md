# Enriquecimento — o que existe no mundo sobre o que está sendo dito

O `plano.py` sabe **quando** mostrar. Não sabe **o que existe**. Quando a fala menciona
uma pesquisa, um pesquisador, um ano, um termo técnico ou um lugar, existe material real
lá fora — e material real vale mais que qualquer render bonito.

> A fala diz "em 1962, o pesquisador Murdock". O plano genérico põe um objeto-símbolo no
> preto. O plano enriquecido põe **o paper de verdade** — título, autores, periódico,
> DOI — como recorte de jornal, e o rosto do pesquisador em meio-tom, se houver imagem
> livre. A diferença entre ilustrar e documentar é essa.

## Quando enriquecer

Rode a etapa quando a fala tiver **âncora verificável**: nome próprio, ano, instituição,
estudo, número, termo com origem datada. Se o roteiro for puramente subjetivo — "você
sente que trava" — não há o que pesquisar, e o plano segue como `personagem` ou `objeto`.

## Os dois tipos que a pesquisa destrava

### `paper` — o documento citado

Mostra a **ficha bibliográfica real**: título, autores, periódico, volume, páginas, ano,
DOI. Opcionalmente uma frase curta entre aspas, com atribuição.

Regras de direito, e elas não são negociáveis:

- **Ficha bibliográfica é fato** — título, autor, periódico, ano e DOI podem aparecer.
- **Fac-símile da página, não.** Não reproduza a digitalização do paper, nem o layout
  original, nem parágrafos inteiros. O componente desenha uma ficha, não uma cópia.
- **Uma citação curta**, entre aspas, com o autor visível. Uma por vídeo, e curta mesmo.
- Se a fala afirma o que o estudo concluiu, a conclusão precisa **bater com o estudo**.
  Se você não conseguiu ler o resumo, escreva `verificado: false` e não afirme nada.

### `retrato` — a pessoa citada

Rosto em **preto e branco de papel de jornal**: cinza puro, contraste alto, meio-tom
visível, tarja com nome e ano.

- Só entra imagem **de licença livre verificada**: domínio público, Wikimedia Commons,
  acervo institucional com licença explícita. A licença vai no plano ou o asset não entra.
- **Não gere o rosto de uma pessoa real.** Nunca. Se não achou imagem livre, o componente
  cai sozinho na **ficha tipográfica** — nome, anos, instituição, em tipografia editorial
  sobre papel. Fica bom e é honesto.
- Pessoa viva merece cuidado extra: retrato fora de contexto, ao lado de uma afirmação
  que ela não fez, é problema mesmo com licença em ordem.

## O que a pesquisa deve devolver por plano

```json
{
  "id": "P00",
  "tipo": "paper",
  "texto": "murdock, 1962",
  "ideia": "por que esta imagem, em uma frase",
  "paper": {
    "titulo": "...", "autores": "...", "publicacao": "...", "ano": 1962,
    "doi": "...", "url": "...", "citacao": "", "verificado": true
  }
}
```

```json
{
  "id": "P02",
  "tipo": "retrato",
  "texto": "bennet murdock",
  "retrato": {
    "nome": "...", "anos": "1925–2018", "instituicao": "...",
    "imagemUrl": "", "licenca": "", "fonte": "",
    "status": "encontrado | sem-imagem-livre"
  }
}
```

`status: "sem-imagem-livre"` é uma resposta **boa**. É o caso comum para pesquisadores de
meados do século, e a ficha tipográfica resolve.

## O resto dos planos

A pesquisa também melhora os planos que continuam genéricos. Para cada um, escreva
`ideia`: uma frase dizendo **que imagem específica** aquele momento pede, e reescreva o
`prompt` a partir dela. "Um objeto simbólico" não é ideia. "Uma fita cassete com o meio
da fita puxado para fora e enrolado" é.

Olhe as referências: o que faz aquelas ilustrações funcionarem é que cada uma é **uma
coisa concreta**, fotografável, com uma leitura só. Nada de metáfora dupla, nada de
composição com três elementos disputando o centro.

## Densidade

Enriquecer não é encher. Num vídeo de 30 s:

- **1 a 2** planos `paper` — mais que isso vira aula
- **1** plano `retrato` — o rosto perde força repetido
- o resto continua sendo imagem, ritmo e legenda

Um documento real bem colocado carrega o vídeo inteiro. Três seguidos matam o ritmo.
