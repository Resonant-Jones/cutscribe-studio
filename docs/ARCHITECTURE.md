# Architecture

CutScribe Studio is organized as a local-first desktop application with clean seams between UI, media analysis, transcription, auto-cut planning, preset scoring, and rendering.

## Runtime layers

```text
PySide6 UI
  -> app orchestration
    -> core/transcribe.py      local faster-whisper transcription
    -> core/ffmpeg.py          FFmpeg and ffprobe wrappers
    -> core/autocut.py         silence-aware cut plan generation
    -> core/presets.py         JSON preset loading and validation
    -> core/profile_scorer.py  heuristic visual scoring
    -> core/render.py          subtitle and MP4 rendering
```

## Design principles

- Local-first by default. No cloud transcription is required for the core path.
- Media files stay on the user's machine.
- Presets are plain JSON so users can inspect, copy, and share them.
- Heavy operations should move to background workers as soon as the first UI loop is stable.
- Placeholders must be explicit. The scaffold should never imply completed behavior that does not exist yet.

## First real pipeline

1. User selects an input video.
2. FFmpeg extracts audio to a temporary WAV file.
3. faster-whisper generates transcript segments and word timestamps.
4. CutScribe writes subtitles from the transcript.
5. FFmpeg burns subtitles into an MP4 export.

## Auto-cut pipeline

The initial auto-cut plan is intentionally simple:

1. FFmpeg runs `silencedetect`.
2. Detected silence intervals are converted into speech intervals.
3. Speech intervals receive configurable padding.
4. Overlapping padded intervals are merged.
5. The resulting `CutPlan` can later feed timeline editing or direct FFmpeg concatenation.

## Smart preset selection

The first scoring system is heuristic-based, not ML-based:

- Estimate frame brightness.
- Estimate frame contrast.
- Estimate bottom-third visual clutter.
- Score preset readability against those metrics.

Future versions can add face detection, subject framing, brand memory, per-user aesthetic preference, and learned ranking.

## Known scaffold limitations

- Rendering currently uses a simple SRT path and leaves ASS active-word caption generation as a marked placeholder.
- UI operations currently run synchronously. This is acceptable for the scaffold but should move to worker threads quickly.
- Auto-cut produces a plan only. It does not yet perform timeline-accurate video concatenation.
