#!/bin/bash
# Test script for getllm commands
# This script tests various getllm commands in both normal and mock modes

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
  timeout 3 bash -c "$1" || echo -e "${YELLOW}Command timed out (expected for interactive commands)${NC}"
  echo ""
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

# Test basic commands
section "Basic Commands"
run_command "getllm --help"

# Test list command
section "List Models Command"
run_command "getllm list"

# Test default model command
section "Default Model Command"
run_command "getllm default"

# Test search commands (with timeout to avoid hanging)
section "Search Commands - Mock Mode"
run_command_timeout "getllm --mock --search bielik"

# Test interactive mode (with timeout to avoid hanging)
section "Interactive Mode - Mock Mode"
run_command_timeout "getllm --mock interactive"

section "Interactive Mode - Normal Mode"
run_command_timeout "getllm interactive"

# Test code generation with mock mode
section "Code Generation - Mock Mode"
run_command "getllm --mock code 'Write a function to calculate factorial'"

# Test code generation with normal mode (if Ollama is available)
section "Code Generation - Normal Mode"
run_command "getllm code 'Write a function to calculate factorial'"

# Test with different templates
section "Templates - Mock Mode"
run_command "getllm --mock code 'Write a function to validate user input' --template secure"

# Test saving code (with mock mode)
section "Save Code - Mock Mode"
run_command "getllm --mock code 'Write a hello world program' --save"

echo -e "\n${GREEN}All tests completed!${NC}"
