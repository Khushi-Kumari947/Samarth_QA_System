from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
from dotenv import load_dotenv

# Add the parent directory to sys.path to enable importing samarth modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Load environment variables from .env file
# The .env file is located in the samarth directory
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    # Fallback to default location
    load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Project Samarth",
    description="AI-driven question-answering platform for Indian government datasets",
    version="1.0.0"
)

# Debug information
print("Starting Project Samarth API")
print(f"Python path: {sys.path}")
print(f"Current directory: {os.getcwd()}")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Project Samarth - Empowering data-driven decision making"}

# Import routers after app creation to avoid circular imports
# Try multiple import strategies for different environments
try:
    print("Attempting to import samarth.api.query_router")
    from samarth.api import query_router
    print("Successfully imported samarth.api.query_router")
    app.include_router(query_router.router)
    print("Registered query router")
except ImportError as e1:
    print(f"Failed to import samarth.api.query_router: {e1}")
    try:
        # Fallback when running from within the samarth directory
        print("Attempting to import api.query_router")
        from api import query_router
        print("Successfully imported api.query_router")
        app.include_router(query_router.router)
        print("Registered query router")
    except ImportError as e2:
        print(f"Failed to import api.query_router: {e2}")
        # Last resort - try relative import
        try:
            print("Attempting to import .api.query_router")
            from .api import query_router
            print("Successfully imported .api.query_router")
            app.include_router(query_router.router)
            print("Registered query router")
        except ImportError as e3:
            print(f"Failed to import .api.query_router: {e3}")
            print(f"Failed to import query_router with all strategies:")
            print(f"Method 1 (samarth.api): {e1}")
            print(f"Method 2 (api): {e2}")
            print(f"Method 3 (relative): {e3}")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Project Samarth"}

# Test endpoint to verify API is working
@app.get("/test")
async def test_endpoint():
    return {"message": "API is working correctly"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)