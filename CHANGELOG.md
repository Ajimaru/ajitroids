# Changelog

## Unreleased

## v0.21.2 (2026-01-16)

### Fixed

- **Replay Viewer**: Recorded gameplay now renders the player, asteroids, enemies, shots, and powerups using captured positions

### Build

- **Release Artifacts**: Release workflow now exports `SETUPTOOLS_SCM_PRETEND_VERSION` from the tag to produce wheels/sdists with the exact tagged version (no dev suffix)

### Documentation

- **Installation**: Updated installation examples to use the `ajitroids` console script and current release asset names

Full Changelog: [v0.21.1...v0.21.2](https://github.com/Ajimaru/ajitroids/compare/v0.21.1...v0.21.2)

## v0.21.1 (2026-01-16)

### Fixed

- **Installation Issues**: Fixed setuptools-scm version detection when installing from release archives
  - Added fallback version to pyproject.toml to support builds without Git metadata
  - Release packages now include pre-built wheel and source distribution with baked-in version

### Changed

- **Installation Methods**: Reorganized and improved installation documentation
  - Method 1: Install from wheel (recommended, no Git required)
  - Method 2: Clone from Git (for development)
  - Method 3: Install from source tarball
  - Added clear instructions for all platforms (Linux, macOS, Windows)
- **Entry Point**: Added `ajitroids` command-line script for easier game launch after pip install
- **Build System**: Release workflow now automatically builds and uploads Python packages (wheel + sdist)

### Documentation

- Clarified installation instructions to be more welcoming for different installation methods
- Fixed typo in repository URL (Ajimarue → Ajimaru)
- Added Windows PowerShell commands for environment variables

Full Changelog: [v0.21.0...v0.21.1](https://github.com/Ajimaru/ajitroids/compare/v0.21.0...v0.21.1)

## v0.21.0 (2026-01-16)

### Added

- **Quick Restart Feature**: Press 'R' during gameplay or on game over screen to instantly restart without menus
- **Stats Dashboard**: New menu option showing detailed game statistics with visual progress bars
  - Game statistics: games played, highest/average scores, level tracking, playtime
  - Combat statistics: asteroids/enemies/bosses destroyed, powerups collected, lives lost
  - Visual metrics: accuracy bar, performance indicator
- **Replay System**: Complete replay recording and playback functionality
  - Automatic recording of all game sessions
  - Replay browser UI with sorting, filtering, and deletion
  - Playback controls: play/pause, variable speed (0.5x/1x/2x), skip forward/backward
  - Full game state serialization saved to JSON files
- **Updated Help Screen**: Added Quick Restart shortcut to in-game help
- **Enhanced Menu**: Added "Replays" and "Statistics" options to main menu

### Changed

- Session statistics now automatically track replay-worthy data
- Game over screen now displays quick restart instruction

### Tests

- Added 44 new comprehensive tests for all new features
- Maintained >89% code coverage across the codebase

Full Changelog: [v0.20.0...v0.21.0](https://github.com/Ajimaru/ajitroids/compare/v0.20.0...v0.21.0)

## v0.20.0 (2026-01-15)

### style

- style(formatting): improved code consistency with Black and autopep8

Full Changelog: [v0.19.10...v0.20.0](https://github.com/Ajimaru/ajitroids/compare/v0.19.10...v0.20.0)

## v0.19.8 (2025-08-05)

### chore

- chore(release): release description optimized

## v0.19.9 (2025-08-05)

### build

- build(docs): release diff link added

Full Changelog: [v0.19.8...v0.19.9](https://github.com/Ajimaru/ajitroids/compare/v0.19.8...v0.19.9)

## v0.19.10 (2025-08-12)

### chore

- chore(test): game tests improved

Full Changelog: [v0.19.9...v0.19.10](https://github.com/Ajimaru/ajitroids/compare/v0.19.9...v0.19.10)