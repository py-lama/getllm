"""
Hugging Face model integration for PyLLM.
"""

import os
import re
import json
import logging
import requests
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from bs4 import BeautifulSoup
from tqdm import tqdm

from .constants import (
    get_models_dir,
    get_hf_models_cache_path,
    DEFAULT_HF_MODELS
)

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
    try:
        # Create models directory if it doesn't exist
        cache_dir = os.path.dirname(get_hf_models_cache_path())
        os.makedirs(cache_dir, exist_ok=True)
        
        # Try to use the Hugging Face API first
        try:
            # Use the API to search for GGUF models
            api_url = "https://huggingface.co/api/models"
            params = {
                'search': 'GGUF',
                'sort': 'downloads',
                'direction': '-1',
                'limit': min(limit, 100),  # API has a max limit
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
                
            if models:
                # Save to cache
                with open(get_hf_models_cache_path(), 'w', encoding='utf-8') as f:
                    json.dump(models, f, indent=2, ensure_ascii=False)
                return True, f"Successfully updated {len(models)} models from Hugging Face API"
                
        except Exception as api_error:
            logger.warning(f"HF API request failed, falling back to web scraping: {api_error}")
        
        # Fall back to web scraping if API fails
        try:
            # Scrape the Hugging Face models page for GGUF models
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
                
                # Get model details
                model_url = f"https://huggingface.co/api/models/{model_id}"
                model_resp = requests.get(model_url, headers=HEADERS, timeout=10)
                
                if model_resp.status_code == 200:
                    model_data = model_resp.json()
                    
                    # Extract relevant information
                    model_info = {
                        'id': model_id,
                        'name': model_data.get('modelId', ''),
                        'author': model_data.get('author', ''),
                        'description': model_data.get('cardData', {}).get('description', ''),
                        'tags': model_data.get('tags', []),
                        'downloads': model_data.get('downloads', 0),
                        'likes': model_data.get('likes', 0),
                        'last_updated': model_data.get('lastModified'),
                        'model_type': next((tag for tag in model_data.get('tags', []) 
                                          if tag in ['llama', 'mistral', 'falcon', 'gpt2']), '')
                    }
                    
                    # Try to get model size if available
                    model_info['size'] = extract_model_size(model_info)
                    
                    models.append(model_info)
                    
            except Exception as e:
                logger.debug(f"Error processing model card: {e}")
                continue
        
        # Save to cache
        cache_path = get_hf_models_cache_path()
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(models, f, indent=2, ensure_ascii=False)
        
        return True, f"Successfully updated {len(models)} models in cache"
        
    except Exception as e:
        error_msg = f"Error updating Hugging Face models cache: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def extract_model_size(model_info: Dict) -> str:
    """Extract model size from model info."""
    # Check if size is in the name
    name = model_info.get('name', '').lower()
    for size in ['7b', '13b', '20b', '30b', '65b', '70b']:
        if size in name:
            return size.upper()
    
    # Check if size is in the description
    desc = model_info.get('description', '').lower()
    for size in ['7b', '13b', '20b', '30b', '65b', '70b']:
        if size in desc:
            return size.upper()
    
    # Check if size is in the tags
    for tag in model_info.get('tags', []):
        if 'b' in tag.lower() and any(c.isdigit() for c in tag):
            return tag.upper()
    
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
