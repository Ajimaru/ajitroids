"""Tests for Settings persistence and defaults."""

import json
import os

import pytest

from modul.settings import Settings


@pytest.fixture
def clean_settings_file(tmp_path, monkeypatch):
    """Run settings persistence tests in an isolated directory.

    Settings reads and writes the relative path "settings.json", so without
    chdir these tests would delete the player's real settings in the project
    root - and the pytest pre-commit hook would wipe them on every commit.
    """
    monkeypatch.chdir(tmp_path)
    settings_file = tmp_path / "settings.json"
    if settings_file.exists():
        settings_file.unlink()
    yield
    if settings_file.exists():
        settings_file.unlink()


class TestSettings:
    """Test suite for the Settings class, covering persistence and default values."""
    def test_settings_initialization_defaults(self, clean_settings_file):
        """Test default settings initialization"""
        settings = Settings()
        assert settings.music_on is True
        assert settings.sound_on is True
        assert settings.fullscreen is False
        assert settings.difficulty == "normal"
        assert settings.music_volume == 0.5
        assert settings.sound_volume == 0.5
        assert settings.dynamic_music_enabled is True
        assert settings.voice_announcements_enabled is True
        assert settings.sound_theme == "default"

    def test_settings_save(self, clean_settings_file):
        """Test saving settings"""
        settings = Settings()
        settings.music_on = False
        settings.sound_on = False
        settings.fullscreen = True
        settings.music_volume = 0.7
        settings.sound_volume = 0.3
        settings.dynamic_music_enabled = False
        settings.voice_announcements_enabled = False
        settings.sound_theme = "retro"

        result = settings.save()
        assert result is True
        assert os.path.exists("settings.json")

        # Verify saved data
        with open("settings.json", "r") as f:
            data = json.load(f)
        assert data["music_on"] is False
        assert data["sound_on"] is False
        assert data["fullscreen"] is True
        assert data["music_volume"] == 0.7
        assert data["sound_volume"] == 0.3
        assert data["dynamic_music_enabled"] is False
        assert data["voice_announcements_enabled"] is False
        assert data["sound_theme"] == "retro"

    def test_settings_load(self, clean_settings_file):
        """Test loading settings"""
        # Create a settings file
        settings_data = {
            "music_on": False,
            "sound_on": False,
            "fullscreen": True,
            "difficulty": "hard",
            "music_volume": 0.8,
            "sound_volume": 0.2,
            "dynamic_music_enabled": False,
            "voice_announcements_enabled": False,
            "sound_theme": "scifi",
        }
        with open("settings.json", "w") as f:
            json.dump(settings_data, f)

        # Load settings
        settings = Settings()
        assert settings.music_on is False
        assert settings.sound_on is False
        assert settings.fullscreen is True
        assert settings.music_volume == 0.8
        assert settings.sound_volume == 0.2
        assert settings.dynamic_music_enabled is False
        assert settings.voice_announcements_enabled is False
        assert settings.sound_theme == "scifi"

    def test_settings_load_no_file(self, clean_settings_file):
        """Test loading settings when no file exists"""
        settings = Settings()
        # Should use defaults
        assert settings.music_on is True
        assert settings.sound_on is True
        assert settings.fullscreen is False

    def test_settings_load_partial_data(self, clean_settings_file):
        """Test loading settings with missing fields"""
        # Create a settings file with partial data
        settings_data = {
            "music_on": False,
        }
        with open("settings.json", "w") as f:
            json.dump(settings_data, f)

        # Load settings
        settings = Settings()
        assert settings.music_on is False
        # Others should retain their constructor defaults
        assert settings.sound_on is True
        assert settings.fullscreen is False
        assert settings.music_volume == 0.5  # Default from __init__
        assert settings.sound_volume == 0.5  # Default from __init__

    def test_settings_save_load_cycle(self, clean_settings_file):
        """Test save and load cycle"""
        settings1 = Settings()
        settings1.music_on = False
        settings1.fullscreen = True
        settings1.music_volume = 0.6
        settings1.save()

        settings2 = Settings()
        assert settings2.music_on is False
        assert settings2.fullscreen is True
        assert settings2.music_volume == 0.6

    def test_settings_save_error_handling(self, clean_settings_file, monkeypatch):
        """Test error handling during save"""
        settings = Settings()

        # Mock open to raise an exception
        def mock_open(*args, **kwargs):
            raise IOError("Mock error")

        monkeypatch.setattr("builtins.open", mock_open)
        result = settings.save()
        assert result is False

    def test_settings_load_error_handling(self, clean_settings_file):
        """Test error handling during load with corrupted file"""
        # Create a corrupted settings file
        with open("settings.json", "w") as f:
            f.write("invalid json content {")

        settings = Settings()
        # Should use defaults when loading fails
        assert settings.music_on is True
        assert settings.sound_on is True


