# Prompts por classe

Prompts em inglês — todo gerador responde melhor. O bloco de grade no fim é
**obrigatório** em toda geração do preset `noturno`: é ele que faz o asset pertencer.

## O bloco de grade (cole no fim de todo prompt)

```
Vertical 9:16, 1080x1920. Pure black background at luminance 12/255, never lifted to
grey. Subject reads as bone white #CCCAC8, never blown out to pure white. Rim light
only from behind and above: warm #FFB067 on one side, cool #7FB4FF on the other, no
frontal light. Chromatic aberration separating edges into orange and cyan, fine film
grain over the entire frame including the blacks, heavy dark vignette in the corners,
large soft bloom halo. Cinematic, contemplative, lonely.
```

## `personagem`

```
A featureless smooth white humanoid figure, no face, no eyes, no mouth, no skin
texture, matte diffuse white surface. [AÇÃO: seated at the edge of a desk, head lowered
/ walking away down a corridor / reaching for something just out of frame]. Shallow
depth of field, 40mm lens, low camera angle looking slightly up at the figure.
+ bloco de grade
```

Negativos: `do not add eyes, do not add mouth, do not add skin texture, no facial
features, no text, no watermark`.

Consistência entre planos é o ponto fraco desta classe. Se o personagem aparece em mais
de dois planos, **modele uma vez no Blender** (Y Bot do Mixamo) e renderize os ângulos —
sai mais barato que brigar com o gerador.

## `objeto`

```
A single [OBJETO] isolated in the centre of the frame, floating in pure darkness,
studio product lighting from behind and above, matte material, no text anywhere on the
object. 85mm lens, shallow depth of field.
+ bloco de grade
```

Funciona muito bem com recorte fotográfico também: um still real recortado e colocado
sobre o preto com a mesma grade fica indistinguível de render, por uma fração do custo.

## `broll` (vídeo generativo)

Descreva **movimento de câmera + lente + luz + duração**, não só o assunto:

```
Slow push-in, 35mm, handheld micro-movement. [CENA]. Practical light sources only,
deep shadows, the lower third falls into darkness. 5 seconds.
+ bloco de grade
```

Peça 4–6 s por clipe; você usará 1,5–3 s. Gerar curto demais tira sua margem de corte.

## Variante 2026 (recorte + halftone)

```
Cut-out photographic subject on pure black, amber glow #FFA33A rimming the silhouette,
thin white line grid overlay, halftone dot texture on top, high contrast, editorial
collage feel. Vertical 9:16.
```

Esta variante é inteiramente reproduzível em CSS/Remotion sobre uma foto recortada —
não precisa de geração se você já tem a foto.

## O que nunca pedir a um gerador de imagem

```
❌ texto legível, título, palavra escrita na imagem
❌ gráfico, rótulo de eixo, porcentagem, número
❌ interface de app, botão com label, tela de celular com conteúdo
❌ o rosto de uma pessoa real
❌ recriação de uma obra específica existente
```

Estilo de uma época (barroco, ukiyo-e, academismo) é legítimo. **Recriar uma obra
específica ou o estilo de um artista vivo, não.**
