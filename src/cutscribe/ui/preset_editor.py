"""Preset editor placeholder widgets.

The first scaffold loads JSON presets directly. A visual preset editor belongs in
an early polish milestone once the render path is stable.
"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class PresetEditor(QWidget):
    """Minimal placeholder for a future visual preset editor."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Preset editor coming soon."))
