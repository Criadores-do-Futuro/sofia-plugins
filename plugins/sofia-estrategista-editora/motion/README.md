# Motion em JavaScript: criar, revisar e renderizar

Este fluxo produz um clipe MP4 de uma composição Canvas/JavaScript. Uma prévia no navegador permite reproduzir e procurar trechos **antes** de renderizar; o registro de revisão fica vinculado ao conteúdo integral do projeto. Depois da renderização, importe o MP4 para uma pista no editor escolhido usando a integração disponível. O código e os assets originais continuam editáveis no projeto, mas o MP4 é achatado e não preserva suas camadas na timeline. Alterações exigem nova revisão e renderização.

Requisitos: Node.js, FFmpeg/ffprobe, Google Chrome (ou `CHROME_PATH`/`--chrome` com seu executável) e `npm ci --prefix motion`. O resultado é H.264 com fundo opaco, sem faixa de áudio nem transparência; adicionar áudio na timeline. O código pode usar bibliotecas locais como Three.js, conservadas no projeto, desenhando o resultado em Canvas; compatibilidade com cada composição 3D precisa ser verificada. A sincronização de assets externos ou fontes de rede não é congelada pelo hash: para uma revisão reproduzível, coloque tudo no projeto e use caminhos locais. Arquivos de mídia ou bibliotecas grandes dentro do projeto também serão incluídos no hash. Links simbólicos são recusados.

Na raiz do repositório:

```sh
node motion/bin/motion.mjs init --projeto /caminho/animacao
# Edite motion.json e animation.js. A função drawMotion(ctx, t, largura, altura)
# recebe o tempo em segundos e deve desenhar o quadro correspondente de modo determinístico.
node motion/bin/motion.mjs preview --projeto /caminho/animacao
# Abra a URL local exibida e revise o movimento. Encerre a prévia com Ctrl+C.
node motion/bin/motion.mjs approve --projeto /caminho/animacao --registro /caminho/revisao.json
node motion/bin/motion.mjs render --projeto /caminho/animacao --registro /caminho/revisao.json --saida /caminho/animacao.mp4
```

O registro é uma declaração de revisão; o software não consegue verificar se uma pessoa assistiu. O comando `approve` não substitui uma revisão visual. A aprovação e o MP4 precisam estar fora do diretório do projeto e nunca sobrescrevem arquivos existentes. Uma alteração em qualquer arquivo do projeto invalida o registro: revise de novo e crie outro registro. A saída informa caminho, hash e duração efetiva, para localizar a mídia e inseri-la na timeline. Criar o arquivo não significa que ele foi importado para CapCut ou DaVinci; confirme isso no editor.

O template inicial é apenas uma demonstração, não uma direção de arte. Crie a composição de acordo com o roteiro, o método Sofia e as preferências do usuário. A prévia visual não equivale a uma verificação criativa e técnica da timeline final; revise enquadramento, tempo, áudio e sincronização também depois da importação.
