#!/bin/bash

set -e

echo "=== Validating Tesseract Monorepo Setup ==="
echo ""

# Check directory structure
echo "✓ Checking directory structure..."
for dir in backend frontend infra docs; do
    if [ -d "$dir" ]; then
        echo "  ✓ $dir/ exists"
    else
        echo "  ✗ $dir/ missing"
        exit 1
    fi
done

# Check key files
echo ""
echo "✓ Checking key files..."
for file in "docker-compose.yml" "Makefile" ".gitignore" "README.md" ".pre-commit-config.yaml"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file exists"
    else
        echo "  ✗ $file missing"
        exit 1
    fi
done

# Check backend structure
echo ""
echo "✓ Checking backend structure..."
for file in "backend/Dockerfile" "backend/pyproject.toml" "backend/app/main.py" "backend/app/settings.py"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file exists"
    else
        echo "  ✗ $file missing"
        exit 1
    fi
done

# Check frontend structure
echo ""
echo "✓ Checking frontend structure..."
for file in "frontend/Dockerfile" "frontend/package.json" "frontend/next.config.ts" "frontend/src/app/page.tsx"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file exists"
    else
        echo "  ✗ $file missing"
        exit 1
    fi
done

# Validate Python syntax
echo ""
echo "✓ Validating Python syntax..."
cd backend
python3 -m py_compile app/*.py app/routers/*.py tests/*.py
echo "  ✓ All Python files are valid"
cd ..

# Validate TypeScript
echo ""
echo "✓ Validating TypeScript..."
cd frontend
npx tsc --noEmit > /dev/null 2>&1
echo "  ✓ TypeScript compiles successfully"
cd ..

# Validate docker-compose syntax
echo ""
echo "✓ Validating docker-compose.yml..."
docker compose config > /dev/null 2>&1
echo "  ✓ docker-compose.yml is valid"

echo ""
echo "==================================="
echo "✓ All validations passed!"
echo "==================================="
echo ""
echo "To start the services, run:"
echo "  docker compose up"
echo ""
echo "Or use the Makefile:"
echo "  make up"
