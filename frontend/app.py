import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any
from datetime import datetime
import os
import altair as alt
from wordcloud import WordCloud
import numpy as np

# Configure the page with responsive layout
st.set_page_config(
    page_title="Market Research RAG Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Get API URL from environment variable or use default
API_URL = os.getenv('API_URL', "https://bi-coding-challenge.onrender.com").rstrip('/')

# Enhanced CSS with responsive design
st.markdown("""
<style>
    /* Responsive container classes */
    .main-container {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        background-color: rgba(17, 25, 40, 0.75);
        backdrop-filter: blur(16px) saturate(180%);
    }
    
    .grid-container {
        display: grid;
        gap: 1rem;
        padding: 1rem;
    }
    
    /* Responsive typography */
    @media (max-width: 768px) {
        .main-title {
            font-size: 1.5rem !important;
        }
        .sub-title {
            font-size: 1.2rem !important;
        }
    }
    
    /* Enhanced component styling */
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.05);
        border-color: rgba(255, 255, 255, 0.1);
    }
    
    .source-card {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    
    /* Animation classes */
    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

def create_topic_visualization(topics_data):
    """Create an interactive topic visualization using Plotly"""
    if not topics_data:
        return None
        
    fig = go.Figure()
    
    for topic in topics_data:
        fig.add_trace(go.Bar(
            name=topic['name'],
            x=[kw for kw in topic['keywords']],
            y=[topic['weight']] * len(topic['keywords']),
            text=[f"{topic['weight']:.2f}"] * len(topic['keywords']),
            textposition='auto',
        ))
    
    fig.update_layout(
        title="Topic Distribution",
        barmode='group',
        template="plotly_dark",
        height=400
    )
    
    return fig

def create_sentiment_gauge(sentiment_score):
    """Create a gauge chart for sentiment visualization"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=sentiment_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [-1, 1]},
            'bar': {'color': "rgba(255, 255, 255, 0.8)"},
            'steps': [
                {'range': [-1, -0.3], 'color': "rgba(255, 0, 0, 0.3)"},
                {'range': [-0.3, 0.3], 'color': "rgba(255, 255, 0, 0.3)"},
                {'range': [0.3, 1], 'color': "rgba(0, 255, 0, 0.3)"}
            ]
        }
    ))
    
    fig.update_layout(
        title="Sentiment Analysis",
        template="plotly_dark",
        height=300
    )
    
    return fig

def create_wordcloud(text):
    """Generate a word cloud from text"""
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='black',
        colormap='viridis'
    ).generate(text)
    
    return wordcloud.to_array()

