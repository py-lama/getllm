#!/bin/bash

# Script to build and publish getllm package to PyPI
# Handles common issues with the build process

set -e  # Exit on error

# Colors for better output
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${BLUE}Building and publishing getllm to PyPI...${NC}"

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Ensure we have the latest build tools
echo -e "${BLUE}Upgrading build tools...${NC}"
pip install --upgrade pip build twine wheel setuptools

# Clean previous build artifacts
echo -e "${BLUE}Cleaning previous build artifacts...${NC}"
rm -rf build/ dist/ *.egg-info/

# Check if questionary is in dependencies
if ! grep -q "questionary" pyproject.toml; then
    echo -e "${YELLOW}Adding questionary to dependencies...${NC}"
    sed -i '/python-dotenv/a questionary = "^2.0.1"' pyproject.toml
fi

# Ensure version is consistent
VERSION=$(grep -oP 'version = "\K[^"]+' pyproject.toml)
echo -e "${BLUE}Current version in pyproject.toml: ${VERSION}${NC}"

SETUP_VERSION=$(grep -oP 'version="\K[^"]+' setup.py 2>/dev/null || echo "not found")
if [ "$SETUP_VERSION" != "not found" ] && [ "$SETUP_VERSION" != "$VERSION" ]; then
    echo -e "${YELLOW}Updating version in setup.py to match pyproject.toml...${NC}"
    sed -i "s/version=\"$SETUP_VERSION\"/version=\"$VERSION\"/" setup.py
    echo -e "${GREEN}Updated setup.py version to $VERSION${NC}"
fi

# Update version in __init__.py if it exists
INIT_FILE="getllm/__init__.py"
if [ -f "$INIT_FILE" ] && grep -q "__version__" "$INIT_FILE"; then
    echo -e "${YELLOW}Updating version in __init__.py...${NC}"
    sed -i "s/__version__ = '[^']*'/__version__ = '$VERSION'/" "$INIT_FILE"
    sed -i "s/__version__ = \"[^\"]*\"/__version__ = \"$VERSION\"/" "$INIT_FILE"
    echo -e "${GREEN}Updated __init__.py version to $VERSION${NC}"
fi

# Build the package using build module (PEP 517)
echo -e "${BLUE}Building the package...${NC}"
python -m build

# Check if the build was successful
if [ ! -d "dist" ] || [ -z "$(ls -A dist)" ]; then
    echo -e "${RED}Build failed! No distribution files found.${NC}"
    exit 1
fi

echo -e "${GREEN}Build successful!${NC}"
echo -e "Distribution files:"
ls -la dist/

# Ask for confirmation before uploading to PyPI
echo -e "${YELLOW}"
read -p "Do you want to upload to PyPI? (y/n) " -n 1 -r
echo -e "${NC}"
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Uploading to PyPI...${NC}"
    python -m twine upload dist/*
    echo -e "${GREEN}Package uploaded to PyPI!${NC}"
    echo -e "You can now install it with: pip install getllm==$VERSION --upgrade"
else
    echo -e "${YELLOW}Upload cancelled. You can upload manually with:${NC}"
    echo -e "python -m twine upload dist/*"
fi
