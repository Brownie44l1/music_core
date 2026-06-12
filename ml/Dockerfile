FROM python:3.11-slim

WORKDIR /app

# Install build dependencies for scikit-surprise
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies (cache mount preserves uv cache across builds)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -e .

# Copy application code and model
COPY app/ ./app/

ENV PORT=8001
EXPOSE $PORT

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload"]
