# Sofia

Sofia es una estratega de videos cortos (Instagram, TikTok, YouTube) que trabaja en español latinoamericano. Da ideas de video, investiga con fuentes, ayuda a elegir el formato y la estructura, escribe el hook y el guion, hace la crítica de un guion, revisa y reescribe textos, analiza videos y perfiles de referencia y aprende la voz del creador. Todo con un método incluido en el plugin: principios de la viralización, elementos adictivos, 23 formatos de grabación, 5 estructuras de guion, cómo romper la burbuja e intención de comando.

Sofia no inventa hechos, números ni citas: lo que no tiene fuente queda marcado como "No verificado" y fuera del guion.

## Instalar y usar

```sh
claude plugin marketplace add Criadores-do-Futuro/sofia-plugins
claude plugin install sofia-latam@sofia-plugins
```

En Codex, usa el catálogo del repositorio en `.agents/plugins/marketplace.json`. Para subir un paquete a mano, usa el ZIP que genera `python3 tools/package_plugins.py` desde la raíz del repositorio.

Pide lo que necesitas con tus palabras ("dame ideas de video", "escríbeme el guion", "haz la crítica de este guion", "analiza este video", "aprende mi voz"). La skill `sofia-latam` elige el flujo.

## Flujos

| Flujo | Qué hace |
|---|---|
| Ideas | De un tema suelto, o de nada, a 3 a 5 ideas con formato, estructura, elementos adictivos, burbuja y semilla, partiendo de lo que ya funcionó en el perfil. |
| Investigación | Hechos en fuente primaria, cada uno con su enlace, y la investigación de la burbuja (cómo habla el público, qué lo mueve, los comentarios con más me gusta). Sin búsqueda disponible, guía una investigación manual con capturas de pantalla. |
| Guion | Hook (texto hablado, texto en pantalla y lo que se ve en los primeros segundos), zona de fijación, 2 o 3 versiones del guion y la lista de grabación. |
| Mejorar | Revisa y reescribe un texto propio, o ajusta solo el fragmento pedido, mostrando antes y después. |
| Crítica | Lee el guion con ojos de quien lo ve y devuelve marcas numeradas (fragmento, por qué cambiar, sugerencia) para pulirlo. |
| Analizar | Analiza un video, una transcripción, una referencia o un perfil, con evidencia, y dice qué partes no pudo ver. |
| Aprender estilo | Aprende la voz del creador (o de cada cliente) a partir de sus guiones. |
| Archivos | Guarda, exporta y arma paneles de análisis en la carpeta que la persona elige. |

## Agentes (en Claude Code)

En Claude Code, el plugin trae un equipo de agentes: escribir va separado de revisar.

- Escriben: `guionista`, `redactor-de-hook`, `estratega-de-ideas`, `especialista-en-burbuja` (también revisa) e `investigador`.
- Revisan: `revisor-de-lo-que-no-se-hace`, `revisor-de-hook`, `revisor-de-voz`, `revisor-de-estructura`, `revisor-de-hechos` y `critico`.

Los agentes solo leen el método y devuelven su texto o sus veredictos; no guardan nada. En las apps sin agentes (ChatGPT, Claude en la web), Sofia hace los mismos roles uno después de otro, en la conversación ("pasadas"), con las mismas reglas.

## Herramientas MCP opcionales

En algunas apps (por ejemplo ChatGPT o Codex) Sofia puede tener tres herramientas de su servidor:

- `list_method_pieces`: lista las piezas del método.
- `read_method_piece`: abre una pieza del método por su id (por ejemplo `formatos/vlog`). El nombre solo también sirve cuando es único.
- `check_script`: revisa un guion terminado contra frases con cara de IA, moldes prohibidos y metalenguaje de comentarios, y estima el tiempo de habla. Devuelve puntos para revisar, no correcciones obligatorias: son señales automáticas que pueden dar falso positivo, y la herramienta cubre solo una parte del Piso. El límite de 15 palabras en la primera frase y las palabras por minuto de la estimación son referencias de la herramienta, no reglas del método.

Qué recibe el servidor: el texto que Sofia manda a `check_script` y el id de la pieza pedida. No guarda nada, no pide inicio de sesión y no recibe tus archivos. Sin esas herramientas, Sofia usa las referencias locales del plugin y revisa las mismas reglas a mano.

## Servicios externos

El plugin no incluye servicios externos, y Sofia no depende de otra app. Trabaja con lo que la persona trae: texto pegado, archivo, enlace o exportación. Si faltan datos de una red social, Sofia pide el archivo, la transcripción, la exportación o capturas de pantalla. Si la propia persona pide usar una herramienta que ya tiene, Sofia sigue su pedido, después de decir qué va a buscar, cuántos elementos y cuánto cuesta, si cuesta. Nunca usa cookies ni sesiones del navegador, nunca salta un inicio de sesión y nunca pide contraseñas.

## Requisitos

- Para el trabajo con texto (ideas, guiones, crítica, revisión, análisis de transcripciones) no hace falta instalar nada.
- Para preparar un video cuadro por cuadro hace falta FFmpeg (con `ffprobe`) y una app que ejecute comandos (opcional). Los comandos están en el flujo de análisis; generan cuadros con tiempos, hojas de contacto y el audio, pero no transcriben ni reconocen efectos por sí solos. Sin terminal, Sofia analiza el texto y dice qué capas no vio.
- El plugin solo contiene texto: sin scripts ni ejecutables.

## Dónde guarda

Sofia guarda solo cuando lo pides o lo autorizas, en la carpeta que elijas, dentro de `sofia-latam/`: tu estilo, tus preferencias, las fichas de cada video, lo aprendido de cada burbuja, referencias, evaluaciones de perfil y análisis. Nunca guarda dentro de la instalación del plugin. De los comentarios de videos guarda solo el texto literal y los me gusta, sin nombre, @, foto ni dirección del autor. Sin acceso a disco, entrega todo en la conversación. No hay telemetría propia.

## Privacidad, términos y soporte

- [Privacy Policy · Política de Privacidad](https://plataforma.academiacriadoresdofuturo.com.br/sofia-latam/privacidad)
- [Términos de uso](https://plataforma.academiacriadoresdofuturo.com.br/sofia-latam/terminos)
- [Soporte](https://plataforma.academiacriadoresdofuturo.com.br/sofia-latam/soporte)
- [Sitio](https://plataforma.academiacriadoresdofuturo.com.br/sofia-latam)

Publicador: **Action Criação Digital Ltda (Criadores do Futuro)**.

Licencia propietaria: [licencia](LICENSE). Las reglas de la pieza `sin-cara-de-ia` fueron adaptadas de [stop-slop](https://github.com/hardikpandya/stop-slop), de Hardik Pandya, bajo licencia MIT. El aviso completo está al final de la pieza, en `skills/sofia-latam/references/sin-cara-de-ia.md`.
