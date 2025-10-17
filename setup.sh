#!/usr/bin/env bash
#
# Voice Blog Creator - Setup Script
# Sets up the environment and installs dependencies
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Voice Blog Creator - Setup${NC}"
echo "================================"
echo

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check for UV
if ! command -v uv &> /dev/null; then
    echo -e "${RED}Error: uv is not installed${NC}"
    echo "Please install uv first: https://github.com/astral-sh/uv"
    exit 1
fi

echo -e "${YELLOW}Creating virtual environment...${NC}"
if [ ! -d ".venv" ]; then
    uv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

echo
echo -e "${YELLOW}Installing dependencies...${NC}"
uv pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

echo
echo -e "${YELLOW}Checking .env file...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    echo 'GEMINI_API_KEY="your_api_key_here"' > .env
    echo -e "${YELLOW}⚠ Please edit .env and add your Gemini API key${NC}"
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

echo
echo -e "${YELLOW}Creating directory structure...${NC}"
mkdir -p input/audio-file
mkdir -p output
mkdir -p scripts
echo -e "${GREEN}✓ Directories created${NC}"

echo
echo -e "${GREEN}Setup complete!${NC}"
echo
echo "Next steps:"
echo "1. Edit .env and add your GEMINI_API_KEY"
echo "2. Place audio files in input/audio-file/{folder_number}/raw.mp3"
echo "3. Run: ./run.sh 1"
echo
