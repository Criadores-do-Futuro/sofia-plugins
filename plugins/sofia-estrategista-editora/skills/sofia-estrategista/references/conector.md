# Mapa do conector Sofia Estrategista

O conector guarda o método da Sofia na versão mais nova, os números de cada perfil, o cérebro com o que a Sofia já aprendeu, a biblioteca de referências e os cards do planejamento. Esta página diz o que cada ferramenta faz e quando chamar.

Sobre como usar cada ferramenta (nome, campos, ordem das chamadas), a descrição que vem nela e as instruções que o conector manda no começo da conversa valem mais que esta página. Os nomes podem mudar entre versões: se um nome daqui não existir, procure o mais parecido e leia a descrição dele. O nome pode vir com um prefixo do aplicativo (por exemplo `mcp__plugin_sofia-estrategista_sofia-estrategista__`). O Piso, a segurança e o OK antes de guardar algo sobre a pessoa valem sempre, mesmo que a descrição de uma ferramenta mande guardar na hora.

## Sumário

1. Método e vídeos (`sofia_*`)
2. Quadro de planejamento (`planejamento_*`)
3. Cérebro do perfil (`cerebro_*`)
4. Referências (`referencia_*`)
5. Perfis (`perfil_*`)
6. Curso
7. O que pode mudar

## 1. Método e vídeos

| Ferramenta | O que faz | Quando |
|---|---|---|
| `sofia_meus_videos` | Os vídeos em andamento, a etapa de cada um, se a voz está salva e o próximo passo sugerido | Começo de toda conversa de conteúdo |
| `sofia_preparar_escrita` | Devolve o pacote da escrita: as regras, como trabalhar com esta pessoa neste perfil, o que ela já recusou, a versão atual (no ajuste e na crítica), o público, o cérebro, o método, a pesquisa e o card | Antes de sugerir ideias, escrever hooks, escrever ou ajustar o roteiro e criticar |
| `sofia_metodo` | Devolve uma peça do método | Quando o pacote não trouxe a peça, ou sem card |
| `sofia_video` | O vídeo inteiro: ficha, pesquisa, estrutura, roteiros com os grifos numerados, lista de gravação e os ids | Ver versões anteriores, referências ligadas, antes de gravar |
| `sofia_salvar` | Salva a parte `roteiro` (cada versão) ou a parte `gravacao` (cenas e teleprompter) | Logo depois de escrever |
| `sofia_grifos` | Salva grifos numa versão, ou registra aceito e recusado pelo número | Lapidar |
| `sofia_perfil` | Lê ou salva o resumo da voz da pessoa (tom, vocabulário, expressões, o que evita) | Aprender a voz |
| `sofia_exportar` | O vídeo inteiro em Markdown | A pessoa quer copiar ou baixar |
| `sofia_apagar` | Apaga dados da pessoa | Só a pedido dela, nesta conversa |

**Peças do `sofia_metodo`:** `principios`, `regras-universais`, `sem-slop`, `sem-slop-resumo`, `como-escrever-bem`, `diagnostico`, `formatos/<formato>` (e `formatos/README`), `estruturas-de-roteiro/<estrutura>`, `elementos-viciantes/README`, `exemplos-analisados/<formato>`, `knowledge/arquetipos-nichos-bolhas`, `knowledge/hooks-que-funcionam`, `knowledge/principios-exemplos`, `instrucoes/roteiro`, `instrucoes/critica`, `instrucoes/estilo`, `instrucoes/ler-videos`, `hook` ou `hook/<formato>`. Com `lista`, ela devolve o que existe.

**Detalhes do `sofia_preparar_escrita`:**
- Recebe o `videoId` (o id do card) e o `tipo`: `ideia`, `hook`, `roteiro`, `ajuste` ou `critica`.
- `sofia_salvar` (roteiro), `sofia_grifos` (grifos novos da Sofia) e `planejamento_mover_card` (hook e estilo) só gravam com o pacote do tipo certo pedido há pouco. Sem ele, devolvem o pacote no lugar de gravar.
- `tipo: "roteiro"` num card em Brainstorming ou Estruturar, sem hook e estilo escolhidos, vira pacote de hook.
- `ajuste` e `critica` precisam de um roteiro salvo. Sem roteiro, a ferramenta dá erro.
- Em `recusou`, guarde o que a pessoa recusou neste card: `hooks`, `estilos` e `ideias` (até 10 de cada) e `modoDeVoz` (`true` quando ela não quis ouvir o roteiro pelo modo de voz). O que foi recusado não volta.

