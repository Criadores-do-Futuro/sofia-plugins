# Fluxo: painel da análise

Quando usar: "monta um painel", "dashboard", "quero ver tudo junto", ou uma análise de dois vídeos ou mais quando a sessão cria arquivos.

Leia antes: `comportamento` e `fluxos/analisar`. O painel mostra só o que a análise observou.

## Onde mostrar

- Num app que mostra páginas na conversa (Artifacts, Canvas), crie a página da análise ali.
- Com acesso a arquivos, escreva um único arquivo HTML em `Analises/painel.html` na pasta da Sofia. Se a pessoa pedir um arquivo separado, use `Analises/<titulo-do-lote>/index.html`.
- Sem nenhum dos dois, entregue a análise em texto, com três achados principais.

## Regras do arquivo

- Um arquivo autocontido, sem scripts e sem recursos externos: `lang="pt-BR"`, a meta de viewport e a Content-Security-Policy `default-src 'none'; img-src 'self' data:; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'`.
- Escape todo texto externo (transcrições, comentários, títulos). Nada de texto externo dentro de código executável.
- Abaixo do título, uma linha diz que só entram dados observados e que métricas ausentes aparecem como indisponíveis. Não use dados de demonstração.
- Imagens só as que existem na pasta, com caminho relativo. Nada de serviço de rastreamento. Não publique o arquivo.

## O que entra

- **Lote (dois vídeos ou mais), no topo:** visão geral, tabela de números lado a lado, ranking das aberturas, o padrão em comum e a principal coisa que mudou.
- **Cada vídeo:** título, link original, diagnóstico, nota de 0 a 10 e explicação da abertura, números, roteiro anotado frase a frase, comentários (só o texto e as curtidas), aprendizados e limitações.
- **Com os quadros vistos:** quadros com o segundo, linha do tempo e a relação entre imagem e fala. Só quadros que você abriu; amostra nunca vira o vídeo inteiro.
- **Sem os quadros:** a capa, se você viu, e nenhum bloco de quadro.
- **Limitações (obrigatório):** o que ficou de fora e como fechar.

## Atualizar

Um pedido gera um painel. Ao atualizar `Analises/painel.html`, mantenha as análises que já existem e acrescente ou atualize os vídeos pelo link. Não repita o mesmo vídeo.

## Conferir e entregar

Confira se o arquivo abre, se os dados são os mesmos da análise e se os links e as imagens existem. Mostre onde o arquivo ficou e, na conversa, só um resumo com os três achados principais. Não diga que publicou.
