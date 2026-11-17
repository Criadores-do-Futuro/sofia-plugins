# De onde veio cada parte

Este repositório junta três projetos. Os três continuam existindo e podem receber melhorias; este arquivo diz de onde cada arquivo veio e o que mudou aqui, para trazer as próximas versões sem perder nada.

## Fontes

| Projeto | Repositório | Commit de origem |
|---|---|---|
| Sofia Estrategista (plugin v1.2.0) | `bento-dev-ia/sofia-estrategista`, branch `feat/redes-oficiais` | `d84a99d` (2026-11-13), "Versão 1.2.0: leitura dos números direto da rede conectada" |
| bEditor Estrategista | `bento-dev-ia/beditor-capcut`, branch `main` | `cca16ea` (2026-11-12), merge do PR #9 |
| bEditor original (cortar, montar, publicar, motion-vox, diretor) | `bento-dev-ia/beditor`, branch `main` | `7feacd6`, mais as alterações ainda não commitadas da cópia local em 16/11/2026 |

## Como os arquivos foram arrumados

- A pasta `plugin/` da Sofia virou a raiz: `skills/sofia-estrategista/`, `commands/`, `agents/`, `.mcp.json`, `.claude-plugin/icon.png` e `LICENSE`.
- O bEditor entrou inteiro, na mesma posição: `beditor/`, `scripts/`, `schemas/`, `motion/`, `docs/`, `tests/`, `requirements-*.txt` e os ignores.
- A skill `skills/beditor-estrategista/` virou `skills/sofia-editora/`. O pacote Python continua com o nome `beditor`, para não quebrar importações.
- `docs/desenho.md` da Sofia virou `docs/desenho-sofia.md`. `scripts/empacotar.sh` e `scripts/conferir-ferramentas.mjs` vieram da Sofia.

Fora os arquivos listados abaixo, todos são cópias idênticas da origem (53 da Sofia e 82 do bEditor, na conferência de 16/11/2026).

## O que mudou aqui

**Da Sofia**

- `skills/sofia-estrategista/SKILL.md`: a descrição manda a edição para a skill `sofia-editora`; o passo 6 em "Gravar" e uma linha em "Onde está o resto" fazem a ponte.
- `.claude-plugin/plugin.json`: nome `sofia-estrategista-editora`, versão `0.1.0`, descrição e palavras-chave dos dois.
- `README.md` e `LICENSE`: reescrito e renomeado para o plugin junto.
- `scripts/empacotar.sh`: monta `dist/sofia-estrategista-editora.plugin` a partir da raiz.
- `scripts/conferir-ferramentas.mjs`: lê os `.md` da raiz, sem `tests/`, `dist/` e `node_modules/`.

**Do bEditor**

- `skills/sofia-editora/SKILL.md`: reescrita na voz da Sofia, com os caminhos do card ao corte, aprender a edição, estilos e motion, ligada ao conector.
- `skills/sofia-editora/references/direcao.md` e `formatos-sofia.md`: as fichas do método agora vêm no plugin.
- `scripts/localizar_sofia.py`: sem `--acervo`, procura em `SOFIA_ACERVO_DIR`, depois em `BEDITOR_SOFIA_DIR`, depois nas fichas da skill `sofia-estrategista`.
- `scripts/analisar_referencias_estilo.py`: caminho novo de `analisar_quadros.py`.
- `.claude-plugin/marketplace.json` (marketplace `sofia-editora`), `.codex-plugin/plugin.json` (skills e conector) e `.agents/plugins/marketplace.json` (marketplace `sofia-editora-local`).
- `.gitignore`, `.cloudignore` e `.npmignore`: somadas as regras da Sofia (`dist/` e configuração de assistente) e liberados `.claude-plugin/icon.png` e `schemas/*.schema.json`.
- `docs/instalacao-e-compatibilidade.md`: nomes e comandos novos.
- `tests/test_marketplaces.py`, `tests/test_localizar_sofia.py` e `tests/test_analisar_quadros.py`: manifestos, skills, conector, comandos e fichas do plugin junto.

**Do bEditor original**

Onde cada parte entrou:

