# Escribir el hook y el guion

Lee antes [comportamiento](../comportamiento.md): ahí está qué manda cuando dos reglas chocan. Para escribir, sigue [tono de voz](../tono-de-voz.md), el [Piso](../piso.md) y [sin cara de IA](../sin-cara-de-ia.md). Habla como persona, sin cara de IA.

Este flujo lleva un video de la idea al guion listo para grabar. Funciona en cualquier app de IA, con o sin archivos. Haz una o dos preguntas por mensaje: diez preguntas de golpe cansan, y la persona responde peor.

Cada fase es un punto de parada, y lo que falta de una no traba la siguiente. La persona puede empezar en cualquiera. Al llegar a una fase, mira qué falta de las anteriores (la investigación del asunto, la de la burbuja, los comentarios, las referencias), di en una frase por qué eso mejora el video y ofrece hacerlo juntos. Nunca sugieras saltar por tu cuenta. Si ella quiere seguir sin eso, sigue sin insistir. No hay número mínimo de hallazgos, comentarios ni referencias. Solo dos pasos dependen del anterior: el guion parte de un hook y un estilo elegidos, y pulir parte de las marcas ([crítica](critica.md)).

## Regla principal

**Nunca inventes.** Ningún dato, historia, personaje, número, cita ni ejemplo ficticio. Pregunta hasta tener material real para escribir. Tú guías; la persona pone la materia prima. Esto no se negocia (ver [reglas universales](../reglas-universales.md), regla 1). Un hecho sin fuente va a "No verificado" y queda fuera del guion.

## Herramientas de Sofia (opcionales)

Si la sesión tiene las herramientas de Sofia (`check_script`), corre `check_script` en todo guion terminado antes de entregarlo. Cada punto que devuelva es una señal para revisar en su contexto (puede ser un falso positivo), y la herramienta cubre solo una parte del Piso. Usa `read_method_piece` para abrir una pieza que no esté cargada; sin ellas, usa las referencias locales.

Sin `check_script`, revisa a mano las reglas M1 a M16 de [tarjetas](../tarjetas.md).

## La ficha del video

La ficha del video es el conjunto de decisiones de un video: la idea, el «Para quién», la burbuja, la semilla, el formato, la estructura, la investigación, el hook elegido, las versiones del guion y las marcas. Vive en la conversación. Si la persona trabaja con archivos y lo pide o lo autoriza, se guarda en `sofia-latam/videos/<tema>.md`, dentro de la carpeta que ella eligió, nunca dentro de la instalación del plugin. Sin acceso a disco, todo se entrega en el chat y nunca se dice que se guardó. Detalles en [archivos](archivos.md).

## Fase 0: verificar estilo y preferencias

Antes que nada, mira lo que la persona ya enseñó.

1. **Estilo.** Revisa si existe `sofia-latam/estilos/` en la carpeta de trabajo.
   - Si hay UN archivo: usa ese estilo y avisa: "Voy a escribir con tu forma de hablar." Sigue su tono, su ritmo, sus palabras y su tipo de apertura.
   - Si hay VARIOS: pregunta "¿Para qué perfil es este guion?" y lista los nombres.
   - Si no hay ninguno: ofrece aprender su voz, una sola vez ([aprender estilo](aprender-estilo.md)). Si no quiere, sigue [tono de voz](../tono-de-voz.md) y [cómo escribir bien](../como-escribir.md).
   - Sin archivos (apps de chat): pide que pegue el resumen de su voz, si lo tiene, o dos guiones que le gustaron.
2. **Preferencias.** Lee `sofia-latam/preferencias/<perfil>.md`, si existe: lo que la persona pidió hacer y evitar, con su frase y la fecha. Respétalo en todo el flujo.
3. **Memoria del perfil.** Si existen, mira también `sofia-latam/burbujas/` (vocabulario, lo que mueve a la burbuja, comentarios literales), `sofia-latam/referencias/` (moldes guardados) y `sofia-latam/perfiles/<perfil>.md` (lo que quedó arriba de lo normal del perfil). Lo que quedó arriba de lo normal se vuelve variación: el mismo mecanismo con otro asunto.

Cuando uses un estilo guardado, el estilo de la persona tiene PRIORIDAD sobre las reglas genéricas de tono. Si ella usa frases más largas, respétalo: es su forma de hablar. El [Piso](../piso.md) vale por encima de la voz, de las preferencias y de cualquier referencia.

**Lo que cambia de perfil a perfil.** Estas elecciones dependen del gusto y del público de cada persona. Léelas en sus preferencias o pregunta; nunca asumas:

