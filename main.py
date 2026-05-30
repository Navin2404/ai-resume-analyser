# main.py — FastAPI Backend Server

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
import re
import shutil
import time
import uuid

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
# FastEmbed everywhere — consistent!
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

load_dotenv()

app = FastAPI(
    title="AI Resume Analyzer API",
    description="Upload resume PDF and ask questions",
    version="1.0.0"
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}", "traceback": traceback.format_exc()}
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # * — any origin allow pannuvom
    # Vercel deploy aana piragu URL change aagum
    # Development + production rendu-laiyum work aagum
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vectorstore = None
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_embeddings():
    # One place-la define pannuvom — everywhere same!
    return FastEmbedEmbeddings(
        model_name="BAAI/bge-small-en-v1.5"
    )

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text()
    full_text = re.sub(r'(?<=[A-Za-z])\s(?=[A-Za-z])', '', full_text)
    full_text = re.sub(r'\n+', '\n', full_text)
    full_text = re.sub(r' +', ' ', full_text)
    return full_text

def get_llm_answer(question, vs):
    retriever = vs.as_retriever(search_kwargs={"k": 3})
    chunks = retriever.invoke(question)
    context = "\n\n".join([c.page_content for c in chunks])

    prompt = f"""You are an expert resume analyzer assistant.
Use only the context below to answer the question accurately.
If the answer is not found in context, say 'This information is not available in the resume.'

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

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

class UploadResponse(BaseModel):
    message: str
    filename: str
    chunks: int

@app.get("/")
def root():
    return {"status": "AI Resume Analyzer API Running!"}

@app.post("/upload", response_model=UploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    global vectorstore

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed!")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    text = extract_text_from_pdf(file_path)

    # Vectorstore release pannuvom
    vectorstore = None
    time.sleep(0.5)

    # Chroma DB delete pannuvom
    if os.path.exists("./chroma_db"):
        try:
            shutil.rmtree("./chroma_db")
            chroma_dir = "./chroma_db"
        except PermissionError:
            chroma_dir = f"./chroma_db_{uuid.uuid4().hex[:8]}"
    else:
        chroma_dir = "./chroma_db"

    # Chunks create pannuvom
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    chunks = splitter.split_text(text)

    # FastEmbed use pannuvom — lightweight!
    vectorstore = Chroma.from_texts(
        texts=chunks,
        embedding=get_embeddings(),
        persist_directory=chroma_dir
    )

    return UploadResponse(
        message="Resume uploaded and processed successfully!",
        filename=file.filename,
        chunks=len(chunks)
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    global vectorstore

    if vectorstore is None:
        if os.path.exists("./chroma_db"):
            vectorstore = Chroma(
                persist_directory="./chroma_db",
                embedding_function=get_embeddings()
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Please upload a resume first!"
            )

    answer = get_llm_answer(request.question, vectorstore)
    return ChatResponse(answer=answer)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)