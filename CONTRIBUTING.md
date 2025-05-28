# Contributing to GetLLM

Thank you for your interest in contributing to GetLLM! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We aim to foster an inclusive and welcoming community.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment
4. Create a new branch for your feature or bug fix
5. Make your changes
6. Run tests to ensure your changes don't break existing functionality
7. Submit a pull request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/py-lama/getllm.git
cd getllm

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in development mode
pip install -e .
```

Alternatively, you can use the Makefile:

```bash
make setup
```

## Testing

GetLLM includes several test suites to ensure all features work correctly:

### Running Unit Tests

```bash
# Run unit tests
make test
```

### Testing Command-line Functionality

```bash
# Test command-line functionality
make test-commands
```

### Testing Installation Options

```bash
# Test Ollama installation options
make test-installation
```

### Testing Model Installation

```bash
# Test model installation
make test-models
```

### Running All Tests

```bash
# Run all tests
make test-all
```

### Docker Testing

You can also run tests in Docker:

```bash
# Run tests in Docker
make docker-test

# Run CLI tests in Docker
make docker-test-cli

# Run tests with Ollama in Docker
make docker-test-with-ollama
```

## Pull Request Process

1. Ensure your code passes all tests
2. Update the documentation if necessary
3. Add a description of your changes to the pull request
4. Your pull request will be reviewed by the maintainers

## Style Guidelines

- Follow PEP 8 style guidelines for Python code
- Use meaningful variable and function names
- Write docstrings for all functions, classes, and modules
- Add comments for complex code sections

## Ollama Integration

When working on Ollama integration features, please ensure:

1. All installation options are properly tested
2. Mock mode works correctly for all commands
3. The bexy sandbox integration is properly maintained
4. Docker-based installation is tested on different platforms

## Documentation

When adding new features, please update the relevant documentation:

- README.md for user-facing features
- CONTRIBUTING.md for developer-facing changes
- Code comments and docstrings for API changes

## Questions?

If you have any questions or need help, please open an issue on GitHub or contact the maintainers directly.

Thank you for contributing to GetLLM!
