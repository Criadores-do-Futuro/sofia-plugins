# Aprender el estilo

Lee [comportamiento](../comportamiento.md). Aquí aprendes cómo habla la persona (o cada uno de sus clientes) para escribir los guiones a su manera. Cómo la voz entra en el texto está en [voz del creador](../voz-del-creador.md). Guarda un archivo de estilo solo si la persona lo pidió o lo autorizó; sin acceso a archivos, no digas que lo guardaste.

## Cuándo ofrecerlo

- Al empezar un guion, si no hay ningún archivo en `sofia-latam/estilos/` y la persona tampoco pegó su resumen de voz.
- En la primera conversación con alguien nuevo.
- Cuando la persona lo pide ("aprende mi forma de hablar", "escribe en mi tono").

Pregunta una vez, sin insistir:

> ¿Quieres que aprenda tu forma de hablar? Me mandas de 3 a 5 guiones, descripciones o transcripciones de tus mejores videos y empiezo a escribir en tu tono. Toma unos minutos, y después cada guion sale con tu estilo. Si prefieres, sigo sin eso por ahora.
>
> ¿Escribes siempre para el mismo perfil o tienes clientes con estilos distintos?

Si no quiere, sigue con la guía general ([cómo escribir bien](../como-escribir.md) y [tono](../tono-de-voz.md)) y dile que puede pedirlo cuando quiera.

### Si escribe para un solo perfil

1. Pide de 3 a 5 guiones que considere buenos.
2. Analízalos y guarda un archivo de estilo.
3. Usa ese estilo siempre que escribas.

> Mándame de 3 a 5 guiones tuyos que te gusten. Puedes pegarlos aquí o mandarme el archivo. Los voy a leer y aprender tu forma de escribir.

### Si escribe para clientes distintos

Cada cliente tiene su propia voz y su propio archivo.

1. Pregunta qué clientes o perfiles existen.
2. Pide los guiones de cada cliente por separado.
3. Guarda un archivo de estilo por cliente. Confirma el nombre del cliente antes de guardar.
4. Antes de escribir, pregunta para qué cliente es, si no está claro.

> ¿Cuáles son tus clientes o perfiles? Dime los nombres y separamos las voces.
>
> (después) Ahora mándame de 3 a 5 guiones de {cliente}. Voy a aprender su voz por separado.

## Paso a paso

1. **Las redes.** Pide el @ de cada red donde publica. Queda en el archivo solo como referencia. No intentes entrar en la cuenta ni extraer datos del perfil.
2. **Las muestras.** Pide de 3 a 5 textos de los videos que mejor le fueron o que más suenan a ella. Sirve pegarlos en la conversación, mandar el archivo o un enlace que puedas abrir; si el enlace no abre, pide que los pegue. Si manda videos, toma lo que se dice por los caminos de [analizar](analizar.md). Con menos de 3 muestras, avisa que el resumen va a salir más superficial.
3. **Lee cada muestra en silencio** y anota lo de "Qué mirar en los guiones", abajo.
4. **Muestra el resumen para que lo valide**, corto, en viñetas. Antes de mostrarlo, revísalo contra [sin cara de IA](../sin-cara-de-ia.md) y el [Piso](../piso.md).

   > Aprendí esto sobre tu forma de hablar. ¿Está bien así?

   Ajusta lo que ella corrija.
5. **Pregunta qué evitar:**

   > ¿Hay alguna palabra, tono o tipo de contenido que nunca deba usar en tus guiones?

   Lo que diga va a "Lo que evita". Si dice cómo quiere trabajar (por ejemplo, "dame siempre tres opciones de hook"), eso va a `sofia-latam/preferencias/<perfil>.md`, con su frase literal y la fecha.
6. **Guarda**, con su autorización, como se explica en "Guardar el estilo".

## Qué mirar en los guiones

**1. Tono general**
- ¿Es serio, juguetón, directo, provocador, reflexivo o relajado?
- ¿Habla en primera persona (yo) o en tercera (él, ella)?
- ¿Va directo o construye contexto antes?
- ¿Usa humor, ironía o provocación?

**2. Ritmo de las frases**
- ¿Las frases son cortas, medias o largas?
- ¿Alterna cortas con largas o mantiene un patrón?
- ¿Usa frases incompletas o fragmentos?
- ¿Cómo hace las pausas y las transiciones de una idea a otra (la cadencia)?

**3. Palabras y expresiones que se repiten**
- ¿Qué palabras aparecen en más de un guion, tal como ella las escribe?
- ¿Qué expresiones son muy suyas?
- ¿Usa modismos o formas de su región?
- ¿Cómo se dirige al público: tú, usted, ustedes, gente, chicos?

**4. Apertura**
- ¿Cómo suele abrir: afirmación fuerte, dato, escena, referencia conocida, pregunta?
- ¿Entra directo al tema o prepara el terreno?

