import sys
import subprocess
import os
import shutil

# --- AUTO ENV & DEPENDENCY SETUP ---
REQUIRED_PACKAGES = ["requests", "bs4", "python-dotenv"]
IMPORT_NAMES = ["requests", "bs4", "dotenv"]  # Correct import for python-dotenv is 'dotenv'
VENV_DIR = os.path.join(os.path.dirname(__file__), ".venv")

# 1. Create venv if missing
if not os.path.isdir(VENV_DIR):
    subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True)
    print(f"Created virtual environment: {VENV_DIR}")

# 2. Activate venv for subprocess installs (current process may not inherit, but subprocess installs will work)
def _venv_python():
    if os.name == "nt":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    else:
        return os.path.join(VENV_DIR, "bin", "python")

# 3. Install missing packages
missing = []
for pkg, imp in zip(REQUIRED_PACKAGES, IMPORT_NAMES):
    try:
        __import__(imp)
    except ImportError:
        missing.append(pkg)
if missing:
    print(f"Installing missing packages: {', '.join(missing)}")
    subprocess.run([_venv_python(), "-m", "pip", "install"] + missing, check=True)
    print("Required dependencies installed. Please restart the script.")
    sys.exit(0)
# --- END AUTO ENV & DEPENDENCY SETUP ---

import subprocess
import os
import json
from pathlib import Path
import dotenv
import requests
import re
from bs4 import BeautifulSoup

def get_models_dir():
    env_path = Path(__file__).parent / ".env"
    example_env_path = Path(__file__).parent / ".env.example"
    env = {}
    if env_path.exists():
        env = dotenv.dotenv_values(env_path)
    elif example_env_path.exists():
        env = dotenv.dotenv_values(example_env_path)
    return env.get("MODELS_DIR", "./models")

def get_default_model():
    env_path = Path(__file__).parent / ".env"
    example_env_path = Path(__file__).parent / ".env.example"
    env = {}
    if env_path.exists():
        env = dotenv.dotenv_values(env_path)
    elif example_env_path.exists():
        env = dotenv.dotenv_values(example_env_path)
    return env.get("OLLAMA_MODEL", "")

def set_default_model(model_name):
    env_path = Path(__file__).parent / ".." / ".env"
    example_env_path = Path(__file__).parent / ".." / "env.example"
    # Jeśli .env nie istnieje, kopiuj z env.example
    if not env_path.exists() and example_env_path.exists():
        shutil.copy(str(example_env_path), str(env_path))
    lines = []
    found = False
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("OLLAMA_MODEL="):
                    lines.append(f"OLLAMA_MODEL={model_name}\n")
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.append(f"OLLAMA_MODEL={model_name}\n")
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"Ustawiono OLLAMA_MODEL={model_name} jako domyślny w .env")

DEFAULT_MODELS = [
    {"name": "tinyllama:1.1b", "size": "1.1B", "desc": "TinyLlama 1.1B - szybki, mały model"},
    {"name": "codellama:7b", "size": "7B", "desc": "CodeLlama 7B - kodowanie, Meta"},
    {"name": "wizardcoder:7b-python", "size": "7B", "desc": "WizardCoder 7B Python"},
    {"name": "deepseek-coder:6.7b", "size": "6.7B", "desc": "Deepseek Coder 6.7B"},
    {"name": "codegemma:2b", "size": "2B", "desc": "CodeGemma 2B - Google"},
    {"name": "phi:2.7b", "size": "2.7B", "desc": "Microsoft Phi-2 2.7B"},
    {"name": "stablelm-zephyr:3b", "size": "3B", "desc": "StableLM Zephyr 3B"},
    {"name": "mistral:7b", "size": "7B", "desc": "Mistral 7B"},
    {"name": "qwen:7b", "size": "7B", "desc": "Qwen 7B"},
    {"name": "gemma:7b", "size": "7B", "desc": "Gemma 7B"},
    {"name": "gemma:2b", "size": "2B", "desc": "Gemma 2B"}
]

MODELS_JSON = "models.json"

def save_models_to_json(models=DEFAULT_MODELS, file_path=None):
    if file_path is None:
        models_dir = get_models_dir()
        Path(models_dir).mkdir(parents=True, exist_ok=True)
        file_path = os.path.join(models_dir, MODELS_JSON)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(models, f, ensure_ascii=False, indent=2)

def load_models_from_json(file_path=None):
    if file_path is None:
        models_dir = get_models_dir()
        file_path = os.path.join(models_dir, MODELS_JSON)
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                models = json.load(f)
                return models
        except Exception as e:
            print(f"Błąd ładowania JSON: {e}")
    return DEFAULT_MODELS

def get_models():
    models = load_models_from_json()
    return models

def install_model(model_name):
    try:
        result = subprocess.run(["ollama", "pull", model_name], check=True)
        print(f"Model {model_name} został pobrany.")
        return True
    except Exception as e:
        print(f"Błąd pobierania modelu {model_name}: {e}")
        return False

