#!/usr/bin/env python3
"""
Ollama Models Scraper
Pobiera i zapisuje wszystkie dostępne modele z Ollama Library do JSON
"""

import json
import time
from typing import List, Dict, Any
from urllib.parse import urljoin
import argparse
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

class OllamaModelsScraper:
    def __init__(self, headless: bool = True):
        self.base_url = "https://ollama.com"
        self.library_url = f"{self.base_url}/library"
        self.search_url = f"{self.base_url}/search"
        self.models = []
        self.headless = headless
        self.driver = self._init_driver()
    
    def _init_driver(self):
        """Initialize and return a Selenium WebDriver"""
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-infobars')
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        return driver
    
    def get_page(self, url: str, wait_for: str = None, timeout: int = 20) -> BeautifulSoup:
        """Load a page with Selenium and return parsed HTML"""
        print(f"🌐 Loading URL: {url}")
        try:
            self.driver.get(url)
            
            # Wait for the page to load completely
            if wait_for:
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_for))
                )
            
            # Wait a bit more for dynamic content
            time.sleep(3)
            
            # Save page source for debugging
            page_source = self.driver.page_source
            with open('debug_page.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            print("💾 Saved page source to debug_page.html")
            
            return BeautifulSoup(page_source, 'html.parser')
            
        except Exception as e:
            print(f"❌ Error loading {url}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            print("✅ WebDriver closed")

    def extract_model_info(self, card_element) -> Dict[str, Any]:
        """Extract model information from a model card element"""
        try:
            # Get model name
            name_elem = card_element.find_element(By.CSS_SELECTOR, 'h3')
            name = name_elem.text.strip() if name_elem else "Unknown"
            
            # Get model URL
            link_elem = card_element.find_element(By.CSS_SELECTOR, 'a')
            url = link_elem.get_attribute('href') if link_elem else ""
            
            # Get description
            desc_elem = card_element.find_elements(By.CSS_SELECTOR, 'p')
            description = desc_elem[0].text.strip() if desc_elem else ""
            
            # Get metadata (pulls, size, updated)
            meta_elems = card_element.find_elements(By.CSS_SELECTOR, 'div.text-sm.text-gray-500')
            metadata = [elem.text.strip().lower() for elem in meta_elems]
            
            pulls = next((m for m in metadata if 'pull' in m or 'download' in m), "0")
            size = next((m for m in metadata if 'gb' in m or 'mb' in m), "Unknown")
            updated = next((m for m in metadata if 'ago' in m or 'updated' in m), "Unknown")
            
            # Get tags
            tags = []
            tag_elems = card_element.find_elements(By.CSS_SELECTOR, 'span.bg-gray-100, span.inline-flex')
            for tag in tag_elems:
                tag_text = tag.text.strip()
                if tag_text and tag_text not in ['Ollama', 'Model', 'Library']:
                    tags.append(tag_text)
            
            return {
                "name": name,
                "url": url,
                "pulls": pulls,
                "size": size,
                "updated": updated,
                "description": description,
                "tags": tags,
                "source": "ollama",
                "ollama_command": f"ollama pull {name}",
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            print(f"⚠️ Error extracting model info: {e}")
            import traceback
            traceback.print_exc()
            return None

    def scrape_library_page(self, page: int = 1) -> List[Dict[str, Any]]:
        """Scrape one page of the Ollama library"""
        print(f"📄 Scraping library page {page}...")
        
        url = f"{self.library_url}?page={page}" if page > 1 else self.library_url
        
        try:
            # Load the page and wait for model cards to load
            self.driver.get(url)
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href^="/library/"]'))
            )
            
            # Wait a bit more for dynamic content
            time.sleep(3)
            
            # Find all model cards
            model_cards = self.driver.find_elements(By.CSS_SELECTOR, 'a[href^="/library/"]')
            print(f"🔍 Found {len(model_cards)} model cards on page {page}")
            
            models = []
            for card in model_cards[:5]:  # Limit to first 5 for testing
                try:
                    model_info = self.extract_model_info(card)
                    if model_info:
                        models.append(model_info)
                        print(f"✅ Added model: {model_info['name']}")
                except Exception as e:
                    print(f"⚠️ Error processing model card: {e}")
                    continue
                    
            return models
            
        except Exception as e:
            print(f"❌ Error scraping library page {page}: {e}")
            import traceback
            traceback.print_exc()
            return []

    def search_models(self, query: str = "", category: str = "") -> List[Dict[str, Any]]:
        """Search for models by query and category"""
        print(f"🔍 Searching for: query='{query}', category='{category}'")
        
        # For now, we'll just use the library page
        # The search functionality on Ollama's site is client-side rendered
        return self.scrape_library_page()

    def scrape_all_categories(self) -> List[Dict[str, Any]]:
        """Scrape'uje wszystkie kategorie modeli"""
        categories = [
            "", "vision", "code", "embedding", "tools", "multimodal",
            "chat", "reasoning", "math", "roleplay"
        ]

        all_models = []
        seen_models = set()

        for category in categories:
            print(f"📂 Scraping category: {category or 'all'}")

            models = self.search_models(category=category)

            for model in models:
                model_key = f"{model['name']}_{model['url']}"
                if model_key not in seen_models:
                    seen_models.add(model_key)
                    all_models.append(model)

            time.sleep(1)  # Rate limiting

        return all_models

    def scrape_all_models(self, detailed: bool = False) -> List[Dict[str, Any]]:
        """Główna funkcja - scrape'uje wszystkie modele"""
        print("🚀 Starting Ollama models scraping...")

        # Scrape library pages
        all_models = []
        page = 1
        max_pages = 50  # Safety limit

        while page <= max_pages:
            models = self.scrape_library_page(page)
            if not models:  # No more models found
                break

            all_models.extend(models)
            print(f"✅ Found {len(models)} models on page {page}")

            page += 1
            time.sleep(1)  # Rate limiting

        # Scrape categories for additional models
        category_models = self.scrape_all_categories()

        # Merge and deduplicate
        seen_models = set()
        final_models = []

        for models_list in [all_models, category_models]:
            for model in models_list:
                model_key = f"{model['name']}_{model['url']}"
                if model_key not in seen_models:
                    seen_models.add(model_key)

                    # Get detailed info if requested
                    if detailed and model['url']:
                        print(f"🔍 Getting details for {model['name']}...")
                        details = self.get_model_details(model['url'])
                        model.update(details)
                        time.sleep(0.5)  # Rate limiting

                    final_models.append(model)

        print(f"✅ Total unique models found: {len(final_models)}")
        return final_models

    def save_to_json(self, models: List[Dict[str, Any]], filename: str):
        """Zapisuje modele do pliku JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    "source": "ollama.com",
                    "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "total_models": len(models),
                    "models": models
                }, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved {len(models)} models to {filename}")
        except Exception as e:
            print(f"❌ Error saving to JSON: {e}")

    def search_local_models(self, query: str) -> List[Dict[str, Any]]:
        """Przeszukuje pobrane modele lokalnie"""
        if not self.models:
            print("❌ No models loaded. Run scrape_all_models() first.")
            return []

        query_lower = query.lower()
        results = []

        for model in self.models:
            if (query_lower in model['name'].lower() or
                    query_lower in model['description'].lower() or
                    any(query_lower in tag.lower() for tag in model['tags'])):
                results.append(model)

        return results


def main():
    parser = argparse.ArgumentParser(description='Scrape Ollama models')
    parser.add_argument('--output', '-o', default='ollama_models.json',
                        help='Output JSON file')
    parser.add_argument('--detailed', '-d', action='store_true',
                        help='Fetch detailed model information (slower)')
    parser.add_argument('--search', '-s', type=str,
                        help='Search for specific models')
    parser.add_argument('--category', '-c', type=str,
                        help='Filter by category')

    args = parser.parse_args()

    scraper = OllamaModelsScraper()

    if args.search:
        # Search mode
        models = scraper.search_models(query=args.search, category=args.category or "")
        print(f"\n🔍 Search results for '{args.search}':")
        for i, model in enumerate(models[:10], 1):  # Show first 10
            print(f"{i}. {model['name']} - {model['description'][:100]}...")
            print(f"   Command: {model['ollama_command']}")
    else:
        # Full scrape mode
        models = scraper.scrape_all_models(detailed=args.detailed)
        scraper.save_to_json(models, args.output)

        # Show summary
        print(f"\n📊 SUMMARY:")
        print(f"Total models: {len(models)}")

        # Count by categories/tags
        tag_counts = {}
        for model in models:
            for tag in model['tags']:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        print(f"Top categories:")
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {tag}: {count}")


if __name__ == "__main__":
    main()