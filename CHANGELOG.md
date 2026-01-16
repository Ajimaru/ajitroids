# Changelog

## Unreleased

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