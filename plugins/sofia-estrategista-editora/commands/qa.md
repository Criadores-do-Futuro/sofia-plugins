---
description: Roda os seis testes de validação sobre um MP4 do bEditor
allowed-tools: Read, Bash, Glob
---

Uso: `/sofia-estrategista-editora:qa <arquivo.mp4>`.

Valide `$1` contra a lista da skill bEditor.

**Antes de olhar frame nenhum**, meça o layout das composições no navegador:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/conferir_layout.py --estilo vox
```

Ele avança a timeline até o fim e lê a caixa real de cada elemento: destaque que não
cobre a palavra, anotação circulando a linha errada, texto fora da área segura, texto
sobreposto, conteúdo vazando o quadro. Roda em segundos, antes do render — o frame
mostra *que* ficou torto; isto mostra *por quê*. Se acusar, conserte antes de renderizar.

Este estilo erra posição com facilidade, e por um motivo estrutural: a colagem gira e
rasga de propósito, e qualquer medida calculada em Python descola da métrica real da
fonte assim que o texto quebra linha. Ao consertar, **ancore no elemento-alvo** (CSS
esticado pelas bordas da caixa real) em vez de corrigir o número — número corrigido
volta a errar no próximo texto de tamanho diferente.

Depois disso, extraia frames em 1,0 s, no meio e perto do fim. Meça o histograma (`noturno`: mediana
abaixo de 40, pico estreito acima de 235). Confira as áreas seguras: nada de texto nos
12% do topo nem nos 22% da base. Olhe os frames e responda ao teste do mudo e ao teste
do polegar com honestidade — se a imagem congelada em 1,0 s não segura, diga isso.

Termine com um veredito curto: entrega ou volta, e o que exatamente refazer.
