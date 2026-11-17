# Aprender a edição de um vídeo editado

Objetivo: transformar a edição de um vídeo pronto (a referência) num guia de estilo com evidência de tempo, guardado na biblioteca e aplicado nos próximos brutos. `RAIZ` é a pasta do plugin (veja o SKILL.md). As regras gerais de análise estão em [estilo.md](estilo.md).

## 0. Antes de começar

- Pergunte de quem é o vídeo e se a pessoa pode usar como referência. A origem e a licença informadas vão para o inventário.
- Se ela tiver o projeto original (draft do CapCut, projeto do DaVinci), peça. Pistas, keyframes e parâmetros são a melhor evidência que existe. Abra só para ler, sem alterar.
- Combine três pastas: `ANALISE` (nova, não pode existir), `PRANCHAS` (nova) e a biblioteca `BIB` (ou `BIBLIOTECA_ESTILOS_RAIZ`). Vídeo longo gera muita prancha: prefira um disco com espaço.
- Escolha um `ID` curto, em minúsculas e com hífens (por exemplo `cortes-secos-zoom`), e um nome que a pessoa reconheça.

## 1. Pegar o vídeo

- Arquivo local: use direto. O plugin nunca copia nem altera o original.
- Link público de um vídeo só: `python3 "$RAIZ/scripts/baixar_referencia.py" URL --saida PASTA_NOVA`. Sem cookies, sem login, sem playlist. Se o site pedir login, peça o arquivo à pessoa. Detalhes em `docs/download-referencia.md`.
- Registre: `python3 "$RAIZ/scripts/inventariar_midia.py" VIDEO --saida INVENTARIO.json --origem "..." --licenca "..."`.

## 2. Medir tudo de uma vez

```sh
python3 "$RAIZ/scripts/preparar_estilo.py" VIDEO [VIDEO2 ...] --nome "NOME" --id ID \
  --analise ANALISE --biblioteca BIB [--modelo MODELO_WHISPER.pt]
```

O que sai em `ANALISE`, por referência `N`:

| Arquivo | O que tem |
|---|---|
| `ref-N-quadros.jsonl` | Uma linha por quadro decodificado: `quadro`, `pts_segundos`, `pontuacao_mudanca`, `luma_media`, `saturacao_media` |
| `ref-N-mudancas.json` | Candidatos de corte (picos de mudança visual), com `pico_segundos` e pontuação |
| `ref-N-audio.json`, `ref-N-trilhas-audio.json` | Silêncios e nível de cada trilha de áudio |
| `manual.json` | O manual inicial v1: medidas de luz e cor e a lista do que falta analisar (`indisponivel`) |
| `capa.jpg`, `analise.json` | A capa (um quadro do meio) e as fontes com hash e limites |

O estilo já entra na biblioteca com esse manual inicial. Com `--modelo`, a transcrição fica na pasta de análise e não entra no manual por padrão.

Os candidatos de corte erram: movimento e flash viram falso corte, e corte sutil pode passar. Eles apontam onde olhar. A confirmação vem das pranchas.

## 3. Ver todos os quadros

```sh
python3 "$RAIZ/scripts/gerar_pranchas_quadros.py" VIDEO --saida PRANCHAS --contar-quadros [--largura 240]
```

Cada prancha tem 25 quadros (5 por 5), em ordem, da esquerda para a direita e de cima para baixo. O `manifesto.json` diz, para cada prancha, `quadro_inicial` e `quadro_final`, e confere se todos os quadros foram processados. O tempo de um quadro está em `ref-N-quadros.jsonl` (`pts_segundos` da linha com aquele `quadro`). Para vídeo longo, use `--largura` menor e leia em blocos.

## 4. Ouvir o que dá para ouvir

- Transcrição com tempo por palavra: `python3 "$RAIZ/scripts/transcrever_referencia.py" VIDEO --modelo MODELO.pt --saida TRANSCRICAO.json --idioma pt` (outras trilhas com `--trilha`). Revise ouvindo quando possível. Veja `docs/transcricao-local.md`.
- Para pôr os indícios de fala no manual: `python3 "$RAIZ/scripts/adicionar_transcricao_ao_manual.py" MANUAL.json TRANSCRICAO.json --referencia ref-1 --saida MANUAL-FALA.json`.
- Você não escuta a trilha. Silêncio e nível medidos, mais a transcrição, mostram respiros, cortes na fala e onde entra outra voz. Música, efeito sonoro e J-cut ou L-cut ficam como `inferido`, com a evidência, ou `indisponivel`.

## 5. Ler a edição, bloco a bloco

No Claude Code, chame o ajudante `analista-de-edicao` uma vez por bloco de pranchas (por exemplo, 8 pranchas, uns 200 quadros), passando: a pasta de análise, a pasta de pranchas, o id da referência (`ref-1`), a duração, o intervalo de pranchas do bloco, a transcrição se houver, e o caminho do arquivo de observações que ele deve escrever. Sem o ajudante, faça a mesma leitura você mesma.

