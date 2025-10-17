# Use specific tag for reproducibility
FROM python:3.11.5-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# system deps, add nonroot user
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential gcc libpq-dev \
 && useradd --create-home --shell /bin/bash appuser \
 && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock* /app/
# If using pip requirements, COPY requirements.txt /app/

# Install dependencies (if using pip)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . /app
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s \
  CMD curl -f http://localhost:8000/healthz || exit 1

CMD ["uvicorn", "pipetrack.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
