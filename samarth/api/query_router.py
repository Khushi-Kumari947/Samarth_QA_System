from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from samarth.services.query_service import query_service
from samarth.models.data_models import QueryRequest, QueryResponse

router = APIRouter(prefix="/api/v1/query", tags=["Query Processing"])

@router.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Process a natural language question and return an AI-generated answer
    """
    try:
        result = await query_service.process_query(request.question, request.user_id)
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.get("/datasets", response_model=List[Dict[str, str]])
async def list_datasets():
    """
    List all available datasets
    """
    try:
        from samarth.data.data_access import MetadataAccess
        datasets = MetadataAccess.list_all_datasets()
        return datasets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving datasets: {str(e)}")