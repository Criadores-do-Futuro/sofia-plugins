---
name: exportar
description: Exporta análises e aprendizados como arquivos .md ou guarda os aprendizados na pasta de dados da pessoa (~/.sofia/) para melhorar a escrita futura.
---

# Exportar e Aprender

## Trigger

Usuário pede para exportar resultados ou pede para a Sofia "aprender" com uma análise.

## Onde gravar

A pasta do plugin é trocada a cada atualização, então **nada é gravado dentro dela**. Os aprendizados vão para a pasta de dados da pessoa, `~/.sofia/` (no Windows, `%USERPROFILE%\.sofia\`), e as exportações vão para a pasta de saída (`output_path` em `~/.sofia/config.yaml`).

## Modos

### Modo 1: Exportar como .md
Gerar arquivo(s) markdown com:
- Análise completa formatada
- Hooks coletados
- Insights de comentários (texto literal, sem @ ou nome de quem comentou)
- Padrões identificados

Output em pasta escolhida pelo usuário ou `{output_path}/Exports/`.

### Modo 2: Aprender (guardar na base da pessoa)
Ativar agente `aprendiz` para:
1. Extrair padrões da análise recente
2. Adicionar hooks à coleção
3. Identificar novos elementos viciantes
4. Gravar em `~/.sofia/aprendizados/` (hooks, padrões, insights de comentários)
5. Sugerir melhorias de método, com confirmação, como nota em `~/.sofia/aprendizados/sugestoes.md`

### Modo 3: Exportar base completa
Gerar arquivo único com toda a base de conhecimento da pessoa:
- A base inicial do plugin (`knowledge/`) somada aos aprendizados de `~/.sofia/aprendizados/`
- Todos os hooks coletados
- Todos os padrões aprendidos
- Todas as métricas agregadas
- Útil para backup ou migração

## Fluxo

1. Perguntar: "O que quer fazer?"
   - Exportar última análise como .md
   - Aprender com a última análise (guardar na sua base)
   - Exportar toda a base de conhecimento
   - Anotar sugestões de melhoria do método

2. Executar modo escolhido

3. Confirmar:
   - Se exportar: mostrar caminho do arquivo
   - Se aprender: mostrar o que foi adicionado/atualizado
   - Se anotar sugestões: mostrar o texto e pedir confirmação antes de gravar

## Regras

- Nunca modificar arquivos da pasta do plugin (`agents/`, `skills/`, `references/`, `knowledge/`)
- Sempre mostrar o que vai ser gravado antes de gravar
- Exportações não afetam a base de conhecimento
- Aprendizados são aditivos (não sobrescrevem, adicionam)
