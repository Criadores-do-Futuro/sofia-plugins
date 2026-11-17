# Setup, saved work and exports

Read [behavior](../../../behavior.md). Check the host's actual file, terminal and image tools. Text work does not need local video dependencies.

Local visual preparation needs Python 3.10 or newer, `ffmpeg` and `ffprobe`. `yt-dlp` is only needed for an authorized public download. Identify missing dependencies, propose the appropriate official installation command and obtain authorization before installation. Do not request passwords or credentials in the conversation. No content service account or API key is required for local preparation.

Use the user's chosen workspace. Export only the requested script, analysis, voice profile or learned patterns as Markdown, JSON or HTML. Preserve existing content before replacing a file; ask when replacement would lose data. Never export keys, author identifiers in comments or complete third-party transcripts.

For a dashboard, use the bundled `templates/dashboard.html` as a structural reference. Keep visible text in English. Escape external strings and use `textContent`, not executable interpolation. One request with several videos produces one consolidated dashboard, with a comparison and a section per video. Keep unavailable metrics distinct from zero and identify inspected evidence and limitations. Preserve previous entries and deduplicate by URL or identifier.

Verify saved files and local image links before returning their paths. Without file access, provide the content in the conversation without claiming it was saved. External publication is a separate action and requires the user's request.
