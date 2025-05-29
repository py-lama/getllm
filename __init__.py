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
    ModelManager,
    HuggingFaceModelManager,
    OllamaModelManager,
    get_models, 
    get_default_model, 
    set_default_model, 
    install_model,
    list_installed_models,
    update_models_from_ollama,
    update_models_metadata,
    search_huggingface_models,
    interactive_model_search,
    update_models_from_huggingface,
    update_huggingface_models_cache,
    load_huggingface_models_from_cache,
    load_ollama_models_from_cache
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
    # Model management classes
    'ModelManager',
    'HuggingFaceModelManager',
    'OllamaModelManager',
    
    # Model management functions
    'get_models',
    'get_default_model',
    'set_default_model',
    'install_model',
    'list_installed_models',
    'update_models_from_ollama',
    'update_models_metadata',
    'update_models_from_huggingface',
    'update_huggingface_models_cache',
    'search_huggingface_models',
    'interactive_model_search',
    'load_huggingface_models_from_cache',
    'load_ollama_models_from_cache',
    
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
