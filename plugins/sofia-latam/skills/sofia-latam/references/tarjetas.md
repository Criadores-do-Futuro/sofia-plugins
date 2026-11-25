# Tarjetas de revisión de Sofia

Cada tarjeta es una regla con código. El texto de la tarjeta es la pregunta de revisión: pasa, falla o no aplica.

Los códigos se leen así:

- **FM** son las reglas de escritura del formato de la ficha del video (`FM.<formato>.<n>`) y **FM.H** es el tipo de hook de ese formato.
- **ES** es el checklist de la estructura de la ficha (`ES.<estructura>.<n>`).
- **@formato**, **@estructura**, **@ejemplo** y **@dominantes** son las piezas del formato, de la estructura, del ejemplo analizado (si el formato tiene uno) y de los elementos dominantes del formato elegidos en la ficha.
- **@hook-del-formato** es la sección "Tipo de hook" de la pieza del formato.

Los demás códigos son los de cada pieza (P, CE, EV, FT, FH, FB, GL, CR, IC, HQ, LS, MI, PB, PM, PV, RU, SS, VZ, ZF).

## Reglas mecánicas (M1 a M16)

Si la sesión tiene la herramienta `check_script` de Sofia, ella revisa parte de estas reglas de forma automática y devuelve puntos para revisar, que pueden ser falsos positivos. Si no, se revisan a mano, una por una.

- **M1** (falla). Sin raya (—).
- **M2** (falla). Sin adverbio terminado en -mente.
- **M3** (falla). Sin el molde de contraste binario de la pieza `sin-cara-de-ia`: afirma directo.
- **M4** (falla). Resultado comparado con "lo normal del perfil", sin términos de estadística.
- **M5** (falla). El comentario entra como texto del propio creador, sin metalenguaje.
- **M6** (falla). Sin las frases prohibidas de la pieza `sin-cara-de-ia`.
- **M7** (falla). Texto en pantalla de 3 a 5 palabras, en hasta 2 líneas.
- **M8** (falla). Texto hablado del hook con hasta 3 frases.
- **M9** (falla). Hook sin saludo ni introducción al comienzo.
- **M10** (aviso). Problema dicho con "tú", y no en primera persona.
- **M11** (aviso). Tres frases seguidas del mismo largo.
- **M12** (aviso). Pregunta solo en el llamado final o cuando vino de un comentario.
- **M13** (aviso). Número que no aparece en la investigación de la ficha.
- **M14** (aviso). Frase que abre con "qué", "por qué" o "cómo" en lugar de la afirmación.
- **M15** (aviso). Voz pasiva: di quién hace.
- **M16** (falla). En la idea, formato, estructura y elementos declarados.

## Por rol

### Estratega de ideas (estratega-de-ideas)
- idea (produce): tarjetas MI, PV, RU; piezas modelo-de-idea, principios, reglas-universales, formatos/README, estructuras-de-guion/README, elementos-adictivos/README, intencion-de-comando-resumen, romper-la-burbuja-resumen, conocimiento/principios-ejemplos, glosario.

### Especialista en burbuja (especialista-en-burbuja)
- idea (produce): tarjetas FB, IC, PB; piezas romper-la-burbuja, intencion-de-comando, investigacion-de-burbuja, conocimiento/arquetipos-nichos-burbujas.
- hook (revisa): tarjetas FB, IC, PB; piezas romper-la-burbuja, intencion-de-comando-resumen, investigacion-de-burbuja.
- guion (revisa): tarjetas FB, IC, PB; piezas romper-la-burbuja, intencion-de-comando, investigacion-de-burbuja.
- crítica (revisa): tarjetas FB, IC, PB; piezas romper-la-burbuja, intencion-de-comando, investigacion-de-burbuja.

### Investigador (investigador)
- idea (produce): tarjetas FT, PB, PM; piezas hechos-y-fuentes, investigacion-de-burbuja, investigacion-manual, reglas-universales.
- investigación (produce): tarjetas FT, PB, PM; piezas hechos-y-fuentes, investigacion-de-burbuja, investigacion-manual, reglas-universales.

### Redactor de hook (redactor-de-hook)
- hook (produce): tarjetas P, FH, ZF, HQ, VZ, SS, LS, GL, FM.H; piezas piso, hacer-hook, zona-de-fijacion, conocimiento/hooks-que-funcionan, conocimiento/arquetipos-nichos-burbujas, flujos/guion, @formato, @ejemplo, @dominantes, voz-del-creador, lenguaje-simple, sin-slop-resumen, principios-resumen, romper-la-burbuja-resumen.

### Guionista (guionista)
- guion (produce): tarjetas P, ES, FM, EV, ZF, IC, FB, FT, VZ, LS, GL, CE, RU; piezas piso, flujos/guion, @estructura, @formato, zona-de-fijacion, @dominantes, @ejemplo, voz-del-creador, como-escribir, hechos-y-fuentes, intencion-de-comando-resumen, romper-la-burbuja-resumen, reglas-universales, lenguaje-simple, sin-slop-resumen.
- ajuste (produce): tarjetas P, SS, LS, GL, VZ, CE; piezas piso, voz-del-creador, como-escribir, lenguaje-simple, sin-slop-resumen.

### Revisor de lo que no se hace (revisor-de-lo-que-no-se-hace)
- hook (revisa): tarjetas P, SS, FH9-FH12, LS, GL; piezas piso, sin-cara-de-ia, hacer-hook, lenguaje-simple, glosario.
- guion (revisa): tarjetas P, SS, FH9-FH12, LS, GL; piezas piso, sin-cara-de-ia, hacer-hook, lenguaje-simple, glosario.
- ajuste (revisa): tarjetas P, SS, LS, GL; piezas piso, sin-cara-de-ia, lenguaje-simple, glosario.
- crítica (revisa): tarjetas P, SS, FH9-FH12, LS, GL; piezas piso, sin-cara-de-ia, hacer-hook, lenguaje-simple, glosario.

### Revisor de hook (revisor-de-hook)
- hook (revisa): tarjetas FH, ZF, HQ, FM.H; piezas hacer-hook, zona-de-fijacion, conocimiento/hooks-que-funcionan, @hook-del-formato.
- guion (revisa): tarjetas FH1-FH8, ZF, FM.H; piezas hacer-hook, zona-de-fijacion, @hook-del-formato.
- crítica (revisa): tarjetas FH1-FH8, ZF, FM.H; piezas hacer-hook, zona-de-fijacion, @hook-del-formato.

### Revisor de voz (revisor-de-voz)
- hook (revisa): tarjetas VZ, LS, SS21; piezas voz-del-creador, lenguaje-simple, sin-cara-de-ia.
- guion (revisa): tarjetas VZ, CE, LS, SS21; piezas voz-del-creador, como-escribir, lenguaje-simple, sin-cara-de-ia.
- ajuste (revisa): tarjetas VZ, CE, LS; piezas voz-del-creador, como-escribir, lenguaje-simple.
- crítica (revisa): tarjetas VZ, CE, LS, SS21; piezas voz-del-creador, como-escribir, lenguaje-simple, sin-cara-de-ia.

