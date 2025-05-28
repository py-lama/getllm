#!/bin/bash
# Test script for getllm model installation with different Ollama options
# This script tests the model installation process with various Ollama installation methods

# Set up colors for better readability
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Function to print section headers
section() {
  echo -e "\n${BLUE}==== $1 ====${NC}"
}

# Function to run a command and print its output
run_command() {
  echo -e "${YELLOW}$ $1${NC}"
  eval "$1"
  local status=$?
  if [ $status -eq 0 ]; then
    echo -e "${GREEN}Command succeeded (exit code: $status)${NC}"
  else
    echo -e "${RED}Command failed (exit code: $status)${NC}"
  fi
  echo ""
}

# Function to run a command with a timeout to avoid hanging
run_command_timeout() {
  echo -e "${YELLOW}$ $1${NC}"
  timeout 10 bash -c "$1" || echo -e "${YELLOW}Command timed out (expected for interactive commands)${NC}"
  echo ""
  # Sleep briefly to allow processes to clean up
  sleep 1
}

# Activate the virtual environment if it exists
if [ -d "venv" ]; then
  source venv/bin/activate
  echo -e "${GREEN}Activated virtual environment${NC}"
else
  echo -e "${RED}No virtual environment found, using system Python${NC}"
fi

# Make sure we're using the local getllm
which getllm
echo ""

# Test the model installation process with mock mode
section "Model Installation - Mock Mode"
run_command_timeout "echo 'tinyllama:1.1b\nYes' | getllm --mock install"

# Test listing installed models with mock mode
section "List Installed Models - Mock Mode"
run_command "getllm --mock installed"

# Test setting default model with mock mode
section "Set Default Model - Mock Mode"
run_command_timeout "echo 'tinyllama:1.1b' | getllm --mock set-default"

# Test model search with mock mode
section "Model Search - Mock Mode"
run_command_timeout "echo 'Cancel' | getllm --mock --search bielik"

# Test model search with mock mode and selecting a model
section "Model Search and Selection - Mock Mode"
run_command_timeout "echo '1\nYes' | getllm --mock --search bielik"

# Test code generation with a specific model in mock mode
section "Code Generation with Specific Model - Mock Mode"
run_command "getllm --mock -m tinyllama:1.1b code 'Write a function to calculate factorial'"

# Test updating the model list
section "Update Models List - Mock Mode"
run_command "getllm --mock update"

# Test the test command
section "Test Default Model - Mock Mode"
run_command "getllm --mock test"

echo -e "\n${GREEN}All model installation tests completed!${NC}"
