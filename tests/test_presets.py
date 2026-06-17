from pathlib import Path

from cutscribe.core.presets import load_preset, load_presets, save_preset
from cutscribe.models import CaptionPreset, CaptionStyle


def test_load_sample_presets() -> None:
    presets = load_presets(Path(__file__).resolve().parents[1] / "presets")

    assert {preset.id for preset in presets} == {
        "classic-bold",
        "teal-focus",
        "magenta-pop",
    }


def test_save_and_load_preset_roundtrip(tmp_path: Path) -> None:
    preset = CaptionPreset(
        id="test-preset",
        name="Test Preset",
        description="Roundtrip test",
        style=CaptionStyle(font_size=42),
        scoring_hints={"clutter_tolerance": 0.5},
    )

    path = save_preset(preset, tmp_path)
    loaded = load_preset(path)

    assert loaded.id == preset.id
    assert loaded.style.font_size == 42
    assert loaded.scoring_hints["clutter_tolerance"] == 0.5
