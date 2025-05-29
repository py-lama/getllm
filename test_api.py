from fastapi import FastAPI
import uvicorn

# Import the app from getllm.api
from getllm.api import app

# Print all registered routes
print("\nRegistered routes:")
for route in app.routes:
    print(f"{route.path} - {route.name}")

# Run the app with debug logging
if __name__ == "__main__":
    uvicorn.run("test_api:app", host="0.0.0.0", port=8001, reload=True, log_level="debug")
