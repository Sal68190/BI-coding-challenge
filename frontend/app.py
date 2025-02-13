import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API URL from environment variable or use default
API_URL = os.getenv("API_URL", "https://bi-coding-challenge.onrender.com/")  # Replace with your actual deployed backend URL

def query_backend(query: str) -> Dict[str, Any]:
    """Send query to FastAPI backend and return response"""
    try:
        # Add error handling and timeout
        response = requests.post(
            f"{API_URL}/api/analyze",
            json={"text": query, "filters": None},
            timeout=30,  # Increased timeout for cold starts
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error("Request timed out. The server might be starting up (cold start). Please try again.")
        return None
    except requests.exceptions.ConnectionError:
        st.error(f"Could not connect to the backend at {API_URL}. Please check if the server is running.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with backend: {str(e)}")
        return None

# Add backend status check
def check_backend_health():
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
   

# Configure the page
st.set_page_config(
    page_title="Market Research RAG Analysis",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stTextInput > div > div > input {
        padding: 0.5rem;
    }
    .user-query {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def query_backend(query: str) -> Dict[str, Any]:
    """Send query to FastAPI backend and return response"""
    try:
        response = requests.post(
            "http://localhost:8000/api/analyze",
            json={"text": query, "filters": None}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with backend: {str(e)}")
        return None

# Main layout
st.title("📊 Market Research Analysis Platform")


# Sidebar for filters and settings
with st.sidebar:
    st.header("Settings")
    temperature = st.slider("Analysis Depth", 0.0, 1.0, 0.7)
    st.divider()
    st.header("Filters")
    date_range = st.date_input("Date Range", [])
    st.divider()
    st.markdown("### About")
    st.markdown("""
    This web app is for the Bounce Insights Coding Challenge. This platform uses RAG (Retrieval Augmented Generation) to analyze given market research reports.
    Ask questions about the reports and get AI-powered insights with source citations.
    """)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Analysis Interface")
    query = st.text_input("Ask a question about the market research reports:", 
                         placeholder="e.g., What are the key market trends identified in both reports?")
    
    if st.button("Analyze", type="primary"):
        with st.spinner("Analyzing..."):
            if query:
                response = query_backend(query)
                if response:
                    # Add to chat history
                    st.session_state.chat_history.append({
                        "query": query,
                        "response": response
                    })

    # Display chat history
    for item in reversed(st.session_state.chat_history):
        with st.container():
            st.markdown("**Your Question:**")
            st.markdown(f"_{item['query']}_")
            st.markdown("**Analysis:**")
            st.markdown(item['response']['answer'])
            with st.expander("View Sources"):
                for source in item['response']['sources']:
                    st.markdown(f"- {source['text']}")
                    st.markdown(f"  *Source: {source['document']} (Confidence: {source['confidence']:.2f})*")

with col2:
    st.header("Insights Dashboard")
    if st.session_state.chat_history:
        # Example visualization
        st.subheader("Confidence Scores")
        confidence_data = pd.DataFrame([
            {"query": item["query"][:30] + "...", 
             "confidence": item["response"]["confidence"]}
            for item in st.session_state.chat_history
        ])
        fig = px.bar(confidence_data, x="query", y="confidence",
                    title="Analysis Confidence Scores")
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center'>
    <small>Made by Saloni Deshpande</small>
</div>
""", unsafe_allow_html=True)

