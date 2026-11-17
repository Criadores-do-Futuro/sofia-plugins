# A biblioteca de mídia — o que há, como se mede, como se escolhe

A biblioteca é da MÁQUINA, não do projeto: quatro pastas apontadas em
`~/.config/beditor/config.json` (`/sofia-estrategista-editora:setup` escreve; `oficina.pasta("musicas")`
lê). Nesta máquina ela mora em `bEditor/Biblioteca/` no SSD. Cada pasta carrega o
próprio `catalogo.json`, escrito por `scripts/biblioteca.py catalogar`.

> **Antes de qualquer coisa: LICENÇA.** As músicas são versões instrumentais e
> karaokê de obras comerciais (Adele, Queen, Beyoncé, Legião, Djavan…), a maioria
> baixada do YouTube — 143 das 185 têm «(youtube)» no nome. Não existe licença
> conhecida para nenhuma delas e o Content ID ao publicar é risco real, com
> reivindicação de receita ou remoção. O catálogo registra isso **por faixa**
> (`origem`, `licenca: "desconhecida"`, `risco: "content-id"`) e `cama` repete o
> aviso a cada chamada. A skill não apaga, não esconde e não decide: mostra, e a
> decisão de usar é do dono. Toda faixa que entrar num vídeo vai para o
> `provas.json` com `tipo: "trilha"`, título, autor e origem — cama sem procedência
> é a mesma dívida que prova sem procedência (`formato-analise.md`, «Som»).

## O que existe em cada pasta

| Pasta | Conteúdo | Catálogo mede |
| --- | --- | --- |
| `Musicas/<CLIMA>/` | 8 climas (DETERMINAÇÃO FORÇA, TENSÃO SUSPENSE, INSPIRAÇÃO SUPERAÇÃO, EMPODERAMENTO CONFIANÇA, FELICIDADE ALEGRIA, ROMANCE AFETO, NOSTALGIA SAUDADE, MELANCOLIA REFLEXÃO), ~185 mp3 nomeados `NN Clima_Sub Artista - Título (Instrumental) - uploader (youtube)`; mais `AVULSAS/` | `dur`, `sr`, `canais`, `lufs`, `lra`, **`eventosMin`**, e do nome: `numero`, `clima` (da pasta), `artista`, `titulo`, `versao`, `canal`, `origem`, `licenca`, `risco`, `vocal` |
| `SFX/` | 14 mp3 (Click, Contagem, DInheiro, Digitando, Gears, Hit, Mensagem Iphone, Relógio, Riser, Teclado iPhone, Woosh, Woosh Deep/Fast/Slow) e os mesmos em `video/*.mp4` | áudio como as músicas; vídeo como os overlays |
| `Overlays/` | `Overlay 1–8, 10.mp4`, um `freepik_…mp4` (1080×1920, 30 fps, `yuv420p`) e `referencias/*.webp` (amostras de estilo, não são overlays) | `w`, `h`, `fps`, `pix_fmt`, `alfa`, `audio` |
| `Logos/` | ~24 png/webp/jpg: claude, chatgpt, gemini, deepseek, perplexity, kling, wan, sora, youtube, instagram, tiktok, premiere, capcut, davinci, photoshop, canva, metricool… | `w`, `h`, `modo`, **`alfa`** (pixel a pixel), `marca` |

## O catálogo — gerar e manter

```
python3 scripts/biblioteca.py catalogar                # as quatro pastas
python3 scripts/biblioteca.py catalogar --so musicas   # uma
python3 scripts/biblioteca.py catalogar --forcar       # remede tudo
```

A chave de cada item é `oficina.identidade()` (tamanho + cabeça + cauda), não o
nome: renomear não remede, trocar o arquivo remede só aquele, arquivo apagado
sai. **Rodar `catalogar` de novo é grátis** — com nada mudado custa o tempo de
ler 16 MB por arquivo. A primeira rodada das 185 faixas leva alguns minutos
(ffprobe + `ebur128` em 6 threads). Um arquivo que falha na medição entra com
`erro` e não derruba a pasta (há um SVG chamado `logo-outro.png` no acervo).

Consultas:

```
biblioteca.py listar musicas --clima tensao --max-eventos 1      # uma linha por faixa
biblioteca.py listar logos --alfa                                # só os que servem ao logo_atras
biblioteca.py listar overlays --json
biblioteca.py cama --clima "melancolia" --n 5                    # ver abaixo
biblioteca.py sfx marcador                                       # ver abaixo
```

### O índice de evento (`eventosMin`)

