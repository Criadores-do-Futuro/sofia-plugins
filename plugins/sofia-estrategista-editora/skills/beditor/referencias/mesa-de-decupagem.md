# A mesa é uma só — nunca se publica uma mesa nova

Cada pessoa tem **a sua** mesa — artifact só é atualizado pela conta dona. O
endereço mora no config desta máquina:

```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/setup.py --artefato mesa
```

- **Imprimiu um endereço:** é a mesa. Leia, edite em cima do que voltou, republique nele.
- **Imprimiu vazio:** esta conta ainda não tem mesa. Publique **uma vez** a partir do
  modelo `painel/mesa.html` e grave o endereço que voltou:
  `setup.py --artefato mesa=<url>`. Dali em diante, vale a regra abaixo.

Instrução do dono em 2026-09-13:

> "Quero que ao editar, e levar para o artifact, nunca recrie um artifact novo, tem que
> sempre usar o artifact completo que nós fizemos com todas as ferramentas que botamos de
> edição."

## A regra

Qualquer vez que uma etapa de edição for para a tela — decupagem, cor, hook, motion,
provas de uma `analise`, o que for — ela entra **nesta** mesa, republicada **neste** URL.

**Nunca:**

- publicar um artifact novo para "mostrar o corte deste vídeo";
- publicar um artifact novo porque a etapa é outra;
- publicar um artifact novo porque o formato é outro (`dinamismo`, `analise`, …);
- publicar um artifact novo porque foi mais rápido do que ler o que já está lá.

Cada mesa nova joga fora tudo o que foi construído: a roda de precisão, a lâmina com
ripple, o juntar, o remover silêncios com guarda, o apagar espaços vazios, o J-cut
automático com a trava do rosto em quadro, o recolar, o ímã, o desfazer de 40 passos, os
dez deslizantes de cor com a linha de ffmpeg de verdade ao lado, o seletor de hook, a
lista do que o áudio conta e os atalhos de teclado. Isso não se reconstrói de memória, e
o que reaparece vem pior.

## O procedimento, toda vez

1. **Ler antes de escrever.** `Artifact action:"read" url:"<o URL acima>"` — a versão
   viva volta como HTML completo, salvo em arquivo. **Construa a atualização em cima
   desse arquivo**, nunca de um rascunho local antigo: publicar numa mesa que esta
   conversa não leu é recusado, e com razão.
2. **Editar o arquivo lido** com `Edit`, acrescentando o que falta sem remover
   ferramenta nenhuma.
3. **Republicar no mesmo URL:** `Artifact file_path:"<arquivo>" url:"<o URL acima>"`.
   Sem `favicon` e sem `icon` — a mesa já tem os dela (✂️), e trocá-los faz o editor
   achar que é outra página.
4. **Arquivos de apoio.** A mesa tem 19 arquivos publicados (`dados.json`,
   `corte-revisao.mp4`, os quadros de comparação de cor, …). Passe em `files` só o que
   mudou: o que não for citado **continua publicado**. Mapear um caminho para `null` é a
   única forma de remover, e remover só se o dono pedir.
5. **Um projeto por vez.** O que muda entre vídeos é o `dados.json`, não o HTML. Trocar
   de projeto é republicar os dados — a mesa é a mesma ferramenta para todos.

## O que já está dentro dela

Para não reconstruir por engano o que existe:

| Painel | Tem |
| --- | --- |
| **Prévia viva** | a edição como dados, sem render (`painel/previa.py`): o take cortado em 360p (≤14,5 MB, cache pelo estado das fontes), zoom e recorte do rosto de cada faixa do `montador.faixas()` aplicados como `transform`, e a legenda+hook como a própria página do `legenda_hf` com `seek()` — o que se aprova é o que vai ao ar. Lista das ênfases, liga/desliga legenda e zoom. Sem `dados.json` de decupagem, a mesa mostra só este painel |
| **Roteiro** | momento a momento com decisão, motivo, pedaços, selo de J-cut, formulário de motion embutido, clique na frase para ir ao tempo |
| **Preview** | vídeo 9:16 com o selo do hook sobreposto, transporte e relógio |
| **O que o áudio conta** | as falas que o Whisper apagou (gagueira, frase recomeçada), achadas por energia |
| **Linha do tempo** | duas pistas com pedaços próprios, régua arrastável, agulha com cabeça de pegar, forma de onda, faixa de motion |
| **Roda de precisão** | a meia-lua do Final Cut do iPad, com passo de quadro / meio segundo / segundo |
| **Ferramentas** | lâmina, apagar com ripple, juntar, juntar a trilha, apagar espaços vazios, remover silêncios com guarda, J-cut automático (com a trava de rosto em quadro), recolar áudio, ímã, desfazer |
| **Atalhos** | B, ⌫, J, R, T, V, ⌘Z, espaço, setas com ⇧ e ⌥ |
| **Cor** | dez deslizantes do `cor.py`, presets, dois quadros de render real lado a lado, a linha de ffmpeg gerada, e a caixa de guardar como preferência do canal |
| **Hook** | opções com miniatura e campo para escrever outro |
| **Análise** (só formato `analise`) | cartões de prova com modo 1/2/3, espinha em %, destaques e buracos |
| **Máscara Dividir** | opcional, desligada de fábrica: liga, onde (meu vídeo / tela dividida), linha, Suavizar (30%), lado que fica, preview por cima do vídeo; salva `mascara` e o `aplicar_decisoes.py` leva ao guia (`tela-dividida.md`) |
| **Barra** | salvar decisões, com estado do que mudou |

Ferramenta nova entra **ao lado** destas. Se alguma precisar sair, é decisão do dono na
conversa, não limpeza por conta própria.

## Aprovar sem renderizar

Pedido do dono em 2026-09-27: editar não pode custar 30–40 minutos por rodada.
Para aprovação:

```
python3 scripts/montar.py --etapa previa --guia … --take … --falas … --projeto <projeto>/guia --edicao <projeto>/edicao
```

Ele monta o corte, a voz e o `public/` (cada um com cache) e para antes de
qualquer render, chamando `painel/previa.py`. Se o `public/` já existe e só o
hook/estilo mudou, basta `python3 painel/previa.py <projeto>/guia --nota "…"`.

e republicar a mesa com os `files` que ele imprime (`previa/edicao.json`,
`previa/legenda.html` e, só quando refeito, `previa/take.mp4`). Mudou zoom,
legenda ou hook: roda de novo em segundos, o take não sobe outra vez. O render
final (`--etapa final`) só depois do "aprovado".
