#!/usr/bin/env python3
"""
Audio Preprocessing Script for STT Optimization
Processes raw.mp3 files in numbered folders and outputs processed.mp3
with improvements for speech-to-text performance.
"""

import os
import sys
import argparse
from pathlib import Path
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range
from pydub.silence import detect_nonsilent
import noisereduce as nr
import numpy as np


class AudioPreprocessor:
    """Handles audio preprocessing for improved STT performance."""

    def __init__(self, input_path, output_path, verbose=False):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.verbose = verbose

    def log(self, message):
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(f"[INFO] {message}")

    def load_audio(self):
        """Load audio file."""
        self.log(f"Loading audio from {self.input_path}")
        audio = AudioSegment.from_file(str(self.input_path))
        self.log(f"Audio loaded: {len(audio)}ms, {audio.channels} channels, {audio.frame_rate}Hz")
        return audio

    def convert_to_mono(self, audio):
        """Convert stereo to mono."""
        if audio.channels > 1:
            self.log("Converting stereo to mono")
            return audio.set_channels(1)
        self.log("Audio is already mono")
        return audio

    def remove_silence(self, audio, silence_thresh=-40, min_silence_len=500, padding=300):
        """Remove silence from audio while keeping natural pauses."""
        self.log(f"Removing silence (threshold: {silence_thresh}dB, min_len: {min_silence_len}ms)")

        # Detect non-silent chunks
        nonsilent_ranges = detect_nonsilent(
            audio,
            min_silence_len=min_silence_len,
            silence_thresh=silence_thresh
        )

        if not nonsilent_ranges:
            self.log("Warning: No non-silent audio detected, returning original")
            return audio

        # Combine non-silent chunks with padding
        output = AudioSegment.empty()
        for start, end in nonsilent_ranges:
            # Add padding around speech
            start = max(0, start - padding)
            end = min(len(audio), end + padding)
            output += audio[start:end]

        removed_ms = len(audio) - len(output)
        self.log(f"Removed {removed_ms}ms of silence ({removed_ms/len(audio)*100:.1f}%)")
        return output

    def reduce_noise(self, audio):
        """Reduce background noise using spectral gating."""
        self.log("Reducing background noise")

        # Convert to numpy array
        samples = np.array(audio.get_array_of_samples())

        # Apply noise reduction
        reduced = nr.reduce_noise(
            y=samples,
            sr=audio.frame_rate,
            stationary=True,
            prop_decrease=0.8
        )

        # Convert back to AudioSegment
        reduced_audio = AudioSegment(
            reduced.tobytes(),
            frame_rate=audio.frame_rate,
            sample_width=audio.sample_width,
            channels=audio.channels
        )

        self.log("Noise reduction complete")
        return reduced_audio

    def normalize_audio(self, audio, target_dBFS=-20.0):
        """Normalize audio levels."""
        self.log(f"Normalizing audio (target: {target_dBFS}dBFS)")

        # Apply normalization
        normalized = normalize(audio)

        # Adjust to target level
        change_in_dBFS = target_dBFS - normalized.dBFS
        normalized = normalized.apply_gain(change_in_dBFS)

        self.log(f"Normalized to {normalized.dBFS:.1f}dBFS")
        return normalized

    def apply_compression(self, audio):
        """Apply dynamic range compression for consistent voice levels."""
        self.log("Applying dynamic range compression")
        compressed = compress_dynamic_range(audio, threshold=-20.0, ratio=4.0, attack=5.0, release=50.0)
        return compressed

    def optimize_for_stt(self, audio):
        """Apply STT-specific optimizations."""
        self.log("Applying STT optimizations")

        # Set sample rate to 16kHz (optimal for most STT engines)
        if audio.frame_rate != 16000:
            self.log(f"Resampling from {audio.frame_rate}Hz to 16000Hz")
            audio = audio.set_frame_rate(16000)

        return audio

    def process(self, steps=None):
        """
        Process audio file with specified steps.

        Args:
            steps: List of processing steps. If None, all steps are applied.
                   Available: ['mono', 'silence', 'noise', 'normalize', 'compress', 'optimize']
        """
        if steps is None:
            steps = ['mono', 'silence', 'noise', 'normalize', 'compress', 'optimize']

        self.log("="*60)
        self.log("Starting audio preprocessing")
        self.log("="*60)

        # Load audio
        audio = self.load_audio()

        # Apply processing steps
        if 'mono' in steps:
            audio = self.convert_to_mono(audio)

        if 'silence' in steps:
            audio = self.remove_silence(audio)

        if 'noise' in steps:
            audio = self.reduce_noise(audio)

        if 'normalize' in steps:
            audio = self.normalize_audio(audio)

        if 'compress' in steps:
            audio = self.apply_compression(audio)

        if 'optimize' in steps:
            audio = self.optimize_for_stt(audio)

        # Save processed audio
        self.log(f"Saving processed audio to {self.output_path}")
        audio.export(str(self.output_path), format="mp3", bitrate="128k")

        self.log("="*60)
        self.log("Processing complete!")
        self.log(f"Output: {self.output_path}")
        self.log("="*60)


