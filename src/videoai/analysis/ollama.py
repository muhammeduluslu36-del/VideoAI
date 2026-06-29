import httpx

from videoai.config import settings


class OllamaAnalyzer:
    def __init__(self) -> None:
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model

    def chat(self, prompt: str, system: str = "") -> str:
        payload: dict = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        if system:
            payload["system"] = system

        response = httpx.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        return response.json().get("response", "")

    def analyze_transcript(self, transcript: str) -> str:
        return self.chat(
            f"Analyze this video transcript. Provide a summary and key points:\n\n{transcript}",
            system="You are a helpful video content analyst.",
        )

    def is_available(self) -> bool:
        try:
            httpx.get(f"{self.base_url}/api/tags", timeout=3).raise_for_status()
            return True
        except Exception:
            return False
