# Contrato editorial v1

O arquivo `schemas/plano-editorial.v1.schema.json` descreve um plano neutro,
independente de CapCut e DaVinci. **Não é um payload nativo de nenhum editor**.
Ele usa tempos inteiros em milissegundos e intervalos semiabertos `[início, fim)`.
Nesta versão, cada clipe reproduz sua origem em velocidade normal, sem retiming.

- `assets` identifica material e duração. `uri` e `provenance` são opcionais;
  disponibilidade, direitos, presença real de áudio e mídia não são verificados.
- `protected_speech` marca intervalos de fala que devem permanecer inteiros no
  áudio. Usar apenas intervalos realmente identificados; o validador não escuta a
  fonte nem encontra erros omitidos da transcrição.
- `clips` posiciona intervalos das fontes na timeline. Áudio e vídeo separados
  podem se sobrepor em pistas diferentes. Para vídeo que também fornece áudio,
  declare `carries_source_audio: true`. Para rosto visível, use `speaker_visible`.
- `text_layers` distingue `caption` de `lettering`. Uma legenda vinculada por
  `speech_id` precisa coincidir com a posição calculada da fala na timeline.

O validador confere schema, IDs, referências, limites de duração e preservação de
fala, além de sinalizar deslocamento relativo de áudio enquanto o mesmo falante
está visível. A detecção de sincronismo depende da anotação de fala e visibilidade:
ela não substitui revisão da prévia e da boca. Uma fala protegida precisa caber
inteiramente em um clipe com áudio; este contrato inicial não aceita fracionar
uma unidade protegida em duas emendas. Não aplique o teste de sincronia ao áudio
que pertence a outra tomada: J-cuts usam pistas independentes.

Instale `requirements-editorial.txt` no ambiente escolhido e execute:

```sh
python3 scripts/validar_plano_editorial.py caminho/do/plano.json
python3 -m unittest discover -s tests -p 'test_plano_editorial.py'
```

O resultado válido não verifica renderização, disponibilidade de fontes,
capacidade do adaptador, persistência do projeto, sincronia real ou qualidade
visual. Essas etapas precisam de leitura e inspeção do editor escolhido.
