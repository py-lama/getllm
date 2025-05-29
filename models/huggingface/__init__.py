"""
Hugging Face model integration for PyLLM.

This module provides functionality for working with Hugging Face models,
including downloading, loading, and interacting with them through a
unified interface.
"""

from .manager import HuggingFaceModelManager, get_hf_model_manager

__all__ = [
    'HuggingFaceModelManager',
    'get_hf_model_manager'
]
