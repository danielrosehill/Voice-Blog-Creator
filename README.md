# Voice-Blog-Creator

Automated agent workflow to convert voice recordings into polished blog posts using Gemini AI.

## Overview

This project provides a complete pipeline to:
1. Preprocess raw audio files for optimal speech-to-text performance
2. Transcribe audio using Gemini 2.5 Flash with light redaction (removes filler words, adds paragraphs)
3. Generate formatted blog posts optimized for web presentation

## Workflow Steps

```
input/audio-file/{folder}/raw.mp3
    ↓ [Step 1: Preprocess]
output/{folder}/processed.mp3
    ↓ [Step 2: Transcribe]
output/{folder}/transcript.txt
    ↓ [Step 3: Generate Blog]
output/{folder}/blog_post.md
```

### Step 1: Audio Preprocessing
- Converts stereo to mono
- Removes silence while keeping natural pauses
- Reduces background noise
- Normalizes audio levels
- Applies dynamic range compression
- Optimizes for STT (16kHz sample rate)

### Step 2: Transcription (Gemini 2.5 Flash)
- Sends processed audio to Gemini API
- Light redaction:
  - Removes filler words (um, uh, like, you know, etc.)
  - Organizes into paragraphs based on topic changes
  - Adds proper spacing
  - Maintains original meaning and speaker's voice

### Step 3: Blog Post Generation (Gemini 2.5 Flash)
- Converts transcript to formatted blog post
- Creates compelling title
- Adds introduction and conclusion
- Organizes with subheadings (## and ###)
- Optimizes for web readability
- Uses proper markdown formatting

## Quick Start

### 1. Setup
```bash
./setup.sh
```

This will:
- Create virtual environment
- Install dependencies
- Create .env file template
- Set up directory structure

### 2. Configure API Key
Edit `.env` and add your Gemini API key:
```bash
GEMINI_API_KEY=your_api_key_here
```

### 3. Add Audio
Place your raw audio file:
```bash
input/audio-file/1/raw.mp3
```

### 4. Run Workflow
```bash
./run.sh 1
```

This will generate:
- `output/1/processed.mp3` - Preprocessed audio
- `output/1/transcript.txt` - Lightly redacted transcript
- `output/1/blog_post.md` - Formatted blog post

## Directory Structure

```
Voice-Blog-Creator/
├── input/                    # Input files
│   └── audio-file/
│       └── {folder}/
│           └── raw.mp3       # Your original audio
│
├── output/                   # Output files
│   └── {folder}/
│       ├── processed.mp3     # Preprocessed audio
│       ├── transcript.txt    # Lightly redacted transcript
│       └── blog_post.md      # Formatted blog post
│
├── scripts/                  # Processing scripts
│   ├── preprocess_audio.py
│   ├── gemini_transcribe.py
│   ├── gemini_blog_post.py
│   └── workflow.py           # Orchestration
│
├── setup.sh                  # Setup script
├── run.sh                    # Run workflow
├── requirements.txt          # Python dependencies
└── .env                      # API keys (not in git)
```

## Usage

### Complete Workflow
```bash
./run.sh 1                    # Process folder 1
./run.sh 1 --force            # Force regenerate all files
./run.sh 1 --verbose          # Show detailed processing
./run.sh 1 --steps 2 3        # Run only steps 2 and 3
```

### Individual Steps (Advanced)
```bash
# Step 1: Preprocess audio
.venv/bin/python scripts/preprocess_audio.py \
  --input input/audio-file/1/raw.mp3 \
  --output output/1/processed.mp3

# Step 2: Transcribe
.venv/bin/python scripts/gemini_transcribe.py \
  --input output/1/processed.mp3 \
  --output output/1/transcript.txt

# Step 3: Generate blog
.venv/bin/python scripts/gemini_blog_post.py \
  --input output/1/transcript.txt \
  --output output/1/blog_post.md
```

## Requirements

- Python 3.12+
- [UV](https://github.com/astral-sh/uv) package manager
- Gemini API key
- ffmpeg (for audio processing)

## Features

- **Clear Separation**: Input and output files are clearly separated
- **Smart Caching**: Skips steps if output already exists (use `--force` to override)
- **Flexible Pipeline**: Run individual steps or full workflow
- **Verbose Logging**: Debug with `-v` flag
- **Quality Optimization**: Each step optimized for its specific purpose

## API Costs

- Gemini 2.5 Flash is used for both transcription and blog generation
- Estimated cost: ~$0.01-0.05 per hour of audio (varies by length and complexity)

## Troubleshooting

### Virtual environment not found
Run `./setup.sh` to create the environment and install dependencies.

### API key errors
Make sure `.env` contains your valid Gemini API key:
```bash
GEMINI_API_KEY=your_actual_api_key_here
```

### Audio file not found
Ensure your audio file is placed at:
```
input/audio-file/{folder_number}/raw.mp3
```