| Na origem | Aqui |
|---|---|
| `skills/beditor/` (scripts, testes, modelo do motion, referências, fontes) | `skills/beditor/` |
| `skills/motion-vox/` | `skills/motion-vox/` |
| `agents/diretor.md`, `enriquecedor.md`, `analista-de-estilo.md` | `agents/` |
| 14 comandos de `commands/` | `commands/`; `aprender.md` virou `aprender-motion.md` e `analise.md` virou `editar-analise.md`, porque os nomes já eram da Sofia |
| `painel/` | `painel/`, sem `instalar_gancho.sh` (ferramenta só de quem desenvolve) |
| `treinamento/demonstracao` | `treinamento/demonstracao` (as pastas de mídia ficam fora do git) |
| `README.md` | `docs/beditor-motion.md` |
| `manual.html` | `docs/manual.html` (nome mantido: o `setup.py` procura esse nome) |
| `requirements.txt` | `requirements-motion.txt` |

Mudanças feitas na entrada:

- Os atalhos `/beditor:...` viraram `/sofia-estrategista-editora:...` em 29 arquivos, inclusive nos testes; `painel/telemetria.py` reconhece os dois nomes, para ler sessões antigas.
- `projeto.sh` e `publicacao.py` acham as fontes do `motion-vox` dentro do plugin, sem cair para `~/.claude/skills`.
- `skills/motion-vox/SKILL.md` e `INSTALAR.md`: a skill vem dentro do plugin; o kit de fotografia é opcional (`$ASSETS`).
- `skills/beditor/referencias/sofia-no-fluxo.md`: sem caminho pessoal; o método vem de `skills/sofia-estrategista/references/`, do `sofia_metodo` ou de `scripts/localizar_sofia.py`.
- `skills/beditor/referencias/legado-local.md`, `docs/beditor-motion.md` e `docs/manual.html`: instalação e atualização pelo plugin junto.
- `hf.py` e `legenda_hf.py`: o CLI do HyperFrames roda com versão fixa (`hyperframes@0.9.58`, trocável por `BEDITOR_HYPERFRAMES`), como pede o diretório da Anthropic.
- `setup.py`: o comando de atualizar é `claude plugin update sofia-estrategista-editora@sofia-editora`.
- `tests/test_setup.py` e `tests/test_terceiros.py`: nome novo do comando, forma nova do campo de licença e menções permitidas ao material da Sofia.
- `.gitignore` e `scripts/empacotar.sh`: somados os derivados do painel e as pastas de mídia do treinamento; o pacote leva `painel/`, `treinamento/` e `requirements-motion.txt`, sem os testes das skills.

Quatro testes da origem já falhavam antes da junção e continuam falhando: `test_painel.test_criterios_do_repo_nao_tem_evidencia_quebrada`, `test_montar.test_tabela_e_conversao` e os dois de UTF-8 de `test_plataforma` (falta `encoding` de entrada e saída em `previa.py`, `capcut_status.py`, `juntar_takes.py` e `legenda_hf.py`).

**Novos**

- `skills/sofia-editora/references/do-card-ao-corte.md` e `aprender-edicao.md`.
- `agents/analista-de-edicao.md`.
- `commands/editar.md`, `commands/aprender-edicao.md` e `commands/estilos.md`.
- `docs/diretorios.md`: o que falta para enviar aos diretórios da Anthropic e da OpenAI.
- Este arquivo.

## Trazer uma versão nova de uma das fontes

1. Veja o que mudou na fonte desde o commit acima: `git -C FONTE diff --stat COMMIT_DE_ORIGEM..NOVO_COMMIT`.
2. Arquivo idêntico aqui: copie a versão nova no lugar novo (a Sofia sai de `plugin/` para a raiz; a skill do bEditor vai para `skills/sofia-editora/`).
3. Arquivo da lista "O que mudou aqui": junte à mão, mantendo a mudança local.
4. Rode os testes, `claude plugin validate .` e `node scripts/conferir-ferramentas.mjs CAMINHO_DO_WEBAPP`.
5. Atualize a tabela de fontes com o commit novo.
