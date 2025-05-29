#!/usr/bin/env python3
"""Debug script for running the PyLLM API with detailed logging."""

import logging
import uvicorn
from getllm.api import app

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Print all registered routes
print("\nRegistered routes:")
for route in app.routes:
    print(f"{route.path} - {route.name}")

if __name__ == "__main__":
    print("\nStarting PyLLM API server...")
    uvicorn.run(
        "getllm.api:app",
        host="0.0.0.0",
        port=8005,
        log_level="debug",
        reload=True
    )
