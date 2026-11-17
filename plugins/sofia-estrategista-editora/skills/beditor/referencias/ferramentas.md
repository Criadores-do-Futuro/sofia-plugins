# Qual ferramenta para qual plano

> **Texto, número e interface são desenhados em código. Matéria, luz e corpo são
> gerados ou filmados. Obra e arquivo são licenciados.**

## A tabela de rota

| `tipo` | Rota primária | Alternativa | Por quê |
| --- | --- | --- | --- |
| `cartela` | Remotion / HTML+CSS | — | única rota com texto legível e editável |
| `dado` | Remotion + Chart.js/D3 | — | o número precisa ser verdadeiro |
| `tela` | HTML → corner pin | Figma → PNG | texto de UI tem que ser desenhado |
| `objeto` | Gemini (nano banana) → upscale → parallax 2.5D | Blender | matéria e luz, sem texto |
| `personagem` | Blender + Mixamo | Gemini + upscale | consistência entre planos |
| `broll` | Veo / Kling / Runway | acervo licenciado | movimento real de câmera |
| `hibrido` | Blender shadow catcher sobre placa | AE | precisa de sombra que crava |
| `tvcrt` | animação livre + CRT em pós | ffmpeg | o CRT é pós, nunca prompt |
| `arquivo` | acervo público | — | licença item a item |
| `obra` | acervo de museu | — | direito da obra E da foto |
| `cotidiano` | celular, luz de janela | — | IA não faz mão em ação nem água corrente |
| `pessoa` | câmera + lapela | — | semelhança de pessoa real não se gera |

## Acesso disponível nesta máquina

```
ffmpeg 8.x         grade, mux, sequência → MP4, CRT, grão            instalado
node 26 / bun      Remotion, Playwright, Puppeteer                   instalado
python3 3.12       plano.py, assets.py, motion-vox (PIL)             instalado
Blender MCP        modelagem, Cycles, compositor — via ferramenta    conectado
Claude artifacts   protótipo visual em HTML antes de virar Remotion  disponível
hyperframes        render hospedado a partir de HTML/Remotion        skill instalada
notebooklm-py      infográfico e deck a partir do roteiro            requer login
Gemini API         geração de imagem                                 requer GEMINI_API_KEY
```

Sem `GEMINI_API_KEY` o `assets.py` escreve `PROMPTS.md` e o trabalho continua — os
prompts colam em qualquer gerador.

## O que a IA generativa não resolve

Cada item é um achado independente, não uma precaução genérica:

- **Texto legível** — erra glifo e acento, e o resultado não é editável nem reproduzível.
- **Número verdadeiro** — rótulo alucinado, barra fora de proporção.
- **O mesmo personagem entre gerações** — e upscale com criatividade alta inventa feições
  num rosto que deveria ser liso.
- **Mão em ação e água corrente** — exatamente o conteúdo de `cotidiano`.
- **Texto de interface** — a UI tem que ser desenhada.
- **Voz a 10 metros** — limite físico, nenhuma restauração recupera.
- **Semelhança de pessoa real** — não é rota, é problema.

## A técnica que mais rende

**Gerar a chapa com IA, animar com código.** Uma imagem estática boa custa segundos;
vídeo generativo custa minutos, sai com enquadramento incerto e clipe curto demais.

O caminho:

1. Gere a imagem em 1080×1920 com o prompt da classe (`prompts-assets.md`).
2. Faça upscale se for aparecer grande.
3. Separe em 2–3 camadas (assunto / meio / fundo) — recorte por prompt ou por máscara.
4. Anime as camadas em velocidades diferentes no Remotion: 100% / 70% / 40%.
5. Aplique a grade por cima de tudo.

Isso é parallax 2.5D. Dá profundidade real a uma imagem parada, roda em segundos,
custa uma chamada e o enquadramento é exatamente o que você pediu. É a razão de o
template do bEditor ter um componente `Parallax` pronto.

## Custo, na ordem

```
código puro       ~0            cartela, dado, tela
imagem IA         centavos      objeto, personagem
upscale           centavos      quando o asset aparece grande
vídeo IA          caro          só quando o movimento é o assunto
acervo            tempo         curadoria e licença
filmar            seu tempo     e ainda assim é o melhor resultado em cotidiano
```
