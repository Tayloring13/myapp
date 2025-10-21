import pandas as pd
import chromadb

# -------------------------
# 1️⃣ EDIT THESE VARIABLES
# -------------------------
CSV_FILE = "temples_kamakura_v1.csv"  # Updated filename
COLLECTION_NAME = "temples_kamakura"   # Updated collection name
# -------------------------

# Load CSV safely
df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
df.columns = df.columns.str.strip()  # remove extra spaces from headers

# Connect to persistent Chroma database
client = chromadb.PersistentClient(path="./chroma_db")

# Delete existing collection if you want to start fresh (optional)
try:
    client.delete_collection(COLLECTION_NAME)
    print(f"🗑️ Deleted existing collection '{COLLECTION_NAME}'")
except:
    pass

# Create the collection
collection = client.create_collection(COLLECTION_NAME)

# Add rows to collection
for _, row in df.iterrows():
    doc_id = str(row.get("id", _))
    
    # ✨ CRITICAL: Combine ALL searchable fields into one document
    title = str(row.get("title", ""))
    content = str(row.get("content", ""))
    alt_names = str(row.get("alt-names", ""))
    context_triggers = str(row.get("context triggers", ""))
    sustainability_nudge = str(row.get("sustainability nudge", ""))
    
    # Create searchable document with all fields
    combined_document = f"""
Title: {title}
Content: {content}
Alternative Names: {alt_names}
Context: {context_triggers}
Sustainability: {sustainability_nudge}
    """.strip()
    
    # Keep metadata separate for structured access
    metadata = {
        "title": title,
        "alt-names": alt_names,
        "category": str(row.get("category", "")),
        "context_triggers": context_triggers,
        "sustainability_nudge": sustainability_nudge
    }

    collection.add(
        ids=[doc_id],
        documents=[combined_document],  # ← Now searches ALL fields!
        metadatas=[metadata]
    )

print(f"✅ {CSV_FILE} loaded into Chroma collection '{COLLECTION_NAME}'")
print(f"📊 Total entries: {len(df)}")