def list_installed_models():
    try:
        output = subprocess.check_output(["ollama", "list"]).decode()
        print("\nZainstalowane modele:")
        for line in output.strip().split("\n")[1:]:
            print("  ", line)
    except Exception as e:
        print("Nie można pobrać listy zainstalowanych modeli (ollama list):", e)

def update_models_from_ollama():
    """
    Fetch the latest coding-related models up to 7B from the Ollama library web page
    and update the local models.json file.
    """
    import requests
    import re
    from bs4 import BeautifulSoup
    import json
    import os
    
    MODELS_HTML_URL = "https://ollama.com/library"
    MODELS_JSON_PATH = os.getenv("MODELS_JSON", "models.json")
    
    try:
        response = requests.get(MODELS_HTML_URL, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all model blocks (h2 headers and following description)
        model_blocks = []
        for h2 in soup.find_all('h2'):
            name = h2.text.strip().lower()
            desc = h2.find_next_sibling('p')
            desc_text = desc.text.strip() if desc else ""
            # Find parameter sizes in description or nearby text
            sizes = re.findall(r'(\d+(?:\.\d+)?)([bm])', desc_text + name)
            sizes = [float(num) for num, unit in sizes if unit == 'b' and float(num) <= 7]
            # Heuristic: filter coding models
            if any(code in name for code in ["code", "coder", "llama", "phi", "gemma", "deepseek", "smollm", "stablelm", "tinyllama", "exaone", "wizard"]):
                if sizes:
                    model_blocks.append({
                        "name": name,
                        "desc": desc_text,
                        "sizes": sizes
                    })
        # Fallback: if no models found, skip update
        if not model_blocks:
            print("Nie znaleziono modeli do zaktualizowania.")
            return
        # Convert to simple list for JSON
        models_list = []
        for m in model_blocks:
            for sz in m["sizes"]:
                models_list.append({
                    "name": m["name"],
                    "size_b": sz,
                    "desc": m["desc"]
                })
        # Save to models.json
        with open(MODELS_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(models_list, f, ensure_ascii=False, indent=2)
        print("Models updated from Ollama.")
    except Exception as e:
        print(f"Error updating from ollama.com: {e}")


class ModelManager:
    """
    Class for managing LLM models in the PyLLM system.
    Provides methods for listing, installing, and using models.
    """
    
    def __init__(self):
        self.default_model = get_default_model() or "llama3"
        self.models = self.get_available_models()
    
    def get_available_models(self):
        """
        Get a list of available models from the models.json file or default list.
        """
        return get_models()
    
    def list_models(self):
        """
        Return a list of available models.
        """
        return self.models
    
    def get_model_info(self, model_name):
        """
        Get information about a specific model.
        """
        for model in self.models:
            if model.get("name") == model_name:
                return model
        return None
    
    def install_model(self, model_name):
        """
        Install a model using Ollama.
        """
        return install_model(model_name)
    
    def list_installed_models(self):
        """
        List models that are currently installed.
        """
        try:
            output = subprocess.check_output(["ollama", "list"]).decode()
            models = []
            for line in output.strip().split("\n")[1:]:
                parts = line.split()
                if parts:
                    models.append({
                        "name": parts[0],
                        "size": parts[1] if len(parts) > 1 else "Unknown"
                    })
            return models
        except Exception as e:
            print(f"Error listing installed models: {e}")
            return []
    
    def set_default_model(self, model_name):
        """
        Set the default model to use.
        """
        set_default_model(model_name)
        self.default_model = model_name
        return True
    
    def get_default_model_name(self):
        """
        Get the name of the current default model.
        """
        return self.default_model
    
    def update_models_from_remote(self):
        """
        Update the models list from the Ollama library.
        """
        update_models_from_ollama()
        self.models = self.get_available_models()
        return True

if __name__ == "__main__":
    default_model = get_default_model()
    print("Available models:")
    models = get_models()
    for idx, m in enumerate(models, 1):
        print(f"{idx}. {m['name']} ({m.get('desc', '')})")
    if default_model:
        print(f"\nCurrent default model: {default_model}\n")
    else:
        print("\nNo default model set in .env\n")
    print("\nSaving list to models.json...")
    save_models_to_json(models)
    print("\nZainstalowane modele:")
    list_installed_models()
    print("\n--- Model Installation ---")
    print("Enter the model number to download, 'u' to update the model list from the Ollama project, or 'q' to exit.")
    while True:
        wyb = input("Choose model (number/'u'/'q'): ").strip()
        if wyb.lower() == 'q':
            print("Done.")
            break
        if wyb.lower() == 'u':
            update_models_from_ollama()
            models = get_models()
            for idx, m in enumerate(models, 1):
                print(f"{idx}. {m['name']} ({m.get('desc', '')})")
            continue
        if wyb.isdigit() and 1 <= int(wyb) <= len(models):
            model_name = models[int(wyb) - 1]["name"]
            # Check if the model is installed
            installed = False
            try:
                output = subprocess.check_output(["ollama", "list"]).decode()
                installed = any(model_name in line for line in output.strip().split("\n")[1:])
            except Exception:
                pass
            if not installed:
                ok = install_model(model_name)
                if not ok:
                    continue
            set_default_model(model_name)
        else:
            print("Invalid choice.")
