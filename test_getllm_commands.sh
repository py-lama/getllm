#!/bin/bash

# Test script for getllm with 100 non-interactive calls
# This script will test various command line options and features

# Set up log directory for test results
TEST_LOG_DIR="./test_logs"
mkdir -p "$TEST_LOG_DIR"

echo "Starting getllm command tests at $(date)" | tee "$TEST_LOG_DIR/test_summary.log"

# Function to run a test and log results
run_test() {
    local test_num=$1
    local cmd=$2
    local description=$3
    
    echo "Test #$test_num: $description" | tee -a "$TEST_LOG_DIR/test_summary.log"
    echo "Command: $cmd" | tee -a "$TEST_LOG_DIR/test_summary.log"
    
    # Run the command and capture output
    output=$(eval "$cmd" 2>&1)
    exit_code=$?
    
    # Log the output
    echo "$output" > "$TEST_LOG_DIR/test_${test_num}_output.log"
    
    # Check if the command was successful
    if [ $exit_code -eq 0 ]; then
        echo "Result: SUCCESS (exit code: $exit_code)" | tee -a "$TEST_LOG_DIR/test_summary.log"
    else
        echo "Result: FAILED (exit code: $exit_code)" | tee -a "$TEST_LOG_DIR/test_summary.log"
    fi
    
    echo "----------------------------------------" | tee -a "$TEST_LOG_DIR/test_summary.log"
}

# Basic commands
run_test 1 "python -m getllm --help" "Show help message"
run_test 2 "python -m getllm --debug --help" "Show help message with debug output"
run_test 3 "python -m getllm list" "List available models"
run_test 4 "python -m getllm --debug list" "List available models with debug output"
run_test 5 "python -m getllm default" "Show default model"

# Model search tests
run_test 6 "python -m getllm --search llama --mock" "Search for llama models in mock mode"
run_test 7 "python -m getllm --search mistral --mock" "Search for mistral models in mock mode"
run_test 8 "python -m getllm --search phi --mock" "Search for phi models in mock mode"
run_test 9 "python -m getllm --debug --search falcon --mock" "Search for falcon models with debug in mock mode"
run_test 10 "python -m getllm --search gemma --mock" "Search for gemma models in mock mode"

# Update tests
run_test 11 "python -m getllm update --mock" "Update models from ollama in mock mode"
run_test 12 "python -m getllm --update-hf --mock" "Update models from Hugging Face in mock mode"
run_test 13 "python -m getllm --debug update --mock" "Update models from ollama with debug in mock mode"
run_test 14 "python -m getllm --debug --update-hf --mock" "Update models from Hugging Face with debug in mock mode"

# Code generation tests (with mock mode to avoid actual LLM calls)
run_test 15 "python -m getllm code 'print hello world' --mock" "Generate hello world code in mock mode"
run_test 16 "python -m getllm code 'create a fibonacci function' --mock" "Generate fibonacci function in mock mode"
run_test 17 "python -m getllm code 'sort a list of numbers' --mock -t basic" "Generate sorting code with basic template in mock mode"
run_test 18 "python -m getllm code 'web scraper for news' --mock -t dependency_aware -d 'requests,beautifulsoup4'" "Generate web scraper with dependencies in mock mode"
run_test 19 "python -m getllm --debug code 'simple calculator' --mock" "Generate calculator with debug in mock mode"
run_test 20 "python -m getllm code 'file reader utility' --mock -t platform_aware" "Generate file reader with platform awareness in mock mode"

# Direct prompts (with mock mode)
run_test 21 "python -m getllm 'write a python function to check if a string is a palindrome' --mock" "Direct prompt for palindrome function in mock mode"
run_test 22 "python -m getllm 'create a simple HTTP server' --mock -t secure" "Direct prompt for HTTP server with secure template in mock mode"
run_test 23 "python -m getllm 'generate a random password' --mock -t performance" "Direct prompt for password generator with performance template in mock mode"
run_test 24 "python -m getllm --debug 'write a function to count words in a text file' --mock" "Direct prompt with debug in mock mode"
run_test 25 "python -m getllm 'create a simple GUI calculator' --mock -t pep8" "Direct prompt for GUI calculator with PEP8 template in mock mode"