O que observar, com o tempo de cada exemplo:

- **Abertura:** os primeiros 3 segundos. O que aparece, o primeiro corte, o primeiro texto na tela.
- **Cortes e ritmo:** onde corta (fim de frase, respiro, no meio da palavra), quanto dura cada plano, se o ritmo muda entre o hook, o meio e o fim.
- **J-cut e L-cut:** a voz que chega antes da imagem, ou fica depois dela.
- **Enquadramento:** rosto centrado ou de lado, plano fechado ou aberto, espaço para a legenda.
- **Zoom e movimento:** punch-in na ênfase, aproximação lenta, tremida, pan, tracking. Diga em que palavra acontece.
- **Transições e máscaras:** corte seco, fade, whip, máscara, tela dividida, tela verde.
- **Legenda:** posição, tamanho, caixa alta ou não, cor, fundo, palavra por palavra ou frase inteira, destaque de palavra.
- **Lettering:** o que diz, função (título, número, prova), fonte aparente, entrada e saída.
- **Imagens de apoio:** quando entram e para quê (prova, demonstração, piada), quanto tempo ficam.
- **Cor e luz:** quente, fria, contraste, mudanças entre cenas. Use as medidas de luz e cor do manual.
- **Som:** música (entra, sai, abaixa sob a fala), efeitos sonoros e em que momento.
- **Fim:** como termina, se há chamada e como aparece.

Cada observação segue o formato do manual (detalhes em `docs/enriquecer-manual-estilo.md`):

```json
{
  "id": "zoom-enfase-01",
  "aspecto": "zoom e câmera",
  "estado": "inferido",
  "descricao": "Punch-in rápido no rosto quando a fala chega ao número do hook.",
  "confianca": 0.7,
  "evidencias": [
    {"referencia_id": "ref-1", "inicio_segundos": 1.2, "fim_segundos": 1.6, "modalidade": "video",
     "nota": "Pranchas 2 e 3, quadros 36 a 48: o rosto cresce cerca de 20% em 4 quadros."}
  ]
}
```

- `estado`: `medido` (há número medido), `inferido` (você viu ou deduziu, com evidência) ou `indisponivel` (não dá para saber; evidências vazias e sem valor).
- `modalidade`: `video`, `audio` ou `audiovisual`.
- Tempos dentro da duração da referência. IDs únicos.
- Uma regra que se repete vira uma observação com várias evidências. Uma exceção vira uma observação própria.

## 6. Gravar o guia

```sh
python3 "$RAIZ/scripts/enriquecer_manual_estilo.py" ANALISE/manual.json --observacoes OBSERVACOES.json --saida MANUAL-REVISADO.json
python3 "$RAIZ/scripts/validar_manual_estilo.py" MANUAL-REVISADO.json
python3 "$RAIZ/scripts/biblioteca_estilos.py" --raiz BIB mostrar ID
python3 "$RAIZ/scripts/biblioteca_estilos.py" --raiz BIB atualizar ID --manual MANUAL-REVISADO.json --hash-esperado HASH
```

O `HASH` é o `manual.estado.sha256` que o `mostrar` devolve. Se vários blocos geraram vários arquivos de observações, junte numa lista só antes de enriquecer, ou enriqueça em sequência (cada saída vira a entrada da próxima). O validador confere estrutura e tempos, não a verdade do que foi escrito.

## 7. Mostrar o guia à pessoa

Entregue o guia como uma receita, na linguagem de 8 anos, nesta ordem: abertura, cortes e ritmo, rosto e enquadramento, zoom e movimento, legenda, lettering, imagens de apoio, cor, som, fim. Cada regra tem um exemplo com tempo ("aos 0:03, corta no respiro, antes da próxima frase") e diz se foi medida ou é hipótese. No fim, liste o que não deu para saber.

Pergunte o que está errado ou faltando. Cada correção vira observação nova e versão nova do guia (passo 6). Com o OK da pessoa e o conector ligado, a referência também pode ir para o site com `referencia_salvar`.

## 8. Aplicar no bruto

Siga o Caminho 1 do SKILL.md com este estilo escolhido. No plano editorial, cada decisão de estilo cita o `id` da observação que ela aplica. Depois de montar, compare a prévia com a referência, bloco a bloco (abertura, ritmo de cortes por bloco, legenda, zoom, som), liste os desvios que importam e corrija. Nunca prometa um vídeo idêntico: o bruto é outro, e a fala da pessoa manda.

## Limites que você conta à pessoa

- Medição de quadro não reconhece efeito, fonte exata, máscara, tracking nem intenção. Isso vem da leitura das pranchas, e fica como hipótese quando não há prova.
- Você não ouve a trilha. Música e efeito sonoro são inferidos pelo nível, pelo silêncio, pela transcrição e pela imagem, ou ficam como não verificáveis.
- Sem o projeto original, parâmetros (curva do zoom, nome da fonte, preset de cor) são aproximações.
- O estilo de outra pessoa é referência de linguagem. Marca, texto, provas e rosto dela não vão para o vídeo novo.
