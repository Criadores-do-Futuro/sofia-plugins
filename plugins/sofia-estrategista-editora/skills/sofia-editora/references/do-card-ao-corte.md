# Do card ao corte

O Caminho 1 do SKILL.md, etapa por etapa. `RAIZ` é a pasta do plugin.

## 1. O card manda na edição

Com o conector ligado e com login:

- `planejamento_quadro`: acha o card do vídeo gravado (em geral na coluna Gravar).
- `sofia_video`: o formato, a estrutura, o hook, as versões do roteiro com a escolhida, as referências ligadas e a lista de gravação.
- `planejamento_gravar`: o roteiro escolhido pronto para gravar e a situação da gravação.
- `cerebro_buscar` na camada `como-trabalhar`: o "faça" e o "evite" da pessoa, que também valem para a edição (legenda, música, ritmo).

Do roteiro saem as marcas da edição: onde o hook abre e qual promessa ele faz, onde cada bloco da estrutura começa, onde a promessa é paga, a virada, o fim e a chamada. Se a fala gravada fugiu do roteiro, a fala gravada vale para o corte. Mostre a diferença à pessoa quando ela mudar o sentido.

Sem o conector, peça o roteiro, o formato e a estrutura. Sem roteiro, parta da fala gravada.

## 2. Entender o bruto

Para cada arquivo gravado:

```sh
python3 "$RAIZ/scripts/inventariar_midia.py" BRUTO --saida BRUTO-inventario.json --origem "gravação da pessoa"
python3 "$RAIZ/scripts/transcrever_referencia.py" BRUTO --modelo MODELO.pt --saida BRUTO-transcricao.json --idioma pt
python3 "$RAIZ/scripts/analisar_trilhas_audio.py" BRUTO --saida BRUTO-audio.json
python3 "$RAIZ/scripts/gerar_pranchas_quadros.py" BRUTO --saida PRANCHAS-BRUTO --contar-quadros --largura 240
```

A transcrição pode engolir palavras: confira as emendas no áudio medido e na imagem. Marque erro, repetição, take bom, respiro e o que cada take mostra. Entre duas tentativas da mesma frase, proponha a melhor e diga por quê; a pessoa decide quando houver dúvida.

## 3. O plano editorial v1

O contrato está em `docs/contrato-editorial.md` e o schema em `schemas/plano-editorial.v1.schema.json`. Tempos em milissegundos inteiros, intervalos `[início, fim)`. Esqueleto mínimo:

```json
{
  "version": "1.0",
  "project": {"title": "Nome do vídeo", "editor": "capcut", "creative_format": "dinamismo"},
  "assets": [{"id": "take", "kind": "video", "duration_ms": 3000}],
  "protected_speech": [{"id": "palavra", "asset_id": "take", "source": {"start_ms": 1000, "end_ms": 1400}, "text": "não"}],
  "clips": [
    {"id": "imagem", "asset_id": "take", "track": "v1", "kind": "video", "source": {"start_ms": 500, "end_ms": 2000}, "timeline": {"start_ms": 0, "end_ms": 1500}, "speaker_visible": true},
    {"id": "voz", "asset_id": "take", "track": "a1", "kind": "audio", "source": {"start_ms": 500, "end_ms": 2000}, "timeline": {"start_ms": 0, "end_ms": 1500}}
  ]
}
```

- `protected_speech` guarda a fala que não pode ser cortada. A proteção de 600 ms de cada lado de [direcao.md](direcao.md) vale para remoção automática de erro.
- J-cut e L-cut usam vídeo e áudio em pistas separadas, com intervalos próprios. Com rosto falando visível, a voz não sai da boca.
- `text_layers` separa `caption` (a fala) de `lettering` (o que você escreve). Lettering passa pelo Piso.
- Ao lado do plano, guarde uma tabela de direção: momento, bloco da estrutura, o que acontece, por quê, e a observação do guia de estilo aplicada (pelo `id`).

Valide até zero erro: `python3 "$RAIZ/scripts/validar_plano_editorial.py" PLANO.json` (precisa de `pip install -r "$RAIZ/requirements-editorial.txt"`). Plano válido não prova sincronia, render nem qualidade. Mostre a tabela à pessoa antes de montar.

## 4. Escolher o editor com evidência

`beditor.editor_capabilities.select_editor(requested, required, evidence)` decide entre `capcut` e `davinci` só com capacidades verificadas no host. Escolha explícita da pessoa nunca muda de editor. Dado ausente é "não verificado", e não "suporta". Liste as capacidades que o plano exige (legenda, áudio separado, lettering, transição, motion importado) antes de decidir.

## 5. Montar

**CapCut Web** (plugin oficial do CapCut no host): sessão, upload dos brutos, draft novo e vazio, e `beditor.capcut_web.apply_new_plan` com as funções do builder oficial instalado. Depois, edição colaborativa do próprio plugin: push do documento completo, leitura da resposta do servidor. Legendas pelo reconhecimento oficial e `beditor.capcut_captions.apply_recognized`. Transições com `beditor.capcut_transitions.prepare_transitions`. Revisão de um draft existente com `beditor.capcut_web_revision.prepare_revision`. Tudo em `docs/ponte-capcut-web.md`.

**CapCut Desktop** (ponte MCP local): CapCut fechado, `beditor.capcut_desktop.write_package` para o pacote, `call_local_bridge` com `status`, `prepare` e `preview`, e o `commit` separado com o `confirmation_token` exato que a ponte devolveu. Em `docs/ponte-capcut-desktop.md`.

**DaVinci Resolve** (MCP do Resolve, com o Resolve aberto): mídia na Media Pool, taxas de quadros lidas do editor, índices das pistas conhecidos. `beditor.davinci_plan.translate` prepara os argumentos de `media_pool.append_to_timeline`, e `beditor.davinci_preflight.prepare` confere colisões contra um retrato atual da timeline. Releia antes, salve e confira depois. Em `docs/ponte-davinci.md`.

**Motion**: [motion.md](motion.md). O clipe renderizado entra numa pista própria e chega achatado.

Nada disso exporta. Exportar é outro pedido.

## 6. Conferir antes de dizer que está pronto

- Read-back: no CapCut Web, `beditor.capcut_readback.compare(plano, snapshot, package_id, segment_ids=...)`. No DaVinci, releia a timeline depois de salvar.
- Assista à prévia acessível, quando houver. Sem prévia, diga que não viu.
- Fala inteira, boca sincronizada, legenda igual à fala, nomes e acentos certos, lettering pelo Piso, áreas seguras do celular, som sem estouro.
- Compare com o guia de estilo, bloco a bloco, e corrija o que destoa.

## 7. Entregar

Em poucas linhas: onde está o projeto (draft ou timeline, com o nome), o que foi aplicado do estilo, o que ficou para fazer à mão, o que não deu para conferir e o próximo passo. Com o conector, não mova o card nem marque como gravado ou postado sem a pessoa pedir. Quando ela postar e pedir, o caminho "Depois de postar" da skill `sofia-estrategista` guarda o resultado.
