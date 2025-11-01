from fastapi import FastAPI
import os
from dotenv import load_dotenv

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

app.include_router(query_router.router, prefix="/api/v1")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Project Samarth"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)