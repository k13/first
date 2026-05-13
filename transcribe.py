#!/usr/bin/env python3
"""
Video transcription tool using yt-dlp + OpenAI Whisper.
Usage: python3 transcribe.py <youtube_url> [--model small|medium|large]
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path


def download_audio(url: str, output_path: str) -> str:
    try:
        import yt_dlp
    except ImportError:
        print("Installing yt-dlp...")
        os.system(f"{sys.executable} -m pip install yt-dlp")
        import yt_dlp

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get("title", "video")
        return title


def transcribe_audio(audio_path: str, model_name: str = "medium") -> dict:
    try:
        import whisper
    except ImportError:
        print("Installing openai-whisper...")
        os.system(f"{sys.executable} -m pip install openai-whisper")
        import whisper

    print(f"Loading Whisper model '{model_name}'...")
    model = whisper.load_model(model_name)

    print("Transcribing...")
    result = model.transcribe(audio_path, verbose=True)
    return result


def format_timestamp(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def save_transcription(result: dict, title: str, output_dir: str = "."):
    safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title)[:80]
    base = Path(output_dir) / safe_title

    # Plain text
    txt_path = base.with_suffix(".txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(result["text"].strip())
    print(f"Saved: {txt_path}")

    # SRT subtitles
    srt_path = base.with_suffix(".srt")
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(result.get("segments", []), 1):
            f.write(f"{i}\n")
            f.write(f"{format_timestamp(seg['start'])} --> {format_timestamp(seg['end'])}\n")
            f.write(seg["text"].strip() + "\n\n")
    print(f"Saved: {srt_path}")

    return str(txt_path), str(srt_path)


def main():
    parser = argparse.ArgumentParser(description="Transcribe a YouTube video using Whisper")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument(
        "--model",
        default="medium",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: medium)",
    )
    parser.add_argument("--output-dir", default=".", help="Output directory (default: current dir)")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        audio_template = os.path.join(tmp, "audio.%(ext)s")
        print(f"Downloading audio from: {args.url}")
        title = download_audio(args.url, audio_template)

        audio_path = os.path.join(tmp, "audio.mp3")
        if not os.path.exists(audio_path):
            # find whatever was downloaded
            files = list(Path(tmp).glob("audio.*"))
            if not files:
                print("Error: audio download failed.")
                sys.exit(1)
            audio_path = str(files[0])

        result = transcribe_audio(audio_path, model_name=args.model)

    save_transcription(result, title, output_dir=args.output_dir)
    print("\nDone!")


if __name__ == "__main__":
    main()
