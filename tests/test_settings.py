import pytest
import os
import json
from modul.settings import Settings


@pytest.fixture
def clean_settings_file():
    """Remove settings file before and after test"""
    settings_file = "settings.json"
    if os.path.exists(settings_file):
        os.remove(settings_file)
    yield
    if os.path.exists(settings_file):
        os.remove(settings_file)


class TestSettings:
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
