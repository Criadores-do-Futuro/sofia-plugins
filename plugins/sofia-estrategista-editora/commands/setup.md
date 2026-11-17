---
description: Prepara esta máquina para o bEditor — verifica dependências, pergunta onde ficam as suas pastas, grava ~/.config/beditor/config.json e gera o manual interativo
allowed-tools: Read, Bash, Glob, AskUserQuestion, Artifact
---

Você está instalando (ou conferindo) o bEditor nesta máquina. O script faz o trabalho;
você conduz a conversa. Regra que vale a sessão inteira: **nunca imprima o valor de uma
chave de API** (o script só diz «presente» ou «ausente»; mantenha assim).

1. **Verificar.**
   `python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/setup.py --verificar`
   Mostre a tabela resumida ao usuário: o que está ok, o que falta (com o comando de
   instalação), o que é opcional e para que serve (Remotion só para o fluxo `motion`;
   Swift só para matte de pessoa e enquadramento pelo rosto, macOS; Gemini só para
   geração de imagem). Se `$ARGUMENTS` for `--so-verificar`, pare aqui.

2. **Perguntar as pastas** com `AskUserQuestion`, em grupos de até quatro por vez, uma
   linha explicando cada uma (a descrição está em `DESCRICAO_PASTAS` do `setup.py`):
   `projetos`, `entregas`, `musicas`, `sfx`, `overlays`, `logos`, `midia`, `marcas`, `render`,
   `treinamento`. **`marcas` é opcional**: uma subpasta por marca — a da pessoa e a de
   cada cliente — com manual, cores, fontes e escolhas de motion. Pergunte se ela edita
   para mais de uma marca; para cada uma, `marca.py nova "<nome>"`, e a principal com
   `--padrao`. Projeto de cliente se liga com `marca.py usar <nome> --projeto <pasta>`. **`midia` é a midiateca compartilhada** (vídeo, imagem e áudio de
   terceiro, usados por vários projetos): sem ela configurada, `midiateca.py` para e
   o `analise` não acha o material baixado antes.
   Antes de perguntar, procure padrões e proponha-os como opção: uma pasta já configurada
   no `config.json` (não a troque sem o usuário pedir); `.../bEditor/Biblioteca/Musicas`,
   `.../Biblioteca/SFX`, `.../Biblioteca/Overlays`, `.../Biblioteca/Logos`, `.../Projetos`,
   `.../Entregas` em volumes montados (`ls /Volumes`); `~/.beditor/render` se já for um link.
   Avise que projetos, entregas e render não podem ficar em `~/Documents` nem na Mesa
   (iCloud), e que `render` precisa de caminho sem acento.

3. **Gravar.** `python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/setup.py --pastas projetos=<...> entregas=<...> ...`
   Acrescente `--criar` só quando o usuário pediu para criar a pasta. Se ele informou o
   canal, `--canal nome="<nome>" arroba=<@arroba>`. O script mescla: pastas não citadas
   ficam como estavam. Se `render` não é ainda `~/.beditor/render`, ofereça o `ln -s`.

4. **Instalar o que falta.** `python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/setup.py --instalar`
   imprime os comandos sem rodar. Mostre-os e pergunte. Só com o sim explícito rode
   `--instalar --sim`, e avise antes o que ele vai fazer (brew, pip, compilar Swift).
   Nada que peça senha ou diálogo do sistema roda sozinho: o script os marca como
   `[manual]`, e você os deixa para o usuário. Repita o passo 1 no fim.
   **O `context-mode` entra aqui como qualquer outra dependência** — o `--verificar`
   já o lista no grupo `[claude code]` com o comando pronto. Explique por que vale:
   sem ele, cada pergunta sobre um arquivo custa o arquivo inteiro em tokens; com
   ele, a sessão roda no sandbox e traz só a resposta. Depois de instalar, o Claude
   Code precisa ser reaberto para o plugin carregar.

5. **Gerar o manual.** `python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/setup.py --manual`
   e diga o caminho impresso (padrão `~/.beditor/manual.html`). Ele abre do disco, com
   o estado desta máquina na aba «Saúde».

6. **Mesa e painel desta conta.** `setup.py --artefato mesa` e `--artefato painel`
   imprimem o endereço gravado nesta máquina. Vazio é normal numa instalação nova: o
   primeiro uso de cada um publica o modelo (`painel/mesa.html`, `painel/index.html`)
   na conta da pessoa e grava o endereço. Nunca aponte para artifact de outra conta —
   ele não aceita escrita de quem não é dono.

7. **Atualizar**, quando o pedido for esse e não uma instalação nova:
   `python3 ${CLAUDE_PLUGIN_ROOT}/skills/beditor/scripts/setup.py --atualizar`
   mostra o que faria (`git pull --ff-only` no plugin e `claude plugin update` no
   context-mode); com o sim, `--atualizar --sim`. Se o pull recusar por trabalho
   local, mostre a mensagem do git e pergunte — não force nada.

8. **Oferecer publicar** o manual como artifact. Se o usuário quiser, use a ferramenta
   `Artifact` com o arquivo gerado (ele já começa por `<title>` e `<style>`, sem
   `<html>`/`<body>`). Não publique sem o pedido.