O ebur128 entrega o loudness momentâneo a cada 100 ms. O script faz a média por
janela de 1 s e conta cada salto **≥ 6 dB** de uma janela para a seguinte, por
minuto de áudio. Entrada de bateria, refrão, virada — o que compete com a
estrutura numerada do vídeo — aparece aqui; um pad contínuo dá zero. O
aquecimento do medidor e o silêncio de cabeça não contam. É a tradução medível
de «a cama não pode ter nenhum evento que o espectador consiga contar».

## Escolher a cama do `analise`

As regras são as de `formato-analise.md`, seção «Som» — leia lá, não aqui. Em
resumo do que o script aplica e do que fica com quem escolhe:

- **Instrumental, sem vocal** — não negociável. `cama` descarta o que tem «vocal»
  no nome (mas não «sem vocal» / «no vocal bleed»); `versao` diz se o nome
  declarou Instrumental/Karaokê/Playback. Nome sem declaração pede escuta.
- **Contínua e sem evento** — `cama` ordena por `eventosMin` e depois por `lra`
  (menor variação ganha) e exige duração ≥ 90 s. LUFS não entra na escolha: o
  nível é o `ganho` do plano (≈ 0,085 sobre a voz normalizada, ~15–20 dB abaixo
  da fala), não a faixa.
- **Troca por assunto, com cruzamento de 1,2–1,5 s em potência constante** — o mapa
  `trilha` do `plano.json` é por momento (`["M09", "v"]`), nunca por segundo.
- A obra analisada pode fornecer a própria cama (versão instrumental do tema) —
  é prova ambiente, e vale mais que faixa genérica. A biblioteca é o plano B.

`cama` imprime as N candidatas com caminho absoluto, LUFS, LRA, eventos/min, o
aviso de licença e o bloco `"musicas": {...}` pronto para colar no `plano.json`
(formato na docstring de `render_analise.py`). `src` sai 0.0: o ponto de entrada
na faixa é decisão de escuta.

## SFX — gatilho → arquivo

A tabela é a de «Os SFX» em `formato-analise.md`; `biblioteca.py sfx <gatilho>`
responde com o arquivo ou com «nenhum» e o motivo.

| Gatilho | SFX | Por quê |
| --- | --- | --- |
| `marcador` — o número do capítulo entra sobre o gesto | `Hit` | impacto curto e seco, sem cauda |
| `cartao` — o cartão entra | `Woosh Fast` | whoosh curto, **só na primeira entrada de cada capítulo**; nas seguintes o corte é mudo |
| `pb` — entrada em P&B | nenhum | é filtro / queda de banda na mistura, não efeito somado |
| `destaque` — a palavra em destaque aparece | nenhum | a palavra já é o evento visual |
| `modo1` — cartão atrás do autor | nenhum | ele não para de falar; um efeito ali corta a frase |

O corpus mede 22–36 transientes por vídeo e só 10–25% caem em corte: **o SFX
acompanha o evento, não o corte.** Pop em toda entrada de vídeo foi testado e
revogado pelo dono (2026-09-14).

## Overlays — o que são, e onde NÃO entram

São texturas de vídeo (luz, grão, partículas, sketch) para compor por cima do
quadro com modo de mesclagem (Screen/Multiply/Add). Nenhum dos atuais tem canal
alfa (`yuv420p`), então compor exige mesclagem, não sobreposição simples.

**O formato `analise` não os usa.** A seção «O que este formato NÃO tem» de
`formato-analise.md` é explícita: sem motion graphics, sem grade de cor de
identidade, sem vinheta, grão ou aberração. Overlays servem a outros formatos
(`dinamismo` com motion, cartelas, `motion-vox`), nunca ao `analise`.

## Logos — como entram no `analise`

Pelo cartão `{"tipo": "logo", "fonte": "<id>", "de": …, "ate": …, "porque": …}`
com `fontes.<id>.arq` apontando para o arquivo. `render_analise.py` abre com
`Image.open` e passa a `cartao.logo_atras`, que redimensiona para 38% da largura
e compõe **em RGBA** por trás de quem fala, parando na `BASE_MODO1`.

O que `logo_atras` exige, e o catálogo confere:

- **Fundo transparente de verdade.** `alfa: true` significa que algum pixel tem
  alfa < 255 — modo RGBA com alfa 255 em tudo é chapado, e «chapado sobre o
  A-roll vira adesivo». `listar logos --alfa` lista só os que servem. JPG nunca
  serve; PNG em modo `P` só se tiver transparência declarada.
- **Formato que o Pillow abre.** SVG não (o `logo-outro.png` do acervo é um SVG
  e sai com `erro`).
- O logo some quando a frase que o citou acaba; o matte do rosto é providenciado
  pelo render, não pelo arquivo.

O logo é uma marca citada, e entra no `provas.json` como fonte (`tipo` da fonte,
título, autor/URL de onde veio), como qualquer insert.
