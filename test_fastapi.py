from fastapi import FastAPI
import uvicorn

# Create a new FastAPI app
app = FastAPI()

@app.get("/test")
async def test():
    return {"message": "Test endpoint working!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("\nRegistered routes:")
    for route in app.routes:
        print(f"{route.path} - {route.name}")
    
    print("\nStarting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8004, log_level="info")
