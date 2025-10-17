#!/usr/bin/env python3
"""
Voice Blog Creator - Complete Workflow Orchestration
Orchestrates the complete pipeline from audio to blog post.

Directory Structure:
- input/audio-file/{folder}/raw.mp3          # Input audio files
- output/{folder}/processed.mp3              # Processed audio
- output/{folder}/transcript.txt             # Transcript
- output/{folder}/blog_post.md               # Blog post
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# Add parent directory to path to find other scripts
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))


def get_python_executable():
    """Get the correct Python executable (prefers virtual environment)."""
    venv_paths = [
        PROJECT_ROOT / ".venv/bin/python",
        PROJECT_ROOT / "venv/bin/python",
    ]

    for venv_python in venv_paths:
        if venv_python.exists():
            return str(venv_python)

    return sys.executable


class WorkflowOrchestrator:
    """Orchestrates the complete voice-to-blog workflow."""

    def __init__(self, folder_number, verbose=False, force=False):
        self.folder_number = folder_number
        self.verbose = verbose
        self.force = force

        # Get Python executable
        self.python = get_python_executable()

        # Directory paths
        self.input_dir = PROJECT_ROOT / "input" / "audio-file" / folder_number
        self.output_dir = PROJECT_ROOT / "output" / folder_number

        # File paths
        self.raw_audio = self.input_dir / "raw.mp3"
        self.processed_audio = self.output_dir / "processed.mp3"
        self.transcript = self.output_dir / "transcript.txt"
        self.blog_post = self.output_dir / "blog_post.md"

        # Validate input folder exists
        if not self.input_dir.exists():
            raise ValueError(f"Input folder not found: {self.input_dir}")

        if not self.raw_audio.exists():
            raise ValueError(f"Raw audio not found: {self.raw_audio}")

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def log(self, message, level="INFO"):
        """Print formatted log message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = f"[{timestamp}] [{level}]"
        print(f"{prefix} {message}")

    def run_command(self, command, description):
        """Run a command and handle output."""
        self.log(f"Running: {description}")

        # Change to scripts directory for execution
        if self.verbose:
            result = subprocess.run(command, shell=False, cwd=SCRIPT_DIR)
        else:
            result = subprocess.run(
                command,
                shell=False,
                capture_output=True,
                text=True,
                cwd=SCRIPT_DIR
            )

        if result.returncode != 0:
            self.log(f"Failed: {description}", level="ERROR")
            if not self.verbose and result.stderr:
                print(result.stderr)
            return False

        self.log(f"Completed: {description}", level="SUCCESS")
        return True

    def check_file_exists(self, file_path, step_name):
        """Check if a file exists and handle force flag."""
        if file_path.exists():
            if self.force:
                self.log(f"File exists but --force is set, will overwrite: {file_path}")
                return False
            else:
                self.log(f"File exists, skipping {step_name}: {file_path}")
                return True
        return False

    def step_1_preprocess_audio(self):
        """Step 1: Preprocess audio (input/raw.mp3 -> output/processed.mp3)."""
        self.log("="*70)
        self.log("STEP 1: Audio Preprocessing")
        self.log("="*70)

        if self.check_file_exists(self.processed_audio, "audio preprocessing"):
            return True

        command = [
            self.python,
            "preprocess_audio.py",
            "--input", str(self.raw_audio),
            "--output", str(self.processed_audio)
        ]

        if self.verbose:
            command.append("--verbose")

        return self.run_command(command, "Audio preprocessing")

    def step_2_transcribe(self):
        """Step 2: Transcribe audio (output/processed.mp3 -> output/transcript.txt)."""
        self.log("="*70)
        self.log("STEP 2: Audio Transcription")
        self.log("="*70)

        if not self.processed_audio.exists():
            self.log(f"Processed audio not found: {self.processed_audio}", level="ERROR")
            self.log("Please run Step 1 first", level="ERROR")
            return False

        if self.check_file_exists(self.transcript, "transcription"):
            return True

        command = [
            self.python,
            "gemini_transcribe.py",
            "--input", str(self.processed_audio),
            "--output", str(self.transcript)
        ]

        if self.verbose:
            command.append("--verbose")

        return self.run_command(command, "Audio transcription")

    def step_3_generate_blog(self):
        """Step 3: Generate blog post (output/transcript.txt -> output/blog_post.md)."""
        self.log("="*70)
        self.log("STEP 3: Blog Post Generation")
        self.log("="*70)

        if not self.transcript.exists():
            self.log(f"Transcript not found: {self.transcript}", level="ERROR")
            self.log("Please run Step 2 first", level="ERROR")
            return False

        if self.check_file_exists(self.blog_post, "blog post generation"):
            return True

        command = [
            self.python,
            "gemini_blog_post.py",
            "--input", str(self.transcript),
            "--output", str(self.blog_post)
        ]

        if self.verbose:
            command.append("--verbose")

        return self.run_command(command, "Blog post generation")

    def run_workflow(self, steps=None):
        """Run the complete workflow or specific steps."""
        if steps is None or 'all' in steps:
            steps = [1, 2, 3]

        self.log("")
        self.log("="*70)
        self.log("VOICE BLOG CREATOR - WORKFLOW ORCHESTRATOR")
        self.log("="*70)
        self.log(f"Folder: {self.folder_number}")
        self.log(f"Input: {self.input_dir}")
        self.log(f"Output: {self.output_dir}")
        self.log(f"Steps to run: {', '.join(map(str, steps))}")
        self.log(f"Force overwrite: {self.force}")
        self.log(f"Verbose: {self.verbose}")
        self.log("="*70)
        self.log("")

        results = {}

        # Step 1: Audio Preprocessing
        if 1 in steps:
            results[1] = self.step_1_preprocess_audio()
            if not results[1]:
                self.log("Workflow stopped due to error in Step 1", level="ERROR")
                return False

        # Step 2: Transcription
        if 2 in steps:
            results[2] = self.step_2_transcribe()
            if not results[2]:
                self.log("Workflow stopped due to error in Step 2", level="ERROR")
                return False

        # Step 3: Blog Post Generation
        if 3 in steps:
            results[3] = self.step_3_generate_blog()
            if not results[3]:
                self.log("Workflow stopped due to error in Step 3", level="ERROR")
                return False

        # Summary
        self.log("")
        self.log("="*70)
        self.log("WORKFLOW COMPLETE")
        self.log("="*70)
        self.log("Generated files:")

        if self.processed_audio.exists():
            self.log(f"  ✓ Processed audio: {self.processed_audio}")

        if self.transcript.exists():
            self.log(f"  ✓ Transcript: {self.transcript}")

        if self.blog_post.exists():
            self.log(f"  ✓ Blog post: {self.blog_post}")

        self.log("="*70)

        return True


