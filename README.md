# BI-coding-challenge
This web application implements a Retrieval-Augmented Generation (RAG) backend system to analyze and compare two provided market research reports. 

---

## Key Features
Retrieval-Augmented Generation (RAG) combines retrieval-based and generation-based methods to provide accurate responses by extracting context from documents and generating relevant answers.
- **Source traceability:** Displays citations and confidence scores for transparency.
- **Interactive UI:** Built with Streamlit for an intuitive user experience.
- **FastAPI backend:** Handles AI processing and query analysis.
- **Data visualization:** Uses CSS

---

## Tech Stack
- **Frontend:** Streamlit (for responsive web interface)
- **Backend:** FastAPI
- **Models used**: LangChain, OpenAI API
- **Vector Store:** FAISS
- **PDF Processing:** LangChain PyPDFLoader

---

## Installation

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