# Various flag combinations
run_test 26 "python -m getllm code 'hello world' --mock -s" "Generate code and save to file in mock mode"
run_test 27 "python -m getllm code 'print current date' --mock -s -r" "Generate and run code in mock mode"
run_test 28 "python -m getllm --debug code 'list files in directory' --mock -s" "Generate code with debug and save in mock mode"
run_test 29 "python -m getllm code 'create a simple class' --mock -m mock-model" "Generate code with specific model in mock mode"
run_test 30 "python -m getllm --debug code 'read JSON file' --mock -t testable" "Generate testable code with debug in mock mode"

# More search variations
run_test 31 "python -m getllm -S llama --mock" "Search for llama models using -S flag in mock mode"
run_test 32 "python -m getllm -S gpt --mock" "Search for gpt models using -S flag in mock mode"
run_test 33 "python -m getllm -S bert --mock" "Search for bert models using -S flag in mock mode"
run_test 34 "python -m getllm -S stable --mock" "Search for stable models using -S flag in mock mode"
run_test 35 "python -m getllm -S tiny --mock" "Search for tiny models using -S flag in mock mode"

# Test with different log file paths
run_test 36 "python -m getllm --debug --log-file $TEST_LOG_DIR/custom_log.log list" "List models with custom log file"
run_test 37 "python -m getllm --debug --log-file $TEST_LOG_DIR/search_log.log --search llama --mock" "Search with custom log file in mock mode"
run_test 38 "python -m getllm --debug --log-file $TEST_LOG_DIR/update_log.log update --mock" "Update with custom log file in mock mode"
run_test 39 "python -m getllm --debug --log-file $TEST_LOG_DIR/code_log.log code 'hello' --mock" "Generate code with custom log file in mock mode"
run_test 40 "python -m getllm --debug --log-file $TEST_LOG_DIR/direct_log.log 'simple function' --mock" "Direct prompt with custom log file in mock mode"

# Test installed command
run_test 41 "python -m getllm installed" "List installed models"
run_test 42 "python -m getllm --debug installed" "List installed models with debug output"

# Test with different model names for various operations
run_test 43 "python -m getllm code 'hello world' --mock -m llama2" "Generate code with llama2 model in mock mode"
run_test 44 "python -m getllm code 'hello world' --mock -m mistral" "Generate code with mistral model in mock mode"
run_test 45 "python -m getllm code 'hello world' --mock -m phi" "Generate code with phi model in mock mode"
run_test 46 "python -m getllm code 'hello world' --mock -m gemma" "Generate code with gemma model in mock mode"
run_test 47 "python -m getllm code 'hello world' --mock -m falcon" "Generate code with falcon model in mock mode"

# Test with different template types
run_test 48 "python -m getllm code 'sort array' --mock -t basic" "Generate code with basic template in mock mode"
run_test 49 "python -m getllm code 'sort array' --mock -t platform_aware" "Generate code with platform_aware template in mock mode"
run_test 50 "python -m getllm code 'sort array' --mock -t dependency_aware" "Generate code with dependency_aware template in mock mode"
run_test 51 "python -m getllm code 'sort array' --mock -t testable" "Generate code with testable template in mock mode"
run_test 52 "python -m getllm code 'sort array' --mock -t secure" "Generate code with secure template in mock mode"
run_test 53 "python -m getllm code 'sort array' --mock -t performance" "Generate code with performance template in mock mode"
run_test 54 "python -m getllm code 'sort array' --mock -t pep8" "Generate code with pep8 template in mock mode"

# Test with invalid commands or options to check error handling
run_test 55 "python -m getllm invalid_command" "Test with invalid command"
run_test 56 "python -m getllm --invalid-option" "Test with invalid option"
run_test 57 "python -m getllm code" "Test code command without prompt"
run_test 58 "python -m getllm --debug invalid_command" "Test invalid command with debug"
run_test 59 "python -m getllm install" "Test install command without model name"
run_test 60 "python -m getllm set-default" "Test set-default command without model name"

# Test with complex prompts
run_test 61 "python -m getllm code 'create a program that calculates prime numbers up to 100' --mock" "Generate prime numbers program in mock mode"
run_test 62 "python -m getllm code 'build a simple REST API with Flask' --mock" "Generate Flask REST API in mock mode"
run_test 63 "python -m getllm code 'implement a binary search tree' --mock" "Generate binary search tree in mock mode"
run_test 64 "python -m getllm code 'create a program to download images from a website' --mock" "Generate image downloader in mock mode"
run_test 65 "python -m getllm code 'implement a simple neural network' --mock" "Generate neural network in mock mode"

