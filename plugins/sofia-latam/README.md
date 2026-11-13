# Sofia LATAM

Sofia es una guionista y analista de videos cortos en español neutro latinoamericano. Analiza videos de TikTok, Instagram y YouTube y explica por qué funcionan. También escribe guiones nuevos, critica y mejora los que ya tienes, y aprende tu estilo de escritura.

## Instalación

```
/plugin marketplace add bento-dev-ia/sofia-plugins
/plugin install sofia-latam@sofia-plugins
```

## Qué necesita

- **ffmpeg** y **yt-dlp**, para sacar cuadros y audio de los videos. Si faltan, Sofia te dice qué comando los instala y espera tu OK antes de instalar nada.
- **Apify** (opcional), para Instagram o TikTok cuando no hay otra vía. Sofia te avisa que el link va a un servicio externo, te da el costo estimado y solo sigue si dices que sí.

Sofia nunca usa las cookies ni la sesión de tu navegador. Si una plataforma pide inicio de sesión, te pide el archivo del video.

## Dónde guarda las cosas

Todo queda en la carpeta `sofia-latam/` de tu directorio de trabajo: los análisis en `sofia-latam/analisis/` y tus estilos en `sofia-latam/estilos/`. Nada se escribe dentro de la carpeta del plugin.

## Contenido del conector

Algunas piezas del método llegan por el conector MCP `sofia-conteudo`. Sin él, Sofia funciona igual y te avisa cuando le falta una pieza.
