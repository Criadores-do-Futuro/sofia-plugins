# Sofia Interna

A Sofia interna da equipe da Criadores do Futuro. O plugin liga o Claude ao console da
plataforma de desafios pelo MCP e traz as skills da gestão de comunidade.

## Instalar

```
/plugin marketplace add bento-dev-ia/sofia-plugins
/plugin install sofia-interna@sofia-plugins
```

Na primeira vez que o Claude usar o conector `sofia-interna`, ele abre o login da plataforma
(OAuth). Entre com a conta da equipe. Ninguém cola chave nem token.

## Endereço do MCP

O conector fica em `.mcp.json` e aponta para a plataforma internacional:

```
https://plataforma.academiacreadoresdelfuturo.com/api/mcp
```

O console da equipe abre em `console.academiacriadoresdofuturo.com`. O domínio e o idioma
do console não decidem qual banco ele lê: cada mercado tem a sua base (o BR no Firebase
nacional, LATAM e EN no internacional), e o console lê cada uma com as permissões dela.

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

## Só para a equipe

Este plugin é de uso interno. Ele fica no repositório privado `sofia-plugins` (a sua conta
do GitHub precisa ter sido convidada) e nunca é enviado ao diretório público da Anthropic
nem ao da OpenAI.

## Privacidade, termos e suporte

- [Privacy — política de privacidade](https://plataforma.academiacriadoresdofuturo.com.br/sofia/privacidade)
- [Terms — termos de uso](https://plataforma.academiacriadoresdofuturo.com.br/sofia/termos)
- [Support — suporte](https://plataforma.academiacriadoresdofuturo.com.br/sofia/suporte)

## Como atualizar

As ferramentas do MCP moram em outro repositório, o `desafiocdf-internacional`, na pasta
`lib/mcp/console`. Este plugin guarda só o conector (`.mcp.json`) e as skills que ensinam a
usar essas ferramentas. Por isso, quando uma ferramenta mudar lá (nome, campos, regra de
cargo ou de mercado), a skill daqui precisa mudar junto.

**Quem mantém o plugin:**

1. Atualize as skills em `plugins/sofia-interna/skills/` para refletir as ferramentas novas.
2. Suba a versão, com o mesmo número, nestes quatro lugares:
   - `plugins/sofia-interna/.claude-plugin/plugin.json`;
   - `plugins/sofia-interna/.codex-plugin/plugin.json`;
   - `listings/sofia-interna.json`;
   - a entrada `sofia-interna` do `.claude-plugin/marketplace.json`.
3. Rode o validador e os testes, a partir da raiz do repositório:

   ```
   python3 -m pip install -r requirements-validation.txt
   python3 tools/validate_plugins.py
   python3 -m unittest discover -s tests -v
   ```

4. Abra um PR. Sem versão nova, quem já instalou não recebe a mudança.

**Quem usa o plugin (já instalado):**

```
/plugin marketplace update sofia-plugins
```

Isso atualiza a lista do marketplace. Depois, atualize o plugin pelo `/plugin` (aba
**Installed**, **Update now**) ou no terminal com
`claude plugin update sofia-interna@sofia-plugins`, e rode `/reload-plugins` (ou abra uma
sessão nova) para usar a versão nova. Se a versão não subiu, não há nada a atualizar.

Para instalar pela primeira vez:

```
/plugin marketplace add bento-dev-ia/sofia-plugins
/plugin install sofia-interna@sofia-plugins
```
