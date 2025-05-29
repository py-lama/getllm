"""
Model management for PyLLM.
"""

import os
import logging
from typing import List, Dict, Optional, Any

from .utils import (
    get_models_dir,
    get_default_model,
    set_default_model,
    get_models,
    install_model,
    list_installed_models,
    get_model_metadata
)
from .huggingface import search_huggingface_models, interactive_model_search
from .ollama import update_ollama_models_cache, list_ollama_models, install_ollama_model

logger = logging.getLogger(__name__)

class ModelManager:
    """
    Class for managing LLM models in the PyLLM system.
    
    This class provides methods for listing, installing, and using models
    from various sources including Ollama and Hugging Face.
    """
    
    def __init__(self):
        """Initialize the ModelManager with default settings."""
        self.default_model = get_default_model() or "llama3"
        self.models = self.get_available_models()
    
    def get_available_models(self) -> List[Dict]:
        """
        Get a list of available models from the models.json file or default list.
        
        Returns:
            A list of dictionaries containing model information.
        """
        return get_models()
    
    def list_models(self) -> List[Dict]:
        """
        Return a list of available models.
        
        Returns:
            A list of dictionaries containing model information.
        """
        return self.models
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """
        Get information about a specific model.
        
        Args:
            model_name: The name of the model to get information about.
            
        Returns:
            A dictionary containing model information, or None if not found.
        """
        return get_model_metadata(model_name)
    
    def install_model(self, model_name: str) -> bool:
        """
        Install a model using Ollama.
        
        Args:
            model_name: The name of the model to install.
            
        Returns:
            True if installation was successful, False otherwise.
        """
        return install_model(model_name)
    
    def list_installed_models(self) -> List[str]:
        """
        List models that are currently installed.
        
        Returns:
            A list of installed model names.
        """
        return list_installed_models()
    
    def set_default_model(self, model_name: str) -> bool:
        """
        Set the default model to use.
        
        Args:
            model_name: The name of the model to set as default.
            
        Returns:
            True if successful, False otherwise.
        """
        if any(m['name'] == model_name for m in self.models):
            self.default_model = model_name
            return set_default_model(model_name)
        return False
    
    def get_default_model_name(self) -> str:
        """
        Get the name of the current default model.
        
        Returns:
            The name of the default model.
        """
        return self.default_model
    
    def update_models_from_remote(self, source: str = "ollama", 
                                query: str = None, 
                                interactive: bool = True) -> List[Dict]:
        """
        Update the models list from a remote source.
        
        Args:
            source: The source to update from ("ollama" or "huggingface").
            query: The search query for Hugging Face models.
            interactive: Whether to allow interactive selection for Hugging Face models.
            
        Returns:
            The updated list of models.
        """
        if source.lower() == "huggingface":
            return self.update_models_from_huggingface(query, interactive)
        elif source.lower() == "ollama":
            return self.update_models_from_ollama()
        else:
            logger.warning(f"Unknown source: {source}")
            return self.models
    
    def search_huggingface_models(self, query: str = None, limit: int = 20) -> List[Dict]:
        """
        Search for models on Hugging Face.
        
        Args:
            query: The search query.
            limit: Maximum number of results to return.
            
        Returns:
            A list of model dictionaries.
        """
        return search_huggingface_models(query, limit)
    
    def interactive_model_search(self, query: str = None) -> Optional[str]:
        """
        Interactive search for models on Hugging Face.
        
        Args:
            query: The search query.
            
        Returns:
            The selected model ID or None if cancelled.
        """
        return interactive_model_search(query, check_ollama=True)
    
    def update_models_from_huggingface(self, query: str = None, 
                                     interactive: bool = True) -> List[Dict]:
        """
        Update models from Hugging Face.
        
        Args:
            query: The search query.
            interactive: Whether to use interactive mode.
            
        Returns:
            The updated list of models.
        """
        from .huggingface import update_models_from_huggingface
        return update_models_from_huggingface(query, interactive)
    
    def update_models_from_ollama(self) -> List[Dict]:
        """
        Update models from Ollama.
        
        Returns:
            The updated list of models.
        """
        success, message = update_ollama_models_cache()
        if not success:
            logger.warning(f"Failed to update Ollama models: {message}")
        
        # Reload models
        self.models = self.get_available_models()
        return self.models
