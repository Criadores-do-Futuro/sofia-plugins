# A conferência: regras com código e o que cada papel lê

Escrever fica separado de conferir. Cada regra do método tem um código, e o texto da regra é a pergunta da conferência: passa, falha ou não se aplica. Os códigos estão dentro de cada peça, na seção "Antes de entregar" (ou equivalente).

## De onde vem cada código

| Código | Peça |
|---|---|
| P | `piso` |
| SS | `sem-slop` |
| LS | `linguagem-simples` |
| GL | `glossario` |
| CE | `como-escrever-bem` |
| VZ | `voz-da-pessoa` |
| FH | `fazer-hook` |
| ZF | `zona-de-fixacao` |
| HQ | `knowledge/hooks-que-funcionam` |
| FB | `furar-bolha` |
| IC | `intencao-de-comando` |
| PB | `pesquisa-de-bolha` |
| PM | `pesquisa-manual` |
| FT | `fatos-e-fontes` |
| RU | `regras-universais` |
| PV | `principios` |
| MI | `modelo-de-ideia` |
| EV | `elementos-viciantes/README` |
| ES.<estrutura>.<n> | o checklist da estrutura do card (`estruturas-de-roteiro/<estrutura>`) |
| FM.<formato>.<n> | as regras de escrita do formato do card (`formatos/<formato>`), na ordem em que aparecem |
| FM.H | a seção "Tipo de hook" do formato do card |
| CR | `fluxos/critica`, "O olho de quem assiste" |

Nas listas abaixo, "o formato", "a estrutura", "o exemplo" e "os dominantes" são a peça do formato do card, a da estrutura, o exemplo analisado do formato (`exemplos-analisados/<formato>`, se existir) e as peças dos elementos viciantes dominantes do formato.

## Regras mecânicas (M1 a M16)

Estas dá para conferir quase sem interpretação. Se a ferramenta `check_script` estiver disponível nesta sessão, ela confere boa parte delas e devolve pontos para revisar, que podem ser falso positivo; sem ela, confira à mão.

- **M1** (falha). Sem travessão.
- **M2** (falha). Sem advérbio terminado em -mente.
- **M3** (falha). Sem o molde de contraste binário da peça `sem-slop`: afirme direto.
- **M4** (falha). Resultado comparado com "o normal do perfil", sem termo de estatística.
- **M5** (falha). Comentário entra como fala do criador, sem metalinguagem.
- **M6** (falha). Sem as frases proibidas da peça `sem-slop`.
- **M7** (falha). Texto na tela de 3 a 5 palavras, em até 2 linhas.
- **M8** (falha). Fala do hook com até 3 frases.
- **M9** (falha). Hook sem saudação nem introdução no começo.
- **M10** (aviso). Problema dito com "você", e não em primeira pessoa.
- **M11** (aviso). Três frases seguidas do mesmo tamanho.
- **M12** (aviso). Pergunta só na chamada final ou quando veio de um comentário.
- **M13** (aviso). Número que não aparece na pesquisa do card.
- **M14** (aviso). Frase que abre com "o que", "por que" ou "como" no lugar da afirmação.
- **M15** (aviso). Voz passiva: diga quem faz.
- **M16** (falha). Na ideia, formato, estrutura e elementos declarados.

Falha segura a entrega até ser corrigida. Aviso não reprova, mas conserte quando a troca for simples.

## O que cada papel lê e confere

