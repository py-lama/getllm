"""
Ollama Server for PyLLM

This package provides a server interface for Ollama for high-quality code generation.
It handles model management, automatic installation, and fallback mechanisms.
"""

from .models import OllamaModelManager
from .server import OllamaServer
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

# For backward compatibility (deprecated, will be removed in a future version)
OllamaIntegration = OllamaServer  # Alias for backward compatibility (deprecated)

__all__ = [
    'OllamaServer',
    'OllamaModelManager',
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
    'ModelValidationError',
    'OllamaIntegration'  # Deprecated, included for backward compatibility
]
