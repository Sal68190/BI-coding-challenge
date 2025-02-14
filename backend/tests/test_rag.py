import pytest
from ..rag import RAGEngine

@pytest.mark.asyncio
async def test_rag_process_query():
    rag = RAGEngine()
    result = await rag.process_query("test query")
    assert "answer" in result
    assert "sources" in result