class TestSettingsValidation:
    """Test suite for repairing settings files that hold implausible values."""

    @staticmethod
    def _load_with(data):
        """Write a settings file holding `data` and load it."""
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(data, f)
        settings = Settings()
        assert settings.load() is True
        return settings

    def test_volume_above_range_is_clamped(self, clean_settings_file):
        """A volume beyond 1.0 is clamped, not passed to the mixer"""
        settings = self._load_with({"music_volume": 99.0})
        assert settings.music_volume == 1.0

    def test_volume_below_range_is_clamped(self, clean_settings_file):
        """A negative volume is clamped to 0.0"""
        settings = self._load_with({"sound_volume": -5.0})
        assert settings.sound_volume == 0.0

    def test_non_numeric_volume_falls_back_to_default(self, clean_settings_file):
        """A volume that is not a number cannot be clamped, so it resets"""
        settings = self._load_with({"music_volume": "loud"})
        assert settings.music_volume == 0.5

    def test_non_boolean_flag_falls_back_to_default(self, clean_settings_file):
        """A string in a boolean field resets instead of being truthy"""
        settings = self._load_with({"music_on": "yes"})
        assert settings.music_on is True

    def test_unknown_difficulty_falls_back_to_default(self, clean_settings_file):
        """An unknown difficulty resets to normal"""
        settings = self._load_with({"difficulty": "impossible"})
        assert settings.difficulty == "normal"

    def test_unknown_language_falls_back_to_default(self, clean_settings_file):
        """A language without a locale catalog resets to English"""
        settings = self._load_with({"language": "klingon"})
        assert settings.language == "en"

    def test_unknown_sound_theme_falls_back_to_default(self, clean_settings_file):
        """An unknown sound theme resets to default"""
        settings = self._load_with({"sound_theme": "techno"})
        assert settings.sound_theme == "default"

    def test_invalid_control_key_falls_back_to_default(self, clean_settings_file):
        """A key name pygame does not know would make the action unreachable"""
        settings = self._load_with({"controls": {"shoot": "K_DOES_NOT_EXIST"}})
        assert settings.controls["shoot"] == "K_SPACE"

    def test_valid_control_key_is_kept(self, clean_settings_file):
        """A remapped but valid key survives validation"""
        settings = self._load_with({"controls": {"shoot": "K_RETURN"}})
        assert settings.controls["shoot"] == "K_RETURN"

    def test_non_boolean_announcement_flag_falls_back(self, clean_settings_file):
        """Announcement flags are booleans keyed by event type"""
        settings = self._load_with({"announcement_types": {"level_up": "on"}})
        assert settings.announcement_types["level_up"] is True

    def test_valid_settings_are_left_alone(self, clean_settings_file):
        """Validation must not touch a file that is already sound"""
        settings = self._load_with({
            "music_on": False,
            "music_volume": 0.3,
            "difficulty": "hard",
            "language": "de",
        })
        assert settings.music_on is False
        assert settings.music_volume == 0.3
        assert settings.difficulty == "hard"
        assert settings.language == "de"

    def test_repaired_file_is_written_back(self, clean_settings_file):
        """The cleaned values are persisted, so warnings appear only once"""
        self._load_with({"music_volume": 99.0, "sound_theme": "techno"})

        with open("settings.json", "r", encoding="utf-8") as f:
            stored = json.load(f)
        assert stored["music_volume"] == 1.0
        assert stored["sound_theme"] == "default"
