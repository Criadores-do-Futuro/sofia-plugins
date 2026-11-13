# Conector: Obsidian Vault

## Estrutura de output

Todo output do Sofia 2.0 é salvo como arquivos Markdown com frontmatter YAML, compatíveis com Obsidian. O Obsidian é opcional: a pasta de saída pode ser qualquer pasta da pessoa.

## Organização de pastas

A pasta de saída é `output_path`, definida em `~/.sofia/config.yaml` (no Windows, `%USERPROFILE%\.sofia\config.yaml`).

```
{output_path}/
├── Pesquisas/
│   └── {nome-do-criador}/
│       └── {titulo-do-video}/
│           ├── roteiro-anotado.md
│           ├── hook.md
│           ├── comentarios.md
│           ├── metricas.md
│           └── aprendizados.md
│
├── Roteiros/
│   └── {YYYY-MM-DD}-{titulo}/
│       ├── roteiro-v1.md
│       ├── roteiro-v2.md
│       ├── critica.md
│       └── versao-final.md
│
├── Analises/
│   └── dashboard.html
│
└── Exports/
```

Os aprendizados (hooks, padrões, insights de comentários, estilos) não ficam aqui: ficam na pasta de dados da Sofia, `~/.sofia/` (ver `/sofia:setup`).

## Configuração

### Achar o vault
Primeiro pergunte à pessoa onde fica o vault. Só procure no computador se ela autorizar a busca na pasta pessoal:
```bash
find ~ -name ".obsidian" -maxdepth 4 -type d 2>/dev/null
```
Mostre o que encontrou e confirme antes de usar.

### Manual
Definir em `~/.sofia/config.yaml`:
```yaml
output_path: "/caminho/completo/para/seu/vault/Sofia"
```

## Convenções de nomenclatura

- **Criadores:** slug do nome (minúsculas, hifens): `nome-do-criador`
- **Títulos:** primeiras 5-6 palavras em slug: `empresario-mentiroso-faturou-bilhoes`
- **Datas:** formato ISO: `2026-05-14`

## Frontmatter padrão

Todos os arquivos incluem:
```yaml
---
title: ""
tags: [sofia, ...]
created: "YYYY-MM-DD"
---
```

## Comentários
Arquivos de comentários guardam o texto literal, as curtidas e a data. Nunca o @, o nome ou a foto de quem comentou.

## Integração com Obsidian

- Tags permitem filtrar por tipo (analise, roteiro, hook, insight)
- Wikilinks conectam análises a roteiros inspirados nelas
- Dataview pode agregar dados dos frontmatters
- Graph view mostra conexões entre análises e roteiros
