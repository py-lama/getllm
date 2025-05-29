"""
Ollama Models Scraper

This module provides functionality to scrape model information from the Ollama website.
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Optional, Any

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class OllamaModelsScraper:
    """Scraper for Ollama models."""
    
    BASE_URL = "https://ollama.ai/library"
    
    def __init__(self, headless: bool = True):
        """
        Initialize the OllamaModelsScraper.
        
        Args:
            headless: Whether to run the browser in headless mode.
        """
        self.headless = headless
        self.driver = None
    
    def __enter__(self):
        """Context manager entry."""
        self.setup_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def setup_driver(self):
        """Set up the Selenium WebDriver."""
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
    
    def close(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def get_models(self) -> List[Dict[str, Any]]:
        """
        Get all available models from the Ollama library.
        
        Returns:
            List of model dictionaries with metadata.
        """
        if not self.driver:
            self.setup_driver()
        
        models = []
        page = 1
        
        while True:
            url = f"{self.BASE_URL}?page={page}" if page > 1 else self.BASE_URL
            print(f"Fetching page {page}...")
            
            self.driver.get(url)
            
            # Wait for the models to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "model-item"))
                )
            except Exception as e:
                print(f"Error waiting for models to load on page {page}: {e}")
                break
            
            # Scroll to load all models (if needed)
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            while True:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Wait for content to load
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            # Parse the page with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            model_elements = soup.find_all('div', class_='model-item')
            
            if not model_elements:
                print(f"No more models found on page {page}")
                break
                
            print(f"Found {len(model_elements)} models on page {page}")
            
            # Process models on this page
            page_models = []
            for model_elem in model_elements:
                try:
                    # Extract model name and tag
                    name_elem = model_elem.find('h3')
                    if not name_elem:
                        continue
                        
                    name_parts = name_elem.text.strip().split(':')
                    name = name_parts[0].strip()
                    tag = name_parts[1].strip() if len(name_parts) > 1 else 'latest'
                    
                    # Extract model metadata
                    metadata = {
                        'name': name,
                        'tag': tag,
                        'full_name': f"{name}:{tag}",
                        'source': 'ollama',
                        'url': f"https://ollama.ai/library/{name}",
                        'metadata': {}
                    }
                    
                    # Extract description if available
                    desc_elem = model_elem.find('p')
                    if desc_elem:
                        metadata['description'] = desc_elem.text.strip()
                    
                    # Extract size if available
                    size_elem = model_elem.find('span', class_='size')
                    if size_elem:
                        metadata['size'] = size_elem.text.strip()
                    
                    # Extract pull count if available
                    pull_elem = model_elem.find('span', class_='pulls')
                    if pull_elem:
                        metadata['pulls'] = pull_elem.text.strip()
                    
                    page_models.append(metadata)
                    
                except Exception as e:
                    print(f"Error parsing model element: {e}")
                    continue
            
            models.extend(page_models)
            page += 1
            
            # Add a small delay between page requests
            time.sleep(1)
            
            # For testing, limit to first 3 pages
            if page > 3:  # Remove this in production
                print("Reached page limit for testing")
                break
                
        return models
    
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
        from ..utils.config import get_models_dir
        cache_dir = get_models_dir()
        cache_dir.mkdir(parents=True, exist_ok=True)
        file_path = cache_dir / "ollama_models.json"
    
    try:
        with OllamaModelsScraper() as scraper:
            return scraper.save_models_to_file(str(file_path))
    except Exception as e:
        print(f"Error updating Ollama models cache: {e}")
        return False
