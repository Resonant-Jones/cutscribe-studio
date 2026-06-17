from pathlib import Path

from cutscribe.core.render import write_ass, write_srt
from cutscribe.models import CaptionPreset, CaptionStyle, TranscriptSegment, TranscriptionResult


def make_transcript() -> TranscriptionResult:
    return TranscriptionResult(
        language="en",
        duration=2.5,
        segments=[
            TranscriptSegment(text="hello world", start=0.0, end=1.25),
            TranscriptSegment(text="caption forge", start=1.5, end=2.5),
        ],
    )


def make_preset() -> CaptionPreset:
    return CaptionPreset(
        id="test-bold",
        name="Test Bold",
        style=CaptionStyle(
            font_family="Arial Black",
            font_size=60,
            primary_color="#FFFFFF",
            outline_color="#000000",
            highlight_color="#FF3FD1",
            uppercase=True,
        ),
    )


def test_write_srt_outputs_numbered_segments(tmp_path: Path) -> None:
    output = write_srt(make_transcript(), tmp_path / "captions.srt")

    text = output.read_text(encoding="utf-8")

    assert "1\n00:00:00,000 --> 00:00:01,250\nhello world" in text
    assert "2\n00:00:01,500 --> 00:00:02,500\ncaption forge" in text


def test_write_ass_outputs_styled_dialogue(tmp_path: Path) -> None:
    output = write_ass(make_transcript(), tmp_path / "captions.ass", make_preset())

    text = output.read_text(encoding="utf-8")

    assert "[V4+ Styles]" in text
    assert "Style: Default,Arial Black,60" in text
    assert "&H00FFFFFF" in text
    assert "&H00D13FFF" in text
    assert "Dialogue: 0,0:00:00.00,0:00:01.25" in text
    assert "HELLO WORLD" in text
