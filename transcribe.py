#!/usr/bin/env python3
"""
YouTube video transcription using yt-dlp + OpenAI Whisper.

Quick start:
    pip install yt-dlp openai-whisper
    # macOS:  brew install ffmpeg
    # Ubuntu: sudo apt install ffmpeg
    python3 transcribe.py "https://youtu.be/6WEsPzHyD9k"

If yt-dlp fails (bot detection), try adding your browser cookies:
    python3 transcribe.py URL --cookies-from-browser chrome
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path


def download_audio(url: str, output_path: str, cookies_from_browser: str | None = None) -> str:
    try:
        import yt_dlp
    except ImportError:
        sys.exit("Install yt-dlp first:  pip install yt-dlp")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": False,
        "no_warnings": False,
    }
    if cookies_from_browser:
        ydl_opts["cookiesfrombrowser"] = (cookies_from_browser,)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return info.get("title", "video")


def transcribe_audio(audio_path: str, model_name: str = "medium", language: str | None = None) -> dict:
    try:
        import whisper
    except ImportError:
        sys.exit("Install whisper first:  pip install openai-whisper")

    print(f"Loading Whisper model '{model_name}'…")
    model = whisper.load_model(model_name)
    print("Transcribing…")
    kwargs = {"verbose": True}
    if language:
        kwargs["language"] = language
    return model.transcribe(audio_path, **kwargs)


def _ts(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def save(result: dict, title: str, output_dir: str = ".") -> tuple[str, str]:
    safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in title)[:80].strip()
    base = Path(output_dir) / safe

    txt_path = str(base.with_suffix(".txt"))
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(result["text"].strip())
    print(f"Saved: {txt_path}")

    srt_path = str(base.with_suffix(".srt"))
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(result.get("segments", []), 1):
            f.write(f"{i}\n{_ts(seg['start'])} --> {_ts(seg['end'])}\n{seg['text'].strip()}\n\n")
    print(f"Saved: {srt_path}")

    return txt_path, srt_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Transcribe a YouTube video with Whisper")
    parser.add_argument("url", help="YouTube URL")
    parser.add_argument("--model", default="medium",
                        choices=["tiny", "base", "small", "medium", "large"],
                        help="Whisper model size (default: medium)")
    parser.add_argument("--language", default=None,
                        help="Force language (e.g. 'ru'). Auto-detected if omitted.")
    parser.add_argument("--cookies-from-browser", metavar="BROWSER",
                        help="Pass cookies from browser (chrome, firefox, safari, …)")
    parser.add_argument("--output-dir", default=".", help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        audio_tmpl = os.path.join(tmp, "audio.%(ext)s")
        print(f"Downloading: {args.url}")
        title = download_audio(args.url, audio_tmpl, args.cookies_from_browser)

        audio_path = os.path.join(tmp, "audio.mp3")
        if not os.path.exists(audio_path):
            files = list(Path(tmp).glob("audio.*"))
            if not files:
                sys.exit("Audio download failed.")
            audio_path = str(files[0])

        result = transcribe_audio(audio_path, model_name=args.model, language=args.language)

    save(result, title, output_dir=args.output_dir)
    print("Done!")


if __name__ == "__main__":
    main()