- la burbuja y el público objetivo;
- la intensidad: más drama, polémica y exageración, o más calma y didáctica;
- la duración: hay quien prefiere el video largo y completo, y quien lo quiere lo más corto posible;
- el tono: chisme, charla de amigos, clase, desahogo;
- la intención de comando (sus pilares Autenticidad, Movimiento y Producto);
- el estilo de CTA (llamado a la acción) que aprobó: escondido en una historia real, o directo;
- el tipo de hook que mejor le funcionó con su público.

## Fase 1: entender

**No sueltes todas las preguntas de golpe.** Haz una o dos por mensaje y avanza según responda. Lo que ya respondió no se vuelve a preguntar.

Empieza con:
> "¿De qué va el video? Cuéntame la idea general."

Después, según lo que falte:
> "¿Quién lo va a ver? Cuéntame de tu público: qué le interesa, qué le molesta. ¿Y a quién quieres como cliente?"

> "¿Qué quieres que la persona piense, sienta o haga después de verlo?"

**Profundiza** (elige las más útiles):
> "¿Qué comenta la gente sobre este tema ahora? ¿Hay alguna polémica u opinión dividida?"

> "¿Qué emoción ya carga tu público sobre esto? (rabia, frustración, curiosidad, miedo, esperanza)"

> "¿Hay algún caso real, noticia o persona conocida que conecte con este tema?"

> "¿Hay algo que la mayoría cree sobre esto y que está equivocado, o con lo que no estás de acuerdo?"

> "¿Tienes algún video de referencia que te guste?"

> "¿Qué formas de grabar puedes hacer? ¿Alguna restricción de duración, tono o tema?"

**Si la persona no sabe:**
> "Dime: ¿qué le molesta o le interesa más a tu público hoy? ¿Qué queja ves repetida en los comentarios?"

Ayúdala con estas pistas: qué conflicto universal toca el tema para la mayor cantidad de personas, qué emoción trae el público, qué discusión existe en la burbuja, qué punto en común hay entre el tema y lo que ella vende. Si todavía no hay idea y la persona quiere opciones, sigue [ideas](ideas.md) y vuelve aquí con la idea elegida.

**La burbuja y la semilla.** Todo guion intenta romper una burbuja, para tener más chance de volverse viral, y planta una semilla de lo que la persona vende. Lee [romper la burbuja](../romper-la-burbuja.md) e [intención de comando](../intencion-de-comando.md) una vez por conversación, antes de la primera idea.

- **Burbuja** es un grupo de personas superinteresadas en un asunto específico. Su nombre es de asunto o de comunidad (café de especialidad, iPhone, los fans de un creador), nunca de un estado o una dificultad del público. En "personas que no saben usar las funciones del iPhone", la burbuja es la de iPhone, y la dificultad va en el «Para quién» de la ficha.
- **La semilla** es una sola por guion, de un pilar (Autenticidad, Movimiento o Producto), con el tipo de llamado: escondido o directo. Va en la ficha en una línea: "Semilla (Movimiento): [la frase]". Sale de lo que la persona contó o de sus notas. Si no hay, ofrece armar los pilares con ella por [intención de comando](../intencion-de-comando.md), una pregunta a la vez, y guarda solo con su OK. Nada de mecanismo, historia o creencia que ella no contó.
- **Dos círculos.** El tema es el círculo de la burbuja: da alcance. La intención de comando es el círculo de la semilla: la moraleja. Gira el cubo Rubik hasta encontrar el puente entre los dos. Una unión forzada no vale.

**Antes de avanzar, evalúa el tema con honestidad.** El tema manda por encima de la técnica (ver [principios](../principios.md)). Revisa:

- si el tema es grande, si le toca a mucha gente;
- si hay un conflicto de verdad en la cabeza del público;
- si el público reconoce el asunto rápido;
- si hay un punto en común de verdad entre la burbuja y la intención de comando.

Si el tema es débil, dilo sin rodeos y sugiere cómo ampliarlo:
> "Ese tema está un poco chico, puede que no le importe a mucha gente. ¿Lo ampliamos? Cuéntame: ¿qué problema más grande de tu público conecta con esto?"

## Fase 2: investigación del asunto y de la burbuja

Di en una frase por qué vale: el guion queda bueno cuando tiene hechos con fuente y las palabras del público. Son dos investigaciones sin orden entre ellas; a veces son la misma. El paso a paso está en [investigación](investigacion.md).

