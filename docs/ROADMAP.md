# Roadmap

## Phase 0: scaffold

- Create Python `src/` layout.
- Add PySide6 application shell.
- Add preset models and sample JSON presets.
- Add FFmpeg, transcription, auto-cut, render, and scoring module seams.
- Add basic tests.

## Phase 1: captioned MP4 from local video

- Validate FFmpeg availability on launch.
- Extract audio from selected video.
- Run faster-whisper locally.
- Generate transcript with word timestamps.
- Write SRT and ASS subtitle files.
- Render captioned MP4.
- Keep logs visible in the UI.

## Phase 2: auto-cut plus smart preset selection

- Run FFmpeg silence detection.
- Create a padded speech cut plan.
- Preview cut plan in the UI.
- Sample frames from video.
- Score available caption presets.
- Recommend a preset before render.

## Phase 3: active-word caption system

- Generate ASS events with per-word timing.
- Support active-word highlight color.
- Support caption entrance and emphasis animation primitives.
- Add preview thumbnails or short preview renders.

## Phase 4: creator workflow polish

- Drag-and-drop import.
- Batch queue.
- Export presets.
- Project save files.
- Recent projects.
- Render progress and cancellation.

## Phase 5: visual intelligence

- Face and subject-region detection.
- Bottom-third occupancy scoring.
- Brand profile memory.
- Per-video preset recommendation.
- Optional user preference learning.
