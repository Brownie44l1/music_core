FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies (cache mount preserves uv cache across builds)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -e .

# Copy application code
COPY app/ ./app/

ENV PORT=8000
EXPOSE $PORT

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
