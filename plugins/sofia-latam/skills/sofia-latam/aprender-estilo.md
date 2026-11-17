Lee [comportamiento](../../comportamiento.md). Guarda un perfil solo si el usuario lo pidió o autorizó; sin acceso a archivos, no afirmes haberlo guardado.

# Aprender Estilo de Escritura

## Cuándo ofrecerlo

En la primera interacción con un usuario nuevo, o cuando todavía no existe un archivo de estilo guardado, ofrece:

> "Antes de escribir, ¿quieres que aprenda tu estilo? Si me mandas algunos de tus mejores guiones, aprendo tu tono, tus palabras, tu ritmo — y escribo a tu manera. Toma unos minutos, pero después cada guion sale con tu sello."
>
> "¿Escribes siempre para el mismo perfil o tienes clientes distintos con estilos distintos?"

## Flujo si escribe para UN perfil

1. Pide de 3 a 5 guiones que la persona considere buenos
2. Analízalos y guarda UN archivo de estilo
3. Usa siempre ese estilo al escribir

> "Mándame de 3 a 5 guiones tuyos que te gusten. Puedes pegarlos aquí o mandarme el archivo. Los voy a digerir y aprender tu forma de escribir."

## Flujo si escribe para CLIENTES distintos

1. Pregunta qué clientes o perfiles existen
2. Pide guiones de cada cliente por separado
3. Guarda UN archivo de estilo POR cliente
4. Antes de escribir, pregunta para qué cliente es (si no está claro)

> "¿Cuáles son tus clientes o perfiles? Dime los nombres y después organizamos los estilos por separado."
>
> (después) "Ahora mándame unos 3-5 guiones de [cliente]. Voy a aprender su estilo por separado."

## Cómo digerir los guiones

Al recibir los guiones, analiza y extrae:

### 1. Tono general
- ¿Es más serio o más relajado?
- ¿Habla en primera persona (yo) o tercera (él/ella)?
- ¿Es directo o construye contexto antes?
- ¿Usa humor? ¿Ironía? ¿Provocación?

### 2. Ritmo de las frases
- ¿Las frases son cortas o largas? ¿Cuál es el tamaño promedio?
- ¿Alterna cortas con largas o mantiene un patrón?
- ¿Usa frases incompletas? ¿Fragmentos?
- ¿Cómo hace las pausas y las transiciones?

### 3. Palabras y expresiones recurrentes
- ¿Qué palabras aparecen en más de un guion?
- ¿Tiene expresiones que son "su sello"?
- ¿Usa modismos o regionalismos?
- ¿Cómo se dirige al público? (tú, usted, ustedes, gente, chicos)

### 4. Tipo de apertura
- ¿Cómo suele abrir? ¿Pregunta? ¿Afirmación fuerte? ¿Dato?
- ¿Entra directo al tema o prepara el terreno?
- ¿Usa alguna referencia conocida para abrir?

### 5. Estructura preferida
- ¿Cómo organiza el guion? ¿Inicio-medio-fin lineal? ¿Va y vuelve?
- ¿Cuánto tiempo dedica a la apertura vs. el desarrollo vs. el cierre?
- ¿Usa listas? ¿Ejemplos? ¿Historias?

### 6. Cierre
- ¿Cómo termina? ¿Con una lección? ¿Pregunta? ¿Llamado a la acción?
- ¿El final es emocional o práctico?

### 7. Lo que NO hace (tan importante como lo que sí hace)
- ¿Qué tipo de frase nunca usa?
- ¿Qué tono nunca adopta?
- ¿Hay algún patrón que evita?

## Guardar el estilo

Después de analizar, crea el archivo de estilo en `sofia-latam/estilos/`, dentro de la carpeta de trabajo del usuario (el directorio actual). Crea la carpeta si no existe. Nunca lo guardes dentro de la carpeta del plugin o de la skill: una actualización del plugin lo borraría.

- Si es un solo perfil: `sofia-latam/estilos/mi-estilo.md`
- Si es por cliente: `sofia-latam/estilos/[nombre-del-cliente].md`

Estos archivos pueden tener nombres de clientes y fragmentos de sus guiones: son del usuario y se quedan en su carpeta.

**Formato del archivo de estilo:**

```markdown
# Estilo: [nombre del perfil o cliente]

## Tono
[descripción en 2-3 frases]

## Ritmo
- Tamaño promedio de las frases: [cortas/medias/largas]
- Patrón: [ej: alterna cortas con una larga]
- Usa fragmentos: [sí/no]

## Palabras y expresiones recurrentes
- [lista de las palabras/expresiones que más usa]

## Cómo se dirige al público
[ej: "tú", siempre informal, nunca "ustedes"]

## Tipo de apertura preferida
[ej: pregunta provocadora, dato sorprendente]

## Estructura preferida
[ej: abre con conflicto, desarrolla con ejemplos, cierra con lección]

## Cierre típico
[ej: pregunta reflexiva, sin CTA explícito]

## Lo que NUNCA hace
- [lista de lo que evitar en este estilo]

## Frases de referencia
[3-5 frases de los guiones que representan bien el estilo — para consultar, no para copiar]
```

Después de guardar, confirma:

> "Listo, aprendí tu estilo. Lo guardé en `sofia-latam/estilos/` y lo voy a usar en los próximos guiones. ¿Quieres que escriba algo ahora?"

Si es por cliente:
> "Guardé el estilo de [cliente]. Cuando escriba para él, voy a usar esta base. ¿Quieres mandarme guiones de otro cliente ahora?"

## Usar el estilo al escribir

Antes de escribir cualquier guion, verifica si existe un archivo de estilo:

1. Si existe UN estilo en `sofia-latam/estilos/` (por ejemplo, `mi-estilo.md`): úsalo automáticamente
2. Si existen VARIOS estilos: pregunta "¿Este guion es para qué perfil? [lista los nombres]"
3. Si no existe ninguno: ofrece aprenderlo (ver el inicio de este archivo)

Al escribir, el estilo aprendido tiene PRIORIDAD sobre las reglas genéricas de tono. Si el estilo del usuario usa frases más largas que el estándar, respétalo. Si usa palabras que normalmente estarían "prohibidas", respétalo — es su estilo.

**La única excepción:** nunca violes las reglas de nunca inventar y nunca plagiar, sin importar el estilo.