### Revisor de estructura (revisor-de-estructura)
- idea (revisa): tarjetas MI, PV, RU, EV; piezas modelo-de-idea, @formato, @estructura, elementos-adictivos/README, principios, reglas-universales.
- guion (revisa): tarjetas ES, FM, EV, PV, RU; piezas @estructura, @formato, elementos-adictivos/README, @dominantes, principios, reglas-universales.
- crítica (revisa): tarjetas ES, FM, EV, PV, RU; piezas @estructura, @formato, elementos-adictivos/README, @dominantes, principios, reglas-universales.

### Revisor de hechos (revisor-de-hechos)
- guion (revisa): tarjetas FT, RU1-RU10, PM, PB; piezas hechos-y-fuentes, reglas-universales, investigacion-manual.
- crítica (revisa): tarjetas FT, RU1-RU10; piezas hechos-y-fuentes, reglas-universales.

### Crítico (critico)
- crítica (revisa): tarjetas CR; piezas flujos/critica, diagnostico, principios-resumen.

## Las tarjetas, por pieza

### como-escribir (como-escribir.md)

- **CE1.** El texto suena como la persona habla, con palabras y giros de todos los días (sección 1).
- **CE2.** Las frases son cortas y pegan fuerte, y las largas son la excepción (sección 2).
- **CE3.** "Y", "Entonces" y "Pero" abren frase donde suena natural (sección 3).
- **CE4.** El texto narra la escena en vez de describirla (sección 4).
- **CE5.** Hay un "pero" que da vuelta la historia en el punto justo (sección 5).
- **CE6.** Pregunta solo en el llamado final o cuando vino de un comentario (sección 6).
- **CE7.** Detalle específico en lugar de afirmación genérica (sección 7).
- **CE8.** La emoción sube escalón por escalón, sin bajar (sección 8).
- **CE9.** El último tercio sale del personaje y llega a la vida de quien mira (sección 9).
- **CE10.** Las palabras crean imagen: verbo de acción y detalle concreto (sección 10).
- **CE11.** Después de 2 o 3 frases de contexto, el impacto llega en una frase corta (sección 11).
- **CE12.** La persona y la situación aparecen por su comportamiento, y quien mira ve la escena (sección 12).
- **CE13.** Después de una historia pesada, el cierre es simple y ligero (sección 13).
- **CE14.** La contradicción, cuando se usa, tiene las dos partes cortas y pegadas (sección 14).
- **CE15.** El CTA continúa el tema del video, o no hay CTA (sección 15).
- **CE16.** Cada hecho dice quién hizo qué, cuánto, para qué y cuándo, si la fuente lo dice (parte 1).
- **CE17.** El cambio de bloque parte de un pedazo concreto del bloque anterior, sin frase de transición anunciada (parte 1).
- **CE18.** La salvedad entra dentro de la historia, en la voz de quien habla, sin aviso pegado en el medio (parte 1).
- **CE19.** La palabra de duda ("parece que", "supuestamente") va solo donde la duda es real, una vez, diciendo quién lo afirma (parte 1).
- **CE20.** Cada bloque tiene una emoción definida para quien mira (parte 1).
- **CE21.** Los elementos adictivos están en el texto, sentidos por quien mira, y ninguno aparece por su nombre en el guion (parte 1).
- **CE22.** Cada bloque tiene escena, detalle y giro: el guion no se volvió una lista de puntos (parte 1).

### elementos-adictivos/README (elementos-adictivos/README.md)

- **EV1.** El tema hace parar y la moraleja sale de él sin forzar.
- **EV2.** La primera frase despierta un sentimiento que la burbuja conoce, y la emoción no muere después del comienzo.
- **EV3.** Hay conflicto con cambio, y el cambio combina con el conflicto.
- **EV4.** La curiosidad abre en el hook y cierra con un "aha" claro, o queda abierta a propósito, con la elección dicha a la persona.
- **EV5.** El contraste tiene propósito y se resuelve al final.
- **EV6.** Las palabras son del día a día del público y crean imagen; alguien de afuera del nicho entiende.
- **EV7.** Cada bloque tiene al menos un elemento activo, y los elementos dominantes del formato aparecen.

### estructuras-de-guion/aida (estructuras-de-guion/aida.md)

- **ES.aida.1.** ¿El tema es interesante para la burbuja?
- **ES.aida.2.** ¿La apertura tiene curiosidad o conflicto?
- **ES.aida.3.** ¿El medio prueba el punto con historia, datos o enseñanza?
- **ES.aida.4.** ¿La moraleja genera deseo emocional?
- **ES.aida.5.** ¿Está el CTA (directo o indirecto)?

### estructuras-de-guion/analisis (estructuras-de-guion/analisis.md)

- **ES.analisis.1.** ¿El hook es un clip del analizado que se entiende solo en hasta 4 s?
- **ES.analisis.2.** ¿La etiqueta es exagerada, graciosa y no ofende a quien mira?
- **ES.analisis.3.** ¿Seguidores + vistas + un detalle singular, antes de la promesa?
- **ES.analisis.4.** ¿La promesa cae entre los 19 y los 26 s, con el analizado como sujeto?
- **ES.analisis.5.** ¿Tres principios, cada uno con nombre → prueba → mecánica → lección → puente?
- **ES.analisis.6.** ¿Al menos un principio bautizado con algo del propio analizado?
- **ES.analisis.7.** ¿El último principio es el pilar de tu método o producto?
- **ES.analisis.8.** ¿Quien presenta solo habla de sí en el cierre?
- **ES.analisis.9.** ¿Hay un giro hacia el espectador antes del CTA?
- **ES.analisis.10.** ¿Los clips del analizado suman entre 8 y 16 % del tiempo, cada uno de hasta 7 s, con el remate (punchline) al final?
- **ES.analisis.11.** ¿Las groserías solo en boca del analizado, y ninguna en un tema sensible?

### estructuras-de-guion/el-yo-tu-futuro (estructuras-de-guion/el-yo-tu-futuro.md)

- **ES.el-yo-tu-futuro.1.** ¿El "Él" genera curiosidad sobre alguien real?
- **ES.el-yo-tu-futuro.2.** ¿El "Yo" muestra vulnerabilidad o una postura genuina?
- **ES.el-yo-tu-futuro.3.** ¿El "Tú" trae al público dentro de la historia?
- **ES.el-yo-tu-futuro.4.** ¿El "Futuro" proyecta algo que el público quiere alcanzar?
- **ES.el-yo-tu-futuro.5.** ¿El mensaje final está claro antes de empezar a escribir?

### estructuras-de-guion/ihc (estructuras-de-guion/ihc.md)

- **ES.ihc.1.** ¿La identificación hace que el público piense "soy yo"?
- **ES.ihc.2.** ¿La historia tiene conflicto, giro y consecuencia?
- **ES.ihc.3.** ¿El contenido planta una semilla clara en la cabeza del público?
- **ES.ihc.4.** ¿El tono es de conversación (sin cara de clase)?

### estructuras-de-guion/modo-incorrecto-modo-correcto (estructuras-de-guion/modo-incorrecto-modo-correcto.md)

