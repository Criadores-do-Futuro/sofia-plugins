# Sofia

Analisa vídeos e transcrições, cria e revisa roteiros, aprende a voz do criador e exporta resultados em português brasileiro. As referências necessárias estão no pacote. Não exige um conector de conteúdo.

## Instalar e usar

No Claude Code, adicione o catálogo e instale a versão portuguesa:

```sh
claude plugin marketplace add bento-dev-ia/sofia-plugins
claude plugin install sofia-br@sofia-plugins
```

No Codex, use o catálogo do repositório em `.agents/plugins/marketplace.json`. Os arquivos `.claude-plugin/plugin.json` e `.codex-plugin/plugin.json` descrevem a mesma versão. Para envio manual, use o ZIP gerado por `python3 tools/package_plugins.py` a partir da raiz do repositório.

Peça para analisar um arquivo ou transcrição, escrever um roteiro, revisar um texto, aprender seu estilo ou exportar. As habilidades disponíveis são `analisar`, `roteiro`, `critica`, `melhorar`, `setup`, `dashboard` e `exportar`. As respostas e os arquivos produzidos ficam em português.

## Recursos e limites

Vídeo local exige FFmpeg e ffprobe, além de ferramenta para abrir imagens. A [análise visual](references/analise-de-video.md) lista os comandos de `ffprobe` e `ffmpeg` que geram quadros com tempos, folhas de contato e áudio quando disponível; eles não transcrevem fala nem reconhecem efeitos sozinhos. O plugin contém só texto: nenhum script ou executável. Para texto e roteiros, esses programas não são necessários. Downloads públicos dependem de autorização e de `yt-dlp`; nunca use cookies ou sessão do navegador para contornar login.

Leia [comportamento](comportamento.md) e [análise visual](references/analise-de-video.md). Instalações, serviços pagos e envio a terceiros exigem autorização. Serviços opcionais, como Apify, YouTube ou Gemini, só são usados por um conector oficial que a pessoa instalou e autorizou; a Sofia não lê chaves da máquina. Aprendizados e exportações ficam fora da instalação; não há telemetria própria.

## Distribuição e atendimento

Publicador pretendido: Alef Marques. Compras de assinaturas, comunidades ou cursos ocorrem na Hotmart; este plugin não processa pagamentos nem controla acesso. A verificação de publicador e as declarações legais são feitas no portal.

Os links confirmados estão em `.codex-plugin/plugin.json`. Uma página de apresentação e a revisão da cobertura dos termos pagos ainda são necessárias para a listagem pública. O relatório de publicação no repositório lista as pendências. Disponibilidade em Claude depende da superfície e de acesso a arquivos; no envio OpenAI, o pacote é marcado para execução local.

Licença proprietária: [licença](LICENSE). A autoria original permanece no manifesto.
