FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir -U uv

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN uv pip install --system -r requirements.txt

# Copy application code
COPY src/ ./src/

# Expose port
EXPOSE 8000

# Run server directly (secrets are loaded by endpoint_server.py)
CMD ["uvicorn", "src.endpoint_server:server.streamable_http_app", "--host", "0.0.0.0", "--port", "8000", "--lifespan", "on", "--proxy-headers", "--forwarded-allow-ips", "*"]
