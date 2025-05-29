#!/bin/bash

# Test script to run only the failed commands from test_getllm_commands.sh
# and save results to a file

# Output file for failed tests
FAILED_TESTS_FILE="failed_tests.log"
TEST_LOG_DIR="./test_logs"

# Ensure test log directory exists
mkdir -p "$TEST_LOG_DIR"

# Clear previous failed tests file
echo "" > "$FAILED_TESTS_FILE"

# Function to run a single test and check if it fails
run_and_check_test() {
    local test_num=$1
    local cmd=$2
    local description=$3
    
    echo "Running test #$test_num: $description"
    echo "Command: $cmd"
    
    # Run the command and capture output and exit code
    output=$($cmd 2>&1)
    exit_code=$?
    
    # Log the output
    echo "$output" > "$TEST_LOG_DIR/test_${test_num}_output.log"
    
    # Check if the command failed
    if [ $exit_code -ne 0 ]; then
        echo "[FAILED] Test #$test_num: $description" | tee -a "$FAILED_TESTS_FILE"
        echo "  Command: $cmd" | tee -a "$FAILED_TESTS_FILE"
        echo "  Exit code: $exit_code" | tee -a "$FAILED_TESTS_FILE"
        echo "  Output saved to: $TEST_LOG_DIR/test_${test_num}_output.log" | tee -a "$FAILED_TESTS_FILE"
        echo "----------------------------------------" | tee -a "$FAILED_TESTS_FILE"
        return 1
    else
        echo "[PASSED] Test #$test_num: $description"
        return 0
    fi
}

# List of previously failed test numbers and their commands
# Format: test_number:command
declare -A failed_tests=(
    [11]="python -m getllm update --mock"
    [13]="python -m getllm --debug update --mock"
    [15]="python -m getllm code 'print hello world' --mock"
    [16]="python -m getllm code 'create a fibonacci function' --mock"
    [17]="python -m getllm code 'sort a list of numbers' --mock -t basic"
    [18]="python -m getllm code 'web scraper for news' --mock -t dependency_aware -d 'requests,beautifulsoup4'"
    [19]="python -m getllm --debug code 'simple calculator' --mock"
    [20]="python -m getllm code 'file reader utility' --mock -t platform_aware"
)

# Run only the failed tests
for test_num in "${!failed_tests[@]}"; do
    cmd="${failed_tests[$test_num]}"
    run_and_check_test "$test_num" "$cmd"
done

# Print summary
echo -e "\n=== Test Summary ==="
if [ -s "$FAILED_TESTS_FILE" ]; then
    echo -e "\nThe following tests failed:"
    cat "$FAILED_TESTS_FILE"
    echo -e "\nSee $TEST_LOG_DIR/ for detailed output"
    exit 1
else
    echo -e "\nAll previously failing tests now pass!"
    exit 0
fi