def main():
    parser = argparse.ArgumentParser(
        description="Voice Blog Creator - Complete workflow orchestration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Workflow Steps:
  1. Audio Preprocessing   - Process raw.mp3 to create processed.mp3
  2. Transcription        - Transcribe processed.mp3 to transcript.txt
  3. Blog Generation      - Convert transcript.txt to blog_post.md

Directory Structure:
  input/audio-file/{folder}/raw.mp3     # Your input audio
  output/{folder}/processed.mp3         # Preprocessed audio
  output/{folder}/transcript.txt        # Lightly redacted transcript
  output/{folder}/blog_post.md          # Formatted blog post

Examples:
  %(prog)s --folder 1                      # Run all steps for folder 1
  %(prog)s --folder 1 --steps 2 3          # Run only transcription and blog generation
  %(prog)s --folder 1 --force              # Force regenerate all files
  %(prog)s --folder 1 --steps 3 --force    # Force regenerate only blog post

Typical usage:
  1. Place raw.mp3 in input/audio-file/1/
  2. Run: %(prog)s --folder 1
  3. Find outputs in output/1/
        """
    )

    parser.add_argument(
        '--folder',
        type=str,
        required=True,
        help='Folder number to process (required)'
    )

    parser.add_argument(
        '--steps',
        type=int,
        nargs='+',
        choices=[1, 2, 3],
        help='Specific steps to run (1=preprocess, 2=transcribe, 3=blog). If omitted, runs all steps.'
    )

    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Verbose output from all steps'
    )

    parser.add_argument(
        '--force',
        '-f',
        action='store_true',
        help='Force overwrite existing files'
    )

    args = parser.parse_args()

    # Create orchestrator
    try:
        orchestrator = WorkflowOrchestrator(
            folder_number=args.folder,
            verbose=args.verbose,
            force=args.force
        )
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    # Run workflow
    try:
        success = orchestrator.run_workflow(steps=args.steps)
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\nWorkflow interrupted by user")
        return 1
    except Exception as e:
        print(f"\nError: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
