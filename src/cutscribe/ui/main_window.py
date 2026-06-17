"""Minimal CutScribe Studio Qt window."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from cutscribe.core.autocut import build_cut_plan
from cutscribe.core.ffmpeg import detect_silence, probe_duration
from cutscribe.core.presets import load_presets
from cutscribe.core.profile_scorer import analyze_video_visuals, rank_presets
from cutscribe.core.render import copy_video_placeholder
from cutscribe.core.transcribe import Transcriber
from cutscribe.models import CaptionPreset


def default_preset_dir() -> Path:
    """Return the preset directory for editable local development."""
    env_dir = os.getenv("CUTSCRIBE_PRESET_DIR")
    if env_dir:
        return Path(env_dir)
    repo_root = Path(__file__).resolve().parents[3]
    return repo_root / "presets"


class MainWindow(QMainWindow):
    """Small UI shell for the first local pipeline."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("CutScribe Studio")
        self.resize(920, 620)

        self.presets: list[CaptionPreset] = load_presets(default_preset_dir())
        self.input_edit = QLineEdit()
        self.output_edit = QLineEdit(str(Path.cwd() / "exports"))
        self.preset_combo = QComboBox()
        self.log = QTextEdit()
        self.log.setReadOnly(True)

        self._build_ui()
        self._load_preset_combo()

    def _build_ui(self) -> None:
        central = QWidget()
        root = QVBoxLayout(central)
        grid = QGridLayout()

        input_button = QPushButton("Choose video")
        input_button.clicked.connect(self.choose_video)
        output_button = QPushButton("Choose output folder")
        output_button.clicked.connect(self.choose_output_folder)

        grid.addWidget(QLabel("Input video"), 0, 0)
        grid.addWidget(self.input_edit, 0, 1)
        grid.addWidget(input_button, 0, 2)
        grid.addWidget(QLabel("Output folder"), 1, 0)
        grid.addWidget(self.output_edit, 1, 1)
        grid.addWidget(output_button, 1, 2)
        grid.addWidget(QLabel("Caption preset"), 2, 0)
        grid.addWidget(self.preset_combo, 2, 1, 1, 2)

        actions = QHBoxLayout()
        analyze_button = QPushButton("Analyze")
        transcribe_button = QPushButton("Transcribe")
        render_button = QPushButton("Render")
        analyze_button.clicked.connect(self.analyze_video)
        transcribe_button.clicked.connect(self.transcribe_video)
        render_button.clicked.connect(self.render_video_placeholder)
        actions.addWidget(analyze_button)
        actions.addWidget(transcribe_button)
        actions.addWidget(render_button)
        actions.addStretch(1)

        root.addLayout(grid)
        root.addLayout(actions)
        root.addWidget(QLabel("Log"))
        root.addWidget(self.log, stretch=1)
        self.setCentralWidget(central)

    def _load_preset_combo(self) -> None:
        self.preset_combo.clear()
        if not self.presets:
            self.preset_combo.addItem("No presets found", None)
            return
        for preset in self.presets:
            self.preset_combo.addItem(preset.name, preset.id)

    def append_log(self, message: str) -> None:
        self.log.append(message)
        self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())

    def selected_video(self) -> Path | None:
        path = Path(self.input_edit.text()).expanduser()
        return path if path.exists() else None

    def selected_preset(self) -> CaptionPreset | None:
        preset_id = self.preset_combo.currentData()
        return next((preset for preset in self.presets if preset.id == preset_id), None)

    def choose_video(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose a video",
            str(Path.home()),
            "Videos (*.mp4 *.mov *.mkv *.avi);;All files (*.*)",
        )
        if path:
            self.input_edit.setText(path)
            self.append_log(f"Selected video: {path}")

    def choose_output_folder(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Choose output folder", self.output_edit.text())
        if path:
            self.output_edit.setText(path)
            self.append_log(f"Selected output folder: {path}")

    def analyze_video(self) -> None:
        video = self.selected_video()
        if not video:
            self.append_log("Choose a valid input video first.")
            return
        try:
            duration = probe_duration(video)
            silences = detect_silence(video)
            cut_plan = build_cut_plan(video, duration, silences)
            self.append_log(f"Duration: {duration:.2f}s")
            self.append_log(f"Detected silences: {len(silences)}")
            self.append_log(f"Auto-cut keep segments: {len(cut_plan.segments)}")

            if self.presets:
                analysis = analyze_video_visuals(video)
                scores = rank_presets(self.presets, analysis)
                best = scores[0]
                self.append_log(
                    f"Best preset candidate: {best.preset_id} "
                    f"({best.score:.2f}) - {', '.join(best.reasons)}"
                )
        except Exception as exc:  # noqa: BLE001 - UI should surface pipeline errors.
            self.append_log(f"Analyze failed: {exc}")

    def transcribe_video(self) -> None:
        video = self.selected_video()
        if not video:
            self.append_log("Choose a valid input video first.")
            return
        try:
            model_name = os.getenv("CUTSCRIBE_WHISPER_MODEL", "small")
            transcriber = Transcriber(model_size=model_name)
            result = transcriber.transcribe(video)
            word_count = sum(len(segment.words) for segment in result.segments)
            self.append_log(
                f"Transcribed {len(result.segments)} segments / {word_count} words. "
                f"Language={result.language}"
            )
        except Exception as exc:  # noqa: BLE001
            self.append_log(f"Transcription failed: {exc}")

    def render_video_placeholder(self) -> None:
        video = self.selected_video()
        preset = self.selected_preset()
        if not video:
            self.append_log("Choose a valid input video first.")
            return
        if not preset:
            self.append_log("Choose a valid preset first.")
            return

        output_dir = Path(self.output_edit.text()).expanduser()
        output_path = output_dir / f"{video.stem}.cutscribe.placeholder.mp4"
        try:
            copy_video_placeholder(video, output_path)
            self.append_log(
                f"Placeholder render copied video to {output_path}. "
                "Full caption render comes next."
            )
        except Exception as exc:  # noqa: BLE001
            self.append_log(f"Render failed: {exc}")


def run() -> int:
    """Run the Qt event loop."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()
