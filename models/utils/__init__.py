"""
Utility functions for model management.

This module provides helper functions for working with models,
including model loading, saving, and other common operations.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from ..exceptions import ModelError

logger = logging.getLogger('getllm.models.utils')

def get_models_dir() -> str:
    """Get the directory where models are stored.
    
    Returns:
        str: Path to the models directory
    """
    return os.path.join(os.path.expanduser("~"), ".cache", "getllm", "models")

def get_model_dir(model_name: str) -> str:
    """Get the directory for a specific model.
    
    Args:
        model_name: Name of the model
        
    Returns:
        str: Path to the model directory
    """
    return os.path.join(get_models_dir(), model_name)

def ensure_model_dir_exists(model_name: str) -> str:
    """Ensure the directory for a model exists.
    
    Args:
        model_name: Name of the model
        
    Returns:
        str: Path to the model directory
    """
    model_dir = get_model_dir(model_name)
    os.makedirs(model_dir, exist_ok=True)
    return model_dir

def load_model_metadata(model_name: str) -> Dict[str, Any]:
    """Load metadata for a model.
    
    Args:
        model_name: Name of the model
        
    Returns:
        dict: Model metadata
        
    Raises:
        ModelError: If the metadata file doesn't exist or is invalid
    """
    metadata_path = os.path.join(get_model_dir(model_name), "metadata.json")
    if not os.path.exists(metadata_path):
        raise ModelError(f"Metadata not found for model: {model_name}")
    
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        raise ModelError(f"Failed to load metadata for model {model_name}: {e}")

def save_model_metadata(model_name: str, metadata: Dict[str, Any]) -> None:
    """Save metadata for a model.
    
    Args:
        model_name: Name of the model
        metadata: Model metadata to save
        
    Raises:
        ModelError: If the metadata cannot be saved
    """
    model_dir = ensure_model_dir_exists(model_name)
    metadata_path = os.path.join(model_dir, "metadata.json")
    
    try:
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
    except (IOError, TypeError) as e:
        raise ModelError(f"Failed to save metadata for model {model_name}: {e}")

def get_model_size(model_name: str) -> Optional[int]:
    """Get the size of a model in bytes.
    
    Args:
        model_name: Name of the model
        
    Returns:
        Optional[int]: Size in bytes, or None if unknown
    """
    try:
        model_dir = get_model_dir(model_name)
        if not os.path.exists(model_dir):
            return None
            
        total_size = 0
        for dirpath, _, filenames in os.walk(model_dir):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.isfile(fp):
                    total_size += os.path.getsize(fp)
        return total_size
    except Exception as e:
        logger.warning(f"Error calculating model size for {model_name}: {e}")
        return None

def format_model_size(size_bytes: Optional[int]) -> str:
    """Format a model size in a human-readable format.
    
    Args:
        size_bytes: Size in bytes, or None
        
    Returns:
        str: Formatted size string (e.g., "1.2 GB")
    """
    if size_bytes is None:
        return "Unknown"
        
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"

def get_available_models() -> List[str]:
    """Get a list of all available models.
    
    Returns:
        List of model names
    """
    models_dir = get_models_dir()
    if not os.path.exists(models_dir):
        return []
        
    return [
        name for name in os.listdir(models_dir)
        if os.path.isdir(os.path.join(models_dir, name))
    ]

def is_model_installed(model_name: str) -> bool:
    """Check if a model is installed.
    
    Args:
        model_name: Name of the model to check
        
    Returns:
        bool: True if the model is installed
    """
    model_dir = get_model_dir(model_name)
    return os.path.exists(model_dir) and os.path.isdir(model_dir)

def delete_model(model_name: str) -> bool:
    """Delete a model.
    
    Args:
        model_name: Name of the model to delete
        
    Returns:
        bool: True if the model was deleted successfully
    """
    import shutil
    
    model_dir = get_model_dir(model_name)
    if not os.path.exists(model_dir):
        return False
        
    try:
        shutil.rmtree(model_dir)
        return True
    except Exception as e:
        logger.error(f"Failed to delete model {model_name}: {e}")
        return False
