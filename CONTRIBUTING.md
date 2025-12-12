# Contributing to Tesseract

Thank you for your interest in contributing to Tesseract! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone <your-fork-url>`
3. Create a feature branch: `git checkout -b feature/your-feature`
4. Make your changes
5. Test your changes
6. Submit a pull request

## Development Setup

See the main [README.md](README.md) and [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for detailed setup instructions.

Quick start:
```bash
docker compose up
```

## Code Style

### Python (Backend)
- Follow PEP 8
- Use type hints
- Use Ruff for linting
- Use Black for formatting
- Write docstrings for public APIs

### TypeScript (Frontend)
- Use ESLint
- Follow the Next.js conventions
- Use TypeScript strict mode
- Write meaningful component names

## Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Test changes
- `chore:` - Build process or auxiliary tool changes

Examples:
```
feat: add user authentication
fix: resolve database connection timeout
docs: update API documentation
```

## Testing

### Backend
```bash
cd backend
pytest
pytest --cov=app tests/  # With coverage
```

### Frontend
```bash
cd frontend
npm test
```

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Ensure linting passes
5. Update the README.md if needed
6. Request review from maintainers

## Code Review

All submissions require review. We use GitHub pull requests for this purpose.

## Reporting Issues

When reporting issues, please include:
- A clear description of the problem
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, Docker version, etc.)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
