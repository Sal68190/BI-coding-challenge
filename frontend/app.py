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
        color: #d4c3a7;
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

import numpy as np
from datetime import datetime, timedelta

with col2:
    st.header("📊 Analytics Hub")
    
    if st.session_state.chat_history:
        # Calculate key metrics
        total_queries = len(st.session_state.chat_history)
        confidence_values = [item["response"].get("confidence", 0.95) 
                           for item in st.session_state.chat_history]
        avg_confidence = sum(confidence_values) / len(confidence_values)
        
        # Get unique documents and their frequencies
        document_frequencies = {}
        for item in st.session_state.chat_history:
            for source in item["response"]["sources"]:
                doc = source["document"]
                document_frequencies[doc] = document_frequencies.get(doc, 0) + 1

        # Custom CSS for better styling
        st.markdown("""
        <style>
        .metric-row {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        .metric-card {
            background: linear-gradient(135deg, #1E1E1E 0%, #2D2D2D 100%);
            padding: 1.2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
            flex: 1;
        }
        .metric-card:hover {
            transform: translateY(-2px);
        }
        .metric-title {
            color: #888;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }
        .metric-value {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 0.3rem;
        }
        .metric-trend {
            font-size: 0.8rem;
            color: #00ff00;
        }
        .trend-up { color: #00ff00; }
        .trend-down { color: #ff4444; }
        .section-container {
            background: rgba(30, 30, 30, 0.6);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)

        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📈 Performance", "🎯 Insights", "📋 History"])
        
        with tab1:
            # Performance Overview Section
            metrics_html = ""
            for metric, value, icon, subtitle in [
                ("Total Queries", total_queries, "🔍", f"+{len(st.session_state.chat_history[-5:])}" if len(st.session_state.chat_history) > 5 else "New"),
                ("Avg Confidence", f"{avg_confidence:.1%}", "📊", "Last 24h"),
                ("Documents Used", len(document_frequencies), "📚", f"{sum(document_frequencies.values())} citations")
            ]:
                metrics_html += f"""
                <div class="metric-card">
                    <div class="metric-title">{icon} {metric}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-trend">{subtitle}</div>
                </div>
                """
            
            st.markdown(f'<div class="metric-row">{metrics_html}</div>', unsafe_allow_html=True)
            
            # Confidence Trend Analysis
            st.markdown('<div class="section-container">', unsafe_allow_html=True)
            st.subheader("Confidence Trends")
            
            trend_data = pd.DataFrame([
                {
                    "Query Number": i + 1,
                    "Confidence": item["response"].get("confidence", 0.95),
                    "Topic": item["query"][:30] + "..." if len(item["query"]) > 30 else item["query"],
                    "Timestamp": item.get("timestamp", "N/A")
                }
                for i, item in enumerate(st.session_state.chat_history)
            ])
            
            line_chart = alt.Chart(trend_data).mark_area(
                line={'color': '#00ff00'},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[
                        alt.GradientStop(color='#00ff00', offset=0),
                        alt.GradientStop(color='transparent', offset=1)
                    ],
                    x1=1,
                    x2=1,
                    y1=1,
                    y2=0
                )
            ).encode(
                x=alt.X('Query Number:Q', title='Query Sequence'),
                y=alt.Y('Confidence:Q', scale=alt.Scale(domain=[0.5, 1])),
                tooltip=['Query Number:Q', 'Confidence:Q', 'Topic:N', 'Timestamp:N']
            ).properties(height=250)
            
            st.altair_chart(line_chart, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            # Document Usage Analysis
            st.markdown('<div class="section-container">', unsafe_allow_html=True)
            st.subheader("Document Insights")
            
            source_data = pd.DataFrame([
                {"Document": doc, "Citations": count}
                for doc, count in document_frequencies.items()
            ]).sort_values("Citations", ascending=True)
            
            bar_chart = alt.Chart(source_data).mark_bar(
                cornerRadius=5
            ).encode(
                x='Citations:Q',
                y=alt.Y('Document:N', sort='-x'),
                color=alt.Color('Citations:Q', scale=alt.Scale(scheme='viridis')),
                tooltip=['Document:N', 'Citations:Q']
            ).properties(height=max(100, len(document_frequencies) * 30))
            
            st.altair_chart(bar_chart, use_container_width=True)
            
            # Add insights summary
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Most Cited Document", 
                         source_data.iloc[-1]["Document"],
                         f"{source_data.iloc[-1]['Citations']} citations")
            with col2:
                st.metric("Average Citations per Doc", 
                         f"{sum(document_frequencies.values()) / len(document_frequencies):.1f}",
                         f"{len(document_frequencies)} unique docs")
            st.markdown('</div>', unsafe_allow_html=True)

        with tab3:
            # Recent Activity
            st.markdown('<div class="section-container">', unsafe_allow_html=True)
            st.subheader("Recent Queries")
            
            for item in list(reversed(st.session_state.chat_history))[:5]:
                with st.container():
                    st.markdown(
                        f"""
                        <div style='
                            background: linear-gradient(135deg, #1E1E1E 0%, #2D2D2D 100%);
                            padding: 1rem;
                            border-radius: 8px;
                            margin-bottom: 1rem;
                            border-left: 4px solid #00ff00;
                        '>
                            <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                                <span style='color: #888;'>{item.get("timestamp", "N/A")}</span>
                                <span style='color: #00ff00;'>{item["response"].get("confidence", 0.95):.1%} confidence</span>
                            </div>
                            <p style='margin: 0.5rem 0; font-size: 1.1rem;'>{item["query"]}</p>
                            <div style='
                                display: flex;
                                gap: 1rem;
                                margin-top: 0.5rem;
                                font-size: 0.9rem;
                                color: #888;
                            '>
                                <span>📚 {len(item["response"]["sources"])} sources</span>
                                <span>🔍 {len(item["query"].split())} words</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Enhanced empty state
        st.markdown(
            """
            <div style='
                text-align: center;
                padding: 3rem 2rem;
                background: linear-gradient(135deg, #1E1E1E 0%, #2D2D2D 100%);
                border-radius: 10px;
                margin-top: 2rem;
            '>
                <h2 style='margin-bottom: 1rem;'>🔍 Start Your Analysis</h2>
                <p style='color: #888; margin-bottom: 2rem;'>
                    Ask questions to see real-time analytics and insights!
                </p>
                <div style='
                    display: inline-block;
                    padding: 1rem;
                    background: rgba(0,255,0,0.1);
                    border-radius: 8px;
                    border: 1px solid #00ff00;
                '>
                    Try asking about market trends, challenges, or key players
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )         
       
# Footer
st.divider()
st.markdown("""
<div style='text-align: center'>
    <small>Made with ❤️ by Saloni Deshpande</small>
</div>
""", unsafe_allow_html=True)