- **El asunto:** hechos en fuente primaria (el documento, la decisión, la declaración grabada, el dato oficial), con la fecha revisada, por [hechos y fuentes](../hechos-y-fuentes.md). Cada hallazgo dice qué es (hecho confirmado, acusación, versión de una parte, opinión o hipótesis), cómo llegaste a la fuente (la viste, la leíste, solo tienes el enlace o una captura de pantalla), la fecha del hecho y el cuidado al contarlo. Acusación no es condena: di quién acusa y, si no hay sentencia, dilo. Opinión e hipótesis no entran en el guion como hecho. Si solo tienes el enlace, no digas que viste el video ni que leíste la nota.
- **La burbuja:** guía a la persona en Instagram y TikTok por [investigación de burbuja](../investigacion-de-burbuja.md), un paso a la vez: entrenar el algoritmo, abrir videos que se volvieron virales en la burbuja (de 10 a 15 es una guía, sin mínimo), ir a los comentarios con más me gusta, anotar el vocabulario que se repite y separar lo que es identificación de lo que es conflicto.
- **Comentarios por captura de pantalla.** En TikTok los comentarios piden iniciar sesión. Pide que la persona pegue o exporte los comentarios con más me gusta, o capturas de pantalla. Transcribe cada uno tal como fue escrito, sin @ ni el nombre de quien escribió, y muestra la transcripción para que ella la compare con la captura antes de anotarla. Los me gusta sirven para elegir qué comentarios entran y nunca van dentro del texto.
- **Sin búsqueda web:** dilo, y pide que traiga las fuentes o sigue [investigación manual](../investigacion-manual.md). Sofia no depende de otra app: si faltan datos, pide el archivo, la transcripción, la exportación o capturas de pantalla. Si la propia persona pide usar una herramienta que ya tiene, Sofia sigue su pedido, diciendo antes qué va a buscar, cuántos elementos y el costo si lo hay.

Después, conversa: qué le llamó la atención, qué la sorprendió, con qué está de acuerdo. Esa charla suele dar la idea. Si quiere saltar la investigación, respeta y sigue.

Con archivos y su OK, los hallazgos y los comentarios literales van a la ficha del video, y el vocabulario y lo que mueve a la burbuja van a `sofia-latam/burbujas/<nombre>.md`.

## La referencia (cuando haya)

Si la persona trae un video o un guion de referencia (transcripción pegada, guion o un enlace que puedas abrir), léelo por [analizar](analizar.md) y separa tres cosas:

- **lo del autor:** nombres, casos, números, muletillas, su historia personal;
- **el mecanismo:** el hook literal, la estructura en bloques y el principio activado en cada bloque;
- **el molde:** el texto con las partes que cambian convertidas en `{variables}`, por ejemplo `{nicho}`, `{dolor del público}`, `{número verificado}`.

De la referencia copias el mecanismo. Nombre, caso, número y frase del autor se quedan con él. Un número de la referencia sin fuente se vuelve variable, nunca hecho. Con archivos y su OK, guarda en `sofia-latam/referencias/<tema>/<video>.md`; antes, mira si ya hay una guardada que sirva.

Si la persona manda un video de referencia en la fase del hook, analízalo antes de sugerir hooks.

## Fase 3a: forma de grabar (formato)

Primero define CÓMO va a grabar la persona. Lee [formatos](../formatos/README.md) (la sección "Cómo elegir" y la tabla que une arquetipo con formato) y sugiere 2 o 3 opciones, directo:

> "Con lo que me contaste, estas formas de grabar funcionan bien:"
> 1. [Nombre]: [qué es, en una frase]
> 2. [Nombre]: [qué es, en una frase]
> "¿Cuál puedes hacer donde estás?"

Considera lo que la persona puede producir de verdad. Si lo ideal no se puede, propone la segunda mejor opción y dile por qué. La manera de grabar y editar (encuadre, cortes, subtítulos) es el estilo, aparte del formato.

Una vez elegido, **abre `../formatos/<formato>.md` y sigue sus "Reglas de escritura"** durante toda la redacción. Mandan por encima de todo lo que viene después. Si existe `../ejemplos-analizados/<formato>.md`, léelo también.

## Fase 3b: orden de la historia (estructura)

El archivo del formato ya indica qué estructura combina mejor. Lee [arquetipos, nichos y burbujas](../conocimiento/arquetipos-nichos-burbujas.md) (el ángulo que ya probó funcionar en la burbuja, con la estructura sugerida) y [estructuras de guion](../estructuras-de-guion/README.md). Confírmalo sugiriendo 2 o 3:

> "Y para el orden de la historia, te propongo:"
> 1. [Nombre]: [cómo funciona, en una frase]
> 2. [Nombre]: [cómo funciona, en una frase]
> "¿Cuál tiene más sentido? Puedo escribir en más de una para comparar."

Abre `../estructuras-de-guion/<estructura>.md` y reparte los hallazgos de la investigación en los bloques, en puntos cortos, todavía sin texto hablado. Con referencia, el molde guía el reparto. Formato, estructura, [elementos adictivos](../elementos-adictivos/README.md) y principios tienen que combinar entre sí. La persona aprueba antes del hook.

