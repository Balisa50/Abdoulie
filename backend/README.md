# Tesseract Backend

FastAPI backend service for the Tesseract SaaS MVP.

## Tech Stack

- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Primary database
- **Redis**: Caching and session storage
- **AWS SDK (boto3)**: S3 and SQS integration

## Development

### Install Dependencies

```bash
pip install uv
uv pip install -e ".[dev]"
```

### Run Locally

```bash
uvicorn app.main:app --reload
```

### Linting and Formatting

```bash
ruff check .
black .
mypy .
```

### Testing

```bash
pytest
```

## API Documentation

When the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
