# ============================================
# ingest.py — PDF-a Vector DB-la store pannuvom
# ============================================

# --- Line 1-5: Imports ---
import os
# os — Operating System functions use pannuvom
# Example: environment variables read pannuvom

from dotenv import load_dotenv
# dotenv — .env file-la irukka secrets load pannuvom
# OPENAI_API_KEY automatically available aagum

from pypdf import PdfReader
import re
# pypdf — PDF file open panni text extract pannuvom
# Word doc maari PDF-a read panna

from langchain_text_splitters import RecursiveCharacterTextSplitter
# LangChain-oda text splitter — periya text-a
# small chunks-a cut pannuvom (500 chars씩)

from langchain_openai import OpenAIEmbeddings
# OpenAI-oda embedding model — text-a numbers-a
# convert pannuvom (vectors)

from langchain_chroma import Chroma

from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
# from langchain_huggingface import HuggingFaceEmbeddings

# ChromaDB — vectors store pannra database
# similarity search support pannudhu

# --- Line 7: .env load ---
load_dotenv()


# .env file-la irukka OPENAI_API_KEY-a
# os.environ-la load pannuvom
# Ipa os.getenv("OPENAI_API_KEY") use pannalaam

# ============================================
# Function 1: PDF read pannuvom
# ============================================
def load_pdf(pdf_path):
    # pdf_path — "my_doc.pdf" maari file location

    reader = PdfReader(pdf_path)
    # PdfReader — PDF file-a open pannuvom
    # reader.pages — all pages list

    full_text = ""
    # Empty string — text accumulate pannuvom

    for page in reader.pages:
        # oru oru page loop pannuvom
        full_text += page.extract_text()
        # Page-la irukka text extract panni
        # full_text-la append pannuvom
        # += means: full_text = full_text + new_text

        # NEW — spaced text clean pannuvom!
        # "N A V E E N" → "NAVEEN"
        full_text = re.sub(r'(?<=[A-Za-z])\s(?=[A-Za-z])', '', full_text)
        # Extra whitespace/newlines clean pannuvom
        full_text = re.sub(r'\n+', '\n', full_text)
        full_text = re.sub(r' +', ' ', full_text)

        print(f"Extracted {len(full_text)} characters")
        print("\n--- CLEANED TEXT PREVIEW ---")
        print(full_text[:300])  # sariya clean aagudha paakuvom
        print("---")

    print(f"Extracted {len(full_text)} characters")
    # len() — string length count pannuvom
    # f-string — variable embed pannuvom

    return full_text
    # Extracted text return pannuvom


# ============================================
# Function 2: Text-a chunks-a split pannuvom
# ============================================
def split_into_chunks(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        # Oru chunk max 500 characters
        # Why? LLM-ku context window limit irukku
        # Full doc once-la kudukka mudiyaadhu

        chunk_overlap=50,
        # Adjacent chunks 50 chars share pannuvom
        # Why? Sentence middle-la cut aaidha
        # context miss aagaama overlap vaikuvom
    )

    chunks = splitter.split_text(text)
    # text → ["chunk1", "chunk2", "chunk3"...]
    # List of strings return pannuvom

    print(f"Created {len(chunks)} chunks")
    return chunks


# ============================================
# Function 3: Chunks embed panni DB-la store
# ============================================
# def store_in_vectordb(chunks):
#     embeddings = OpenAIEmbeddings()
#     # OpenAI text-embedding-ada-002 model use aagum
#     # "Hello world" → [0.023, -0.412, 0.891, ...]
#     # 1536 numbers — oru sentence represent pannuvom
#     # Similar sentences — similar numbers!
#
#     vectorstore = Chroma.from_texts(
#         texts=chunks,
#         # Store pannra text list
#
#         embedding=embeddings,
#         # Epdi embed pannuvom nu specify
#
#         persist_directory="./chroma_db"
#         # Disk-la save pannra folder
#         # Program close aanalum data irukum
#     )
#
#     print("Vector DB-la successfully stored!")
#     return vectorstore


def store_in_vectordb(chunks):

    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
        cache_folder="/tmp/embeddings"  # Render-la /tmp use pannuvom
    )
    # embeddings = HuggingFaceEmbeddings(
    #     model_name="all-MiniLM-L6-v2"
    #     # 100% free, local-a run aagum
    #     # First time 80MB download aagum — one time only
    # )

    vectorstore = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    print("Vector DB stored!")
    return vectorstore




# ============================================
# Main function: Ellame oru jagathla run
# ============================================
def ingest(pdf_path):
    print(f"Loading PDF: {pdf_path}")
    text = load_pdf(pdf_path)  # Step 1
    chunks = split_into_chunks(text)  # Step 2
    store_in_vectordb(chunks)  # Step 3
    print("Ingestion complete!")


# ============================================
# Entry point — direct run aana matrum execute
# ============================================
import os

if __name__ == "__main__":
    # Project folder-la irukka first PDF auto-detect pannuvom
    pdf_files = [f for f in os.listdir(".") if f.endswith(".pdf")]

    if pdf_files:
        print(f"Found PDF: {pdf_files[0]}")
        ingest(pdf_files[0])
    else:
        print("Bro! PDF file project folder-la paste pannu first!")
        print(f"Folder: {os.getcwd()}")