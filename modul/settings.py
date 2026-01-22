"""Manage user settings persistence and defaults."""

import json
import os

# Module lint rules: allow the existing `current_settings` name and a small
# number of broad-except usages and the global statement used for the
# runtime singleton registration.
# pylint: disable=invalid-name,global-statement,broad-exception-caught

# Runtime singleton assigned when Settings() is constructed
current_settings = None


class Settings:
    def __init__(self):
        self.music_on = True
        self.sound_on = True
        self.fullscreen = False
        self.difficulty = "normal"
        self.music_volume = 0.5
        self.sound_volume = 0.5
        self.dynamic_music_enabled = True
        self.voice_announcements_enabled = True
        self.sound_theme = "default"
        # Per-announcement type enable flags
        self.announcement_types = {
            "level_up": True,
            "boss_incoming": True,
            "boss_defeated": True,
            "game_over": True,
            "new_weapon": False,
            "shield_active": False,
            "low_health": False,
            "powerup": False,
            "extra_life": True,
            "achievement": True,
            "high_score": True,
        }
        # Controls mapping: store readable pygame key names
        # Examples: "K_LEFT", "K_SPACE"
        # Displayed actions: rotate_left, rotate_right, thrust, reverse,
        # shoot, switch_weapon, pause
        self.controls = {
            "rotate_left": "K_LEFT",
            "rotate_right": "K_RIGHT",
            "thrust": "K_UP",
            "reverse": "K_DOWN",
            "shoot": "K_SPACE",
            "switch_weapon": "K_b",
            "pause": "K_ESCAPE",
        }

        # Language selection: 'en' default, add 'de' for German
        self.language = "en"
        # TTS preferences: selected voice id/name and voice language.
        # Defaults to the current UI language.
        # Empty `tts_voice` uses the engine default.
        self.tts_voice = ""
        self.tts_voice_language = self.language
        # Whether to show the TTS voice selection directly in the Options menu
        self.show_tts_in_options = False
        self.load()
        # Register this instance as the active settings for runtime consumers
        global current_settings
        current_settings = self
        print("Settings after loading:")
        print(f"  Music={self.music_on}")
        print(f"  Sound={self.sound_on}")
        print(f"  Fullscreen={self.fullscreen}")
        print(f"  Music Volume={self.music_volume}")
        print(f"  Sound Volume={self.sound_volume}")
        print(f"  Dynamic Music={self.dynamic_music_enabled}")
        print(f"  Voice Announcements={self.voice_announcements_enabled}")
        print(f"  Theme={self.sound_theme}")

    def save(self):
        settings_data = {
            "music_on": self.music_on,
            "sound_on": self.sound_on,
            "fullscreen": self.fullscreen,
            "music_volume": self.music_volume,
            "sound_volume": self.sound_volume,
            "dynamic_music_enabled": self.dynamic_music_enabled,
            "voice_announcements_enabled": self.voice_announcements_enabled,
            "sound_theme": self.sound_theme,
            "announcement_types": self.announcement_types,
            "controls": self.controls,
            "language": self.language,
            "tts_voice": self.tts_voice,
            "tts_voice_language": self.tts_voice_language,
            "show_tts_in_options": self.show_tts_in_options,
        }

        try:
            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump(settings_data, f)
                print("Settings saved")
            return True
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error saving settings: {e}")
            return False

    def load(self):
        if not os.path.exists("settings.json"):
            print("No settings file found, using default values")
            return False

        try:
            with open("settings.json", "r", encoding="utf-8") as f:
                settings_data = json.load(f)
                self.music_on = settings_data.get("music_on", True)
                self.sound_on = settings_data.get("sound_on", True)
                self.fullscreen = settings_data.get("fullscreen", False)
                self.difficulty = settings_data.get("difficulty", "normal")
                # Preserve constructor defaults when values are missing
                _mv = settings_data.get("music_volume", self.music_volume)
                self.music_volume = _mv
                _sv = settings_data.get("sound_volume", self.sound_volume)
                self.sound_volume = _sv
                _dm = settings_data.get("dynamic_music_enabled", True)
                self.dynamic_music_enabled = _dm
                _va = settings_data.get("voice_announcements_enabled", True)
                self.voice_announcements_enabled = _va
                _theme = settings_data.get("sound_theme", "default")
                self.sound_theme = _theme
                # Load announcement types with defaults from __init__
                loaded_types = settings_data.get("announcement_types", {})
                for key in self.announcement_types:
                    if key in loaded_types:
                        self.announcement_types[key] = loaded_types[key]
                # Load controls mapping with defaults
                loaded_controls = settings_data.get("controls", {})
                for key in self.controls:
                    if key in loaded_controls:
                        self.controls[key] = loaded_controls[key]
                # Load language selection
                self.language = settings_data.get("language", self.language)
                # Load TTS preferences
                _tv = settings_data.get("tts_voice", self.tts_voice)
                self.tts_voice = _tv
                _tvl = settings_data.get(
                    "tts_voice_language",
                    self.tts_voice_language,
                )
                self.tts_voice_language = _tvl
                # Load UI preference for showing TTS in Options
                _show = settings_data.get(
                    "show_tts_in_options",
                    self.show_tts_in_options,
                )
                self.show_tts_in_options = _show
                print("Settings loaded")
            return True
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error loading settings: {e}")
            return False
