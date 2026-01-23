"""Module modul.achievements — minimal module docstring."""

import json


class Achievement:
    """Represents a single achievement with name, description, and unlock status."""
    def __init__(self, name, description):
        """Initialize an achievement with name and description."""
        self.name = name
        self.description = description
        self.unlocked = False

    def unlock(self):
        """Mark the achievement as unlocked."""
        self.unlocked = True


class AchievementSystem:
    """Manages achievements, loading, saving, and unlocking."""
    def __init__(self, achievements_file="achievements.json"):
        """Initialize the achievement system with file path."""
        self.achievements_file = achievements_file
        self.achievements = []
        self.notification_callback = None
        self.initialize_standard_achievements()
        self.load_unlocked_achievements()

    def set_notification_callback(self, callback):
        """Set the callback function for achievement notifications."""
        self.notification_callback = callback

    def initialize_standard_achievements(self):
        """Initialize the list of standard achievements."""
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
        """Load unlocked achievements from the JSON file."""
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
        """Save unlocked achievements to the JSON file."""
        unlocked_achievements = [
            {"name": achievement.name, "description": achievement.description, "unlocked": True}
            for achievement in self.achievements
            if achievement.unlocked
        ]
        if unlocked_achievements:
            try:
                with open(self.achievements_file, "w", encoding="utf-8") as file:
                    json.dump(unlocked_achievements, file, indent=4)
                print(f"Unlocked achievements saved: {len(unlocked_achievements)} entries")
            except OSError as e:
                print(f"Failed to save achievements to {self.achievements_file}: {e}")
        else:
            # When there are no unlocked achievements, write an empty list
            # to avoid leaving a stale file with previous data.
            try:
                with open(self.achievements_file, "w", encoding="utf-8") as file:
                    json.dump([], file, indent=4)
                print(f"No unlocked achievements; wrote empty list to {self.achievements_file}")
            except OSError as e:
                print(f"Failed to write empty achievements file {self.achievements_file}: {e}")

    def load_achievements(self):
        """Load achievements (delegates to load_unlocked_achievements)."""
        # Delegate to existing loader that reads unlocked achievements from file.
        # Keep this method for compatibility and potential future expansion.
        return self.load_unlocked_achievements()

    def save_achievements(self):
        """Save achievements (delegates to save_unlocked_achievements)."""
        self.save_unlocked_achievements()

    def unlock(self, name, use_ascii=False):
        """Unlock an achievement by name. If use_ascii is True, show ASCII art in notification."""
        for achievement in self.achievements:
            if achievement.name == name and not achievement.unlocked:
                achievement.unlock()
                self.save_unlocked_achievements()
                print(f"Achievement unlocked: {achievement.name} - {achievement.description}")
                if self.notification_callback:
                    # If ASCII notifications were requested, try to use a per-achievement
                    # ASCII art mapping. Fall back to the description when no art exists.
                    if use_ascii:
                        ascii_map = {
                            "Fleet Commander": """
███████╗██╗     ███████╗████████╗
██╔════╝██║     ██╔════╝╚══██╔══╝
█████╗  ██║     █████╗     ██║
██╔══╝  ██║     ██╔══╝     ██║
███████╗███████╗███████╗   ██║
╚══════╝╚══════╝╚══════╝   ╚═╝
""",
                        }
                        # Other achievements may be added here in the future
                        ascii_art = ascii_map.get(achievement.name)
                        if ascii_art:
                            self.notification_callback(achievement.name, ascii_art)
                        else:
                            # No ascii art available for this achievement; send description
                            self.notification_callback(achievement.name, achievement.description)
                    else:
                        self.notification_callback(achievement.name, achievement.description)
                return True
        return False

    def is_unlocked(self, name):
        """Check if an achievement is unlocked."""
        for achievement in self.achievements:
            if achievement.name == name:
                return achievement.unlocked
        return False

    def check_fleet_commander(self, ships):
        """Check and unlock Fleet Commander achievement if all ships are unlocked."""
        # Defensive checks: ensure ships object exists and has expected attributes
        if not ships:
            return False
        if not (hasattr(ships, "unlocked_ships") and hasattr(ships, "ships")):
            return False

        try:
            if len(ships.unlocked_ships) == len(ships.ships):
                # Prefer an ASCII notification for Fleet Commander unlocks
                self.unlock("Fleet Commander", use_ascii=True)
                return True
        except Exception:
            # Defensive: do not raise from stats/achievement checks
            return False
        return False

    def unlock_achievement(self, name, use_ascii=True):
        """Deprecated compatibility wrapper for older API tests.

        Historically tests and older code called `unlock_achievement(name)`.
        Keep a small wrapper that forwards to the newer `unlock` method.
        """
        return self.unlock(name, use_ascii=use_ascii)
