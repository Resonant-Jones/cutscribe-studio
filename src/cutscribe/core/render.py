"""Subtitle and video rendering helpers."""

from __future__ import annotations

import shutil
from pathlib import Path

from cutscribe.core.ffmpeg import ensure_binary, run_command
from cutscribe.models import CaptionPreset, TranscriptionResult

ASS_ALIGNMENT_BY_POSITION = {
    "bottom_center": 2,
    "middle_center": 5,
    "top_center": 8,
}


def _format_srt_time(seconds: float) -> str:
    millis = int(round(seconds * 1000))
    hours, rem = divmod(millis, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, ms = divmod(rem, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{ms:03}"


def _format_ass_time(seconds: float) -> str:
    centis = int(round(seconds * 100))
    hours, rem = divmod(centis, 360_000)
    minutes, rem = divmod(rem, 6_000)
    secs, cs = divmod(rem, 100)
    return f"{hours}:{minutes:02}:{secs:02}.{cs:02}"


def _hex_to_ass_color(hex_color: str) -> str:
    """Convert #RRGGBB to ASS &HAABBGGRR format with no alpha."""
    value = hex_color.strip().removeprefix("#")
    if len(value) != 6:
        raise ValueError(f"Expected #RRGGBB color, got: {hex_color}")
    red = value[0:2]
    green = value[2:4]
    blue = value[4:6]
    return f"&H00{blue}{green}{red}".upper()


def _escape_ass_text(text: str) -> str:
    """Escape user transcript text for ASS dialogue events."""
    return text.replace("{", "\\{").replace("}", "\\}").replace("\n", r"\N")


def _escape_filter_path(path: str | Path) -> str:
    """Escape a subtitle path for FFmpeg's subtitles filter.

    FFmpeg filter syntax treats backslashes, colons, and single quotes as special
    in different positions. This keeps local paths with spaces and apostrophes
    usable without shell=True.
    """
    resolved = str(Path(path).resolve())
    return resolved.replace("\\", r"\\").replace(":", r"\:").replace("'", r"\'")


def write_srt(transcript: TranscriptionResult, output_path: str | Path) -> Path:
    """Write a simple SRT file from transcript segments.

    This is useful for debugging and compatibility. The normal styled render path
    should use `write_ass` so presets can affect caption appearance.
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


def write_ass(
    transcript: TranscriptionResult,
    output_path: str | Path,
    preset: CaptionPreset,
    play_res_x: int = 1080,
    play_res_y: int = 1920,
) -> Path:
    """Write a styled ASS subtitle file from transcript segments.

    This is not active-word highlighting yet. It is the first real styled caption
    output path and preserves the interface needed for word-level ASS events.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    style = preset.style
    alignment = ASS_ALIGNMENT_BY_POSITION.get(style.position, 2)
    primary = _hex_to_ass_color(style.primary_color)
    outline = _hex_to_ass_color(style.outline_color)
    highlight = _hex_to_ass_color(style.highlight_color)
    font_name = style.font_family.replace(",", " ")
    bold = -1 if "bold" in font_name.lower() or "black" in font_name.lower() else 0
    back_color = "&H64000000"
    style_values = [
        "Default",
        font_name,
        str(style.font_size),
        primary,
        highlight,
        outline,
        back_color,
        str(bold),
        "0",
        "0",
        "0",
        "100",
        "100",
        "0",
        "0",
        "1",
        str(style.stroke_width),
        str(style.shadow),
        str(alignment),
        "80",
        "80",
        "120",
        "1",
    ]

    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "WrapStyle: 0",
        "ScaledBorderAndShadow: yes",
        f"PlayResX: {play_res_x}",
        f"PlayResY: {play_res_y}",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: " + ",".join(style_values),
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]

    for segment in transcript.segments:
        text = segment.text.upper() if style.uppercase else segment.text
        lines.append(
            "Dialogue: 0,"
            f"{_format_ass_time(segment.start)},{_format_ass_time(segment.end)},"
            f"Default,,0,0,0,,{_escape_ass_text(text)}"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def render_captioned_video(
    input_video: str | Path,
    subtitle_file: str | Path,
    output_video: str | Path,
    preset: CaptionPreset,
) -> Path:
    """Burn subtitles into a video with FFmpeg.

    ASS files can carry preset styling. SRT files still work, but styling will be
    limited by FFmpeg/libass behavior.
    """
    ensure_binary("ffmpeg")
    output = Path(output_video)
    output.parent.mkdir(parents=True, exist_ok=True)

    subtitle_path = _escape_filter_path(subtitle_file)
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

    Retained as a dev fallback, but the UI now prefers real subtitle rendering.
    """
    output = Path(output_video)
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(input_video, output)
    return output