# Test with various combinations of options
run_test 66 "python -m getllm --debug code 'hello world' --mock -s -r" "Generate, save and run code with debug in mock mode"
run_test 67 "python -m getllm --debug code 'read CSV file' --mock -t dependency_aware -d pandas" "Generate code with dependency and debug in mock mode"
run_test 68 "python -m getllm --debug code 'web server' --mock -t secure -s" "Generate secure web server and save with debug in mock mode"
run_test 69 "python -m getllm --debug --log-file $TEST_LOG_DIR/complex_log.log code 'data analysis' --mock -t performance -d numpy,pandas" "Complex command with multiple options in mock mode"
run_test 70 "python -m getllm --debug code 'unit test example' --mock -t testable -s -r" "Generate testable code, save and run with debug in mock mode"

# Additional search tests
run_test 71 "python -m getllm --search 7b --mock" "Search for 7b models in mock mode"
run_test 72 "python -m getllm --search 13b --mock" "Search for 13b models in mock mode"
run_test 73 "python -m getllm --search 70b --mock" "Search for 70b models in mock mode"
run_test 74 "python -m getllm --search gguf --mock" "Search for gguf models in mock mode"
run_test 75 "python -m getllm --search ggml --mock" "Search for ggml models in mock mode"

# Test with very short and very long prompts
run_test 76 "python -m getllm code 'hi' --mock" "Generate code with very short prompt in mock mode"
run_test 77 "python -m getllm code 'create a comprehensive library management system with user authentication, book catalog, borrowing functionality, fine calculation, and reporting features' --mock" "Generate code with very long prompt in mock mode"

# Test with special characters in prompts
run_test 78 "python -m getllm code 'print(\"Hello, world!\")' --mock" "Generate code with quotes in prompt in mock mode"
run_test 79 "python -m getllm code 'calculate 2+2' --mock" "Generate code with plus sign in prompt in mock mode"
run_test 80 "python -m getllm code 'check if x > y' --mock" "Generate code with greater than sign in prompt in mock mode"

# Test with multiple consecutive commands
run_test 81 "python -m getllm list && python -m getllm default" "Run multiple commands in sequence"
run_test 82 "python -m getllm --debug list && python -m getllm --debug default" "Run multiple commands with debug in sequence"

# Additional edge cases
run_test 83 "python -m getllm" "Run without any command or prompt"
run_test 84 "python -m getllm --debug" "Run with debug but without command"
run_test 85 "python -m getllm --mock" "Run with mock but without command"
run_test 86 "python -m getllm --debug --mock" "Run with debug and mock but without command"
run_test 87 "python -m getllm code '' --mock" "Generate code with empty prompt in mock mode"

# Test with multiple flags
run_test 88 "python -m getllm --debug --mock code 'hello world'" "Generate code with multiple flags in mock mode"
run_test 89 "python -m getllm --debug --mock --log-file $TEST_LOG_DIR/multi_flag.log code 'hello world'" "Generate code with multiple flags and custom log in mock mode"
run_test 90 "python -m getllm --debug --mock -m llama2 code 'hello world'" "Generate code with multiple flags and model in mock mode"

# Test with unusual but valid combinations
run_test 91 "python -m getllm code 'hello world' --mock -t basic -t platform_aware" "Test with repeated template flag in mock mode"
run_test 92 "python -m getllm code 'hello world' --mock -m llama2 -m mistral" "Test with repeated model flag in mock mode"
run_test 93 "python -m getllm --debug --debug code 'hello world' --mock" "Test with repeated debug flag in mock mode"
run_test 94 "python -m getllm --mock --mock code 'hello world'" "Test with repeated mock flag in mock mode"

# Test with environment variables
run_test 95 "GETLLM_DEBUG=1 python -m getllm list" "Test with debug environment variable"
run_test 96 "GETLLM_MODEL=llama2 python -m getllm code 'hello world' --mock" "Test with model environment variable in mock mode"

# Final batch of tests
run_test 97 "python -m getllm test --mock" "Test the default model in mock mode"
run_test 98 "python -m getllm --debug test --mock" "Test the default model with debug in mock mode"
run_test 99 "python -m getllm --version" "Check version information"
run_test 100 "python -m getllm --debug --version" "Check version information with debug output"

echo "All tests completed at $(date)" | tee -a "$TEST_LOG_DIR/test_summary.log"
echo "Test results are available in the $TEST_LOG_DIR directory"
