# Analizar Video

**Recuerda: sigue las reglas de `references/tono-de-voz.md`. Habla como persona, no como IA.**

## Lo que sí puedes hacer (no te subestimes)

Tú **ves imagen**. Abres un cuadro del video, lees texto en pantalla, identificas corte, encuadre y gesto. El script `scripts/prepare-visual-analysis.py` existe para eso: usa `ffmpeg` para sacar los cuadros.

Lo que a veces falta no es capacidad, es **acceso al archivo**. TikTok e Instagram bloquean la descarga por red en algunos entornos. Eso es plomería, no es ojo.

Regla: **nunca digas que "no puedes analizar video".** Di qué ruta está disponible y qué entrega esa ruta.

---

## Elige la ruta antes de cualquier cosa

Elige según la superficie. No intentes una ruta que el entorno bloquea de forma conocida.

| Ruta | Cuándo | Capa visual | Costo |
|---|---|---|---|
| A — Archivo en mano | El usuario subió el video, o está en disco | **Completa** | Gratis |
| B — yt-dlp directo | Claude Code o Cowork Desktop, con un link | **Completa** | Gratis |
| C — Apify en el Chat | Claude Chat con conector Apify, **solo con el OK del usuario** | **Portada + transcripción + métricas + comentarios** | Pago (créditos del usuario) |
| D — Búsqueda pública | Claude Chat sin archivo y sin OK para Apify | **Solo lo que esté públicamente indexado** | Gratis |

- **La ruta por defecto es la A:** pedir el archivo del video. Es la más completa, no depende de la plataforma y no gasta créditos.
- Puedes cambiar solo, sin preguntar, entre las rutas gratuitas (A, B y D).
- La Ruta C gasta créditos y manda el link a un servicio de terceros: nunca entres en ella sin el OK explícito del usuario (ver la Ruta C).
- Antes de instalar cualquier programa (`yt-dlp`, `ffmpeg`), dile al usuario qué comando lo instala y pide su OK.

**Derechos y términos de cada plataforma.** Descargar o raspar videos puede ir contra los términos de TikTok, Instagram o YouTube. Usa la descarga (Ruta B) y los raspadores (Ruta C) solo con contenido propio del usuario o que él tiene derecho a analizar, y díselo una vez: la responsabilidad por los términos de cada plataforma es suya. Si tiene el archivo, pídelo.

## Qué significa "ver video" en Claude

Claude no recibe MP4 como modalidad visual nativa. La forma confiable es descomponer el video en imágenes ordenadas, cruzar cada cuadro con timestamps y transcripción, y pedir una segunda pasada más densa en los tramos ambiguos. Un GIF animado no resuelve: Claude usa solo el primer cuadro.

- Todos los modelos Claude actuales aceptan imágenes. Si la superficie permite elegir, usa el modelo más capaz disponible para texto pequeño, muchos cuadros o detalles de edición. Si no permite elegir, sigue con el modelo disponible y declara solo una limitación que realmente haya aparecido.
- En el Chat, envía como máximo 20 imágenes por mensaje. Para más cuadros, divide en lotes cronológicos numerados, preserva la continuidad entre lotes y concluye solo después de inspeccionar todos.
- En Cowork Desktop, prefiere archivo local + ejecución de código. En Cowork web/móvil, archivo local y navegador dependen de que el Desktop esté abierto y conectado; si no están disponibles, pide el upload del archivo.
- Las hojas de contacto sirven para barrer la línea de tiempo. Abre el cuadro individual cuando necesites leer texto, gesto, objeto o corte. Coloca las imágenes antes de las instrucciones de análisis cuando la superficie lo permita.
- En videos largos, haz una pasada amplia y luego repite solo en los intervalos relevantes. Un barrido disperso nunca debe presentarse como observación continua de todo el video.

**Claude Chat:** no pruebes `yt-dlp` contra TikTok/Instagram y no intentes descargar una URL firmada de Apify con `curl` o `web_fetch`. El sandbox bloquea `tiktok.com` y `api.apify.com`. Pide el upload del video o, con el OK del usuario, usa las herramientas del conector Apify (Ruta C).

---

## Ruta A — Archivo en mano (la mejor ruta)

1. Ubica la carpeta de la skill (la indica `SKILL.md`; es la carpeta que contiene ese archivo).
2. Ejecuta, desde el directorio de trabajo del usuario:

```bash
python3 "CARPETA_DE_LA_SKILL/scripts/prepare-visual-analysis.py" "RUTA_DEL_ARCHIVO" --output "sofia-latam/analisis/cuadros/IDENTIFICADOR"
```

En Windows, si `python3` no existe, usa `python` o `py`.

