# Motion editorial — a linguagem do projeto e a continuidade entre planos

Veio da linha do Codex (`beditor-motion-noir`: `SKILL.md` e
`editorial-motion-workflow.md`), reescrita para o pipeline daqui, que é
guia → corte → motion → acabamento. O conhecimento de base é um vídeo público sobre motion graphics com IA, estudado em
2026-09-10 (ver `procedencia.md`). O que se aproveitou dele não foi o conector nem a promessa de "um prompt". Foi a
disciplina de manter uma gramática visual estável ao longo de muitos planos.

`estilos.md` diz qual sotaque a casa usa. Este arquivo diz como **cada projeto**
fixa a própria linguagem e não a perde no meio.

## Duas regras que valem antes de tudo

**Modo rápido não é atalho de qualidade.** `/sofia-estrategista-editora:montar`, tudo de uma vez,
esconde as aprovações intermediárias, mas não pula nenhuma etapa: decupagem,
fatos, linguagem, beats, montagem e QC acontecem igual, só que sem parar para
perguntar.

**Fala dirigida ao editor não é conteúdo.** Quando o take tem "editor, corta
isso", "aqui entra o gráfico", "refaz essa", a frase sai do vídeo e vira
requisito do momento correspondente no guia (`decisao: cortar`, com o pedido
escrito no `porque` do momento que ele afeta). Leia pelo contexto: "editor"
também pode ser assunto da fala.

## Descoberta, antes do primeiro quadro

Se ainda não estiver decidido, descubra só o que muda o resultado:

- plataforma, proporção, duração e idioma;
- objetivo, público e a ação que se quer do espectador;
- roteiro fechado ou liberdade para reestruturar;
- identidade existente e referências permitidas;
- densidade visual e energia de edição;
- quanto é rosto, arquivo, B-roll, motion e geração;
- política de fatos, direitos, pessoa real, envio remoto e teto de custo.

O `formato` do guia (`formatos.md`) já responde metade: em `dinamismo` não há
motion, e este arquivo quase não se aplica.

## O style bible do projeto

Um preset abre a conversa, mas não é a identidade final. Antes de gastar com
geração, escreva o style bible em `guia/estilo.md`. Ele precisa ser específico
a ponto de dois planos parecerem do mesmo vídeo, e diferente a ponto de não ser
um preset genérico:

- `style_id` e três adjetivos de direção;
- paleta com a **função** de cada cor;
- famílias tipográficas e hierarquia;
- materiais e marcas: papel rasgado, meio-tom, lápis, recorte, 3D, CRT, tecido,
  vidro;
- luz, sombra, grão e profundidade;
- enquadramento e câmera;
- curvas de movimento, tempo de entrada, leitura e saída, e frequência de corte;
- como se tratam pessoa, foto, mapa, número e tela;
- **seis invariantes** que nunca mudam e **seis clichês** proibidos;
- as referências autorizadas e o papel de cada uma.

"Estilo Vox", "cartoon" ou "whiteboard" não servem como direção. Converta o
rótulo em atributos observáveis e monte uma combinação própria. Pedido "no
estilo de" um estúdio ou criador é referência de **nível**, nunca de assinatura:
não se replica pacote gráfico nem composição identificável.

O `direcaoMotion` do guia é este style bible reduzido aos oito itens que toda
cena segue (estilo de animação, movimento, transições, paleta, tipografia,
câmera, clima e ritmo, som), e cada momento de motion leva a sua `cena` com o
prompt próprio (`direcao-de-motion.md`). O style bible é a fonte; o guia leva o
resumo.

## Cada momento responde cinco perguntas

1. O que a fala afirma, ou o que faz o público sentir?
2. Qual é a menor imagem que deixa isso claro?
3. Por que ela aparece **neste** instante?
4. O plano pede exatidão (HyperFrames) ou variação (Gemini)?
5. O que liga este plano ao anterior e ao próximo?

A intenção de cada fala é uma destas: provar, concretizar, criar tensão,
contrastar, revelar, concluir ou respirar. Motion decorativo não é intenção. Se
não há evidência para escolher uma classe, fica o rosto (`fala`) ou se pede
material; não se inventa fato, dado nem arquivo histórico.

## Os registros, e para que serve cada um

| Registro | Serve para |
| --- | --- |
| colagem documental | causalidade, contexto, evidência: arquivo licenciado, papel, meio-tom, anotação, mapa |
| cartoon / ilustração | simplificar, fazer humor, personificar, mudar a energia |
| whiteboard | processo, sequência, comparação, ensino. **O traço é desenhado, mas rótulo e número são HyperFrames** |
| B-roll gerado | concretude, atmosfera, transição, o que é impossível filmar, cobertura de fala |
| motion isolado | uma inserção curta num vídeo já gravado |
| híbrido | o Gemini dá a matéria, o HyperFrames dá informação, marca e tempo |

Alternar registro tem de ter propósito. A mesma cartela, o mesmo zoom ou a
mesma figura branca em sequência é repetição, não linguagem.

## Continuidade entre planos

- Cada família de planos tem uma `familia` no guia (é o `continuity_id` da
  linha do Codex): tudo que deve parecer o mesmo mundo usa a mesma, e o `estado`
  diz em que ponto dessa família o momento está.
- Congele personagem, objeto, figurino, paleta, luz, textura, direção de tela e
  escala dentro de uma `familia`.
- **Keyframe antes de animar.** Gere o quadro de referência, aprove, e só então
  anime (`producao-gemini.md`).
- Defina primeiro e último quadro sempre que uma transição depender deles.
- Deixe folga de 0,25–0,50 s em cada ponta quando o motor permitir, para corte e
  dissolução.
- Faça match cut por forma, cor, direção ou sentido. Não encadeie transição
  aleatória.
- Mudança de estilo sinaliza mudança de narrativa. Sem isso, é falha de
  consistência.

## Voz, música e tempo

- **A voz manda no tempo.** Não se regrava nem se altera fala sem autorização.
- Mudança visual cai em substantivo, verbo de ação, número, contraste ou
  revelação.
- **J-cut** puxa a próxima ideia; **L-cut** segura a continuidade emocional.
  Os dois obedecem a `sincronia.md`: só existem onde a imagem sobre a qual a voz
  toca **não mostra a boca de quem fala**. Sobre o rosto, a voz sai com a boca.
- Um momento pode respirar sem motion. Corte permanente mata o impacto.
- Efeito sonoro é pontuação seletiva, não trilha de cada tween: cai em
  palavra-chave, em ação ou na troca de classe. CRT, arquivo e tela podem ter
  textura sonora própria, desde que não finjam a origem do material.
- Áudio gerado pelo Gemini é **stem candidato**. Nunca substitui sozinho voz,
  música ou efeito aprovados.

## Erros que reprovam o fluxo

- gerar antes de fechar fatos e roteiro;
- mostrar número gerado sem validar e recompor em código;
- pedir um explainer inteiro numa geração só;
- aceitar a primeira tentativa sem comparar com o momento;
- misturar estilos porque cada plano recebeu um prompt isolado;
- depender de texto gerado onde legibilidade e tempo importam;
- usar preset sem personalizar;
- movimento decorativo sem função;
- não guardar prompt, referência, custo, versão e motivo de rejeição.
