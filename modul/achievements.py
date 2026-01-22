"""Module modul.achievements — minimal module docstring."""

import json


class Achievement:
    """TODO: add docstring."""
    def __init__(self, name, description):
        """TODO: add docstring."""
        self.name = name
        self.description = description
        self.unlocked = False

    def unlock(self):
        """TODO: add docstring."""
        self.unlocked = True


class AchievementSystem:
    """TODO: add docstring."""
    def __init__(self, achievements_file="achievements.json"):
        """TODO: add docstring."""
        self.achievements_file = achievements_file
        self.achievements = []
        self.notification_callback = None
        self.initialize_standard_achievements()
        self.load_unlocked_achievements()

    def set_notification_callback(self, callback):
        """TODO: add docstring."""
        self.notification_callback = callback

    def initialize_standard_achievements(self):
        """TODO: add docstring."""
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
            ("Triple Threat", "Use triple shot 20 times."),
            ("Fleet Commander", "Unlock all four spaceships."),
        ]
        for name, description in standard_achievements:
            achievement = Achievement(name, description)
            self.achievements.append(achievement)
        print(
            f"Standard achievements initialized in memory: {len(self.achievements)} entries"
        )

    def load_unlocked_achievements(self):
        """TODO: add docstring."""
        try:
            with open(self.achievements_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                for item in data:
                    if item.get("unlocked", False):
                        for achievement in self.achievements:
                            if achievement.name == item["name"]:
                                achievement.unlocked = True
                                break
                unlocked_count = len([a for a in self.achievements if a.unlocked])
                total_count = len(self.achievements)
                print(
                    f"Unlocked achievements loaded: {unlocked_count} of {total_count}"
                )
        except FileNotFoundError:
            print("Achievements file not found - all achievements are locked")
        except json.JSONDecodeError as e:
            print(f"Error loading achievements file: {e}")

    def save_unlocked_achievements(self):
        """TODO: add docstring."""
        unlocked_achievements = [
            {"name": achievement.name, "description": achievement.description, "unlocked": True}
            for achievement in self.achievements
            if achievement.unlocked
        ]
        if unlocked_achievements:
            with open(self.achievements_file, "w", encoding="utf-8") as file:
                json.dump(unlocked_achievements, file, indent=4)
            print(f"Unlocked achievements saved: {len(unlocked_achievements)} entries")
        else:
            print("No unlocked achievements to save")

    def load_achievements(self):
        """TODO: add docstring."""
        # Delegate to existing loader that reads unlocked achievements from file.
        # Keep this method for compatibility and potential future expansion.
        return self.load_unlocked_achievements()
    def save_achievements(self):
        """TODO: add docstring."""
        self.save_unlocked_achievements()

    def unlock_achievement(self, name):
        """TODO: add docstring."""
        for achievement in self.achievements:
            if achievement.name == name and not achievement.unlocked:
                achievement.unlock()
                self.save_unlocked_achievements()
                print(f"Achievement unlocked: {achievement.name} - {achievement.description}")
                if self.notification_callback:
                    ascii_art = """
                    ███████╗██╗     ███████╗████████╗
                    ██╔════╝██║     ██╔════╝╚══██╔══╝
                    █████╗  ██║     █████╗     ██║
                    ██╔══╝  ██║     ██╔══╝     ██║
                    ███████╗███████╗███████╗   ██║
                    ╚══════╝╚══════╝╚══════╝   ╚═╝
                    """
                    self.notification_callback(achievement.name, ascii_art)
                break

    def unlock(self, name):
        """TODO: add docstring."""
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
        """TODO: add docstring."""
        for achievement in self.achievements:
            if achievement.name == name:
                return achievement.unlocked
        return False

    def check_fleet_commander(self, ships):
        """TODO: add docstring."""
        if len(ships.unlocked_ships) == len(ships.ships):
            self.unlock("Fleet Commander")