- **ES.modo-incorrecto-modo-correcto.1.** ¿El conflicto es un dolor real del público?
- **ES.modo-incorrecto-modo-correcto.2.** ¿El modo incorrecto es algo que el público reconoce que hace?
- **ES.modo-incorrecto-modo-correcto.3.** ¿El giro es creíble y específico?
- **ES.modo-incorrecto-modo-correcto.4.** ¿El modo correcto es claro y aplicable?
- **ES.modo-incorrecto-modo-correcto.5.** ¿El cambio muestra un resultado concreto?

### hechos-y-fuentes (hechos-y-fuentes.md)

- **FT1.** Cada hecho, número y caso del texto aparece en la investigación de la ficha, con fuente.
- **FT2.** Lo que quedó sin fuente está fuera del texto y listado en "No verificado".
- **FT3.** Acusación, versión de una de las partes, opinión e hipótesis entran como tales, diciendo de quién son.
- **FT4.** El texto cuenta la versión más nueva del hecho.
- **FT5.** Número redondeado hacia abajo, y comparación solo con una cuenta hecha a partir de un dato verificado.
- **FT6.** Motivo, dinero y uso de IA solo aparecen con fuente.
- **FT7.** El comentario usado en el guion entró como texto del propio creador, sin comillas y sin metalenguaje.
- **FT8.** Las palabras del comentario quedaron cerca del original, con el ajuste justo para que sea coherente y se pueda decir en voz alta.
- **FT9.** Un hallazgo sacado de una captura de pantalla dice que vino de una captura y trae la fecha que la captura muestra.

### hacer-hook (hacer-hook.md)

- **FH9.** Tardar en decir el asunto. Saludo ("hola, gente", "¿qué tal, amigos?"), introducción o rodeo como "hoy vi lo más increíble del mundo", sin decir el asunto. El público se va en los 2 primeros segundos. Corta lo que enreda y di el asunto exacto en el primer o el segundo segundo.
- **FH10.** Confundir. Frase larga, en voz pasiva, cortada a la mitad o con dos sentidos. Si la persona necesita parar para descifrar la frase, la salta. Voz activa, palabras del día a día y el menor número de palabras.
- **FH11.** Parecer que no es para ella. La persona entiende el asunto, pero no se ve en él. Pasa mucho cuando el creador habla de sí: "Yo tengo este problema" crea distancia. Háblale a quien mira ("Si tú pasas por este problema", "tu negocio") y ancla la frase en un dolor que la persona conoce o en un resultado práctico que quiere.
- **FH12.** No dar ganas de saber más. El hook es claro y es para ella, pero no abre ninguna curiosidad. El contraste lo resuelve: lo que la mayoría hace o cree, junto a un modo más rápido, más simple o inesperado que funciona (paso 3).
- **FH1.** En 2 segundos se puede saber de qué trata el video y qué se gana.
- **FH2.** Un asunto y una duda, sin saludo, introducción ni rodeo.
- **FH3.** Lo que se dice tiene de 1 a 3 frases cortas, en voz activa, con el asunto en las primeras palabras y lo que está en juego.
- **FH4.** El texto en pantalla tiene de 3 a 5 palabras, en hasta dos líneas.
- **FH5.** Imagen, texto y lo que se dice tratan de la misma cosa (sin sonido y solo escuchando).
- **FH6.** El problema se dice con "tú".
- **FH7.** Un contraste concreto da ganas de saber más.
- **FH8.** El segundo siguiente entrega valor y abre la zona de fijación (pieza `zona-de-fijacion`).

### formatos/analisis (formatos/analisis.md)

- **FM.analisis.H.** Un clip del propio analizado, de 4 s como máximo, que se entiende solo y termina en el remate (punchline). Enseguida, una etiqueta exagerada sobre algo inofensivo de él (noticia falsa cómica, "el/la X más Y de internet" o insulto cariñoso), convertida en elogio con "La verdad es que…".
- **FM.analisis.1.** Hook = clip del analizado (hasta 4 s, autosuficiente, remate al final). Sin un clip así, cambia de analizado.
- **FM.analisis.2.** Credencial antes de la promesa: seguidores redondeados + promedio o pico de vistas + un detalle singular.
- **FM.analisis.3.** Promesa entre los 19 y los 26 s, con el analizado como sujeto: "Por eso hoy vamos a analizar los tres principios que [nombre] usa para…".
- **FM.analisis.4.** Tres principios, cada uno en nombre → prueba (lista de 3 con anticlímax + clip que muestra solo) → mecánica → lección imperativa para "tú" → puente al siguiente.
- **FM.analisis.5.** Al menos un principio con nombre sacado del propio analizado; el último principio es el pilar del método o producto de quien presenta.
- **FM.analisis.6.** Separa el hecho verificable (números, clips) de la interpretación ("lo que yo llamo…").
- **FM.analisis.7.** Quien presenta solo habla de sí en el cierre; antes del CTA, gira hacia el espectador (pregunta espejo, regaño u objeción dramatizada).
- **FM.analisis.8.** CTA con callback al analizado: "qué pena que [nombre] no enseñe [X]… pero yo sí".
- **FM.analisis.9.** La etiqueta y las bromas nunca ofenden al propio público; la grosería, solo en boca del analizado.

### formatos/analogia (formatos/analogia.md)

- **FM.analogia.H.** Escena inmersiva con el objeto concreto en acción, sosteniendo el significado. O un contraste inesperado entre el objeto y el asunto ("Este vaso explica por qué no logras ahorrar dinero.").
- **FM.analogia.1.** Elige algo concreto y familiar cuyo funcionamiento corresponda de verdad a la idea.
- **FM.analogia.2.** Muestra o cuenta la situación antes de explicar el significado.
- **FM.analogia.3.** Conserva la brecha el tiempo suficiente para generar curiosidad.
- **FM.analogia.4.** Declara el puente con claridad: "esto es lo que pasa cuando…".
- **FM.analogia.5.** Mapea solo correspondencias que se sostienen; una analogía forzada pierde credibilidad.
- **FM.analogia.6.** Cierra con una consecuencia práctica o un cambio de perspectiva.

### formatos/detras-de-camaras (formatos/detras-de-camaras.md)

- **FM.detras-de-camaras.H.** Declaración del resultado sorprendente antes de revelar el proceso ("hice X en Y tiempo: esto es lo que nadie muestra").
- **FM.detras-de-camaras.1.** Abre con el resultado, nunca con el proceso.
- **FM.detras-de-camaras.2.** Usa el guion para construir la narrativa del proceso como una secuencia de descubrimientos.
- **FM.detras-de-camaras.3.** Incluye los errores y obstáculos reales: un detrás de cámaras sin fricción no es auténtico.
- **FM.detras-de-camaras.4.** Usa lenguaje coloquial e íntimo, como si le mostraras algo a un amigo.
- **FM.detras-de-camaras.5.** El giro narrativo es el momento en que algo salió mal (o muy bien) de forma inesperada.
- **FM.detras-de-camaras.6.** El Efecto Aha es la revelación de lo que de verdad importó en el proceso.
- **FM.detras-de-camaras.7.** La moraleja debe ser una lección aprendida en el proceso, no una teoría previa.
- **FM.detras-de-camaras.8.** El CTA debe invitar al espectador a intentar el mismo proceso o a seguir para ver más detrás de cámaras.

