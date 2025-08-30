# Use a slim Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Start uvicorn without specifying a port
# The Python script handles PORT from environment
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]