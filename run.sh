#!/usr/bin/env bash
#
# Voice Blog Creator - Run Script
# Executes the complete workflow for a given folder
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if folder number is provided
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: No folder number provided${NC}"
    echo "Usage: $0 <folder_number> [options]"
    echo
    echo "Options:"
    echo "  --force, -f       Force overwrite existing files"
    echo "  --verbose, -v     Verbose output"
    echo "  --steps N...      Run specific steps (1=preprocess, 2=transcribe, 3=blog)"
    echo
    echo "Examples:"
    echo "  $0 1              # Process folder 1"
    echo "  $0 1 --force      # Force regenerate all outputs"
    echo "  $0 1 --steps 2 3  # Only transcribe and generate blog"
    exit 1
fi

# Check if .venv exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Running setup...${NC}"
    ./setup.sh
    echo
fi

# Activate virtual environment and run workflow
echo -e "${GREEN}Running Voice Blog Creator workflow...${NC}"
echo

.venv/bin/python scripts/workflow.py --folder "$@"
