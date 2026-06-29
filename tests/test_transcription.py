from videoai.transcription.whisper import TranscriptionResult, Segment, _format_timestamp


def test_format_timestamp_srt():
    assert _format_timestamp(3661.5) == "01:01:01,500"


def test_format_timestamp_vtt():
    assert _format_timestamp(90.25, vtt=True) == "00:01:30.250"


def test_full_text():
    result = TranscriptionResult(segments=[
        Segment(0.0, 2.0, " Hello"),
        Segment(2.0, 4.0, " world"),
    ])
    assert result.full_text == "Hello world"


def test_to_srt():
    result = TranscriptionResult(segments=[
        Segment(0.0, 2.5, " Test caption"),
    ])
    srt = result.to_srt()
    assert "1\n" in srt
    assert "00:00:00,000 --> 00:00:02,500" in srt
    assert "Test caption" in srt
