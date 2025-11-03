FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY wsgi.py .

EXPOSE 5003

CMD ["gunicorn", "--bind", "0.0.0.0:5003", "--workers", "2", "--timeout", "60", "wsgi:app"]
