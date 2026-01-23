"""Game assets package for Ajitroids.

This package contains audio assets used throughout the Ajitroids game, including
sound effects and background music. Assets are organized as audio files (.wav for
sound effects, .mp3 for music) that provide auditory feedback for game events,
UI interactions, and atmospheric enhancement.

Asset types:
- Sound effects (.wav): Player actions, enemy interactions, UI feedback, and
  voice announcements for achievements and game states.
- Background music (.mp3): Ambient tracks for menus, gameplay, boss fights, and
  game over sequences.

Public API:
This package does not expose a public API directly. Assets are loaded by other
modules (e.g., sounds.py) using file paths or resource loading mechanisms.

Usage notes:
- Assets should be loaded efficiently to avoid performance issues.
- File paths are relative to this package directory.
- Ensure audio formats are supported by the target platform's audio system.
"""
