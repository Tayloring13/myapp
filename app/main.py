import os
import uvicorn
from fastapi import FastAPI

app = FastAPI()

# Example route
@app.get("/ping")
def ping():
    return {"message": "pong"}

if __name__ == "__main__":
    # Get the port Railway sets, default to 8000 locally
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)