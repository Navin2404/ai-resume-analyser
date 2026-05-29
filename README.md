# AI Resume Analyzer 🤖

RAG-based resume analyzer built with Python, LangChain, and Groq LLM.

## Features
- Upload any PDF resume
- Ask questions about the resume
- Powered by LLaMA 3.3 70B via Groq

## Tech Stack
- Python
- LangChain
- ChromaDB (Vector Database)
- HuggingFace Embeddings
- Groq LLM (LLaMA 3.3 70B)

## Setup
1. Clone the repo
2. Install dependencies
   pip install -r requirements.txt
3. Create .env file
   GROQ_API_KEY=your_key_here
4. Run ingest
   python ingest.py
5. Run chatbot
   python chatbot.py