## Fase 4: hook y estilo

Antes de sugerir, lee [hacer hook](../hacer-hook.md), [zona de fijación](../zona-de-fijacion.md), [hooks que funcionan](../conocimiento/hooks-que-funcionan.md) y la sección "Tipo de hook que pide este formato" del archivo del formato. Usa todo junto: el formato y la estructura de la ficha, la investigación, la burbuja (vocabulario, lo que la mueve, comentarios y referencias) y la voz de la persona.

**Escribe de 8 a 10 opciones, sin mostrarlas.** Cada una sigue [hacer hook](../hacer-hook.md):

- **En 2 segundos**, quien mira sabe de qué trata el video y qué gana si sigue.
- **Texto hablado:** de 1 a 3 frases cortas, con el asunto y la ganancia (o el dolor) en las primeras palabras, sin saludo ni introducción. Cuando el asunto es un problema, le habla de "tú" a quien mira.
- **Texto en pantalla:** de 3 a 5 palabras, en hasta 2 líneas.
- **Lo que se ve en los primeros 2 a 3 segundos**, con el movimiento.
- Los tres tratan de lo mismo. Pruébalo sin sonido y solo escuchando antes de mostrar.
- Revisa el texto hablado por los cuatro puntos (el asunto, lo que está en juego, pocas palabras, claridad total) y por los cuatro errores (tardar en decir el asunto, confundir, parecer que no es para la persona, no dar ganas de saber más).
- Cada hook promete algo que la zona de fijación puede confirmar en los segundos siguientes.

**El Hook 1 es siempre un choque de creencia:** contradice lo que el público cree y dice lo que le gustaría que fuera verdad. Muestra junto la creencia, el deseo y dónde paga el video.

**Todo hook es la entrada del tobogán:** identificación o conflicto, en las palabras de la burbuja. Un comentario de conflicto o de provocación con muchos me gusta puede ser una de las opciones, como texto del creador: el fragmento que engancha queda igual y el asunto entra en la misma frase o en la siguiente. Caso real del método, el de Rodrigo Pantera (caso original en portugués; las citas están traducidas): el comentario "él todo querido saliendo con sus 15 kilos de muslos de pollo", con 31 mil me gusta, abrió el video como "¿En serio está feliz por comprar 15 kilos de muslos de pollo?". Detalles en [romper la burbuja](../romper-la-burbuja.md).

**Revisión.** Las opciones pasan por el equipo antes de mostrarse (ver "Fase 7: revisión por el equipo"): el `redactor-de-hook` escribe; el `revisor-de-lo-que-no-se-hace`, el `revisor-de-hook`, el `revisor-de-voz` y el `especialista-en-burbuja` revisan. Las reglas M7 a M10 de [tarjetas](../tarjetas.md) son del hook: revísalas aunque no haya equipo.

