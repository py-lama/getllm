#!/usr/bin/env python3
"""
Simplified build script for getllm package.
This script bypasses Poetry's build system and uses setuptools directly.
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build_artifacts():
    """Clean previous build artifacts."""
    print("Cleaning previous build artifacts...")
    for path in ["build", "dist", "getllm.egg-info"]:
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
                print(f"Removed directory: {path}")
            else:
                os.remove(path)
                print(f"Removed file: {path}")

def ensure_dependencies():
    """Ensure all required build dependencies are installed."""
    print("Installing build dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", 
                   "pip", "wheel", "setuptools", "twine"], check=True)

def update_version_files():
    """Ensure version is consistent across all files."""
    # Read version from pyproject.toml
    version = None
    with open("pyproject.toml", "r") as f:
        for line in f:
            if line.strip().startswith("version = "):
                version = line.strip().split("=")[1].strip().strip('"').strip("'")
                break
    
    if not version:
        print("Could not find version in pyproject.toml")
        return False
    
    print(f"Found version in pyproject.toml: {version}")
    
    # Update setup.py if it exists
    if os.path.exists("setup.py"):
        with open("setup.py", "r") as f:
            setup_content = f.read()
        
        if "version=" in setup_content:
            import re
            new_content = re.sub(r'version="[^"]*"', f'version="{version}"', setup_content)
            new_content = re.sub(r"version='[^']*'", f"version='{version}'", new_content)
            
            with open("setup.py", "w") as f:
                f.write(new_content)
            print(f"Updated version in setup.py to {version}")
    
    # Update __init__.py
    init_path = os.path.join("getllm", "__init__.py")
    if os.path.exists(init_path):
        with open(init_path, "r") as f:
            init_content = f.read()
        
        if "__version__" in init_content:
            import re
            new_content = re.sub(r'__version__ = "[^"]*"', f'__version__ = "{version}"', init_content)
            new_content = re.sub(r"__version__ = '[^']*'", f"__version__ = '{version}'", new_content)
            
            with open(init_path, "w") as f:
                f.write(new_content)
            print(f"Updated version in __init__.py to {version}")
    
    return version

def build_package():
    """Build the package using setuptools."""
    print("Building the package using setuptools...")
    try:
        # Build source distribution
        subprocess.run([sys.executable, "setup.py", "sdist"], check=True)
        
        # Build wheel
        subprocess.run([sys.executable, "setup.py", "bdist_wheel"], check=True)
        
        print("Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return False

def upload_to_pypi():
    """Upload the package to PyPI using twine."""
    print("Checking distribution files...")
    if not os.path.exists("dist") or not os.listdir("dist"):
        print("No distribution files found. Build failed or not run.")
        return False
    
    print("Found the following distribution files:")
    for file in os.listdir("dist"):
        print(f"  - {file}")
    
    print("\nUploading to PyPI...")
    try:
        subprocess.run([sys.executable, "-m", "twine", "upload", "dist/*"], check=True)
        print("Upload completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Upload failed: {e}")
        return False

def main():
    """Main build process."""
    # Get the current directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Clean previous build artifacts
    clean_build_artifacts()
    
    # Ensure dependencies
    ensure_dependencies()
    
    # Update version files
    version = update_version_files()
    if not version:
        print("Failed to update version files.")
        return 1
    
    # Build the package
    if not build_package():
        return 1
    
    # Ask if user wants to upload to PyPI
    print("\n")
    response = input("Do you want to upload to PyPI? (y/n): ")
    if response.lower() == "y":
        if not upload_to_pypi():
            return 1
    else:
        print("Skipping upload to PyPI.")
        print("You can upload manually with: python -m twine upload dist/*")
    
    print(f"\nBuild process completed for getllm {version}!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