def find_audio_folders(base_path="audio-file"):
    """Find all numbered folders containing raw.mp3 files."""
    base = Path(base_path)
    folders = []

    if not base.exists():
        print(f"Error: Directory '{base_path}' not found")
        return folders

    # Find numbered folders
    for item in sorted(base.iterdir(), key=lambda x: int(x.name) if x.name.isdigit() else float('inf')):
        if item.is_dir() and item.name.isdigit():
            raw_file = item / "raw.mp3"
            if raw_file.exists():
                folders.append(item)

    return folders


def select_folder_interactive(folders):
    """Interactive folder selection."""
    if not folders:
        print("No folders with raw.mp3 files found in audio-file/")
        return None

    print("\nAvailable audio folders:")
    print("-" * 40)
    for idx, folder in enumerate(folders, 1):
        raw_file = folder / "raw.mp3"
        size_mb = raw_file.stat().st_size / (1024 * 1024)
        print(f"{idx}. Folder {folder.name} (raw.mp3: {size_mb:.2f}MB)")
    print("-" * 40)

    while True:
        try:
            choice = input(f"\nSelect folder (1-{len(folders)}) or 'q' to quit: ").strip()
            if choice.lower() == 'q':
                return None

            idx = int(choice) - 1
            if 0 <= idx < len(folders):
                return folders[idx]
            else:
                print(f"Please enter a number between 1 and {len(folders)}")
        except (ValueError, KeyboardInterrupt):
            print("\nCancelled")
            return None


def main():
    parser = argparse.ArgumentParser(
        description="Preprocess audio files for improved STT performance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Processing steps:
  mono      - Convert stereo to mono
  silence   - Remove silence while keeping natural pauses
  noise     - Remove background noise
  normalize - Normalize audio levels
  compress  - Apply dynamic range compression
  optimize  - Optimize for STT (16kHz sample rate)

Examples:
  %(prog)s                          # Interactive mode
  %(prog)s --folder 1               # Process folder 1
  %(prog)s --all                    # Process all folders
  %(prog)s --folder 1 --steps mono noise normalize
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
        help='Output audio file path'
    )

    parser.add_argument(
        '--folder',
        type=str,
        help='Folder number to process (e.g., 1, 2, 3) [deprecated]'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Process all folders [deprecated]'
    )

    parser.add_argument(
        '--steps',
        nargs='+',
        choices=['mono', 'silence', 'noise', 'normalize', 'compress', 'optimize'],
        help='Processing steps to apply (default: all)'
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
        help='Overwrite existing processed.mp3 files'
    )

    args = parser.parse_args()

    # New mode: direct input/output
    if args.input and args.output:
        input_file = Path(args.input)
        output_file = Path(args.output)

        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Process audio
        preprocessor = AudioPreprocessor(input_file, output_file, verbose=args.verbose)
        try:
            preprocessor.process(steps=args.steps)
            print(f"\n✓ Successfully processed {input_file.name}")
            return 0
        except Exception as e:
            print(f"\n✗ Error processing {input_file.name}: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            return 1

    # Legacy folder mode
    # Find available folders
    folders = find_audio_folders(args.base_path)

    if not folders:
        print(f"No folders with raw.mp3 files found in {args.base_path}/")
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
            print(f"Error: Folder {args.folder} not found or doesn't contain raw.mp3")
            return 1
    else:
        # Interactive mode
        selected = select_folder_interactive(folders)
        if selected:
            folders_to_process = [selected]
        else:
            return 0

    # Process selected folders
    for folder in folders_to_process:
        input_file = folder / "raw.mp3"
        output_file = folder / "processed.mp3"

        # Check if output exists
        if output_file.exists() and not args.force:
            response = input(f"\n{output_file} already exists. Overwrite? (y/n): ").strip().lower()
            if response != 'y':
                print(f"Skipping folder {folder.name}")
                continue

        print(f"\n{'='*60}")
        print(f"Processing folder: {folder.name}")
        print(f"{'='*60}")

        # Process audio
        preprocessor = AudioPreprocessor(input_file, output_file, verbose=args.verbose)
        try:
            preprocessor.process(steps=args.steps)
            print(f"\n✓ Successfully processed folder {folder.name}")
        except Exception as e:
            print(f"\n✗ Error processing folder {folder.name}: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()

    return 0


if __name__ == "__main__":
    sys.exit(main())
