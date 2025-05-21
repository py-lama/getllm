# Pyllm

A package for managing LLM models with Ollama integration.

## Features

- Model management for Large Language Models
- Integration with Ollama API
- Model installation and configuration
- Default model selection
- Model discovery from Ollama's library

## Installation

```bash
pip install pyllm
```

## Usage

```python
from pyllm import get_models, get_default_model, set_default_model, install_model

# Get available models
models = get_models()
for model in models:
    print(f"{model['name']} - {model.get('desc', '')}")

# Get the current default model
default_model = get_default_model()
print(f"Current default model: {default_model}")

# Set a new default model
set_default_model("codellama:7b")

# Install a model
install_model("deepseek-coder:6.7b")
```

## Environment Variables

The package uses the following environment variables:

- `OLLAMA_MODEL`: The default model to use with Ollama

## License

