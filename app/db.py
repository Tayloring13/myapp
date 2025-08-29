import os
import chromadb
from chromadb.config import Settings

# Directory for persistent DB (fallback to in-memory if not writable)
CHROMA_PATH = "./chroma"

def get_client():
    try:
        return chromadb.PersistentClient(path=CHROMA_PATH)
    except Exception as e:
        print(f"[Chroma warning] Falling back to in-memory client: {e}")
        return chromadb.Client(Settings())  # In-memory fallback

client = get_client()
collection = client.get_or_create_collection("my_collection")


def add_test_entry():
    try:
        collection.add(
            documents=["Hello from Chroma in Railway!"],
            ids=["test1"]
        )
    except Exception as e:
        print(f"[Chroma error] Could not add entry: {e}")


def query_test_entry(query: str):
    try:
        return collection.query(
            query_texts=[query],
            n_results=1
        )
    except Exception as e:
        return {"error": str(e)}