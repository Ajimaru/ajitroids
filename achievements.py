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
        self.load_achievements()

    def load_achievements(self):
        self.achievements.clear()  # Liste vor dem Laden leeren
        try:
            with open(self.achievements_file, 'r') as file:
                data = json.load(file)
                for item in data:
                    achievement = Achievement(item['name'], item['description'])
                    achievement.unlocked = item.get('unlocked', False)
                    self.achievements.append(achievement)
        except FileNotFoundError:
            self.save_achievements()

    def save_achievements(self):
        data = [
            {
                'name': achievement.name,
                'description': achievement.description,
                'unlocked': achievement.unlocked
            } for achievement in self.achievements
        ]
        with open(self.achievements_file, 'w') as file:
            json.dump(data, file, indent=4)

    def add_achievement(self, name, description):
        achievement = Achievement(name, description)
        self.achievements.append(achievement)
        self.save_achievements()

    def unlock_achievement(self, name):
        for achievement in self.achievements:
            if achievement.name == name and not achievement.unlocked:
                achievement.unlock()
                self.save_achievements()
                print(f"Achievement unlocked: {achievement.name} - {achievement.description}")
                break

    def unlock(self, name):
        for achievement in self.achievements:
            if achievement.name == name and not achievement.unlocked:
                achievement.unlock()
                self.save_achievements()
                print(f"Achievement unlocked: {achievement.name} - {achievement.description}")
                return True
        return False

    def is_unlocked(self, name):
        for achievement in self.achievements:
            if achievement.name == name:
                return achievement.unlocked
        return False
