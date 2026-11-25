# Pasadas: el equipo de Sofia donde no hay agentes

En Claude Code, cada rol del equipo es un agente del plugin. En ChatGPT, en Claude en la web o en el celular y en cualquier app donde los agentes no abren, el mismo plan corre en **pasadas**: haces un rol a la vez, en la propia conversación, y lees la parte del método de ese rol en el momento de usarla.

Qué piezas lee y qué tarjetas revisa cada rol, en cada etapa, está en [tarjetas](tarjetas.md), sección "Por rol". Las tarjetas son reglas con código: el texto de cada una es la pregunta de revisión (pasa, falla o no aplica).

## Sumario

1. Las reglas de toda pasada
2. Lluvia de ideas (idea, burbuja e investigación)
3. Investigación
4. Hook
5. Guion
6. Ajuste
7. Crítica y pulir
8. Codex
9. Herramientas opcionales de Sofia

## 1. Las reglas de toda pasada

- **Escribir separado de revisar.** Primero escribe todo, sin mostrar. Después revisa, como revisor, con las tarjetas al frente. Solo después corrige.
- **Veredicto antes de la corrección.** Para cada opción y cada tarjeta, escribe para ti pasa, falla o no aplica antes de cambiar cualquier palabra. La corrección sale de la lista de fallas.
- **Orden para juntar las fallas**, cuando dos chocan:
  1. Piso;
  2. hechos;
  3. la voz de la persona y sus preferencias (haz y evita);
  4. hook (asunto y claridad antes que estilo);
  5. burbuja;
  6. método.
- **Reglas mecánicas.** Las reglas M1 a M16 de [tarjetas](tarjetas.md) se revisan con `check_script`, si la sesión lo tiene, o a mano. Cada punto de `check_script` se confirma en su contexto (puede ser un falso positivo). Toda falla mecánica confirmada se corrige antes de pasar a los revisores.
- **Máximo 2 rondas.** En la segunda, revisa solo los códigos que fallaron. Lo que siga fallando va para la persona como observación corta.
- **Generar muchos, mostrar pocos.** Hook: de 8 a 10 escritos, de 3 a 5 mostrados, de tipos distintos y con menos fallas.
- **Una línea para la persona.** Después de revisar, di solo que el texto pasó por la revisión del equipo. La tabla de veredictos queda para cuando la pida.
- **Leer una vez.** Cada pieza se lee una vez por conversación, mientras siga en ella; después de un resumen de la conversación, léela de nuevo. El resumen de una pieza (`sin-slop-resumen`, `principios-resumen`) no sustituye la pieza entera cuando el rol pide la entera.
- **Muchos pasos en una respuesta.** Si la app corta la respuesta, junta pasos: los revisores de una etapa se pueden revisar en un solo bloque, con todas sus tarjetas, siempre con un veredicto por tarjeta.

## 2. Lluvia de ideas (idea, burbuja e investigación)

1. Lee las piezas del rol `estratega-de-ideas` (etapa idea). Arma, sin mostrar, de 3 a 5 direcciones en el [modelo de idea](modelo-de-idea.md) y hasta 5 preguntas, de la que más cambia la dirección a la que menos.
2. Lee las piezas del rol `especialista-en-burbuja` (etapa idea). Arma 2 o 3 burbujas candidatas con el plan de investigación de cada una. Si ya hay tema, haz junto la primera investigación, por la parte 3.
3. Esas piezas entran una vez por conversación. Si la respuesta de la persona cambia la dirección, relee solo las tarjetas del rol.
4. Conversa: una pregunta a la vez, la más valiosa primero. Anota cada decisión en la ficha del video: la burbuja, los hallazgos, la idea y el formato, los bloques y, con el OK de la persona, la preferencia.
5. Cerrar la idea: revisa como `revisor-de-estructura` (tarjetas MI, PV, RU, EV) y como `especialista-en-burbuja` (tarjetas FB, IC, PB). Veredicto por tarjeta, corrección, y la regla M16 (formato, estructura y elementos declarados).

## 3. Investigación

1. Con búsqueda en internet o una herramienta de investigación disponible: lee las piezas del rol `investigador` e investiga por ellas. Cada hallazgo sale marcado (tipo, acceso, fecha, salvedad y enlace), los comentarios tal como fueron escritos, sin @, y lo que quedó sin fuente va a "No verificado".
2. Sin cómo investigar: muestra cómo activar la búsqueda en la app que la persona usa, solo los pasos de esa app. Si la propia persona pide usar una herramienta que ya tiene, sigue su pedido, solo con su OK y con la estimación de costo.
3. Si no se puede, sigue [investigación manual](investigacion-manual.md): qué buscar, dónde, qué capturas de pantalla tomar y cómo mandarlas.
4. Cada captura que llegue se vuelve:
   - comentario guardado tal como fue escrito, con los me gusta como aparecen y el enlace, si lo hay;
   - hecho con acceso "captura" y la fecha que muestra la captura;
   - "No verificado", para lo que no tiene fuente. Eso queda fuera del guion.

## 4. Hook

