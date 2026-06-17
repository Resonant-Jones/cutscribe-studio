"""Simple silence-aware auto-cut planning."""

from __future__ import annotations

from pathlib import Path

from cutscribe.models import CutPlan, CutSegment, SilenceInterval


def build_cut_plan(
    source_path: str | Path,
    duration: float,
    silences: list[SilenceInterval],
    padding_seconds: float = 0.18,
) -> CutPlan:
    """Convert silence intervals into padded speech segments.

    This function returns a plan only. It does not mutate media or perform final
    concatenation yet. Timeline editing comes later.
    """
    cursor = 0.0
    speech: list[CutSegment] = []

    for silence in sorted(silences, key=lambda item: item.start):
        if silence.start > cursor:
            speech.append(CutSegment(start=cursor, end=silence.start))
        cursor = max(cursor, silence.end)

    if cursor < duration:
        speech.append(CutSegment(start=cursor, end=duration))

    padded = [
        CutSegment(
            start=max(0.0, segment.start - padding_seconds),
            end=min(duration, segment.end + padding_seconds),
        )
        for segment in speech
        if segment.end > segment.start
    ]

    merged: list[CutSegment] = []
    for segment in padded:
        if not merged or segment.start > merged[-1].end:
            merged.append(segment)
        else:
            merged[-1].end = max(merged[-1].end, segment.end)

    return CutPlan(
        source_path=str(source_path),
        duration=duration,
        padding_seconds=padding_seconds,
        segments=merged,
    )
