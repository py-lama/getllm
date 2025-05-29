"""
Model management for PyLLM.

This package provides functionality for managing LLM models, including
installation, listing, and updating models from various sources.
"""

import os
import sys
import subprocess
from pathlib import Path

# --- Auto dependency setup ---
REQUIRED_PACKAGES = ["requests", "bs4", "python-dotenv"]
IMPORT_NAMES = ["requests", "bs4", "dotenv"]  # Correct import for python-dotenv
VENV_DIR = os.path.join(os.path.dirname(__file__), ".venv")

# 1. Create venv if missing
if not os.path.isdir(VENV_DIR):
    subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True)
    print(f"Created virtual environment: {VENV_DIR}")

def _venv_python():
    """Get the path to the Python interpreter in the virtual environment."""
    if os.name == "nt":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    return os.path.join(VENV_DIR, "bin", "python")

# 2. Install missing packages
missing = []
for pkg, imp in zip(REQUIRED_PACKAGES, IMPORT_NAMES):
    try:
        __import__(imp)
    except ImportError:
        missing.append(pkg)

if missing:
    print(f"Installing missing packages: {', '.join(missing)}")
    subprocess.run([_venv_python(), "-m", "pip", "install"] + missing, check=True)
    print("Required dependencies installed. Please restart the script.")
    sys.exit(0)
# --- End auto dependency setup ---

# Import the main components
from .manager import ModelManager
from .constants import DEFAULT_MODELS, DEFAULT_HF_MODELS
from .utils import (
    get_models_dir,
    get_default_model,
    set_default_model,
    get_models,
    install_model,
    list_installed_models,
    update_models_metadata,
    get_model_metadata,
    load_huggingface_models_from_cache,
    load_ollama_models_from_cache
)
from .huggingface import (
    search_huggingface_models,
    interactive_model_search,
    update_models_from_huggingface,
    update_huggingface_models_cache
)
from .ollama import (
    update_models_from_ollama,
    update_ollama_models_cache,
    list_ollama_models,
    install_ollama_model
)

__all__ = [
    # Main classes
    'ModelManager',
    
    # Constants
    'DEFAULT_MODELS',
    'DEFAULT_HF_MODELS',
    
    # Core functions
    'get_models_dir',
    'get_default_model',
    'set_default_model',
    'get_models',
    'install_model',
    'list_installed_models',
    'get_model_metadata',
    'update_models_metadata',
    
    # Hugging Face integration
    'load_huggingface_models_from_cache',
    'search_huggingface_models',
    'interactive_model_search',
    'update_models_from_huggingface',
    'update_huggingface_models_cache',
    
    # Ollama integration
    'load_ollama_models_from_cache',
    'update_models_from_ollama',
    'update_ollama_models_cache',
    'list_ollama_models',
    'install_ollama_model',
]

# Initialize the default model manager instance
model_manager = ModelManager()
