from dataclasses import dataclass, field

import anthropic

from videoai.config import settings


@dataclass
class HighlightTimestamp:
    start: float
    end: float
    title: str
    score: float
    reason: str


@dataclass
class VideoAnalysis:
    summary: str
    highlights: list[HighlightTimestamp] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    suggested_title: str = ""
    suggested_description: str = ""
    hashtags: list[str] = field(default_factory=list)


class ClaudeAnalyzer:
    MODEL = "claude-sonnet-4-6"

    def __init__(self) -> None:
        self._client: anthropic.Anthropic | None = None

    def _client_or_raise(self) -> anthropic.Anthropic:
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set")
        if self._client is None:
            self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        return self._client

    def analyze_transcript(self, transcript: str, context: str = "") -> VideoAnalysis:
        client = self._client_or_raise()
        prompt = _build_analysis_prompt(transcript, context)
        message = client.messages.create(
            model=self.MODEL,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        return _parse_analysis(message.content[0].text)

    def find_highlights(self, transcript: str, max_clips: int = 5) -> list[HighlightTimestamp]:
        client = self._client_or_raise()
        prompt = _build_highlights_prompt(transcript, max_clips)
        message = client.messages.create(
            model=self.MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return _parse_highlights(message.content[0].text)

    def generate_social_content(self, transcript: str, platform: str = "general") -> dict:
        client = self._client_or_raise()
        prompt = (
            f"Based on this transcript, generate social media content for {platform}.\n"
            f"Return JSON with: title, description, hashtags (list), hook (first 3 seconds script).\n\n"
            f"Transcript:\n{transcript}"
        )
        message = client.messages.create(
            model=self.MODEL,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        import json, re
        match = re.search(r"\{.*\}", message.content[0].text, re.DOTALL)
        return json.loads(match.group()) if match else {}


def _build_analysis_prompt(transcript: str, context: str) -> str:
    return (
        "Analyze this video transcript and return JSON with:\n"
        "summary, topics (list), suggested_title, suggested_description, hashtags (list).\n\n"
        f"Context: {context}\n\nTranscript:\n{transcript}"
    )


def _build_highlights_prompt(transcript: str, max_clips: int) -> str:
    return (
        f"Find the top {max_clips} most engaging moments in this transcript.\n"
        "Return JSON array with: start (seconds), end (seconds), title, score (0-1), reason.\n\n"
        f"Transcript (with timestamps):\n{transcript}"
    )


def _parse_analysis(text: str) -> VideoAnalysis:
    import json, re
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return VideoAnalysis(summary=text)
    data = json.loads(match.group())
    highlights = [
        HighlightTimestamp(**h) for h in data.get("highlights", [])
    ]
    return VideoAnalysis(
        summary=data.get("summary", ""),
        highlights=highlights,
        topics=data.get("topics", []),
        suggested_title=data.get("suggested_title", ""),
        suggested_description=data.get("suggested_description", ""),
        hashtags=data.get("hashtags", []),
    )


def _parse_highlights(text: str) -> list[HighlightTimestamp]:
    import json, re
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        return []
    data = json.loads(match.group())
    return [HighlightTimestamp(**h) for h in data]
