.PHONY: help up down build clean logs test lint format install

help:
	@echo "Tesseract SaaS MVP - Available commands:"
	@echo "  make up         - Start all services with docker compose"
	@echo "  make down       - Stop all services"
	@echo "  make build      - Build all Docker images"
	@echo "  make clean      - Remove all containers, volumes, and images"
	@echo "  make logs       - Show logs from all services"
	@echo "  make test       - Run tests for backend and frontend"
	@echo "  make lint       - Run linters for backend and frontend"
	@echo "  make format     - Format code for backend and frontend"
	@echo "  make install    - Install dependencies locally"

up:
	docker compose up -d
	@echo "Services are starting..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "API Docs: http://localhost:8000/docs"

down:
	docker compose down

build:
	docker compose build

clean:
	docker compose down -v --rmi all
	@echo "Cleaned up all containers, volumes, and images"

logs:
	docker compose logs -f

logs-backend:
	docker compose logs -f backend

logs-frontend:
	docker compose logs -f frontend

test:
	@echo "Running backend tests..."
	cd backend && pytest
	@echo "Running frontend tests..."
	cd frontend && npm test

lint:
	@echo "Linting backend..."
	cd backend && ruff check .
	@echo "Linting frontend..."
	cd frontend && npm run lint

format:
	@echo "Formatting backend..."
	cd backend && black . && ruff check --fix .
	@echo "Formatting frontend..."
	cd frontend && npm run lint -- --fix

install:
	@echo "Installing backend dependencies..."
	cd backend && pip install uv && uv pip install -e ".[dev]"
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Installing pre-commit hooks..."
	pre-commit install