3. Lee `manifest.json` y abre con la herramienta de imágenes **todas** las hojas en `contacts/`, en orden.
4. Abre cuadros individuales de `frames/` y `scenes/` cuando haya texto pequeño, corte rápido, gesto o acción ambigua.
5. Cruza los segundos del manifiesto con subtítulo/transcripción y `audio.mp3`.
6. Si el barrido revela un tramo decisivo, ejecuta de nuevo con `--start SEGUNDO --end SEGUNDO --max-frames 40`. No aumentes los cuadros de todo el video cuando la duda está en un tramo corto.

Si falta `ffmpeg`, dile al usuario qué comando lo instala en su sistema (Mac: `brew install ffmpeg`; Linux: el gestor de paquetes de su distribución; Windows: `winget install ffmpeg`) y pide su OK antes de correrlo.

Si el script falla, `ffmpeg` lo resuelve a mano (crea antes la carpeta `sofia-latam/analisis/cuadros/IDENTIFICADOR/frames`):

```bash
ffprobe -v error -show_entries format=duration -of csv=p=0 video.mp4
ffmpeg -i video.mp4 -vf fps=1/3 sofia-latam/analisis/cuadros/IDENTIFICADOR/frames/f_%03d.jpg -hide_banner -loglevel error
ffmpeg -i video.mp4 -vn -acodec libmp3lame sofia-latam/analisis/cuadros/IDENTIFICADOR/audio.mp3 -hide_banner -loglevel error
```

Después abre los `.jpg` con la herramienta de imágenes. **Ábrelos de verdad.** No describas un cuadro que no miraste.

---

## Ruta B — yt-dlp directo

Úsala solo con contenido propio del usuario o que él tiene derecho a analizar (ver "Derechos y términos").

```bash
python3 "CARPETA_DE_LA_SKILL/scripts/prepare-visual-analysis.py" "URL_DEL_VIDEO" --output "sofia-latam/analisis/cuadros/IDENTIFICADOR"
```

Habla, metadatos y comentarios:

```bash
yt-dlp --write-auto-sub --sub-lang es,en --skip-download --write-info-json -o "sofia-latam/analisis/cuadros/IDENTIFICADOR/info" "URL_DEL_VIDEO"
yt-dlp --write-comments --skip-download -o "sofia-latam/analisis/cuadros/IDENTIFICADOR/info" "URL_DEL_VIDEO"
```

De los comentarios lee solo el texto y los likes. No guardes el autor, el @ ni el id de quien comentó.

Si falta `yt-dlp`, dile al usuario qué comando lo instala y pide su OK antes de correrlo:
- Mac: `brew install yt-dlp`
- Linux: `pip3 install yt-dlp`
- Windows: `winget install yt-dlp`

Si la plataforma pide inicio de sesión, no intentes saltártelo ni uses las cookies o la sesión del navegador: pide al usuario que te mande el archivo del video (Ruta A).

Acepta `tiktok.com`, `vm.tiktok.com`, `vt.tiktok.com`.

**¿Falló por red?** Pasa a otra ruta gratuita (pide el archivo o usa la Ruta D) y dile al usuario en una frase qué cambió. No reportes el error como si fuera un callejón sin salida. La Ruta C solo con su OK.

---

## Ruta C — Captura vía Apify en Claude Chat

Busca `search-actors`, `call-actor`, `get-dataset-items` y `get-key-value-store-record`. Si el conector no está disponible, pasa a la Ruta D y ofrece el upload.

### Antes de llamar a cualquier actor: pide el OK

Apify es un servicio de terceros que cobra en los créditos de la cuenta del usuario. Antes de la primera llamada, dile en un solo mensaje:

- que el link del video se va a mandar a Apify;
- el costo estimado: cerca de US$ 0,05 por video (metadatos, portada y transcripción) más cerca de US$ 0,025 por cada 20 comentarios, multiplicado por la cantidad de videos. Es una estimación: el precio de cada actor puede cambiar;
- que la alternativa gratuita es mandar el archivo del video (Ruta A), que además da el análisis visual completo.

> "Para leer este video desde el Chat necesito mandar el link a Apify, un servicio externo que usa los créditos de tu cuenta: cerca de US$ 0,08 por video con 20 comentarios (es una estimación). Si prefieres no gastar, mándame el archivo del video y lo analizo completo gratis. ¿Sigo con Apify?"

Solo sigue con un sí explícito. Si dice que no, pasa a la Ruta A o D. Si pidió varios videos, el OK cubre ese lote; para otro lote, pregunta de nuevo.

### Video, metadatos, portada y transcripción

Llama a `clockworks/tiktok-video-scraper` una vez por URL:

```json
{
  "postURLs": ["URL_LIMPIA"],
  "shouldDownloadVideos": true,
  "shouldDownloadCovers": true,
  "downloadSubtitlesOptions": "TRANSCRIBE_ALL_VIDEOS"
}
```

