# CutScribe Studio

CutScribe Studio is a local-first desktop video clipping and captioning tool. The initial target is a CapCut-style workflow for creators who want to drop in a video, generate captions locally, trim dead air, apply reusable caption presets, and export a ready-to-post MP4.

The project is intentionally starting small and honest: the first milestone is a captioned MP4 from a local video. The second milestone is auto-cut plus smart preset selection.

## Product intent

CutScribe Studio is designed around a local-first pipeline:

- **PySide6 / Qt for Python** for the desktop UI.
- **faster-whisper** for local transcription and word timestamps.
- **FFmpeg** for audio extraction, silence detection, subtitle burn-in, and rendering.
- **JSON preset files** for reusable caption styling.
- **Heuristic profile scoring** as the first step toward automatically selecting the most flattering caption profile per video.

## Current scaffold status

This repository currently contains a runnable skeleton, not a finished editor. Several pipeline seams are implemented as thin wrappers or explicit placeholders so the architecture can grow without pretending the dragon is already house-trained.

Implemented now:

- Minimal PySide6 window.
- Input video picker.
- Output folder picker.
- Preset loading from `presets/*.json`.
- Analyze, Transcribe, and Render action buttons.
- FFmpeg helper wrappers.
- Silence-detection parser.
- Preset models and validation.
- Heuristic profile scoring placeholder.
- Styled ASS subtitle generation from transcript segments.
- Compatibility SRT subtitle generation.
- FFmpeg caption burn-in path for captioned MP4 exports.
- Tests for preset loading, profile scoring, and subtitle formatting.

Planned next:

- Active-word ASS caption generation from word timestamps.
- Timeline-aware auto-cut exports.
- Batch processing.
- Worker threads so long video operations do not block the Qt event loop.
- Stronger frame sampling for visual-aware preset selection.

## Requirements

Install system FFmpeg first:

```bash
ffmpeg -version
ffprobe -version
```

Then install the Python package in editable mode:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## Run

After installing the package:

```bash
python -m cutscribe
```

You can also use the console script:

```bash
cutscribe
```

## First caption render workflow

1. Start the app from the activated virtual environment.
2. Choose an input video.
3. Choose an output folder.
4. Choose a caption preset.
5. Click **Transcribe**.
6. Wait for CutScribe to write both `.ass` and `.srt` subtitle files.
7. Click **Render**.
8. Look for `*.captioned.mp4` in the output folder.

The ASS file carries the current preset styling. Active-word highlighting is not implemented yet, but the render path is now shaped for it.

## Development

Run tests from the activated virtual environment:

```bash
source .venv/bin/activate
pytest
```

If you run plain `pytest` outside the virtual environment, your system Python may not see the editable install or dependencies.

Run linting:

```bash
ruff check .
```

## Milestones

### Milestone 1: captioned MP4 from local video

- Load a local video.
- Extract or read audio.
- Transcribe locally with faster-whisper.
- Produce subtitles with word timestamps.
- Render a captioned MP4 through FFmpeg.

### Milestone 2: auto-cut plus smart preset selection

- Detect silence using FFmpeg `silencedetect`.
- Preserve configurable speech padding.
- Generate a cut plan.
- Sample frames for brightness, contrast, and bottom-third clutter.
- Score presets by readability and aesthetic fit.
- Recommend or auto-apply the strongest preset.

## License

MIT. See `LICENSE`.
