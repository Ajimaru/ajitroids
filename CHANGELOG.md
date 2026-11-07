# Changelog

<!-- markdownlint-disable MD024 -->

## Unreleased

### Added

- Game modes: `classic` (unchanged), `survival` (endless waves with growing
  quotas and faster spawns) and `time_attack` (kill quota per round against a
  clock, cleared rounds add time). Selectable in a new mode menu or directly
  with `--mode`. Progression lives in `modul/game_modes.py` and is unit-tested.
- HUD readout for the active mode (wave counter, round clock with kill quota).
- Survival and time attack hide the level row, because their pacing comes from
  waves and rounds rather than the score curve.
- Combo chain: consecutive kills inside `COMBO_WINDOW` raise the score
  multiplier (`ComboTracker` in `modul/combo.py`). Asteroid, enemy-ship and boss
  kills all feed the chain; taking a hit or quick-restarting resets it, the
  session best survives and appears in the end-of-session statistics.
- HUD readout `Combo xN (kills)` with a bar for the remaining window time.
- `speed_boost` power-up (temporary thrust multiplier). The counter and the
  "Speed Demon" achievement existed before, but the power-up itself was never
  spawnable.
- Achievements "Combo Master" (3x multiplier) and "Chain Reaction" (25 kills in
  one chain).
- `P` saves a screenshot to `screenshots/`.

### Changed

- `H` / `F1` opens the help screen; previously the triggering key press closed
  it again in the same frame, so the screen was never visible.
- Help screen tips moved into their own column instead of overflowing below the
  footer, and the missing `en`/`de` translations were added.
- `ESC` resumes from the pause menu.
- `F11` toggles fullscreen at runtime; it used to modify a module-level surface
  the game loop never drew to.
- `Level Master`, `High Scorer`, `Asteroid Hunter` and the level-50 ship unlocks
  only trigger in classic, so survival and time attack cannot farm them
  incidentally.
- Survival waves and time attack quotas scale with the selected difficulty, so
  "hard" is harder in every mode instead of only in classic.
- `docs/architecture/game-mechanics.md`: power-up table, combo section and point
  values now match the implementation.

### Build & CI

- Versioning reduced to one source: the git tag. `VERSION`,
  `modul/update_version.py` and the generated `modul/_version.py` are gone, and
  `pyproject.toml` no longer carries a `fallback_version`. `modul/version.py`
  reads the installed package metadata and reports `0.0.0+unknown` when the
  project is not installed.
- CI checks out the full tag history, because `setuptools-scm` needs it for the
  editable install and the lockfile check.
- pytest minimum raised to 9.0.3 in `requirements.txt`, the `dev` extra and
  `minversion` (CVE-2025-71176 in the insecure temp-directory handling).
- `pre-commit` moved into the `dev` extra, so `uv sync --extra dev` restores the
  git hook environment instead of leaving it broken after a venv rebuild. The CI
  job no longer installs it separately.
- Manual release defaults to `main` and accepts prerelease tags like
  `v0.25.0rc1`; `docs/development/release-process.md` and the bug report
  template describe the real flow and use `python main.py --version`.

## v0.25.0

### Added

- Remappable keyboard/gamepad controls, German localization and TTS voice
  selection.
- Four boss types with distinct attacks and stats, scaling health, and a cap on
  boss projectiles.

### Fixed

- Gameplay, replay, audio and statistics issues, including run resets,
  collision/reward handling, replay completion and dashboard layout.
- Tutorial translations, menu navigation and release/install workflows.

### Build & CI

- Python support now starts at 3.10 and includes 3.13; CI, security scanning,
  locale checks and release workflows were consolidated and hardened.

## v0.24.0 (2026-01-17)

### Added

- Text-to-speech voice announcements (pyttsx3-based) with generated WAV
  fallbacks for environments without TTS.
- `VoiceAnnouncementsMenu` in `Options` to toggle individual announcement types.

### Changed

- Per-announcement-type enable flags added to settings and `VoiceAnnouncement`
  (defaults: `new_weapon`, `shield_active`, `low_health`, `powerup` = OFF).
- Announcement display moved from upper third to lower third of the screen for
  improved readability.
- `update_version.py` script and `VERSION` file added to centralize version
  maintenance; `modul/_version.py` now generated from `VERSION`.

### Removed / Chore

- Removed `VERSION_MANAGEMENT.md` (documentation consolidated into workflow).
- Moved `update_version.py` into `modul/` and updated `.gitignore` to ignore
  generated `modul/_version.py`.

### Notes

- Many gameplay polishing changes and audio fixes landed in prior v0.23.0; this
  release focuses on voice announcement UX, settings, and release tooling.

## v0.23.0 (2026-01-16)

### Fixed

- Asteroid split crash resolved (`angle` now always defined) and split angles
  spread consistently across shard counts.
- Sound effect volume now respects the linear slider value; toggle on/off
  reapplies the expected volume instead of curved amplification.

### Changed

- Asteroid scoring is type-aware via multipliers (ice 0.9x, metal 1.5x, crystal
  0.6x) on top of size-based base points; metal asteroids use a warmer brass
  color for better contrast against ice blue.
