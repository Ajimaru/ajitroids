import json

class Achievement:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.unlocked = False

    def unlock(self):
        self.unlocked = True

class AchievementSystem:
    def __init__(self, achievements_file='achievements.json'):
        self.achievements_file = achievements_file
        self.achievements = []
        self.notification_callback = None
        self.initialize_standard_achievements()
        self.load_unlocked_achievements()
    def set_notification_callback(self, callback):
        self.notification_callback = callback

    def initialize_standard_achievements(self):
        standard_achievements = [
            ("First Blood", "Destroy your first asteroid."),
            ("Survivor", "Survive for 10 minutes."),
            ("Asteroid Hunter", "Destroy 1000 asteroids."),
            ("Power User", "Collect 250 power-ups."),
            ("Boss Slayer", "Defeat your first boss."),
            ("Level Master", "Reach level 666."),
            ("High Scorer", "Score 250,000 points."),
            ("Shield Expert", "Use shield 50 times."),
            ("Speed Demon", "Use speed boost 25 times."),
            ("Triple Threat", "Use triple shot 20 times.")
        ]
        for name, description in standard_achievements:
            achievement = Achievement(name, description)
            self.achievements.append(achievement)
        print(f"Standard-Achievements im Speicher initialisiert: {len(self.achievements)} Einträge")

    def load_unlocked_achievements(self):
        try:
            with open(self.achievements_file, 'r') as file:
                data = json.load(file)
                for item in data:
                    if item.get('unlocked', False):
                        for achievement in self.achievements:
                            if achievement.name == item['name']:
                                achievement.unlocked = True
                                break
                print(f"Freigeschaltete Achievements geladen: {len([a for a in self.achievements if a.unlocked])} von {len(self.achievements)}")
        except FileNotFoundError:
            print("Achievements-Datei nicht gefunden - alle Achievements sind gesperrt")
        except json.JSONDecodeError as e:
            print(f"Fehler beim Laden der Achievements-Datei: {e}")

    def save_unlocked_achievements(self):
        unlocked_achievements = [
            {
                'name': achievement.name,
                'description': achievement.description,
                'unlocked': True
            } for achievement in self.achievements if achievement.unlocked
        ]
        if unlocked_achievements:
            with open(self.achievements_file, 'w') as file:
                json.dump(unlocked_achievements, file, indent=4)
            print(f"Freigeschaltete Achievements gespeichert: {len(unlocked_achievements)} Einträge")
        else:
            print("Keine freigeschalteten Achievements zum Speichern")

    def load_achievements(self):
        pass

    def save_achievements(self):
        self.save_unlocked_achievements()

    def unlock_achievement(self, name):
        for achievement in self.achievements:
            if achievement.name == name and not achievement.unlocked:
                achievement.unlock()
                self.save_unlocked_achievements()
                print(f"Achievement unlocked: {achievement.name} - {achievement.description}")
                if self.notification_callback:
                    self.notification_callback(achievement.name, achievement.description)
                break

    def unlock(self, name):
        for achievement in self.achievements:
            if achievement.name == name and not achievement.unlocked:
                achievement.unlock()
                self.save_unlocked_achievements()
                print(f"Achievement unlocked: {achievement.name} - {achievement.description}")
                if self.notification_callback:
                    self.notification_callback(achievement.name, achievement.description)
                return True
        return False

    def is_unlocked(self, name):
        for achievement in self.achievements:
            if achievement.name == name:
                return achievement.unlocked
        return False
