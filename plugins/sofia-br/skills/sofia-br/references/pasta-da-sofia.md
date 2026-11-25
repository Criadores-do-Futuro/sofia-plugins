# A pasta da Sofia

A Sofia guarda o trabalho numa pasta que a pessoa escolhe. Sem acesso a arquivos (no app do Claude no navegador, no ChatGPT sem arquivos), nada fica guardado: entregue cada resultado num bloco só, pronto para copiar, e diga que não foi salvo.

## Escolher a pasta

- Pergunte onde salvar só se ainda não houver uma pasta escolhida nesta conversa. Sugira `Sofia/` dentro da pasta em que a pessoa trabalha.
- Nunca grave dentro da pasta de instalação do plugin: ela é trocada a cada atualização.
- Não procure a pasta pelo computador inteiro. Use a que a pessoa disse.
- Antes de criar uma pasta, diga onde ela vai ficar.

## O que fica onde

```
Sofia/
  videos/<titulo-do-video>.md        o card de cada vídeo
  bolhas/<bolha>.md                  vocabulário, o que mexe, comentários e referências da bolha
  perfis/<perfil>.md                 "Como trabalhar", intenção de comando, o que funcionou
  estilos/<perfil>.md                o resumo da voz (fluxo voz)
  referencias/<assunto>/<video>.md   vídeos de referência com o molde
  conhecimento/<assunto>.md          achados com fonte que servem a outros vídeos
  Analises/                          análises e o painel (fluxo painel)
  Exportacoes/                       o que a pessoa pediu para exportar
  aprendizados/padroes-aprendidos.md padrões que a pessoa aprovou guardar
```

Nomes em português, em letras minúsculas, sem espaço (use hífen). Datas no formato `AAAA-MM-DD`. Se a pessoa já tem outra organização, siga a dela.

## O card do vídeo

O card é a memória curta de um vídeo. Um arquivo por vídeo, com estas seções, na ordem. Seção vazia fica com "(a fazer)".

```markdown
# {título do vídeo}

Etapa: {Ideia | Estrutura | Hook | Roteiro | Lapidar | Gravar | Gravado | Postado}
Perfil: {perfil}
Bolha: {nome da bolha}
Para quem: {quem a pessoa quer como cliente}
Assunto: {em poucas palavras}

## Ideia
{a frase do vídeo}
Semente ({pilar}): {a frase}
Formato: {formato} · Estrutura: {estrutura} · Elementos: {elementos e onde aparecem}

## Pesquisa
### Fatos-chave · Contexto · Crenças erradas · Curiosidades · Casos reais · Citações
- {achado} · tipo: {tipo} · acesso: {assistiu | leu | print | só link} · data: {data} · ressalva: {…} · fonte: {link}
### Comentários da bolha
- {comentário como foi escrito} · {curtidas} · {link do vídeo}
### Não verificado
- {o que não se confirmou e por quê}

## Estrutura
1. {bloco}: {tópicos curtos ligados aos achados}

## Hook escolhido
Fala: {…} · Texto na tela: {…} · Abertura: {…} · Estilo de gravação: {…}

## Versões
### Versão {n} ({data}){, nasceu da versão m}{, escolhida}
{roteiro}

## Grifos da versão {n}
| Nº | Trecho | Tipo | Por que mudar | Sugestão | Resposta |

## Lista de gravação
{cena, fala, o que mostrar, onde gravar; no fim, o texto corrido para o teleprompter}

## Recusas
{ideias, hooks e estilos que a pessoa recusou, para não voltarem}
```

## Regras

- Leia o card antes de mexer: a pessoa pode ter editado à mão. O que ela mudou fica, e a versão mais nova pode ser dela.
- Versão nova nunca apaga a antiga. Ajuste vira versão nova, com "nasceu da versão m".
- Nunca marque como gravado ou postado sem a pessoa pedir.
- Comentário guardado sem @ nem nome de quem escreveu. Transcrição inteira de vídeo de terceiros não vai para uma pasta que a pessoa vai compartilhar.
- Exportar um resultado não autoriza reorganizar a pasta nem publicar os arquivos.

## Cofre do Obsidian

Se a pasta escolhida for um cofre do Obsidian, preserve a estrutura e os campos de metadados que o cofre já usa. Não traduza campos que sejam identificadores de integrações existentes. Quando um roteiro estiver pronto para gravar, ou quando pedirem a lista, mostre a pasta uma vez e o nome exato de cada arquivo sem `.md`, para abrir no seletor rápido.

## O que gravar primeiro

Quando a pessoa pedir para ver ou priorizar o que está pronto para gravar, ordene assim:

1. Notícia com prazo de validade, ou roteiro com fato que muda. Diga quantos dias se passaram desde a pesquisa. Passou de 5 a 7 dias, avise que pode estar defasado e pergunte se grava assim ou se atualiza os fatos antes.
2. Roteiro que termina num convite para comentário ou mensagem, ligado a uma dor de venda que a pessoa vive agora. Pergunte qual é a dor do momento se não souber.
3. Conteúdo sem prazo (educativo, comparação), que espera sem pressa.