**Detalhes do `sofia_salvar` (parte `roteiro`):**
- Campos: `titulo`, `hook`, `comoAbre`, `roteiro` (o texto falado), `principios` (trecho, princípio e porquê), `lacunas` (a curiosidade aberta e onde fecha), `oQuePrecisaSerReal`, `modo` (`fiel` ou `criativo`).
- Cada card do planejamento já é um vídeo: o id do card é o `videoId`. Não crie outro vídeo para um card.
- **Versão alternativa:** sem `nasceuDe`, a versão fica ao lado das outras, como as 2 ou 3 da primeira escrita.
- **Ajuste:** com `nasceuDe` igual ao número da versão de origem. As versões antigas ficam guardadas.
- **Corte:** a versão que perde mais de 30% das palavras da versão de origem só é salva com `pediuCorte: true`. Use só quando a pessoa pediu para cortar.
- **Versão escolhida:** a nova vira a escolhida se o card não tinha uma, ou se ela é ajuste da escolhida. Senão, fica como alternativa até a pessoa escolher (`planejamento_editar_card` com `roteiroEscolhido`).
- O mesmo texto salvo duas vezes não cria versão nova.
- Em Brainstorming ou Estruturar, sem hook e estilo escolhidos, a ferramenta não salva e devolve o pacote de hook.
- Salvar um roteiro com o card em Estruturar leva o card para Revisar. O card nunca volta de coluna.
- Tema, pesquisa, ideia e estrutura têm ferramenta própria no quadro (veja a parte 2).

**Detalhes do `sofia_grifos`:**
- Cada grifo leva: o trecho exato do roteiro (que só aparece num lugar), o tipo (`cortar`, `trocar`, `reforcar` ou `duvida`), o comentário em palavras simples com o princípio entre parênteses e a sugestão (vazia em cortar, a pergunta em dúvida).
- Grifos novos da Sofia precisam do pacote da crítica pedido há pouco (`sofia_preparar_escrita` com `tipo: "critica"`).
- **Grifos da pessoa:** com `doAluno: true`, o comentário vai nas palavras dela e o tipo é cortar, trocar ou dúvida. Não há aceito nem recusado: são os pedidos dela. Para escrever a versão nova a partir deles, chame `sofia_preparar_escrita` (ajuste) e salve com `nasceuDe` da versão grifada.
- Respostas vão pelo número do grifo. Sem grifos nem respostas, a ferramenta lista os grifos da versão.
- Com todos respondidos, o servidor monta e salva a versão nova.

## 2. Quadro de planejamento

O quadro tem as colunas Brainstorming, Estruturar, Revisar, Lapidar e Gravar. Cada coluna pede uma coisa pronta para o card entrar.

| Coluna | O card chega com | Quem decide |
|---|---|---|
| Estruturar | formato, estrutura, elementos e princípios | a pessoa aprova |
| Revisar | hook e estilo escolhidos pela pessoa. O roteiro é escrito aqui | a pessoa escolhe hook e estilo, a Sofia escreve |
| Lapidar | grifos com comentário | a Sofia grifa, a pessoa aceita ou recusa cada um |
| Gravar | a versão escolhida, com os grifos aceitos | a pessoa escolhe a versão |

| Ferramenta | O que faz | Quando |
|---|---|---|
| `planejamento_quadro` | Os cards e a coluna de cada um | A pessoa fala dos cards |
| `planejamento_criar_card` | Cria um card | Ideia aprovada |
| `planejamento_salvar_pesquisa` | Salva a pesquisa nos grupos: fatos-chave, contexto, crenças erradas, curiosidades, casos reais, citações, comentários da bolha. Também guarda outras ideias de vídeo e leva os achados com fonte para o cérebro do perfil (conte isso, com a linha que a ferramenta devolve) | Depois de pesquisar |
| `planejamento_estruturar_card` | Grava o que entra em cada bloco da estrutura, em tópicos curtos ligados aos achados | Em Estruturar, sem texto falado |
| `planejamento_mover_card` | Move o card de coluna | Quando a coluna nova tem o que pede |
| `planejamento_editar_card` | Atualiza campos: tema, notas, ideia, paraQuem, formato, estrutura, elementos, princípios, hook, estilo, roteiroEscolhido, statusDeGravacao e outros | Trocar a versão escolhida, corrigir um campo |
| `planejamento_gravar` | O roteiro escolhido pronto para gravar, com a situação da gravação | Card em Gravar |
| `planejamento_postado` | Grava o link, os números e se funcionou. Se funcionou, também guarda o resultado no cérebro do perfil (conte isso) | Só a pedido, depois de postar |
| `planejamento_guardar_card` | Guarda o card inteiro no cérebro, em Cards guardados | A pessoa quer guardar para depois |
| `planejamento_reusar_card` | Cria um card novo a partir de um guardado ou de um que funcionou | Repetir o que deu certo |
| `planejamento_dividir_card` | Divide um card em 2 a 6 | Uma estrutura rende mais de um vídeo |
| `planejamento_juntar_duplicado` | Junta dois cards iguais | Só a pedido |