- `TRANSCRIBE_ALL_VIDEOS` fuerza la transcripción por IA. Usa `DOWNLOAD_SUBTITLES` cuando el subtítulo nativo alcance y el menor costo sea prioridad.
- Costo observado aproximado: US$ 0,003 por el video + US$ 0,0013 por la descarga + US$ 0,048 por la transcripción, cerca de US$ 0,05 por video. Trátalo como estimación, porque el precio del actor puede cambiar.
- En `get-dataset-items`, lee `diggCount`, `shareCount`, `playCount`, `commentCount` y `collectCount`.
- `videoMeta.transcriptionLink` y `videoMeta.coverUrl` apuntan a registros del Key-Value Store. Extrae `{storeId}` y `{key}` y pásalos a `get-key-value-store-record`.
- La transcripción vuelve como texto; léela completa. La portada vuelve como imagen; inspecciónala de verdad y compara el texto visual con la primera frase hablada.
- Nunca uses `curl` ni `web_fetch` en esas URLs dentro del Chat. No intentes obtener `videoMeta.downloadAddr`: el archivo grande se convierte en una URL firmada que el sandbox no puede descargar.

### Comentarios

Llama a `clockworks/tiktok-comments-scraper` una vez por URL:

```json
{
  "postURLs": ["URL_LIMPIA"],
  "commentsPerPost": 20
}
```

Lee solo `text`, `diggCount` y `createTimeISO`. No leas ni guardes `uniqueId` ni ningún otro dato de quien comentó. Ordena por `diggCount` descendente antes de seleccionar los 20 principales; el orden del dataset no garantiza popularidad. El costo observado ronda US$ 0,025 por 20 comentarios, pero puede variar.

### Múltiples videos

Corre los dos actors una vez por video. `postURLs` acepta array, pero llamadas separadas preservan la trazabilidad entre métricas, transcripción, portada, comentarios y la sección correspondiente del dashboard.

### Transparencia obligatoria, una sola vez

> "Aquí en Claude Chat pude ver la portada y leer transcripción, métricas y comentarios, pero no los cuadros intermedios. Para analizar cortes, gestos y texto en pantalla a lo largo del video, necesito el upload del archivo o correrlo en Claude Code/Cowork Desktop."

No describas edición, gestos intermedios ni timestamps visuales que no fueron inspeccionados.

---

## Ruta D — Claude Chat sin Apify

Usa solo búsqueda pública sobre el link o el perfil. Como rara vez hay material suficiente del video específico, separa hechos encontrados de inferencias, di la limitación y ofrece el upload. No conviertas título, thumbnail ni fragmentos en análisis visual del cuerpo del video.

---

## Otras plataformas

- **YouTube:** en Claude Code/Cowork Desktop, la Ruta B casi siempre funciona; en el Chat, usa contenido público accesible o pide el upload.
- **Instagram:** en Claude Code/Cowork Desktop, usa la Ruta B; si pide inicio de sesión, pide el archivo. En el Chat, un actor de Instagram en Apify sigue las mismas reglas de la Ruta C (OK y costo estimado antes) y tiene la misma limitación del MP4.
- **Archivo que el usuario ya tiene:** pide el upload. Es la ruta más rápida, más completa y no gasta ningún crédito.

---

## Antes de analizar, pregunta

- "¿Este video es de tu nicho? ¿Cuál es tu público?"
- "¿Quieres entender alguna parte en específico?"

Si llegaron dos o más videos, o el contexto ya lo deja claro, sáltate las preguntas y entrega. Preguntar después de dos intercambios de mensaje ya es dilatar.

## Cuando son dos videos o más

Compara. Es el análisis más útil que existe.

**Trata todos los links del mismo mensaje como un único lote.** Prepara y analiza cada video en su propia carpeta de `sofia-latam/analisis/cuadros/`, pero no publiques ni guardes un dashboard por video. Genera el artifact solo después de que todos los análisis estén listos.

- Arma la tabla de números lado a lado.
- Calcula likes ÷ vistas de cada uno. ¿Dio parecido? El problema de lo que salió mal **no es el video, es el tema o la apertura**. ¿Dio distinto? El problema está dentro del video.
- Compara las portadas lado a lado. Ahí aparece mucho.
- Señala la variable que cambió. Una sola, la principal.

## REGLA DE BREVEDAD

**Analiza FRASE POR FRASE. Cada frase del guion recibe su análisis. Pero el análisis de cada frase tiene que ser CORTO.**

- Cada frase del guion = 1 bloque separado con análisis
- Máximo 1 frase de análisis por frase del guion. UNA.
- Ve directo al punto: qué le hace esa frase a quien está viendo.
- No expliques el porqué del porqué. Solo el porqué.
- Nunca te saltes frases. Todas se analizan.

