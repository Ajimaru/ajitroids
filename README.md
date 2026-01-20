<!-- markdownlint-disable MD013 -->

# 🚀 Ajitroids

[![Python](https://img.shields.io/badge/python-3.09%2B-blue.svg)](https://python.org)
[![Latest Release](https://img.shields.io/github/v/release/Ajimaru/ajitroids?sort=semver)](https://github.com/Ajimaru/ajitroids/releases/latest)
[![Coverage](https://codecov.io/gh/Ajimaru/ajitroids/graph/badge.svg?branch=main)](https://codecov.io/gh/Ajimaru/ajitroids)
![Language Count](https://img.shields.io/github/languages/count/Ajimaru/ajitroids)
[![Issues](https://img.shields.io/github/issues/Ajimaru/ajitroids)](https://github.com/Ajimaru/ajitroids/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Ajimaru/ajitroids/pulls)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Stars](https://img.shields.io/github/stars/Ajimaru/ajitroids)
![Forks](https://img.shields.io/github/forks/Ajimaru/ajitroids)

[A modern Asteroids remake built with Pygame]

![Ajitroids Screenshot](docs/assets/screenshots/Ajitroids_title.png)

## 🎮 Game Description

Ajitroids is an exciting remake of the classic arcade game Asteroids with modern
features and gameplay elements. Pilot your spaceship through dangerous asteroid
fields, dodge space rocks, destroy enemies and collect power-ups while trying to
achieve the highest score.

![Ajitroids Screenshot](docs/assets/screenshots/Ajitroids_gameplay.gif)

## ✨ Features

- **Classic Gameplay**: Control your ship with precise rotation and thrust
- **Modern Graphics**: Enhanced visuals with particle effects and animations
- **Advanced Audio System**:
  - **Dynamic Music**: Music intensity changes based on game state (asteroids,
    enemies, boss fights)
  - **Voice Announcements**: Audio announcements for key events ("Level up!",
    "Boss incoming!", "Game over!")
  - **Sound Themes**: Choose between different audio packs (Default, Retro,
    Sci-Fi, Orchestral)
- **Power-Up System**: Collect various weapon upgrades and shields
- **Advanced Asteroid Types**: Face four distinct asteroid types (Normal, Ice,
  Metal, Crystal) with unique behaviors
- **Highscore System**: Save your best results and compare them
- **Boss Fights**: Face epic boss enemies in higher levels
- **Customizable Settings**: Fullscreen mode, audio options, themes and more
- **Smooth Animations**: Fluid ship movements and asteroid rotations
- **Quick Restart**: Press 'R' to instantly restart without going through menus
- **Stats Dashboard**: View detailed statistics with visual progress bars
- **Replay System**: Watch and analyze your previous games with playback
  controls
- **Performance Profiler**: Real-time FPS monitoring and performance metrics
  (F12)

## 🚀 Installation

### Prerequisites

- Python 3.9 or higher (tested up to 3.12)
- [uv](https://github.com/astral-sh/uv) or pip

### Method 1: Install from Release (Recommended)

Download `ajitroids-latest-py3-none-any.whl` from the
[Releases page](https://github.com/Ajimaru/ajitroids/releases/latest):

```bash
# Install with pip
pip install ajitroids-latest-py3-none-any.whl

# Run the game via the installed console script
ajitroids
# If ~/.local/bin is not on your PATH, run it explicitly:
~/.local/bin/ajitroids
```

### Method 2: Clone from Git (For Development)

```bash
# Clone the repository
git clone https://github.com/Ajimaru/ajitroids.git
cd ajitroids

# Install dependencies with uv (recommended)
uv sync

# Or install with pip
pip install -r requirements.txt

# Start the game with uv
uv run main.py
# or  pip
python main.py
```

<details>
<summary>🔧 Development Setup</summary>

If you plan to contribute or develop for Ajitroids, set up the development
environment with pre-commit hooks:

```bash
# Run the setup script (Linux/macOS)
bash setup-dev.sh

# Or manual setup (all platforms)
pip install pre-commit
pre-commit install

# Run hooks on all files (optional, to check before committing)
pre-commit run --all-files
```

**What this does:**

- Installs pre-commit framework
- Activates git hooks that check code quality on every commit
- Runs **flake8** (style), **pylint** (code analysis), and **prettier**
  (markdown formatting)
- Prevents commits that violate configured style rules

</details>

<details>
<summary>📚 Documentation</summary>

Comprehensive developer documentation is available:

- **[Developer Documentation](https://ajimaru.github.io/ajitroids/)**: Complete
  guide for developers
- **[Getting Started](https://ajimaru.github.io/ajitroids/getting-started/)**:
  Setup and installation
- **[Architecture](https://ajimaru.github.io/ajitroids/architecture/overview/)**:
  Code architecture and design
- **[API Reference](https://ajimaru.github.io/ajitroids/api/python/)**:
  Auto-generated API docs
- **[Contributing Guide](https://ajimaru.github.io/ajitroids/development/contributing/)**:
  How to contribute

### Building Documentation Locally

```bash
# Install documentation dependencies
pip install -r requirements-docs.txt

# Serve documentation locally
mkdocs serve

# Open http://127.0.0.1:8000 in your browser
```

</details>

### Method 3: Install from Source Archive

If you downloaded a source archive (.tar.gz) from releases (prefer
`ajitroids-latest.tar.gz`):

```bash
# Extract and install
pip install ajitroids-latest.tar.gz

# Run the game via the installed console script
ajitroids
```

## 🌟 Gameplay

- **Main Menu:** Choose from different game modes or adjust settings
- **Tutorial:** Learn the basics of the game (recommended for beginners)
- **Asteroids:** Destroy asteroids to collect points
- **Power-Ups:** Collect special power-ups for unique abilities
- **Boss Enemies:** Powerful boss enemies appear after certain levels
- **Highscores:** Save your best performances and compare them with others
- **Achievements:** Unlock achievements for completing special challenges

## 🎯 Controls

### Game Controls

- **Arrow Keys**: Control ship (rotation and thrust)
- **Space**: Shoot
- **ESC**: Pause game
- **B**: Switch weapons (when available)
- **R**: Quick restart (during game or game over screen)

### Function Keys

- **F1 / H**: Toggle help screen (in-game)
- **F8**: Toggle FPS display
- **F9**: Toggle sound effects
- **F10**: Toggle music
- **F11**: Toggle fullscreen
- **F12**: Toggle performance profiler (in-game monitoring)

### Replay Controls (in Replay Viewer)

- **Space**: Pause/Resume playback
- **Left/Right Arrows**: Skip backward/forward 5 seconds
- **1**: 0.5x playback speed
- **2**: 1.0x playback speed (normal)
- **3**: 2.0x playback speed
- **ESC**: Exit replay viewer

<details>
<summary>💻 Command-Line Options</summary>

Ajitroids supports several command-line arguments for enhanced control:

```bash
# Display version
python main.py --version

# Show help and available options
python main.py --help

# Enable debug mode with verbose logging
python main.py --debug

# Skip main menu and start game directly
python main.py --skip-intro

# Force windowed or fullscreen mode
python main.py --windowed
python main.py --fullscreen

# Save logs to a file
python main.py --log-file game.log
```

</details>

## 🚀 Spaceships

Ajitroids features unlockable spaceships with unique abilities:

- **Speedster**: A fast and agile ship, perfect for dodging asteroids.
- **Tank**: A heavily armored ship that can fire on two directions.
- **Destroyer**: A powerful ship equipped with advanced weaponry.

Unlock these ships by progressing through the game and achieving milestones!

## 🛡️ Enemies

- **Enemy Ships**: Hostile ships that chase the player and add challenge to the
  gameplay
- **Interaction**: Enemies can collide with the player and be destroyed by
  weapons
- **Dynamic Movement**: Enemies actively pursue the player within a detection
  radius

## 🛠️ Technical Details

- Developed with Pygame
- Object-oriented design with separate classes for game elements
- Modular sound engine with dynamic effects
- Efficient particle system for visual effects
- Collision detection with optimized algorithms

## 📜 License

This project is licensed under the MIT License with Commons Clause - see the
LICENSE.md file for details.

### 👥 Contributors

- Me - Main Developer
- GitHub Copilot - Development Assistant

### 🙏 Acknowledgements

- Inspiration from the classic Atari game Asteroids
- Thanks to the [Pygame](https://www.pygame.org/ "Pygame Homepage") community
  for the great library
- [Boot.dev](https://www.boot.dev/ "Boot.dev Homepage") for support and
  inspiration
- GitHub Copilot for assistance with code development
- Developed with ❤️ and Pygame

_Note: This project is in active development. New features and improvements are
regularly being added._
