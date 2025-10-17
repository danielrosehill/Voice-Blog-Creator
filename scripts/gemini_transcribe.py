#!/usr/bin/env python3
"""
Gemini Audio Transcription Script
Sends processed audio to Gemini API for transcription with light redaction.
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
import time
import mimetypes

# Load environment variables
load_dotenv()


class GeminiTranscriber:
    """Handles audio transcription using Gemini API."""

    def __init__(self, api_key=None, verbose=False):
        self.verbose = verbose
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or .env file")

        # Configure Gemini
        genai.configure(api_key=self.api_key)

        # Use Gemini 2.5 Flash for multimodal audio transcription
        self.model = genai.GenerativeModel('gemini-2.5-flash')

        self.log("Gemini transcriber initialized (gemini-2.5-flash)")

    def log(self, message):
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(f"[INFO] {message}")

    def transcribe_audio(self, audio_path, output_path):
        """
        Transcribe audio file with light redaction using inline audio.

        Light redaction includes:
        - Removing filler words (um, uh, like, you know, etc.)
        - Adding proper paragraphs based on topic changes
        - Adding appropriate spacing
        - Maintaining the original content and meaning
        """
        self.log("="*60)
        self.log("Starting transcription with light redaction")
        self.log("="*60)

        # Check file size
        audio_path = Path(audio_path)
        file_size_mb = audio_path.stat().st_size / (1024 * 1024)
        self.log(f"Audio file size: {file_size_mb:.2f}MB")

        # Read audio file
        self.log(f"Reading audio file: {audio_path}")

        # Create prompt for light redaction
        prompt = """Generate a transcript of this audio with the following light redactions:

1. Remove common filler words (um, uh, like, you know, so, actually, basically, etc.)
2. Organize the content into clear paragraphs based on topic shifts
3. Add proper spacing between paragraphs
4. Maintain the original content, meaning, and speaker's voice
5. Do NOT change the actual words or meaning beyond removing fillers
6. Do NOT add content that wasn't spoken
7. Preserve the natural flow and conversational tone

Output only the transcribed text with no additional commentary or formatting markers."""

        self.log("Sending transcription request to Gemini...")

        # Read audio file as binary
        with open(audio_path, 'rb') as f:
            audio_data = f.read()

        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(str(audio_path))
        if not mime_type:
            mime_type = 'audio/mpeg'  # Default for MP3

        self.log(f"MIME type: {mime_type}")

        # Create audio part for inline sending
        audio_part = {
            "inline_data": {
                "mime_type": mime_type,
                "data": audio_data
            }
        }

        # Generate transcription with inline audio
        response = self.model.generate_content(
            [prompt, audio_part],
            request_options={"timeout": 600}  # 10 minute timeout for long audio
        )

        transcript = response.text.strip()

        self.log(f"Transcription complete ({len(transcript)} characters)")

        # Save transcript
        self.log(f"Saving transcript to {output_path}")
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(transcript, encoding='utf-8')

        self.log("="*60)
        self.log("Transcription saved successfully!")
        self.log("="*60)

        return transcript


def find_audio_folders(base_path="audio-file"):
    """Find all numbered folders containing processed.mp3 files."""
    base = Path(base_path)
    folders = []

    if not base.exists():
        print(f"Error: Directory '{base_path}' not found")
        return folders

    # Find numbered folders
    for item in sorted(base.iterdir(), key=lambda x: int(x.name) if x.name.isdigit() else float('inf')):
        if item.is_dir() and item.name.isdigit():
            processed_file = item / "processed.mp3"
            if processed_file.exists():
                folders.append(item)

    return folders


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe audio files using Gemini API with light redaction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --folder 1                   # Transcribe folder 1
  %(prog)s --folder 1 --force           # Overwrite existing transcript
  %(prog)s --all                        # Transcribe all folders
        """
    )

    parser.add_argument(
        '--input',
        type=str,
        help='Input audio file path'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Output transcript file path'
    )

    parser.add_argument(
        '--folder',
        type=str,
        help='Folder number to transcribe (e.g., 1, 2, 3) [deprecated]'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Transcribe all folders [deprecated]'
    )

    parser.add_argument(
        '--base-path',
        default='audio-file',
        help='Base path to audio folders (default: audio-file)'
    )

    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Verbose output'
    )

    parser.add_argument(
        '--force',
        '-f',
        action='store_true',
        help='Overwrite existing transcript files'
    )

    args = parser.parse_args()

    # New mode: direct input/output
    if args.input and args.output:
        # Initialize transcriber
        try:
            transcriber = GeminiTranscriber(verbose=args.verbose)
        except ValueError as e:
            print(f"Error: {e}")
            return 1

        # Transcribe audio
        try:
            transcriber.transcribe_audio(args.input, args.output)
            print(f"\n✓ Successfully transcribed {Path(args.input).name}")
            return 0
        except Exception as e:
            print(f"\n✗ Error transcribing: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            return 1

    # Legacy folder mode
    # Find available folders
    folders = find_audio_folders(args.base_path)

    if not folders:
        print(f"No folders with processed.mp3 files found in {args.base_path}/")
        print("Please run preprocess_audio.py first")
        return 1

    # Determine which folders to process
    folders_to_process = []

    if args.all:
        folders_to_process = folders
    elif args.folder:
        # Find folder by number
        folder_path = Path(args.base_path) / args.folder
        if folder_path in folders:
            folders_to_process = [folder_path]
        else:
            print(f"Error: Folder {args.folder} not found or doesn't contain processed.mp3")
            return 1
    else:
        print("Error: Please specify --folder NUMBER or --all")
        return 1

    # Initialize transcriber
    try:
        transcriber = GeminiTranscriber(verbose=args.verbose)
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    # Process selected folders
    for folder in folders_to_process:
        input_file = folder / "processed.mp3"
        output_file = folder / "transcript.txt"

        # Check if output exists
        if output_file.exists() and not args.force:
            print(f"\n{output_file} already exists. Skipping (use --force to overwrite)")
            continue

        print(f"\n{'='*60}")
        print(f"Transcribing folder: {folder.name}")
        print(f"{'='*60}")

        # Transcribe audio
        try:
            transcriber.transcribe_audio(input_file, output_file)
            print(f"\n✓ Successfully transcribed folder {folder.name}")
            print(f"  Transcript saved to: {output_file}")
        except Exception as e:
            print(f"\n✗ Error transcribing folder {folder.name}: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()

    return 0


if __name__ == "__main__":
    sys.exit(main())
