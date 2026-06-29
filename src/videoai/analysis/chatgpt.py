from openai import OpenAI

from videoai.config import settings


class ChatGPTAnalyzer:
    MODEL = "gpt-4o"

    def __init__(self) -> None:
        self._client: OpenAI | None = None

    def _client_or_raise(self) -> OpenAI:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        if self._client is None:
            self._client = OpenAI(api_key=settings.openai_api_key)
        return self._client

    def chat(self, prompt: str, system: str = "") -> str:
        client = self._client_or_raise()
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=self.MODEL,
            messages=messages,
            max_tokens=1024,
        )
        return response.choices[0].message.content or ""

    def analyze_transcript(self, transcript: str) -> str:
        system = (
            "You are a video content analyst. Analyze transcripts and provide "
            "structured insights about content, key moments, and social media potential."
        )
        return self.chat(
            f"Analyze this transcript and summarize key points:\n\n{transcript}",
            system=system,
        )
