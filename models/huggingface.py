"""
Hugging Face model integration for PyLLM.
"""

import os
import re
import json
import logging
import requests
from typing import List, Dict, Optional, Tuple, Union
from pathlib import Path

from bs4 import BeautifulSoup
from tqdm import tqdm

from .constants import (
    get_models_dir,
    get_hf_models_cache_path,
    get_ollama_models_cache_path,
    get_models_metadata_path,
    DEFAULT_HF_MODELS
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

# Headers to avoid 403 Forbidden errors
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def search_huggingface_models(query: str = None, limit: int = 20) -> List[Dict]:
    """
    Search for models on Hugging Face that match the given query.
    
    Args:
        query: The search query (e.g., "bielik"). If None, returns all models.
        limit: Maximum number of results to return.
        
    Returns:
        A list of dictionaries containing model information.
    """
    try:
        # First try to update from web to get fresh results
        success, _ = update_huggingface_models_cache(limit=50)
        
        # If web update failed, try to load from cache
        if not success:
            models = load_huggingface_models_from_cache()
            # If no cached models, use the default ones
            if not models:
                models = DEFAULT_HF_MODELS
        else:
            # Reload models after update
            models = load_huggingface_models_from_cache()
        
        # Filter by query if provided
        if query:
            query = query.lower()
            filtered_models = []
            for model in models:
                if (query in model.get('id', '').lower() or 
                    query in model.get('name', '').lower() or 
                    query in model.get('description', '').lower() or
                    any(query in str(tag).lower() for tag in model.get('tags', []))):
                    filtered_models.append(model)
            models = filtered_models
        
        return models[:limit]
        
    except Exception as e:
        logger.warning(f"Error searching Hugging Face models: {e}")
        # Fall back to default models if there's an error
        return [m for m in DEFAULT_HF_MODELS 
               if not query or 
               query.lower() in m.get('name', '').lower() or 
               query.lower() in m.get('description', '').lower()]

def update_huggingface_models_cache(limit: int = 50) -> Tuple[bool, str]:
    """
    Update the Hugging Face models cache by fetching from the HF website.
    
    Args:
        limit: Maximum number of models to fetch
        
    Returns:
        A tuple of (success, message)
    """
    def fetch_from_api() -> Tuple[bool, str, List[Dict]]:
        """Try to fetch models from Hugging Face API."""
        try:
            api_url = "https://huggingface.co/api/models"
            params = {
                'search': 'GGUF',
                'sort': 'downloads',
                'direction': '-1',
                'limit': min(limit, 100),
                'full': 'false'
            }
            
            response = requests.get(api_url, headers=HEADERS, params=params, timeout=30)
            response.raise_for_status()
            api_models = response.json()
            
            models = []
            for model in api_models:
                models.append({
                    'id': model.get('modelId', ''),
                    'name': model.get('modelId', '').split('/')[-1],
                    'author': model.get('author', ''),
                    'description': model.get('cardData', {}).get('description', ''),
                    'downloads': model.get('downloads', 0),
                    'likes': model.get('likes', 0),
                    'tags': model.get('tags', []) + (['gguf'] if 'gguf' not in model.get('tags', []) else [])
                })
            
            return True, f"Fetched {len(models)} models from API", models
            
        except Exception as e:
            logger.warning(f"HF API request failed: {e}")
            return False, f"API request failed: {e}", []
    
    def fetch_from_web() -> Tuple[bool, str, List[Dict]]:
        """Fallback to web scraping if API fails."""
        try:
            url = "https://huggingface.co/models?sort=trending&search=GGUF"
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            model_cards = soup.find_all('article', {'class': 'card'})
            
            models = []
            for card in tqdm(model_cards[:limit], desc="Fetching models"):
                try:
                    model_id = card.find('a')['href'].strip('/')
                    title = card.find('h4').text.strip()
                    
                    model_url = f"https://huggingface.co/api/models/{model_id}"
                    model_resp = requests.get(model_url, headers=HEADERS, timeout=10)
                    
                    if model_resp.status_code == 200:
                        model_data = model_resp.json()
                        
                        model_info = {
                            'id': model_id,
                            'name': model_data.get('modelId', '').split('/')[-1],
                            'author': model_data.get('author', ''),
                            'description': model_data.get('cardData', {}).get('description', ''),
                            'tags': model_data.get('tags', []),
                            'downloads': model_data.get('downloads', 0),
                            'likes': model_data.get('likes', 0),
                        }
                        
                        model_info['size'] = extract_model_size(model_info)
                        models.append(model_info)
                        
                except Exception as e:
                    logger.warning(f"Error processing model {model_id if 'model_id' in locals() else 'unknown'}: {e}")
                    continue
            
            if models:
                return True, f"Fetched {len(models)} models from web", models
            return False, "No models found on Hugging Face", []
            
        except Exception as e:
            logger.error(f"Web scraping failed: {e}")
            return False, f"Web scraping failed: {e}", []
    
    # Main function logic
    try:
        # Create cache directory if it doesn't exist
        cache_dir = os.path.dirname(get_hf_models_cache_path())
        os.makedirs(cache_dir, exist_ok=True)
        
        # Try API first
        success, message, models = fetch_from_api()
        
        # Fall back to web scraping if API fails
        if not success or not models:
            logger.warning(f"Falling back to web scraping: {message}")
            success, message, models = fetch_from_web()
        
        # If we have models, save them to cache
        if models:
            try:
                with open(get_hf_models_cache_path(), 'w', encoding='utf-8') as f:
                    json.dump(models, f, indent=2, ensure_ascii=False)
                return True, f"Successfully updated {len(models)} models in cache"
            except IOError as e:
                error_msg = f"Error writing to cache: {e}"
                logger.error(error_msg)
                return False, error_msg
        
        return success, message or "No models found"
        
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        logger.error(error_msg)
        return False, error_msg

def load_huggingface_models_from_cache() -> List[Dict]:
    """
    Load Hugging Face models from the cache file.
    
    Returns:
        A list of Hugging Face models, or an empty list if the cache file doesn't exist or is invalid.
    """
    try:
        cache_path = get_hf_models_cache_path()
        if not cache_path or not os.path.exists(cache_path):
            logger.debug("No Hugging Face cache file found")
            return []
            
        with open(cache_path, 'r', encoding='utf-8') as f:
            models = json.load(f)
            if not isinstance(models, list):
                logger.warning("Invalid cache format: expected a list of models")
                return []
            
            # Ensure all models have required fields
            valid_models = []
            for model in models:
                if not isinstance(model, dict):
                    continue
                if 'id' not in model or not model['id']:
                    continue
                if 'name' not in model or not model['name']:
                    model['name'] = model['id'].split('/')[-1]
                if 'tags' not in model:
                    model['tags'] = []
                valid_models.append(model)
                
            return valid_models
            
    except Exception as e:
        logger.warning(f"Error loading Hugging Face models from cache: {e}")
        return []

def extract_model_size(model_info: Dict) -> str:
    """Extract model size from model info."""
    if not isinstance(model_info, dict):
        return 'Unknown'
        
    try:
        # Try to extract size from model name or tags
        name = str(model_info.get('name', '')).lower()
        tags = [str(tag).lower() for tag in model_info.get('tags', []) if tag]
        
        # Check common size patterns in name
        for pattern in [r'(\d+\.?\d*)(b|B)', r'(\d+\.?\d*)(m|M)']:
            match = re.search(pattern, name)
            if match:
                return f"{match.group(1)}{match.group(2).upper()}"
        
        # Check tags for size
        size_patterns = ['7b', '13b', '20b', '65b', '70b', '1.1b', '3b', '6b', '12b']
        for pattern in size_patterns:
            if any(pattern in tag for tag in tags):
                return pattern.upper()
            if pattern in name:
                return pattern.upper()
        
        # Try to get size from model ID
        model_id = str(model_info.get('id', '')).lower()
        for pattern in size_patterns:
            if pattern in model_id:
                return pattern.upper()
                
    except Exception as e:
        logger.warning(f"Error extracting model size: {e}")
    
    return 'Unknown'

def interactive_model_search(query: str = None, check_ollama: bool = True) -> Optional[str]:
    """
    Interactive search for models on Hugging Face.
    
    Args:
        query: The search query (e.g., "bielik"). If None, prompts the user.
        check_ollama: Whether to check if Ollama is installed.
        
    Returns:
        The selected model ID or None if cancelled.
    """
    try:
        from simple_term_menu import TerminalMenu
    except ImportError:
        logger.error("simple_term_menu package is required for interactive search")
        return None
    
    if check_ollama:
        # Check if Ollama is installed
        try:
            from getllm.ollama import OllamaServer
            if not OllamaServer().is_ollama_installed():
                print("Ollama is not installed. Please install Ollama first.")
                return None
        except Exception as e:
            logger.error(f"Error checking Ollama installation: {e}")
            return None
    
    # If no query provided, prompt the user
    if not query:
        query = input("Enter search query (or press Enter to list all models): ")
    
    # Search for models
    models = search_huggingface_models(query)
    
    if not models:
        print("No models found matching your query.")
        return None
    
    # Create menu options
    options = []
    for i, model in enumerate(models, 1):
        size = model.get('size', 'N/A')
        downloads = model.get('downloads', 0)
        desc = model.get('description', 'No description')[:60] + '...' if model.get('description') else 'No description'
        options.append(f"{i}. {model['name']} ({size}) - {desc} (📥 {downloads})")
    
    # Add exit option
    options.append("Exit")
    
    # Show menu
    menu = TerminalMenu(
        options,
        title=f"Found {len(models)} models. Select one to install:",
        menu_cursor_style=("fg_green", "bold"),
        menu_highlight_style=("fg_cyan", "bold")
    )
    
    selected_index = menu.show()
    
    # Handle selection
    if selected_index is None or selected_index >= len(models):
        return None
    
    return models[selected_index]['id']
