"""Local transcription via faster-whisper."""

from __future__ import annotations

from pathlib import Path

from cutscribe.models import TranscriptSegment, TranscriptionResult, TranscriptWord


class Transcriber:
    """Thin faster-whisper adapter.

    The model is loaded lazily so the UI can start quickly. Real production use
    should run this in a worker thread or process to avoid blocking Qt.
    """

    def __init__(self, model_size: str = "small", device: str = "auto", compute_type: str = "auto") -> None:
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model = None

    def _load_model(self):
        if self._model is None:
            from faster_whisper import WhisperModel

            kwargs = {}
            if self.device != "auto":
                kwargs["device"] = self.device
            if self.compute_type != "auto":
                kwargs["compute_type"] = self.compute_type
            self._model = WhisperModel(self.model_size, **kwargs)
        return self._model

    def transcribe(self, audio_or_video_path: str | Path) -> TranscriptionResult:
        """Transcribe a local audio or video file with word timestamps."""
        model = self._load_model()
        segments_iter, info = model.transcribe(str(audio_or_video_path), word_timestamps=True)

        segments: list[TranscriptSegment] = []
        for segment in segments_iter:
            words = [
                TranscriptWord(
                    text=word.word.strip(),
                    start=float(word.start),
                    end=float(word.end),
                    probability=getattr(word, "probability", None),
                )
                for word in (segment.words or [])
            ]
            segments.append(
                TranscriptSegment(
                    text=segment.text.strip(),
                    start=float(segment.start),
                    end=float(segment.end),
                    words=words,
                )
            )

        return TranscriptionResult(
            language=getattr(info, "language", None),
            duration=getattr(info, "duration", None),
            segments=segments,
        )
