# Estilos — a mesma gramática, sotaques diferentes

O plugin lê o take, decide o corte e escolhe as classes sempre do mesmo jeito. O
que muda de um estilo para outro é **como cada classe aparece**: a exposição, a
tipografia, a presença ou ausência do rosto, o acabamento.

Hoje há dois estilos medidos, e o guia escolhe um no cabeçalho (`estilo:`). O
padrão é `noturno`. O terceiro, `bento-ui`, não é de vídeo inteiro: é a marca
do dono para o plano de interface.

## O estilo desta casa é `noturno`, e não se pergunta

O dono do canal pediu, com estas palavras: *"a skill deveria sempre usar este
estilo pra mim"*, apontando para a conta de onde o `noturno` foi medido. Então
`estilo: noturno` é o padrão em todo guia deste canal — não é uma escolha a
oferecer a cada vídeo. Só troque se ele pedir a troca em voz alta, e nesse caso
escreva no `porque` do guia que a troca foi pedida.

**As referências estão em disco, e valem mais que esta descrição.** Antes de
escrever motion para este canal, abra o índice visual da classe que você vai
usar:

```
<pasta treinamento do config>/<corpus do noturno>/
  frames-por-categoria/_indices/     20 amostras por categoria, as 12 categorias
  frames-por-categoria/GUIA.md       o que cada categoria é e quando usar
```

As 12 categorias de lá são a origem da tabela de classes do `catalogo-visual.md`
— `01-motion3d-personagem` é o `personagem`, `08-broll-cotidiano` é o
`cotidiano`, `09-tela-dispositivo` é a `tela`, e assim por diante. Ver o frame
real evita exatamente o erro registrado no catálogo: inventar uma geometria
própria em vez de mostrar a coisa dita. Se o volume não estiver montado, diga
que não conferiu as referências em vez de escrever de memória.

---

## `noturno` — medido em 2.623 frames

O estilo do canal por padrão. O escuro é a regra e a claridade é o acontecimento.

- **Fundo** `#0B0B0E`, luminância 12/255, nunca preto absoluto. Ocupa 90% da tela.
- **Sujeito** em branco osso `#CCCAC8`; o 255 só aparece no halo, nunca no corpo.
- **Luz** sem frontal: key fria contornando por cima, rim âmbar `#FFB067` de um
  lado, rim ciano `#7FB4FF` do outro.
- **Figura humana** é o avatar branco sem rosto — sem olhos, sem boca, sem pele.
  O espectador ocupa aquele corpo.
- **Tipografia** condensada e pesada em caixa alta, `Anton`, entressilaba negativa,
  revelada por máscara de baixo para cima.
- **Acabamento obrigatório** em toda cena: meio-tom, grão de filme, vinheta escura,
  dupla sombra de contato.
- **Câmera nunca parada:** push-in contínuo de 2% a 4%.

Quando usar: ensaio, tese, tema pesado, narração em segunda pessoa. É o estilo em
que o rosto de quem fala é a exceção, não a régua.

---

## `demonstracao` — medido em 222 frames classificados

O oposto útil: aqui a claridade do quadro é informação. Tela clara quer dizer
produto e demonstração; quadro escuro quer dizer pessoa falando.

- **Rosto real, sempre.** Não há avatar anônimo. Ou o busto do criador falando,
  ou uma bolha de rosto sobre o render.
- **Tela e pessoa divididas:** metade superior é a captura de tela, metade
  inferior é o busto, com a legenda exatamente na linha de corte. Esse formato
  não existe no `noturno`.
- **Duas tipografias com função:** etiqueta colorida de fundo sólido para
  tela e demonstração; itálico serifado sem caixa para arquivo e b-roll. A
  tipografia sinaliza que tipo de imagem está no quadro.
- **Exposição de amplitude larga:** de luminância mediana 14 no estúdio escuro a
  121 nas telas quase brancas. Um grupo tem até vinheta invertida, com as bordas
  mais claras que o centro, como estúdio de produto.
- **Sem grão simulado.** O ruído que existe é de captura de tela, não textura
  aplicada.

Quando usar: demonstração de ferramenta, tutorial, review, qualquer vídeo em que
a tela precise ser lida e a sua reação importe tanto quanto o conteúdo dela.

---

## `bento-ui` — interface e fluxo, na marca do canal

Não é um estilo medido de terceiro: é a **marca do projeto**
(o `manual.md` da marca que `marca.py mostrar --projeto` indicar — cada canal ou
cliente tem a sua, fora do plugin), aplicada ao plano que mostra um **fluxo de
produto**, como clicar, gerar, montar e publicar. Nasceu no projeto 08, quando o
dono aceitou um único motion no meio do footage oficial desde que fosse
*"mais bonito, mais elegante, estilo bento uiux"*.

- **Tokens da marca, sem inventar:** papel creme `#F5EAD7`, cartão `#FFF8E9`,
  tinta `#211315`, vinho `#8F1837` (ação e estado), vinho profundo `#4E0B22`
  (sombra dura), rosa impresso `#E3B8A6` (apoio), amarelo editorial `#F0B95B`
  **só em progresso e ação**, verde `#2E6B46` só no "pronto".
- **Três dispositivos, e só eles:** cartão contornado (2–3 px de tinta, raio
  26–38 px), sombra dura deslocada (7 px rosa no cartão, 12 px vinho na moldura)
  e estado em vinho. **Sem gradiente, neon, vidro nem desfoque.**
- **Montserrat 800** nos rótulos (sobretítulo 14 px com tracking 1,7 px,
  título 25 px com −0,8 px). O texto é rótulo mais estado, nunca frase corrida.
- **Um fluxo só, persistente.** A moldura entra uma vez (0,36 s, `power3.out`)
  e o estado avança dentro dela: ação → roteiro → mídia → timeline → selo
  "PRONTO PARA POSTAR". Não é uma sucessão de cartelas.
- **Honesto sobre o que é:** ilustra o fluxo do criador, sem selo de recurso
  de um produto que não o tem (`tela-dividida.md`, fatos).

Quando usar: o trecho que descreve um processo de software dentro de um vídeo
cujo resto é rosto ou footage. Nunca como identidade de vídeo inteiro.

---

## Como escolher, e como misturar

Escolha pelo **verbo do vídeo**. Se o vídeo argumenta, `noturno`. Se o vídeo
mostra como se faz, `demonstracao`.

Misturar é legítimo em um caso só: um vídeo `noturno` que precisa provar algo na
tela pode pegar emprestado o split de `demonstracao` naquele momento, desde que o
fundo e o acabamento continuem os do `noturno`. O contrário — um vídeo de
demonstração que vira ensaio no meio — quase sempre significa que são dois vídeos.

**Footage fornecido não entra na grade de ninguém.** Na tela dividida com
vídeo oficial ou de referência (`tela-dividida.md`), o topo mantém a luz
capturada, e quem fala sai em SDR natural (`sdr.py`), sem aberração, grão nem
dessaturação. O estilo aparece só no que a edição desenha: hook, legenda e o
eventual plano de interface.

As medições completas de cada estilo ficam em `treinamento/<estilo>/`. As folhas de
contato que as originaram ficam na pasta de treinamento de quem treinou, fora do plugin. Um estilo novo entra por `aprender.py` mais o
agente `analista-de-estilo`, e vira mais uma opção aqui — nunca uma substituição.