### formatos/caja-de-preguntas (formatos/caja-de-preguntas.md)

- **FM.caja-de-preguntas.H.** Provocación directa: la pregunta de la caja leída en voz alta, seguida de la reacción del creador.
- **FM.caja-de-preguntas.1.** Elige una pregunta que toque una creencia, un dolor o una división real de la audiencia.
- **FM.caja-de-preguntas.2.** Muestra y lee la pregunta temprano; tiene que entenderse sin contexto extra.
- **FM.caja-de-preguntas.3.** Reacciona antes de entregar la respuesta para crear expectativa.
- **FM.caja-de-preguntas.4.** Da una posición específica, sostenida por un caso, un razonamiento o un contraste.
- **FM.caja-de-preguntas.5.** Haz que la respuesta le sirva también a quien no envió la pregunta.
- **FM.caja-de-preguntas.6.** Cierra invitando a nuevas preguntas o a tomar una postura.

### formatos/cine (formatos/cine.md)

- **FM.cine.H.** Escena inmersiva que pone al espectador dentro de un momento específico antes de cualquier contexto.
- **FM.cine.1.** Abre in media res: dentro de la escena, no antes de ella.
- **FM.cine.2.** Cada línea del guion debe corresponder a una escena o plano específico.
- **FM.cine.3.** El conflicto debe mostrarse, no explicarse.
- **FM.cine.4.** Usa diálogo o narración interna para revelar el estado emocional del personaje.
- **FM.cine.5.** El giro debe ser un momento visual claro, no solo una frase.
- **FM.cine.6.** La moraleja nunca se dice con todas las letras: emerge de la última escena.
- **FM.cine.7.** El ritmo del texto debe reflejar el ritmo del corte (frases cortas = cortes rápidos).
- **FM.cine.8.** El CTA, si lo hay, debe integrarse con naturalidad al final de la escena.

### formatos/comparacion (formatos/comparacion.md)

- **FM.comparacion.H.** Contraste inesperado que opone los dos elementos en la primera frase de una forma que sorprende.
- **FM.comparacion.1.** Presenta los dos lados con equidad antes de revelar la conclusión.
- **FM.comparacion.2.** Usa criterios claros y verificables para la comparación.
- **FM.comparacion.3.** Cada criterio comparado debe escalar el contraste, de lo más superficial a lo más profundo.
- **FM.comparacion.4.** Nunca reveles cuál es "el mejor" antes de construir la comparación completa.
- **FM.comparacion.5.** Usa ejemplos reales para cada lado: no compares en lo abstracto.
- **FM.comparacion.6.** El giro narrativo es el criterio decisivo que lo cambia todo.
- **FM.comparacion.7.** La moraleja debe ser la lección que emerge de la comparación, no la preferencia personal del creador.
- **FM.comparacion.8.** El CTA debe invitar al espectador a aplicar el criterio decisivo en su propia vida.

### formatos/conflicto-situacional (formatos/conflicto-situacional.md)

- **FM.conflicto-situacional.H.** Escena inmersiva dentro de la acción: la primera imagen y la primera frase ya están en medio del conflicto.
- **FM.conflicto-situacional.1.** Empieza dentro de la acción; no expliques la escena antes de que ocurra.
- **FM.conflicto-situacional.2.** Dale a cada personaje un objetivo simple y opuesto.
- **FM.conflicto-situacional.3.** Usa frases cortas, reactivas y naturales; un conflicto explicado suena falso.
- **FM.conflicto-situacional.4.** Planta una pregunta inmediata: "¿qué pasó?" o "¿cómo va a terminar esto?".
- **FM.conflicto-situacional.5.** Haz la transición hacia el mensaje sin romper la promesa de la apertura.
- **FM.conflicto-situacional.6.** La conclusión tiene que resignificar la escena, no solo abandonarla.
- **FM.conflicto-situacional.7.** Evita escenificaciones que puedan causar un riesgo real o engañar a terceros fuera del contexto del video.

### formatos/charla-de-bar (formatos/charla-de-bar.md)

- **FM.charla-de-bar.H.** Choque de creencia dicho como confesión ("Me tomó diez años admitir que {creencia} estaba equivocada.").
- **FM.charla-de-bar.1.** Escribe como un habla dirigida a una persona específica, no a un público.
- **FM.charla-de-bar.2.** Abre a la mitad de un pensamiento, una pregunta o una confesión.
- **FM.charla-de-bar.3.** Usa ejemplos personales, interrupciones y preguntas retóricas con moderación.
- **FM.charla-de-bar.4.** Evita las enumeraciones rígidas, los títulos hablados y el tono de clase.
- **FM.charla-de-bar.5.** Conserva una línea de razonamiento clara por debajo de la naturalidad.
- **FM.charla-de-bar.6.** Cierra como la conclusión de una conversación, no como un eslogan publicitario.

### formatos/creativo-perezoso (formatos/creativo-perezoso.md)

- **FM.creativo-perezoso.H.** Contraste inesperado visual en los primeros 3 a 6 segundos, con una frase que solo tiene sentido junto con la imagen.
- **FM.creativo-perezoso.1.** Haz que la primera frase dependa de lo que aparece en la apertura.
- **FM.creativo-perezoso.2.** Crea una pregunta visual que lo que se dice prometa resolver.
- **FM.creativo-perezoso.3.** Pasa rápido al encuadre simple sin que parezca otro video.
- **FM.creativo-perezoso.4.** Usa el resto para pagar la curiosidad creada por el hook.
- **FM.creativo-perezoso.5.** No mantengas el mismo nivel de estímulo todo el video; el contraste define el formato.
- **FM.creativo-perezoso.6.** Retoma el elemento inicial en el pago de la promesa (payoff) cuando eso refuerce la unidad.

### formatos/dialogo (formatos/dialogo.md)

- **FM.dialogo.H.** Primera frase de uno de los personajes que crea tensión o contraste inmediato sin contexto previo.
- **FM.dialogo.1.** Cada personaje debe tener voz y vocabulario distintos: el espectador necesita saber quién habla.
- **FM.dialogo.2.** El conflicto entre los personajes debe ser el motor del guion.
- **FM.dialogo.3.** Usa cortes rápidos de cámara o indicadores visuales para distinguir a los personajes.
- **FM.dialogo.4.** Cada línea debe avanzar el conflicto: nunca des vueltas.
- **FM.dialogo.5.** Uno de los personajes representa al espectador (su duda, su error, su creencia).
- **FM.dialogo.6.** El giro narrativo es el momento en que un personaje cambia de posición o es sorprendido.
- **FM.dialogo.7.** La moraleja emerge de la resolución del conflicto entre los personajes.
- **FM.dialogo.8.** El CTA debe conectar al espectador con el personaje que representa su posición actual.

### formatos/dinamismo (formatos/dinamismo.md)

