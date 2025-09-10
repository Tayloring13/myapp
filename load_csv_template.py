import pandas as pd
import chromadb

# -------------------------
# 1️⃣ EDIT THESE VARIABLES
# -------------------------
CSV_FILE = "TEMPLES.csv"        # Name of your CSV file
COLLECTION_NAME = "TEMPLES"  # Name for the Chroma collection
# -------------------------

# Load CSV safely
df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
df.columns = df.columns.str.strip()  # remove extra spaces from headers

# Connect to persistent Chroma database
client = chromadb.PersistentClient(path="./chroma_db")

# Create (or get) the collection
collection = client.get_or_create_collection(COLLECTION_NAME)

# Add rows to collection
for _, row in df.iterrows():
    doc_id = str(row.get("id", _))          # fallback to row index if no id column
    content = str(row.get("content", ""))   # default empty string if column missing
    metadata = {col: str(row[col]) for col in df.columns if col != "content"}

    collection.add(
        ids=[doc_id],
        documents=[content],
        metadatas=[metadata]
    )

print(f"✅ {CSV_FILE} loaded into Chroma collection '{COLLECTION_NAME}'")