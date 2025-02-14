import pytest
from unittest.mock import patch
import streamlit as st
import app

def test_query_backend(mock_response):
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response
        
        result = app.query_backend("test query")
        assert result == mock_response

def test_create_topic_visualization():
    topics_data = [
        {
            "name": "Topic 1",
            "keywords": ["test", "example"],
            "weight": 0.8
        }
    ]
    fig = app.create_topic_visualization(topics_data)
    assert fig is not None

def test_create_sentiment_gauge():
    fig = app.create_sentiment_gauge(0.5)
    assert fig is not None
