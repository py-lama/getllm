"""
Ollama model integration for PyLLM.

This module provides functionality for working with Ollama models,
including downloading, loading, and interacting with them through a
unified interface.
"""

from .manager import OllamaModelManager, get_ollama_model_manager

__all__ = [
    'OllamaModelManager',
    'get_ollama_model_manager'
]
