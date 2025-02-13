import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from typing import Dict, Any

# Configure the page
st.set_page_config(
    page_title="Market Research RAG Analysis",
    page_icon="📊",
    layout="wide"
)

# Custom CSS with improved text visibility
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
    
    /* Source viewer styles */
    .source-viewer {
        background-color: white;
        color: #1F2937;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #E5E7EB;
        margin-bottom: 1rem;
    }
    
    /* Expander styles */
    .stExpander {
        background-color: white;
    }
    .stExpander .streamlit-expanderContent {
        background-color: white;
        color: #1F2937;
    }
    
    /* PDF viewer styles */
    .pdf-viewer {
        background-color: white;
        color: #1F2937;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #E5E7EB;
    }
    
    /* Document content styles */
    .document-content {
        color: #1F2937 !important;
        background-color: white;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        border: 1px solid #E5E7EB;
    }
    
    /* Confidence score styles */
    .confidence-score {
        color: #059669;
        font-weight: 600;
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
            "https://bi-coding-challenge.onrender.com/api/analyze",
            json={"text": query, "filters": None}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with backend: {str(e)}")
        return None

def display_chat_history():
    """Display chat history with improved source visibility"""
    if 'chat_history' not in st.session_state or not st.session_state.chat_history:
        st.warning("No chat history found")
        return
    
    for item in reversed(st.session_state.chat_history):
        with st.container():
            # Question
            st.markdown('<div class="user-query">', unsafe_allow_html=True)
            st.markdown(f"**Your Question:**")
            st.markdown(f"_{item['query']}_")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Analysis
            st.markdown("**Analysis:**")
            if 'response' in item and 'answer' in item['response']:
                st.markdown(item['response']['answer'])
            else:
                st.error("Response format incorrect")
            
            # Sources
            with st.expander("View Sources"):
                if 'response' in item and 'sources' in item['response']:
                    for source in item['response']['sources']:
                        st.markdown(f"""
                            <div class="source-viewer">
                                <div class="document-content">
                                    {source['text']}
                                </div>
                                <div style="margin-top: 0.5rem;">
                                    <em>Source: {source['document']}</em>
                                    <span class="confidence-score">
                                        (Confidence: {source['confidence']:.2f})
                                    </span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No sources available for this response")

# Main layout
st.title("📊 Market Research Analysis Platform")

# Sidebar
with st.sidebar:
    st.header("Settings")
    temperature = st.slider("Analysis Depth", 0.0, 1.0, 0.7)
    st.divider()
    st.header("Filters")
    date_range = st.date_input("Date Range", [])
    st.divider()
    st.markdown("### About")
    st.markdown("""
    This web app uses RAG (Retrieval Augmented Generation) to analyze market research reports.
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
                    st.session_state.chat_history.append({
                        "query": query,
                        "response": response
                    })
    
    # Display chat history
    display_chat_history()

with col2:
    st.header("Insights Dashboard")
    if st.session_state.chat_history:
        # Confidence scores visualization
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
    <small>Made with ❤️ by Your Name</small>
</div>
""", unsafe_allow_html=True)