**Detalhes do `planejamento_salvar_pesquisa`:** cada achado leva o link da fonte e pode levar:
- `tipoDeInformacao`: `fato-confirmado` (a fonte comprova), `acusacao` (alguém acusa, sem condenação), `versao-de-parte` (o lado de uma das partes), `opiniao` (o que alguém acha) ou `hipotese` (o que pode ser, sem prova).
- `acesso`: `assistiu`, `leu` ou `so-link` (só tem o link, sem abrir).
- `dataDaInformacao`: quando o fato aconteceu ou foi dito, se for diferente da data da fonte (até 40 caracteres).
- `ressalva`: o cuidado ao usar, em uma frase (até 300 caracteres). Por exemplo: "a empresa nega".
- `substitui`: o id de um achado deste card que a informação nova corrige. O antigo fica guardado e sai da escrita.

O servidor avisa quando há acusação (diga quem acusa e que não há condenação, se não houver) e quando há fonte só com link (não diga que viu ou leu, e abra antes de usar).

**Detalhes do `planejamento_mover_card`:**
- **Para Revisar:** o card precisa do hook e do estilo escolhidos pela pessoa e do pacote de hook pedido há pouco (`sofia_preparar_escrita` com `tipo: "hook"`). Mande `escolhidoPeloAluno: true` só depois da resposta dela. Escolha só do hook ou só do estilo fica salva e o card não anda.
- **Em Revisar sem roteiro:** o card anda e a resposta traz o pacote do roteiro.
- **Para Lapidar sem grifos:** o card não anda e a resposta traz o pacote da crítica.
- **Para Gravar:** os grifos precisam estar todos respondidos. O servidor monta a versão com os grifos aceitos. O card nunca é marcado como gravado sozinho.
- `soMover: true` só quando a pessoa disser "só mova".
- Quando a ação da coluna é da Sofia (escrever, grifar), faça e siga. Quando a escolha é da pessoa (hook, estilo, versão), pergunte.
- Avise a pessoa em uma linha quando mover.

**Detalhes do `planejamento_editar_card`:** em Brainstorming e Estruturar, a ferramenta recusa hook e estilo. Eles entram pelo `planejamento_mover_card`, com a escolha da pessoa.

**Detalhes do `planejamento_postado`:** sem resultado informado, o servidor compara as views com o normal do perfil. De 1,25 vez o normal para cima funcionou, abaixo de 0,8 vez não funcionou. Nunca invente número.

## 3. Cérebro do perfil

O cérebro guarda, por perfil, o que a Sofia aprende. As camadas incluem: `como-trabalhar`, `o-que-funcionou`, `o-que-nao-funcionou`, `temas`, `dores`, `bolhas`, `crencas`, `historias`, `vocabulario`, `achados`, `citacoes`, `ideias-guardadas`, `cards-guardados`, `roteiros`, `formatos`, `estruturas`, `estilos`, `produtos`.

| Ferramenta | O que faz | Quando |
|---|---|---|
| `cerebro_indice` | O que existe em cada camada | Antes de buscar |
| `cerebro_buscar` | Busca por `consulta`, nas `camadas` escolhidas, com `limite` | Ideias, pesquisa, antes de escrever |
| `cerebro_ler` | Lê um item inteiro | Item achado na busca |
| `cerebro_guardar` | Guarda algo que vale para os próximos vídeos | A pessoa conta algo duradouro e diz que pode guardar; avise em uma linha o que guardou |
| `cerebro_preferencia` | Guarda em `como-trabalhar` o que a pessoa elogiou (faça) ou reclamou (evite), com a frase dela e a data | Depois do elogio ou da bronca, quando ela disser que pode guardar. O OK vale para aquela anotação |
| `cerebro_esquecer` | Tira um item | Só a pedido |
| `cerebro_desfazer` | Desfaz a última mudança | Só a pedido |

