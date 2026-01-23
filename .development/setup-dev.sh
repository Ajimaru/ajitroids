#!/bin/bash
# Setup script for development environment
# Installs pre-commit hooks and development dependencies

set -e

echo "🚀 Setting up ajitroids development environment..."

# Check if Python is available and meets the minimum version requirement
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10+."
    exit 1
fi

# Verify Python version is >= 3.10
PY_VER=$(python3 -c 'import sys; print("{}.{}".format(*sys.version_info[:2]))')
PY_MAJOR=$(python3 -c 'import sys; print(sys.version_info[0])')
PY_MINOR=$(python3 -c 'import sys; print(sys.version_info[1])')
if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
    echo "❌ Detected Python $PY_VER. ajitroids requires Python 3.10+."
    exit 1
fi

# Create/activate venv if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Activating virtual environment..."
# Try unix-style activate first, then windows-style. Do not swallow errors.
if [ -f "venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    # shellcheck disable=SC1091
    source venv/Scripts/activate
fi

# Verify virtualenv activation to avoid accidental global installs
if [ -z "$VIRTUAL_ENV" ]; then
    # Fallback check: compare python's sys.prefix basename to 'venv'
    PREFIX=$(python3 -c 'import sys,os; print(os.path.basename(sys.prefix))' 2>/dev/null || echo unknown)
    if [ "$PREFIX" != "venv" ]; then
        echo "❌ Failed to activate virtualenv (VIRTUAL_ENV unset, python prefix: $PREFIX)."
        echo "Please run: source venv/bin/activate (or venv/Scripts/activate) and re-run this script."
        exit 1
    fi
fi

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
