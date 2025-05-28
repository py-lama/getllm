#!/usr/bin/env python3
"""
Fix for the build process in getllm.
This script modifies the Poetry build process to handle path issues.
"""
import os
import sys
import shutil
from pathlib import Path
import subprocess

def fix_build_environment():
    """Fix the build environment to ensure proper paths are used."""
    print("Fixing build environment for getllm...")
    
    # Get the project root directory
    project_root = Path(__file__).parent.absolute()
    
    # Create a .env file with the correct paths if it doesn't exist
    env_file = project_root / ".env"
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write(f"PYTHONPATH={project_root}\n")
            f.write(f"MODELS_DIR={project_root}/models\n")
            f.write("OLLAMA_MODEL=llama3\n")
        print(f"Created .env file at {env_file}")
    
    # Clean up any previous build artifacts
    build_dir = project_root / "build"
    dist_dir = project_root / "dist"
    egg_info_dir = project_root / "getllm.egg-info"
    
    for dir_path in [build_dir, dist_dir, egg_info_dir]:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"Removed {dir_path}")
    
    # Create a clean venv for building
    venv_dir = project_root / "build_venv"
    if venv_dir.exists():
        shutil.rmtree(venv_dir)
    
    print("Creating a clean virtual environment for building...")
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
    
    # Determine the pip path
    pip_path = venv_dir / "bin" / "pip" if os.name != "nt" else venv_dir / "Scripts" / "pip.exe"
    
    # Install build dependencies
    print("Installing build dependencies...")
    subprocess.run([str(pip_path), "install", "--upgrade", "pip", "wheel", "setuptools", "poetry"], check=True)
    
    # Install project dependencies
    print("Installing project dependencies...")
    subprocess.run([str(pip_path), "install", "-e", "."], cwd=project_root, check=True)
    
    print("Build environment fixed successfully!")
    return True

def build_package():
    """Build the package using the fixed environment."""
    project_root = Path(__file__).parent.absolute()
    venv_dir = project_root / "build_venv"
    
    # Determine the python path
    python_path = venv_dir / "bin" / "python" if os.name != "nt" else venv_dir / "Scripts" / "python.exe"
    
    # Build the package
    print("Building the package...")
    result = subprocess.run(
        [str(python_path), "-m", "build", "--sdist", "--wheel", "."],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("Package built successfully!")
        print(f"Wheel file available in {project_root / 'dist'}")
        return True
    else:
        print("Failed to build the package:")
        print(result.stderr)
        return False

if __name__ == "__main__":
    if fix_build_environment():
        build_package()
