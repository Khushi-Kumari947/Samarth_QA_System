from fastapi import FastAPI
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

@app.get("/")
async def root():
    return {"message": "Welcome to Project Samarth - Empowering data-driven decision making"}

# Import routers after app creation to avoid circular imports
from samarth.api import query_router
app.include_router(query_router.router)

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