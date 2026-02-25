FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p chroma_db

# Cloud Run listens on $PORT (usually 8080)
EXPOSE 8080

ENV PYTHONUNBUFFERED=1

# Run gunicorn with the app instance from app.py
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 2 --threads 4 app:app"]