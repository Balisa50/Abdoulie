# Tesseract Setup Checklist

Use this checklist to ensure your development environment is properly configured.

## Prerequisites

- [ ] Docker Desktop installed (or Docker Engine + Docker Compose)
- [ ] Git installed
- [ ] (Optional) Python 3.11+ for local backend development
- [ ] (Optional) Node.js 20+ for local frontend development

## Initial Setup

- [ ] Repository cloned
- [ ] Navigate to project directory: `cd tesseract`

## Environment Configuration

- [ ] Copy `.env.example` to `.env`
- [ ] Copy `backend/.env.example` to `backend/.env`
- [ ] Copy `frontend/.env.example` to `frontend/.env`
- [ ] Review and adjust environment variables if needed

## Docker Setup

- [ ] Verify Docker is running: `docker --version`
- [ ] Verify Docker Compose: `docker compose version`
- [ ] Validate docker-compose.yml: `docker compose config`
- [ ] Build images: `docker compose build` or `make build`
- [ ] Start services: `docker compose up` or `make up`

## Verification

- [ ] All services started successfully
- [ ] PostgreSQL is healthy: `docker compose ps postgres`
- [ ] Redis is healthy: `docker compose ps redis`
- [ ] LocalStack is healthy: `docker compose ps localstack`
- [ ] Backend is running: `curl http://localhost:8000/health`
- [ ] Frontend is accessible: Open http://localhost:3000 in browser
- [ ] API docs accessible: http://localhost:8000/docs

## Optional Local Development

### Backend (without Docker)
- [ ] Create virtual environment: `python3 -m venv venv`
- [ ] Activate venv: `source venv/bin/activate`
- [ ] Install dependencies: `pip install -e ".[dev]"`
- [ ] Run tests: `pytest`
- [ ] Run linter: `ruff check .`
- [ ] Run formatter: `black .`

### Frontend (without Docker)
- [ ] Install dependencies: `npm install`
- [ ] Run development server: `npm run dev`
- [ ] Run linter: `npm run lint`
- [ ] Run type check: `npx tsc --noEmit`

## Development Tools

- [ ] Install pre-commit: `pip install pre-commit`
- [ ] Install hooks: `pre-commit install`
- [ ] Test hooks: `pre-commit run --all-files`

## Testing the Setup

### Quick validation script
```bash
./validate.sh
```

### Quick start script
```bash
./quickstart.sh
```

### Manual tests
- [ ] Backend health check: `curl http://localhost:8000/health`
- [ ] Backend root: `curl http://localhost:8000/`
- [ ] Frontend loads in browser
- [ ] Frontend shows backend status
- [ ] API docs load: http://localhost:8000/docs

## Troubleshooting

If you encounter issues:

1. **Services won't start**
   ```bash
   make clean
   make build
   make up
   ```

2. **Port conflicts**
   - Check if ports are in use: `lsof -i :3000` (or :8000, :5432, etc.)
   - Modify port mappings in docker-compose.yml if needed

3. **Build failures**
   ```bash
   docker compose down -v
   docker compose build --no-cache
   docker compose up
   ```

4. **Permission issues**
   - Ensure Docker has proper permissions
   - On Linux, add user to docker group: `sudo usermod -aG docker $USER`

## Ready to Develop! 🚀

Once all checkboxes are complete, you're ready to start developing!

- Read [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for development workflow
- Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) to understand the system
- Read [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines
