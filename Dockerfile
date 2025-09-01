FROM python:3.11-slim

WORKDIR /app

# Copy dependencies first
COPY requirements.txt .

# Copy the CSV explicitly from the build context
COPY ./TEMPLES.csv ./TEMPLES.csv

# Copy the app folder
COPY ./app ./app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python", "-m", "app.main"]