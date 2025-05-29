#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
getLLM: A package for managing LLM models with Ollama integration.

This package provides functionality for managing, installing, and configuring
LLM models for use with the Ollama API.
"""

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
    OllamaError,
    ModelNotFoundError
)

__all__ = [
    'get_models',
    'get_default_model',
    'set_default_model',
    'install_model',
    'list_installed_models',
    'update_models_from_ollama',
    'get_ollama_integration',
    'start_ollama_server',
    'install_ollama_model',
    'list_ollama_models',
]
