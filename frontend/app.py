import streamlit as st
import requests
import pandas as pd
from typing import Dict, Any
from datetime import datetime
import os
import altair as alt
import numpy as np
import time

# Configure Altair
alt.data_transformers.disable_max_rows()

# Configure the page 
st.set_page_config(
    page_title="Market Research RAG Analysis",
    page_icon="📊",
    layout="wide"
)

# Get API URL from environment variable or use default
API_URL = os.getenv('API_URL', "https://bi-coding-challenge.onrender.com").rstrip('/')

def show_loading_state(attempt: int = 1, max_retries: int = 3):
    """Display informative loading state with progress"""
    with st.status(f"Processing Query (Attempt {attempt}/{max_retries})", expanded=True) as status:
        status.write("⚡ Connecting to server...")
        time.sleep(1)
        status.write("🔄 Initializing models...")
        time.sleep(1)
        status.write("🔍 Retrieving relevant documents...")
        time.sleep(1)
        
        if attempt > 1:
            status.write("🔥 Server warming up (cold start)...")
            status.write("⏳ This might take 30-60 seconds...")
        
        return status

def query_backend(query: str, max_retries: int = 3) -> Dict[str, Any]:
    """Send query to FastAPI backend with retry mechanism"""
    for attempt in range(max_retries):
        try:
            status = show_loading_state(attempt + 1, max_retries)
            
            response = requests.post(
                f"{API_URL}/api/analyze",
                json={"text": query, "filters": None},
                timeout=30 if attempt == 0 else 60,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
            
            if response.status_code == 200:
                status.update(label="✅ Analysis complete!", state="complete")
                return response.json()
            elif response.status_code == 503:
                status.write("🔄 Server is starting up...")
                time.sleep(5)
                continue
            else:
                status.update(label="❌ Error occurred", state="error")
                raise Exception(f"Server returned status code: {response.status_code}")
                
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                status.write("⏳ Request timed out. Retrying...")
                time.sleep(5)
                continue
            else:
                st.error("❌ Request timed out after multiple attempts. Please try again.")
                return None
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            return None
    
    return None

def check_backend_health():
    """Check backend health with detailed feedback"""
    try:
        response = requests.get(f"{API_URL}/api/health", timeout=5)
        
        if response.status_code == 200:
            try:
                data = response.json()
                status = data.get("status")
                return status == "healthy", data.get("message", "")
            except:
                return False, "Invalid response format"
        else:
            return False, f"Server returned status {response.status_code}"
            
    except requests.exceptions.Timeout:
        return False, "Server is starting up (timeout)"
    except requests.exceptions.ConnectionError:
        return False, "Could not connect to server"
    except Exception as e:
        return False, str(e)

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
        background-color: #301d28;
        border-left: 3px solid #0f0406;
        margin: 0.5rem 0;
        color: #414a57;
        border-radius: 0.25rem;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }
    .metric-card {
        background-color: #303b30;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    .stExpander {
        background-color: #1f2937;
        border-radius: 0.5rem;
        border: 1px solid #E5E7EB;
    }
    .stExpander .streamlit-expanderContent {
        background-color: #363c45;
        color: #414a57;
    }
    .confidence-score {
        color: #3c5941;
        font-weight: 600;
    }
    .document-content {
        color: #01080f !important;
        background-color: #9c8d79;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        border: 1px solid #01080f;
    }
    .stats-container {
        background-color: #122a40;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .chart-container {
        background-color: #1f2937;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border: 1px solid #363c45;
    }
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 6px;
    }
    .status-healthy {
        background-color: #10B981;
    }
    .status-warning {
        background-color: #F59E0B;
    }
    .status-error {
        background-color: #EF4444;
    }
</style>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Header
st.title("📊 Market Research Analysis Platform")

