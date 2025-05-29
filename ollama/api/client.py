"""Ollama API client for model interactions."""

import json
import logging
import requests
from typing import Dict, Any, Optional, List, Union, Iterator

logger = logging.getLogger('getllm.ollama.api.client')

class OllamaClient:
    """Client for interacting with the Ollama API."""
    
    def __init__(self, base_url: str = "http://localhost:11434/api"):
        """Initialize the Ollama API client.
        
        Args:
            base_url: Base URL for the Ollama API
        """
        self.base_url = base_url.rstrip('/')
        self.generate_url = f"{self.base_url}/generate"
        self.chat_url = f"{self.base_url}/chat"
        self.embeddings_url = f"{self.base_url}/embeddings"
        self.timeout = int(os.getenv('OLLAMA_TIMEOUT', '30'))
    
    def generate(
        self,
        prompt: str,
        model: str,
        system: Optional[str] = None,
        template: Optional[str] = None,
        context: Optional[List[int]] = None,
        stream: bool = False,
        raw: bool = False,
        format: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Union[Dict[str, Any], Iterator[Dict[str, Any]]]:
        """Generate a response from the model.
        
        Args:
            prompt: The prompt to generate a response for
            model: The model to use for generation
            system: System message to set the behavior of the model
            template: The full prompt template to use
            context: The context parameter returned from a previous request
            stream: If true, returns a generator that yields responses as they're generated
            raw: If true, no formatting will be applied to the prompt
            format: The format to return the response in (currently only 'json' is supported)
            options: Additional model parameters (e.g., temperature, top_p, etc.)
            
        Returns:
            The generated response or a generator of response chunks if streaming
        """
        payload = {
            'model': model,
            'prompt': prompt,
            'stream': stream,
            'raw': raw
        }
        
        if system is not None:
            payload['system'] = system
        if template is not None:
            payload['template'] = template
        if context is not None:
            payload['context'] = context
        if format is not None:
            payload['format'] = format
        if options is not None:
            payload['options'] = options
        
        try:
            if stream:
                return self._stream_request(self.generate_url, payload)
            else:
                response = requests.post(
                    self.generate_url,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        stream: bool = False,
        format: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Union[Dict[str, Any], Iterator[Dict[str, Any]]]:
        """Generate a chat response.
        
        Args:
            messages: List of message objects with 'role' and 'content' keys
            model: The model to use for generation
            stream: If true, returns a generator that yields responses as they're generated
            format: The format to return the response in (currently only 'json' is supported)
            options: Additional model parameters
            
        Returns:
            The chat response or a generator of response chunks if streaming
        """
        payload = {
            'model': model,
            'messages': messages,
            'stream': stream
        }
        
        if format is not None:
            payload['format'] = format
        if options is not None:
            payload['options'] = options
        
        try:
            if stream:
                return self._stream_request(self.chat_url, payload)
            else:
                response = requests.post(
                    self.chat_url,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in chat completion: {str(e)}")
            raise
    
    def embeddings(
        self,
        prompt: str,
        model: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate embeddings for a prompt.
        
        Args:
            prompt: The prompt to generate embeddings for
            model: The model to use for generating embeddings
            options: Additional model parameters
            
        Returns:
            Dictionary containing the embeddings and metadata
        """
        payload = {
            'model': model,
            'prompt': prompt
        }
        
        if options is not None:
            payload['options'] = options
        
        try:
            response = requests.post(
                self.embeddings_url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def _stream_request(self, url: str, payload: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """Handle streaming requests.
        
        Args:
            url: The URL to send the request to
            payload: The request payload
            
        Yields:
            Response chunks as they're received
        """
        try:
            with requests.post(
                url,
                json=payload,
                stream=True,
                timeout=self.timeout
            ) as response:
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line.decode('utf-8'))
                            yield chunk
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to decode chunk: {line}")
                            continue
                            
        except requests.exceptions.RequestException as e:
            logger.error(f"Streaming request failed: {str(e)}")
            raise
