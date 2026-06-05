FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies into the system Python (no venv needed inside Docker)
RUN uv sync --frozen --no-dev --no-install-project

# Copy application source
COPY . .

# Make uv-installed binaries available on PATH
ENV PATH="/app/.venv/bin:$PATH"

# ChromaDB persists to a volume mounted at runtime
VOLUME ["/app/chroma_db"]

# 8000 = FastAPI backend, 8501 = Streamlit frontend
EXPOSE 8000 8501
