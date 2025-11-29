# Agent API

FastAPI server for document processing and extraction.

## Features

- PDF file upload and processing
- Document to binary conversion
- RESTful API endpoints

## Endpoints

- `POST /agent/intake` - Upload and process PDF documents

## Development

```bash
# Install dependencies
uv sync

# Run the server
uv run python -m agent_api.main

# Run tests
uv run pytest
```
