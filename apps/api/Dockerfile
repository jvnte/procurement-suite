FROM python:3.13-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY data ./data

# Install dependencies
RUN uv sync --frozen

# Expose port
EXPOSE 8081

# Run the application
CMD ["uv", "run", "python", "-m", "asklio_api.main"]
