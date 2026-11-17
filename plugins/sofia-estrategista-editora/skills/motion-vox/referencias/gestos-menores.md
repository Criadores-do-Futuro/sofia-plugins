# Os gestos menores

O que faz a Vox parecer Vox não são os planos complexos — são quatro gestos pequenos,
repetidos, que dão caráter ao que de outro modo seria um gráfico de template. Nenhum
deles custa render. Todos são procedurais.

Estão aqui porque o kit já sabia compor a cena e já sabia sair dela, mas não tinha o
vocabulário do **intervalo**: o que acontece enquanto um elemento simples aparece,
enquanto uma imagem fica parada, e na borda do quadro.

Origem: a decupagem de Lewis McGregor (PremiumBeat, 2021) sobre o canal da Vox. As
receitas dele são de After Effects; o que está abaixo é a tradução para camada em PIL,
que é como este kit desenha.

---

## 1. Cadência de 12fps para gráfico simples

Um rótulo, um número, uma legenda de apoio que entra de `scale 0`. Animado a 24fps fica
liso e sem personalidade — lê como template de editor. A Vox anima esses elementos a
**12fps** e insere num corte de 24.

Aqui, a timeline é 24fps por construção, então não se troca a cadência do projeto: o
elemento **segura o próprio valor por dois frames**.

```python
def em_doze(frame, t0):
    """Congela o progresso em passos de 2 frames — 'on twos' de posição."""
    return t0 + ((frame - t0) // 2) * 2
```

Isso é primo do `boil`, e a distinção importa:

| | O que trava | Efeito |
| --- | --- | --- |
| `boil` | a **forma** (remap, semente a cada 9fps) | redesenhado à mão |
| `em_doze` | a **posição/escala** (valor a cada 2 frames) | stop motion |

**Não aplique aos dois ao mesmo tempo no mesmo elemento.** Forma saltando junto com
posição lê como falha de render, não como escolha. Regra: objeto fotografado leva
`boil`; rótulo e tipografia de apoio levam `em_doze`.

**A legenda queimada nunca leva `em_doze`.** Mesmo motivo do boil (`legenda.md`): é
acessibilidade, e travar a entrada atrasa a palavra em relação à fala.

---

## 2. Revelação mordida

A entrada de faixa e rótulo da Vox não é um wipe limpo — a máscara abre **em pedaços
irregulares, pulando frames**, como se o papel estivesse sendo comido ao contrário. É o
mesmo princípio do 12fps: aspereza deliberada no lugar de suavidade.

Receita:

1. A máscara da faixa avança em **passos desiguais**: por exemplo `0 → 18% → 22% → 55%
   → 61% → 100%`, não em progresso linear.
2. Entre dois passos, **segure** 1–3 frames. É a pausa que faz ler como mordida.
3. A borda do passo não é reta: use a mesma borda rasgada do papel, deslocada por
   ruído — borda reta devolve o wipe de template que se queria evitar.
4. **O texto entra depois da faixa**, com 3–5 frames de atraso, e com a própria
   sequência de passos. Entrar junto faz os dois lerem como um bloco só.

O atraso do texto é o detalhe que mais paga. Sem ele a faixa parece um retângulo
animado; com ele parece papel sendo posto e depois escrito.

---

## 3. Fundo em movimento

O problema: uma fotografia ou um recorte precisa ficar **15 segundos** no ar enquanto a
fala explica. Parado sobre cor chapada, morre. Mas nada na cena pode se mexer o
bastante para disputar atenção com o que está sendo dito.

A solução da Vox não é animar o elemento — é **animar o fundo atrás dele**, com
textura que troca rápido demais para ser seguida e devagar demais para distrair.

- 5 ou 6 texturas de papel diferentes, alternadas em ordem, **2 a 3 trocas por segundo**.
- Tendo só uma textura, espelhe e gire: o padrão lê como diferente.
- O elemento em cima **não se mexe**. Quem vive é o fundo.

Isso resolve o caso que a regra de densidade (`SKILL.md`, 30–40% de cobertura) deixa em
aberto: o plano longo em que não há o que ilustrar, mas há o que sustentar.

**Armadilha de bitrate.** Textura trocando 3x por segundo em quadro cheio é conteúdo
novo a cada 8 frames, e o encoder paga caro. Mantenha a troca **restrita à área do
fundo** — nunca sobre o vídeo ao vivo — e prefira 2 trocas/s quando a cena passar de 8
segundos. É a mesma economia que o grão já respeita em `render.py` ("on twos", campo
borrado).

---

## 4. Borda de lente

Elemento 2D — recorte de jornal, print de rede social, ficha — sobre fundo claro tem
uma planura que denuncia a montagem. A Vox devolve a ele **características de lente
real**: aberração cromática e desfoque **só nas bordas**, com o centro limpo.

O ponto inteiro está no "só nas bordas". Aplicar ao quadro todo é erro visível — e é a
mesma lógica pela qual o fundo não leva boil (`boil.md`): efeito de lente é do **olho
que olha**, não do objeto olhado.

Receita:

1. Separe os canais R e B por **1 a 2 px** em sentidos opostos (rotação mínima). Acima
   disso vira glitch, que a Style Bible §13 proíbe.
2. Desfoque gaussiano de **σ ≈ 3,5** na mesma camada de ajuste.
3. Máscara **circular central subtraída**, com esfumado (`feather`) de ~50 px: o centro
   fica intacto, o efeito só sobrevive no anel externo.

Use com parcimônia — em cena de elemento único que segura alguns segundos, que é
exatamente onde a planura aparece. Ligado o tempo todo, deixa de ser lente e vira filtro.

---

## Como isso entra na ordem de execução

Nenhum destes gestos é etapa nova. Todos moram na **etapa 5 (compor)**:

| Gesto | Onde decidir | Onde aplicar |
| --- | --- | --- |
| cadência 12fps | ao escrever o evento no blueprint | `build_M#`, na curva de entrada |
| revelação mordida | ao escolher o registro (`registros.md`) | máscara da faixa |
| fundo em movimento | quando o plano passar de ~8s sem evento | camada de fundo |
| borda de lente | cena de elemento único | camada de ajuste, por último |

A regra-mãe continua valendo acima de todos: **movimento acompanha raciocínio**. Um
gesto menor que não está ancorado numa palavra (`SKILL.md`, ±3 frames) é enfeite — e
enfeite é justamente o que estes quatro existem para evitar.

---

## O vox tem duas pontas

O mesmo estilo é desenhado por dois motores neste plugin, e os quatro gestos valem
para os dois — o que muda é como se escreve cada um:

| | motor | onde | os gestos aqui |
| --- | --- | --- | --- |
| **este kit** | camadas em PIL, frame a frame | `skills/motion-vox/lib/` | `em_doze()`, máscara em passos, troca de textura, camada de ajuste |
| **bEditor** | HTML/CSS com GSAP, via HyperFrames | `skills/beditor/scripts/hf_vox.py` | `passos()`, `mordida()`, `_base_js()`, `verniz()` |

A descrição para gente ler, do lado do bEditor, está em
`skills/beditor/referencias/galeria-estilos.md`. **Quem mudar um gesto de um lado
confere no outro** — foi para isso que os dois arquivos se citam.

Uma divergência conhecida, ainda não resolvida: o papel deste kit é `#D9D8D1` e o do
`estilos.MOTION["vox"]` é `#E7E0D2`. São a mesma ideia de papel creme medida em
referências diferentes. Unificar é decisão de direção de arte, não de código — até lá,
cada motor usa o seu, e nenhum dos dois está errado por engano.
