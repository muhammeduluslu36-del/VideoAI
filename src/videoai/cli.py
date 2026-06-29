from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import track

app = typer.Typer(name="videoai", help="AI-powered video processing toolkit")
console = Console()


@app.command()
def transcribe(
    video: Path = typer.Argument(..., help="Video or audio file to transcribe"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory"),
    fmt: str = typer.Option("srt", "--format", "-f", help="Output format: srt or vtt"),
    language: Optional[str] = typer.Option(None, "--language", "-l", help="Force language (e.g. tr, en)"),
) -> None:
    """Transcribe a video/audio file using Whisper."""
    from videoai.config import settings
    from videoai.transcription import WhisperTranscriber

    settings.ensure_dirs()
    console.print(f"[bold]Transcribing:[/bold] {video}")

    transcriber = WhisperTranscriber()
    result = transcriber.transcribe_and_save(video, output_dir=output, fmt=fmt)

    console.print(f"[green]Done:[/green] {result}")
    console.print(f"Language: {result}")


@app.command()
def clips(
    video: Path = typer.Argument(..., help="Source video file"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    max_clips: int = typer.Option(5, "--max-clips", "-n"),
    platform: str = typer.Option("tiktok", "--platform", "-p", help="tiktok / reels / youtube"),
) -> None:
    """Extract top highlight clips from a video using AI."""
    from videoai.config import settings
    from videoai.video.ffmpeg import FFmpegProcessor
    from videoai.transcription import WhisperTranscriber
    from videoai.analysis import ClaudeAnalyzer
    from videoai.video.clips import ClipGenerator

    settings.ensure_dirs()
    console.print(f"[bold]Processing:[/bold] {video}")

    ffmpeg = FFmpegProcessor()
    console.print("Extracting audio...")
    audio = ffmpeg.extract_audio(video)

    console.print("Transcribing...")
    transcriber = WhisperTranscriber()
    result = transcriber.transcribe(audio)
    

    # Build timestamped transcript for AI
    timestamped = "\n".join(
        f"[{s.start:.1f}s - {s.end:.1f}s] {s.text}" for s in result.segments
    )

    console.print("Finding highlights with Claude...")
    analyzer = ClaudeAnalyzer()
    highlights = analyzer.find_highlights(timestamped, max_clips=max_clips)

    timestamps = [
        {"start": h.start, "end": h.end, "title": h.title, "score": h.score}
        for h in highlights
    ]

    social = platform in ("tiktok", "reels")
    console.print(f"Generating {len(timestamps)} clips...")
    generator = ClipGenerator()
    paths = generator.from_highlights(video, timestamps, social_format=social, output_dir=output)

    for p in paths:
        console.print(f"[green]✓[/green] {p}")


@app.command()
def analyze(
    video: Path = typer.Argument(..., help="Video file to analyze"),
    provider: str = typer.Option("claude", "--provider", "-p", help="claude / chatgpt / ollama"),
) -> None:
    """Analyze video content using AI."""
    from videoai.config import settings
    from videoai.video.ffmpeg import FFmpegProcessor
    from videoai.transcription import WhisperTranscriber

    settings.ensure_dirs()
    ffmpeg = FFmpegProcessor()
    audio = ffmpeg.extract_audio(video)

    transcriber = WhisperTranscriber()
    result = transcriber.transcribe(audio)

    console.print(f"[red]PROVIDER = {provider}[/red]")

    if provider == "claude":
        from videoai.analysis import ClaudeAnalyzer
        analysis = ClaudeAnalyzer().analyze_transcript(result.full_text)
        console.print(f"[bold]Summary:[/bold] {analysis.summary}")
        console.print(f"[bold]Topics:[/bold] {', '.join(analysis.topics)}")
        console.print(f"[bold]Title:[/bold] {analysis.suggested_title}")
    elif provider == "chatgpt":
        from videoai.analysis import ChatGPTAnalyzer
        out = ChatGPTAnalyzer().analyze_transcript(result.full_text)
        console.print(out)
    else:
        from videoai.analysis import OllamaAnalyzer
        out = OllamaAnalyzer().analyze_transcript(result.full_text)
        console.print(out)


@app.command()
def serve() -> None:
    """Start the REST API server for the React frontend."""
    import uvicorn
    uvicorn.run("videoai.api.app:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    app()
