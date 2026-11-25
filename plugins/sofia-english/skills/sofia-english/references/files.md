# Setup, saved work and exports

Read [behavior](behavior.md). Check the host's actual file, terminal and image tools. Text work does not need local video dependencies.

## Setup

Local visual preparation needs `ffmpeg` and `ffprobe`, plus a tool that can open images. `yt-dlp` is only needed for an authorized public download. Identify missing dependencies, propose the appropriate official installation command and obtain authorization before installation. Do not request passwords or credentials in the conversation. No content service account or API key is required for local preparation.

The optional Sofia tools (`list_method_pieces`, `read_method_piece`, `check_script`) need no setup inside this package: when the host has them connected, use them; when it doesn't, the local references hold the same method.

## Where work is saved

Use the user's chosen workspace, never the plugin installation. Suggested subfolders, all under `sofia-english/` in that workspace:

| Folder | What goes there |
|---|---|
| `sofia-english/briefs/` | One video brief per video (`<slug>.md`): decisions, research with sources and "Unverified", hook, versions and highlights |
| `sofia-english/styles/` | One creator profile per person or client (`<profile-name>.md`): voice, do and avoid, bubbles, commander's intent notes |
| `sofia-english/analyses/` | Video and profile analyses, and dashboards |
| `sofia-english/swipe-file/` | Saved references: templates with {variables}, literal hooks, up to 20 literal comments without author identifiers |

Save only what the user requested or authorized. Show a profile or a summary before saving unless saving was already requested. Preserve existing content before replacing a file; ask when replacement would lose data. Confirm a path only after verifying the file exists. Without file access, provide the content in the conversation and say it was not saved.

## Exports

Export only the requested script, video brief, analysis, voice profile or learned patterns, as Markdown, JSON or HTML. Never export keys, author identifiers in comments or complete third-party transcripts. Offer a downloadable file only when the host provides file-creation and download tools, and verify the file before linking it.

For a dashboard, write a single self-contained HTML file with no scripts and no external resources: `lang="en-US"`, a viewport meta tag and a Content-Security-Policy of `default-src 'none'; img-src 'self' data:; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'`. Under a title and a line saying that only observed data is used and missing metrics are marked unavailable, add four sections in this order: Inspected material, Main findings, Evidence and limits, Sources. Keep visible text in English. Escape external strings and use `textContent`, not executable interpolation. One request with several videos produces one consolidated dashboard, with a comparison and a section per video. Keep unavailable metrics distinct from zero and identify inspected evidence and limitations. Preserve previous entries and deduplicate by URL or identifier.

Verify saved files and local image links before returning their paths. External publication is a separate action and requires the user's request.