- **FM.dinamismo.H.** Declaración directa de beneficio o resultado en 1 frase, seguida de un corte inmediato al primer punto.
- **FM.dinamismo.1.** Cada frase corresponde a un corte o a un movimiento de cámara: escribe corto.
- **FM.dinamismo.2.** Usa listas numeradas implícitas: el espectador debe sentir progresión.
- **FM.dinamismo.3.** Lenguaje directo y objetivo, sin introducciones largas.
- **FM.dinamismo.4.** Cada punto debe ser más sorprendente o más valioso que el anterior.
- **FM.dinamismo.5.** Varía el tipo de información: estadística → ejemplo → pregunta → afirmación.
- **FM.dinamismo.6.** Evita los conectores largos: usa los cortes para hacer la transición.
- **FM.dinamismo.7.** El Efecto Aha debe ser el punto más fuerte: colócalo en el clímax del ritmo.
- **FM.dinamismo.8.** El CTA debe entregarse en el pico de la energía: no desaceleres antes de terminar.

### formatos/experimento-social (formatos/experimento-social.md)

- **FM.experimento-social.H.** Declaración de la premisa del experimento de forma que cree expectativa inmediata ("hice X con Y personas para descubrir Z").
- **FM.experimento-social.1.** La premisa del experimento debe ser el hook: directa y específica.
- **FM.experimento-social.2.** Explica las "reglas" del experimento en 1 o 2 frases, no más.
- **FM.experimento-social.3.** Documenta las reacciones de forma imparcial: deja que el espectador saque conclusiones antes que el creador.
- **FM.experimento-social.4.** Construye suspenso antes de revelar el resultado.
- **FM.experimento-social.5.** El Efecto Aha es el resultado del experimento: guárdalo para el momento de mayor tensión.
- **FM.experimento-social.6.** La moraleja debe emerger de los resultados, no ser impuesta por el creador.
- **FM.experimento-social.7.** Usa personas reales e identificables: el anonimato debilita el impacto.
- **FM.experimento-social.8.** El CTA debe conectar el resultado del experimento con una reflexión personal del espectador.

### formatos/formato-combinado (formatos/formato-combinado.md)

- **FM.formato-combinado.H.** El hook del formato que conduce. Cuando la propia mezcla sorprende (por ejemplo, una Charla breve que se vuelve Cine a la mitad de la frase), usa un contraste inesperado.
- **FM.formato-combinado.1.** Declara para ti qué formato conduce la narrativa y cuál amplía la ejecución.
- **FM.formato-combinado.2.** Dale una función distinta a cada formato; evita duplicar el mismo efecto.
- **FM.formato-combinado.3.** Planifica dónde entra, sale o se superpone cada capa.
- **FM.formato-combinado.4.** Conserva las señales mínimas que hacen identificable a cada formato.
- **FM.formato-combinado.5.** Haz que las transiciones carguen significado, no solo variedad.
- **FM.formato-combinado.6.** Revisa el guion con las reglas de los dos formatos y resuelve los conflictos de forma consciente.
- **FM.formato-combinado.7.** Al analizar, nombra la combinación como `Formato A + Formato B`.

### formatos/lo-fi (formatos/lo-fi.md)

- **FM.lo-fi.H.** Choque de creencia o provocación directa: la opinión fuerte dicha en la primera frase, sin preparación.
- **FM.lo-fi.1.** Empieza rápido, como si la idea acabara de surgir.
- **FM.lo-fi.2.** Usa una tesis lo bastante fuerte para sostener la ausencia de una producción elaborada.
- **FM.lo-fi.3.** Escribe para el habla natural: frases cortas, muletillas y pausas.
- **FM.lo-fi.4.** Evita las introducciones formales, las listas excesivas y el texto con cara de teleprompter.
- **FM.lo-fi.5.** Conserva las imperfecciones que dan humanidad, pero corta las repeticiones que no aportan.
- **FM.lo-fi.6.** No intentes compensar la simplicidad con exceso de efectos en la edición.

### formatos/narrado (formatos/narrado.md)

- **FM.narrado.H.** Escena inmersiva o declaración de consecuencia que crea una imagen mental fuerte en la primera frase.
- **FM.narrado.1.** Cada frase debe crear una imagen mental: escribe para los ojos del espectador.
- **FM.narrado.2.** Usa frases cortas y rítmicas: la narración necesita respiro entre las frases.
- **FM.narrado.3.** Construye la narrativa como si fuera un documental en miniatura.
- **FM.narrado.4.** La progresión debe ser visual: dónde estamos → conflicto → giro → resolución.
- **FM.narrado.5.** Evita las abstracciones: todo debe poder traducirse en imagen.
- **FM.narrado.6.** Usa el tiempo verbal presente para crear inmersión ("entra", no "entró").
- **FM.narrado.7.** El Efecto Aha debe entregarse en el momento exacto en que lo visual confirma el argumento.
- **FM.narrado.8.** El CTA debe decirse como consecuencia inevitable de lo que acaba de mostrarse.

### formatos/narrador (formatos/narrador.md)

- **FM.narrador.H.** Contraste inesperado: el narrador dice algo y el personaje reacciona en contra, ya en el primer intercambio.
- **FM.narrador.1.** Dale al narrador una función clara: presentar, exponer, presionar o contradecir.
- **FM.narrador.2.** Haz que el personaje reaccione de modo visible y verbal; no escribas dos monólogos paralelos.
- **FM.narrador.3.** Alterna frases cortas para mantener el ritmo y la relación de causa y efecto.
- **FM.narrador.4.** Deja que el narrador sepa o revele algo que tensione al personaje.
- **FM.narrador.5.** Escala la interacción hasta una decisión, una confesión o un giro.
- **FM.narrador.6.** Diferencia las voces por vocabulario, intención y subtítulo, no solo por timbre.

### formatos/charla-breve (formatos/charla-breve.md)

- **FM.charla-breve.H.** Provocación directa o declaración de consecuencia que desafía una creencia del espectador.
- **FM.charla-breve.1.** El hook debe desafiar una creencia o un comportamiento que tiene el espectador.
- **FM.charla-breve.2.** No uses más de 3 argumentos por video: elige los más fuertes.
- **FM.charla-breve.3.** Cada argumento debe ser corto, directo y verificable.
- **FM.charla-breve.4.** Usa ejemplos concretos: nunca argumentes en lo abstracto.
- **FM.charla-breve.5.** El lenguaje debe sonar como el creador hablándole a un amigo, no presentando ante un público.
- **FM.charla-breve.6.** Construye hasta la moraleja como si fuera un descubrimiento, no una conclusión predicada.
- **FM.charla-breve.7.** El Efecto Aha debe ser la frase más poderosa del video: guárdalo para el final.
- **FM.charla-breve.8.** El CTA debe ser una pregunta reflexiva o una invitación a la acción inmediata.

### formatos/storytelling-visual (formatos/storytelling-visual.md)

- **FM.storytelling-visual.H.** Declaración de consecuencia visual: la primera frase crea una imagen que lo visual confirma de inmediato.
- **FM.storytelling-visual.1.** El guion debe indicar qué elementos visuales aparecen en cada tramo.
- **FM.storytelling-visual.2.** Lo que se dice y lo visual deben trabajar juntos: nunca duplicar la misma información.
- **FM.storytelling-visual.3.** Usa lo visual para probar lo que dice la voz.
- **FM.storytelling-visual.4.** La historia debe tener un arco completo: planteamiento → conflicto → giro → resolución.
- **FM.storytelling-visual.5.** Cada transición visual debe coincidir con un giro narrativo.
- **FM.storytelling-visual.6.** Usa personajes reales con historias verificables.
- **FM.storytelling-visual.7.** El Efecto Aha debe ser el momento en que lo visual y lo dicho se encuentran de forma sorprendente.
- **FM.storytelling-visual.8.** El CTA debe reforzarse con imagen, no solo decirse.

