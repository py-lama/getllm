# GetLLM Testing Guide

This document provides comprehensive testing instructions for the GetLLM package.

## Testing Environments

GetLLM can be tested in various environments to ensure it works correctly across different platforms and configurations.

### Isolated Docker Testing Environment

To ensure GetLLM works correctly in different environments and to catch issues like the Ollama dependency error, we've created a Docker-based testing environment:

```bash
# Build the Docker test environment
make docker-build

# Run all tests in an isolated Docker container
make docker-test

# Run CLI-specific tests in Docker
make docker-test-cli

# Run tests with Ollama integration
make docker-test-with-ollama

# Run Ansible-based installation tests
make docker-test-ansible

# Start an interactive shell in the test container
make docker-interactive

# Clean up Docker test resources
make docker-clean
```

### Local Testing

For local testing, you can use the following commands:

```bash
# Run unit tests
make test

# Run linting
make lint

# Format code
make format
```

### Makefile Testing

Test the GetLLM Makefile using the following commands from the root directory:

```bash
# Test only the GetLLM Makefile
./test_all_makefiles.sh --test-only "getllm"

# Test with verbose output
./test_all_makefiles.sh --verbose --test-only "getllm"

# Try to fix common issues
./test_all_makefiles.sh --fix --test-only "getllm"
```

### Standard Docker-based Testing

Test GetLLM in an isolated Docker container using the root test script:

```bash
# Test GetLLM in Docker
./docker_test_makefiles.sh --test-only "getllm"
```

### GitHub Actions Testing

Test and validate GetLLM's GitHub Actions workflows:

```bash
# Validate GitHub Actions workflows
./tests/validate_github_workflows.sh

# Test GitHub Actions workflows locally
./tests/test_github_actions.sh --test-only "getllm/ci.yml" --job build-test
```

### Using the Makefile in tests directory

The `tests` directory contains a comprehensive Makefile for testing the entire ecosystem:

```bash
# Test GetLLM Makefile
cd tests && make test-makefiles

# Test GitHub Actions workflows
cd tests && make test-github-actions
```

## Troubleshooting Common Test Issues

### Ollama Dependency Error

When running tests that interact with Ollama, you might encounter this error:

```
Error installing model: [Errno 2] No such file or directory: 'ollama'
```

This happens because getllm requires the Ollama binary to be installed and available in your PATH.

#### Solutions:

1. **Install Ollama**: Follow the instructions at [ollama.com](https://ollama.com) to install Ollama on your system.

2. **Use Mock Mode**: If you can't install Ollama, use the mock mode:
   ```bash
   getllm --mock --search llama
   ```

3. **Use Docker Testing Environment**: Use our Docker testing environment which includes Ollama:
   ```bash
   make docker-test-with-ollama
   ```

### Timeout Errors

When testing direct code generation, you might encounter timeout errors like `ReadTimeoutError: HTTPConnectionPool(host='localhost', port=11434): Read timed out`. This indicates that the Ollama server is not responding in time, which could be due to:
- The model is too large for your system's resources
- The Ollama server is busy with other requests
- The prompt requires too much processing time

#### Workaround:

For timeout issues, try:
1. Using a smaller model
2. Increasing the timeout in the test configuration
3. Using the mock mode for testing: `--mock`

## Continuous Integration

GetLLM uses GitHub Actions for continuous integration. The CI pipeline includes:

1. **Linting**: Code quality checks using flake8
2. **Unit Tests**: Running pytest for unit tests
3. **Integration Tests**: Testing with actual Ollama models
4. **Build Testing**: Ensuring the package builds correctly

You can view the CI configuration in `.github/workflows/ci.yml`.

## Adding New Tests

When adding new tests to GetLLM:

1. Place unit tests in the `tests/` directory
2. Follow the naming convention `test_*.py`
3. Use pytest fixtures for common setup
4. Mock external dependencies when appropriate
5. Include both positive and negative test cases

For CLI tests, use the `subprocess` module to invoke the actual command-line interface.

## Test Coverage

To generate a test coverage report:

```bash
make test-coverage
```

This will generate a coverage report in the `htmlcov/` directory that you can view in your browser.
