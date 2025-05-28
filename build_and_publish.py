#!/usr/bin/env python3
"""
Non-interactive build and publish script for getllm package.
This script automatically builds and publishes the package without asking for confirmation.
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
    """Ensure version is consistent across all files and increment patch if needed."""
    # Read version from pyproject.toml
    version = None
    pyproject_path = "pyproject.toml"
    setup_path = "setup.py"
    
    # Get current version from pyproject.toml
    with open(pyproject_path, "r") as f:
        for line in f:
            if line.strip().startswith("version = "):
                version = line.strip().split("=")[1].strip().strip('"').strip("'")
                break
    if not version:
        print("Could not find version in pyproject.toml")
        return False
    print(f"Found version in pyproject.toml: {version}")

    # Get current version in setup.py
    setup_version = None
    if os.path.exists(setup_path):
        with open(setup_path, "r") as f:
            for line in f:
                if line.strip().startswith("version=") or line.strip().startswith("version ="):
                    setup_version = line.split("=")[1].split(",")[0].strip().strip('"').strip("'")
                    break
    # If versions match, increment patch version
    if setup_version == version:
        print("setup.py version matches pyproject.toml. Incrementing patch version...")
        major, minor, patch = map(int, version.split("."))
        patch += 1
        new_version = f"{major}.{minor}.{patch}"
        # Update pyproject.toml
        with open(pyproject_path, "r") as f:
            lines = f.readlines()
        with open(pyproject_path, "w") as f:
            for line in lines:
                if line.strip().startswith("version = "):
                    f.write(f'version = "{new_version}"\n')
                else:
                    f.write(line)
        # Update setup.py
        with open(setup_path, "r") as f:
            lines = f.readlines()
        with open(setup_path, "w") as f:
            for line in lines:
                if line.strip().startswith("version=") or line.strip().startswith("version ="):
                    prefix = line.split("=")[0]
                    f.write(f'{prefix}= "{new_version}",\n')
                else:
                    f.write(line)
        print(f"Incremented version to {new_version}")
    else:
        print("setup.py and pyproject.toml versions do not match or already updated.")
    return True

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
    
    # Upload to PyPI without asking
    print("\nAutomatically publishing to PyPI...")
    if not upload_to_pypi():
        return 1
    
    print(f"\nBuild and publish process completed for getllm!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
