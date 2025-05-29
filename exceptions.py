"""
Custom exceptions for the getllm package.
"""

class GetLLMError(Exception):
    """Base exception for all getllm exceptions."""
    pass

class ModelError(GetLLMError):
    """Base exception for model-related errors."""
    pass

class ModelNotFoundError(ModelError):
    """Raised when a model is not found."""
    pass

class ModelInstallationError(ModelError):
    """Raised when there's an error installing a model."""
    pass

class ModelQueryError(ModelError):
    """Raised when there's an error querying a model."""
    pass

class ConfigurationError(GetLLMError):
    """Raised when there's a configuration error."""
    pass

class AuthenticationError(GetLLMError):
    """Raised when there's an authentication error."""
    pass

class ValidationError(GetLLMError):
    """Raised when there's a validation error."""
    pass
