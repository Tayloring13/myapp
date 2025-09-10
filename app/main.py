import os
import uvicorn
from fastapi import FastAPI, Query
from pydantic import BaseModel
import chromadb
import pandas as pd
from openai import OpenAI
from threading import Lock

from app.prompts import JAPANAUT_PROMPT

app = FastAPI()

# --- Global variables ---
CSV_FILE = "./TEMPLES.csv"
COLLECTION_NAME = "TEMPLES"
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = None
collection_lock = Lock()  # Ensure thread-safe lazy initialization

# Choose model via env var if you want to change later
MODEL = os.getenv("OPENAI_MODEL", "gpt-4.0-mini")

# --- Response model for GPT-4 endpoint ---
class LLMResponse(BaseModel):
    query: str
    response: str

# --- GPT-powered /query endpoint ---
@app.get("/query", response_model=LLMResponse)
def query_chroma_llm(q: str = Query(..., description="Query text")):
    global collection

    try:
        # Step 0: check API key
        OPENAI_KEY = os.getenv("OPENAI_API_KEY")
        if not OPENAI_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is missing!")
        client = OpenAI(api_key=OPENAI_KEY)

        # Step 1: lazy Chroma initialization
        with collection_lock:
            if collection is None:
                try:
                    collection = chroma_client.get_collection(COLLECTION_NAME)
                except chromadb.errors.InvalidCollectionException:
                    df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
                    df.columns = df.columns.str.strip()
                    collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
                    for _, row in df.iterrows():
                        doc_id = str(row.get("id", _))
                        content = str(row.get("content", ""))
                        metadata = {col: str(row[col]) for col in df.columns if col != "content"}
                        collection.add(ids=[doc_id], documents=[content], metadatas=[metadata])
                    print(f"✅ {CSV_FILE} loaded into Chroma collection '{COLLECTION_NAME}'")

        # Step 2: retrieve top Chroma chunks
        results = collection.query(query_texts=[q], n_results=3)
        chunks = results.get('documents', [[]])[0]
        if not chunks:
            chunks = ["Sorry, I don’t have information on that topic yet."]

        # Step 3: prepare user message (context + user question)
        context_text = chr(10).join(chunks)
        user_message = (
            "Use the following extracted notes to answer the user's question.\n\n"
            f"{context_text}\n\n"
            f"User question: {q}\n\n"
            "Answer naturally and helpfully in Japanaut's voice."
        )

        # Step 4: call OpenAI Chat API with system prompt = JAPANAUT_PROMPT
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": JAPANAUT_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=300
        )

        answer = response.choices[0].message.content.strip()

    except Exception as e:
        answer = f"An error occurred: {str(e)}"

    return LLMResponse(query=q, response=answer)

# --- Root route for Railway health checks ---
@app.get("/")
def root():
    return {"status": "ok"}

# --- Ping route ---
@app.get("/ping")
def ping():
    return {"message": "pong"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)