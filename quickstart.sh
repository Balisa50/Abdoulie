#!/bin/bash

set -e

echo "╔════════════════════════════════════════╗"
echo "║   Tesseract SaaS MVP - Quick Start     ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    echo "❌ Error: Docker Compose is not available"
    echo "Please ensure you have Docker Compose installed"
    exit 1
fi

echo "✓ Docker is installed"
echo "✓ Docker Compose is available"
echo ""

# Copy environment files if they don't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✓ .env created from .env.example"
fi

if [ ! -f backend/.env ]; then
    echo "📝 Creating backend/.env file..."
    cp backend/.env.example backend/.env
    echo "✓ backend/.env created"
fi

if [ ! -f frontend/.env ]; then
    echo "📝 Creating frontend/.env file..."
    cp frontend/.env.example frontend/.env
    echo "✓ frontend/.env created"
fi

echo ""
echo "🚀 Starting services with Docker Compose..."
echo "This may take a few minutes on first run..."
echo ""

docker compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

echo ""
echo "╔════════════════════════════════════════╗"
echo "║          Services are ready!           ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "🌐 Access your applications:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "📊 Check service status:"
echo "   docker compose ps"
echo ""
echo "📝 View logs:"
echo "   docker compose logs -f"
echo ""
echo "🛑 Stop services:"
echo "   docker compose down"
echo ""
echo "For more commands, see the Makefile or run 'make help'"
