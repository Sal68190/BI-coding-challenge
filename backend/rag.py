from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import os
from typing import Dict, Any, List
from dotenv import load_dotenv
import time

import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS



load_dotenv()

class RAGEngine:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model='text-embedding-3-small')
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.initialize_vector_store()
        self.llm = ChatOpenAI(
            temperature=0.7,
            model_name="gpt-4o-mini"
        )
        self.initialize_qa_chain()

    def initialize_vector_store(self):
        documents = []
        # PDFs are in a directory called docs inside venv
        
        pdf_dir = "backend/docs"
        
        for filename in os.listdir(pdf_dir):
            if filename.endswith(".pdf"):
                file_path = os.path.join(pdf_dir, filename)
                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())

        print(len(documents), "documents loaded.")
        
        # Split documents into chunks
        texts = self.text_splitter.split_documents(documents)
        print(len(texts), "chunks created.")

        print("-----------------------------------")
        print("Creating vector store...")
        print("-----------------------------------")
        # Create vector store
        self.vector_store = FAISS.from_documents(texts, self.embeddings)
        

    def get_relevant_context(self, query: str, k: int = 3) -> List[Dict]:
        docs = self.vector_store.similarity_search_with_score(query, k=k)
        return [
            {
                "text": doc[0].page_content,
                "document": doc[0].metadata.get("source", "Unknown"),
                "confidence": 1 - doc[1]  # Converting distance to confidence
            }
            for doc in docs
        ]
    
    def initialize_qa_chain(self):
        # Custom prompt template for market research analysis
       prompt_template = """You are an AI assistant with expertise in market research analysis. You can engage in general conversation and answer questions about any topic, while also having specific knowledge about market research reports when relevant.

        For market research related questions, use the following context:
        Context: {context}

        Question: {question}

        If the question is a general query (like greetings, casual conversation, or non-market research topics):
        - Respond naturally and appropriately
        - Engage in friendly conversation
        - Don't force market research context if it's not relevant

        If the question is about market research:
        1. Directly address the question using the provided context
        2. Cite specific information from the sources
        3. Highlight key insights and trends
        4. Note any limitations in the available information

        Remember: You can handle both casual conversation and detailed market analysis. Choose the appropriate response style based on the question type.

        Answer:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )

        # Create QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_kwargs={"k": 3}
            ),
            chain_type_kwargs={
                "prompt": PROMPT
            },
            return_source_documents=True
        )

    async def process_query(self, query: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        # Get response
        result = self.qa_chain({"query": query})
        
        return {
            "answer": result["result"],
            "sources": [
                {
                    "text": doc.page_content,
                    "document": doc.metadata.get("source", "Unknown"),
                    "confidence": 0.95  # Could be refined based on relevance scores
                }
                for doc in result["source_documents"]
            ]
        }
    

if __name__ == "__main__":
    rag_engine = RAGEngine()
    rag_engine.initialize_qa_chain()
    print("RAG Engine initialized.")
    input("Press Enter to exit...")
