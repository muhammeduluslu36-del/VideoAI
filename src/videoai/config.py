from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Keys
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # Whisper
    whisper_model: str = "large-v3"
    whisper_device: str = "auto"

    # FFmpeg
    ffmpeg_path: str = "ffmpeg"

    # Paths
    data_input_dir: Path = Path("data/input")
    data_output_dir: Path = Path("data/output")
    data_temp_dir: Path = Path("data/temp")

    # Clip defaults
    clip_max_duration: int = 60
    clip_aspect_ratio: str = "9:16"

    # Premiere Pro
    premiere_host: str = "localhost"
    premiere_port: int = 3000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    def ensure_dirs(self) -> None:
        for d in [self.data_input_dir, self.data_output_dir, self.data_temp_dir]:
            d.mkdir(parents=True, exist_ok=True)


settings = Settings()
