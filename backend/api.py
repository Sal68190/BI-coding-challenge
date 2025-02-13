from fastapi import APIRouter, HTTPException, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from .rag import RAGEngine  # Changed to relative import

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()
rag_engine = RAGEngine()

class Query(BaseModel):
    text: str
    filters: Optional[Dict[str, Any]] = None

class Source(BaseModel):
    text: str
    document: str
    confidence: float

class AnalysisResponse(BaseModel):
    answer: str
    sources: List[Source]
    confidence: float

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_query(query: Query):
    try:
        result = await rag_engine.process_query(query.text, query.filters)
        return AnalysisResponse(
            answer=result["answer"],
            sources=result["sources"],
            confidence=result.get("confidence", 0.95)
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@router.get("/health")
async def health_check():
    return {"status": "healthy", "rag_engine": "initialized"}

# Add root route
@app.get("/")
async def root():
    return {"message": "Welcome to RAG API"}

# Include router with prefix
app.include_router(router, prefix="/api")

