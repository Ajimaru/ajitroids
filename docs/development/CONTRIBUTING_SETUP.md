<!-- markdownlint-disable MD013 -->

# Contributing to Ajitroids

Thank you for your interest in contributing to Ajitroids! This guide will help
you get started with development.

## Setting Up Your Development Environment

### Automatic Setup (Recommended)

Run the provided setup script to install all dependencies and activate
pre-commit hooks:

```bash
bash setup-dev.sh
```

This script will:

1. Create a Python virtual environment (if needed)
2. Install all project dependencies
3. Install the pre-commit framework
4. Activate git pre-commit hooks

### Manual Setup

If you prefer manual setup:

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-docs.txt
pip install pre-commit

# Activate git hooks
pre-commit install
```

## Code Quality & Pre-Commit Hooks

This project uses pre-commit hooks to maintain code quality. Hooks automatically
run on every commit and will:

- **flake8**: Check code style (PEP 8)
- **pylint**: Analyze code for errors and maintainability
- **prettier**: Format Markdown files
- **Pre-commit hooks**: Check for trailing whitespace, valid YAML, etc.

### Running Pre-Commit Manually

To run all checks on the current staged files:

```bash
pre-commit run
```

To run all checks on all files:

```bash
pre-commit run --all-files
```

## Commit Guidelines

1. Write descriptive commit messages
2. Keep commits focused and atomic
3. Reference related issues using `#issue-number`
4. Ensure all pre-commit checks pass before pushing

## Development Workflow

1. Create a new branch for your feature: `git checkout -b feature/my-feature`
2. Make your changes
3. Commit with descriptive messages
4. Push to your fork
5. Create a Pull Request with a clear description

## Testing

Run tests before submitting a PR:

```bash
pytest tests/
```

## Building Documentation

To build and view documentation locally:

```bash
pip install -r requirements-docs.txt
mkdocs serve
```

Then open `http://127.0.0.1:8000` in your browser.

## Code Style

- Follow PEP 8 guidelines
- Maximum line length: 79 characters
- Use meaningful variable and function names
- Add docstrings to functions and classes

## Questions?

Open an issue or start a discussion on the GitHub repository.

---

Thank you for contributing! 🎮
