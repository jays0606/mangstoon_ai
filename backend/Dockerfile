FROM python:3.12-slim

WORKDIR /app

# Install dependencies via pip (no uv in prod image)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY mangstoon_ai/ mangstoon_ai/

# Cloud Run injects PORT (default 8080)
ENV PORT=8080

EXPOSE ${PORT}

CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT}
