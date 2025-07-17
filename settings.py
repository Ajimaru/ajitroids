import json
import os

class Settings:
    def __init__(self):
        self.music_on = True
        self.sound_on = True
        self.fullscreen = False
        self.difficulty = "normal"
        self.load()
        print(f"Settings nach dem Laden: Musik={self.music_on}, Sound={self.sound_on}, Vollbild={self.fullscreen}")
        
    def save(self):
        settings_data = {
            "music_on": self.music_on,
            "sound_on": self.sound_on,
            "fullscreen": self.fullscreen,
            "difficulty": self.difficulty
        }
        
        try:
            with open("settings.json", "w") as f:
                json.dump(settings_data, f)
                print("Einstellungen gespeichert")
            return True
        except Exception as e:
            print(f"Fehler beim Speichern der Einstellungen: {e}")
            return False
            
    def load(self):
        if not os.path.exists("settings.json"):
            print("Keine Einstellungsdatei gefunden, verwende Standardwerte")
            return False
            
        try:
            with open("settings.json", "r") as f:
                settings_data = json.load(f)
                self.music_on = settings_data.get("music_on", True)
                self.sound_on = settings_data.get("sound_on", True)
                self.fullscreen = settings_data.get("fullscreen", False)
                self.difficulty = settings_data.get("difficulty", "normal")
                print("Einstellungen geladen")
            return True
        except Exception as e:
            print(f"Fehler beim Laden der Einstellungen: {e}")
            return False