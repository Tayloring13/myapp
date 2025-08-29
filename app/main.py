import os
import uvicorn
from fastapi import FastAPI
from app.db import add_test_entry, query_test_entry

app = FastAPI()

@app.on_event("startup")
def startup_event():
    try:
        add_test_entry()
    except Exception as e:
        print(f"[Startup error] {e}")

@app.get("/ask")
def ask(query: str):
    try:
        result = query_test_entry(query)
        return {"query": query, "result": result}
    except Exception as e:
        return {"query": query, "error": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)