## Formato del análisis

> "Fragmento del guion"

Qué hace: [1 frase corta].

---

**Ejemplo de cómo debe quedar:**

> "¿Sabías que el 90% de las personas hace esto mal?"

Lanza un número que asusta. La persona piensa "¿será que yo lo hago mal?" y se queda.

---

> "Y lo peor: nadie te cuenta la verdad sobre esto"

Aumenta la curiosidad. Ahora quiere saber cuál es esa verdad.

---

> "Pero la realidad es que esto cambia todo"

El "pero" jala el tapete. Estaba en un lugar, ahora está en otro.

---

**Reglas:**
- `> "texto"` para el guion, texto normal para el análisis
- `---` entre bloques
- 1 frase por análisis. Corta. Directa.
- NUNCA agrupes frases. Cada frase del guion = 1 bloque separado.
- Señala lo principal que hace esa frase. No listes varios trucos.

## Cómo se hizo el video

Antes del resumen final, di en 3 líneas cortas:
- **Forma de grabar:** [qué formato de `references/formatos/`; si mezcla dos, di cuál domina]
- **Orden de la historia:** [qué estructura de `references/estructuras-de-guion/`]
- **Qué acertó o falló en esa forma de grabar:** [1 frase, comparando con las "Reglas de escritura" del archivo del formato]

En las rutas A, B y C, agrega:
- **Hook visual:** qué aparece en los primeros segundos y por qué engancha
- **Edición:** cortes, cámara, texto en pantalla, gestos y cambios de ritmo, con timestamps
- **Imagen + habla:** dónde se refuerzan o se contradicen

En la ruta D, cámbialo por:
- **La portada:** qué muestra y qué promete su texto
- **Portada × primera frase:** ¿dicen lo mismo o cosas distintas?
- **Señales indirectas:** qué dicen los números y comentarios sobre dónde enganchó o soltó

No inventes un timestamp que no viste. Nunca.

## Apertura

- ¿Qué hace que la gente se detenga? [1 frase]
- Nota: X/10

## Resumen final (3 líneas)

1. La idea central en 1 frase
2. Qué carga el video (qué principio está haciendo el trabajo pesado — en palabras simples)
3. Qué se podría mejorar (sugerencia práctica conectada a un principio, 1 frase)

## Artifact obligatorio

- En superficies con Artifacts, crea un artifact HTML interactivo en la conversación.
- En Claude Code o en un entorno sin Artifacts, usa `templates/dashboard.html` y guárdalo en `sofia-latam/analisis/dashboard.html`, en la carpeta de trabajo del usuario. Si el usuario pide un archivo separado para esa solicitud, usa `sofia-latam/analisis/{titulo-del-lote}/index.html`.
- **Una solicitud genera un dashboard.** Con un video, el dashboard contiene un ítem. Con dos o más, contiene todos los videos, nunca un HTML por video.
- En el lote, incluye arriba: visión general, tabla de métricas lado a lado, ranking de aperturas, patrón en común y la principal variable que cambió. Después, crea una sección navegable y completa para cada video.
- Cada video debe incluir: título, link original, diagnóstico, nota y explicación de la apertura, números, guion anotado, comentarios, aprendizajes y limitaciones.
- Rutas A/B/C: incluye cuadros con timestamp, línea de tiempo y relación imagen–habla. Solo cuadros realmente inspeccionados. Nunca presentes una muestra como si fuera el video entero.
- **Imágenes de los cuadros:** en el `dashboard.html` local, usa rutas relativas a `sofia-latam/analisis/` (por ejemplo, `cuadros/IDENTIFICADOR/frames/t-00001.jpg`). En un Artifact, las rutas locales no abren: incrusta solo los cuadros clave reducidos como imagen en base64 si puedes generarla con código; si no, deja el tiempo y la descripción sin imagen.
- Ruta D: incluye la portada (esa sí la viste) y quita los bloques de cuadro en vez de rellenarlos con suposición.
- Comentarios: solo el texto tal como fue escrito, los likes y tu lectura. Nunca el @ ni el nombre de quien comentó.
- El bloque de limitaciones es obligatorio: dice qué capa quedó fuera y cómo cerrarla.
- Al actualizar `sofia-latam/analisis/dashboard.html`, conserva los análisis ya existentes y agrega o actualiza los videos por link/ID; no dupliques el mismo video.
- Entrega el artifact y, en la conversación, muestra solo un resumen corto con los tres hallazgos principales.

## Después, pregunta

> "¿Quieres escribir un guion basado en esto, mejorar uno que ya tienes, o entender alguna parte mejor?"
