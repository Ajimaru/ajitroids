import json
import os

class Settings:
    def __init__(self):
        self.music_on = True
        self.sound_on = True
        self.fullscreen = False
        self.difficulty = "normal"
        self.load()
        print(f"Settings after loading: Music={self.music_on}, Sound={self.sound_on}, Fullscreen={self.fullscreen}")
        
    def save(self):
        settings_data = {
            "music_on": self.music_on,
            "sound_on": self.sound_on,
            "fullscreen": self.fullscreen
        }

        try:
            with open("settings.json", "w") as f:
                json.dump(settings_data, f)
                print("Settings saved")
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
            
    def load(self):
        if not os.path.exists("settings.json"):
            print("No settings file found, using default values")
            return False
            
        try:
            with open("settings.json", "r") as f:
                settings_data = json.load(f)
                self.music_on = settings_data.get("music_on", True)
                self.sound_on = settings_data.get("sound_on", True)
                self.fullscreen = settings_data.get("fullscreen", False)
                self.difficulty = settings_data.get("difficulty", "normal")
                print("Settings loaded")
            return True
        except Exception as e:
            print(f"Error loading settings: {e}")
            return False