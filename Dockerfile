# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copy code
COPY app/ ./app/
COPY frontend/ ./frontend/
COPY data/ ./data/

# Prepare ChromaDB folder
RUN mkdir -p /app/data/chroma_db

# Expose ports
EXPOSE 8000 8501

# Default to a shell; overridden by docker-compose commands
CMD ["bash"]