### formatos/pantalla-dividida (formatos/pantalla-dividida.md)

- **FM.pantalla-dividida.H.** Declaración de consecuencia curiosa o escena inmersiva en segunda persona.
- **FM.pantalla-dividida.1.** Abre con la consecuencia, no con el contexto.
- **FM.pantalla-dividida.2.** Usa "pero" como dispositivo técnico de contraste.
- **FM.pantalla-dividida.3.** Pon al espectador dentro de la escena con "tú" y "tu".
- **FM.pantalla-dividida.4.** Cada tramo debe intensificar el conflicto del anterior.
- **FM.pantalla-dividida.5.** El Efecto Aha es el pago de la pregunta abierta: nunca lo reveles antes de construir tensión.
- **FM.pantalla-dividida.6.** La moraleja debe girar la cámara hacia el espectador.
- **FM.pantalla-dividida.7.** Usa marcas, programas y nombres reales y verificables.
- **FM.pantalla-dividida.8.** El CTA debe ser consecuencia natural de la moraleja.

### formatos/pantalla-verde (formatos/pantalla-verde.md)

- **FM.pantalla-verde.H.** Declaración de consecuencia que apunta de frente al elemento visual de fondo.
- **FM.pantalla-verde.1.** El hook debe mencionar o apuntar de frente al visual de fondo.
- **FM.pantalla-verde.2.** Cada frase debe construirse como si lo visual fuera una prueba de lo que se dice.
- **FM.pantalla-verde.3.** Usa datos reales, capturas de pantalla verificables y nombres reconocibles.
- **FM.pantalla-verde.4.** Construye suspenso antes de revelar el Efecto Aha.
- **FM.pantalla-verde.5.** El giro narrativo debe ser el momento en que lo visual y lo dicho se alinean.
- **FM.pantalla-verde.6.** La moraleja debe sacarse de lo que el visual prueba, no de lo que opina el creador.
- **FM.pantalla-verde.7.** Usa un lenguaje analítico pero accesible, como un amigo que explica algo que descubrió.
- **FM.pantalla-verde.8.** El CTA debe conectar el insight visual con una acción específica del espectador.

### formatos/the-office (formatos/the-office.md)

- **FM.the-office.H.** Declaración directa a la cámara que crea intimidad y extrañeza al mismo tiempo.
- **FM.the-office.1.** El creador habla como si lo estuvieran filmando sin saberlo, en tono confesional.
- **FM.the-office.2.** Usa las miradas a la cámara como "comentario" sobre lo que está pasando.
- **FM.the-office.3.** El humor debe surgir del contraste entre lo que se dice y lo que es obvio.
- **FM.the-office.4.** La ironía debe ser sutil: nunca expliques el chiste.
- **FM.the-office.5.** La situación narrada debe ser reconocible y embarazosa o verdadera para casi todos.
- **FM.the-office.6.** La moraleja emerge como una confesión, no como una enseñanza.
- **FM.the-office.7.** Usa pausas y silencios estratégicos: el ritmo de The Office es lo que crea el humor.
- **FM.the-office.8.** El CTA debe entregarse con el mismo tono confesional del resto del video.

### formatos/trivial (formatos/trivial.md)

- **FM.trivial.H.** Choque de creencia dicho como confesión, con el objeto en las manos.
- **FM.trivial.1.** Escribe como una conversación paralela a la actividad, no como una presentación formal.
- **FM.trivial.2.** Abre con una observación íntima, una confesión o una frase que alguien diría en la cocina.
- **FM.trivial.3.** Usa el objeto o la actividad cuando refuerce la idea, sin convertir todo en un tutorial.
- **FM.trivial.4.** Usa frases cortas, pausas y pequeñas digresiones naturales.
- **FM.trivial.5.** Conserva un punto central claro para que la espontaneidad no se vuelva dispersión.
- **FM.trivial.6.** Cierra con una conclusión simple, como quien termina un pensamiento en voz alta.

### formatos/vlog (formatos/vlog.md)

- **FM.vlog.H.** Escena inmersiva del momento más fuerte del vlog, o declaración de consecuencia ("Fui a {lugar} pensando que {expectativa}. Volví {cambio}.").
- **FM.vlog.1.** Define la promesa del recorrido: qué va a pasar, decidirse o descubrirse.
- **FM.vlog.2.** Narra las transiciones que la imagen sola no explica, sin describir lo obvio.
- **FM.vlog.3.** Selecciona momentos que cambian el estado de la historia; no hagas un catálogo de todo lo que pasó.
- **FM.vlog.4.** Incluye un obstáculo, una sorpresa o una decisión para crear progresión.
- **FM.vlog.5.** Alterna la presencia en cámara, el ambiente y los detalles para darle textura a la experiencia.
- **FM.vlog.6.** Termina mostrando el resultado y qué cambió para el creador.

### romper-la-burbuja (romper-la-burbuja.md)

- **FB1.** La burbuja tiene nombre de tema o de comunidad, pasa la prueba rápida y es de uno de los 6 tipos.
- **FB2.** El tema, la intención de comando y el punto en común están claros, sin unión forzada.
- **FB3.** La apertura activa identificación o conflicto con las palabras de la burbuja.
- **FB4.** La transición llega al punto en común sin corte de tema.
- **FB5.** El cierre entrega la intención de comando con un llamado a la acción claro.
- **FB6.** Los comentarios usados están en las palabras del público, como texto del creador, sin comillas y sin metalenguaje.
- **FB7.** El nombre de una persona real solo aparece con un hecho que tiene fuente.
- **FB8.** El formato creativo sigue lo que ya funciona (90/10).

### glosario (glosario.md)

- **GL1.** Un término del método (hook, CTA, burbuja, retención, B-roll y los otros de esta pieza) aparece ante la persona como dice la columna "Cómo explicarlo", o con esa explicación en la misma frase.

### flujos/critica (flujos/critica.md)

- **CR1.** El tema hace parar y la moraleja cabe en una frase.
- **CR2.** La primera frase despierta una emoción.
- **CR3.** Existe conflicto, y el cambio aparece.
- **CR4.** El hook abre una pregunta y el guion la responde.
- **CR5.** Todo nombre tiene contexto antes.
- **CR6.** Un niño de 8 años entiende a la primera vez que lo escucha.
- **CR7.** Tres frases seguidas no tienen el mismo largo, y ningún párrafo termina en frase de efecto.

### intencion-de-comando (intencion-de-comando.md)

- **IC1.** El guion planta una sola semilla, de un pilar, escrita en la idea de la ficha.
- **IC2.** La semilla sale de las notas del perfil o de lo que la persona dijo en la conversación, sin mecanismo, historia ni creencia inventados.
- **IC3.** Autenticidad y movimiento aparecen dentro de la historia, sin pausa para propaganda.
- **IC4.** El cierre refuerza una creencia del movimiento.
- **IC5.** El llamado a la acción tiene tipo: escondido (con un caso real) o directo (cerca de 2 de cada 10 videos).

