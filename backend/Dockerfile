FROM python:3.12-slim

WORKDIR /app

# WeasyPrint system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 \
    libffi-dev libcairo2 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY . .

# Non-root user for security
RUN adduser --disabled-password --no-create-home appuser && \
    mkdir -p /app/uploads && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
