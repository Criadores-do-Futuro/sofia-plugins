# Sofia Estrategista

A Sofia Estrategista do curso Criador Estrategista, dos Criadores do Futuro, agora também editora de vídeo. Um plugin só, para o Claude e para o Codex, que junta:

- **a Sofia Estrategista:** o método do curso inteiro (princípios da viralização, elementos viciantes, formatos, estruturas, hooks, pesquisa com fonte, roteiro, grifos, análise de vídeo e de perfil) e o conector que lê e salva no planejamento da pessoa no site;
- **o bEditor Estrategista:** edição na timeline do CapCut ou do DaVinci Resolve, aprendizado de estilo a partir de um vídeo já editado, biblioteca de estilos, plano editorial validado e motion;
- **o bEditor original:** guia de edição do diretor, decupagem com revisão, corte de silêncio e de erro, motion graphics em Remotion e no estilo editorial `motion-vox`, cama musical, legenda, master, QA medido, branding do canal, painel de revisão e preparo da publicação.

O mesmo método que escolhe o formato, a estrutura e o hook decide o corte, a imagem, a legenda e o som.

## O que vem no plugin

| Parte | O que é |
|---|---|
| Skill `sofia-estrategista` | Ideia, pesquisa, formato, estrutura, hook, roteiro, grifos, análise de vídeo e de perfil, com e sem o conector |
| Skill `sofia-editora` | Edição na timeline, aprendizado de estilo, biblioteca de estilos e motion |
| Skill `beditor` | Decupagem, guia de edição, montagem, motion graphics em Remotion, finalização, QA e publicação (o bEditor original) |
| Skill `motion-vox` | Motion graphics no estilo editorial de papel e legenda queimada sobre um clipe vertical já cortado |
| Atalhos da Sofia | `roteiro`, `ideias`, `pesquisa`, `analisar`, `critica`, `conectar`, `editar`, `aprender-edicao` e `estilos` |
| Atalhos do bEditor | `setup`, `dirigir`, `cortar`, `motion-graficos`, `finalizar`, `publicar`, `montar`, `plano`, `motion`, `aprender-motion`, `editar-analise`, `qa`, `branding` e `painel` |
| Ajudantes (Claude Code e Cowork) | `pesquisador` (fonte primária), `critico` (primeira leitura do roteiro), `analista-de-edicao` (lê as pranchas de quadros de uma referência), `diretor` (guia de edição de um take), `enriquecedor` (confere os fatos marcados no guia) e `analista-de-estilo` (lê as folhas de contato de um estilo de motion) |
| Conector | Sofia Estrategista, em `.mcp.json` |
| Painel (só no Claude Code) | `hooks/register.tsx`: um painel ao lado da conversa com os cards de cada etapa do planejamento, o @ do perfil e o uso das janelas de 5 horas e de 7 dias do Claude, com quanto falta para zerar. Abre sozinho no início da sessão e pelo comando `/sofia-painel`. No site, no app de conversa e no Codex, fica parado |
| Ferramentas | `scripts/` e o pacote Python `beditor/` (medição, pranchas, transcrição, biblioteca, plano editorial, pontes do CapCut e do DaVinci), `schemas/`, `motion/`, os scripts das skills `beditor` e `motion-vox`, o `painel/` de revisão e as fontes livres (OFL) do motion |

## O que a Sofia faz na edição

1. **Do card ao corte.** Lê o card do planejamento (formato, estrutura, hook, roteiro escolhido), entende o bruto (inventário, transcrição, erros, respiros, pranchas), monta um plano editorial por momento, valida, monta no editor escolhido e confere o projeto salvo contra o plano.
2. **Aprender a editar com um vídeo editado.** Mede cada quadro decodificado e cada trilha de áudio, gera pranchas com todos os quadros, transcreve com tempo por palavra e lê a edição bloco a bloco: cortes e ritmo, J-cut e L-cut, enquadramento, zoom e movimento, transições, legenda, lettering, imagens de apoio, cor, som, abertura e fim. Cada regra do guia tem evidência de tempo e diz se foi medida, inferida ou se não deu para saber. O guia vai para a biblioteca, com versões, e é aplicado nos próximos brutos.
3. **Estilos.** Lista, carrega e versiona os guias guardados. Estilo salvo nunca é usado como se a pessoa tivesse escolhido.
4. **Motion.** Cria, mostra a prévia, registra a revisão, renderiza e importa o clipe numa pista própria.
5. **Take a take, em etapas aprovadas.** `dirigir` (guia), `cortar` (decupagem), `motion-graficos`, `finalizar` (cama, legenda, grade e master) e `publicar` (título, descrição, capa e agendamento). Cada etapa entrega algo para a pessoa ver antes da seguinte. Detalhes em [docs/beditor-motion.md](docs/beditor-motion.md).

