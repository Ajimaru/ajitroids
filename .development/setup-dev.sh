#!/bin/bash
# Setup script for development environment
# Installs pre-commit hooks and development dependencies

set -e

echo "🚀 Setting up ajitroids development environment..."

# Resolve directories so the script works no matter where it's called from.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"

# Supported interpreter range. The upper bound is not cosmetic: pygame has no
# prebuilt wheel beyond MAX_MINOR yet, and on a newer interpreter its font
# module fails to import, which breaks the whole test suite. Raise MAX_MINOR
# only together with the CI matrix in .github/workflows/ci.yml.
MIN_MINOR=10
MAX_MINOR=13

# Report a candidate interpreter's minor version, or nothing if unusable.
py_minor() {
    "$1" -c 'import sys; print(sys.version_info[1] if sys.version_info[0] == 3 else "")' 2>/dev/null
}

# Prefer whatever python3 points at, but fall back to an explicitly versioned
# interpreter when the default is outside the supported range. This is what
# keeps the script working on a machine whose python3 has moved ahead.
PYTHON=""
CANDIDATES="python3"
for minor in $(seq "$MAX_MINOR" -1 "$MIN_MINOR"); do
    CANDIDATES="$CANDIDATES python3.$minor"
done

for candidate in $CANDIDATES; do
    command -v "$candidate" &> /dev/null || continue
    minor=$(py_minor "$candidate")
    [ -n "$minor" ] || continue
    if [ "$minor" -ge "$MIN_MINOR" ] && [ "$minor" -le "$MAX_MINOR" ]; then
        PYTHON="$candidate"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "❌ No supported Python found. ajitroids needs 3.$MIN_MINOR - 3.$MAX_MINOR."
    if command -v python3 &> /dev/null; then
        echo "   Detected default: $(python3 -V 2>&1)"
    fi
    echo "   Install a supported version, e.g. 3.$MAX_MINOR, and re-run this script."
    exit 1
fi

echo "🐍 Using $($PYTHON -V 2>&1) ($(command -v "$PYTHON"))"

# Create/activate venv if needed. An existing venv built on an unsupported
# interpreter is replaced rather than reused, otherwise the version check above
# would pass while the broken environment stays in place.
if [ -d "$VENV_DIR" ]; then
    EXISTING_MINOR=$(py_minor "$VENV_DIR/bin/python")
    if [ -z "$EXISTING_MINOR" ] || [ "$EXISTING_MINOR" -lt "$MIN_MINOR" ] || [ "$EXISTING_MINOR" -gt "$MAX_MINOR" ]; then
        echo "♻️  Existing .venv uses an unsupported Python - recreating it..."
        rm -rf "$VENV_DIR"
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    "$PYTHON" -m venv "$VENV_DIR"
fi

echo "📦 Activating virtual environment..."
# Try unix-style activate first, then windows-style. Do not swallow errors.
if [ -f "$VENV_DIR/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"
elif [ -f "$VENV_DIR/Scripts/activate" ]; then
    # shellcheck disable=SC1091
    source "$VENV_DIR/Scripts/activate"
fi

# Verify virtualenv activation to avoid accidental global installs
if [ -z "$VIRTUAL_ENV" ]; then
    # Fallback check: compare python's sys.prefix basename to 'venv'
    PREFIX=$(python3 -c 'import sys,os; print(os.path.basename(sys.prefix))' 2>/dev/null || echo unknown)
    EXPECTED_PREFIX="$(basename "$VENV_DIR")"
    if [ "$PREFIX" != "$EXPECTED_PREFIX" ]; then
        echo "❌ Failed to activate virtualenv (VIRTUAL_ENV unset, python prefix: $PREFIX)."
        echo "Please run: source .venv/bin/activate (or .venv/Scripts/activate) and re-run this script."
        exit 1
    fi
fi

# Install through the venv interpreter explicitly. Going via `$VENV_PYTHON -m pip`
# rather than a bare `pip` means a half-applied activation can never silently
# install into the system environment.
if [ -x "$VENV_DIR/bin/python" ]; then
    VENV_PYTHON="$VENV_DIR/bin/python"
else
    VENV_PYTHON="$VENV_DIR/Scripts/python.exe"
fi

echo "📦 Installing dependencies..."
"$VENV_PYTHON" -m pip install --upgrade pip setuptools wheel
"$VENV_PYTHON" -m pip install -r "$PROJECT_ROOT/requirements.txt"
"$VENV_PYTHON" -m pip install -r "$PROJECT_ROOT/requirements-docs.txt"

echo "🪝 Installing pre-commit hooks..."
"$VENV_PYTHON" -m pip install pre-commit
cd "$PROJECT_ROOT"
"$VENV_PYTHON" -m pre_commit install

echo "✅ Development environment setup complete!"
echo "💡 Pre-commit hooks are now active. They will run on git commit."
echo "   To run hooks manually on all files: pre-commit run --all-files"
