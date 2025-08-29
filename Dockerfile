FROM python:3.11-slim

# Prevents Python from writing .pyc files & ensures stdout/stderr are unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for building Python wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libffi-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps first (cache-friendly layer)
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy your app code
COPY app/ ./app

# Railway provides $PORT at runtime
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "${PORT}"]