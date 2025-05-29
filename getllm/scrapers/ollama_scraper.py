"""
Ollama Models Fetcher

This module provides functionality to fetch model information from the Ollama API.
"""

import json
import time
import requests
from pathlib import Path
from typing import List, Dict, Optional, Any

# Ollama API endpoints
OLLAMA_API_BASE = "https://ollama.ai"
OLLAMA_LIBRARY_URL = f"{OLLAMA_API_BASE}/library"


class OllamaModelsScraper:
    """Fetcher for Ollama models using the Ollama API."""
    
    def __init__(self, api_base: str = None):
        """
        Initialize the OllamaModelsFetcher.
        
        Args:
            api_base: Base URL for the Ollama API. Defaults to the official API.
        """
        self.api_base = api_base or OLLAMA_API_BASE
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        pass
    
    def get_models(self) -> List[Dict[str, Any]]:
        """
        Get all available models from the Ollama library.
        
        Returns:
            List of model dictionaries with metadata.
        """
        try:
            response = requests.get(OLLAMA_LIBRARY_URL, timeout=30)
            response.raise_for_status()
            
            models_data = response.json()
            if not isinstance(models_data, list):
                print("Unexpected response format from Ollama API")
                return []
                
            models = []
            for model_data in models_data:
                try:
                    name = model_data.get('name', '')
                    if not name:
                        continue
                        
                    # Get tags for this model
                    tags_url = f"{OLLAMA_LIBRARY_URL}/{name}"
                    tags_response = requests.get(tags_url, timeout=30)
                    tags_data = tags_response.json() if tags_response.status_code == 200 else {}
                    
                    # Process each tag
                    for tag_name, tag_info in tags_data.get('tags', {}).items():
                        full_name = f"{name}:{tag_name}" if tag_name != 'latest' else name
                        
                        model_info = {
                            'name': name,
                            'tag': tag_name,
                            'full_name': full_name,
                            'source': 'ollama',
                            'url': f"https://ollama.ai/library/{name}",
                            'metadata': {
                                'size': tag_info.get('size', 0),
                                'digest': tag_info.get('digest', ''),
                                'last_modified': tag_info.get('last_modified', '')
                            }
                        }
                        
                        # Add model details if available
                        if 'details' in tag_info:
                            model_info['metadata'].update({
                                'architecture': tag_info['details'].get('architecture', ''),
                                'os': tag_info['details'].get('os', ''),
                                'created': tag_info['details'].get('created', '')
                            })
                        
                        models.append(model_info)
                        
                except Exception as e:
                    print(f"Error processing model {name}: {e}")
                    continue
                    
            return models
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching models from Ollama API: {e}")
            return []
    
    def save_models_to_file(self, file_path: str) -> bool:
        """
        Save the scraped models to a JSON file.
        
        Args:
            file_path: Path to save the models JSON file.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            models = self.get_models()
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(models, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving models to file: {e}")
            return False


def update_ollama_models_cache(file_path: Optional[str] = None) -> bool:
    """
    Update the local cache of Ollama models.
    
    Args:
        file_path: Optional path to save the cache file. If not provided,
                  will use the default cache path.
                  
    Returns:
        True if successful, False otherwise.
    """
    if file_path is None:
        # Create the cache directory if it doesn't exist
        cache_dir = os.path.join(os.path.expanduser('~'), '.getllm', 'cache')
        os.makedirs(cache_dir, exist_ok=True)
        file_path = os.path.join(cache_dir, 'ollama_models.json')
    
    try:
        with OllamaModelsScraper() as scraper:
            models = scraper.get_models()
            if not models:
                print("❌ No models found in the Ollama library")
                return False
                
            # Save the models to the cache file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(models, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Successfully updated Ollama models cache with {len(models)} models")
            return True
            
    except Exception as e:
        print(f"❌ Error updating Ollama models cache: {str(e)}")
        return False
    
    try:
        with OllamaModelsScraper() as scraper:
            return scraper.save_models_to_file(str(file_path))
    except Exception as e:
        print(f"Error updating Ollama models cache: {e}")
        return False
