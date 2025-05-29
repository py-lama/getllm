"""
Custom exceptions for the Ollama integration.
"""

class OllamaError(Exception):
    """Base exception for all Ollama-related errors."""
    pass

class ModelNotFoundError(OllamaError):
    """Raised when a specified model is not found."""
    pass

class InstallationError(OllamaError):
    """Raised when there's an error during installation."""
    pass

class ServerError(OllamaError):
    """Raised when there's an error with the Ollama server."""
    pass

class DiskSpaceError(OllamaError):
    """Raised when there's not enough disk space for an operation."""
    def __init__(self, message, available_gb=None, required_gb=None):
        super().__init__(message)
        self.available_gb = available_gb
        self.required_gb = required_gb

class ModelInstallationError(OllamaError):
    """Raised when there's an error installing a model."""
    pass