**Detalhes do `cerebro_preferencia`:** vale só para este perfil. Se já houver regra contrária, nada é gravado e a resposta mostra a antiga: pergunte se a pessoa mudou de ideia e, se mudou, chame de novo com `substitui`.

## 4. Referências

Vídeos reais de outros criadores, guardados para copiar o mecanismo. Nome, caso, número e frase do autor ficam com ele.

| Ferramenta | O que faz |
|---|---|
| `referencia_salvar` | Guarda um vídeo com o formato, os números e até 20 comentários entre os mais curtidos, literais, com as curtidas, sem @ e sem nome de quem escreveu |
| `referencia_editar` | Corrige uma referência |
| `referencia_listar`, `referencia_buscar`, `referencia_ver` | Acha e lê referências |
| `referencia_usar` | Liga uma referência a um card, em um de três graus: literal, meio-termo ou criativo |
| `referencia_apagar` | Só a pedido |

Para pegar números e comentários, use o caminho que funcionar, nesta ordem: o link aberto, a transcrição pública, uma ferramenta de métricas que a própria pessoa ligou ou o que ela colar. Coletor pago só se ela já tiver um ligado: diga qual coletor, quantos itens e quanto deve custar, e espere o OK. Se ela usa o Claude no Chrome, ele pode abrir o vídeo no navegador dela, com o OK dela e só para ler. Nunca contorne login e nunca peça senha.

## 5. Perfis

| Ferramenta | O que faz |
|---|---|
| `perfil_listar` | Os perfis da pessoa (o dela e os de clientes) |
| `perfil_ver` | Números do perfil, o normal dele e os vídeos acima do normal |
| `perfil_salvar_avaliacao` | Salva a avaliação de um perfil, que vira a galáxia no site. A resposta oferece guardar os vencedores no cérebro e na biblioteca do perfil: com o sim da pessoa, use `cerebro_guardar` e `referencia_salvar` |
| `perfil_definir_alvo`, `perfil_desfazer_alvo` | Marca ou desmarca um perfil como alvo |
| `perfil_salvar_leitura` | Guarda a leitura de hoje de um perfil avaliado: seguidores e os vídeos recentes, com os números do dia. Uma por dia; ler de novo no mesmo dia substitui. Vai com `agendada: true` quando vem da tarefa agendada da pessoa |
| `perfil_ler_da_rede` | Lê os números de hoje direto do YouTube, do Instagram ou do TikTok, pela conexão que a pessoa fez em Meus dados, e guarda como a leitura do dia. Só lê a conta conectada com a mesma arroba do perfil. Sem a rede conectada, devolve o passo e o link para conectar, sem guardar nada |
| `perfil_evolucao` | A evolução semana a semana: vídeos por semana (a constância), seguidores, o normal do perfil, os vídeos acima do normal e o engajamento. Só leitura |

Com a rede conectada em Meus dados, o site lê o perfil sozinho toda segunda. Sem a rede conectada, a leitura semanal automática é uma tarefa agendada que a própria pessoa pede (veja "Evolução do perfil" na skill); sem ela, a leitura acontece quando a pessoa pedir.

Fale de resultado contra o normal do perfil: "2 vezes o normal do perfil", "perto do normal". Mande o link da página do site em vez de montar painel no chat, a não ser que a pessoa peça.

## 6. Curso

`onde_estou`, `ver_etapa`, `marcar_etapa`, `ver_situacao`, `buscar_no_curso`, `glossario`, `kit`, `escrever_abordagem`, `preparar_reuniao`, `preco_e_contrato`, `destravar`. Use quando a pergunta for sobre o curso (etapas, aulas, vendas, abordagem de clientes), sem um vídeo no meio.

## 7. O que pode mudar

Esta skill foi escrita para a versão do conector de novembro de 2026. Pontos que ainda podem mudar de nome ou de jeito:

- O faça e o evite em `como-trabalhar` podem ganhar ferramenta própria.
- Conversa por voz: pode haver um modo em que a pessoa fala em vez de digitar. As regras de escrita continuam as mesmas.
- Se uma ferramenta citada aqui não aparecer na lista do conector, use a de nome mais parecido e avise a pessoa em uma linha.
