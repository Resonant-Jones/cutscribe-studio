"""Preset loading and saving."""

from __future__ import annotations

import json
from pathlib import Path

from cutscribe.models import CaptionPreset


def load_preset(path: str | Path) -> CaptionPreset:
    """Load a single caption preset JSON file."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return CaptionPreset.model_validate(data)


def load_presets(directory: str | Path) -> list[CaptionPreset]:
    """Load all presets from a directory, sorted by file name."""
    root = Path(directory)
    if not root.exists():
        return []
    return [load_preset(path) for path in sorted(root.glob("*.json"))]


def save_preset(preset: CaptionPreset, directory: str | Path) -> Path:
    """Save a preset as pretty JSON using its id as the file name."""
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{preset.id}.json"
    path.write_text(preset.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return path
