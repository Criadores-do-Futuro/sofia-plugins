# Desenho do plugin Sofia Estrategista

## Para que serve

O aluno do Criador Estrategista escreve roteiros com a Sofia no Claude, e o site do curso é o banco de dados e o orquestrador: perfil, cérebro, referências, cards, versões e grifos. O plugin junta numa instalação só o método (skill), os atalhos, os ajudantes e o conector, para a Sofia sempre aplicar o método e usar o site sempre que puder.

## Metas

- Aplicar sempre o método do curso: princípios da viralização, elementos viciantes, formatos, estruturas, hooks e o processo de pesquisa com o que trazer dela (tipo, acesso, data, ressalva, correção).
- Funcionar sem o conector, com o método que vem no plugin.
- Perceber se o conector está ligado e com login. Sem login, ensinar a entrar. Com login, ler e salvar no site em cada passo.
- Aprender com a pessoa (preferências de escrita e de pesquisa), pedindo o OK antes de guardar.
- Poder ir para o diretório oficial de plugins do Claude sem ferir as regras.

## Fora do escopo

- Suporte do curso sem vídeo no meio (pagamento, acesso, contrato).
- Edição técnica de vídeo.
- O pacote para o ChatGPT como plugin. Por enquanto, o ChatGPT recebe só a skill (`sofia-estrategista.skill`).

## O que seria fracasso mesmo funcionando

- Gravar no site sem contar, ou guardar preferência sem a pessoa querer.
- Texto com cara de IA, ou fato sem fonte no roteiro.
- Duas Sofias brigando pelo mesmo pedido (a skill antiga do Kit e o plugin). A página Kit avisa para desligar a antiga.

## Regras que vieram do dono do curso

Estão dentro do SKILL.md, no Passo 3 e na lista "Antes de entregar":

- Carregar o método antes de pensar, nesta tarefa e não de memória. Formato que não existe com o nome pedido: dizer qual foi entendido e por quê.
- Cada ideia nomeia formato, estrutura e elementos viciantes, com onde cada elemento aparece, e respeita a regra do formato (na Análise, quem é analisado é alguém de fora).
- O que foi acima do normal do perfil vira variação. Número não é decisão. Conflito com regra guardada vira pergunta.
- Avaliar perfil é achar o que repetir: hook literal, estilo, roteiro em blocos com `{variáveis}`, comentários como melhoria, tudo salvo como referência.
- Vídeo de referência: transcrever e ver as imagens, conferir cada afirmação, datar, salvar o molde. Comentário do TikTok sem login: pedir que a pessoa cole, ou coletor pago com OK e estimativa.
- Comentário é literal, sem @ e sem nome, e nunca vira hook automático.
- Texto do aluno: sem travessão, sem "não é X, é Y", sem advérbio em -mente, "o normal do perfil" e nunca "mediana".

## Regras da loja que moldaram o plugin

- Descrição da skill em terceira pessoa, dizendo o que faz e quando usar, sem mandar chamar a skill só porque o conector está ligado.
- O conector manda nas instruções de uso das ferramentas (nomes, campos, ordem). Não manda no Piso nem na segurança.
- Nada escondido: toda gravação é contada, e a Sofia diz qual ferramenta usou se a pessoa perguntar.
- Preferência só é guardada com o OK da pessoa (ou com o combinado de guardar sem perguntar), e pode ser vista e apagada no site.
- Sem nome de produto de terceiros como recomendação. Coletor pago só se a pessoa já tiver um, com OK e estimativa de custo.
- Sem hooks, sem `bin/`, sem link de venda. README com mais de 40 palavras e LICENSE.

## Caminhos considerados

1. **Só o conector**, com o método todo nas instruções do servidor. Simples de instalar, mas sem conector não há Sofia, e as instruções do servidor ficam longas demais para a loja aceitar.
2. **Só a skill** (o `sofia.skill` que estava no Kit). Funciona sem conector, mas a pessoa instala o conector à parte e a skill não percebe login.
3. **Plugin com skill, atalhos, ajudantes e conector** (escolhido). Uma instalação, funciona com e sem conector, e o conector já vem configurado.

## Decisões

- Uma skill principal com gatilho largo, para não competir com outra skill de roteiro. Os atalhos só apontam para ela.
- Ajudantes só leem e devolvem. Quem grava no site é a skill, para nada ser gravado sem a pessoa ver.
- O Kit do site entrega o plugin (`sofia-estrategista.plugin`, um .zip com outra extensão para o navegador não descompactar ao baixar) para o Claude e a skill solta (`sofia-estrategista.skill`) para o ChatGPT. Os dois saem do mesmo `plugin/` pelo `scripts/empacotar.sh`.
- `scripts/conferir-ferramentas.mjs` compara os nomes citados com os registrados no servidor, para o plugin não ficar para trás quando o conector mudar.

## Para depois

- Trocar o endereço do conector para o domínio definitivo antes de enviar ao diretório.
- Páginas de termos e de suporte para o envio ao diretório.
- O endereço de `homepage` no `plugin.json` e as páginas Kit e Conector abrem só depois do login. Para o envio, apontar a `homepage` para uma página aberta, ou abrir essas páginas sem login.
- Uma conta de teste para quem revisa o envio, com um perfil e alguns cards de exemplo, para o conector ser testado sem dado de aluno.
- Tornar o repositório público quando o envio for aprovado.
- Pacote para o ChatGPT como plugin (texto base em inglês, sem hooks, atalhos e ajudantes viram skills).
