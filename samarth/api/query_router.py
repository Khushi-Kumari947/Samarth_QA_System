from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

# Handle imports for different environments
query_service = None
QueryRequest = None
QueryResponse = None
MetadataAccess = None

# Try multiple import strategies for different environments
import_errors = []

try:
    # When running as part of the samarth module
    from samarth.services.query_service import query_service
    from samarth.models.data_models import QueryRequest, QueryResponse
except ImportError as e1:
    import_errors.append(f"samarth.module: {e1}")
    try:
        # When running standalone, import directly from services and models directories
        from services.query_service import query_service
        from models.data_models import QueryRequest, QueryResponse
    except ImportError as e2:
        import_errors.append(f"standalone: {e2}")
        try:
            # Fallback to relative imports when running from within the samarth directory
            from ..services.query_service import query_service
            from ..models.data_models import QueryRequest, QueryResponse
        except ImportError as e3:
            import_errors.append(f"relative: {e3}")
            query_service = None
            QueryRequest = None
            QueryResponse = None

# Try to import MetadataAccess for the datasets endpoint
try:
    # When running as part of the samarth module
    from samarth.data.data_access import MetadataAccess
except ImportError as e1:
    try:
        # When running standalone, import directly from data directory
        from data.data_access import MetadataAccess
    except ImportError as e2:
        try:
            # Fallback to relative import when running from within the samarth directory
            from ..data.data_access import MetadataAccess
        except ImportError as e3:
            MetadataAccess = None

# Print import errors for debugging
if import_errors:
    print("Import warnings in query_router.py:")
    for error in import_errors:
        print(f"  - {error}")

router = APIRouter(prefix="/api/v1/query", tags=["Query Processing"])

@router.post("/ask", response_model=None)  # Remove response_model for now to avoid import issues
async def ask_question(request: Dict):  # Use Dict instead of QueryRequest to avoid import issues
    """
    Process a natural language question and return an AI-generated answer
    """
    try:
        # Check if query_service was imported successfully
        if query_service is None:
            raise Exception("query_service not imported successfully")
        
        # Use the question from the request dict
        question = request.get("question", "")
        user_id = request.get("user_id")
        
        result = await query_service.process_query(question, user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.get("/datasets", response_model=None)  # Remove response_model for now to avoid import issues
async def list_datasets():
    """
    List all available datasets
    """
    try:
        # Check if MetadataAccess was imported successfully
        if MetadataAccess is None:
            raise Exception("MetadataAccess not imported successfully")
            
        datasets = MetadataAccess.list_all_datasets()
        return datasets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving datasets: {str(e)}")