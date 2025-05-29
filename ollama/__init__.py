"""
Ollama Integration for PyLLM

This package provides integration with Ollama for high-quality code generation.
It handles model management, automatic installation, and fallback mechanisms.
"""

from .integration import OllamaIntegration
from .api.client import OllamaClient
from .services.server import OllamaServer
from .models.manager import OllamaModelManager
from .models.installer import ModelInstaller
from .utils import ProgressSpinner, progress_bar
from .exceptions import (
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

__all__ = [
    'OllamaIntegration',
    'OllamaClient',
    'OllamaServer',
    'OllamaModelManager',
    'ModelInstaller',
    'ProgressSpinner',
    'progress_bar',
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