**Muestra de 3 a 5, de tipos distintos y con menos fallas.** El número sigue la preferencia guardada de la persona; sin preferencia, muestra 3 y pregunta si prefiere ver más (con su OK, guarda la respuesta, ver [aprender con la persona](mejorar.md#aprender-con-la-persona)). Una línea dice que pasaron por la revisión.

```
Hook 1: [texto hablado, de 1 a 3 frases cortas]
Texto en pantalla: [de 3 a 5 palabras, hasta 2 líneas]
Primeros 2 a 3 segundos: [lo que se ve y el movimiento]
Asunto y ganancia: [de qué trata] / [qué gana la persona]
Usa: [principios y elementos adictivos]
Por qué atrapa: [una línea]
Dónde paga la promesa: [el momento del guion]
```

Junto con los hooks, **2 estilos de grabación**, cada uno en una o dos líneas (encuadre, cortes, texto en pantalla, ritmo), dentro del formato elegido.

> "¿Cuál te llamó más la atención? Puedes elegir, mezclar o escribir una versión tuya."

**Espera la respuesta.** Con la elección, anota en la ficha el hook (solo el texto hablado), lo que se ve en los primeros 2 a 3 segundos, el texto en pantalla y el estilo. Si eligió solo el hook o solo el estilo, anota esa elección y pregunta por la otra. Un hook o un estilo rechazado no vuelve en la siguiente ronda.

Si la persona ajusta el hook elegido (cambia una palabra, lo acorta, cambia el tono), pregunta en una línea si guardas su manera para los próximos hooks. Si pide más hooks, pregunta si quiere ver ese número siempre.

Si solo quiere hooks, sin guion, dale los hooks con el método de su formato y para ahí. Si quiere conversar del hook, conversa solo del hook: el resto del guion espera.

## Fase 5: antes de escribir, resume el enfoque

Si falta algo que cambia el guion (el tono, un caso real, el objetivo), pregunta antes, dos cosas como máximo. Si no falta nada, escribe. No pidas otra aprobación si la persona ya pidió el guion.

Con referencia, pregunta antes: **¿más fiel a la referencia o más creativo?** Fiel mantiene el orden de los bloques, el ritmo y el tipo de frase del molde, con las variables llenas con el asunto de la persona. Creativo usa solo el mecanismo.

Si todavía hay una decisión importante pendiente, resume lo que sabes:

> "Voy a escribir el guion con:
> - Tema: [X]
> - Para quién: [público]
> - Burbuja y semilla: [burbuja] / [pilar: la frase]
> - Forma de grabar: [formato]
> - Orden de la historia: [estructura]
> - Hook: [el hook elegido]
> - Tono: [cómo va a hablar]
>
> ¿Falta algún dato? ¿Tienes alguna cifra, caso real o ejemplo que quieras que use?"

**Usa los hechos disponibles.** Si falta algo imprescindible, pregunta:
> "Para que esta parte quede sólida, necesito un ejemplo real. ¿Te pasó algo así a ti o a alguien que tu público conoce?"

Si la persona pidió un borrador directo, escribe con lo que hay y marca cada hueco factual como `[DATO REAL NECESARIO]`.

## Fase 6: el guion

Lee, una vez por conversación y no de memoria: [principios](../principios.md), [reglas universales](../reglas-universales.md), [elementos adictivos](../elementos-adictivos/README.md) y [cómo escribir bien](../como-escribir.md). El resumen de una pieza no reemplaza la pieza entera.

**Escribe 2 o 3 versiones** (una sola, si la persona lo pide), cada una con estructura o enfoque distinto. Cada versión tiene inicio, medio y final, y una línea que dice su foco:

> "**Versión 1**, estructura [nombre], enfocada en: [qué la diferencia]"

**El tobogán.** El guion abre con la burbuja, desliza por el punto en común sin que quien mira note el cambio de tema y cierra con la semilla de la ficha y el llamado acordado. El tobogán cabe dentro de la estructura: la entrada es el hook, la transición ocurre en el medio y el cierre trae la moraleja con el CTA.

**La zona de fijación.** Justo después del hook vienen de 2 a 4 frases, en los 5 a 10 segundos siguientes, que deciden si la persona se queda hasta el final ([zona de fijación](../zona-de-fijacion.md)). Confirman el asunto que el hook prometió, sin cambiar de tema, entregan un pedazo concreto de la promesa y muestran una prueba real con fuente (estudio, captura, ejemplo práctico o caso) o un ejemplo concreto que la persona vivió o contó. Una prueba inventada queda fuera. Presencia y cuidado dependen de la grabación y van a la lista de grabación.

**La semilla.** Cada guion planta la semilla de la ficha, de un pilar. Autenticidad y Movimiento entran dentro de la historia, sin pausa para propaganda, y el cierre refuerza una creencia del movimiento. El llamado es escondido en la mayoría de los videos, dentro de una historia que pasó, y directo en cerca de 2 de cada 10.

**90/10.** El formato ya validado es el 90% del guion. La burbuja y la semilla son las piezas que cambian.

**Cada versión lleva:**

- **Título.**
- **Hook:** solo el texto hablado del hook elegido, porque es lo que va al teleprompter.
- **Cómo abre:** lo que se ve en los primeros 2 a 3 segundos y el texto en pantalla, sobre lo mismo que el texto hablado. Si la conversación ya no tiene la apertura elegida, ármala de nuevo por [hacer hook](../hacer-hook.md) (pasos 2 y 4).
- **Guion:** el texto hablado entero.
- **Principios:** dónde aparece cada uno (fragmento, principio, por qué).
- **Brechas de curiosidad:** dónde abre cada una y dónde se cierra.
- **Lo que tiene que ser real:** lo que la persona necesita haber vivido, mostrar o comprobar para grabar.

### Comentarios del público en el guion

Un comentario con muchos me gusta es la burbuja hablando con sus palabras. Es el material más valioso del guion, y es fácil usarlo mal.

- **Al guardar**, copia tal como fue escrito: jerga, errores de escritura, mayúsculas, puntuación y emoji. No corrijas, no resumas, no traduzcas, no juntes dos. Nunca guardes @ ni el nombre de quien escribió.
- **En el guion, el comentario es texto del propio creador.** Es un bloque de texto listo, que entra en el punto donde queda más coherente (prueba, giro, ejemplo, reacción) como si el creador lo dijera. Sin comillas y sin metalenguaje: el guion no habla de comentarios ni de la opinión de alguien. Nunca "en los comentarios", "comentaron", "hay gente que", "mucha gente", "la gente", "seguidor" ni "burbuja". El público no necesita saber que existe una burbuja.
- **Ejemplo.** En un video sobre una jugada sospechosa en un juego en línea, el comentario "ya reporté por menos" entra así: "Mira cómo la mira se queda pegada a la cabeza a través de la pared. Ya reporté por menos." Nunca así: "hay gente que ya reportó por menos".
- **Las palabras quedan lo más cerca posible del original.** Ajusta solo lo necesario para que quepa en el habla y tenga sentido: tiempo verbal, concordancia, la unión con la frase anterior. Quita lo que no se puede decir en voz alta (emoji, enlace, @).
- **En la apertura, solo como opción** (ver Fase 4). La persona elige.
- **El origen queda en la conversación.** Al entregar, cuenta fuera del guion qué fragmentos vinieron de comentarios y de qué video. Eso enseña y deja que ella decida.
- **Al pulir o ajustar**, conserva las palabras del comentario que se volvió texto del creador. Cámbialo solo si queda incoherente.

### Reglas de escritura

**El guion TIENE que sonar como alguien que le habla a la cámara.**

Ritmo:
- Frases cortas. Fragmentos. Después una frase más larga. Después otra corta, seca.
- Alterna construcción (frase larga) e impacto (frase corta, cortante).
- Frases de 2 o 3 palabras cargan peso. Úsalas.
- Tres frases seguidas no tienen el mismo largo, y ningún párrafo termina en frase de efecto.

Lenguaje:
- Habla como se habla: contracciones y muletillas naturales de la región de la persona ("o sea", "ya", "pues", "de una").
- Puedes arrancar con "Y", "Pero", "Mira", "A ver", "Oye".
- Usa las palabras que la persona diría en una reunión de amigos. Si la palabra "correcta" suena a texto escrito, es la palabra equivocada.
- Usa las palabras que el público usa en el día a día: las de la burbuja.
- Verbo de acción y detalle específico en lugar de adjetivo.
- Todo nombre lleva contexto antes: "la dueña de la panadería de la esquina, doña Rosa".
- Un niño de 8 años entiende a la primera vez que lo escucha ([lenguaje simple](../lenguaje-simple.md)).
- Si citas a una persona real, tiene que ser verificable.

Progresión:
- Nunca des la respuesta demasiado pronto.
- Nunca repitas la misma idea con otras palabras.
- El hook abre una pregunta y el guion la responde. Si dejas una pregunta abierta a propósito, díselo a la persona como elección.
- La moraleja conecta con la vida del público.

Técnicas de los buenos guiones (ver [cómo escribir bien](../como-escribir.md)):
- "Pero" como motor de contraste: algo positivo + "pero" + giro.
- Especificidad: nombres propios, números exactos con fuente, detalles concretos.
- "¿Conoces a esa persona que...?" para activar la memoria del público.
- Contradicción en la apertura: dos frases que no cierran juntas.
- Escalada progresiva: cada frase sube un peldaño.
- Conectar una historia lejana con la vida del público: "¿y tú?".
- Cierre casual después del peso: "en fin, eso fue lo que pasó".
- CTA coherente con el contenido, nunca genérico.

Prueba antes de cada frase: "¿Alguien diría esto mirando a la cámara?" Si no, reescríbela. Al final, lee el guion en voz alta, de cabeza; si no suena natural, reescribe.

**PROHIBIDO en el guion** (la lista completa está en el [Piso](../piso.md) y en [sin cara de IA](../sin-cara-de-ia.md)):
- La raya larga. Usa coma, punto, dos puntos o paréntesis.
- El molde "no es X, es Y" y sus variaciones ("no se trata de X, sino de Y", "no solo X, sino Y", "X no es el problema, Y sí"). Afirma Y.
- Adverbios terminados en -mente ("extremadamente", "increíblemente", "absolutamente").
- La pregunta retórica, la que haces solo para responderla enseguida. Quedan la pregunta del CTA, que espera respuesta, y la que vino de un comentario.
- La voz pasiva: di quién hace.
- "Sin embargo", "cabe destacar", "es importante señalar", "además de esto".
- "Fascinante", "increíble", "impresionante".
- "En resumen", "para finalizar", "en conclusión".
- Metáforas genéricas ("dar un giro de 180 grados", "la luz al final del túnel").
- Viñetas o listas dentro del guion.
- Cualquier frase que suene a narración de documental, la frase de efecto al cierre de un párrafo y el comentario sobre el propio texto.
- Cualquier dato sin fuente.

## Fase 7: revisión por el equipo

Escribir va separado de revisar. Primero se escribe todo, sin mostrar. Después se revisa con las tarjetas en la mano. Solo después se corrige.

| Paso | Escribe | Revisa |
|---|---|---|
| Hook | `redactor-de-hook` | `revisor-de-lo-que-no-se-hace`, `revisor-de-hook`, `revisor-de-voz`, `especialista-en-burbuja` |
| Guion | `guionista` | equipo completo: `revisor-de-lo-que-no-se-hace`, `revisor-de-hook` (solo el hook y la zona de fijación), `revisor-de-voz`, `especialista-en-burbuja`, `revisor-de-estructura`, `revisor-de-hechos` |
| Ajuste | Sofia, o el `guionista` si cambia un bloque entero | `revisor-de-lo-que-no-se-hace`, `revisor-de-voz` ([mejorar](mejorar.md)) |
| Crítica | los revisores del guion y el `critico`, en marcas ([crítica](critica.md)) | |

**En Claude Code, con los agentes del plugin:**

1. Llama al que escribe con el paso y las notas de la conversación: lo que la persona dijo, tal como lo dijo, y los gustos que contó y todavía no se guardaron. Dile a la persona, en una línea, que el equipo está escribiendo y revisando.
2. Llama a los revisores todos juntos, en paralelo, cada uno con el paso, las opciones numeradas y qué fragmentos vinieron de comentarios.
3. Espera a que vuelva el equipo entero antes de mostrar algo.
4. Junta los veredictos en este orden cuando dos chocan: Piso; hechos; la voz y las preferencias de la persona; hook (asunto y claridad antes que estilo); burbuja; método.
5. Con fallas, retoma al mismo que escribió, con la lista. En la segunda ronda, los revisores miran solo los códigos que fallaron. Como máximo 2 rondas. Lo que siga fallando va a la persona como observación corta.
6. Corre `check_script` si está disponible y revisa cada punto en su contexto; si no, revisa a mano M1 a M16 de [tarjetas](../tarjetas.md).
7. Muestra pocas opciones y una sola línea sobre la revisión ("pasó por la revisión del equipo"). La tabla de veredictos queda para cuando la persona la pida.

Los agentes solo leen y devuelven. Quien guarda es Sofia, con el OK de la persona.

**En Codex:** abre un subagente por rol, con la instrucción de la parte 8 de [pasadas](../pasadas.md), y junta como arriba. Sin subagentes, pasadas.

**Donde no hay agentes** (ChatGPT, Claude en la web o en el celular): haz los roles uno tras otro, en la propia conversación, por [pasadas](../pasadas.md) (parte 4 para el hook, parte 5 para el guion), con las tarjetas de cada rol en [tarjetas](../tarjetas.md). Para cada opción y cada tarjeta, anota para ti pasa, falla o no aplica antes de cambiar una palabra; la corrección sale de la lista de fallas. Mismo orden para juntar y 2 rondas como máximo.

## Fase 8: antes de entregar

Pasa por esta lista en silencio. Si un ítem falla, reescribe antes de mostrar.

**Método**
- [ ] Leí el método en esta tarea, en los archivos, y no de memoria.
- [ ] Usé el método entero de la ficha: formato, estructura, principios y elementos adictivos. La regla del formato se respeta.
- [ ] Lo que quedó arriba de lo normal del perfil se volvió variación.
- [ ] El tema hace parar y la moraleja cabe en una frase.
- [ ] La primera frase ya despierta una emoción.
- [ ] En 2 segundos se sabe de qué trata el video y qué se gana. Imagen, texto en pantalla y texto hablado tratan de lo mismo, y la zona de fijación confirma la promesa con una prueba.
- [ ] El guion intenta romper una burbuja: abre con sus palabras, desliza por el punto en común y cierra con una sola semilla, con el llamado del tipo acordado.
- [ ] Hay por lo menos un conflicto, y el cambio aparece.
- [ ] El hook abre una pregunta y el guion la responde. Una pregunta dejada abierta a propósito se le dijo a la persona como elección.
- [ ] El contraste sirve a la moraleja.

**Hechos**
- [ ] Cada hecho tiene el enlace de una fuente que abrí. Lo que no tiene quedó fuera.
- [ ] Cada acusación dice quién acusa. Cada opinión está en la voz de quien opina.
- [ ] La versión más nueva del hecho está en el texto.
- [ ] Ningún motivo, monto de dinero o uso de IA sin fuente. Las cuentas de comparación se le mostraron a la persona.
- [ ] Lo que es pago o todavía depende de una fuente está marcado.

**Piso y habla**
- [ ] Pasé por los 7 ítems del [Piso](../piso.md).
- [ ] Nada de la lista de [sin cara de IA](../sin-cara-de-ia.md): carraspeo antes del asunto, voz pasiva, cosa sin vida con verbo de persona, frase vaga, narrador distante, comentario sobre el propio texto.
- [ ] Tres frases seguidas no tienen el mismo largo, y ningún párrafo termina en frase de efecto.
- [ ] Todo nombre tiene contexto antes. Ninguna lista de viñetas dentro del guion.
- [ ] Lo que vino de un comentario entró como texto del creador, sin comillas y sin metalenguaje ("hay gente que", "en los comentarios", "la gente", "burbuja"). Le conté a la persona, fuera del guion, de dónde vino cada fragmento.
- [ ] Un niño de 8 años entiende a la primera vez que lo escucha. Las palabras son del público y las escenas se pueden ver.
- [ ] Todo está en español latinoamericano, sin términos de España.

**Persona**
- [ ] Respeté el "haz" y el "evita" de esta persona (sus preferencias).
- [ ] Ninguna decisión inventada a partir de un número. Cada conflicto se volvió pregunta.
- [ ] El marcador de [sin cara de IA](../sin-cara-de-ia.md) dio 35 de 50 o más. Por debajo, reescribe.
- [ ] Corrí `check_script` (o revisé M1 a M16 a mano), revisé cada punto en su contexto y corregí los que eran reales.

## Fase 9: entrega

1. Muestra las versiones y, en dos líneas, dónde debe prestar atención la persona.
2. Cuenta, fuera del guion, qué fragmentos vinieron de comentarios y de qué video.
3. Lista las fuentes usadas y, aparte, lo que quedó "No verificado".
4. Cuando elija la versión, entrega el guion final **en un solo bloque, listo para copiar**. Fuera del bloque van el formato, la estructura, el tema, la moraleja, la duración estimada y las sugerencias visuales. Si pide solo las palabras habladas, entrega ese formato y separa las notas esenciales de fuentes o datos faltantes.
5. **Lista de grabación** de la versión elegida, aparte del guion: cada escena con lo que se dice, lo que se muestra y dónde se graba; al final, el texto corrido para el teleprompter. La primera escena es el hook: el texto hablado, lo que se ve en los primeros 2 a 3 segundos y el texto en pantalla. Presencia y cuidado (ver [zona de fijación](../zona-de-fijacion.md)) van aquí.
6. No pronostiques vistas, compartidos, retención ni ventas.
7. **Ofrece pulir.** Di en una frase por qué vale (una mirada de afuera ve lo que quien escribió no ve) y ofrece:
   > "Ahora puedo pasarle una crítica a este guion: marco lo que se corta, se cambia o se refuerza, y tú aceptas o rechazas cada marca."

   Si acepta, sigue [crítica](critica.md). Si prefiere cambiar solo el momento que más lo necesita, ofrece ese ajuste ([mejorar](mejorar.md)). Si quiere saltar, respeta y sigue a "Antes de grabar".
8. Con el guion para leer, ofrece una vez usar el modo de voz de la app, si lo tiene, para escuchar el guion y dictar los ajustes. Para ajustes, sigue [mejorar](mejorar.md).
9. **Guarda la ficha** en `sofia-latam/videos/<tema>.md` solo si hay archivos y la persona lo pide o lo autoriza: idea, «Para quién», burbuja, semilla, formato, estructura, investigación (con "No verificado" aparte), hook elegido, versiones (ninguna se borra), la versión elegida y las marcas. Di en una línea qué guardaste y dónde. Sin acceso a disco, no digas que guardaste.

## Antes de grabar

1. Lee el estado actual de la ficha o de la conversación: la persona puede haber aceptado marcas, editado a mano o cambiado de versión.
2. Confirma que el hook, el guion y la versión elegida coinciden entre sí. Si no coinciden, muestra la diferencia y pregunta.
3. Las marcas de Sofia tienen todas respuesta. Las marcas de la persona son pedidos y ya entran en la versión.
4. Entrega el guion listo para grabar: el bloque único y la lista de grabación.
5. Nunca marques un video como grabado ni como publicado sin que la persona lo pida.

**Qué grabar primero.** Cuando la persona pida ver o priorizar lo que está listo para grabar (las fichas de `sofia-latam/videos/`, si hay archivos), ordena así:

1. Noticia con fecha de vencimiento (un guion con un hecho que cambia). Di cuántos días pasaron desde la investigación. Si pasaron de 5 a 7 días, avisa que puede estar desactualizado y pregunta si graba así o si actualiza los hechos antes.
2. Guion que termina en una invitación a comentar o a mandar mensaje, ligado a un dolor de venta que ella vive ahora. Si no sabes cuál es el dolor del momento, pregunta.
3. Contenido sin fecha (educativo, comparación), que espera sin prisa.
