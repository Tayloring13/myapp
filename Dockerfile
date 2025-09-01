FFROM python:3.11-slim

WORKDIR /app

# Copy all files needed first
COPY requirements.txt .
COPY TEMPLES.csv ./TEMPLES.csv
COPY app ./app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python", "-m", "app.main"]