- Pre-commit now runs the full Pytest suite; pytest hook uses `python3` for
  reliability.

### Build

- Version bumped to 0.23.0 with setuptools-scm fallback aligned.

Full Changelog:
[v0.22.0...v0.23.0](https://github.com/Ajimaru/ajitroids/compare/v0.22.0...v0.23.0)

## v0.22.0 (2026-01-16)

### Added

- Pause menu shows the full keyboard shortcut list.
- Restart from pause now has a confirmation dialog to prevent accidental loss of
  a running session.

### Changed

- Performance profiler overlay moved to the bottom-right corner for better menu
  visibility.
- Leaving a running game for the main menu now requires confirmation; the
  difficulty menu ESC action returns to the main menu instead of silently
  exiting the flow.
- Centralized version lookup via importlib.metadata with setuptools-scm
  fallback, so the in-game version matches the package version without manual
  sync.
- Lint configuration aligned to the project’s 127-character line length.

### Build

- Set setuptools-scm fallback version to 0.22.0; release workflow will pick up
  the tagged version for artifacts and release notes injection.

Full Changelog:
[v0.21.2...v0.22.0](https://github.com/Ajimaru/ajitroids/compare/v0.21.2...v0.22.0)

## v0.21.2 (2026-01-16)

### Fixed

- Replay viewer now renders player, asteroids, enemies, shots, and powerups
  using the recorded frame data.

### Changed

- Replays are saved as compressed `.json.gz` with quantized values and more
  robust loading/browsing.

### Build

- Release workflow exports `SETUPTOOLS_SCM_PRETEND_VERSION` from the tag and
  injects the changelog section into the release body so artifacts match the
  tagged version.

### Documentation

- Installation examples use the `ajitroids` console script, and packaged assets
  are shipped with the module.

Full Changelog:
[v0.21.1...v0.21.2](https://github.com/Ajimaru/ajitroids/compare/v0.21.1...v0.21.2)

## v0.21.1 (2026-01-16)

### Fixed

- **Installation Issues**: Fixed setuptools-scm version detection when
  installing from release archives
  - Added fallback version to pyproject.toml to support builds without Git
    metadata
  - Release packages now include pre-built wheel and source distribution with
    baked-in version

### Changed

- **Installation Methods**: Reorganized and improved installation documentation
  - Method 1: Install from wheel (recommended, no Git required)
  - Method 2: Clone from Git (for development)
  - Method 3: Install from source tarball
  - Added clear instructions for all platforms (Linux, macOS, Windows)
- **Entry Point**: Added `ajitroids` command-line script for easier game launch
  after pip install
- **Build System**: Release workflow now automatically builds and uploads Python
  packages (wheel + sdist)

### Documentation

- Clarified installation instructions to be more welcoming for different
  installation methods
- Fixed typo in repository URL (Ajimarue → Ajimaru)
- Added Windows PowerShell commands for environment variables

Full Changelog:
[v0.21.0...v0.21.1](https://github.com/Ajimaru/ajitroids/compare/v0.21.0...v0.21.1)

## v0.21.0 (2026-01-16)

### Added

- **Quick Restart Feature**: Press 'R' during gameplay or on game over screen to
  instantly restart without menus
- **Stats Dashboard**: New menu option showing detailed game statistics with
  visual progress bars
  - Game statistics: games played, highest/average scores, level tracking,
    playtime
  - Combat statistics: asteroids/enemies/bosses destroyed, powerups collected,
    lives lost
  - Visual metrics: accuracy bar, performance indicator
- **Replay System**: Complete replay recording and playback functionality
  - Automatic recording of all game sessions
  - Replay browser UI with sorting, filtering, and deletion
  - Playback controls: play/pause, variable speed (0.5x/1x/2x), skip
    forward/backward
  - Full game state serialization saved to JSON files
- **Updated Help Screen**: Added Quick Restart shortcut to in-game help
- **Enhanced Menu**: Added "Replays" and "Statistics" options to main menu

### Changed

- Session statistics now automatically track replay-worthy data
- Game over screen now displays quick restart instruction

### Tests

- Added 44 new comprehensive tests for all new features
- Maintained >89% code coverage across the codebase

Full Changelog:
[v0.20.0...v0.21.0](https://github.com/Ajimaru/ajitroids/compare/v0.20.0...v0.21.0)

## v0.20.0 (2026-01-15)

### style

- style(formatting): improved code consistency with Black and autopep8

Full Changelog:
[v0.19.10...v0.20.0](https://github.com/Ajimaru/ajitroids/compare/v0.19.10...v0.20.0)

## v0.19.8 (2025-08-05)

### chore

- chore(release): release description optimized

## v0.19.9 (2025-08-05)

### build

- build(docs): release diff link added

Full Changelog:
[v0.19.8...v0.19.9](https://github.com/Ajimaru/ajitroids/compare/v0.19.8...v0.19.9)

## v0.19.10 (2025-08-12)

### chore

- chore(test): game tests improved

Full Changelog:
[v0.19.9...v0.19.10](https://github.com/Ajimaru/ajitroids/compare/v0.19.9...v0.19.10)
