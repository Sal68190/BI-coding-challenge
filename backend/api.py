# backend/api.py
from fastapi import APIRouter, HTTPException, FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
from .rag import RAGEngine
from .utils.keepalive import KeepAliveSystem
import os
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://rag-challenge.streamlit.app/"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
router = APIRouter()
try:
    rag_engine = RAGEngine()
    logger.info("RAG Engine initialized successfully")
except Exception as e:
    logger.error(f"Error initializing RAG Engine: {str(e)}")
    logger.error(traceback.format_exc())
    raise

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
        logger.info(f"Processing query: {query.text}")
        result = await rag_engine.process_query(query.text, query.filters)
        logger.info("Query processed successfully")
        return AnalysisResponse(
            answer=result["answer"],
            sources=result["sources"],
            confidence=result.get("confidence", 0.95)
        )
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": type(e).__name__,
                "trace": traceback.format_exc()
            }
        )

@router.get("/health")
async def health_check():
    try:
        # Check if RAG engine is initialized
        if not rag_engine:
            raise Exception("RAG Engine not initialized")
            
        # Test RAG engine basic functionality
        test_query = "test"
        await rag_engine.process_query(test_query)
        
        return {
            "status": "healthy",
            "rag_engine": "initialized and functional",
            "version": os.getenv("APP_VERSION", "1.0.0")
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "type": type(e).__name__
        }

# Add root route
@app.get("/")
async def root():
    return {"message": "Welcome to RAG API", "version": os.getenv("APP_VERSION", "1.0.0")}

# Include router with prefix
app.include_router(router, prefix="/api")

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up API server...")
    try:
        # Initialize keepalive system
        keepalive = KeepAliveSystem(os.getenv('SERVICE_URL', 'https://bi-coding-challenge.onrender.com'))
        keepalive.start()
        logger.info("Keepalive system started")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        logger.error(traceback.format_exc())

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down API server...")