## Regras do produto

- A montagem, o texto, a legenda, o som, os efeitos e a revisão final vivem na timeline do editor escolhido. Os scripts medem, preparam e conferem; não trocam a timeline por um MP4 montado fora.
- Projeto editável salvo e vídeo exportado são entregas diferentes. Exportar, publicar e marcar o card como gravado ou postado só com pedido da pessoa.
- Geração de vídeo, imagem ou voz e coletor pago só com OK, depois de dizer o que vai gerar e quanto custa.
- Medição de quadro não reconhece efeito, fonte, máscara nem intenção. O que vem da leitura das pranchas fica como hipótese quando não há prova.
- Preferência da pessoa só é guardada com o OK dela.

## Instalar

O repositório é privado: quem instala precisa de acesso ao GitHub.

**Claude Code**

```sh
claude plugin marketplace add bento-dev-ia/sofia-estrategista-editora
claude plugin install sofia-estrategista-editora@sofia-editora
```

Depois, `/mcp` para entrar no conector Sofia Estrategista com o e-mail do curso. Para testar um checkout: `claude --plugin-dir "CAMINHO_DO_REPOSITORIO"`.

**Claude no navegador ou no app**

`scripts/empacotar.sh` gera `dist/sofia-estrategista-editora.zip`, com o plugin dentro da pasta `sofia-estrategista-editora/`. Envie o `.zip` em Personalizar › Plugins › Adicionar › Enviar plugin e conecte o conector na aba Conectores do plugin. O método e o conector funcionam ali. A edição precisa de um computador com Python, FFmpeg e o editor aberto, então depende do que o host oferece.

**Codex**

```sh
codex plugin marketplace add bento-dev-ia/sofia-estrategista-editora
codex plugin add sofia-estrategista-editora@sofia-editora-local
```

O catálogo é `.agents/plugins/marketplace.json`. Com o `.zip` do kit, descompacte e aponte para a pasta:

```sh
unzip sofia-estrategista-editora.zip
codex plugin marketplace add ./sofia-estrategista-editora
codex plugin add sofia-estrategista-editora@sofia-editora-local
```

O caminho pelo `.zip` foi testado num perfil limpo do Codex CLI 0.160.0; o caminho pelo GitHub depende de acesso ao repositório privado.

Os detalhes por ferramenta estão em [docs/instalacao-e-compatibilidade.md](docs/instalacao-e-compatibilidade.md).

## O que precisa no computador para editar

- Python 3.10 ou mais novo, FFmpeg e ffprobe.
- `yt-dlp` para baixar referência por link; Whisper com um modelo `.pt` já baixado para transcrição local.
- `pip install -r requirements-editorial.txt` para validar o plano editorial; `requirements-capcut-desktop.txt` para a ponte do CapCut Desktop.
- Node, Chrome e `npm ci --prefix motion` para motion.
- Para as skills `beditor` e `motion-vox`: `pip install -r requirements-motion.txt`, e o `/sofia-estrategista-editora:setup` confere o resto e diz o comando de cada item que falta.
- O editor: o plugin oficial do CapCut no host (CapCut Web), a ponte local (CapCut Desktop) ou o MCP do DaVinci Resolve com o Resolve aberto.

A biblioteca de estilos fica na pasta de `BIBLIOTECA_ESTILOS_RAIZ`. Aponte para um disco com espaço: pranchas e análises de vídeo longo crescem rápido.

## Conferir antes de publicar uma versão

```sh
python3 -m unittest discover -s tests -v
claude plugin validate .
node scripts/conferir-ferramentas.mjs CAMINHO_DO_WEBAPP  # checkout na branch que vai para produção
scripts/empacotar.sh
```

`conferir-ferramentas.mjs` acusa quando o plugin cita uma ferramenta do conector que o servidor não tem.

## Documentação

