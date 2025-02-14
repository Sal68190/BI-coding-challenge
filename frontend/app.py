import streamlit as st
import requests
import pandas as pd
from typing import Dict, Any
from datetime import datetime
import os

# Configure the page 
st.set_page_config(
    page_title="Market Research RAG Analysis",
    page_icon="📊",
    layout="wide"
)

# Get API URL from environment variable or use default
API_URL = os.getenv('API_URL', "https://bi-coding-challenge.onrender.com").rstrip('/')

def query_backend(query: str) -> Dict[str, Any]:
    """Send query to FastAPI backend and return response"""
    try:
        response = requests.post(
            f"{API_URL}/api/analyze",
            json={"text": query, "filters": None},
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
        st.error(f"Could not connect to the backend at {API_URL}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with backend: {str(e)}")
        return None

def check_backend_health():
    """Check if backend is healthy with detailed debugging"""
    try:
        health_url = f"{API_URL}/api/health"
        st.sidebar.caption(f"Checking health at: {health_url}")
        
        response = requests.get(
            health_url,
            timeout=5,
            headers={
                "Accept": "application/json"
            }
        )
        
        # Debug response details in an expander
        with st.sidebar.expander("Debug Details", expanded=False):
            st.write(f"Status Code: {response.status_code}")
            try:
                st.write("Response:", response.json())
            except:
                st.write("Raw Response:", response.text)
        
        if response.status_code == 200:
            try:
                data = response.json()
                return data.get("status") == "healthy"
            except:
                st.sidebar.warning("Backend response wasn't valid JSON")
                return False
                
        return False
        
    except requests.exceptions.RequestException as e:
        with st.sidebar.expander("Connection Error Details", expanded=True):
            st.error(f"Error: {str(e)}")
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
        background-color: #472e3d;
        border-left: 3px solid #0f0406;
        margin: 0.5rem 0;
        color: #030b17;
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
        color: #384f37;
        font-weight: 600;
    }
    .document-content {
        color: #d4c3a7 !important;
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
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Header
st.title("📊 Market Research Analysis Platform")

# Sidebar content (unchanged)
with st.sidebar:
    st.header("Settings")
    
    # Backend status indicator with detailed information
    st.subheader("Backend Status")
    backend_status = check_backend_health()
    
    if backend_status:
        st.success("Backend: Connected")
    else:
        st.error("Backend: Not Connected")
        st.warning("""
        Troubleshooting steps:
        1. Backend might be in cold start mode (wait 1-2 minutes)
        2. Check if the URL is correct
        3. Verify the backend is deployed
        4. Check for any network issues
        """)
    
    temperature = st.slider("Analysis Depth", 0.0, 1.0, 0.7)
    st.divider()
    
    # Filters
    st.header("Filters")
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

# Main content
col1, col2 = st.columns([2, 1])

# Analysis Interface (col1 content unchanged)
with col1:
    st.header("Analysis Interface")
    query = st.text_input(
        "Ask a question about the market research reports:", 
        placeholder="e.g., What are the key market trends identified in both reports?",
        key="query_input"
    )
    
    if st.button("Analyze", type="primary", disabled=not backend_status):
        if not query:
            st.warning("Please enter a question to analyze.")
        else:
            with st.spinner("Analyzing... This might take a moment on cold start."):
                response = query_backend(query)
                if response:
                    # Add to chat history with timestamp
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

# Enhanced Insights Dashboard (col2)
import seaborn as sns
import matplotlib.pyplot as plt

# Set seaborn style
sns.set_style("darkgrid")
plt.style.use("dark_background")

with col2:
    st.header("📊 Analytics")
    if st.session_state.chat_history:
        # Create tabs for different analytics views
        tab1, tab2, tab3 = st.tabs(["📈 Overview", "📊 Trends", "📝 Recent"])
        
        with tab1:
            # Overview metrics in a modern grid
            total_queries = len(st.session_state.chat_history)
            confidence_values = [item["response"].get("confidence", 0.95) 
                               for item in st.session_state.chat_history]
            avg_confidence = sum(confidence_values) / len(confidence_values)
            
            unique_docs = set()
            for item in st.session_state.chat_history:
                for source in item["response"]["sources"]:
                    unique_docs.add(source["document"])

            # Modern metric cards with icons
            st.markdown("""
            <style>
            .metric-card {
                background-color: #1E1E1E;
                padding: 1rem;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 1rem;
            }
            </style>
            """, unsafe_allow_html=True)

            cols = st.columns(3)
            with cols[0]:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <h3>🔍 Queries</h3>
                        <h2>{total_queries}</h2>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            
            with cols[1]:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <h3>📊 Avg Confidence</h3>
                        <h2>{avg_confidence:.1%}</h2>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            
            with cols[2]:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <h3>📚 Documents</h3>
                        <h2>{len(unique_docs)}</h2>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )

        with tab2:
            # Enhanced trend visualization using seaborn
            st.subheader("Confidence Trends")
            
            # Create trend data
            trend_data = pd.DataFrame([
                {
                    "Query": f"Q{i+1}",
                    "Confidence": item["response"].get("confidence", 0.95),
                    "Topic": item["query"][:30] + "..." if len(item["query"]) > 30 else item["query"]
                }
                for i, item in enumerate(st.session_state.chat_history)
            ])
            
            # Create confidence trend plot
            fig, ax = plt.subplots(figsize=(10, 4))
            sns.lineplot(data=trend_data, x="Query", y="Confidence", marker='o')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

            # Source distribution analysis
            st.subheader("Source Distribution")
            source_counts = {}
            for item in st.session_state.chat_history:
                for source in item["response"]["sources"]:
                    doc = source["document"]
                    source_counts[doc] = source_counts.get(doc, 0) + 1
            
            source_data = pd.DataFrame([
                {"Document": doc, "Citations": count}
                for doc, count in source_counts.items()
            ]).sort_values("Citations", ascending=True)
            
            # Create horizontal bar plot
            fig, ax = plt.subplots(figsize=(10, max(4, len(source_counts) * 0.5)))
            sns.barplot(data=source_data, x="Citations", y="Document", palette="viridis")
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

            # Additional trend analysis
            if len(st.session_state.chat_history) > 1:
                st.subheader("Confidence Distribution")
                fig, ax = plt.subplots(figsize=(10, 4))
                sns.histplot(confidence_values, bins=min(10, len(confidence_values)), kde=True)
                plt.xlabel("Confidence Score")
                plt.ylabel("Frequency")
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()

        with tab3:
            st.subheader("Recent Queries")
            for item in list(reversed(st.session_state.chat_history))[:5]:
                with st.container():
                    st.markdown(
                        f"""
                        <div style='padding: 1rem; background-color: #1E1E1E; border-radius: 8px; margin-bottom: 1rem;'>
                            <small style='color: #888;'>{item.get("timestamp", "N/A")}</small>
                            <p style='margin: 0.5rem 0;'>{item["query"]}</p>
                            <div style='display: flex; gap: 1rem;'>
                                <small style='color: #888;'>Confidence: {item["response"].get("confidence", 0.95):.1%}</small>
                                <small style='color: #888;'>Sources: {len(item["response"]["sources"])}</small>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    else:
        # Enhanced empty state
        st.markdown(
            """
            <div style='text-align: center; padding: 2rem;'>
                <h3>🔍 Start Analyzing</h3>
                <p>Ask questions to see insights and analytics!</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        with st.expander("📝 Example Questions"):
            st.markdown("""
            - What are the main market trends discussed in the reports?
            - What are the key challenges mentioned?
            - Which companies are the major players?
            - What growth projections are mentioned?
            """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center'>
    <small>Made with ❤️ by Saloni Deshpande</small>
</div>
""", unsafe_allow_html=True)
