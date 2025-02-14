# api.py
from fastapi import APIRouter, HTTPException, FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from .rag import RAGEngine
from .utils.keepalive import KeepAliveSystem
from textblob import TextBlob
import gensim
from gensim import corpora
import os

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://rag-challenge.streamlit.app/"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
router = APIRouter()
rag_engine = RAGEngine()
keepalive = KeepAliveSystem(os.getenv('SERVICE_URL', 'https://bi-coding-challenge.onrender.com'))

class Query(BaseModel):
    text: str
    filters: Optional[Dict[str, Any]] = None

class Source(BaseModel):
    text: str
    document: str
    confidence: float
    sentiment: Optional[float] = None

class Topic(BaseModel):
    name: str
    keywords: List[str]
    weight: float

class AnalysisResponse(BaseModel):
    answer: str
    sources: List[Source]
    confidence: float
    topics: Optional[List[Topic]] = None
    sentiment: Optional[float] = None

def perform_topic_modeling(texts: List[str], num_topics: int = 3) -> List[Topic]:
    # Tokenize and create dictionary
    texts_tokens = [text.split() for text in texts]
    dictionary = corpora.Dictionary(texts_tokens)
    corpus = [dictionary.doc2bow(text) for text in texts_tokens]
    
    # Train LDA model
    lda_model = gensim.models.ldamodel.LdaModel(
        corpus=corpus,
        num_topics=num_topics,
        id2word=dictionary
    )
    
    # Extract topics
    topics = []
    for idx, topic in lda_model.print_topics(-1):
        keywords = [(word, float(weight)) for word, weight in 
                   [item.split('*') for item in topic.split('+')]]
        topics.append(Topic(
            name=f"Topic {idx + 1}",
            keywords=[kw[0].strip('"') for kw in keywords],
            weight=sum(kw[1] for kw in keywords) / len(keywords)
        ))
    
    return topics

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_query(query: Query, background_tasks: BackgroundTasks):
    try:
        # Get RAG response
        result = await rag_engine.process_query(query.text, query.filters)
        
        # Perform sentiment analysis
        blob = TextBlob(result["answer"])
        sentiment = blob.sentiment.polarity
        
        # Perform topic modeling on sources
        source_texts = [source["text"] for source in result["sources"]]
        topics = perform_topic_modeling(source_texts)
        
        # Add sentiment to sources
        for source in result["sources"]:
            source_blob = TextBlob(source["text"])
            source["sentiment"] = source_blob.sentiment.polarity
        
        return AnalysisResponse(
            answer=result["answer"],
            sources=result["sources"],
            confidence=result.get("confidence", 0.95),
            topics=topics,
            sentiment=sentiment
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

@app.on_event("startup")
async def startup_event():
    keepalive.start()

@app.on_event("shutdown")
async def shutdown_event():
    keepalive.stop()

# Add root route
@app.get("/")
async def root():
    return {"message": "Welcome to RAG API"}

# Include router with prefix
app.include_router(router, prefix="/api")
