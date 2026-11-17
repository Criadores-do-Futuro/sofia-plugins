# Portões de qualidade

Veio da linha do bEditor mantida no Codex e foi reescrita para apontar os
scripts que existem aqui. Serve ao vídeo montado **e** a cada plano isolado.

**Reprovação em fato, direito, segurança ou integridade de arquivo é
bloqueante.** Não se compensa com média alta nos outros eixos.

## 1. Narrativa

- O gancho cria pergunta, tensão ou promessa nos primeiros segundos
  (`retencao.md`: Freeze Point).
- Cada inserção prova, explica, contrasta, antecipa, revela ou faz respirar.
  Movimento decorativo não conta.
- A progressão visual acompanha a do argumento.
- O clímax recebe mais contraste, escala ou silêncio; o final resolve o que a
  abertura abriu.

No formato `dinamismo` este eixo se concentra no hook e no corte, porque não há
motion para carregar progressão (`formatos.md`).

## 2. Montagem e áudio

- O corte tira erro e redundância **sem mutilar respiração natural**. Pausa que
  trabalha a favor fica, e o `porque` diz por quê.
- J-cut só onde a cauda de quem sai **não** mostra a boca de quem fala. Em vídeo
  de rosto na câmera não existe lugar para ele, e insistir produz dublagem fora
  de sincronia (`sincronia.md`).
- Mudança visual aterrissa em palavra, ação, número ou impacto escolhido.
- A voz continua inteligível no celular; cama e efeito não mascaram consoante.
  `medir.py` afere loudness e separação da cama.
- Sem clique, sem corte seco de ambiência, sem drift, sem descasamento labial
  introduzido pela montagem. **Este é bloqueante**, e a soma das durações bater
  não é prova dele: mede-se contra o bruto, trecho a trecho, e olhando os
  lábios num quadro do meio e num do fim (`sincronia.md`).
- **No arquivo final, não só na prévia.** O render final pode deslizar a imagem
  sozinho (grade de quadros, `sincronia.md`); a prévia aprovada não prova o
  master. Correlação de energia de movimento final × `aroll.mp4`: 0 quadro em
  todas as janelas válidas, ou não sobe.
- Zoom só em ênfase de voz medida e só desfeito num corte (`formatos.md`).

## 3. Continuidade visual

- Personagem, objeto, roupa, material, luz, paleta e direção de tela respeitam a
  `familia` e o `estado` do momento.
- Transição tem motivação: forma, cor, movimento ou sentido.
- Sem membro deformado, morphing acidental, flicker, nem detalhe que muda sem
  motivo.
- Overlay pertence ao espaço: perspectiva, sombra, oclusão, grão e motion blur
  coerentes com a placa.
- Em tela dividida, cabelo, olhos, boca e queixo de quem fala ficam inteiros em
  todas as amostras, e o matte, quando existe, não tem halo, flicker nem perda de
  cabelo (`tela-dividida.md`).

## 4. Design e legibilidade

- A hierarquia se entende em um quadro, em tela de celular.
- Hook no terço superior, com acentuação correta e nenhuma letra cortada;
  legenda logo abaixo da boca, fixa, fora da faixa da interface (`hook.md`,
  `formatos.md`).
- Texto essencial respeita as zonas seguras e fica tempo de ser lido — o mínimo
  de leitura de um gráfico é 2,5 s, e `validar.py` reprova abaixo disso.
- Tipografia, espessura, tracking, caixa e animação seguem o estilo declarado
  (`estilos.md`), não o gosto do dia.
- **Número, data, nome, rótulo e gráfico vêm do fato confirmado**, nunca de
  pixel gerado — é a regra de `rotas-de-geracao.md`, e `validar.py` recusa uma
  `ideia` de imagem que peça texto legível.

## 5. Fatos, origem e segurança

- Toda afirmação verificável tem fonte e estado (`precisaDeFato` → `fatos.json`).
  Número sem fonte não entra: fica pendente do autor, e o plano sai sem ele.
- Arquivo histórico e mídia sintética não são apresentados um como o outro.
- Direito, consentimento, transformação, provedor e origem registrados
  (`procedencia.md`).
- Nenhuma chave, dado pessoal, notificação ou identificador em mídia, log ou
  manifesto.
- Custo de geração dentro do teto combinado.

## 6. A inspeção, na ordem

Automático primeiro, olho depois — nessa ordem, porque olho cansa e script não:

1. `validar.py` até zero erros; `medir.py` no preview, e **preview reprovado não
   se mostra como pronto**.
2. Renderize os quadros do gancho, do primeiro gráfico, da virada de estilo, do
   clímax e do final.
3. **Olhe os quadros.** Depois assista ao vídeo inteiro, em velocidade normal,
   com áudio.
4. Assista **sem áudio** — testa se a imagem se explica. Depois **só o áudio** —
   testa se a montagem continua fazendo sentido de ouvido.
5. Teste a versão comprimida, no tamanho em que ela vai ser vista.

O passo 3 é o que mais se pula e o que mais pega defeito. Uma legenda virando
cortina preta sobre 120 s de vídeo passou por dois scripts e só morreu quando
alguém olhou o quadro.

## A nota

Dê 0 a 4 por eixo. Exija **3** em narrativa, montagem, continuidade e design.
Exija **4** em fato, direito, segurança e integridade — esses não têm meio-termo.

Registre a reprovação por id de momento e **regenere só o que reprovou**. Refazer
o vídeo inteiro por causa de um plano é como o tempo some.
