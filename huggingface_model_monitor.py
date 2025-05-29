import json
import time
import logging
import random
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import requests
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('huggingface_monitor.log')
    ]
)
logger = logging.getLogger(__name__)

# Configuration
OUTPUT_DIR = Path("huggingface_models_data")
OUTPUT_DIR.mkdir(exist_ok=True)
POLL_INTERVAL = 3600  # 1 hour in seconds (HF has rate limits)
BASE_URL = "https://huggingface.co"
SEARCH_URL = f"{BASE_URL}/models-llm"

# Common coding-related tags to filter models
CODING_TAGS = [
    'code', 'coding', 'programming', 'python', 'javascript', 'java', 'c++', 'c#', 'go', 'rust',
    'typescript', 'ruby', 'php', 'swift', 'kotlin', 'scala', 'haskell', 'ocaml', 'lua', 'perl',
    'programming-language', 'code-generation', 'code-completion', 'code-search', 'code-search-net',
    'code-translation', 'code2vec', 'codebert', 'codet5', 'codegen', 'incoder', 'polycoder',
    'star-coder', 'wizardcoder', 'llama-coder', 'replit-code', 'codegpt', 'codex', 'copilot',
    'github-copilot', 'santacoder', 'bigcode', 'code-llama', 'deepseek-coder', 'starcoder',
    'wizardlm', 'phind-codellama', 'magicoder', 'deepseek-ai', 'codefuse-ai', 'codebooga',
    'codeup-llm', 'codegeex', 'codegpt2', 'codegpt-java', 'codegpt-js', 'codegpt-py',
    'codegpt-rb', 'codegpt-ts', 'codegpt2-python', 'codegpt2-java', 'codegpt2-javascript',
    'codegpt2-typescript', 'codegpt2-ruby', 'codegpt2-php', 'codegpt2-go', 'codegpt2-rust',
    'codegpt2-cpp', 'codegpt2-csharp', 'codegpt2-swift', 'codegpt2-kotlin', 'codegpt2-scala',
    'codegpt2-haskell', 'codegpt2-ocaml', 'codegpt2-lua', 'codegpt2-perl'
]

def get_session() -> requests.Session:
    """Create and return a requests session with custom headers."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://huggingface.co/',
        'DNT': '1',
    })
    return session

def is_coding_related(model_data: Dict[str, Any]) -> bool:
    """Check if a model is related to coding based on its metadata."""
    # Check model name
    model_name = model_data.get('modelId', '').lower()
    if any(tag in model_name for tag in CODING_TAGS):
        return True
    
    # Check model tags
    tags = model_data.get('tags', [])
    if any(isinstance(tag, str) and any(code_tag in tag.lower() for code_tag in CODING_TAGS) for tag in tags):
        return True
    
    # Check model description
    description = model_data.get('description', '').lower()
    if any(tag in description for tag in CODING_TAGS):
        return True
    
    return False

def scrape_hf_models(session: requests.Session, limit: int = 100) -> List[Dict[str, Any]]:
    """Scrape coding-related models from Hugging Face."""
    logger.info("Scraping Hugging Face for coding-related models...")
    
    try:
        # Add a small delay to be polite
        time.sleep(random.uniform(2, 5))
        
        # First, get the CSRF token
        response = session.get(BASE_URL)
        response.raise_for_status()
        csrf_token = None
        
        # Try to extract CSRF token from HTML
        if '<meta name="csrf-token"' in response.text:
            csrf_token = response.text.split('<meta name="csrf-token" content="')[1].split('"')[0]
        
        # Prepare the API request
        headers = {
            'Content-Type': 'application/json',
            'Referer': SEARCH_URL,
            'X-Requested-With': 'XMLHttpRequest',
        }
        
        if csrf_token:
            headers['X-CSRF-Token'] = csrf_token
        
        # Make the search request
        search_params = {
            'search': 'code',
            'sort': 'downloads',
            'direction': '-1',
            'limit': limit,
            'full': 'true',
            'config': 'true',
        }
        
        response = session.get(
            f"{BASE_URL}/api/models-llm",
            params=search_params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        models = data.get('models', [])
        
        if not models:
            logger.warning("No models found in the API response.")
            return []
        
        # Filter for coding-related models
        coding_models = [
            model for model in models 
            if is_coding_related(model)
        ]
        
        logger.info(f"Found {len(coding_models)} coding-related models out of {len(models)} total models.")
        
        # Get additional details for each model
        detailed_models = []
        for model in coding_models[:50]:  # Limit to top 50 to avoid rate limiting
            try:
                model_id = model.get('modelId')
                if not model_id:
                    continue
                    
                # Get model details
                model_url = f"{BASE_URL}/api/models/{model_id}"
                model_response = session.get(model_url, timeout=30)
                model_response.raise_for_status()
                model_details = model_response.json()
                
                # Extract relevant information
                model_info = {
                    'id': model_id,
                    'author': model.get('author'),
                    'downloads': model.get('downloads', 0),
                    'likes': model.get('likes', 0),
                    'tags': model.get('tags', []),
                    'pipeline_tag': model.get('pipeline_tag', ''),
                    'last_modified': model.get('lastModified'),
                    'card_data': model.get('cardData', {}),
                    'siblings': model_details.get('siblings', []),
                    'config': model_details.get('config', {}),
                    'model_type': model_details.get('model_type', ''),
                    'scraped_at': datetime.now().isoformat()
                }
                
                detailed_models.append(model_info)
                
                # Be nice to the server
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                logger.error(f"Error processing model {model.get('modelId', 'unknown')}: {e}")
                continue
        
        return detailed_models
        
    except requests.RequestException as e:
        logger.error(f"Error fetching from Hugging Face: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return []

def save_models_data(models: List[Dict[str, Any]]) -> bool:
    """Save models data to a JSON file with timestamp."""
    if not models:
        logger.warning("No models to save.")
        return False
        
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = OUTPUT_DIR / f"huggingface_coding_models_{timestamp}.json"
        
        # Ensure output directory exists
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # Save to JSON file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'model_count': len(models),
                'models': models
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(models)} coding-related models to {filename}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving models data: {e}", exc_info=True)
        return False

def main():
    """Main function to run the Hugging Face model monitor."""
    logger.info("Starting Hugging Face coding models monitor...")
    
    # Create a session for making requests
    session = get_session()
    
    try:
        while True:
            start_time = time.time()
            
            # Scrape models
            models = scrape_hf_models(session)
            
            if models:  # Only save if we got some models
                save_models_data(models)
            else:
                logger.warning("No coding-related models were found in this iteration.")
            
            # Calculate time to sleep (account for time taken to scrape)
            elapsed = time.time() - start_time
            sleep_time = max(3600, POLL_INTERVAL - elapsed)  # At least 1 hour between scrapes
            
            logger.info(f"Waiting {sleep_time/3600:.1f} hours until next update...")
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        logger.info("\nMonitoring stopped by user.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        # Clean up the session
        session.close()
        logger.info("Session closed.")

if __name__ == "__main__":
    print("Starting Hugging Face coding models monitor...")
    print("This will monitor for new and updated coding-related models.")
    print(f"Data will be saved to: {OUTPUT_DIR.absolute()}")
    print("Press Ctrl+C to stop monitoring.\n")
    
    main()
