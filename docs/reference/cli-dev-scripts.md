# Development Scripts

This document describes the development scripts and CLI commands available for
Ajitroids.

## Running the Game

### Basic Execution

```bash
# Run with Python
python main.py

# Run with uv (if installed)
uv run main.py

# Run as module
python -m ajitroids
```

### Command-Line Options

```bash
# Show help
python main.py --help

# Enable debug mode
python main.py --debug

# Start in fullscreen
python main.py --fullscreen

# Set custom resolution
python main.py --resolution 1920x1080

# Disable sound
python main.py --no-sound

# Show version
python main.py --version
```

## Testing Commands

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=modul

# Run specific test file
pytest tests/test_player_respawn.py

# Run specific test
pytest tests/test_player_respawn.py::test_player_respawn

# Run with verbose output
pytest -v

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Run in parallel (requires pytest-xdist)
pytest -n auto
```

### Test Options

```bash
# Generate HTML coverage report
pytest --cov=modul --cov-report=html

# Show missing lines
pytest --cov=modul --cov-report=term-missing

# Run only failed tests from last run
pytest --lf

# Run failed tests first
pytest --ff
```

## Code Quality

### Formatting

```bash
# Format all Python files
black modul/ tests/ main.py

# Check formatting without changes
black --check modul/ tests/ main.py

# Format specific file
black modul/player.py

# Show diff without applying
black --diff modul/player.py
```

### Linting

```bash
# Lint all files
flake8 modul/ tests/ main.py

# Lint specific directory
flake8 modul/

# Show statistics
flake8 --statistics modul/

# Generate HTML report
flake8 --format=html --htmldir=flake-report modul/
```

### Type Checking

```bash
# Install mypy
pip install mypy

# Run type checking
mypy modul/

# Strict mode
mypy --strict modul/

# Generate report
mypy --html-report mypy-report modul/
```

## Documentation

### Building Documentation

```bash
# Install dependencies
pip install -r requirements-docs.txt

# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build

# Build with strict mode (fail on warnings)
mkdocs build --strict

# Deploy to GitHub Pages (manual)
mkdocs gh-deploy
```

### Documentation Options

```bash
# Serve on different port
mkdocs serve --dev-addr localhost:8001

# Serve with live reload
mkdocs serve --livereload

# Clean build directory
mkdocs build --clean

# Verbose build output
mkdocs build --verbose
```

## Building and Packaging

### Building Package

```bash
# Install build tools
pip install build

# Build distribution
python -m build

# Build only wheel
python -m build --wheel

# Build only source distribution
python -m build --sdist
```

### Installing Locally

```bash
# Install in development mode
pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"

# Install from local build
pip install dist/ajitroids-*.whl
```

## UML Diagram Generation

### Prerequisites

```bash
# Install dependencies
pip install pylint graphviz

# On Ubuntu/Debian
sudo apt-get install graphviz

# On macOS
brew install graphviz
```

### Generate Diagrams

Create the diagram generation script:

**`scripts/generate-diagrams.sh`**:

```bash
#!/usr/bin/env bash
set -e

echo "Generating UML diagrams..."

# Create output directory
mkdir -p docs/reference/diagrams

# Generate class diagrams
pyreverse -o png -p Ajitroids modul/

# Move to docs
mv classes_Ajitroids.png docs/reference/diagrams/classes.png
mv packages_Ajitroids.png docs/reference/diagrams/packages.png

echo "Diagrams generated in docs/reference/diagrams/"
```

Make executable:

```bash
chmod +x scripts/generate-diagrams.sh
```

Run:

```bash
./scripts/generate-diagrams.sh
```

## Git Workflow Scripts

### Clean Repository

```bash
# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Remove build artifacts
rm -rf build/ dist/ *.egg-info/

# Remove test artifacts
rm -rf .pytest_cache/ htmlcov/ .coverage