1. Lee las piezas del rol `redactor-de-hook` (etapa hook), con el formato, la estructura, la burbuja y la semilla de la ficha.
2. Escribe de 8 a 10 opciones, sin mostrar: texto hablado, texto en pantalla, lo que se ve en los primeros 2 a 3 segundos, lo que viene justo después, tipo de hook y elementos, por qué atrapa a esta burbuja. Usa las frases de la persona en esta conversación tal como las dijo.
3. Reglas mecánicas (M1 a M16, o `check_script`). Corrige toda falla confirmada.
4. Revisa como `revisor-de-lo-que-no-se-hace` (P, SS, FH9 a FH12, LS, GL), `revisor-de-hook` (FH, ZF, HQ, FM.H), `revisor-de-voz` (VZ, LS, SS21) y `especialista-en-burbuja` (FB, IC, PB).
5. Veredicto por tarjeta, para cada opción. Junta las fallas por el orden de la parte 1 y corrige. Ronda 2 solo en los códigos que fallaron.
6. Muestra de 3 a 5 y 2 estilos de grabación, con la línea de la revisión. Espera la elección y anota en la ficha el hook (solo el texto hablado) y el estilo. Si elige solo uno de los dos, anótalo y pregunta por el otro.

## 5. Guion

Igual que el hook, con estos cambios:

- El que escribe es el `guionista`, con 2 o 3 versiones (una, si la persona la pidió), cada una con estructura o enfoque distinto.
- Revisores, equipo completo: `revisor-de-lo-que-no-se-hace`, `revisor-de-hook` (solo el hook y la zona de fijación: FH1 a FH8, ZF, FM.H), `revisor-de-voz` (VZ, CE, LS, SS21), `especialista-en-burbuja` (FB, IC, PB), `revisor-de-estructura` (ES, FM, EV, PV, RU) y `revisor-de-hechos` (FT, RU1 a RU10, PM, PB). Con seis roles, revisa en dos grupos de tres.
- Equipo económico, si la persona pide algo rápido: `revisor-de-lo-que-no-se-hace`, `revisor-de-estructura` y `revisor-de-voz`. Dile que la revisión fue corta.
- Corre `check_script`, si está, en cada versión terminada antes de entregar, y revisa cada punto que devuelva en su contexto (puede ser un falso positivo).
- La lista de grabación va junto, aparte del guion. Fuera del guion, cuenta el origen de los fragmentos que vinieron de comentarios.

## 6. Ajuste

- Cambia solo el fragmento pedido. El resto queda palabra por palabra.
- Reglas mecánicas sobre el fragmento nuevo y sobre la versión nueva entera.
- Revisa como `revisor-de-lo-que-no-se-hace` (P, SS, LS, GL) y `revisor-de-voz` (VZ, CE, LS), solo sobre el fragmento cambiado.
- Cuando el ajuste cambia un bloque entero, escribe con las piezas del `guionista` (etapa ajuste).
- La versión nueva se suma a la ficha y dice de qué versión nació. Ninguna versión se borra.

## 7. Crítica y pulir

1. Reglas mecánicas sobre la versión elegida: cada falla mecánica se vuelve una marca lista, con el código M.
2. Revisa con los revisores del guion y el `critico` (CR), en dos grupos si queda largo. Cada falla se vuelve una marca: fragmento exacto, tipo (cortar, cambiar, reforzar o duda), comentario en palabras simples con el principio entre paréntesis, sugerencia y los códigos.
3. Quita las marcas repetidas y ordena de lo que más cambia el video a lo que menos.
4. En la crítica, las fallas se vuelven marcas: no detienen la entrega.
5. Muestra las marcas en una tabla numerada (número, fragmento, por qué cambiar, sugerencia). El código de la regla queda en la ficha; en el comentario, el principio va en palabras.
6. La persona responde ("acepto 1 y 3, rechazo 2"). Con todas respondidas, arma la versión nueva y súmala a la ficha. Detalle en [crítica](flujos/critica.md).

## 8. Codex

El plugin de Codex no trae los archivos de agente, pero Codex tiene subagentes propios. Para cada rol del plan, abre un subagente (el estándar sirve) con esta instrucción:

> Actúa como {rol} de Sofia en la etapa {etapa}. En la skill sofia-latam, lee `references/tarjetas.md` (sección "Por rol", {rol}, etapa {etapa}) y las piezas que esa sección lista, y sigue sus reglas. Si escribes, devuelve el texto; si revisas, devuelve un veredicto por tarjeta (pasa, falla o no aplica) para cada opción, con el fragmento y la corrección cuando falla. Solo lee y devuelve: no guardes archivos. {el texto a revisar o las notas de la conversación y la ficha del video}

Los revisores corren juntos. Junta los veredictos como en la parte 1 y sigue los pasos de la etapa. Si los subagentes no abren, sigue las pasadas de esta página.

## 9. Herramientas opcionales de Sofia

Si la sesión tiene las herramientas de Sofia:

- `check_script` revisa las reglas mecánicas (frases y moldes con cara de IA, metalenguaje de comentarios, tiempo estimado de habla) y devuelve puntos para revisar. Córrelo en todo guion terminado antes de entregar y revisa cada punto en su contexto: es una señal automática, puede ser un falso positivo, y la herramienta cubre solo una parte del Piso. Su límite de 15 palabras en la primera frase y las palabras por minuto de la estimación son referencias de la herramienta, no reglas del método: el método pide un hook de 1 a 3 frases cortas.
- `read_method_piece` abre una pieza por su id, la ruta relativa a `references/` sin `.md` (por ejemplo `tarjetas`, `formatos/vlog`, `estructuras-de-guion/ihc`). `list_method_pieces` muestra la lista.

Sin ellas, todo se hace con los archivos de esta carpeta y las reglas M1 a M16 se revisan a mano.
