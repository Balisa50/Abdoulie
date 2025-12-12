# Development Guide

## Getting Started

### Prerequisites

Ensure you have the following installed:
- Docker Desktop (or Docker Engine + Docker Compose)
- Git
- (Optional) Python 3.11+
- (Optional) Node.js 20+

### Initial Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd tesseract
```

2. Copy environment files:
```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

3. Start the development environment:
```bash
docker compose up
```

## Development Workflow

### Making Changes

1. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes in the appropriate directory:
   - Backend changes: `backend/`
   - Frontend changes: `frontend/`
   - Infrastructure: `infra/`
   - Documentation: `docs/`

3. Test your changes locally:
```bash
make lint
make test
```

4. Commit your changes:
```bash
git add .
git commit -m "feat: add your feature description"
```

### Running Individual Services

#### Backend Only

```bash
cd backend
pip install uv
uv pip install -e ".[dev]"

# Start dependencies
docker compose up postgres redis localstack -d

# Run backend
uvicorn app.main:app --reload
```

#### Frontend Only

```bash
cd frontend
npm install

# Make sure backend is running
npm run dev
```

### Database Operations

#### Access PostgreSQL

```bash
docker compose exec postgres psql -U tesseract -d tesseract
```

#### Access Redis

```bash
docker compose exec redis redis-cli
```

### Working with LocalStack

#### Create S3 Bucket

```bash
aws --endpoint-url=http://localhost:4566 s3 mb s3://tesseract-uploads
```

#### Create SQS Queue

```bash
aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name tesseract-tasks
```

#### List Resources

```bash
aws --endpoint-url=http://localhost:4566 s3 ls
aws --endpoint-url=http://localhost:4566 sqs list-queues
```

## Code Style

### Python (Backend)

- Use Ruff for linting
- Use Black for formatting
- Use mypy for type checking
- Follow PEP 8 guidelines
- Write docstrings for public functions

### TypeScript (Frontend)

- Use ESLint for linting
- Follow the Next.js conventions
- Use TypeScript strict mode
- Prefer functional components with hooks

### Commit Messages

Follow conventional commits:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Test changes
- `chore:` - Build/tooling changes

## Testing

### Backend Tests

```bash
cd backend
pytest
pytest -v  # Verbose
pytest --cov=app tests/  # With coverage
pytest -k test_name  # Run specific test
```

### Frontend Tests

```bash
cd frontend
npm test
npm test -- --watch  # Watch mode
```

## Debugging

### Backend Debugging

Add breakpoints using `breakpoint()` in Python code. When running with Docker:

```bash
docker compose up backend
docker attach tesseract-backend
```

### Frontend Debugging

Use browser DevTools or VS Code debugger with the following configuration:

```json
{
  "type": "node",
  "request": "attach",
  "name": "Next.js",
  "port": 9229
}
```

## Common Issues

### Port Already in Use

```bash
# Find process using port
lsof -i :8000
# Kill process
kill -9 <PID>
```

### Docker Build Issues

```bash
# Clean build
docker compose down -v
docker compose build --no-cache
docker compose up
```

### Database Migration Issues

(To be implemented with Alembic)

## Performance Tips

- Use Docker build cache
- Mount volumes for hot reloading
- Use `docker compose up -d` to run in background
- Limit Docker resource usage in Docker Desktop settings

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [LocalStack Documentation](https://docs.localstack.cloud/)
