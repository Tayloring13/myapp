import os
import uvicorn
from fastapi import FastAPI, Query
from pydantic import BaseModel
import chromadb
import pandas as pd
from openai import OpenAI

app = FastAPI()

# --- Chroma setup ---
CSV_FILE = "./TEMPLES.csv"
COLLECTION_NAME = "TEMPLES"
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Preload collection at startup
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

# --- Response model for GPT-4 endpoint ---
class LLMResponse(BaseModel):
    query: str
    response: str

# --- GPT-4 powered /query endpoint ---
@app.get("/query", response_model=LLMResponse)
def query_chroma_llm(q: str = Query(..., description="Query text")):
    try:
        # Step 0: check API key
        OPENAI_KEY = os.getenv("OPENAI_API_KEY")
        if not OPENAI_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is missing!")

        client = OpenAI(api_key=OPENAI_KEY)

        # Step 1: retrieve top Chroma chunks
        results = collection.query(query_texts=[q], n_results=3)
        chunks = results['documents'][0] if 'documents' in results else []
        if not chunks:
            chunks = ["Sorry, I don’t have information on that topic yet."]

        # Step 2: prepare prompt for GPT-4
        prompt = (
            "You are a friendly Japanese travel guide. Use the following info to answer the user's question:\n\n"
            f"{chr(10).join(chunks)}\n\n"
            f"User question: {q}\n\nAnswer naturally and helpfully."
        )

        # Step 3: call OpenAI GPT-4 using new API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful Japanese travel guide."},
                {"role": "user", "content": prompt}
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