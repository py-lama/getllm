import json
import time
import re
import requests
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote_plus
import random
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ollama_monitor.log')
    ]
)
logger = logging.getLogger(__name__)

# Set a custom user agent to avoid blocking
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Configuration
OUTPUT_DIR = Path("ollama_models_data")
OUTPUT_DIR.mkdir(exist_ok=True)
POLL_INTERVAL = 60  # seconds

def get_session():
    """Create and return a requests session with custom headers."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    return session

def scrape_models(session):
    """Scrape models from the Ollama library."""
    try:
        logger.info("Making request to Ollama library...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://ollama.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        response = session.get("https://ollama.com/library", headers=headers, timeout=30)
        response.raise_for_status()
        logger.info(f"Got response with status code: {response.status_code}")
        
        logger.info("Parsing HTML content...")
        soup = BeautifulSoup(response.text, 'lxml')
        models = []
        
        # Find all model list items with x-test-model attribute
        logger.debug("Searching for model list items...")
        model_items = soup.select('li[x-test-model]')
        logger.info(f"Found {len(model_items)} model items")
        
        if not model_items:
            logger.warning("No model items found! Dumping page content for debugging...")
            with open("debug_ollama_page.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            logger.info("Saved debug_ollama_page.html for inspection")
            return []
        
        for i, item in enumerate(model_items, 1):
            try:
                logger.debug(f"Processing model {i}/{len(model_items)}")
                
                # Extract model name from the h2 element
                h2 = item.select_one('h2')
                if not h2:
                    logger.debug(f"Skipping model {i} - no h2 found")
                    continue
                    
                model_name = h2.get_text(strip=True)
                if not model_name:
                    logger.debug(f"Skipping model {i} - no model name found")
                    continue
                    
                logger.debug(f"Found model: {model_name}")
                
                # Extract model URL
                model_url = ''
                link = item.find('a', href=True)
                if link and link.get('href', '').startswith('/library/'):
                    model_url = f"https://ollama.com{link['href']}"
                
                # Extract description - first p tag after h2
                description = ''
                desc_p = h2.find_next_sibling('p')
                if desc_p:
                    description = desc_p.get_text(strip=True)
                
                # Extract model sizes from spans with specific classes
                sizes = []
                size_spans = item.select('span.bg-gray-100, span.bg-gray-200')
                for span in size_spans:
                    size_text = span.get_text(strip=True)
                    if size_text and any(x in size_text.lower() for x in ['b', 'k', 'm', 'g']):
                        sizes.append(size_text)
                
                # Extract metadata (pulls, last updated, etc.)
                metadata = {}
                meta_div = item.select_one('div.flex.space-x-5')
                if meta_div:
                    for span in meta_div.find_all('span'):
                        text = span.get_text(strip=True)
                        if ':' in text:
                            key, value = text.split(':', 1)
                            metadata[key.strip().lower()] = value.strip()
                
                # Extract tags - look for spans with specific classes
                tags = []
                tag_elements = item.select('span.inline-flex.items-center.rounded-md')
                for tag in tag_elements:
                    tag_text = tag.get_text(strip=True)
                    if tag_text and tag_text not in sizes:  # Avoid duplicating size tags
                        tags.append(tag_text)
                
                model_data = {
                    'name': model_name,
                    'url': model_url,
                    'description': description or "No description",
                    'sizes': sizes,
                    'tags': tags,
                    'metadata': metadata
                }
                logger.debug(f"Collected model data: {model_data}")
                models.append(model_data)
                
            except Exception as e:
                logger.error(f"Error parsing model {i}: {e}", exc_info=True)
                continue
                
        logger.info(f"Successfully processed {len(models)} models")
        return models
        
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}", exc_info=True)
        return []
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return []

def get_models_fingerprint(models):
    """Create a fingerprint of the models data to detect changes."""
    if not models:
        return None
    
    def make_hashable(obj):
        if isinstance(obj, (str, int, float, bool, bytes)) or obj is None:
            return obj
        elif isinstance(obj, dict):
            return tuple(sorted((k, make_hashable(v)) for k, v in obj.items()))
        elif isinstance(obj, (list, tuple)):
            return tuple(make_hashable(x) for x in obj)
        else:
            return str(obj)
    
    # Create a consistent fingerprint based on model data
    fingerprint_data = []
    for model in sorted(models, key=lambda x: x.get('name', '').lower()):
        model_data = {
            'name': model.get('name', ''),
            'description': model.get('description', ''),
            'sizes': sorted(model.get('sizes', [])),
            'tags': sorted(model.get('tags', [])),
            'metadata': dict(sorted(model.get('metadata', {}).items()))
        }
        # Convert all data to hashable types
        fingerprint_data.append(make_hashable(model_data))
    return hash(tuple(fingerprint_data))

def save_models_data(models, prev_fingerprint=None):
    """Save models data to a JSON file with timestamp if data has changed."""
    if not models:
        logger.warning("No models to save.")
        return None, None
    
    # Sort models by name for consistent output
    sorted_models = sorted(models, key=lambda x: x.get('name', '').lower())
    current_fingerprint = get_models_fingerprint(sorted_models)
    
    # Only save if the data has changed
    if current_fingerprint and current_fingerprint != prev_fingerprint:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = OUTPUT_DIR / f"ollama_models_{timestamp}.json"
            
            # Ensure output directory exists
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            
            # Save to JSON file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'model_count': len(sorted_models),
                    'models': sorted_models
                }, f, indent=2, ensure_ascii=False, sort_keys=True)
            
            logger.info(f"Saved {len(sorted_models)} models to {filename}")
            return filename, current_fingerprint
            
        except Exception as e:
            logger.error(f"Error saving models data: {e}", exc_info=True)
    else:
        logger.info("No changes detected in model data, skipping save.")
    
    return None, current_fingerprint

def main():
    """Main function to run the Ollama model monitor."""
    logger.info("Starting Ollama model monitor...")
    
    # Create a session for making requests
    session = get_session()
    prev_fingerprint = None
    
    try:
        while True:
            start_time = time.time()
            
            # Scrape models
            logger.info("Scraping Ollama models...")
            models = scrape_models(session)
            
            if models:  # Only process if we got some models
                # Save models if they've changed
                filename, prev_fingerprint = save_models_data(models, prev_fingerprint)
                if filename:
                    logger.info(f"Changes detected, saved to {filename}")
            else:
                logger.warning("No models were scraped in this iteration.")
            
            # Calculate time to sleep (account for time taken to scrape)
            elapsed = time.time() - start_time
            sleep_time = max(1, POLL_INTERVAL - elapsed)
            
            if sleep_time > 0:
                logger.info(f"Waiting {sleep_time:.1f} seconds until next update...")
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
    print("Starting Ollama model monitor...")
    print(f"Data will be saved to: {OUTPUT_DIR.absolute()}")
    print("Press Ctrl+C to stop monitoring")
    main()
