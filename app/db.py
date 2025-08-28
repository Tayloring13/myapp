import chromadb
from chromadb.config import Settings

# Create a persistent client (stores DB in ./chroma directory)
client = chromadb.PersistentClient(path="./chroma")

# Make or get a collection
collection = client.get_or_create_collection("my_collection")

def add_test_entry():
    collection.add(
        documents=["Hello from Chroma in Railway!"],
        ids=["test1"]
    )

def query_test_entry(query: str):
    return collection.query(
        query_texts=[query],
        n_results=1
    )