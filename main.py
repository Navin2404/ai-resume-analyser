# main.py — One file-la everything control pannuvom

import sys
# sys.argv — command line arguments read pannuvom
# python main.py document.pdf
# sys.argv = ["main.py", "document.pdf"]

from ingest import ingest
from chatbot import chat

# Other files-la irukka functions import pannuvom

# ============================================
# main.py — FastAPI Backend Server
# Frontend React-la irundhu inga call varum
# ============================================

# --- Imports ---
import os
import shutil
# shutil — files copy/move/delete pannuvom

from fastapi import FastAPI, UploadFile, File, HTTPException
# FastAPI — web framework
# UploadFile — PDF upload receive pannuvom
# File — file parameter define pannuvom
# HTTPException — error response pannuvom

from fastapi.middleware.cors import CORSMiddleware
# CORS — React (localhost:3000) → FastAPI (localhost:8000)
# different ports — browser block pannudu by default
# CORSMiddleware — allow pannuvom

from pydantic import BaseModel
# BaseModel — request/response data structure define pannuvom
# JSON body validate pannuvom automatically

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
import re

load_dotenv()


# ============================================
# FastAPI app create pannuvom
# ============================================
app = FastAPI(
    title="AI Resume Analyzer API",
    description="Upload resume PDF and ask questions",
    version="1.0.0"
)
# app — oru server instance
# title/description — automatic docs-la teriyadha

# ============================================
# CORS Setup — React connect aaga allow pannuvom
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",
                   "http://localhost:5173"],
    # React default ports — rendu allow pannuvom
    # Vite uses 5173, CRA uses 3000

    allow_credentials=True,
    allow_methods=["*"],    # GET, POST, PUT, DELETE — all allow
    allow_headers=["*"],    # All headers allow
)



# ============================================
# Global variables — app memory-la store
# ============================================
vectorstore = None
# None — initially DB load aagala
# PDF upload aana piragu load aagum

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
# uploads/ folder create pannuvom
# exist_ok=True — already irundha error vendam

# ============================================
# Helper Functions
# ============================================
def extract_text_from_pdf(pdf_path):
    # PDF → clean text
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text()

    # Spaced characters fix — "N A V E E N" → "NAVEEN"
    full_text = re.sub(r'(?<=[A-Za-z])\s(?=[A-Za-z])', '', full_text)
    full_text = re.sub(r'\n+', '\n', full_text)
    full_text = re.sub(r' +', ' ', full_text)
    return full_text

def create_vectorstore(text):
    # Text → chunks → embeddings → ChromaDB
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    chunks = splitter.split_text(text)

    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    vs = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    return vs

def get_llm_answer(question, vs):
    # Question → retrieve → LLM → answer
    retriever = vs.as_retriever(search_kwargs={"k": 3})
    chunks = retriever.invoke(question)
    context = "\n\n".join([c.page_content for c in chunks])

    prompt = f"""You are an expert resume analyzer assistant.
Use only the context below to answer the question accurately.
If the answer is not found in the context, say 'This information is not available in the resume.'

Context:
{context}

Question: {question}
Answer:"""

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0
    )
    response = llm.invoke(prompt)
    return response.content


# ============================================
# Pydantic Models — Request/Response structure
# ============================================
class ChatRequest(BaseModel):
    question: str
    # Frontend JSON body: {"question": "What are skills?"}


class ChatResponse(BaseModel):
    answer: str
    # Response JSON: {"answer": "Python, React..."}


class UploadResponse(BaseModel):
    message: str
    filename: str
    chunks: int


# ============================================
# API Endpoints
# ============================================

# --- Health Check ---
@app.get("/")
def root():
    # Browser-la localhost:8000 open panna idu teriyadha
    return {"status": "AI Resume Analyzer API Running!"}


# --- Upload Endpoint ---
# main.py — upload_resume function update pannuvom

@app.post("/upload", response_model=UploadResponse)
async def upload_resume(file: UploadFile = File(...)):

    global vectorstore

    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files allowed!"
        )

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    text = extract_text_from_pdf(file_path)

    # FIX — vectorstore close pannivom first, aprom delete pannuvom
    if vectorstore is not None:
        vectorstore = None
        # None panna — chroma connection release aagum

    # Windows-la file lock release aaga konjam wait pannuvom
    import time
    time.sleep(0.5)

    # Now safe-a delete pannalaam
    if os.path.exists("./chroma_db"):
        try:
            shutil.rmtree("./chroma_db")
        except PermissionError:
            # Still locked-a? Different folder use pannuvom
            import uuid
            chroma_dir = f"./chroma_db_{uuid.uuid4().hex[:8]}"
        else:
            chroma_dir = "./chroma_db"
    else:
        chroma_dir = "./chroma_db"

    # New vectorstore create pannuvom
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    chunks = splitter.split_text(text)

    vectorstore = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        persist_directory=chroma_dir
    )

    return UploadResponse(
        message="Resume uploaded and processed successfully!",
        filename=file.filename,
        chunks=len(chunks)
    )


# --- Chat Endpoint ---
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    global vectorstore

    # PDF upload aagala nu check pannuvom
    if vectorstore is None:
        # chroma_db already irukka load pannuvom
        if os.path.exists("./chroma_db"):
            embeddings = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2"
            )
            vectorstore = Chroma(
                persist_directory="./chroma_db",
                embedding_function=embeddings
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Please upload a resume first!"
            )
            # 400 — resume upload pannadhey nu solrom

    answer = get_llm_answer(request.question, vectorstore)

    return ChatResponse(answer=answer)


# ============================================
# Server Run — python main.py
# ============================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        # 0.0.0.0 — all network interfaces listen pannuvom
        # localhost matrum illa, network-laiyum access pannalaam

        port=8000,
        # localhost:8000 — la server run aagum

        reload=False
        # True — code change aana auto restart
        # Production-la False
    )

# if __name__ == "__main__":
#
#     if len(sys.argv) > 1:
#         # Command line-la file name kudutanga?
#         # python main.py myfile.pdf — ila
#
#         pdf_file = sys.argv[1]
#         # sys.argv[1] — second argument = pdf filename
#
#         print(f"Ingesting {pdf_file}...")
#         ingest(pdf_file)
#         print("\nNow starting chat...\n")
#
#     chat()
#     # Always chat mode start aagum