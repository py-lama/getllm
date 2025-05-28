#!/usr/bin/env python3
"""
Test script for the integrated model scrapers
"""

import os
import sys
import json
from getllm.models import update_huggingface_models_cache, update_models_from_ollama, update_models_metadata
from getllm.models import load_huggingface_models_from_cache, load_ollama_models_from_cache

def test_huggingface_scraper():
    print("\nud83dudd0d Testing Hugging Face Models Scraper Integration...")
    
    # Update the HF models cache
    print("Updating Hugging Face models cache (limit: 20)...")
    success = update_huggingface_models_cache(limit=20)
    
    if success:
        print("u2705 Successfully updated Hugging Face models cache")
    else:
        print("u274c Failed to update Hugging Face models cache")
    
    # Load models from cache
    hf_models = load_huggingface_models_from_cache()
    print(f"Loaded {len(hf_models)} models from Hugging Face cache")
    
    # Display a few models
    if hf_models:
        print("\nSample Hugging Face models:")
        for i, model in enumerate(hf_models[:5], 1):
            print(f"{i}. {model.get('name', model.get('id', 'Unknown'))} - {model.get('description', '')[:50]}...")
    
    return success

def test_ollama_scraper():
    print("\nud83dudd0d Testing Ollama Models Scraper Integration...")
    
    # Update the Ollama models
    print("Updating Ollama models (limit: 20)...")
    models = update_models_from_ollama(save_to_cache=True, limit=20)
    
    if models:
        print(f"u2705 Successfully retrieved {len(models)} Ollama models")
    else:
        print("u274c Failed to retrieve Ollama models")
    
    # Load models from cache
    ollama_models = load_ollama_models_from_cache()
    print(f"Loaded {len(ollama_models)} models from Ollama cache")
    
    # Display a few models
    if ollama_models:
        print("\nSample Ollama models:")
        for i, model in enumerate(ollama_models[:5], 1):
            print(f"{i}. {model.get('name', 'Unknown')} - {model.get('description', '')[:50]}...")
    
    return bool(models)

def test_models_metadata():
    print("\nud83dudd0d Testing Combined Models Metadata...")
    
    # Update the models metadata
    print("Updating models metadata...")
    success = update_models_metadata()
    
    if success:
        print("u2705 Successfully updated models metadata")
    else:
        print("u274c Failed to update models metadata")
    
    # Load the metadata file
    metadata_path = os.path.join(os.path.dirname(os.path.abspath(os.path.dirname(__file__))), 
                               'getllm', 'models_metadata.json')
    
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            print(f"\nMetadata summary:")
            print(f"Total models: {metadata.get('total_models', 0)}")
            print(f"Ollama models: {metadata.get('ollama_models', 0)}")
            print(f"Hugging Face models: {metadata.get('huggingface_models', 0)}")
            
            return True
        except Exception as e:
            print(f"Error loading metadata: {e}")
            return False
    else:
        print(f"Metadata file not found at {metadata_path}")
        return False

def main():
    print("ud83dude80 Testing Integrated Model Scrapers")
    
    # Test Hugging Face scraper
    hf_success = test_huggingface_scraper()
    
    # Test Ollama scraper
    ollama_success = test_ollama_scraper()
    
    # Test models metadata
    metadata_success = test_models_metadata()
    
    # Print summary
    print("\nud83dudccb Test Summary:")
    print(f"Hugging Face Scraper: {'u2705 Success' if hf_success else 'u274c Failed'}")
    print(f"Ollama Scraper: {'u2705 Success' if ollama_success else 'u274c Failed'}")
    print(f"Models Metadata: {'u2705 Success' if metadata_success else 'u274c Failed'}")

if __name__ == "__main__":
    main()
