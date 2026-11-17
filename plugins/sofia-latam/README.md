# Sofia

Analiza videos y transcripciones, escribe y revisa guiones, aprende la voz del creador y exporta resultados en español latinoamericano. Las referencias necesarias están incluidas. No requiere un conector de contenido.

## Instalar y usar

```sh
claude plugin marketplace add bento-dev-ia/sofia-plugins
claude plugin install sofia-latam@sofia-plugins
```

En Codex, usa el catálogo del repositorio en `.agents/plugins/marketplace.json`. `.claude-plugin/plugin.json` y `.codex-plugin/plugin.json` describen la misma versión. Para subir un paquete manualmente, utiliza el ZIP generado con `python3 tools/package_plugins.py` desde la raíz del repositorio.

Pide analizar un video o una transcripción, escribir un guion, revisar un texto, aprender una voz o exportar resultados. La habilidad `sofia-latam` elige el flujo adecuado. Las respuestas y archivos generados están en español.

## Recursos y límites

La preparación visual local necesita FFmpeg y ffprobe, además de una herramienta para abrir imágenes. La referencia de análisis indica los comandos de `ffprobe` y `ffmpeg` que generan cuadros con tiempos, hojas de contacto y audio si existe; no transcriben ni reconocen efectos por sí solos. El plugin solo contiene texto: sin scripts ni ejecutables. El trabajo de texto no requiere estos programas. Las descargas públicas necesitan autorización y `yt-dlp`; nunca uses cookies ni sesiones del navegador para saltar el inicio de sesión.

Lee [comportamiento](comportamiento.md). Instalar programas, gastar créditos o enviar medios a terceros requiere autorización. Los resultados y perfiles se guardan fuera de la instalación. No hay telemetría propia.

## Datos y servicios externos

El plugin no tiene servidor propio y no guarda nada fuera de la computadora de la persona.

- **Guardado localmente, solo si se pide o autoriza:** perfiles de voz del creador y de clientes, análisis, guiones y exportaciones, en la carpeta elegida.
- **Comentarios de videos:** solo el texto literal y los me gusta; no se guardan nombre, identificador, foto ni dirección del autor.
- **Servicios externos, siempre con autorización en cada uso:**
  - YouTube, Instagram y TikTok, mediante `yt-dlp`, para descargar un video público autorizado o sus metadatos y comentarios;
  - Apify, YouTube Data API y Gemini, solo mediante el conector oficial que la persona instaló, con su cuenta y su facturación.

## Privacidad, términos y soporte

- [Privacy — política de privacidad](https://plataforma.academiacriadoresdofuturo.com.br/sofia-latam/privacidad)
- [Terms — términos de uso](https://plataforma.academiacriadoresdofuturo.com.br/sofia-latam/terminos)
- [Support — soporte](https://plataforma.academiacriadoresdofuturo.com.br/sofia-latam/soporte)

## Distribución y soporte

Publicador previsto: Alef Marques. Las compras de suscripciones, comunidades o cursos se realizan en Hotmart. El plugin no procesa pagos ni controla el acceso. La identidad y las declaraciones legales se verifican en el portal.

Los enlaces verificados de soporte, privacidad y términos del plugin Sofia están en el manifiesto, en español. Todavía falta una página pública de presentación de esta versión y actualizar el soporte para sus comandos actuales. Las páginas del GPT gratuito y de Sofia Estrategista Editora describen otros productos. El ZIP técnico no equivale a una aprobación para publicar. La ejecución local se declara en el manifiesto de OpenAI.

Licencia propietaria: [licencia](LICENSE). La autoría original se conserva en el manifiesto.