### conocimiento/hooks-que-funcionan (conocimiento/hooks-que-funcionan.md)

- **HQ1.** La opción 1 es un choque de creencia: la creencia del público puesta al revés, dicha como orden, confesión o consecuencia absurda.
- **HQ2.** El choque es verdad, u opinión sincera del creador probada en el video, y el texto señala dónde el video paga el choque.
- **HQ3.** Ninguna opción promete resultado ("vas a crecer", "vas a facturar").
- **HQ4.** Cada opción declara uno de los tipos de hook de esta pieza, y el tipo combina con el formato de la ficha.
- **HQ5.** Las opciones tienen tipos distintos entre sí.
- **HQ6.** Cada opción trae un dato concreto (nombre, número, hecho) o una persona o marca que el público conoce, cuando la investigación lo tiene.
- **HQ7.** Cada opción dice en qué bloque del guion el video paga la duda del hook.
- **HQ8.** Ninguna opción abre con saludo, anuncio ("en este video vas a ver", "¿sabías que", "quédate hasta el final"), pregunta retórica o comentario de video sin el asunto en la misma frase o en la siguiente.

### lenguaje-simple (lenguaje-simple.md)

- **LS1.** Hook y guion simples, siempre. Escribe para quien nunca oyó hablar del asunto: tan simple que un niño de 8 años lo entienda, sin tono de quien le habla a un niño. Una idea por frase, frases cortas y palabras del día a día. Un término técnico solo si el público lo usa, y explicado al momento con un ejemplo cotidiano. Un número difícil se vuelve una comparación fácil. El video también queda simple: un solo asunto, pocos pasos y nada que obligue a pausar para entender. Si una frase hay que leerla dos veces, reescríbela.
- **LS2.** En la crítica, lo que cuesta entender se vuelve una marca de cambiar, con la versión simple en el comentario: palabra difícil, frase larga, término técnico sin explicación, número sin comparación o dos ideas en la misma frase.
- **LS3.** Contexto antes del nombre: "la dueña de la panadería de la esquina, doña Rosa".
- **LS4.** Un número grande se vuelve imagen, con una cuenta hecha a partir de un dato verificado.
- **LS5.** El resultado de un video se compara con "lo normal del perfil" ("3 veces lo normal del perfil", "cerca de lo normal").
- **LS6.** Si necesitas tomar aire en medio de la frase, está larga: divídela.

### modelo-de-idea (modelo-de-idea.md)

- **MI1.** Burbuja y semilla siempre. La burbuja tiene nombre de tema o de comunidad; un nombre de estado o de dificultad va en el "Para quién". La semilla es una sola, de un pilar (Autenticidad, Movimiento o Producto), y sale de las notas de la persona o de lo que ella contó. Sin notas ni conversación sobre eso, pregunta antes de inventar. Con la ficha, la línea "Semilla ({pilar}): {la frase}" va en la Idea de la ficha.
- **MI2.** Los tres ejes siempre. Formato, estructura y elementos adictivos, con el lugar donde aparece cada elemento. Un nombre de elemento sin lugar no cuenta.
- **MI3.** Formato y estructura son cosas distintas. El formato dice cómo grabar. La estructura dice el orden de la historia. Un formato puede usar más de una estructura.
- **MI4.** Los elementos siguen la jerarquía. Tema y moraleja primero. Una idea sin tema fuerte no se salva con contraste.
- **MI5.** El elemento ocurre en la escena. En el video, nadie oye el nombre del elemento. Di qué ve o qué escucha la persona en ese punto.
- **MI6.** Hecho con fuente. Si la idea depende de un número o de un caso, márcalo en "Necesita ser real". Sin fuente, la idea cambia o sale.
- **MI7.** Sin decisión inventada. Un número bajo no quiere decir que la persona abandonó un tema. Si el dato choca con lo que ella pidió, pregunta.
- **MI8.** El Piso (pieza `piso`) vale aquí también, incluso en el título y en el posible hook.
- **MI9.** Variación de lo que funcionó. La idea parte de lo que quedó por encima de lo normal del perfil cuando hay un ganador, y dice de dónde vino.
- **MI10.** Vale la regla del formato. En el Análisis, el analizado es alguien de afuera que entretiene, nunca el propio perfil.

### investigacion-de-burbuja (investigacion-de-burbuja.md)

- **PB1.** La burbuja tiene nombre de tema o de comunidad y es de uno de los 6 tipos; el dolor o la dificultad fue al "Para quién".
- **PB2.** Cada comentario está como fue escrito, sin @ ni nombre de quien escribió, con los me gusta como aparecen en el video.
- **PB3.** Cada comentario está marcado como identificación o conflicto.
- **PB4.** El vocabulario, lo que mueve a la burbuja y las referencias están separados en listas.
- **PB5.** El comentario sacado de una captura de pantalla fue revisado por la persona contra la captura antes de guardarlo.
- **PB6.** Nada se guardó sin el pedido o el OK de la persona.

### investigacion-manual (investigacion-manual.md)

- **PM1.** Cada hallazgo de captura de pantalla dice que vino de una captura y trae la fecha que la captura muestra, o la salvedad de que no aparece.
- **PM2.** La persona revisó la transcripción de cada comentario contra la captura antes de guardarlo.
- **PM3.** Lo que la captura no comprueba quedó en "No verificado".

### piso (piso.md)

- **P1.** Sin raya (—). Usa coma, punto, dos puntos o paréntesis.
- **P2.** Sin el molde "no es X, es Y" ni sus variaciones ("no se trata de X, sino de Y", "no solo X, sino Y", "X no es el problema, Y sí"). Afirma Y.
- **P3.** Sin adverbio terminado en -mente. Córtalo. La frase casi siempre queda mejor sin él.
- **P4.** Sin pregunta retórica, esa que haces solo para responder enseguida. Afirma. Quedan la pregunta del CTA, que espera respuesta en los comentarios, y la pregunta que vino de un comentario del público y entró como texto del creador.
- **P5.** Sin cliché y sin frase de IA. Las listas están en la pieza `sin-cara-de-ia`.
- **P6.** Ningún dato sin fuente. Número, fecha, caso y cita solo con una fuente que abriste. Sin fuente, la frase sale o queda sin el número.
- **P7.** El comentario del público se vuelve texto del propio creador. Guárdalo como fue escrito, sin @ y sin el nombre de quien escribió. En el guion entra como si el propio creador lo dijera: sin comillas y sin metalenguaje. Nada de "en los comentarios", "comentaron", "hay gente que", "mucha gente", "la gente", "seguidor" ni "burbuja". Ajusta solo lo mínimo para que sea coherente. No se vuelve hook por sí solo: uno de conflicto o de provocación, con muchos me gusta, puede ser una de las opciones de apertura, y la persona elige. Mira la pieza `hechos-y-fuentes`.

### principios (principios.md)