# Remove documentation build
rm -rf site/
```

### Check Repository Status

```bash
# Show status
git status

# Show diff
git --no-pager diff

# Show staged changes
git --no-pager diff --staged

# Show log
git log --oneline -10
```

## Utility Scripts

### Reset Settings

**`scripts/reset-settings.sh`**:

```bash
#!/usr/bin/env bash

echo "Resetting Ajitroids settings..."
rm -rf ~/.ajitroids/
echo "Settings reset. They will be recreated on next run."
```

### Backup Save Data

**`scripts/backup-saves.sh`**:

```bash
#!/usr/bin/env bash

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

cp -r ~/.ajitroids/* "$BACKUP_DIR/"
echo "Saved data backed up to $BACKUP_DIR"
```

### Run Full CI Checks

**`scripts/ci-check.sh`**:

```bash
#!/usr/bin/env bash
set -e

echo "Running CI checks..."

echo "1. Formatting check..."
black --check modul/ tests/ main.py

echo "2. Linting..."
flake8 modul/ tests/ main.py

echo "3. Running tests..."
pytest --cov=modul

echo "4. Building package..."
python -m build

echo "All checks passed!"
```

## Development Shortcuts

### Create Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"
```

### Quick Test

```bash
# Run game quickly
python main.py --no-sound --resolution 800x600
```

### Profile Performance

```bash
# Install profiler
pip install py-spy

# Profile the game
py-spy record -o profile.svg -- python main.py

# View profile
open profile.svg
```

## Environment Setup

### Development Environment

```bash
# Install all dependencies
pip install -r requirements.txt
pip install -r requirements-docs.txt
pip install -e ".[dev]"

# Verify installation
python -c "import pygame; print(pygame.version.ver)"
pytest --version
black --version
```

### Pre-commit Hooks

Set up pre-commit hooks to check code before committing:

**`.git/hooks/pre-commit`**:

```bash
#!/bin/bash

echo "Running pre-commit checks..."

# Format check
black --check modul/ tests/ main.py || {
    echo "Code formatting failed. Run: black modul/ tests/ main.py"
    exit 1
}

# Lint check
flake8 modul/ tests/ main.py || {
    echo "Linting failed."
    exit 1
}

# Run tests
pytest || {
    echo "Tests failed."
    exit 1
}

echo "Pre-commit checks passed!"
```

Make executable:

```bash
chmod +x .git/hooks/pre-commit
```

## Continuous Integration

### GitHub Actions

Workflows are defined in `.github/workflows/`:

- **`python-package.yml`**: Run tests on push/PR
- **`docs.yml`**: Build and deploy documentation
- **`release.yml`**: Create releases on tags
- **`static.yml`**: Deploy static GitHub Pages

### Running Locally

Simulate CI environment:

```bash
# Use act to run GitHub Actions locally
brew install act  # macOS
act push          # Run on push event
```

## Debugging Tools

### Python Debugger

```bash
# Run with pdb
python -m pdb main.py

# Common pdb commands:
# n - next line
# s - step into
# c - continue
# b - set breakpoint
# l - list code
# p - print variable
```

### Interactive Console

```bash
# Run Python shell with game modules
python -i -c "import pygame; from modul import *"
```

## Performance Monitoring

### FPS Monitoring

```bash
# Run with FPS display
python main.py --debug --show-fps
```

### Memory Profiling

```bash
# Install memory profiler
pip install memory_profiler

# Profile memory
python -m memory_profiler main.py
```

## Asset Management

### Check Assets

```bash
# List all assets
find assets/ -type f

# Check for missing assets
# (Add custom script as needed)
```

### Optimize Assets

```bash
# Optimize PNG images
optipng assets/**/*.png

# Optimize audio files
# (Use appropriate tools for your audio format)
```

## Next Steps

- [Configuration](configuration.md): Configuration reference
- [Contributing](../development/contributing.md): Contribution workflow
- [Testing](../development/testing.md): Testing guide
