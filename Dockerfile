FROM python:3.11-slim

WORKDIR /app

# Copy dependencies first
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the CSV and the app
COPY TEMPLES.csv ./TEMPLES.csv
COPY app ./app

# Preload Chroma collection at build time (optional: build-time preload)
RUN python -c "import pandas as pd, chromadb; \
    df=pd.read_csv('./TEMPLES.csv', encoding='utf-8-sig'); \
    client=chromadb.PersistentClient(path='./chroma_db'); \
    col=client.get_or_create_collection('TEMPLES'); \
    [col.add(ids=[str(i)], documents=[str(row['content'])], metadatas={c:str(row[c]) for c in df.columns if c!='content'}) for i,row in df.iterrows()]"

EXPOSE 8000

CMD ["python", "-m", "app.main"]