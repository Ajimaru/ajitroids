#!/bin/bash
# Setup script for development environment
# Installs pre-commit hooks and development dependencies

set -e

echo "🚀 Setting up ajitroids development environment..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10+."
    exit 1
fi

# Create/activate venv if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Activating virtual environment..."
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null || true

echo "📦 Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -r requirements-docs.txt

echo "🪝 Installing pre-commit hooks..."
pip install pre-commit
pre-commit install

echo "✅ Development environment setup complete!"
echo "💡 Pre-commit hooks are now active. They will run on git commit."
echo "   To run hooks manually on all files: pre-commit run --all-files"
