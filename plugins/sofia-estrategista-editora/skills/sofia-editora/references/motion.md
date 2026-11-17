# Motion e animação

Use motion e 3D quando servirem à história ou forem pedidos. Trechos animados
podem explicar uma ideia dentro de um vídeo gravado; uma peça inteira também
pode ser animada por código, sem usar geração de vídeo paga. O roteiro e o
formato Sofia determinam o papel de cada visual; a preferência do usuário vence
presets genéricos. No formato dinamismo treinado, não acrescente motion ou trilha
por padrão. Consulte referências locais de JavaScript/3D e suas licenças.

Priorize texto, lettering, formas, keyframes e outros elementos nativos editáveis
quando o editor e sua integração suportarem o efeito. Quando não suportarem,
uma animação JavaScript ou 3D pode ser preparada como mídia e importada em pista
própria, se o pedido permitir; o projeto da animação deve permanecer disponível.
Um clipe importado é achatado: seus elementos internos não viram camadas
editáveis automaticamente. Explique essa diferença antes de depender dela.

Vídeo integral gerado por IA exige os modelos, credenciais e aprovações de custos
aplicáveis. Assets gerados são organizados na timeline escolhida. Acompanhe
progresso e reutilize resultados; não gere novas versões apenas por uma mudança
de texto ou por teste de conexão. Busque imagens, sons e referências com fonte
e licença rastreáveis quando ajudarem a história.

O objetivo é revisar a timeline e fazer ajustes rapidamente. Prévia ao vivo,
geração dentro do editor e atualização de animação sem render dependem da função
realmente disponível em cada integração: não são garantidas pelo planejamento.
Uma alteração em código pode exigir novo render e substituição do clipe. Nunca
afirme que o usuário viu uma mudança em tempo real sem observá-la no editor.

## Prévia antes do render

Para motion em JavaScript baseado em Canvas, use o fluxo documentado em
`motion/README.md`: crie e ajuste o projeto, abra a prévia, registre a revisão
do projeto, renderize e importe o MP4 na timeline escolhida. O registro é
invalidado caso os arquivos mudem após a revisão. Guarde o projeto original
para futuras alterações e confirme a inserção do MP4 pelo adaptador real do
editor. Esse renderizador não produz áudio nem transparência; adicione áudio
na timeline e verifique qualquer necessidade de canal alfa antes de escolhê-lo.
