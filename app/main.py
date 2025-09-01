import os
import uvicorn
from fastapi import FastAPI, Query
from pydantic import BaseModel
import chromadb
import pandas as pd

app = FastAPI()

# --- Root route for Railway health checks ---
@app.get("/")
def root():
    return {"status": "ok"}

# --- Ping route ---
@app.get("/ping")
def ping():
    return {"message": "pong"}

# --- Response model for clarity ---
class QueryResponse(BaseModel):
    query: str
    results: list

# --- Lazy-loaded Chroma setup ---
chroma_client = None
collection = None
CSV_FILE = "./TEMPLES.csv"
COLLECTION_NAME = "TEMPLES"

def get_collection():
    global chroma_client, collection
    if collection is not None:
        return collection

    # Connect to persistent Chroma DB
    chroma_client = chromadb.PersistentClient(path="./chroma_db")

    # Try to get the collection
    try:
        collection = chroma_client.get_collection(COLLECTION_NAME)
    except chromadb.errors.InvalidCollectionException:
        # Collection not found → load CSV
        df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
        df.columns = df.columns.str.strip()

        collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
        for _, row in df.iterrows():
            doc_id = str(row.get("id", _))
            content = str(row.get("content", ""))
            metadata = {col: str(row[col]) for col in df.columns if col != "content"}

            collection.add(
                ids=[doc_id],
                documents=[content],
                metadatas=[metadata]
            )
        print(f"✅ {CSV_FILE} loaded into Chroma collection '{COLLECTION_NAME}'")
    return collection

# --- Chroma query endpoint ---
@app.get("/query", response_model=QueryResponse)
def query_chroma(q: str = Query(..., description="The query text to search in Chroma")):
    col = get_collection()
    try:
        results = col.query(query_texts=[q], n_results=3)
        chunks = results['documents'][0] if 'documents' in results else []
        if not chunks:
            chunks = ["Sorry, I don’t have information on that topic yet."]
    except Exception as e:
        chunks = [f"An error occurred while querying the database: {str(e)}"]

    return QueryResponse(query=q, results=chunks)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)