- [De onde veio cada parte](docs/origens.md)
- [Instalação e compatibilidade](docs/instalacao-e-compatibilidade.md)
- [Contrato editorial e validação](docs/contrato-editorial.md)
- [Análise de estilo](docs/analise-de-estilo.md) e [enriquecer o manual](docs/enriquecer-manual-estilo.md)
- [Baixar referência](docs/download-referencia.md) e [transcrição local](docs/transcricao-local.md)
- [CapCut Web](docs/ponte-capcut-web.md), [CapCut Desktop](docs/ponte-capcut-desktop.md) e [DaVinci Resolve](docs/ponte-davinci.md)
- [Arquitetura](docs/arquitetura.md), [plano e critérios](docs/plano.md), [referências técnicas](docs/referencias-tecnicas.md)
- [Proteção de arquivos e distribuição](docs/seguranca-distribuicao.md)
- [bEditor: motion, decupagem, finalização e publicação](docs/beditor-motion.md) e o [manual interativo](docs/manual.html) que o setup preenche
- [Enviar aos diretórios da Anthropic e da OpenAI](docs/diretorios.md)

## O que o plugin roda, envia e baixa

**Roda no computador**, só quando a pessoa pede a etapa: Python 3, FFmpeg e ffprobe, Whisper local (mlx-whisper ou faster-whisper), OpenCV, Node com Remotion e Chrome para o render de motion, `xcrun swiftc` no macOS para compilar o recorte de pessoa (Vision), e um servidor de prévia só em `127.0.0.1`.

**Instala só com o sim da pessoa:** `setup.py --instalar` e `--atualizar` mostram os comandos (`brew`, `pip`, `git pull --ff-only` num clone, `claude plugin install`) e só executam com `--sim`.

**Envia**, sempre com a conta e a escolha da pessoa:

- ao conector Sofia Estrategista (`https://plataforma.criadorestrategista.com.br/api/mcp`), depois do login: o que ela pede para ler ou salvar no planejamento, no cérebro e nas referências;
- à API Gemini do Google, só com a chave `GEMINI_API_KEY` da própria pessoa: os prompts das imagens geradas;
- ao Zernio ou ao Metricool, só com o sim a cada publicação: vídeo, capa, título e descrição do post;
- ao CapCut e ao DaVinci Resolve, pelas ferramentas dos próprios fornecedores: a montagem na timeline.

**Baixa:** vídeo público pelo link que a pessoa der (`yt-dlp`, sem cookies nem login); modelos de visão na primeira vez (OpenCV Zoo no GitHub e MediaPipe no Google Cloud Storage); fontes do Google Fonts e a GSAP do jsDelivr nas prévias em HTML; pacotes npm do `motion/` com `npm ci`; os pacotes do projeto de motion da skill `beditor` com `npm install` (`scripts/projeto.sh`, versões fixas no `package.json` do modelo); e o CLI de render `hyperframes@0.9.58` da HeyGen pelo `npx`, só nas etapas de motion e legenda que o usam (a variável `BEDITOR_HYPERFRAMES` troca a versão).

**Lê no computador**, só quando a pessoa roda: `custos.py` e `painel/telemetria.py` leem os registros de sessão do Claude Code (`~/.claude/projects`) para somar tokens e tempo por etapa. O resultado fica num arquivo local.

Nada é enviado para a Criadores do Futuro além do que passa pelo conector. Não há telemetria.

## Privacidade, termos e suporte

O conector só funciona para alunos do curso, depois do login. Vídeos, transcrições, pranchas e guias de estilo ficam no computador de quem usa; o plugin nunca copia nem altera o vídeo original.

| | Português | Español | English |
|---|---|---|---|
| Privacidade | [privacidade](https://plataforma.academiacriadoresdofuturo.com.br/sofia-editora/privacidade) | [privacidad](https://plataforma.academiacriadoresdofuturo.com.br/sofia-editora/privacidad) | [privacy](https://plataforma.academiacriadoresdofuturo.com.br/sofia-editora/privacy) |
| Termos de uso | [termos](https://plataforma.academiacriadoresdofuturo.com.br/sofia-editora/termos) | [términos](https://plataforma.academiacriadoresdofuturo.com.br/sofia-editora/terminos) | [terms](https://plataforma.academiacriadoresdofuturo.com.br/sofia-editora/terms) |
| Suporte | [suporte](https://plataforma.academiacriadoresdofuturo.com.br/sofia-editora/suporte) | [soporte](https://plataforma.academiacriadoresdofuturo.com.br/sofia-editora/soporte) | [support](https://plataforma.academiacriadoresdofuturo.com.br/sofia-editora/support) |

## Licença

Pode baixar, instalar e usar para criar o seu conteúdo ou o de clientes. Redistribuir, revender ou publicar cópias não é permitido. Veja [LICENSE](LICENSE).
