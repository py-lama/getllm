#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
getLLM: A package for managing LLM models with Ollama integration.

This package provides functionality for managing, installing, and configuring
LLM models for use with the Ollama API.
"""

__version__ = "0.1.0"

# Import from the getllm subpackage
from getllm.getllm.models import (
    get_models, 
    get_default_model, 
    set_default_model, 
    install_model,
    list_installed_models,
    update_models_from_ollama
)
from getllm.getllm.ollama import (
    OllamaServer as OllamaIntegration,
    get_ollama_integration,
    start_ollama_server,
    install_ollama_model,
    list_ollama_models,
    query_ollama,
    OllamaError,
    OllamaInstallationError,
    OllamaStartupError,
    ModelNotFoundError,
    ModelInstallationError,
    ModelGenerationError,
    APIError,
    AuthenticationError,
    RateLimitExceededError,
    InsufficientDiskSpaceError,
    ModelValidationError
)

# Import the CLI
try:
    from getllm.cli import cli
    CLI_AVAILABLE = True
except ImportError:
    import warnings
    warnings.warn("CLI dependencies not installed. Install with 'pip install getllm[cli]'")
    CLI_AVAILABLE = False

__all__ = [
    # Model management functions
    'get_models',
    'get_default_model',
    'set_default_model',
    'install_model',
    'list_installed_models',
    'update_models_from_ollama',
    
    # Ollama integration
    'OllamaIntegration',
    'get_ollama_integration',
    'start_ollama_server',
    'install_ollama_model',
    'list_ollama_models',
    'query_ollama',
    
    # Exceptions
    'OllamaError',
    'OllamaInstallationError',
    'OllamaStartupError',
    'ModelNotFoundError',
    'ModelInstallationError',
    'ModelGenerationError',
    'APIError',
    'AuthenticationError',
    'RateLimitExceededError',
    'InsufficientDiskSpaceError',
    'ModelValidationError'
]

# Only expose cli if available
if CLI_AVAILABLE:
    __all__.append('cli')
