# Sofia Português

Analisa vídeos e transcrições, cria e revisa roteiros, aprende a voz do criador e exporta resultados em português brasileiro. As referências necessárias estão no pacote. Não exige um conector de conteúdo.

## Instalar e usar

No Claude Code, adicione o catálogo e instale a versão portuguesa:

```sh
claude plugin marketplace add bento-dev-ia/sofia-plugins
claude plugin install sofia@sofia-plugins
```

No Codex, use o catálogo do repositório em `.agents/plugins/marketplace.json`. Os arquivos `plugin.json` e `.codex-plugin/plugin.json` descrevem a mesma versão. Para envio manual, use o ZIP gerado por `python3 tools/package_plugins.py` a partir da raiz do repositório.

Peça para analisar um arquivo ou transcrição, escrever um roteiro, revisar um texto, aprender seu estilo ou exportar. As habilidades disponíveis são `analisar`, `roteiro`, `critica`, `melhorar`, `setup`, `dashboard` e `exportar`. As respostas e os arquivos produzidos ficam em português.

## Recursos e limites

Vídeo local exige Python 3.10 ou posterior, FFmpeg e ffprobe, além de ferramenta para abrir imagens. O preparador em `scripts/prepare-visual-analysis.py` gera quadros com tempos e áudio quando disponível; não transcreve fala nem reconhece efeitos sozinho. Para texto e roteiros, esses programas não são necessários. Downloads públicos dependem de autorização e de `yt-dlp`; nunca use cookies ou sessão do navegador para contornar login.

Leia [comportamento](comportamento.md) e [análise visual](references/analise-de-video.md). Instalações, serviços pagos e envio a terceiros exigem autorização. O serviço opcional de análise Gemini usa a conta e a chave da pessoa; exige `--allow-upload` e o modelo configurado em `SOFIA_GEMINI_MODEL`. Aprendizados e exportações ficam fora da instalação; não há telemetria própria.

## Distribuição e atendimento

Publicador pretendido: Alef Marques. Compras de assinaturas, comunidades ou cursos ocorrem na Hotmart; este plugin não processa pagamentos nem controla acesso. A verificação de publicador e as declarações legais são feitas no portal.

Os links confirmados estão em `plugin.json`. Uma página de apresentação e a revisão da cobertura dos termos pagos ainda são necessárias para a listagem pública. O relatório de publicação no repositório lista as pendências. Disponibilidade em Claude depende da superfície e de acesso a arquivos; no envio OpenAI, o pacote é marcado para execução local.

Licença proprietária: [licença](LICENSE). A autoria original permanece no manifesto.
