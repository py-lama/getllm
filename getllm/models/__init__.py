"""
This package contains model-related functionality for the getllm application.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from .base import ModelManager
from .huggingface import HuggingFaceModelManager
from .ollama import OllamaModelManager
from .metadata import ModelMetadataManager
from ..utils.config import get_models_dir, get_models_metadata_path

# Initialize model managers
huggingface_manager = HuggingFaceModelManager()
ollama_manager = OllamaModelManager()
metadata_manager = ModelMetadataManager()

# Define default models
DEFAULT_HF_MODELS = [
    "gpt2",
    "bert-base-uncased",
    "distilgpt2"
]

def get_models() -> List[Dict[str, Any]]:
    """
    Get all available models from all sources.
    
    Returns:
        List of model dictionaries with metadata.
    """
    models = []
    
    # Get models from Hugging Face
    try:
        hf_models = huggingface_manager.get_available_models()
        models.extend([{"source": "huggingface", **model} for model in hf_models])
    except Exception as e:
        print(f"Error getting Hugging Face models: {e}")
    
    # Get models from Ollama
    try:
        ollama_models = ollama_manager.get_available_models()
        models.extend([{"source": "ollama", **model} for model in ollama_models])
    except Exception as e:
        print(f"Error getting Ollama models: {e}")
    
    return models

def get_hf_models_cache_path() -> Path:
    """
    Get the path to the Hugging Face models cache file.
    
    Returns:
        Path to the cache file.
    """
    return get_models_dir() / "huggingface_models.json"

def update_huggingface_models_cache(limit: int = 50) -> bool:
    """
    Update the cache of available Hugging Face models.
    
    Args:
        limit: Maximum number of models to fetch.
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        models = huggingface_manager.get_available_models(limit=limit)
        cache_path = get_hf_models_cache_path()
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(cache_path, 'w') as f:
            json.dump(models, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error updating Hugging Face models cache: {e}")
        return False

def update_models_from_ollama() -> bool:
    """
    Update the list of available Ollama models.
    
    Returns:
        True if successful, False otherwise.
    """
    try:
        ollama_models = ollama_manager.get_available_models()
        # Update metadata
        for model in ollama_models:
            metadata_manager.update_model_metadata(
                model['name'],
                {"source": "ollama", "last_updated": str(metadata_manager.get_current_timestamp())}
            )
        return True
    except Exception as e:
        print(f"Error updating Ollama models: {e}")
        return False

def update_models_metadata() -> bool:
    """
    Update metadata for all models.
    
    Returns:
        True if successful, False otherwise.
    """
    try:
        # Update Hugging Face models metadata
        hf_models = huggingface_manager.get_available_models()
        for model in hf_models:
            metadata_manager.update_model_metadata(
                model['name'],
                {"source": "huggingface", "last_updated": str(metadata_manager.get_current_timestamp())}
            )
        
        # Update Ollama models metadata
        update_models_from_ollama()
        
        return True
    except Exception as e:
        print(f"Error updating models metadata: {e}")
        return False

def load_huggingface_models_from_cache() -> List[Dict]:
    """
    Load Hugging Face models from cache.
    
    Returns:
        List of Hugging Face models from cache.
    """
    cache_path = get_hf_models_cache_path()
    if not cache_path.exists():
        return []
    
    try:
        with open(cache_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading Hugging Face models from cache: {e}")
        return []

def load_ollama_models_from_cache() -> List[Dict]:
    """
    Load Ollama models from cache.
    
    Returns:
        List of Ollama models from cache.
    """
    cache_path = get_models_dir() / "ollama_models.json"
    if not cache_path.exists():
        return []
    
    try:
        with open(cache_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading Ollama models from cache: {e}")
        return []

def search_huggingface_models(query: str = None, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Search for models on Hugging Face based on a query string.
    
    Args:
        query: Search query string
        limit: Maximum number of models to return
        
    Returns:
        List of model dictionaries matching the query
    """
    try:
        # Use the huggingface_manager to search for models
        return huggingface_manager.search_models(query=query, limit=limit)
    except Exception as e:
        print(f"Error searching Hugging Face models: {e}")
        return []

def get_huggingface_models(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Get available models from Hugging Face.
    
    Args:
        limit: Maximum number of models to return
        
    Returns:
        List of model dictionaries
    """
    try:
        return huggingface_manager.get_available_models()[:limit]
    except Exception as e:
        print(f"Error getting Hugging Face models: {e}")
        return []

def update_models_from_huggingface(query: str = None, limit: int = 20) -> bool:
    """
    Update models from Hugging Face based on a query string.
    
    Args:
        query: Optional search query to filter models
        limit: Maximum number of models to update
        
    Returns:
        True if successful, False otherwise
    """
    try:
        models = search_huggingface_models(query=query, limit=limit)
        # Update metadata for each model
        for model in models:
            metadata_manager.update_model_metadata(
                model.get('name', model.get('id', '')),
                {"source": "huggingface", "last_updated": str(metadata_manager.get_current_timestamp())}
            )
        return True
    except Exception as e:
        print(f"Error updating models from Hugging Face: {e}")
        return False

__all__ = [
    'ModelManager',
    'HuggingFaceModelManager',
    'OllamaModelManager',
    'ModelMetadataManager',
    'get_models',
    'get_hf_models_cache_path',
    'update_huggingface_models_cache',
    'update_models_from_ollama',
    'update_models_metadata',
    'DEFAULT_HF_MODELS',
    'search_huggingface_models',
    'get_huggingface_models',
    'update_models_from_huggingface',
    'load_huggingface_models_from_cache',
    'load_ollama_models_from_cache'
]