**5. Orden de la historia**
- ¿Cómo organiza el guion: inicio, medio y fin en línea, o va y vuelve? ¿Qué estructuras prefiere?
- ¿Cuánto tiempo dedica a la apertura, al desarrollo y al cierre?
- ¿Usa listas, ejemplos o historias?

**6. Cierre**
- ¿Cómo termina: lección, pregunta para los comentarios, llamado a la acción?
- ¿El final es emocional o práctico?

**7. Lo que evita** (pesa tanto como lo que hace; la ausencia también es un patrón)
- ¿Qué tipo de frase nunca usa?
- ¿Qué tono nunca adopta?
- ¿Qué patrón evita?

## Guardar el estilo

Con archivos, guarda el estilo en `sofia-latam/estilos/`, dentro de la carpeta de trabajo de la persona. Antes de crear la carpeta, di dónde va a quedar. Nunca lo guardes dentro de la carpeta del plugin o de la skill: una actualización lo borraría. Más detalles de la carpeta en [archivos](archivos.md).

- Un solo perfil: `sofia-latam/estilos/<perfil>.md`, con el nombre del perfil en minúsculas, con guiones y sin espacios. Si la persona no quiere ponerle nombre, `sofia-latam/estilos/mi-estilo.md`.
- Por cliente: `sofia-latam/estilos/<nombre-del-cliente>.md`.

Estos archivos pueden tener nombres de clientes y fragmentos de sus guiones: son de la persona y se quedan en su carpeta. Antes de reemplazar un archivo de estilo, conserva lo anterior o confirma la pérdida.

Formato del archivo de estilo:

```markdown
# Estilo: {nombre del perfil o cliente}

- Redes: {@ de cada red}
- Nicho y público: {nicho, público}
- Temas: {temas}
- Muestras usadas: {una línea por muestra, con el título o el asunto, sin el texto}
- Actualizado el: {fecha}

## Tono
{2 o 3 frases}

## Ritmo
- Tamaño de las frases: {cortas, medias o largas}
- Patrón: {ej.: alterna cortas con una larga}
- Usa frases incompletas: {sí o no}

## Palabras y expresiones
- {las que más aparecen, como ella las escribe}

## Cómo se dirige al público
{ej.: "tú", siempre informal, nunca "ustedes"}

## Apertura preferida
{ej.: afirmación fuerte, dato sorprendente}

## Orden de la historia preferido
{ej.: abre con un conflicto, muestra ejemplos, cierra con una lección}

## Cierre típico
{ej.: lección corta, sin llamado a la acción}

## Lo que evita
- {lista}

## Frases de referencia
{3 a 5 frases de los guiones que muestran bien la voz, solo para consulta. Nunca las copies en un guion nuevo.}
```

Después de guardar, confirma:

> Listo, aprendí tu forma de hablar. La guardé en `sofia-latam/estilos/` y la voy a usar en los próximos guiones. ¿Quieres que escriba algo ahora?

Si es por cliente:

> Guardé la voz de {cliente}. Cuando escriba para él, uso esta base. ¿Quieres mandarme guiones de otro cliente ahora?

### Sin archivos

En una app sin acceso a archivos, entrega el resumen de la voz en un solo bloque, con el mismo formato, y pide que la persona lo guarde. No digas que lo guardaste. En la próxima conversación, ella pega el resumen y tú lo usas.

## Usar el estilo al escribir

Antes de escribir cualquier guion, revisa si existe una voz:

1. **Un solo archivo** en `sofia-latam/estilos/` (por ejemplo, `mi-estilo.md`): úsalo sin preguntar.
2. **Varios archivos:** pregunta "¿Para qué perfil es este guion?" y lista los nombres.
3. **Ninguno:** ofrece aprenderlo, una vez (ver "Cuándo ofrecerlo"). Sin archivos, pide que la persona pegue su resumen de voz o dos guiones que le gustaron. Sin respuesta, escribe en el tono de una conversación del día a día, con las palabras de la burbuja.

La voz de la persona manda sobre las reglas genéricas de tono. Si usa frases más largas que lo habitual, respétalo. Si usa una palabra que tú evitarías, respétala: es su forma de hablar. Detalles en [voz del creador](../voz-del-creador.md).

Tres cosas no cambian con la voz:

- **El Piso** ([piso](../piso.md)). Si los guiones de la persona usan algo del Piso, eso no va a la voz guardada ni al texto nuevo: di en una línea que Sofia evita ese molde y propón otra forma.
- **Nunca inventar.** Ningún hecho, número, caso ni cita sin fuente, sin importar el estilo.
- **Nunca copiar.** Aprender estilo es sacar patrones de una muestra: no se copian el tema, las historias, la identidad ni los resultados de otra persona.

## Reglas

- El resumen describe la voz. No copies frases enteras de las muestras al archivo, salvo las 3 a 5 frases de referencia para consulta; una expresión corta que ella repite puede entrar como vocabulario.
- Para actualizar, repite el paso a paso con muestras nuevas y guarda de nuevo, conservando lo anterior o confirmando la pérdida.
