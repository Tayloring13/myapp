import os
import uvicorn
from fastapi import FastAPI, Query
from pydantic import BaseModel
import chromadb
import pandas as pd
from chromadb.errors import InvalidCollectionException

app = FastAPI(title="Japanaut Chroma API")

# --- Ping route ---
@app.get("/ping")
def ping():
    return {"message": "pong"}

# --- Chroma setup ---
client = chromadb.PersistentClient(path="./chroma_db")

# Ensure collection exists
try:
    collection = client.get_collection("TEMPLES")
    print("Collections in Chroma DB:", [c.name for c in client.list_collections()])
except InvalidCollectionException:
    print("TEMPLES collection not found, loading CSV...")
    # Load CSV
    CSV_FILE = "./TEMPLES.csv"
    df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    collection = client.get_or_create_collection("TEMPLES")
    for _, row in df.iterrows():
        doc_id = str(row.get("id", _))
        content = str(row.get("content", ""))
        metadata = {col: str(row[col]) for col in df.columns if col != "content"}
        collection.add(ids=[doc_id], documents=[content], metadatas=[metadata])
    print(f"✅ {CSV_FILE} loaded into Chroma collection 'TEMPLES'")

# --- Response model ---
class QueryResponse(BaseModel):
    query: str
    results: list

# --- Chroma query endpoint ---
@app.get("/query", response_model=QueryResponse)
def query_chroma(q: str = Query(..., description="The query text to search in Chroma")):
    try:
        results = collection.query(query_texts=[q], n_results=3)
        chunks = results.get('documents', [[]])[0] if results.get('documents') else []
        if not chunks:
            chunks = ["Sorry, I don’t have information on that topic yet."]
    except Exception as e:
        chunks = [f"An error occurred while querying the database: {str(e)}"]
    return QueryResponse(query=q, results=chunks)

# --- Uvicorn startup ---
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)