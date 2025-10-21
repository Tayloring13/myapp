import chromadb
import pandas as pd

# Connect to local Chroma DB
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("temples_kamakura")

# Check what's in the collection
print("=" * 60)
print("📊 CHROMA DATABASE STATUS")
print("=" * 60)
print(f"Collection name: {collection.name}")
print(f"Total documents: {collection.count()}")
print()

# Get all IDs to see which temples are loaded
all_data = collection.get()
ids = sorted([int(id) for id in all_data['ids']])
print(f"Temple IDs in Chroma: {ids}")
print()

# Check if we're missing any IDs from 1-49
expected_ids = set(range(1, 50))
loaded_ids = set(ids)
missing_ids = expected_ids - loaded_ids
if missing_ids:
    print(f"⚠️ Missing temple IDs: {sorted(missing_ids)}")
else:
    print("✅ All 49 temples loaded!")
print()

# Compare with CSV
df = pd.read_csv('temples_kamakura_v1.csv', encoding='utf-8-sig')
csv_ids = sorted(df['id'].tolist())
print(f"Temple IDs in CSV: {len(csv_ids)} entries")
print(f"CSV IDs: {csv_ids}")
print()

# Test search across different fields
print("=" * 60)
print("🔍 TESTING SEARCH FUNCTIONALITY")
print("=" * 60)

test_searches = [
    ("Title search", "Great Buddha"),
    ("Japanese alt-name", "鶴岡八幡宮"),
    ("Context trigger", "Kannon statue"),
    ("Sustainability nudge", "walk instead of taxi"),
]

for search_type, query in test_searches:
    print(f"\n--- {search_type}: '{query}' ---")
    results = collection.query(
        query_texts=[query],
        n_results=3
    )
    
    if results['documents'][0]:
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        )):
            print(f"\nResult {i+1} (distance: {distance:.4f}):")
            print(f"  Title: {metadata.get('title', 'N/A')}")
            print(f"  Category: {metadata.get('category', 'N/A')}")
            # Show first 150 chars of document
            print(f"  Document preview: {doc[:150]}...")
    else:
        print("  ❌ No results found!")

print("\n" + "=" * 60)
print("✅ Local Chroma test complete!")
print("=" * 60)