def query_backend(query: str) -> Dict[str, Any]:
    """Enhanced backend query function with better error handling"""
    try:
        with st.spinner("🤔 Analyzing your query..."):
            response = requests.post(
                f"{API_URL}/api/analyze",
                json={"text": query, "filters": None},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "topics" not in data:
                    data["topics"] = []  # Ensure topics field exists
                return data
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
                return None
                
    except requests.exceptions.Timeout:
        st.error("⏳ Request timed out. The server might be starting up (cold start). Please try again.")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None

# Initialize session state for advanced features
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'topic_history' not in st.session_state:
    st.session_state.topic_history = []
if 'sentiment_history' not in st.session_state:
    st.session_state.sentiment_history = []

# Main layout
st.title("📊 Advanced Market Research Analysis")

# Sidebar with enhanced controls
with st.sidebar:
    st.header("Analysis Controls")
    
    # Advanced settings
    with st.expander("🛠️ Advanced Settings", expanded=False):
        max_sources = st.slider("Maximum Sources", 1, 10, 5)
        min_confidence = st.slider("Minimum Confidence", 0.0, 1.0, 0.7)
        enable_topics = st.toggle("Enable Topic Analysis", True)
        enable_sentiment = st.toggle("Enable Sentiment Analysis", True)
    
    # Filters
    with st.expander("🎯 Filters", expanded=False):
        date_range = st.date_input("Date Range", [])
        categories = st.multiselect(
            "Categories",
            ["Market Trends", "Competition", "Technology", "Regulations"],
            []
        )
    
    # Session Management
    if st.button("🗑️ Clear History"):
        st.session_state.chat_history = []
        st.session_state.topic_history = []
        st.session_state.sentiment_history = []
        st.success("History cleared!")

# Main content area with responsive layout
col1, col2 = st.columns([2, 1])

with col1:
    # Query input with enhanced UI
    st.markdown('<div class="main-container fade-in">', unsafe_allow_html=True)
    query = st.text_input(
        "🔍 Ask your question:",
        placeholder="e.g., What are the emerging trends in the market?",
        key="query_input"
    )
    
    if st.button("🚀 Analyze", type="primary"):
        if query:
            response = query_backend(query)
            if response:
                # Update session state
                st.session_state.chat_history.append({
                    "query": query,
                    "response": response,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
                if "topics" in response:
                    st.session_state.topic_history.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "topics": response["topics"]
                    })
                
                if "sentiment" in response:
                    st.session_state.sentiment_history.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "sentiment": response["sentiment"]
                    })
    
    # Display chat history with enhanced visualization
    for item in reversed(st.session_state.chat_history):
        st.markdown('<div class="main-container fade-in">', unsafe_allow_html=True)
        
        # Query section
        st.markdown("### 🗣️ Question")
        st.info(item["query"])
        st.caption(f"Asked at {item['timestamp']}")
        
        # Answer section with enhanced formatting
        st.markdown("### 🤖 Analysis")
        st.write(item["response"]["answer"])
        
        # Create tabs for different visualizations
        tab1, tab2, tab3 = st.tabs(["📚 Sources", "📊 Topics", "😊 Sentiment"])
        
        with tab1:
            for idx, source in enumerate(item["response"]["sources"], 1):
                with st.container():
                    st.markdown(f"**Source {idx}**")
                    st.markdown(f'<div class="source-card">{source["text"]}</div>', 
                              unsafe_allow_html=True)
                    cols = st.columns(3)
                    with cols[0]:
                        st.metric("Confidence", f"{source['confidence']:.1%}")
                    with cols[1]:
                        if "sentiment" in source:
                            st.metric("Sentiment", f"{source['sentiment']:.2f}")
        
        with tab2:
            if "topics" in item["response"]:
                topic_fig = create_topic_visualization(item["response"]["topics"])
                if topic_fig:
                    st.plotly_chart(topic_fig, use_container_width=True)
        
        with tab3:
            if "sentiment" in item["response"]:
                sentiment_fig = create_sentiment_gauge(item["response"]["sentiment"])
                st.plotly_chart(sentiment_fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Enhanced analytics dashboard
    st.markdown('<div class="main-container fade-in">', unsafe_allow_html=True)
    st.header("📈 Analytics Dashboard")
    
    # Summary metrics
    if st.session_state.chat_history:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Queries", len(st.session_state.chat_history))
        with col2:
            avg_confidence = np.mean([
                item["response"].get("confidence", 0)
                for item in st.session_state.chat_history
            ])
            st.metric("Avg. Confidence", f"{avg_confidence:.1%}")
        
        # Sentiment trend
        if st.session_state.sentiment_history:
            sentiment_data = pd.DataFrame(st.session_state.sentiment_history)
            st.line_chart(
                sentiment_data.set_index("timestamp")["sentiment"],
                use_container_width=True
            )
        
        # Topic evolution
        if st.session_state.topic_history:
            st.markdown("### Topic Evolution")
            topic_data = []
            for entry in st.session_state.topic_history:
                for topic in entry["topics"]:
                    topic_data.append({
                        "timestamp": entry["timestamp"],
                        "topic": topic["name"],
                        "weight": topic["weight"]
                    })
            
            topic_df = pd.DataFrame(topic_data)
            if not topic_df.empty:
                topic_chart = alt.Chart(topic_df).mark_area().encode(
                    x="timestamp:T",
                    y="weight:Q",
                    color="topic:N",
                    tooltip=["topic", "weight"]
                ).properties(height=300)
                st.altair_chart(topic_chart, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center'>
    <small>Made with ❤️ by Saloni Deshpande</small>
</div>
""", unsafe_allow_html=True)
