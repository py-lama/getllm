# Makefile for PyLLM

.PHONY: all setup clean test lint format run help venv

# Default values
PORT ?= 8001
HOST ?= 0.0.0.0

# Default target
all: help

# Create virtual environment if it doesn't exist
venv:
	@test -d venv || python3 -m venv venv

# Setup project
setup: venv
	@echo "Setting up PyLLM..."
	@. venv/bin/activate && pip install -e .

# Clean project
clean:
	@echo "Cleaning PyLLM..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name *.egg-info -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +

# Run tests
test: setup
	@echo "Testing PyLLM..."
	@. venv/bin/activate && python -m unittest discover

# Lint code
lint: setup
	@echo "Linting PyLLM..."
	@. venv/bin/activate && flake8 pyllm

# Format code
format: setup
	@echo "Formatting PyLLM..."
	@. venv/bin/activate && black pyllm

# Run the API server
run: setup
	@echo "Running PyLLM API server on port $(PORT)..."
	@. venv/bin/activate && uvicorn pyllm.api:app --host $(HOST) --port $(PORT)

# Run with custom port (for backward compatibility)
run-port: setup
	@echo "Running PyLLM API server on port $(PORT)..."
	@. venv/bin/activate && uvicorn pyllm.api:app --host $(HOST) --port $(PORT)

# Help
help:
	@echo "PyLLM Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  setup     - Set up the project"
	@echo "  clean     - Clean the project"
	@echo "  test      - Run tests"
	@echo "  lint      - Lint the code"
	@echo "  format    - Format the code with black"
	@echo "  run       - Run the API server"
	@echo "  run-port PORT=8001 - Run the API server on a custom port"
	@echo "  help      - Show this help message"
