"""FFmpeg and ffprobe helpers.

These wrappers keep shell execution in one place so the UI and pipeline modules do
not grow subprocess tentacles.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

from cutscribe.models import SilenceInterval


class FFmpegError(RuntimeError):
    """Raised when an FFmpeg command fails."""


def ensure_binary(name: str) -> str:
    """Return the path to a required binary or raise a helpful error."""
    binary = shutil.which(name)
    if not binary:
        raise FFmpegError(f"Required binary not found on PATH: {name}")
    return binary


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    """Run a command and raise `FFmpegError` on non-zero exit."""
    completed = subprocess.run(args, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise FFmpegError(
            "Command failed:\n"
            + " ".join(args)
            + "\n\nSTDOUT:\n"
            + completed.stdout
            + "\n\nSTDERR:\n"
            + completed.stderr
        )
    return completed


def probe_duration(video_path: str | Path) -> float:
    """Return media duration in seconds using ffprobe."""
    ensure_binary("ffprobe")
    args = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(video_path),
    ]
    result = run_command(args)
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def extract_audio(video_path: str | Path, output_wav: str | Path, sample_rate: int = 16000) -> Path:
    """Extract mono WAV audio for transcription."""
    ensure_binary("ffmpeg")
    output = Path(output_wav)
    output.parent.mkdir(parents=True, exist_ok=True)
    args = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        str(sample_rate),
        str(output),
    ]
    run_command(args)
    return output


def detect_silence(
    video_path: str | Path,
    noise_db: int = -35,
    min_duration: float = 0.45,
) -> list[SilenceInterval]:
    """Detect silence intervals using FFmpeg's `silencedetect` filter.

    FFmpeg writes silencedetect events to stderr. This parser extracts matching
    `silence_start` and `silence_end` pairs. Unclosed trailing silence is ignored
    by design for the first scaffold.
    """
    ensure_binary("ffmpeg")
    args = [
        "ffmpeg",
        "-i",
        str(video_path),
        "-af",
        f"silencedetect=noise={noise_db}dB:d={min_duration}",
        "-f",
        "null",
        "-",
    ]
    completed = subprocess.run(args, capture_output=True, text=True, check=False)
    if completed.returncode not in (0, 1):
        # FFmpeg commonly returns 0 here. Keep this guard conservative.
        raise FFmpegError(completed.stderr)

    starts = [
        float(match.group(1))
        for match in re.finditer(r"silence_start: ([0-9.]+)", completed.stderr)
    ]
    ends = [
        float(match.group(1))
        for match in re.finditer(r"silence_end: ([0-9.]+)", completed.stderr)
    ]
    return [
        SilenceInterval(start=start, end=end)
        for start, end in zip(starts, ends, strict=False)
        if end > start
    ]
