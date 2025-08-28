from fastapi import FastAPI
from .db import add_test_entry, query_test_entry

app = FastAPI()

@app.on_event("startup")
def startup_event():
    add_test_entry()  # Load one doc on startup

@app.get("/ask")
def ask(query: str):
    result = query_test_entry(query)
    return {"query": query, "result": result}