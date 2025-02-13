import streamlit as st
import requests
import pandas as pd
import os

# Safely import plotly
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("Visualization library not available. Some features may be limited.")

# Get API URL from environment variable or use default
API_URL = "https://bi-coding-challenge.onrender.com"

def query_backend(query: str):
    """Send query to FastAPI backend and return response"""
    try:
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
        st.error("Request timed out. The server might be starting up (cold start). Please try again in a few moments.")
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

# Configure the page
st.set_page_config(
    page_title="Market Research RAG Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
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
    .stAlert {
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 0.5rem;
    }
    .source-text {
        font-size: 0.9em;
        padding: 0.5rem;
        background-color: #f8f9fa;
        border-left: 3px solid #6c757d;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'last_query_time' not in st.session_state:
    st.session_state.last_query_time = None

# Header
st.title("📊 Market Research RAG Analysis")

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

with col1:
    st.header("Analysis Interface")
    
    # Query input
    query = st.text_input(
        "Ask a question about the market research reports:",
        placeholder="e.g., What are the key market trends identified in both reports?",
        key="query_input"
    )
    
    # Analysis button
    if st.button("Analyze", type="primary"):
        if not query:
            st.warning("Please enter a question to analyze.")
        else:
            with st.spinner("Analyzing... This might take a moment on cold start."):
                response = query_backend(query)
                if response:
                    # Add timestamp to chat history
                    st.session_state.chat_history.append({
                        "query": query,
                        "response": response,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })
                    st.session_state.last_query_time = datetime.now()
    
    # Display chat history
    for item in reversed(st.session_state.chat_history):
        with st.container():
            # Query
            st.markdown("#### Question:")
            st.info(item["query"])
            
            # Timestamp
            st.caption(f"Asked at {item['timestamp']}")
            
            # Analysis
            st.markdown("#### Analysis:")
            st.write(item["response"]["answer"])
            
            # Sources
            with st.expander("View Sources"):
                for idx, source in enumerate(item["response"]["sources"], 1):
                    st.markdown(f"**Source {idx}:**")
                    st.markdown(f'<div class="source-text">{source["text"]}</div>', 
                              unsafe_allow_html=True)
                    st.caption(f"Document: {source['document']} | Confidence: {source['confidence']:.2%}")
                    st.divider()

with col2:
    st.header("Insights Dashboard")
    if st.session_state.chat_history:
        # Analytics
        st.metric(
            "Total Queries",
            len(st.session_state.chat_history)
        )
        
        if PLOTLY_AVAILABLE:
            try:
                # Confidence visualization
                st.subheader("Confidence Scores")
                confidence_data = pd.DataFrame([
                    {
                        "Query": f"Q{i+1}",
                        "Confidence": item["response"].get("confidence", 0.95),
                        "Question": item["query"][:30] + "..."
                    }
                    for i, item in enumerate(reversed(st.session_state.chat_history))
                ])
                
                fig = px.line(
                    confidence_data,
                    x="Query",
                    y="Confidence",
                    title="Analysis Confidence Trend",
                    hover_data=["Question"]
                )
                fig.update_layout(
                    hovermode='x unified',
                    yaxis_range=[0, 1]
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Average confidence
                avg_confidence = confidence_data["Confidence"].mean()
                st.metric(
                    "Average Confidence",
                    f"{avg_confidence:.2%}"
                )
                
            except Exception as e:
                st.error("Error creating visualization")
                st.write("Raw Data:")
                st.dataframe(confidence_data)
        else:
            # Fallback to basic Streamlit chart
            confidence_data = pd.DataFrame([
                {"Query": f"Q{i+1}", "Confidence": item["response"].get("confidence", 0.95)}
                for i, item in enumerate(st.session_state.chat_history)
            ])
            st.bar_chart(confidence_data.set_index("Query")["Confidence"])

# Footer
st.divider()
st.markdown("""
<div style='text-align: center'>
    <small>Market Research RAG Analysis Platform | Made with ❤️ by Saloni Deshpande</small>
</div>
""", unsafe_allow_html=True)
