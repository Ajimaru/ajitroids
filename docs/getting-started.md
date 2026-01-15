# Getting Started

This guide will help you set up your development environment and start working on Ajitroids.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9 or higher**: [Download Python](https://www.python.org/downloads/)
- **Git**: [Download Git](https://git-scm.com/downloads)
- **uv** (recommended) or pip for package management

## Installation

### Option 1: Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver.

```bash
# Clone the repository
git clone https://github.com/Ajimaru/ajitroids.git
cd ajitroids

# Install dependencies
uv install

# Run the game
uv run main.py
```

### Option 2: Using pip

```bash
# Clone the repository
git clone https://github.com/Ajimaru/ajitroids.git
cd ajitroids

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

## Development Setup

### Installing Development Dependencies

For development, you'll need additional tools for testing and code quality:

```bash
# Install development dependencies
pip install -e ".[dev]"
```

This installs:

- `pytest`: For running tests
- `black`: For code formatting
- `flake8`: For code linting

### Installing Documentation Dependencies

To build and preview documentation locally:

```bash
pip install -r requirements-docs.txt
```

## Running the Game

Once installed, you can run the game with:

```bash
python main.py
```

Or with uv:

```bash
uv run main.py
```

## Project Structure

```
ajitroids/
├── main.py              # Entry point
├── modul/               # Game modules
│   ├── player.py        # Player ship logic
│   ├── asteroid.py      # Asteroid logic
│   ├── boss.py          # Boss enemy logic
│   ├── powerup.py       # Power-up system
│   ├── menu.py          # Menu system
│   ├── sounds.py        # Sound management
│   ├── achievements.py  # Achievement system
│   └── ...
├── assets/              # Game assets (images, sounds)
├── tests/               # Test files
├── docs/                # Documentation
└── requirements.txt     # Python dependencies
```

## Running Tests

Run the test suite with pytest:

```bash
pytest
```

For verbose output:

```bash
pytest -v
```

To run specific tests:

```bash
pytest tests/test_player_respawn.py
```

## Code Quality

### Formatting Code

Format your code with black:

```bash
black modul/ tests/ main.py
```

### Linting Code

Check code quality with flake8:

```bash
flake8 modul/ tests/ main.py
```

## Building Documentation

To build and serve the documentation locally:

```bash
mkdocs serve
```

Then open your browser to `http://127.0.0.1:8000/`

## Next Steps

- Read the [Architecture Overview](architecture/overview.md) to understand the codebase
- Check out the [Contributing Guide](development/contributing.md) to start making changes
- Explore the [Python API](api/python.md) for detailed code documentation

## Common Issues

### Pygame Installation Issues

If you encounter issues installing Pygame, especially on Linux, you may need to install SDL dependencies:

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-dev libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
```

**macOS:**
```bash
brew install sdl2 sdl2_image sdl2_mixer sdl2_ttf
```

### Sound Issues

If you don't hear any sound:

1. Check your system volume
2. Ensure audio output device is properly configured
3. Try adjusting sound settings in the game menu

## Getting Help

If you run into problems:

1. Check the [Issue Tracker](https://github.com/Ajimaru/ajitroids/issues)
2. Read through existing issues to see if someone else has encountered the same problem
3. Create a new issue with detailed information about your problem
