# BI-coding-challenge
This web application implements a Retrieval-Augmented Generation (RAG) backend system to analyze and compare two provided market research reports. 

## Watch the Demo

Click on the image below to watch the demo[<img width="1440" alt="Image" src="https://github.com/user-attachments/assets/25c97184-ce16-4c0d-a06a-a0a2ca99e2d3" />](https://youtu.be/p0-AAe0ZI6Y)

---

# Key Features

## Core Capabilities

- Document analysis using RAG and LangChain
- Semantic search with FAISS vector store
- Real-time topic modeling and sentiment analysis
- Interactive data visualizations
- Cold start prevention system

## Technical Features

- Responsive UI with Streamlit
- FastAPI backend with async support
- OpenAI integration for advanced NLP
- Comprehensive test coverage
- Performance optimized with caching

---

## Tech Stack
- **Frontend:** Streamlit (for responsive web interface)
- **Backend:** FastAPI
- **Models used**: LangChain, OpenAI API
- **Vector Store:** FAISS
- **PDF Processing:** LangChain PyPDFLoader

---

# Development

## Backend Development
The backend is built with FastAPI and includes:
- Async request handling
- RAG implementation with LangChain
- FAISS vector store for document retrieval
- Automatic cold start prevention

## Frontend Development
The frontend uses Streamlit and features:
- Interactive visualizations with Plotly
- Real-time analytics dashboard
- Responsive design
- Session state management

## Performance Optimization
The platform includes several performance optimizations:
- Cold start prevention using keepalive system
- Efficient vector store management
- Response caching
- Optimized state management
- Lazy loading of components

## Error Handling
The application implements comprehensive error handling:
- Backend validation with Pydantic
- Frontend error feedback
- Graceful degradation
- Detailed error logging

---

# Installation

To set up and run the RAG Chatbot, follow these steps:

### Step 1: Clone the repository

Clone the repository to your local machine:
```bash
git clone https://github.com/Sal68190/BI-coding-challenge.git
cd BI-coding-challenge
```

### Step 2: Set up a virtual environment

Create and activate a virtual environment to manage dependencies:

**For Linux/MacOS**:
```bash
python3 -m venv venv
source venv/bin/activate
```

**For Windows**:
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install dependencies

Install the required dependencies by running:
```bash
pip install -r backend/requirements.txt
```

### Step 4: Set up the environment variables

Ensure you have all the necessary environment variables set up (if applicable), such as API keys or file paths, as described in the documentation or project configuration files.

### Step 5: Running the application

After setting up the environment, start the backend and frontend servers:

**Backend Server**: Start the FastAPI server:
```bash
uvicorn api.main:app --reload
```
This will run the server at `http://localhost:8000`.

**Frontend Interface**: Start the Streamlit frontend:
```bash
streamlit run frontend/app.py
```
This will open the chat interface in your browser at `http://localhost:8501`.

Now, the RAG Chatbot should be fully functional on your local machine.
