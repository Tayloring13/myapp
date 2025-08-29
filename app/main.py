from fastapi import FastAPI
from app.db import add_test_entry, query_test_entry  # absolute import is safer

app = FastAPI()


@app.on_event("startup")
def startup_event():
    try:
        add_test_entry()  # Load one doc on startup
    except Exception as e:
        # Prevents whole app from crashing if DB init fails
        print(f"[Startup error] Could not add test entry: {e}")


@app.get("/ask")
def ask(query: str):
    try:
        result = query_test_entry(query)
        return {"query": query, "result": result}
    except Exception as e:
        return {"query": query, "error": str(e)}