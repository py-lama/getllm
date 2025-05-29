#!/usr/bin/env python3
"""
Test script for default model functionality.
"""
import sys
import json
from pathlib import Path
from getllm.models import get_default_model, set_default_model
from getllm.ollama.api import get_ollama_integration

def test_default_model():
    """Test getting and setting the default model."""
    # Test setting a default model
    test_model = "llama2"
    print(f"Setting default model to: {test_model}")
    set_default_model(test_model, 'ollama')
    
    # Test getting the default model
    model_info = get_default_model()
    print(f"Retrieved default model: {model_info}")
    
    # Test with Ollama integration
    print("\nTesting Ollama integration:")
    runner = get_ollama_integration(model=model_info)
    print(f"Ollama runner created with model: {runner.model}")
    
    # List installed models
    try:
        installed_models = runner.list_installed_models()
        print("\nInstalled models:")
        for model in installed_models:
            print(f"- {model.get('name', 'unknown')}")
    except Exception as e:
        print(f"Error listing models: {e}")
    
    # Check if the default model is installed
    model_installed = any(m.get('name', '').startswith(model_info) for m in installed_models)
    print(f"\nIs default model '{model_info}' installed? {model_installed}")
    
    if not model_installed:
        print("\nTo install the default model, run:")
        print(f"ollama pull {model_info}")

if __name__ == "__main__":
    test_default_model()
