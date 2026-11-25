# Sofia

A Sofia é uma estrategista de vídeo curto (Reels, TikTok, Shorts) que trabalha em português do Brasil. Ela ajuda o criador a ter ideias, pesquisar com fonte, escolher formato e estrutura, escrever hook e roteiro, criticar e lapidar com grifos, melhorar um roteiro, analisar vídeos e perfis de referência e aprender a voz de quem escreve. Tudo pelo mesmo método: princípios da viralização, elementos viciantes, formatos de gravação, estruturas de roteiro, furar a bolha e intenção de comando.

O plugin é só texto: uma skill (`sofia-br`) com o método e os fluxos, e os agentes da equipe para o Claude Code. Não tem script, executável nem servidor próprio.

## Instalar

No Claude Code, adicione o catálogo e instale:

```sh
claude plugin marketplace add Criadores-do-Futuro/sofia-plugins
claude plugin install sofia-br@sofia-plugins
```

No Codex e no ChatGPT, use o catálogo do repositório ou o pacote enviado ao diretório de plugins. Os arquivos `.claude-plugin/plugin.json` e `.codex-plugin/plugin.json` descrevem a mesma versão.

Depois, é só pedir: "me dá ideias de vídeo sobre…", "escreve um roteiro sobre…", "me dá hooks para…", "critica esse roteiro", "analisa esse vídeo", "aprende meu jeito de falar". No Codex e no ChatGPT, também dá para chamar `$sofia-br`.

## Fluxos

| Fluxo | O que faz |
|---|---|
| Preparar | Escolhe a pasta onde salvar, confere o que a sessão tem e monta o perfil (voz, intenção de comando, "como trabalhar") |
| Ideias | Brainstorm de 3 a 5 ideias, cada uma com formato, estrutura, elementos viciantes, bolha e semente |
| Pesquisa | Fatos em fonte primária, marcados por tipo, acesso, data e ressalva, e a pesquisa da bolha (vocabulário e comentários mais curtidos) |
| Roteiro | Formato e estrutura, de 8 a 10 hooks conferidos (mostra de 3 a 5), versões do roteiro com zona de fixação, semente e lista de gravação |
| Crítica | Grifos (cortar, trocar, reforçar, dúvida) com o princípio de cada um, ou o veredicto curto de um roteiro solto |
| Melhorar | Ajuste só no trecho pedido, ou a reescrita inteira preservando o que funciona |
| Analisar | Vídeo ou perfil de referência, frase a frase, com o que dá para repetir e as limitações do que foi visto |
| Voz | Aprende o jeito de falar da pessoa (ou de cada cliente) a partir de amostras |
| Painel | Junta a análise de vários vídeos numa página |
| Exportar | Salva resultados e guarda aprendizados, só com o OK da pessoa |

Regras que valem em tudo: nada inventado (fato, número e caso só com fonte aberta), nenhum texto com cara de IA (sem travessão, sem "não é X, é Y", sem advérbio em -mente) e comentário do público guardado como foi escrito e usado no roteiro como fala do próprio criador.

## Agentes (Claude Code)

No Claude Code, cada papel da equipe é um agente: escrever fica separado de conferir.

- Escrevem: `estrategista-de-ideias`, `especialista-em-bolha` (propor), `pesquisador`, `redator-de-hook`, `roteirista`, `melhorador`.
- Conferem: `revisor-o-que-nao-fazer`, `revisor-de-hook`, `revisor-de-voz`, `especialista-em-bolha`, `revisor-de-estrutura`, `revisor-de-fatos`, `critico`.
- Analisam e aprendem: `analista-de-principios`, `aprendiz`.

Os agentes só leem e devolvem; quem guarda alguma coisa é a Sofia, com o OK da pessoa. No ChatGPT, no Codex e no Claude do navegador, a mesma equipe roda em passadas, um papel por vez, na própria conversa.

## Ferramentas MCP opcionais

Onde o servidor da Sofia estiver disponível (no ChatGPT e no Codex; no Claude ele pode não existir), a skill usa três ferramentas:

- `list_method_pieces`: lista as peças do método.
- `read_method_piece`: devolve uma peça pelo id (o caminho dentro de `skills/sofia-br/references/`, sem `.md`, por exemplo `knowledge/hooks-que-funcionam`). O nome sozinho também serve quando é único.
- `check_script`: confere um roteiro pronto contra as regras mecânicas de `skills/sofia-br/references/checks.json` e devolve pontos para revisar. São sinais automáticos que podem dar falso positivo, e a ferramenta cobre só parte do Piso. O limite de 15 palavras na primeira frase e as palavras por minuto da estimativa de tempo são referências da ferramenta, não regras do método.

O que o servidor recebe: o texto do roteiro enviado ao `check_script` e o id da peça pedida. Ele não guarda nada e não pede login. Sem o servidor, a Sofia usa as referências locais e confere à mão.

## Serviços externos

Nenhum serviço externo faz parte do plugin, e a Sofia não depende de outro app. Ela trabalha com o que a pessoa traz: texto colado, arquivo, link ou exportação. Se faltar dado de rede social, a Sofia pede o arquivo, a transcrição, a exportação ou prints. Se a própria pessoa pedir para usar uma ferramenta que já tem, a Sofia segue o pedido, dizendo antes o que vai buscar e, se for pago, quanto custa. Ela não lê credenciais da máquina, não pede senha e não contorna login.

## Requisitos

- Nada para escrever, criticar e analisar texto.
- Opcional, com terminal: FFmpeg e ffprobe para ver os quadros de um vídeo local; yt-dlp para baixar um vídeo público com autorização; Whisper para transcrever. A Sofia pergunta antes de instalar qualquer um.
- Sem terminal, a análise de vídeo é de texto (transcrição, legenda, prints), e a Sofia diz quais camadas não viu.

## Onde salva

Na pasta que a pessoa escolher (a sugestão é `Sofia/`, na pasta de trabalho): o card de cada vídeo, as bolhas, o perfil, a voz, as referências e as análises. Nunca dentro da instalação do plugin. Guardar algo sobre a pessoa só com o OK dela. Sem acesso a arquivos, nada é salvo: a Sofia entrega o texto pronto para copiar. Comentários são guardados só com o texto, as curtidas e a data, sem nome nem @ de quem escreveu. Não há telemetria.

## Publicador, privacidade e suporte

Publicado por **Action Criação Digital Ltda (Criadores do Futuro)**.

- [Privacy Policy · Política de Privacidade](https://plataforma.academiacriadoresdofuturo.com.br/sofia/privacidade)
- [Termos de uso](https://plataforma.academiacriadoresdofuturo.com.br/sofia/termos)
- [Suporte](https://plataforma.academiacriadoresdofuturo.com.br/sofia/suporte)
- [Site](https://plataforma.academiacriadoresdofuturo.com.br/sofia)

Licença proprietária: [LICENSE](LICENSE). O trecho adaptado de [stop-slop](https://github.com/hardikpandya/stop-slop), de Hardik Pandya, segue a licença MIT. O aviso completo está no fim da peça `sem-slop`, em `skills/sofia-br/references/sem-slop.md`.
