# Aprender a voz da pessoa

## Com o conector ligado

- Leia antes a peça `instrucoes/estilo` do `sofia_metodo`. Ela vale mais que esta página.
- Veja se a voz já está salva: `sofia_meus_videos` diz, e `sofia_perfil` lê o resumo.
- Depois de digerir os roteiros, mostre o resumo da voz e pergunte se pode salvar. Com o OK, salve com `sofia_perfil` e avise onde ela vê. O conector guarda só o resumo da voz (tom, vocabulário, expressões, o que a pessoa evita). O texto dos roteiros que ela mandou fica de fora. Por isso, no conector, a seção "Frases de referência" do modelo abaixo não entra.
- Palavras e expressões que valem para os próximos vídeos também podem ir para o cérebro (`cerebro_guardar`, camada `vocabulario`), com o OK da pessoa.
- Quem atende clientes tem um perfil por cliente no conector, cada um com a sua voz. Confirme o perfil antes de salvar.

## Sem o conector

- **No Claude Code ou em outro terminal com acesso a arquivos:** salve o arquivo de voz na pasta em que a pessoa está trabalhando, em `Sofia/estilos/<perfil>.md`. Use o nome do perfil ou do cliente, em letras minúsculas e sem espaço. Antes de criar a pasta, diga onde ela vai ficar. Não salve dentro da pasta da skill: ela é trocada quando a skill é atualizada.
- **No app do Claude ou em outro chat:** não dá para salvar arquivo. Entregue o resumo da voz num bloco só e peça para a pessoa guardar. Na próxima conversa, ela cola o resumo e você usa.

## Quando oferecer

Na primeira conversa com alguém novo, ou quando não existe voz salva, ofereça:

> "Antes de escrever, quer que eu aprenda o seu jeito de falar? Me manda alguns dos seus melhores roteiros. Eu aprendo o seu tom, as suas palavras e o seu ritmo. Leva uns minutos, e depois todo roteiro sai com a sua cara."
>
> "Você escreve sempre para o mesmo perfil ou tem clientes com estilos diferentes?"

## Se ela escreve para um perfil só

1. Peça de 3 a 5 roteiros que ela considera bons.
2. Analise e salve uma voz só.
3. Use essa voz sempre que escrever.

> "Me manda de 3 a 5 roteiros seus que você gosta. Pode colar aqui ou mandar o arquivo. Vou ler e aprender o seu jeito de escrever."

## Se ela escreve para clientes diferentes

1. Pergunte quais clientes ou perfis existem.
2. Peça roteiros de cada cliente, separados.
3. Salve uma voz por cliente.
4. Antes de escrever, pergunte para qual cliente é, se não estiver claro.

> "Quais são os seus clientes ou perfis? Me conta os nomes, e a gente separa as vozes."
>
> (depois) "Agora manda de 3 a 5 roteiros do {cliente}. Vou aprender a voz dele separada."

## O que olhar nos roteiros

**1. Tom geral**
- Sério ou descontraído.
- Fala em primeira pessoa (eu) ou em terceira (ele, ela).
- Vai direto ou constrói contexto antes.
- Usa humor, ironia ou provocação.

**2. Ritmo das frases**
- Tamanho das frases: curtas, médias ou longas.
- Se alterna curtas com longas ou mantém um padrão.
- Se usa frases incompletas.
- Como faz pausas e passagens de uma ideia para outra.

**3. Palavras e expressões que se repetem**
- Palavras que aparecem em mais de um roteiro.
- Expressões que são a cara dela.
- Gírias e jeitos da região.
- Como chama o público: você, tu, vocês, pessoal, galera.

**4. Abertura**
- Como costuma abrir: afirmação forte, dado, cena, referência conhecida.
- Se entra direto no assunto ou prepara o terreno.

**5. Ordem da história**
- Como organiza o roteiro: começo, meio e fim em linha, ou vai e volta.
- Quanto tempo gasta na abertura, no meio e no fim.
- Se usa listas, exemplos ou histórias.

**6. Fechamento**
- Como termina: lição, pergunta para os comentários, chamada para agir.
- Se o fim é emocional ou prático.

**7. O que ela evita** (pesa tanto quanto o que ela faz)
- Tipo de frase que ela nunca usa.
- Tom que ela nunca adota.
- Padrão que ela evita.

## Modelo do resumo da voz

```markdown
# Voz: {nome do perfil ou cliente}

## Tom
{2 ou 3 frases}

## Ritmo
- Tamanho das frases: {curtas, médias ou longas}
- Padrão: {ex.: alterna curtas com uma longa}
- Usa frases incompletas: {sim ou não}

## Palavras e expressões
- {as que mais aparecem}

## Como chama o público
{ex.: "você", sempre informal, nunca "vocês"}

## Abertura preferida
{ex.: afirmação forte, dado surpreendente}

## Ordem da história preferida
{ex.: abre com conflito, mostra exemplos, fecha com lição}

## Fechamento típico
{ex.: lição curta, sem chamada para agir}

## O que ela evita
- {lista}

## Frases de referência
{3 a 5 frases dos roteiros que mostram bem a voz, só para consulta. Nunca copie no roteiro novo.}
```

Depois de salvar, confirme:

> "Pronto, aprendi o seu jeito. Salvei e vou usar nos próximos roteiros. Quer que eu escreva algo agora?"

Se for por cliente:

> "Salvei a voz do {cliente}. Quando for escrever para ele, uso essa base. Quer mandar roteiros de outro cliente agora?"

## Usar a voz ao escrever

Antes de escrever qualquer roteiro, veja se existe voz salva:

1. Uma voz só: use sem perguntar.
2. Várias vozes: pergunte "Esse roteiro é para qual perfil?" e liste os nomes.
3. Nenhuma: ofereça aprender (veja "Quando oferecer").

A voz da pessoa vale mais que as regras gerais de tom. Se ela fala com frases mais longas, respeite. Se usa uma palavra que você evitaria, respeite: é o jeito dela.

Três coisas não mudam com a voz:

- O Piso do SKILL.md. Se os roteiros dela usam algo do Piso (por exemplo, o molde "não é isso, é aquilo"), não leve para a voz salva. Diga em uma linha que a skill evita esse molde e proponha outro jeito.
- Nunca inventar.
- Nunca copiar o tema de outra pessoa.
