# Contributing to Ajitroids

Thank you for your interest in contributing to Ajitroids! This guide will help
you get started with contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)

## Code of Conduct

Please read and follow our
[Code of Conduct](https://github.com/Ajimaru/ajitroids/blob/main/CODE_OF_CONDUCT.md).

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Basic understanding of Pygame
- Familiarity with object-oriented programming

### Setting Up Development Environment

1. **Fork and clone the repository**

```bash
git clone https://github.com/YOUR-USERNAME/ajitroids.git
cd ajitroids
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
# Game dependencies
pip install -r requirements.txt

# Development dependencies
pip install -e ".[dev]"

# Documentation dependencies (optional)
pip install -r requirements-docs.txt
```

4. **Create a new branch**

```bash
git checkout -b feature/your-feature-name
```

## Development Workflow

### 1. Make Your Changes

- Write clean, readable code
- Follow the existing code structure
- Add comments for complex logic
- Update documentation if needed

### 2. Test Your Changes

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_player_respawn.py

# Run with verbose output
pytest -v
```

### 3. Format Your Code

```bash
# Format with black
black modul/ tests/ main.py

# Check with flake8
flake8 modul/ tests/ main.py
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "feat: add new power-up type"
```

**Commit message format:**

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length**: 127 characters (configured in `pyproject.toml`)
- **Indentation**: 4 spaces
- **Quotes**: Use double quotes for strings
- **Naming conventions**:
  - Classes: `PascalCase`
  - Functions/methods: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
  - Private methods: `_leading_underscore`

### Code Organization

```python
# Standard library imports
import random
from typing import List, Tuple

# Third-party imports
import pygame
from pygame import Vector2

# Local imports
from modul.circleshape import CircleShape
from modul.constants import SCREEN_WIDTH, SCREEN_HEIGHT
```

### Documentation

Use docstrings for classes and functions:

```python
def calculate_trajectory(start: Vector2, end: Vector2, speed: float) -> Vector2:
    """Calculate trajectory from start to end position.

    Args:
        start: Starting position vector
        end: Target position vector
        speed: Movement speed

    Returns:
        Velocity vector for movement
    """
    direction = (end - start).normalize()
    return direction * speed
```

### Type Hints

Use type hints where appropriate:

```python
def spawn_asteroid(position: Vector2, velocity: Vector2, size: int) -> Asteroid:
    """Spawn a new asteroid at the given position."""
    return Asteroid(position, velocity, size)
```

## Testing Guidelines

### Writing Tests

Tests are located in the `tests/` directory.

**Example test:**

```python
import pytest
from modul.player import Player
from pygame import Vector2

def test_player_respawn():
    """Test that player respawns correctly after death."""
    player = Player(100, 100)
    player.lives = 2

    # Simulate death
    player.take_damage()

    assert player.lives == 1
    assert player.invulnerable == True
```

### Test Coverage

- Write tests for new features
- Update tests when modifying existing features
- Aim for good coverage of critical paths
- Test edge cases and error conditions

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_player_respawn.py

# With coverage report
pytest --cov=modul

# Stop on first failure
pytest -x
```

## Pull Request Process

### Before Submitting

- [ ] Code follows the style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages are clear and descriptive

### PR Description Template

```markdown
## Description

Brief description of changes

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

How has this been tested?

## Screenshots (if applicable)

Add screenshots for UI changes

## Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes (or properly documented)
```

### Review Process

1. **Automated checks** will run on your PR
2. **Code review** by maintainers
3. **Requested changes** (if any)
4. **Approval** and merge

## Issue Guidelines

### Reporting Bugs

Use the bug report template and include:

- **Description**: Clear description of the bug
- **Steps to reproduce**: Numbered steps
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Screenshots**: If applicable
- **Environment**:
  - OS (e.g., Windows 11, Ubuntu 22.04)
  - Python version
  - Pygame version

### Requesting Features

Use the feature request template and include:

- **Description**: Clear feature description
- **Use case**: Why is this useful?
- **Proposed solution**: How could it work?
- **Alternatives**: Other solutions considered

### Good First Issues

Look for issues labeled `good first issue` if you're new to the project.

## Development Tips

### Debugging

```python
# Enable FPS display
settings.video.fps_display = True

# Draw debug collision circles
def draw_debug(screen, entity):
    pygame.draw.circle(screen, (255, 0, 0), entity.position, entity.radius, 1)
```

### Testing Locally

```bash
# Run the game
python main.py

# Run in different modes
python main.py --debug
python main.py --fullscreen
```

### Documentation

Build and preview documentation:

```bash
# Install docs dependencies
pip install -r requirements-docs.txt

# Serve docs locally
mkdocs serve

# Build docs
mkdocs build
```

## Getting Help

- **Documentation**: Read the [developer docs](../index.md)
- **Discussions**: Use
  [GitHub Discussions](https://github.com/Ajimaru/ajitroids/discussions)
- **Issues**: Search existing issues or create a new one
- **Discord**: Join our community (if available)

## Recognition

Contributors will be recognized in:

- Release notes
- Contributors list
- Special achievements in-game (for significant contributions)

Thank you for contributing to Ajitroids! 🚀
