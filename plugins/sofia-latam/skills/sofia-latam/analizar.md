# Analizar video con evidencia

Lee [comportamiento](../../comportamiento.md). Elige la ruta según las herramientas realmente disponibles, sin presumir capacidades por el nombre de la aplicación.

## Elegir la fuente

- Video con terminal y herramienta de imágenes: prepara muestras locales e inspecciona los cuadros.
- Transcripción sin video: analiza palabras y orden narrativo; no concluyas sobre imagen, cortes, gestos ni tono de voz.
- Portada aislada: analiza solo la portada. Los comentarios y métricas no demuestran lo que aparece en el resto del video.
- Enlace sin acceso: explica el límite y pide el archivo o la transcripción. No describas el contenido por el título.
- Servicio externo: usa solo herramientas disponibles y autorizadas; comprueba el esquema y el precio actual antes de llamar. El paquete no garantiza un precio ni un recolector externo.

## Preparar el video

Identifica la raíz absoluta del plugin que contiene `plugin.json`. Sustituye las rutas descriptivas del ejemplo antes de ejecutarlo. No dependas de variables específicas de Claude. Usa una carpeta de salida nueva y vacía.

```sh
python3 "/ruta/absoluta/del/plugin/scripts/prepare-visual-analysis.py" "/ruta/del/video.mp4" --output "/carpeta/del/usuario/analisis-01" --max-frames 80
```

Necesitas Python 3.10 o posterior, `ffmpeg` y `ffprobe`. El preparador no necesita clave, no transcribe palabras ni reconoce efectos automáticamente. Para una referencia pública cuyo uso fue autorizado, agrega `--allow-download` y utiliza su dirección HTTPS; requiere `yt-dlp`. El descargador ignora configuraciones externas y no usa cookies. Si pide iniciar sesión, solicita el archivo, no un método para saltarlo.

Lee `manifest.json`: sus campos técnicos indican archivo, intervalo, rutas y tiempos de cuadros decodificados. Abre las hojas de contacto en orden y los cuadros individuales relevantes. Para texto pequeño o movimiento ambiguo, prepara otra carpeta con `--start` y `--end`, aumentando la densidad solo en ese tramo. Una muestra no demuestra ausencia de cortes entre cuadros. Extraer audio no equivale a escucharlo o transcribirlo.

## Analizar y entregar

Usa [principios](references/principios.md), [formatos](references/formatos/README.md) y [estructuras](references/estructuras-de-guion/README.md). Identifica tema, idea final y recursos editoriales con evidencia. Relaciona imagen y palabras solo si inspeccionaste ambas. Distingue tiempos observados de inferencias sobre el intervalo. Cita fragmentos breves y explica su efecto en una o dos frases sin reproducir toda la transcripción.

Los datos ausentes no son cero. No calcules tasas con denominador cero ni compares métricas sin identificar la base. Guarda comentarios solo con texto y cantidad de me gusta, sin datos del autor. No trates algunos comentarios como una encuesta representativa.

Con varios videos, compara ganchos, estructuras, métricas disponibles, patrón común y variable distinta en un panel consolidado. Incluye límites: qué imágenes, palabras, audio, comentarios y métricas inspeccionaste realmente. Para crear o exportar el panel sigue [archivos](archivos.md). Si piden una respuesta breve o no puedes crear archivos, entrega el análisis en texto.
