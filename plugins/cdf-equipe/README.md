# cdf-equipe

A Sofia interna da equipe da Criadores do Futuro. O plugin liga o Claude ao console da
plataforma de desafios pelo MCP e traz as skills da gestão de comunidade.

## Instalar

```
/plugin marketplace add bento-dev-ia/sofia-plugins
/plugin install cdf-equipe@sofia-plugins
```

Na primeira vez que o Claude usar o conector `cdf-equipe`, ele abre o login da plataforma
(OAuth). Entre com a conta da equipe. Ninguém cola chave nem token.

## Endereço do MCP (falta confirmar)

O conector fica em `.mcp.json`. O endereço de produção da plataforma ainda não está
definido: os documentos da plataforma tratam o domínio como "a confirmar" e a variável
`NEXT_PUBLIC_SITE_URL` é definida na Vercel. Por isso o arquivo traz um marcador:

```
https://CONFIRMAR-ENDERECO-DA-PLATAFORMA/api/mcp
```

Troque o marcador pelo endereço de produção (sem barra no fim, com `/api/mcp`) antes de
distribuir o plugin.

## Skills

| Skill | Para que serve |
|---|---|
| `console-da-equipe` | O que é o console, cargos, mercados e a regra de operação. Comece por ela. |
| `avisos-e-tarefas` | Criar e alterar avisos e tarefas agendadas, com prévia e aprovação. |
| `insights-do-discord` | A rotina semanal de ler o Discord e salvar os insights. |
| `demandas-e-reunioes` | Transformar a ata de uma reunião em demandas no quadro. |
| `depoimentos` | Achar depoimentos e guardar o texto literal, com a autorização pendente. |
| `rotinas-agendadas` | Deixar uma rotina do Claude agendada, e quando usar uma tarefa do console. |

As ferramentas que cada pessoa enxerga dependem do cargo e dos mercados dela.
