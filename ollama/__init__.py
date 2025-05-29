"""
Ollama Integration for PyLLM

This package provides integration with Ollama for high-quality code generation.
It handles model management, automatic installation, and fallback mechanisms.
"""

from .api.client import OllamaClient
from .services.server import OllamaServer
from .models.manager import OllamaModelManager
from .models.installer import ModelInstaller
from .utils.progress import ProgressSpinner

__all__ = [
    'OllamaClient',
    'OllamaServer',
    'OllamaModelManager',
    'ModelInstaller',
    'ProgressSpinner'
]
