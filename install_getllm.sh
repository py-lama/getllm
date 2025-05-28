#!/bin/bash

# Script to properly install getllm package
# Handles common pip installation issues

set -e  # Exit on error

# Colors for better output
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${BLUE}Installing getllm package...${NC}"

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if running in a virtual environment
in_venv=0
if [ -n "$VIRTUAL_ENV" ]; then
    in_venv=1
    echo -e "${GREEN}Running in virtual environment: $VIRTUAL_ENV${NC}"
else
    echo -e "${YELLOW}Not running in a virtual environment.${NC}"
    
    # Check if we're in the getllm directory
    if [ -f "$SCRIPT_DIR/pyproject.toml" ] && [ -d "$SCRIPT_DIR/getllm" ]; then
        echo -e "${YELLOW}Installing from local directory...${NC}"
        
        # Create a virtual environment if it doesn't exist
        if [ ! -d "$SCRIPT_DIR/venv" ]; then
            echo -e "${BLUE}Creating virtual environment...${NC}"
            python -m venv "$SCRIPT_DIR/venv"
        fi
        
        # Activate the virtual environment
        echo -e "${BLUE}Activating virtual environment...${NC}"
        source "$SCRIPT_DIR/venv/bin/activate"
        in_venv=1
    fi
fi

# Function to install getllm
install_getllm() {
    local install_mode=$1
    local version=$2
    
    echo -e "${BLUE}Upgrading pip, setuptools, and wheel...${NC}"
    pip install --upgrade pip setuptools wheel
    
    if [ "$install_mode" == "local" ]; then
        echo -e "${BLUE}Installing getllm from local directory...${NC}"
        
        # Clean previous build artifacts
        if [ -d "$SCRIPT_DIR/build" ]; then
            rm -rf "$SCRIPT_DIR/build"
        fi
        if [ -d "$SCRIPT_DIR/dist" ]; then
            rm -rf "$SCRIPT_DIR/dist"
        fi
        if [ -d "$SCRIPT_DIR/getllm.egg-info" ]; then
            rm -rf "$SCRIPT_DIR/getllm.egg-info"
        fi
        
        # Install with pip in development mode
        pip install -e "$SCRIPT_DIR" --no-cache-dir
    else
        # Install from PyPI
        if [ -n "$version" ]; then
            echo -e "${BLUE}Installing getllm==$version from PyPI...${NC}"
            pip install --upgrade getllm==$version --no-cache-dir
        else
            echo -e "${BLUE}Installing latest getllm from PyPI...${NC}"
            pip install --upgrade getllm --no-cache-dir
        fi
    fi
}

# Determine installation mode
if [ -f "$SCRIPT_DIR/pyproject.toml" ] && [ -d "$SCRIPT_DIR/getllm" ]; then
    # We're in the getllm directory, install from local
    install_mode="local"
    
    # Get version from pyproject.toml
    version=$(grep -oP 'version = "\K[^"]+' "$SCRIPT_DIR/pyproject.toml")
    echo -e "${BLUE}Local getllm version: $version${NC}"
else
    # Install from PyPI
    install_mode="pypi"
    
    # Check if a specific version was requested
    if [ -n "$1" ]; then
        version=$1
    else
        version=""
    fi
fi

# Install getllm
install_getllm "$install_mode" "$version"

# Verify installation
echo -e "${BLUE}Verifying installation...${NC}"
installed_version=$(pip show getllm | grep -oP "Version: \K.*" || echo "not installed")

if [ "$installed_version" == "not installed" ]; then
    echo -e "${RED}Installation failed! getllm is not installed.${NC}"
    exit 1
else
    echo -e "${GREEN}getllm $installed_version successfully installed!${NC}"
fi

# Test the command
echo -e "${BLUE}Testing getllm command...${NC}"
if command -v getllm &> /dev/null; then
    getllm --version || echo -e "${YELLOW}getllm command exists but --version flag not supported${NC}"
else
    echo -e "${YELLOW}getllm command not found in PATH. You may need to:${NC}"
    echo "1. Add the installation directory to your PATH"
    echo "2. Create a symlink to the getllm command"
    echo "3. Restart your terminal session"
fi

# If we activated a venv, remind the user
if [ "$in_venv" -eq 1 ] && [ "$install_mode" == "local" ]; then
    echo -e "\n${YELLOW}Note: getllm is installed in a virtual environment.${NC}"
    echo -e "To use it, either:"
    echo -e "1. Activate the virtual environment with: ${BLUE}source $SCRIPT_DIR/venv/bin/activate${NC}"
    echo -e "2. Or use the full path: ${BLUE}$SCRIPT_DIR/venv/bin/getllm${NC}"
fi

echo -e "\n${GREEN}Installation process completed!${NC}"
