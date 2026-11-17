# Dados locais e distribuição

As regras de `.gitignore` reduzem o risco de adicionar gravações, imagens,
transcrições, credenciais e outros dados locais ao repositório. Arquivos que já
estão rastreados continuam rastreados, mesmo quando passam a combinar com uma
regra; regras de ignore não apagam o histórico nem inspecionam o conteúdo.
Confira `git status` e o conteúdo staged antes de cada commit. Arquivos de
imagem intencionalmente distribuíveis exigem inclusão explícita e revisão.

A pasta `motion/` é um pacote npm privado. Seu `package.json` lista os arquivos
exatos que pode empacotar; `motion/.npmignore` adiciona exclusões. A regra na
raiz `.npmignore` só se aplica se um pacote npm for criado ali. Confira o
resultado com `npm pack --dry-run --json --ignore-scripts` na pasta `motion/`.
Nunca publique ou remova `private` sem uma decisão explícita.

`.cloudignore` é um inventário preventivo de exclusões: não há garantia de que
uma ferramenta de nuvem reconheça esse nome. Confira a documentação e o
conjunto efetivamente enviado de cada serviço; use seus mecanismos próprios de
exclusão e permissões. Nem esse arquivo nem `.npmignore` bloqueiam o upload
manual ou o processamento por ferramentas que não os leiam.

A biblioteca de estilos e os manuais podem conter dados pessoais ou caminhos de
origem. Guarde-os fora do repositório ou nas pastas locais ignoradas; nomes
arbitrários de arquivos JSON não são classificados automaticamente como privados.
Nunca coloque senhas, tokens ou credenciais em exemplos, registros ou prompts.
