# Instalação e compatibilidade

Os manifestos e catálogos deste repositório preparam a distribuição privada para o Claude e para o Codex. Eles não provam que tudo funciona em todo host. Instalar o pacote, entrar no conector, conectar o editor e testar uma edição são etapas separadas. O repositório é privado: quem instala precisa de acesso ao GitHub.

## Claude Code

O catálogo é `.claude-plugin/marketplace.json` (marketplace `sofia-editora`) e o plugin é a raiz do repositório.

```sh
claude plugin marketplace add bento-dev-ia/sofia-estrategista-editora
claude plugin install sofia-estrategista-editora@sofia-editora
```

Depois, `/mcp` para entrar no conector Sofia Estrategista. Para desenvolver, carregue um checkout confiável com `claude --plugin-dir CAMINHO_DO_REPOSITORIO`. Confira o manifesto com `claude plugin validate .`.
[Documentação oficial dos marketplaces do Claude](https://code.claude.com/docs/en/plugin-marketplaces).

Se o plugin `sofia-estrategista` (só a estrategista) também estiver instalado, as duas skills `sofia-estrategista` aparecem juntas. Deixe um dos dois plugins instalado. O mesmo vale para o plugin `beditor` antigo: este já traz as skills `beditor` e `motion-vox`, os ajudantes `diretor`, `enriquecedor` e `analista-de-estilo` e os atalhos, agora como `/sofia-estrategista-editora:...` (`aprender` virou `aprender-motion` e `analise` virou `editar-analise`).

Depois de instalar, rode `/sofia-estrategista-editora:setup`: ele confere Python, FFmpeg, Whisper, Node e o resto, e mostra o comando de cada item que falta. Para atualizar: `claude plugin update sofia-estrategista-editora@sofia-editora`.

## Claude no navegador, no app e no Cowork

`scripts/empacotar.sh` gera `dist/sofia-estrategista-editora.zip`, com o plugin inteiro dentro da pasta `sofia-estrategista-editora/` (a forma que o envio aceita: o `.claude-plugin/plugin.json` dentro de uma única pasta no topo do `.zip`). Envie o `.zip` em Personalizar › Plugins › Adicionar › Enviar plugin e conecte na aba Conectores do plugin.

O pacote segue as regras do envio: em `.claude-plugin/` vai só o `plugin.json` (o `marketplace.json` fica no repositório, para instalar pelo GitHub); o ícone fica em `assets/`; o cabeçalho de cada skill e de cada comando usa só os campos aceitos fora do Claude Code (`name`, `description`, `license`, `compatibility`, `metadata` e `allowed-tools`), porque no chat cada comando vira uma skill. `tests/test_pacote.py` confere essas regras, e o `empacotar.sh` roda o `claude plugin validate` na pasta montada antes de fechar o `.zip`.

Se o Safari abrir o `.zip` sozinho ao baixar, baixe de novo pelo Chrome ou desligue a opção de abrir arquivos seguros nos ajustes do Safari. Não comprima a pasta pelo Finder: ele junta a pasta `__MACOSX` ao `.zip`, e o envio deixa de achar o plugin. O método e o conector funcionam em qualquer um desses hosts. A edição usa Python, FFmpeg, os arquivos de vídeo e o editor aberto no computador, então só funciona onde o host dá acesso a eles.

## Codex

O manifesto é `.codex-plugin/plugin.json`, com as skills em `./skills/` e o conector em `./.mcp.json`. O catálogo é `.agents/plugins/marketplace.json` (marketplace `sofia-editora-local`).

```sh
codex plugin marketplace add bento-dev-ia/sofia-estrategista-editora
codex plugin add sofia-estrategista-editora@sofia-editora-local
```

Pelo `.zip` do kit:

```sh
unzip sofia-estrategista-editora.zip
codex plugin marketplace add ./sofia-estrategista-editora
codex plugin add sofia-estrategista-editora@sofia-editora-local
```

O caminho pelo `.zip` foi testado num perfil limpo do Codex CLI 0.160.0: o plugin instala, as quatro skills aparecem e o conector aparece em `codex mcp list` com o endereço do domínio próprio. O caminho pelo GitHub depende de acesso ao repositório privado. Ajudantes (`agents/`) são do Claude. O Codex transforma em skill só os comandos sem argumento (`conectar` e `branding`); no Codex, as quatro skills (`sofia-estrategista`, `sofia-editora`, `beditor` e `motion-vox`) fazem o mesmo trabalho sem os atalhos. O `hooks/hooks.json` só declara o painel do Claude Code (`modules`); no teste, o Codex montou a sessão com o plugin sem aviso nem erro. O manifesto marca `requires_local_executor`, porque a edição precisa do computador: o Codex só oferece o plugin onde há execução local. Inicie uma sessão nova depois de instalar e confira se as skills e o conector aparecem.
[Documentação oficial de plugins do Codex](https://developers.openai.com/plugins/build/plugins).

## ChatGPT e outras ferramentas

ChatGPT na web e no celular, GPTs personalizados e outras IAs não rodam este pacote sozinhos nem herdam conectores de outra sessão. Cada host, o acesso aos arquivos, as ferramentas do editor e o login precisam ser comprovados um por um. Os recursos do CapCut variam por cliente: não prometa edição colaborativa, geração ou legenda automática onde essas operações não existem.

## Dependências e privacidade

- O plugin orienta o agente. Ele não inclui o plugin oficial do CapCut, o DaVinci Resolve nem os conectores deles. Instale e conecte cada um pelo canal do fornecedor.
- As fichas do método vêm no plugin, em `skills/sofia-estrategista/references/`. Com o conector ligado, `sofia_metodo` devolve a versão do site, que vale mais.
- Os scripts usam a biblioteca padrão do Python, com dependências opcionais listadas no README (`requirements-editorial.txt`, `requirements-capcut-desktop.txt` e `requirements-motion.txt`). O README também lista tudo o que o plugin roda, envia e baixa. Eles precisam do plugin inteiro: copiar só um `SKILL.md` não instala as ferramentas.
- Não distribua uma pasta de trabalho com vídeos, transcrições, credenciais, dependências ou arquivos locais sem olhar antes. Git e ignore não limpam arquivo já rastreado nem garantem filtro em todo host.
