---
description: Etapa 1 — decupagem. Entrega o corte para o editor revisar antes de qualquer motion.
allowed-tools: Read, Write, Edit, Bash, Glob
---

Argumentos: `$ARGUMENTS` = caminho do take bruto. Pré-requisito: `guia/guia.json` validado
(vem de `/sofia-estrategista-editora:dirigir`).

Esta etapa entrega **só o corte**: sem motion, sem música, sem legenda. O editor julga
uma coisa de cada vez.

1. `python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/montar.py --etapa corte --guia guia/guia.json --take <take> --falas <take>.whisper.json --projeto edicao/motion --edicao edicao`
2. Entregue `edicao/corte-revisao.mp4` (324×576, leve) e mostre a tabela de
   `edicao/corte.md`: trechos que ficam, o que saiu com o porquê, e os J-cuts.
3. **Mesa de decupagem.** A página **já existe pronta no plugin**, em
   `painel/mesa.html`: copie-a para `edicao/mesa/mesa.html` e publique com os
   arquivos do projeto ao lado (`dados.json`, `corte-revisao.mp4`, `tiras.jpg`,
   `cor/`, `hook/`). **Não desenhe uma página nova.** A mesa e o painel são a
   mesma identidade — papel creme com ponto, painéis de borda grossa e sombra
   dura, Bangers no display —, e é isso que faz o plugin ter uma cara só; uma
   página avulsa, por mais bonita, quebra a experiência e joga fora as
   funcionalidades que já estão construídas.

   A mesa é uma ilha de edição, não
   uma lista: roteiro à esquerda, preview à direita, timeline embaixo. Duas
   pistas, **vídeo e áudio cortados em pedaços próprios**: miniaturas do take na
   de cima, a forma de onda decodificada do próprio take na de baixo. O editor
   corta na agulha (só o clipe selecionado, ou vídeo e áudio de uma vez),
   apaga com ripple, arrasta o áudio para montar o J-cut, e um ímã desligável
   encaixa a borda do áudio na borda do vídeo dono. Publique com
   `capabilities: {db: {}}`.
   Quando o editor disser que terminou, leia o documento
   (`Artifact action:"read_db"`, coleção `decisoes`, id do projeto), salve em
   `edicao/decisoes.json` e aplique:
   `python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/aplicar_decisoes.py --guia guia/guia.json --decisoes edicao/decisoes.json --contato guia/contato.json`
   Na coluna da esquerda, **o motion de cada momento vem junto da frase que ele
   ilustra**, não numa lista à parte: a ideia sugerida pelo diretor aparece sob o
   texto e abre num formulário — tipo, ideia, movimento, entrada, saída, quanto
   entra antes da fala, família e estado. Dá para **editar**, **remover** (o trecho
   volta a ser só rosto) e **adicionar** motion onde não havia. Cada tipo pede o
   dado que o validador vai cobrar: `cartela` pede o texto, `palavras`/`camadas`/
   `indice` pedem as palavras, `tela` pede o modo. `dado` fica com o enriquecedor,
   porque número precisa de fonte.

   **A mesa também julga a cor e o hook**, porque é onde o editor já está com o
   material na frente. A aba **Cor** traz os dez números de `cor.py` em
   deslizantes, com o preview aplicando a grade ao vivo (aproximação em CSS) e,
   ao lado, dois quadros **renderizados pelo ffmpeg** — nunca peça a aprovação
   pela aproximação. Uma marca diz se aquela grade vira preferência do canal
   (`~/.beditor/cor.json`) ou fica só neste vídeo (`guia.cor`). A aba **Hook**
   mostra o texto do gancho composto sobre o primeiro quadro real, nas regras do
   `motion.md` da marca do projeto (`marca.py mostrar --projeto`). No documento salvo isso chega em `cor`,
   `corPreferenciaDoCanal` e `hook`.

   **🤫 Remover silêncios** (tecla `R`) acha as pausas na onda do próprio take,
   dentro de cada trecho, e tira as que passam do mínimo em ms — deixando o respiro
   escolhido ao lado em cada ponta. Trecho que era pausa inteira sai do corte; o que
   tinha pausa no meio vira dois ou mais pedaços (`M03·a`, `M03·b`). **Arrastar a
   borda de um clipe de vídeo** apara para dentro e devolve material para fora, até
   onde o momento vai e sem invadir o pedaço vizinho: é assim que se corrige um
   respiro curto demais. O áudio alinhado acompanha a borda.

   **A agulha na mão.** Três lugares levam a agulha, com o mesmo gesto: a régua
   em cima da timeline, a **cabeça da própria agulha** (o triângulo laranja, com
   área de pegar maior que o desenho) e o corpo das pistas. A roda de precisão
   continua sendo para o quadro exato; o arraste é para atravessar o take
   depressa. Quem estava tocando pausa no primeiro toque — o preview segue a
   mão, não briga com ela. Na trilha junta o arraste anda no tempo do arquivo e
   volta para o bruto ao soltar, porque o dado guardado é sempre do bruto.

   **⇥ Juntar a trilha** (tecla `T`) troca o relógio do desenho. A peça guarda
   sempre o tempo do **bruto** — é de lá que o montador tira o material —, mas ler
   o corte nesse relógio obriga o olho a pular os buracos que apagar deixou. Com a
   trilha junta, os pedaços vivos ficam **ombro a ombro, como saem no arquivo**:
   régua, onda, tira de quadros e faixa de motion fecham o buraco junto, e a roda
   de precisão passa a andar no tempo do arquivo, pulando o que foi apagado em vez
   de atravessá-lo. O áudio acompanha porque a posição dele é a do vídeo dono
   menos o J-cut — **a sincronia é por construção, não por ajuste**. Nada no
   documento salvo muda: é só o desenho. Quem está fora some da vista nesse modo;
   para devolver um pedaço, use **devolver** no roteiro.

   **␣ Apagar espaços vazios** (tecla `V`) tira o ar sem fala, que tem duas
   formas: o pedaço sem palavra nenhuma dentro (sai do corte) e a cabeça ou a
   cauda de um pedaço — o que sobra antes da primeira palavra e depois da última
   (aparado). É o que fica para trás quando se apara à mão e quando um momento foi
   partido. Não confundir com 🤫 remover silêncios, que trata da pausa **entre**
   duas palavras, no meio do pedaço. A guarda de `ritmo.md` fica de pé nas duas
   pontas; sem ela o corte come a consoante que abre e a que fecha.

   O botão **⤵ J-cut automático** (tecla `J`) lê a onda já extraída, mede o silêncio
   no fim do áudio que sai e no começo do que entra, e adianta o áudio de cada corte
   até o alvo em ms escolhido ao lado — **nunca além da pausa de quem sai**, para não
   pôr duas falas uma em cima da outra. Clipe cujo áudio já foi movido à mão ele não
   toca; `🔗 Recolar áudio` desfaz tudo.

   O documento traz quatro mapas, e o script aplica os quatro — mais a cor e o
   hook, que não são de momento nenhum: `cor` vai para `~/.beditor/cor.json`
   quando a marca diz que vale para o canal, senão para `guia.cor`; `hook` vira
   `guia.hook`, desenhado depois junto da legenda:
   - `escolhas` — `fica`/`sai` por momento. Devolve o motion guardado quando um
     corte é desfeito.
   - `jcuts` — quanto o áudio entra antes da imagem; vira `audioAntesMs` no
     momento, conferido contra a pausa da frase pelo `validar.py`.
   - `cortes` — os pedaços que ficam dentro de um momento; o momento é aparado e
     a sobra vira um momento `cortar` ao lado, para o take continuar coberto de
     ponta a ponta. Momento partido em vários pedaços (é o que tirar as pausas do
     meio faz) vira uma sequência: o primeiro pedaço guarda o momento **com o
     motion**, cada pausa vira um `cortar` (`M03p1`), e cada pedaço seguinte vira
     um `aroll` que continua a fala (`M03-2`). O motion não se repete nos pedaços
     — mesmo gráfico entrando duas vezes o validador recusaria de qualquer jeito.
   - `motions` — o motion editado, criado ou removido na mesa. Só vem o que mudou;
     `null` remove. Momento em `aroll` que ganha motion vira `aroll+motion`; motion
     escrito num momento cortado fica guardado em `_motion` até ele voltar. O que a
     mesa não edita (`camera`, a ficha do enriquecedor) permanece.

   **J-cut — leia antes de oferecer o botão.** O J-cut só existe onde a cauda de
   quem sai **não** mostra a boca de quem fala. Em take de rosto na câmera — que é
   todo `dinamismo` — não há esse lugar, e o `montar.py` zera o `audioAntesMs`
   sozinho. Se ainda assim um J-cut chegar ao montador, ele **para o pipeline**:
   a implementação atual desloca o segmento inteiro em vez de sobrepor as duas
   pistas, e isso põe a voz à frente da boca pelo trecho todo. Três masters saíram
   assim antes de alguém olhar. `referencias/sincronia.md` tem a regra e o teste.

   Sem J-cut, a voz sai do próprio A-roll: cortada junto com a imagem, em
   sincronia por construção.
4. Ouça também os ajustes ditos em conversa e execute-os **no guia**, nunca no vídeo:
   - "mantém o M25" → `decisao` de M25 vira `aroll` (ou `motion`, se houver ideia).
   - "corta também de 2:31 a 2:35" → o momento daquele intervalo vira `cortar`, com
     `porque` escrito.
   - "o gráfico entra tarde no M24" → ajusta `entraAntesMs`, sempre ≤ `pausaAntesMs` da
     frase (o `validar.py` reprova se passar).
   Depois de cada ajuste: `validar.py` até zero erros e rode a etapa de novo.
5. Quando o editor aprovar, registre: `mkdir -p edicao/aprovado && touch edicao/aprovado/corte`.
   Só então siga para `/sofia-estrategista-editora:motion-graficos`.

Sempre com vigia: processo sem progresso por 4 min é morto e investigado, nunca esperado.
