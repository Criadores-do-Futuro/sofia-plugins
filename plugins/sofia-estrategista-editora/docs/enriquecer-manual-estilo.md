# Acrescentar observações ao manual de estilo

Depois de assistir e ouvir a referência — ou examinar o projeto original quando
disponível — crie um arquivo JSON com uma lista de observações. Exemplo:

```json
[
  {
    "id": "zoom-abertura-01",
    "aspecto": "movimento de câmera",
    "estado": "inferido",
    "descricao": "Parece haver uma aproximação durante a primeira frase.",
    "confianca": 0.6,
    "evidencias": [
      {
        "referencia_id": "ref-1",
        "inicio_segundos": 1.2,
        "fim_segundos": 2.6,
        "modalidade": "audiovisual",
        "nota": "Hipótese a conferir na timeline original."
      }
    ]
  }
]
```

Para gerar outra versão sem alterar o manual de origem:

```sh
python3 scripts/enriquecer_manual_estilo.py manual.json \
  --observacoes observacoes.json --saida manual-revisado.json
```

O ID da referência deve existir no manual, os tempos devem estar dentro da
respectiva duração e cada observação deve ter ID único. `medido` e `inferido`
exigem evidência temporal. Use `indisponivel` com evidências vazias quando não
for possível avaliar; nunca coloque um valor inventado nesse estado. A confiança,
quando usada, deve estar entre 0 e 1. O programa valida a estrutura, mas não
verifica se o relato é verdadeiro. Os registros existentes são preservados,
inclusive lacunas anteriores; o programa não resolve contradições entre eles.
Revise-as antes de usar o guia como base para edição. O arquivo de saída deve
ser novo, e o comando não o grava se a validação falhar.

## Atualizar um estilo já cadastrado

Após gerar e revisar o novo manual, consulte o estilo para obter
`manual.estado.sha256` e use esse valor como hash esperado:

```sh
python3 scripts/biblioteca_estilos.py --raiz /caminho/biblioteca mostrar meu-estilo
python3 scripts/biblioteca_estilos.py --raiz /caminho/biblioteca atualizar meu-estilo \
  --manual manual-revisado.json --hash-esperado HASH_OBTIDO
```

A atualização valida o novo manual e preserva a capa. O manual novo é gravado
como arquivo de versão identificado por SHA-256; as versões anteriores e seus
hashes ficam registradas em `historico_manuais` no metadado do estilo. Ao ler,
a biblioteca confere o hash da versão atual. Uma atualização com hash antigo,
arquivo atual alterado ou outro processo deste utilitário editando o mesmo
estilo é recusada. Se os metadados mudarem durante a operação, o programa
interrompe; uma versão gravada antes da falha poderá ficar como arquivo não
referenciado e será reutilizada caso seus bytes sejam idênticos na nova tentativa.

O lock serializa somente ferramentas que respeitam o lock desta biblioteca. Uma
edição externa feita exatamente entre a última conferência e a troca de metadados
pode não ser detectada. Se uma interrupção deixar `.atualizacao.lock`, confira
que não há atualização em execução antes de removê-lo manualmente.
