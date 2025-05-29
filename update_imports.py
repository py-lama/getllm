#!/usr/bin/env python3
"""
Script to update imports after removing duplicate files.
"""
import os
import re
from pathlib import Path

# Files that need to be updated
FILES_TO_UPDATE = [
    "test_default_model.py",
    "test_installation_options.sh",
    "getllm/interactive_cli.py",
    "getllm/__init__.py",
    "getllm/cli.py",
    "getllm/models.py",
    "tests/test_ollama_search.py",
    "tests/ollama/test_api.py",
    "tests/test_ollama_integration.py"
]

# Mapping of old imports to new ones
IMPORT_MAPPING = {
    "from getllm.ollama_integration": "from getllm.ollama.api",
    "from .ollama_integration": "from .ollama.api"
}

def update_file(file_path):
    """Update imports in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        updated = False
        for old, new in IMPORT_MAPPING.items():
            if old in content:
                content = content.replace(old, new)
                updated = True
        
        if updated:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to update all files."""
    base_dir = Path(__file__).parent
    updated_count = 0
    
    for file_path in FILES_TO_UPDATE:
        full_path = base_dir / file_path
        if full_path.exists():
            if update_file(full_path):
                updated_count += 1
    
    print(f"\nUpdated {updated_count} files.")

if __name__ == "__main__":
    main()
