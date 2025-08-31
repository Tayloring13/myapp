import os
import uvicorn
from fastapi import FastAPI, Query
from pydantic import BaseModel
import chromadb

app = FastAPI(title="Japanaut Chroma API")

# --- Ping route ---
@app.get("/ping")
def ping():
    return {"message": "pong"}

# --- Chroma setup ---
client = chromadb.PersistentClient(path="./chroma_db")

# Debug: list all collections (remove/comment after confirming)
print("Collections in Chroma DB:", [c.name for c in client.list_collections()])

# Get your collection
collection = client.get_collection("TEMPLES")

# --- Response model ---
class QueryResponse(BaseModel):
    query: str
    results: list

# --- Chroma query endpoint ---
@app.get("/query", response_model=QueryResponse)
def query_chroma(q: str = Query(..., description="The query text to search in Chroma")):
    try:
        # Search Chroma for top 3 relevant chunks
        results = collection.query(query_texts=[q], n_results=3)

        # Safely extract documents
        chunks = results.get('documents', [[]])[0] if results.get('documents') else []

        # Fallback if nothing found
        if not chunks:
            chunks = ["Sorry, I don’t have information on that topic yet."]

    except Exception as e:
        # Graceful error handling
        chunks = [f"An error occurred while querying the database: {str(e)}"]

    return QueryResponse(query=q, results=chunks)

# --- Uvicorn startup for Railway/local ---
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)