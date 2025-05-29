#!/bin/bash

# Test script to verify all getllm CLI commands
# Exit on error
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to run a test command
run_test() {
    local test_name="$1"
    local cmd="$2"
    local expected_exit_code=${3:-0}  # Default to expecting success (0)
    
    echo -e "\n${GREEN}TESTING:${NC} $test_name"
    echo "Command: $cmd"
    
    # Run the command and capture output and exit code
    output=$($cmd 2>&1)
    exit_code=$?
    
    # Check if the command succeeded or failed as expected
    if [ $exit_code -eq $expected_exit_code ]; then
        echo -e "${GREEN}✓ PASSED${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (Expected exit code: $expected_exit_code, Got: $exit_code)"
        echo "Output:"
        echo "$output"
        return 1
    fi
}

# Test each command
run_test "Basic code generation" "python -m getllm --mock code 'print hello world'"
run_test "Code with template" "python -m getllm --mock code 'sort a list of numbers' -t basic"
run_test "Code with dependencies" "python -m getllm --mock code 'web scraper' -t dependency_aware -d 'requests,beautifulsoup4'"
run_test "List models" "python -m getllm --mock list"
run_test "Show installed models" "python -m getllm --mock installed"
run_test "Update models" "python -m getllm --mock update"
run_test "Show default model" "python -m getllm --mock default"
run_test "Test model" "python -m getllm --mock test"
run_test "Interactive mode" "echo 'exit' | python -m getllm --mock interactive"

# Test with debug flag
run_test "Debug mode" "python -m getllm --debug --mock code 'test debug'"

# Test with search
run_test "Search models" "python -m getllm --mock --search 'llama'"

# Test version
run_test "Version" "python -m getllm --version"

# Test help
run_test "Help" "python -m getllm --help"

echo -e "\n${GREEN}All tests completed successfully!${NC}"
