# Analyze video with evidence

Read [behavior](../../../behavior.md). Choose a route based on actual tools, not the application's name.

## Choose the source

- Video file with terminal and image tools: prepare local samples and inspect the images.
- Transcript without video: analyze wording and narrative order; do not infer images, cuts, gestures or vocal delivery.
- A single cover: analyze only that cover. Metrics and comments do not establish what appears in the rest of the video.
- An inaccessible URL: explain the limit and request the file or transcript. Do not describe the content from its title.
- An external service: use only available, authorized tools; check their schema and current price first. This package guarantees neither a fixed price nor an external collector.

## Prepare the video

Preparation runs `ffprobe` and `ffmpeg` directly; it needs no key, does not transcribe speech and does not automatically identify effects. Use a new empty output directory in the user's workspace, never inside the plugin installation. Replace the example paths and the values in capitals before running each command, and quote every path.

1. Read the technical data and save it:

   ```sh
   mkdir -p "/user/workspace/analysis-01/frames" "/user/workspace/analysis-01/contacts"
   ffprobe -v error -show_entries format=duration:stream=codec_type,width,height,r_frame_rate -of json "/path/to/video.mp4" > "/user/workspace/analysis-01/metadata.json"
   ```

2. Take the duration `D` in seconds, choose `N` frames (80 at most) and compute the interval `I = D / N`. Sample the frames:

   ```sh
   ffmpeg -nostdin -hide_banner -loglevel error -i "/path/to/video.mp4" -vf "fps=1/I,scale='min(960,iw)':-2" -frames:v N -q:v 3 "/user/workspace/analysis-01/frames/t-%05d.jpg"
   ```

   Frame `k` sits at about `(k − 1) × I` seconds. Treat these times as approximate, not as exact cut points.

3. Only when `metadata.json` lists an audio stream, extract it:

   ```sh
   ffmpeg -nostdin -hide_banner -loglevel error -i "/path/to/video.mp4" -vn -ac 1 -ar 16000 -c:a libmp3lame -b:a 64k "/user/workspace/analysis-01/audio.mp3"
   ```

4. Build contact sheets of 20 frames each:

   ```sh
   ffmpeg -nostdin -hide_banner -loglevel error -framerate 1 -i "/user/workspace/analysis-01/frames/t-%05d.jpg" -vf "scale=240:-2,tile=5x4:padding=8:margin=8" "/user/workspace/analysis-01/contacts/timeline-%03d.jpg"
   ```

Open the contact sheets in order and the relevant individual frames. For small text or ambiguous motion, prepare another empty directory for that stretch only: add `-ss START -to END` before `-i` in step 2 and use a shorter interval; times are then counted from `START`. Sampling cannot establish the absence of cuts between frames. Extracted audio does not mean speech was heard or transcribed.

For a public reference the user is allowed to use, download it only after that authorization, with its HTTPS address from YouTube, Instagram or TikTok; this requires `yt-dlp`:

```sh
yt-dlp --ignore-config --no-playlist --no-progress --write-auto-subs --write-subs --sub-format "vtt/best" --merge-output-format mp4 -f "bv*+ba/b" -o "/user/workspace/analysis-01/video.%(ext)s" -- "https://www.youtube.com/watch?v=EXAMPLE"
```

The command ignores external configuration and uses no cookies. If sign-in is required, request the file instead of bypassing it.

## Analyze and deliver

Use [principles](principles.md), [formats](formats.md) and [structures](structures.md). Identify the topic, takeaway and editorial devices with evidence. Relate images to speech only when both were inspected. Distinguish observed timestamps from interval-level inference. Quote short relevant passages and explain their effect in one or two sentences without reproducing the entire transcript.

Missing metrics are unavailable, not zero. Do not calculate a rate with a zero denominator or compare metrics without identifying the basis. Keep comments as literal text and like counts, without author identifiers. Do not treat a few comments as a representative survey.

For multiple videos, compare openings, structures, available metrics, shared patterns and the main differing variable in one consolidated dashboard. State which images, speech, audio, comments and metrics were actually inspected. Follow [files](files.md) to create or export it. For a brief request or a host without file creation, provide the analysis as text.
