"""
Ollama Integration for PyLLM

This package provides integration with Ollama for high-quality code generation.
It handles model management, automatic installation, and fallback mechanisms.
"""

from .models import OllamaModelManager
from .server import OllamaServer
from .exceptions import OllamaError, ModelNotFoundError, InstallationError
from .api import query_ollama, list_ollama_models, install_ollama_model

# For backward compatibility
OllamaIntegration = OllamaServer  # Alias for backward compatibility

def get_ollama_integration(model: str = None):
    """
    Get an OllamaIntegration instance with the specified model.
    
    Args:
        model: Optional model name to use
        
    Returns:
        An OllamaIntegration instance
    """
    return OllamaServer(model=model)

def start_ollama_server():
    """
    Start the Ollama server and return an OllamaIntegration instance.
    
    Returns:
        An OllamaIntegration instance with the server started
    """
    server = OllamaServer()
    server.start()
    return server

__all__ = [
    'OllamaIntegration',
    'OllamaServer',
    'OllamaModelManager',
    'OllamaError',
    'ModelNotFoundError',
    'InstallationError',
    'get_ollama_integration',
    'start_ollama_server',
    'query_ollama',
    'list_ollama_models',
    'install_ollama_model',
]
