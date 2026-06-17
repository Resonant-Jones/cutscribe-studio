from cutscribe.core.profile_scorer import choose_best_preset, rank_presets, score_preset_for_analysis
from cutscribe.models import CaptionPreset, CaptionStyle, VideoAnalysis


def make_preset(preset_id: str, **hints: float) -> CaptionPreset:
    return CaptionPreset(
        id=preset_id,
        name=preset_id,
        style=CaptionStyle(),
        scoring_hints=hints,
    )


def test_profile_score_stays_between_zero_and_one() -> None:
    preset = make_preset("classic", prefers_dark_background=0.8, clutter_tolerance=0.9)
    analysis = VideoAnalysis(
        brightness=0.25,
        contrast=0.55,
        bottom_third_clutter=0.3,
        aspect_ratio=16 / 9,
    )

    score = score_preset_for_analysis(preset, analysis)

    assert 0.0 <= score.score <= 1.0
    assert score.preset_id == "classic"
    assert score.reasons


def test_rank_presets_prefers_dark_friendly_preset_for_dark_video() -> None:
    dark = make_preset("dark-friendly", prefers_dark_background=1.0, clutter_tolerance=0.8)
    bright = make_preset("bright-friendly", prefers_bright_background=1.0, clutter_tolerance=0.8)
    analysis = VideoAnalysis(
        brightness=0.2,
        contrast=0.5,
        bottom_third_clutter=0.2,
        aspect_ratio=9 / 16,
    )

    ranked = rank_presets([bright, dark], analysis)

    assert ranked[0].preset_id == "dark-friendly"


def test_choose_best_preset_returns_none_for_empty_list() -> None:
    analysis = VideoAnalysis(
        brightness=0.5,
        contrast=0.5,
        bottom_third_clutter=0.5,
        aspect_ratio=1.0,
    )

    assert choose_best_preset([], analysis) is None
