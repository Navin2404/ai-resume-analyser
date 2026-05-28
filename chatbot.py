# ============================================
# chatbot.py — Questions kekuvom, answers vaanguvom
# ============================================

import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
# OpenAIEmbeddings → HuggingFaceEmbeddings change pannuvom
# ingest.py-la use pannana same model use pannanum!

from langchain_chroma import Chroma
# langchain_community → langchain_chroma change pannuvom
# Warning fix aagum

from langchain_groq import ChatGroq

# from langchain_google_genai import ChatGoogleGenerativeAI
# OpenAI → Gemini change pannuvom

load_dotenv()


# ============================================
# Function 1: Already stored DB-a load pannuvom
# ============================================
def load_vectordb():

    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
        # ingest.py-la use pannana SAME model!
        # Different model use panna vectors match aagaadhu
    )

    vectorstore = Chroma(
        persist_directory="./chroma_db",
        # ingest.py save panna same folder
        embedding_function=embeddings
    )

    print("Vector DB loaded!")
    return vectorstore


# ============================================
# Function 2: Question kekki answer vaanguvom
# ============================================
def get_answer(question, vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    relevant_chunks = retriever.invoke(question)
    print("\n--- DEBUG: Retrieved Chunks ---")
    for i, chunk in enumerate(relevant_chunks):
        print(f"Chunk {i + 1}: {chunk.page_content[:200]}")
    print("--- END DEBUG ---\n")

    context = "\n\n".join([c.page_content for c in relevant_chunks])

    prompt = f"""You are a helpful resume analyzer assistant.
Use only the context below to answer the question.
If answer is not in context, say 'I dont know'.

Context:
{context}

Question: {question}
Answer:"""

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        # Free, fast, GPT-4 level performance!
        api_key=os.getenv("GROQ_API_KEY")
    )

    response = llm.invoke(prompt)
    return response.content

def chat():
    print("\n=== Resume Analyzer Ready! ===")
    print("'quit' type panni exit pannalaam\n")

    vectorstore = load_vectordb()

    while True:
        question = input("You: ").strip()

        if question.lower() == "quit":
            print("Bye bro!")
            break

        if not question:
            continue

        answer = get_answer(question, vectorstore)
        print(f"\nBot: {answer}\n")

if __name__ == "__main__":
    chat()
# ============================================
# Function 3: Chat loop — continue conversation
# ============================================
def chat():
    print("\n=== PDF Chatbot Ready! ===")
    print("'quit' type panni exit pannalaam\n")

    vectorstore = load_vectordb()
    # Once load panna — every question-ku reload venaam
    # Memory-la keep pannuvom — fast!

    while True:
        # Infinite loop — user quit solluvaraikkum

        question = input("You: ").strip()
        # input() — user keyboard type pannuvom
        # .strip() — extra spaces remove pannuvom
        # "  Hello  " → "Hello"

        if question.lower() == "quit":
            # .lower() — uppercase handle pannuvom
            # "QUIT", "Quit", "quit" — ellame work
            print("Bye bro! Vanakkam!")
            break
            # while loop exit pannuvom

        if not question:
            # Empty string check — just Enter panna
            continue
            # Skip panni next iteration

        print("\nBot: ", end="")
        # end="" — newline venaam, answer same line-la

        answer = get_answer(question, vectorstore)
        print(answer)
        print()
        # Extra blank line — readability-ku


if __name__ == "__main__":
    chat()