# Analizar video con evidencia

Lee [comportamiento](../../comportamiento.md). Elige la ruta según las herramientas realmente disponibles, sin presumir capacidades por el nombre de la aplicación.

## Elegir la fuente

- Video con terminal y herramienta de imágenes: prepara muestras locales e inspecciona los cuadros.
- Transcripción sin video: analiza palabras y orden narrativo; no concluyas sobre imagen, cortes, gestos ni tono de voz.
- Portada aislada: analiza solo la portada. Los comentarios y métricas no demuestran lo que aparece en el resto del video.
- Enlace sin acceso: explica el límite y pide el archivo o la transcripción. No describas el contenido por el título.
- Servicio externo: usa solo herramientas disponibles y autorizadas; comprueba el esquema y el precio actual antes de llamar. El paquete no garantiza un precio ni un recolector externo.

## Preparar el video

La preparación ejecuta `ffprobe` y `ffmpeg` directamente; no necesita clave, no transcribe palabras ni reconoce efectos automáticamente. Usa una carpeta de salida nueva y vacía en el espacio de trabajo del usuario, nunca dentro de la instalación del plugin. Sustituye las rutas del ejemplo y los valores en mayúsculas antes de ejecutar cada comando, y pon cada ruta entre comillas.

1. Lee los datos técnicos y guárdalos:

   ```sh
   mkdir -p "/carpeta/del/usuario/analisis-01/frames" "/carpeta/del/usuario/analisis-01/contacts"
   ffprobe -v error -show_entries format=duration:stream=codec_type,width,height,r_frame_rate -of json "/ruta/del/video.mp4" > "/carpeta/del/usuario/analisis-01/metadata.json"
   ```

2. Toma la duración `D` en segundos, elige `N` cuadros (80 como máximo) y calcula el intervalo `I = D / N`. Extrae los cuadros:

   ```sh
   ffmpeg -nostdin -hide_banner -loglevel error -i "/ruta/del/video.mp4" -vf "fps=1/I,scale='min(960,iw)':-2" -frames:v N -q:v 3 "/carpeta/del/usuario/analisis-01/frames/t-%05d.jpg"
   ```

   El cuadro `k` está cerca de `(k − 1) × I` segundos. Trata esos tiempos como aproximados, no como puntos exactos de corte.

3. Solo si `metadata.json` muestra una pista de audio, extráela:

   ```sh
   ffmpeg -nostdin -hide_banner -loglevel error -i "/ruta/del/video.mp4" -vn -ac 1 -ar 16000 -c:a libmp3lame -b:a 64k "/carpeta/del/usuario/analisis-01/audio.mp3"
   ```

4. Arma hojas de contacto de 20 cuadros cada una:

   ```sh
   ffmpeg -nostdin -hide_banner -loglevel error -framerate 1 -i "/carpeta/del/usuario/analisis-01/frames/t-%05d.jpg" -vf "scale=240:-2,tile=5x4:padding=8:margin=8" "/carpeta/del/usuario/analisis-01/contacts/timeline-%03d.jpg"
   ```

Abre las hojas de contacto en orden y los cuadros individuales relevantes. Para texto pequeño o movimiento ambiguo, prepara otra carpeta vacía solo para ese tramo: agrega `-ss INICIO -to FIN` antes de `-i` en el paso 2 y usa un intervalo menor; los tiempos se cuentan desde `INICIO`. Una muestra no demuestra ausencia de cortes entre cuadros. Extraer audio no equivale a escucharlo o transcribirlo.

Para una referencia pública cuyo uso fue autorizado, descárgala solo después de esa autorización, con su dirección HTTPS de YouTube, Instagram o TikTok; requiere `yt-dlp`:

```sh
yt-dlp --ignore-config --no-playlist --no-progress --write-auto-subs --write-subs --sub-format "vtt/best" --merge-output-format mp4 -f "bv*+ba/b" -o "/carpeta/del/usuario/analisis-01/video.%(ext)s" -- "https://www.youtube.com/watch?v=EJEMPLO"
```

El comando ignora configuraciones externas y no usa cookies. Si pide iniciar sesión, solicita el archivo, no un método para saltarlo.

## Analizar y entregar

Usa [principios](references/principios.md), [formatos](references/formatos/README.md) y [estructuras](references/estructuras-de-guion/README.md). Identifica tema, idea final y recursos editoriales con evidencia. Relaciona imagen y palabras solo si inspeccionaste ambas. Distingue tiempos observados de inferencias sobre el intervalo. Cita fragmentos breves y explica su efecto en una o dos frases sin reproducir toda la transcripción.

Los datos ausentes no son cero. No calcules tasas con denominador cero ni compares métricas sin identificar la base. Guarda comentarios solo con texto y cantidad de me gusta, sin datos del autor. No trates algunos comentarios como una encuesta representativa.

Con varios videos, compara ganchos, estructuras, métricas disponibles, patrón común y variable distinta en un panel consolidado. Incluye límites: qué imágenes, palabras, audio, comentarios y métricas inspeccionaste realmente. Para crear o exportar el panel sigue [archivos](archivos.md). Si piden una respuesta breve o no puedes crear archivos, entrega el análisis en texto.
