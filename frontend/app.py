import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Safely import plotly
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("Visualization library not available. Some features may be limited.")

# Load environment variables
load_dotenv()

# Get API URL from environment variable or use default
API_URL = os.getenv("API_URL", "https://bi-coding-challenge.onrender.com")

# Rest of your imports and setup code...

# In the visualization section, modify the code to handle missing plotly:
with col2:
    st.header("Insights Dashboard")
    if st.session_state.chat_history:
        # Example visualization
        st.subheader("Confidence Scores")
        try:
            confidence_data = pd.DataFrame([
                {"query": item["query"][:30] + "...", 
                 "confidence": item["response"].get("confidence", 0.95)}
                for item in st.session_state.chat_history
            ])
            
            if PLOTLY_AVAILABLE:
                fig = px.bar(confidence_data, x="query", y="confidence",
                            title="Analysis Confidence Scores")
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Fallback to basic Streamlit chart
                st.bar_chart(confidence_data.set_index("query")["confidence"])
                
            # Add numerical summary
            st.metric("Average Confidence", 
                     f"{confidence_data['confidence'].mean():.2%}")
            st.metric("Queries Analyzed", 
                     len(st.session_state.chat_history))
                     
        except Exception as e:
            st.error("Error creating visualization")
            st.write("Raw Data:")
            st.dataframe(confidence_data)

# Rest of your code remains the same...
