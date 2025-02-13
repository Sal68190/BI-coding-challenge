import streamlit as st
import requests
import pandas as pd
from typing import Dict, Any
from datetime import datetime

# Configure the page 
st.set_page_config(
    page_title="Market Research RAG Analysis",
    page_icon="📊",
    layout="wide"
)

# Backend URL
API_URL = "https://bi-coding-challenge.onrender.com"

def query_backend(query: str) -> Dict[str, Any]:
    """Send query to backend and return response"""
    try:
        response = requests.post(
            f"{API_URL}/api/analyze",
            json={"text": query},
            timeout=30,
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
        st.error(f"Could not connect to the backend. Please check if the server is running.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with backend: {str(e)}")
        return None

def check_backend_health():
    """Check if backend is healthy"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

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
        background-color: #122a40;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .source-text {
        font-size: 0.9em;
        padding: 1rem;
        background-color: #122a40;
        border-left: 3px solid #4d2525;
        margin: 0.5rem 0;
        color: #1F2937;
        border-radius: 0.25rem;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }
    .metric-card {
        background-color: #2b4854;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    .stExpander {
        background-color: #122a40;
        border-radius: 0.5rem;
        border: 1px solid #E5E7EB;
    }
    .stExpander .streamlit-expanderContent {
        background-color: #422a38;
        color: #1F2937;
    }
    .confidence-score {
        color: #4d2525;
        font-weight: 600;
    }
    .document-content {
        color: #778ca8 !important;
        background-color: #422a38;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        border: 1px solid #E5E7EB;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Header
st.title("📊 Market Research Analysis Platform")

# Sidebar
with st.sidebar:
    st.header("Settings")
    
    # Backend status indicator
    backend_status = check_backend_health()
    if backend_status:
        st.success("Backend: Connected")
    else:
        st.error("Backend: Not Connected")
        st.info("If the backend is not responding, it might be in cold start mode. Please wait a moment and try again.")
    
    st.divider()
    
    # Clear history button
    if st.button("Clear History", type="secondary"):
        st.session_state.chat_history = []
        st.success("Chat history cleared!")
    
    st.divider()
    st.markdown("### About")
    st.markdown("""
    This platform uses RAG (Retrieval Augmented Generation) to analyze market research reports.
    Ask questions about the reports and get AI-powered insights with source citations.
    
    Features:
    - 🤖 AI-powered analysis
    - 📊 Visual insights
    - 📝 Source citations
    - 🔍 Semantic search
    """)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Analysis Interface")
    query = st.text_input(
        "Ask a question about the market research reports:", 
        placeholder="e.g., What are the key market trends identified in both reports?",
        key="query_input"
    )
    
    if st.button("Analyze", type="primary"):
        if not query:
            st.warning("Please enter a question to analyze.")
        else:
            with st.spinner("Analyzing... This might take a moment on cold start."):
                response = query_backend(query)
                if response:
                    st.session_state.chat_history.append({
                        "query": query,
                        "response": response,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })

    # Display chat history
    for item in reversed(st.session_state.chat_history):
        with st.container():
            st.markdown("#### Question:")
            st.info(item["query"])
            
            if "timestamp" in item:
                st.caption(f"Asked at {item['timestamp']}")
            
            st.markdown("#### Analysis:")
            st.write(item["response"]["answer"])
            
            with st.expander("View Sources"):
                for idx, source in enumerate(item["response"]["sources"], 1):
                    st.markdown(f"""
                        <div class="source-text">
                            <strong>Source {idx}:</strong><br>
                            <div class="document-content">
                                {source["text"]}
                            </div>
                            <div style="margin-top: 0.5rem; font-size: 0.8em;">
                                <em>Document: {source['document']}</em>
                                <span class="confidence-score">
                                    &nbsp;|&nbsp;Confidence: {source['confidence']:.2%}
                                </span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

with col2:
    st.header("Insights Dashboard")
    if st.session_state.chat_history:
        # Analytics
        metrics_col1, metrics_col2 = st.columns(2)
        with metrics_col1:
            st.metric("Total Queries", len(st.session_state.chat_history))
        
        # Create confidence data
        confidence_data = pd.DataFrame([
            {
                "Query": f"Q{i+1}",
                "Confidence": sum(s['confidence'] for s in item["response"]["sources"]) / len(item["response"]["sources"]),
            }
            for i, item in enumerate(reversed(st.session_state.chat_history))
        ])
        
        # Average confidence
        with metrics_col2:
            avg_confidence = confidence_data["Confidence"].mean()
            st.metric("Average Confidence", f"{avg_confidence:.2%}")
        
        # Confidence visualization
        st.subheader("Confidence Trend")
        st.line_chart(
            confidence_data.set_index("Query")["Confidence"],
            use_container_width=True
        )
        
        # Query details
        st.subheader("Recent Queries")
        details_df = pd.DataFrame([
            {
                "Time": item.get("timestamp", "N/A"),
                "Query": item["query"][:40] + "..." if len(item["query"]) > 40 else item["query"],
                "Avg. Confidence": f"{sum(s['confidence'] for s in item['response']['sources']) / len(item['response']['sources']):.2%}"
            }
            for item in reversed(st.session_state.chat_history[-5:])
        ])
        st.dataframe(
            details_df,
            use_container_width=True,
            hide_index=True
        )

# Footer
st.divider()
st.markdown("""
<div style='text-align: center'>
    <small>Made with ❤️ by Saloni Deshpande</small>
</div>
""", unsafe_allow_html=True)
