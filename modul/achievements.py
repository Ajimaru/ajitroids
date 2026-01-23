"""Module modul.achievements — minimal module docstring."""

import json


class Achievement:
    """Represents a single achievement with name, description, and unlock status."""
    def __init__(self, name, description):
        """
        Create an Achievement with a name, description, and default locked state.
        
        Parameters:
            name (str): Display name of the achievement.
            description (str): Short description shown when the achievement is unlocked.
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
        Initialize the achievement system and load persisted unlocked achievements.
        
        Parameters:
            achievements_file (str): Path to the JSON file used to persist unlocked achievements. Defaults to "achievements.json".
        
        Description:
            Sets up internal state (file path, achievement list, notification callback), populates the standard achievements, and loads any previously unlocked achievements from the specified file.
        """
        self.achievements_file = achievements_file
        self.achievements = []
        self.notification_callback = None
        self.initialize_standard_achievements()
        self.load_unlocked_achievements()

    def set_notification_callback(self, callback):
        """
        Register a callback to be invoked when an achievement is unlocked.
        
        Parameters:
            callback (callable): A function accepting two positional arguments: (name: str, payload: str).
                - `name` is the achievement name.
                - `payload` is either ASCII art for the achievement (when enabled and available) or the achievement description.
        """
        self.notification_callback = callback

    def initialize_standard_achievements(self):
        """
        Populate self.achievements with the application's predefined standard Achievement instances.
        
        Creates Achievement objects for the canonical set of in-game achievements (name and description) and appends them to the system's in-memory achievements list; logs the total count added.
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
        Load unlocked achievements from the achievements JSON file.
        
        Marks in-memory Achievement instances as unlocked when the file contains entries with "unlocked": true, prints a summary of loaded vs total achievements, and leaves achievements locked while printing an explanatory message if the file is missing or contains invalid JSON.
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
        Persist currently unlocked achievements to the configured JSON file.
        
        Writes a JSON array of unlocked achievements (each with name, description, and unlocked=true) to the achievements file. If no achievements are unlocked, writes an empty list to avoid leaving stale data. File I/O errors are caught and reported via printed messages; the method does not raise on OSError.
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
        Load previously unlocked achievements from persistent storage into the in-memory list.
        
        This method preserves the public API for callers that expect a `load_achievements` entrypoint and may be extended in the future.
        """
        # Delegate to existing loader that reads unlocked achievements from file.
        # Keep this method for compatibility and potential future expansion.
        return self.load_unlocked_achievements()

    def save_achievements(self):
        """
        Persist the currently unlocked achievements to the configured achievements file.
        
        This writes the set of unlocked achievements so future runs can restore their state.
        """
        self.save_unlocked_achievements()

    def unlock(self, name, use_ascii=False):
        """
        Unlock the achievement matching `name` and persist the unlocked state.
        
        If the achievement is unlocked and a notification callback is registered, the callback
        is invoked with the achievement name and either ASCII art (when `use_ascii` is True
        and art is available) or the achievement description.
        
        Parameters:
            name (str): The name of the achievement to unlock.
            use_ascii (bool): When True, prefer sending ASCII art to the notification callback
                if an ASCII representation exists for the achievement.
        
        Returns:
            `True` if an achievement was unlocked by this call, `False` otherwise.
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
        Determine whether the achievement with the given name is unlocked.
        
        Parameters:
            name (str): The achievement name to check.
        
        Returns:
            bool: `True` if the achievement exists and is unlocked, `False` otherwise.
        """
        for achievement in self.achievements:
            if achievement.name == name:
                return achievement.unlocked
        return False

    def check_fleet_commander(self, ships):
        """
        Check whether all ships are unlocked and unlock the "Fleet Commander" achievement.
        
        Performs validation on the provided ships object (it must have `unlocked_ships` and `ships` attributes). If the counts of unlocked ships and total ships are equal, unlocks the "Fleet Commander" achievement and requests an ASCII notification.
        
        Parameters:
            ships: An object with `unlocked_ships` and `ships` attributes (both iterable/collection-like).
        
        Returns:
            True if the achievement was unlocked, False otherwise (including when `ships` is invalid or an error occurs).
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
        Provide a backward-compatible API to unlock an achievement by name.
        
        Deprecated: kept for backward compatibility with older tests and code.
        
        Parameters:
            name (str): The name of the achievement to unlock.
            use_ascii (bool): If True, request an ASCII-art notification when unlocking.
        
        Returns:
            bool: `True` if the achievement was unlocked, `False` otherwise.
        """
        return self.unlock(name, use_ascii=use_ascii)