import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_response():
    return {
        "answer": "Test answer",
        "sources": [
            {
                "text": "Source text",
                "document": "test.pdf",
                "confidence": 0.95
            }
        ],
        "confidence": 0.95
    }
