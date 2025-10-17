#!/usr/bin/env python3
"""
Gemini Blog Post Generator
Converts transcripts into formatted blog posts optimized for web presentation.
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()


class GeminiBlogGenerator:
    """Handles blog post generation from transcripts using Gemini API."""

    def __init__(self, api_key=None, verbose=False):
        self.verbose = verbose
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or .env file")

        # Configure Gemini
        genai.configure(api_key=self.api_key)

        # Use Gemini 2.5 Flash for text generation
        self.model = genai.GenerativeModel('gemini-2.5-flash')

        self.log("Gemini blog generator initialized")

    def log(self, message):
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(f"[INFO] {message}")

    def generate_blog_post(self, transcript_path, output_path):
        """
        Generate a formatted blog post from a transcript.

        The blog post will include:
        - Compelling title
        - Introduction
        - Well-structured sections with subheadings
        - Optimized for web readability
        - Proper markdown formatting
        """
        self.log("="*60)
        self.log("Starting blog post generation")
        self.log("="*60)

        # Read transcript
        transcript_path = Path(transcript_path)
        if not transcript_path.exists():
            raise FileNotFoundError(f"Transcript not found: {transcript_path}")

        transcript = transcript_path.read_text(encoding='utf-8')
        self.log(f"Loaded transcript ({len(transcript)} characters)")

        # Create prompt for blog post generation
        prompt = """You are a professional blog writer. Convert the following transcript into a well-formatted, engaging blog post.

Requirements:
1. Create a compelling, SEO-friendly title
2. Write a brief, engaging introduction that hooks the reader
3. Organize the content into logical sections with clear subheadings (using ## for main sections, ### for subsections)
4. Ensure smooth transitions between sections
5. Add a conclusion that summarizes key points
6. Use proper markdown formatting:
   - Use **bold** for emphasis on important points
   - Use bullet points (-) for lists where appropriate
   - Use > blockquotes for notable quotes or key insights
   - Use code blocks (```) if technical content is discussed
7. Maintain the original meaning and insights from the transcript
8. Optimize for web readability (shorter paragraphs, clear structure)
9. Keep the author's voice and tone

Do NOT add:
- Meta descriptions or SEO tags
- Publishing dates or author bios
- Links or references not in the original content
- Content not present in the transcript

Output the blog post in markdown format, starting with the title as an H1 (#).

Here's the transcript:

---

""" + transcript

        self.log("Sending blog post generation request to Gemini...")

        # Generate blog post
        response = self.model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.7,  # Slightly creative but focused
                top_p=0.9,
                top_k=40,
                max_output_tokens=8192,
            )
        )

        blog_post = response.text.strip()

        self.log(f"Blog post generated ({len(blog_post)} characters)")

        # Save blog post
        self.log(f"Saving blog post to {output_path}")
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(blog_post, encoding='utf-8')

        self.log("="*60)
        self.log("Blog post saved successfully!")
        self.log("="*60)

        return blog_post


def find_transcript_folders(base_path="audio-file"):
    """Find all numbered folders containing transcript.txt files."""
    base = Path(base_path)
    folders = []

    if not base.exists():
        print(f"Error: Directory '{base_path}' not found")
        return folders

    # Find numbered folders
    for item in sorted(base.iterdir(), key=lambda x: int(x.name) if x.name.isdigit() else float('inf')):
        if item.is_dir() and item.name.isdigit():
            transcript_file = item / "transcript.txt"
            if transcript_file.exists():
                folders.append(item)

    return folders


def main():
    parser = argparse.ArgumentParser(
        description="Generate blog posts from transcripts using Gemini API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --folder 1                   # Generate blog post for folder 1
  %(prog)s --folder 1 --force           # Overwrite existing blog post
  %(prog)s --all                        # Generate blog posts for all folders
        """
    )

    parser.add_argument(
        '--input',
        type=str,
        help='Input transcript file path'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Output blog post file path'
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
        help='Overwrite existing blog post files'
    )

    args = parser.parse_args()

    # New mode: direct input/output
    if args.input and args.output:
        # Initialize blog generator
        try:
            generator = GeminiBlogGenerator(verbose=args.verbose)
        except ValueError as e:
            print(f"Error: {e}")
            return 1

        # Generate blog post
        try:
            generator.generate_blog_post(args.input, args.output)
            print(f"\n✓ Successfully generated blog post from {Path(args.input).name}")
            return 0
        except Exception as e:
            print(f"\n✗ Error generating blog post: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            return 1

    # Legacy folder mode
    # Find available folders
    folders = find_transcript_folders(args.base_path)

    if not folders:
        print(f"No folders with transcript.txt files found in {args.base_path}/")
        print("Please run gemini_transcribe.py first")
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
            print(f"Error: Folder {args.folder} not found or doesn't contain transcript.txt")
            return 1
    else:
        print("Error: Please specify --folder NUMBER or --all")
        return 1

    # Initialize blog generator
    try:
        generator = GeminiBlogGenerator(verbose=args.verbose)
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    # Process selected folders
    for folder in folders_to_process:
        input_file = folder / "transcript.txt"
        output_file = folder / "blog_post.md"

        # Check if output exists
        if output_file.exists() and not args.force:
            print(f"\n{output_file} already exists. Skipping (use --force to overwrite)")
            continue

        print(f"\n{'='*60}")
        print(f"Generating blog post for folder: {folder.name}")
        print(f"{'='*60}")

        # Generate blog post
        try:
            generator.generate_blog_post(input_file, output_file)
            print(f"\n✓ Successfully generated blog post for folder {folder.name}")
            print(f"  Blog post saved to: {output_file}")
        except Exception as e:
            print(f"\n✗ Error generating blog post for folder {folder.name}: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()

    return 0


if __name__ == "__main__":
    sys.exit(main())
