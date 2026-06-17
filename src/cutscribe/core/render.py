"""Subtitle and video rendering helpers."""

from __future__ import annotations

import shutil
from pathlib import Path

from cutscribe.core.ffmpeg import ensure_binary, run_command
from cutscribe.models import CaptionPreset, TranscriptionResult


def _format_srt_time(seconds: float) -> str:
    millis = int(round(seconds * 1000))
    hours, rem = divmod(millis, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, ms = divmod(rem, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{ms:03}"


def write_srt(transcript: TranscriptionResult, output_path: str | Path) -> Path:
    """Write a simple SRT file from transcript segments.

    This is the starter path. ASS active-word caption output belongs in the next
    milestone and should preserve word-level timing.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for index, segment in enumerate(transcript.segments, start=1):
        lines.extend(
            [
                str(index),
                f"{_format_srt_time(segment.start)} --> {_format_srt_time(segment.end)}",
                segment.text,
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def render_captioned_video(
    input_video: str | Path,
    subtitle_file: str | Path,
    output_video: str | Path,
    preset: CaptionPreset,
) -> Path:
    """Burn subtitles into a video with FFmpeg.

    The `preset` argument is accepted now so the renderer interface is stable.
    The current implementation uses FFmpeg's `subtitles` filter with simple SRT.
    Full preset-driven ASS styling is a marked placeholder.
    """
    ensure_binary("ffmpeg")
    output = Path(output_video)
    output.parent.mkdir(parents=True, exist_ok=True)

    # Placeholder: convert CaptionPreset -> ASS style and render active-word events.
    # For now, burn the provided subtitle file.
    subtitle_path = str(Path(subtitle_file).resolve()).replace("'", "\\'")
    args = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_video),
        "-vf",
        f"subtitles='{subtitle_path}'",
        "-c:a",
        "copy",
        str(output),
    ]
    run_command(args)
    return output


def copy_video_placeholder(input_video: str | Path, output_video: str | Path) -> Path:
    """Copy a video when render prerequisites are missing.

    This keeps the UI button useful during scaffold testing without pretending a
    full render has happened.
    """
    output = Path(output_video)
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(input_video, output)
    return output
