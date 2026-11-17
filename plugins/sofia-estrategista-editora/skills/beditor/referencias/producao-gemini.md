# Produção com Gemini — papéis, manifesto, custo e privacidade

Veio da linha do Codex (`gemini-production.md`), que a conferiu contra a
documentação oficial em **2026-09-10**. Modelo muda de nome e sai de linha:
antes de um lote pago, confira de novo em
[modelos](https://ai.google.dev/gemini-api/docs/models),
[preços](https://ai.google.dev/gemini-api/docs/pricing) e
[descontinuações](https://ai.google.dev/gemini-api/docs/deprecations).
Referências de uso: [compreensão de vídeo](https://ai.google.dev/gemini-api/docs/video-understanding),
[Omni](https://ai.google.dev/gemini-api/docs/omni),
[Veo](https://ai.google.dev/gemini-api/docs/veo),
[imagem](https://ai.google.dev/gemini-api/docs/image-generation),
[Files API](https://ai.google.dev/gemini-api/docs/files),
[retenção](https://ai.google.dev/gemini-api/docs/zdr).
Use o SDK unificado Google Gen AI, nunca o legado.

`rotas-de-geracao.md` diz **quando** o Gemini desenha. Este arquivo diz
**como**, sem gastar à toa e sem vazar nada.

## "Gemini" não é um botão só

Cada papel se configura separado:

| Papel | Modelo (conferido em 2026-09-10) | Uso |
| --- | --- | --- |
| compreensão e direção | `gemini-3.8-flash` | vídeo inteiro, roteiro, transcrição, beats, JSON estruturado, QC semântico |
| keyframe rápido | `gemini-3.1-flash-image` | figura, objeto, fundo, colagem, variação |
| keyframe de alta fidelidade | `gemini-3-pro-image` | quadro mestre, asset que justifica o custo |
| vídeo padrão | `gemini-omni-1.1-flash` | clipe a partir de texto, imagem ou vídeo; edição conversacional |
| vídeo alternativo | `veo-3.1-fast-generate-preview` | geração rápida com áudio e controles do Veo |
| vídeo premium | `veo-3.1-generate-preview` | só quando a diferença paga custo e espera |

**Hoje o `assets.py` ainda gera imagem com `gemini-2.5-flash-image`**
(`BEDITOR_MODELO_IMAGEM` troca). Mudar o padrão é decisão de código, com teste,
não de documento. Modelo `preview` precisa de alternativa configurada e nunca é
a única rota de produção.

## O que é do Gemini, o que é do HyperFrames

Gemini: entender o vídeo e citar tempo; transformar roteiro e guia em JSON
validado; gerar e editar keyframe, elemento, fundo e footage; animar imagem
aprovada; comparar o render ao beat e apontar desvio (sem substituir o olho do
editor).

HyperFrames: todo texto que precisa estar certo e legível; número, data,
gráfico, mapa, diagrama, interface, rótulo; legenda, área segura, easing,
tempo por quadro, transparência; e a montagem de várias camadas do Gemini numa
composição reproduzível.

Mesmo que o modelo consiga escrever, **informação de fato e de marca continua
determinística**.

## O manifesto, antes de qualquer chamada paga

Um item por plano. É o que se aprova antes de gastar:

```yaml
shot_id: s014
momento: M09                 # o momento do guia.json que este plano serve
render_engine: gemini-omni
model: gemini-omni-1.1-flash
duration_seconds: 6
aspect_ratio: "9:16"
purpose: "materializar a metáfora de pressão crescente"
continuity_id: "papel-vermelho-v2"   # a `familia` do momento no guia
sources:
  first_frame: "assets/keyframes/s014-inicio.png"
  last_frame: "assets/keyframes/s014-fim.png"
  references: ["assets/estilo/papel-v2.png"]
prompt:
  subject: "uma pilha de documentos recortados"
  action: "comprime devagar até quase rasgar"
  environment: "mesa editorial creme com marcas de registro"
  composition: "close vertical, centro livre para overlay"
  camera: "push-in lento, sem corte"
  lighting: "luz lateral quente, sombra curta constante"
  material: "papel fosco, borda rasgada, meio-tom sutil"
  timing: "0-1s estabelece; 1-4s comprime; 4-6s segura"
  audio: "sem diálogo; impacto seco aos 4s"
  exclusions: ["texto", "logo", "mãos extras", "troca de paleta", "tremor de câmera"]
fatos: []                    # ids do fatos.json quando o plano afirma algo
estimated_cost_usd: 0.60
remote_consent: pending
acceptance_tests:
  - "um único plano contínuo"
  - "papel e luz iguais ao keyframe aprovado"
  - "centro utilizável para o overlay"
```

O prompt declara fontes e o papel de cada uma, depois descreve sujeito, ação,
contexto, estilo, composição, câmera, lente e foco, luz, material, movimento,
tempo, áudio e exclusões. No Omni, marque o tempo como `[0-2s]` e escreva
"single continuous shot / no scene cuts" quando não quiser montagem interna.

## O fluxo

1. Analise metadado local e **materialize o arquivo** antes de qualquer upload
   (arquivo `dataless` do iCloud trava o envio sem aviso: ver `SKILL.md`).
2. Mostre ao editor: provedor, o que sobe, para quê, retenção, custo estimado e
   teto do lote.
3. **Só envie depois do sim explícito.** A chave mora em `~/.config/beditor/env`
   ou no Keychain, nunca em prompt, log, manifesto ou Git (`procedencia.md`).
4. Keyframes em baixa resolução primeiro. Escolha a direção antes do vídeo.
5. Planos de 3 a 10 s. Ação complexa vira vários planos, nunca uma geração longa.
6. Continuidade por referência e por primeiro/último quadro. Áudio de vídeo de
   referência não é fonte confiável.
7. Grave: id da operação, modelo, prompt, hash das referências, custo estimado e
   real, tentativa e motivo de rejeição. O `<ID>.prompt.txt` ao lado de cada
   imagem já faz parte disso.
8. Baixe a saída para o projeto, confira duração, resolução e áudio, e **apague
   o upload remoto** quando não servir mais.
9. Texto e dado por cima em HyperFrames; montagem sobre a voz aprovada.
10. QC técnico, factual, visual e narrativo. Resposta HTTP 200 não é plano
    aprovado.

## Custo e privacidade

- Rode seco primeiro e estime `segundos × preço do modelo`, contando as
  tentativas. Pelo preço consultado, 6 s de Omni ficam em torno de US$ 0,60,
  valor que se recalcula antes do lote.
- `store=false` quando não precisa de edição conversacional. Estado multi-turno
  só com benefício claro.
- A Files API guarda upload por até 48 horas. Apague ao terminar.
- Material sensível vai pelo serviço pago com faturamento ativo, nunca pela
  cota gratuita.
- Vídeo gerado sai com marca de procedência (SynthID). Preserve os metadados.
- **Filtro de segurança não se afrouxa** para destravar uma geração.

## Quando dá errado

| Falha | O que fazer |
| --- | --- |
| modelo indisponível ou descontinuado | consultar a lista atual, escolher o equivalente, registrar a troca |
| conteúdo bloqueado | explicar a categoria e ajustar a proposta legítima; nunca contornar |
| incoerência visual | voltar ao keyframe, simplificar a ação, reforçar os invariantes, e não empilhar adjetivo |
| texto ou fato errado na imagem | tirar da geração e compor em HyperFrames |
| custo estourou o teto | parar o lote; nunca trocar de modelo em silêncio nem seguir cobrando |
| sem credencial | entregar manifesto e prompts em modo seco (`PROMPTS.md`); não declarar mídia gerada |
