# Tesseract SaaS MVP

A modern, full-stack SaaS application built with FastAPI, Next.js, and a comprehensive cloud infrastructure stack.

## 🏗️ Architecture

This is a monorepo containing all components of the Tesseract SaaS platform:

```
tesseract/
├── backend/          # FastAPI application
├── frontend/         # Next.js + TypeScript application
├── infra/            # Infrastructure as code (future)
├── docs/             # Documentation
└── docker-compose.yml # Local development stack
```

## 🚀 Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Primary database
- **Redis**: Caching and session storage
- **Boto3**: AWS SDK for S3 and SQS

### Frontend
- **Next.js 15**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **ESLint**: Code linting

### Infrastructure
- **Docker & Docker Compose**: Containerization
- **PostgreSQL 16**: Relational database
- **Redis 7**: In-memory data store
- **LocalStack**: Local AWS cloud stack (S3, SQS)

### Development Tools
- **uv**: Fast Python package installer
- **Ruff**: Lightning-fast Python linter
- **Black**: Python code formatter
- **pre-commit**: Git hooks framework
- **Makefile**: Task automation

## 📋 Prerequisites

- Docker & Docker Compose
- (Optional) Python 3.11+ for local backend development
- (Optional) Node.js 20+ for local frontend development

## 🛠️ Quick Start

### 1. Clone the repository

```bash
git clone <repository-url>
cd tesseract
```

### 2. Start all services

```bash
docker compose up
```

Or use the Makefile:

```bash
make up
```

### 3. Access the applications

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

### 4. Check health

The backend health endpoint: http://localhost:8000/health

```json
{
  "status": "healthy",
  "app": "Tesseract SaaS MVP",
  "version": "0.1.0",
  "timestamp": "2024-01-01T00:00:00.000000"
}
```

## 🔧 Development Workflow

### Environment Setup

Copy the example environment files:

```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### Using Make Commands

```bash
make help          # Show all available commands
make up            # Start all services
make down          # Stop all services
make build         # Build Docker images
make clean         # Remove all containers and volumes
make logs          # View logs from all services
make logs-backend  # View backend logs only
make logs-frontend # View frontend logs only
make lint          # Run linters
make format        # Format code
make test          # Run tests
```

### Backend Development

#### Run locally (without Docker)

```bash
cd backend
pip install uv
uv pip install -e ".[dev]"
uvicorn app.main:app --reload
```

#### Run tests

```bash
cd backend
pytest
```

#### Lint and format

```bash
cd backend
ruff check .
black .
mypy .
```

### Frontend Development

#### Run locally (without Docker)

```bash
cd frontend
npm install
npm run dev
```

#### Build for production

```bash
npm run build
npm start
```

#### Lint

```bash
npm run lint
```

## 🗄️ Services

### PostgreSQL
- **Port**: 5432
- **Database**: tesseract
- **User**: tesseract
- **Password**: tesseract

### Redis
- **Port**: 6379
- **URL**: redis://localhost:6379/0

### LocalStack
- **Port**: 4566
- **Services**: S3, SQS
- **Endpoint**: http://localhost:4566

To create S3 bucket and SQS queue:

```bash
aws --endpoint-url=http://localhost:4566 s3 mb s3://tesseract-uploads
aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name tesseract-tasks
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
pytest --cov=app tests/  # With coverage
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 🎨 Code Quality

### Pre-commit Hooks

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

Run manually:

```bash
pre-commit run --all-files
```

### Linting

**Backend:**
- Ruff for linting
- Black for formatting
- mypy for type checking

**Frontend:**
- ESLint for linting
- Built-in TypeScript type checking

## 📚 API Documentation

Once the backend is running, interactive API documentation is available:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🐳 Docker Services

The `docker-compose.yml` defines the following services:

1. **postgres** - PostgreSQL database
2. **redis** - Redis cache
3. **localstack** - Local AWS services
4. **backend** - FastAPI application
5. **frontend** - Next.js application

All services include health checks and proper dependency management.

## 📁 Project Structure

```
tesseract/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI application entry
│   │   ├── settings.py      # Configuration management
│   │   └── routers/
│   │       └── health.py    # Health check endpoints
│   ├── tests/               # Backend tests
│   ├── Dockerfile
│   ├── pyproject.toml       # Python dependencies
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js App Router
│   │   │   ├── page.tsx     # Home page
│   │   │   └── layout.tsx   # Root layout
│   │   └── components/      # React components
│   ├── public/              # Static assets
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   └── README.md
├── infra/                   # Infrastructure as code (future)
├── docs/                    # Documentation
├── docker-compose.yml
├── Makefile
├── .pre-commit-config.yaml
├── .gitignore
└── README.md
```

## 🔐 Environment Variables

See `.env.example`, `backend/.env.example`, and `frontend/.env.example` for all available configuration options.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `AWS_ENDPOINT_URL` - LocalStack endpoint (or real AWS)
- `NEXT_PUBLIC_API_URL` - Backend API URL for frontend

## 🚢 Deployment

(Future sections for production deployment)

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

Quick guide:
1. Create a feature branch
2. Make your changes
3. Run tests and linters
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Services won't start

```bash
make clean
make build
make up
```

### Port conflicts

If ports 3000, 8000, 5432, 6379, or 4566 are in use, modify the port mappings in `docker-compose.yml`.

### Frontend can't connect to backend

Check that:
1. Backend is running: `curl http://localhost:8000/health`
2. CORS settings allow your origin in `backend/app/settings.py`
3. `NEXT_PUBLIC_API_URL` is set correctly

### Database connection issues

Ensure PostgreSQL is healthy:

```bash
docker compose ps postgres
docker compose logs postgres
```

## 📞 Support

For issues and questions, please open an issue in the repository.
