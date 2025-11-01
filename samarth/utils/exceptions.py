# Exception Handling for Project Samarth
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any

class SamarthException(Exception):
    """Base exception class for Project Samarth"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class DatasetNotFoundException(SamarthException):
    """Raised when a requested dataset is not found"""
    def __init__(self, dataset_name: str):
        super().__init__(f"Dataset '{dataset_name}' not found", 404)

class QueryGenerationException(SamarthException):
    """Raised when SQL query generation fails"""
    def __init__(self, reason: str):
        super().__init__(f"Failed to generate SQL query: {reason}", 422)

class DataRetrievalException(SamarthException):
    """Raised when data retrieval from warehouse fails"""
    def __init__(self, reason: str):
        super().__init__(f"Failed to retrieve data: {reason}", 500)

class LLMProcessingException(SamarthException):
    """Raised when LLM processing fails"""
    def __init__(self, reason: str):
        super().__init__(f"LLM processing failed: {reason}", 500)

# Exception handlers
async def samarth_exception_handler(request: Request, exc: SamarthException) -> JSONResponse:
    """Handle Samarth-specific exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message}
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions"""
    return JSONResponse(
        status_code=500,
        content={"error": "An unexpected error occurred"}
    )

# Register exception handlers in main application
def register_exception_handlers(app):
    """Register exception handlers with the FastAPI application"""
    app.add_exception_handler(SamarthException, samarth_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)