# Sidebar content
with st.sidebar:
    st.header("System Status")
    is_healthy, message = check_backend_health()
    
    if is_healthy:
        st.success("✅ System Ready")
    else:
        st.warning("⚠️ System Warming Up")
        st.info(f"Status: {message}")
        
        with st.expander("ℹ️ About Cold Starts"):
            st.markdown("""
            **What's happening?**
            - The server is initializing after being inactive
            - First request may take 30-60 seconds
            - Subsequent requests will be much faster
            
            **Tips:**
            1. Wait for the system to warm up
            2. Don't refresh the page
            3. Your request will be processed automatically
            """)
    
    st.divider()
    
    # Analysis Settings
    st.header("Settings")
    temperature = st.slider("Analysis Depth", 0.0, 1.0, 0.7)
    date_range = st.date_input("Date Range", [])
    
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

# Main content layout
col1, col2 = st.columns([2, 1])

# Analysis Interface
with col1:
    st.header("Analysis Interface")
    query = st.text_input(
        "Ask a question about the market research reports:", 
        placeholder="e.g., What are the key market trends identified in both reports?",
        key="query_input"
    )
    
    if st.button("Analyze", type="primary", disabled=not is_healthy):
        if not query:
            st.warning("⚠️ Please enter a question to analyze.")
        else:
            response = query_backend(query)
            if response:
                st.toast("✨ Analysis completed successfully!")
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
                    st.markdown(f"**Source {idx}:**")
                    st.markdown(f'<div class="source-text">{source["text"]}</div>', 
                              unsafe_allow_html=True)
                    st.caption(f"Document: {source['document']} | Confidence: {source['confidence']:.2%}")
                    st.divider()


# Analytics Dashboard
with col2:
    st.header("📊 Analytics Hub")
    
    if st.session_state.chat_history:
        # Calculate metrics
        total_queries = len(st.session_state.chat_history)
        confidence_values = [item["response"].get("confidence", 0.95) 
                           for item in st.session_state.chat_history]
        avg_confidence = sum(confidence_values) / len(confidence_values)
        
        # Document frequencies
        document_frequencies = {}
        for item in st.session_state.chat_history:
            for source in item["response"]["sources"]:
                doc = source["document"]
                document_frequencies[doc] = document_frequencies.get(doc, 0) + 1

        # Metrics Overview
        metrics_cols = st.columns(3)
        with metrics_cols[0]:
            st.metric("Queries", total_queries, "Total")
        with metrics_cols[1]:
            st.metric("Confidence", f"{avg_confidence:.1%}", "Average")
        with metrics_cols[2]:
            st.metric("Documents", len(document_frequencies), "Unique")

        # Charts
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("Confidence Trends")
        
        trend_data = pd.DataFrame([
            {
                "Query": f"Q{i+1}",
                "Confidence": item["response"].get("confidence", 0.95),
                "Topic": item["query"]
            }
            for i, item in enumerate(st.session_state.chat_history)
        ])
        
        line_chart = alt.Chart(trend_data).mark_line(
            point=True
        ).encode(
            x=alt.X('Query:N', title='Query'),
            y=alt.Y('Confidence:Q', scale=alt.Scale(domain=[0.5, 1])),
            tooltip=['Query:N', 'Confidence:Q', 'Topic:N']
        ).properties(height=200)
        
        st.altair_chart(line_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Document Usage
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("Document Usage")
        
        source_data = pd.DataFrame([
            {"Document": doc, "Citations": count}
            for doc, count in document_frequencies.items()
        ]).sort_values("Citations", ascending=True)
        
        bar_chart = alt.Chart(source_data).mark_bar().encode(
            x='Citations:Q',
            y=alt.Y('Document:N', sort='-x'),
            tooltip=['Document:N', 'Citations:Q']
        ).properties(height=max(100, len(document_frequencies) * 30))
        
        st.altair_chart(bar_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("""
        ### 🚀 Getting Started
        1. Type your question in the analysis interface
        2. First query may take longer (cold start)
        3. System will process automatically
        4. Results and analytics will appear here
        """)
    
# Footer
st.divider()
st.markdown("""
<div style='text-align: center'>
    <small>Made with ❤️ by Saloni Deshpande</small>
</div>
""", unsafe_allow_html=True)
