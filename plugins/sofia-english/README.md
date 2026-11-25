# Sofia

Sofia is a short-form video strategist for Instagram Reels, TikTok and YouTube Shorts, working in American English. She helps creators find video ideas, research facts with sources, write hooks and scripts, critique and rewrite drafts, analyze reference videos and profiles, and learn the creator's own voice. Everything follows one method: the virality principles, the addictive elements, 23 recording formats, 5 script structures, breaking into a bubble and planting one seed of what the creator sells. Nothing is invented: every number, case and quote needs a source, and audience comments are kept exactly as written.

## Install and use

```sh
claude plugin marketplace add Criadores-do-Futuro/sofia-plugins
claude plugin install sofia-english@sofia-plugins
```

For Codex, use the repository catalog at `.agents/plugins/marketplace.json`. Then ask for what you need ("give me video ideas about...", "write a 45-second script about...", "critique my script", "analyze this video", "learn my voice"). The `sofia-english` skill picks the workflow. Responses and generated files stay in English.

## Workflows

| Workflow | What it does |
|---|---|
| Ideas | A brainstorm that ends in 3 to 5 ideas, each with format, structure, addictive elements, the bubble and the seed |
| Research | Facts in primary sources, an "Unverified" list, and bubble research from the most-liked comments |
| Hooks | Hook options with spoken line, on-screen text and the first seconds, plus recording styles |
| Script | A direct draft, or 2 or 3 versions step by step, with the hold zone right after the hook |
| Review and rewrite | The main finding, strengths, prioritized problems with before and after, and targeted rewrites |
| Critique | Numbered highlights (cut, replace, strengthen, question) the creator accepts or rejects |
| Analyze | A video, transcript, reference or whole profile, saying which layers were actually inspected |
| Voice | Learn the creator's voice from 3 to 5 real samples and apply it |

The method itself lives in `skills/sofia-english/references/`: the Floor (rules every text passes), no AI-speak, plain language, writing well, how to make the hook, the hold zone, facts and sources, the formats, structures and addictive elements, annotated example scripts and a glossary.

## Agents (Claude Code)

In Claude Code, Sofia's team runs as agents of this plugin. Writers: `ideas-strategist`, `bubble-specialist`, `researcher`, `hook-writer` and `scriptwriter`. Reviewers: `dont-do-reviewer`, `hook-reviewer`, `voice-reviewer`, `structure-reviewer`, `fact-reviewer` and the `critic`. The agents only read and return their work; they never save anything. Where agents aren't available (ChatGPT, Claude on the web or mobile, Codex without subagents), Sofia runs the same roles one after another as passes.

## Optional Sofia tools

Some hosts may connect the optional Sofia tools: `list_method_pieces`, `read_method_piece` and `check_script`. When they are available, Sofia runs `check_script` on every finished hook and script and opens method pieces with `read_method_piece` (by full id, such as `knowledge/hooks-that-work`, or by name when it is unique). `check_script` returns points to review, not required fixes: they are automatic signals that can be false positives, and the tool covers only part of the Floor. Its 15-word limit on the first sentence and the words per minute behind the time estimate are the tool's references, not rules of the method. When they aren't, she uses the bundled references and checks the same rules by hand (they are listed in `skills/sofia-english/references/checks.json`).

What the server receives: the text sent to `check_script`, and the id of the method piece requested. It stores nothing and requires no sign-in.

## External services

No external service is part of this plugin, and Sofia does not depend on another app. She works with what the person brings: pasted text, a file, a link or an export. If social media data is missing, she asks the person to paste it or export it (a file, a transcript or screenshots). If the person asks her to use a tool they already have, she follows the request, after saying what it will fetch, how many items and the estimated cost. She never reads browser cookies or sessions, never bypasses a sign-in and never asks for a password.

## Requirements and limits

Text work (ideas, research with the host's own search, hooks, scripts, critique, transcript analysis) needs nothing else. Optional local tools, used only with a terminal and the person's authorization:

- FFmpeg and ffprobe, plus a tool that can open images, to sample frames, contact sheets and audio from a video file. They do not transcribe speech or identify effects on their own.
- yt-dlp, to download a public reference video the person is allowed to use, after their authorization, with no cookies.

The plugin ships text only: no scripts or executables. Without a terminal, Sofia analyzes the transcript as text and says which layers (images, audio, cuts, metrics) she did not see.

## Where work is saved

Sofia keeps each video's working record (the video brief) in the conversation. When the host has file tools and the person agrees, she saves to the folder they choose, under `sofia-english/`: `briefs/` (one per video), `styles/` (creator profiles and voices), `analyses/` and `swipe-file/` (saved references). Nothing is saved inside the plugin installation, and nothing is saved without saying what and where. Comments are kept as literal text, without the author's name or handle. There is no built-in telemetry.

## Publisher, privacy, terms and support

Published by **Action Criação Digital Ltda (Criadores do Futuro)**.

- [Privacy Policy](https://plataforma.academiacriadoresdofuturo.com.br/sofia-english/privacy)
- [Terms](https://plataforma.academiacriadoresdofuturo.com.br/sofia-english/terms)
- [Support](https://plataforma.academiacriadoresdofuturo.com.br/sofia-english/support)
- [Website](https://plataforma.academiacriadoresdofuturo.com.br/sofia-english)

Proprietary license: [LICENSE](LICENSE). The no AI-speak rules are adapted from [stop-slop](https://github.com/hardikpandya/stop-slop) by Hardik Pandya (MIT license). The full notice is at the end of the `no-ai-speak` piece, in `skills/sofia-english/references/no-ai-speak.md`.
