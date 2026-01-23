"""Module modul.achievements — minimal module docstring."""

import json


class Achievement:
    """Represents a single achievement with name, description, and unlock status."""
    def __init__(self, name, description):
        """
        Create an Achievement with a display name and description.
        
        Parameters:
            name (str): The achievement's display name.
            description (str): Short text shown when the achievement is unlocked.
        
        Notes:
            The achievement's unlocked state is initialized to False.
        """
        self.name = name
        self.description = description
        self.unlocked = False

    def unlock(self):
        """Mark the achievement as unlocked."""
        self.unlocked = True


class AchievementSystem:
    """Manages achievements, loading, saving, and unlocking."""
    def __init__(self, achievements_file="achievements.json"):
        """
        Initialize the AchievementSystem and restore persisted unlock state.
        
        Sets the path used for persistence, prepares the in-memory achievements list and notification callback, populates standard achievements, and loads any previously unlocked achievements from the configured JSON file.
        
        Parameters:
            achievements_file (str): Path to the JSON file where unlocked achievements are stored (defaults to "achievements.json").
        """
        self.achievements_file = achievements_file
        self.achievements = []
        self.notification_callback = None
        self.initialize_standard_achievements()
        self.load_unlocked_achievements()

    def set_notification_callback(self, callback):
        """
        Register a notification callback for unlocked achievements.
        
        Parameters:
            callback (callable): Function to invoke when an achievement is unlocked. If the achievement is unlocked with use_ascii=True the callback is called with a single string argument (ASCII art or the achievement description). Otherwise the callback is called with two arguments: (name, description).
        """
        self.notification_callback = callback

    def initialize_standard_achievements(self):
        """
        Populate self.achievements with a predefined set of standard Achievement instances.
        
        Creates and appends a fixed list of standard achievements (name and description pairs) to the existing in-memory achievements list; does not modify persistent storage.
        """
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
        """
        Update in-memory achievements' unlocked state from the achievements JSON file.
        
        Reads self.achievements_file, and for each entry with "unlocked": true sets the corresponding Achievement.instance's `unlocked` attribute to True by matching on name. If the file is missing or malformed, leaves achievements' unlocked states unchanged and reports the issue via printed messages.
        """
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
        """
        Persist unlocked achievements to the configured JSON file.
        
        Writes a JSON array of unlocked achievements (each object contains `name`, `description`, and `unlocked: True`) to self.achievements_file. If no achievements are unlocked, writes an empty list to avoid leaving stale data on disk. File write failures are caught and reported.
        """
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
        """
        Load persisted unlocked achievements for backward compatibility.
        """
        # Delegate to existing loader that reads unlocked achievements from file.
        # Keep this method for compatibility and potential future expansion.
        return self.load_unlocked_achievements()

    def save_achievements(self):
        """Save achievements (delegates to save_unlocked_achievements)."""
        self.save_unlocked_achievements()

    def unlock(self, name, use_ascii=False):
        """
        Unlocks the named achievement and persists the updated unlocked state.
        
        Parameters:
            name (str): The exact name of the achievement to unlock.
            use_ascii (bool): If True and a notification callback is set, attempt to send per-achievement ASCII art to the callback; if no ASCII art exists for the achievement, the achievement description is sent. If False, the description is sent to the callback when present.
        
        Returns:
            bool: `True` if an existing, locked achievement was found and unlocked by this call; `False` otherwise.
        """
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
        """
        Determine whether an achievement with the given name is unlocked.
        
        Parameters:
            name (str): The achievement name to look up.
        
        Returns:
            True if an achievement with that name exists and is unlocked, False otherwise.
        """
        for achievement in self.achievements:
            if achievement.name == name:
                return achievement.unlocked
        return False

    def check_fleet_commander(self, ships):
        """
        Determine whether the Fleet Commander achievement should be unlocked based on the provided ships state.
        
        If the ships object has matching `unlocked_ships` and `ships` attributes and every ship is unlocked, unlocks the "Fleet Commander" achievement and prefers an ASCII notification. The function performs defensive checks and returns without raising on invalid input or unexpected errors.
        
        Parameters:
            ships: An object expected to have `unlocked_ships` and `ships` attributes (both iterable). If `ships` is falsy or missing these attributes, the function will do nothing.
        
        Returns:
            True if the achievement was unlocked, False otherwise.
        """
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

    def unlock_achievement(self, name, use_ascii=False):
        """
        Compatibility wrapper that forwards to `unlock` for backward compatibility.
        
        Deprecated: call `unlock(name, use_ascii=...)` directly.
        
        Parameters:
        	name (str): The achievement name to unlock.
        	use_ascii (bool): If True, request ASCII-art notification when available.
        
        Returns:
        	bool: `True` if the achievement was unlocked, `False` otherwise.
        """
        return self.unlock(name, use_ascii=use_ascii)