- **PV1.** La idea que vende ese video. Sin una respuesta clara, el problema viene antes de cualquier técnica.
- **PV2.** El tema y el tamaño del mundo que alcanza. Eso define el techo antes de cualquier análisis.
- **PV3.** Dónde ocurren el conflicto y el cambio, en la pantalla o en la cabeza del público. Si no ocurren en ningún lugar, no hay emoción ni retención.
- **PV4.** Dónde se abren las dudas y cuándo se cierran. Una duda que cierra demasiado pronto mata el debate. Una duda concreta dejada abierta a propósito genera comentarios.
- **PV5.** Si el aha llega después de que la persona piensa. Si llega muy temprano, satisface sin atrapar. La ausencia elegida lleva el debate a los comentarios.

### reglas-universales (reglas-universales.md)

- **RU1.** Los personajes son reales y se puede comprobar quiénes son.
- **RU2.** Las historias ocurrieron de verdad.
- **RU3.** El dato tiene fuente.
- **RU4.** Si no sabes a quién usar, dilo y deja la ficción afuera.
- **RU5.** La originalidad viene de los principios y de la estructura.
- **RU6.** Un ejemplo inventado para mostrar la forma se dice como inventado, y nunca va al guion.
- **RU7.** El personaje real viene con el link de la fuente.
- **RU8.** El dato o el número viene con el lugar de donde salió.
- **RU9.** La historia contada se puede encontrar en una búsqueda.
- **RU10.** Vale la pena gastar unos segundos buscando una historia real para el guion.
- **RU11.** Un tema fuerte con técnica floja le gana a una técnica perfecta con un tema flojo.
- **RU12.** Nunca cambies un principio por una frase que solo "suena bonita".
- **RU13.** El orden de los principios (Tema, Familiaridad, Conflicto, Curiosidad, Aha) sirve para juzgar por qué un video atrapa. El orden de los elementos adictivos, en la pieza `elementos-adictivos/README`, sirve solo para elegir los elementos de un guion. Mira la pieza `principios`.
- **RU14.** Elogio solo cuando se lo merece.
- **RU15.** Nada de problema inventado.
- **RU16.** Sé específico: dónde y por qué.
- **RU17.** Si está bien, di que está bien.
- **RU18.** Usa las palabras de la burbuja del público. Nada de lenguaje académico.
- **RU19.** Referencias conocidas por el público. Lo que solo tú conoces no cuenta.
- **RU20.** El conflicto mueve a quien va a mirar.
- **RU21.** La moraleja se conecta con la vida de quien mira.
- **RU22.** Copia los principios, la estructura y los elementos. El tema literal se queda afuera.
- **RU23.** Si el original usa a una persona famosa, usa a otra igual de conocida.
- **RU24.** Si el original usa una traición, usa un conflicto igual de universal.
- **RU25.** El esqueleto se reutiliza. La ropa es nueva.
- **RU26.** Provocar sostiene a la persona. Enseñar solo no la sostiene.
- **RU27.** Un guion que solo explica, sin conflicto en la cabeza de quien mira, hay que rehacerlo.
- **RU28.** La información entra como herramienta para construir la historia.

### sin-cara-de-ia (sin-cara-de-ia.md)

- **SS1.** Ve directo al punto. Sin anunciar lo que vas a decir.
- **SS2.** Huye de las fórmulas. Sin contraste binario, sin lista por lo negativo, sin pregunta de apoyo en lugar de la afirmación.
- **SS3.** Alguien hace algo. Toda frase tiene a una persona actuando. Una cosa sin vida con verbo de persona ("el algoritmo decide castigarte", "el dolor pide") sale.
- **SS4.** Sé específico. Nombre, número, lugar, hora. "Siempre", "nunca" y "todo el mundo" solo cuando sean verdad.
- **SS5.** Pon a la persona en la escena. "Tú" le gana a "las personas". El detalle concreto le gana a la idea abstracta.
- **SS6.** Varía el ritmo. Mezcla frase corta con frase larga. Dos ítems le ganan a tres. Termina cada párrafo de una manera distinta.
- **SS7.** Confía en quien escucha. Afirma. Sin suavizar, sin justificarte, sin explicar tu propio chiste.
- **SS8.** Corta la frase de efecto. Si la línea parece hecha para volverse captura de pantalla, reescríbela.
- **SS9.** ¿Sobró un adverbio terminado en -mente? Córtalo.
- **SS10.** ¿Voz pasiva? Encuentra quién hace y ponlo como sujeto.
- **SS11.** ¿Una cosa sin vida con verbo de persona? Di la persona que actúa.
- **SS12.** ¿Una frase que empieza con "qué", "por qué" o "cómo" en lugar de la afirmación? Afirma.
- **SS13.** ¿Algún "la verdad es que", "mira", "pues sí" u otra frase de la lista? Córtalo.
- **SS14.** ¿Algún molde de contraste de la tabla? Afirma la segunda mitad directo.
- **SS15.** ¿Tres frases seguidas del mismo largo? Rompe una.
- **SS16.** ¿Un párrafo que termina en frase de efecto? Varía.
- **SS17.** ¿Raya (—) en algún lugar? Cámbiala por coma, punto, dos puntos o paréntesis.
- **SS18.** ¿Una declaración vaga ("las implicaciones son grandes")? Di cuál es la implicación.
- **SS19.** ¿Un narrador distante ("las personas hoy en día")? Pon a la persona en la escena con "tú".
- **SS20.** ¿Un comentario sobre la estructura del propio texto? Bórralo.
- **SS21.** ¿El texto suma al menos 35 de 50 en el marcador de la pieza `sin-cara-de-ia`, con nota de 1 a 10 en cada dimensión? Por debajo de eso, reescribe.

### voz-del-creador (voz-del-creador.md)

- **VZ1.** Cada palabra y expresión existe en el modo de hablar de la persona (perfil, memoria del perfil, muestras) o en el habla del día a día de su burbuja.
- **VZ2.** Nada de lo que la persona dijo que evita aparece en el texto.
- **VZ3.** Leído en voz alta, el texto suena como sus muestras.
- **VZ4.** La frase que la persona dijo en esta conversación y que entró al texto mantiene sus palabras.
- **VZ5.** El modo de llamar al público (tú, vos, ustedes, gente) es el suyo.
- **VZ6.** La voz no tumbó ningún ítem del Piso.

### zona-de-fijacion (zona-de-fijacion.md)

- **ZF1.** Las 2 a 4 frases tratan del mismo asunto que el hook prometió.
- **ZF2.** Un pedazo concreto de la promesa llega en esos segundos.
- **ZF3.** Hay una prueba real, con fuente, o un ejemplo concreto de la persona.
- **ZF4.** La burbuja se reconoce: un detalle de su día a día, en sus palabras.
- **ZF5.** Nada de introducción, propaganda ni cambio de tema en ese tramo.
- **ZF6.** Presencia y cuidado están en la lista de grabación.

## Fuera de la escritura

- `flujos/analizar`: sirve al análisis de video y de perfil, fuera de la escritura de la ficha.
- `flujos/aprender-estilo`: sirve para aprender la voz de la persona; la voz guardada llega por la pieza `voz-del-creador` y por el perfil.
- `ejemplos-analizados/storytelling-persona`: no hay un formato con ese nombre en el catálogo; sirve al análisis de video.
