"""Heuristic caption profile scoring."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from cutscribe.models import CaptionPreset, ProfileScore, VideoAnalysis


def analyze_video_visuals(video_path: str | Path, sample_count: int = 12) -> VideoAnalysis:
    """Sample video frames and estimate simple visual readability metrics.

    This is deliberately heuristic. It is a starter signal, not a cinematic truth
    machine. Future versions can add face detection, subject masks, and learned
    aesthetic ranking.
    """
    import cv2

    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT)) or sample_count
    width = float(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 16)
    height = float(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 9)
    positions = np.linspace(0, max(frame_count - 1, 0), num=max(sample_count, 1), dtype=int)

    brightness_values: list[float] = []
    contrast_values: list[float] = []
    clutter_values: list[float] = []

    for frame_index in positions:
        capture.set(cv2.CAP_PROP_POS_FRAMES, int(frame_index))
        ok, frame = capture.read()
        if not ok:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness_values.append(float(np.mean(gray) / 255.0))
        contrast_values.append(float(np.std(gray) / 128.0))

        bottom = gray[int(gray.shape[0] * 0.66) :, :]
        edges = cv2.Canny(bottom, 80, 160)
        clutter_values.append(float(np.mean(edges > 0)))

    capture.release()

    if not brightness_values:
        raise ValueError(f"Could not sample frames from video: {video_path}")

    return VideoAnalysis(
        brightness=float(np.clip(np.mean(brightness_values), 0.0, 1.0)),
        contrast=float(np.clip(np.mean(contrast_values), 0.0, 1.0)),
        bottom_third_clutter=float(np.clip(np.mean(clutter_values) * 4.0, 0.0, 1.0)),
        aspect_ratio=width / height,
    )


def score_preset_for_analysis(preset: CaptionPreset, analysis: VideoAnalysis) -> ProfileScore:
    """Score one preset against already-computed video metrics."""
    hints = preset.scoring_hints
    dark_fit = hints.get("prefers_dark_background", 0.5) * (1.0 - analysis.brightness)
    bright_fit = hints.get("prefers_bright_background", 0.5) * analysis.brightness
    contrast_fit = min(analysis.contrast + 0.25, 1.0)
    clutter_tolerance = hints.get("clutter_tolerance", 0.5)
    clutter_fit = 1.0 - max(0.0, analysis.bottom_third_clutter - clutter_tolerance)

    raw_score = (dark_fit + bright_fit + contrast_fit + clutter_fit) / 4.0
    score = float(np.clip(raw_score, 0.0, 1.0))

    reasons = []
    if analysis.bottom_third_clutter > 0.65:
        reasons.append("busy bottom third")
    if analysis.brightness < 0.35:
        reasons.append("dark footage")
    elif analysis.brightness > 0.65:
        reasons.append("bright footage")
    if analysis.contrast < 0.25:
        reasons.append("low contrast")
    if not reasons:
        reasons.append("balanced visual profile")

    return ProfileScore(preset_id=preset.id, score=score, reasons=reasons)


def rank_presets(presets: list[CaptionPreset], analysis: VideoAnalysis) -> list[ProfileScore]:
    """Return preset scores from strongest to weakest."""
    return sorted(
        (score_preset_for_analysis(preset, analysis) for preset in presets),
        key=lambda item: item.score,
        reverse=True,
    )


def choose_best_preset(presets: list[CaptionPreset], analysis: VideoAnalysis) -> CaptionPreset | None:
    """Return the highest-scoring preset, if any presets exist."""
    if not presets:
        return None
    scores = rank_presets(presets, analysis)
    best_id = scores[0].preset_id
    return next(preset for preset in presets if preset.id == best_id)
