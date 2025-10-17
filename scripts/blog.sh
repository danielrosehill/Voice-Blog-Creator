#!/usr/bin/env bash
# Wrapper for blog generation step

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

"$PROJECT_ROOT/.venv/bin/python" "$SCRIPT_DIR/gemini_blog_post.py" "$@"
