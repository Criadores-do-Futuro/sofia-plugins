# Analyze video with evidence

Read [behavior](../../../behavior.md). Choose a route based on actual tools, not the application's name.

## Choose the source

- Video file with terminal and image tools: prepare local samples and inspect the images.
- Transcript without video: analyze wording and narrative order; do not infer images, cuts, gestures or vocal delivery.
- A single cover: analyze only that cover. Metrics and comments do not establish what appears in the rest of the video.
- An inaccessible URL: explain the limit and request the file or transcript. Do not describe the content from its title.
- An external service: use only available, authorized tools; check their schema and current price first. This package guarantees neither a fixed price nor an external collector.

## Prepare the video

Find the absolute plugin root containing `plugin.json`. Replace the descriptive paths below before execution, without depending on Claude-specific variables. Use a new empty output directory.

```sh
python3 "/absolute/plugin/path/scripts/prepare-visual-analysis.py" "/path/to/video.mp4" --output "/user/workspace/analysis-01" --max-frames 80
```

Preparation requires Python 3.10 or newer, `ffmpeg` and `ffprobe`. It needs no key, does not transcribe speech and does not automatically identify effects. For a public reference the user is allowed to use, add `--allow-download` and provide its HTTPS URL; this requires `yt-dlp`. The downloader ignores external configuration and does not use cookies. If sign-in is required, request the file instead of bypassing it.

Read `manifest.json`: its technical fields identify the source, sampled window, paths and decoded frame timestamps. Open contact sheets in order and relevant individual frames. For small text or ambiguous motion, prepare another directory with `--start` and `--end`, increasing density only in that interval. Sampling cannot establish the absence of cuts between frames. Extracted audio does not mean speech was heard or transcribed.

## Analyze and deliver

Use [principles](principles.md), [formats](formats.md) and [structures](structures.md). Identify the topic, takeaway and editorial devices with evidence. Relate images to speech only when both were inspected. Distinguish observed timestamps from interval-level inference. Quote short relevant passages and explain their effect in one or two sentences without reproducing the entire transcript.

Missing metrics are unavailable, not zero. Do not calculate a rate with a zero denominator or compare metrics without identifying the basis. Keep comments as literal text and like counts, without author identifiers. Do not treat a few comments as a representative survey.

For multiple videos, compare openings, structures, available metrics, shared patterns and the main differing variable in one consolidated dashboard. State which images, speech, audio, comments and metrics were actually inspected. Follow [files](files.md) to create or export it. For a brief request or a host without file creation, provide the analysis as text.
