"""Ollama server management."""

import os
import subprocess
import time
import logging
import requests
from typing import Optional

logger = logging.getLogger('getllm.ollama.server')

class OllamaServer:
    """Manages the Ollama server lifecycle."""
    
    def __init__(self, ollama_path: str = None):
        """Initialize the Ollama server manager.
        
        Args:
            ollama_path: Path to the Ollama executable. If not provided, 
                        will look for 'ollama' in PATH or use OLLAMA_PATH env var.
        """
        self.ollama_path = ollama_path or os.getenv('OLLAMA_PATH', 'ollama')
        self.process = None
        self.base_api_url = "http://localhost:11434/api"
        self.version_api_url = f"{self.base_api_url}/version"
        self.timeout = int(os.getenv('OLLAMA_TIMEOUT', '30'))
        
    def is_running(self) -> bool:
        """Check if the Ollama server is running.
        
        Returns:
            bool: True if the server is running, False otherwise.
        """
        try:
            response = requests.get(self.version_api_url, timeout=5)
            return response.status_code == 200
        except (requests.exceptions.ConnectionError, requests.exceptions.RequestException):
            return False
    
    def start(self) -> bool:
        """Start the Ollama server.
        
        Returns:
            bool: True if the server was started successfully, False otherwise.
        """
        if self.is_running():
            logger.info("Ollama server is already running")
            return True
            
        logger.info("Starting Ollama server...")
        try:
            self.process = subprocess.Popen(
                [self.ollama_path, "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for the server to start
            for _ in range(10):  # Try for 10 seconds
                if self.is_running():
                    logger.info("Ollama server started successfully")
                    return True
                time.sleep(1)
                
            # If we get here, the server didn't start
            logger.error("Failed to start Ollama server: Timeout")
            if self.process:
                _, stderr = self.process.communicate(timeout=5)
                if stderr:
                    logger.error(f"Error output: {stderr.decode().strip()}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to start Ollama server: {str(e)}")
            return False
    
    def stop(self) -> None:
        """Stop the Ollama server if it was started by this instance."""
        if self.process:
            logger.info("Stopping Ollama server...")
            try:
                self.process.terminate()
                self.process.wait(timeout=10)
                logger.info("Ollama server stopped")
            except subprocess.TimeoutExpired:
                logger.warning("Force stopping Ollama server...")
                self.process.kill()
                self.process.wait()
                logger.warning("Ollama server force stopped")
            except Exception as e:
                logger.error(f"Error stopping Ollama server: {str(e)}")
            finally:
                self.process = None
    
    def restart(self) -> bool:
        """Restart the Ollama server.
        
        Returns:
            bool: True if the server was restarted successfully, False otherwise.
        """
        self.stop()
        return self.start()
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
