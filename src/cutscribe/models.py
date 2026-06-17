"""Shared domain models for CutScribe Studio."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

CaptionPosition = Literal["bottom_center", "middle_center", "top_center"]


class CaptionStyle(BaseModel):
    """Visual styling for generated captions."""

    font_family: str = "Arial"
    font_size: int = Field(default=64, gt=0)
    primary_color: str = "#FFFFFF"
    outline_color: str = "#000000"
    highlight_color: str = "#FFD54A"
    stroke_width: int = Field(default=4, ge=0)
    shadow: int = Field(default=2, ge=0)
    position: CaptionPosition = "bottom_center"
    uppercase: bool = False
    max_words_on_screen: int = Field(default=5, gt=0)


class CaptionPreset(BaseModel):
    """Reusable caption profile loaded from a JSON preset file."""

    id: str
    name: str
    description: str = ""
    style: CaptionStyle = Field(default_factory=CaptionStyle)
    scoring_hints: dict[str, float] = Field(default_factory=dict)


class TranscriptWord(BaseModel):
    """A word-level timestamp emitted by faster-whisper."""

    text: str
    start: float
    end: float
    probability: float | None = None


class TranscriptSegment(BaseModel):
    """A transcript segment with optional word-level timings."""

    text: str
    start: float
    end: float
    words: list[TranscriptWord] = Field(default_factory=list)


class TranscriptionResult(BaseModel):
    """Full transcription result for a media item."""

    language: str | None = None
    duration: float | None = None
    segments: list[TranscriptSegment] = Field(default_factory=list)


class SilenceInterval(BaseModel):
    """A detected silence interval in seconds."""

    start: float
    end: float


class CutSegment(BaseModel):
    """A segment to preserve in an auto-cut export."""

    start: float
    end: float


class CutPlan(BaseModel):
    """A simple list of timeline intervals to keep."""

    source_path: str
    duration: float
    padding_seconds: float
    segments: list[CutSegment] = Field(default_factory=list)


class VideoAnalysis(BaseModel):
    """Visual metrics used for preset scoring."""

    brightness: float = Field(ge=0.0, le=1.0)
    contrast: float = Field(ge=0.0, le=1.0)
    bottom_third_clutter: float = Field(ge=0.0, le=1.0)
    aspect_ratio: float = Field(gt=0.0)


class ProfileScore(BaseModel):
    """Score for a preset against a video's visual profile."""

    preset_id: str
    score: float = Field(ge=0.0, le=1.0)
    reasons: list[str] = Field(default_factory=list)