| Papel | Etapa | Códigos | Peças |
|---|---|---|---|
| estrategista-de-ideias | ideia (escreve) | MI, PV, RU | `modelo-de-ideia`, `principios`, `regras-universais`, `formatos/README`, `estruturas-de-roteiro/README`, `elementos-viciantes/README`, `intencao-de-comando-resumo`, `furar-bolha-resumo`, `knowledge/principios-exemplos`, `glossario` |
| especialista-em-bolha | ideia (propõe) | FB, IC, PB | `furar-bolha`, `intencao-de-comando`, `pesquisa-de-bolha`, `knowledge/arquetipos-nichos-bolhas` |
| especialista-em-bolha | hook, roteiro, crítica (confere) | FB, IC, PB | `furar-bolha`, `intencao-de-comando` (no hook, o resumo), `pesquisa-de-bolha` |
| pesquisador | ideia, pesquisa (escreve) | FT, PB, PM | `fatos-e-fontes`, `pesquisa-de-bolha`, `pesquisa-manual`, `regras-universais` |
| redator-de-hook | hook (escreve) | P, FH, ZF, HQ, VZ, SS, LS, GL, FM.H | `piso`, `fazer-hook`, `zona-de-fixacao`, `knowledge/hooks-que-funcionam`, `knowledge/arquetipos-nichos-bolhas`, `fluxos/roteiro`, o formato, o exemplo, os dominantes, `voz-da-pessoa`, `linguagem-simples`, `sem-slop-resumo`, `principios-resumo`, `furar-bolha-resumo` |
| roteirista | roteiro (escreve) | P, ES, FM, EV, ZF, IC, FB, FT, VZ, LS, GL, CE, RU | `piso`, `fluxos/roteiro`, a estrutura, o formato, `zona-de-fixacao`, os dominantes, o exemplo, `voz-da-pessoa`, `como-escrever-bem`, `fatos-e-fontes`, `intencao-de-comando-resumo`, `furar-bolha-resumo`, `regras-universais`, `linguagem-simples`, `sem-slop-resumo` |
| roteirista | ajuste (escreve) | P, SS, LS, GL, VZ, CE | `piso`, `voz-da-pessoa`, `como-escrever-bem`, `linguagem-simples`, `sem-slop-resumo` |
| revisor-o-que-nao-fazer | hook, roteiro, crítica | P, SS, FH9 a FH12, LS, GL | `piso`, `sem-slop`, `fazer-hook`, `linguagem-simples`, `glossario` |
| revisor-o-que-nao-fazer | ajuste | P, SS, LS, GL | `piso`, `sem-slop`, `linguagem-simples`, `glossario` |
| revisor-de-hook | hook | FH, ZF, HQ, FM.H | `fazer-hook`, `zona-de-fixacao`, `knowledge/hooks-que-funcionam`, o "Tipo de hook" do formato |
| revisor-de-hook | roteiro, crítica (só o hook e a zona de fixação) | FH1 a FH8, ZF, FM.H | `fazer-hook`, `zona-de-fixacao`, o "Tipo de hook" do formato |
| revisor-de-voz | hook | VZ, LS, SS21 | `voz-da-pessoa`, `linguagem-simples`, `sem-slop` |
| revisor-de-voz | roteiro, crítica | VZ, CE, LS, SS21 | `voz-da-pessoa`, `como-escrever-bem`, `linguagem-simples`, `sem-slop` |
| revisor-de-voz | ajuste | VZ, CE, LS | `voz-da-pessoa`, `como-escrever-bem`, `linguagem-simples` |
| revisor-de-estrutura | ideia | MI, PV, RU, EV | `modelo-de-ideia`, o formato, a estrutura, `elementos-viciantes/README`, `principios`, `regras-universais` |
| revisor-de-estrutura | roteiro, crítica | ES, FM, EV, PV, RU | a estrutura, o formato, `elementos-viciantes/README`, os dominantes, `principios`, `regras-universais` |
| revisor-de-fatos | roteiro | FT, RU1 a RU10, PM, PB | `fatos-e-fontes`, `regras-universais`, `pesquisa-manual` |
| revisor-de-fatos | crítica | FT, RU1 a RU10 | `fatos-e-fontes`, `regras-universais` |
| critico | crítica | CR | `fluxos/critica`, `diagnostico`, `principios-resumo` |

## A equipe de cada etapa

| Etapa | Escreve | Confere |
|---|---|---|
| Ideia | estrategista-de-ideias, especialista-em-bolha (propor) e pesquisador | revisor-de-estrutura e especialista-em-bolha |
| Pesquisa | pesquisador | revisor-de-fatos, no roteiro |
| Hook | redator-de-hook | revisor-o-que-nao-fazer, revisor-de-hook, revisor-de-voz e especialista-em-bolha |
| Roteiro | roteirista | revisor-o-que-nao-fazer, revisor-de-hook (só hook e zona de fixação), revisor-de-voz, especialista-em-bolha, revisor-de-estrutura e revisor-de-fatos |
| Ajuste | a Sofia, ou o roteirista se o ajuste muda um bloco inteiro | revisor-o-que-nao-fazer e revisor-de-voz |
| Crítica | os revisores do roteiro e o critico, em grifos | as regras M |

## Como juntar os vereditos

- Para cada opção e cada código, o veredito vem antes de qualquer correção.
- Quando duas correções brigam, vale esta ordem: 1) Piso; 2) fatos; 3) a voz da pessoa e o "como trabalhar" dela; 4) hook (assunto e clareza antes de estilo); 5) bolha; 6) método.
- No máximo 2 rodadas. Na segunda, confira só os códigos que falharam. O que ainda falhar vai para a pessoa como observação curta.
- Depois da conferência, diga à pessoa só que o texto passou pela conferência. A tabela dos vereditos fica para quando ela pedir.

## Formato da resposta de quem confere

- Primeira linha: "Conferidas:" e os códigos de todas as regras conferidas.
- Depois, uma tabela só com as falhas: opção, código, trecho exato, correção pronta na voz da pessoa.
- Última linha: as opções que passaram em tudo.
- Na crítica, cada falha vira grifo: trecho exato, tipo (cortar, trocar, reforçar ou dúvida), comentário em palavras simples com o princípio entre parênteses, sugestão e os códigos.
