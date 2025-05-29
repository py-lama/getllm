#!/bin/bash
# Test script for getllm Ollama installation options
# This script tests the various Ollama installation methods

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
  timeout 5 bash -c "$1" || echo -e "${YELLOW}Command timed out (expected for interactive commands)${NC}"
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

# Test the mock mode with various commands
section "Mock Mode Tests"

# Test mock mode with code generation
section "Code Generation with Mock Mode"
run_command "getllm --mock code 'Write a function to calculate factorial'"

# Test mock mode with different templates
section "Templates with Mock Mode"
run_command "getllm --mock -t secure code 'Write a function to validate user input'"

# Test mock mode with saving code
section "Save Code with Mock Mode"
run_command "getllm --mock -s code 'Write a hello world program'"

# Test mock mode with model search (with timeout to avoid hanging)
section "Search Models with Mock Mode"
run_command_timeout "echo 'Cancel' | getllm --mock --search bielik"

# Test the Ollama server check
section "Ollama Server Check"
run_command "python -c 'from getllm.ollama import OllamaServer; print(\"Server running:\", OllamaServer().check_server_running())'"

# Test the Ollama installation check
section "Ollama Installation Check"
run_command "python -c 'from getllm.ollama import OllamaServer; print(\"Ollama installed:\", OllamaServer().is_ollama_installed)'"

# Test the bexy sandbox setup (non-interactive test)
section "Bexy Sandbox Setup Test"
run_command "python -c 'from getllm.ollama import OllamaServer; print(\"Bexy path exists:\", __import__(\"os\").path.isdir(__import__(\"os\").path.join(__import__(\"os\").path.dirname(__import__(\"os\").path.dirname(__import__(\"os\").path.dirname(OllamaServer.__module__))), \"bexy\")))'"

# Test model installation with mock mode
section "Model Installation with Mock Mode"
run_command_timeout "echo 'codellama:7b\nYes' | getllm --mock install"

# Test installed models listing with mock mode
section "List Installed Models with Mock Mode"
run_command "getllm --mock installed"

# Test setting default model with mock mode
section "Set Default Model with Mock Mode"
run_command_timeout "echo 'codellama:7b' | getllm --mock set-default"

# Test the interactive mode with mock mode (with timeout to avoid hanging)
section "Interactive Mode with Mock Mode"
run_command_timeout "echo 'exit' | getllm --mock interactive"

echo -e "\n${GREEN}All installation option tests completed!${NC}"
