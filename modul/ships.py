"""Ship definitions, persistence and rendering helpers."""

import json
import math
import os
import pygame
try:
    from modul.i18n import gettext
except (ImportError, ModuleNotFoundError):  # pragma: no cover - fallback when i18n unavailable
    def gettext(key):
        """
        Return the localized string for the given translation key or the key itself if no translation is available.
        
        Parameters:
            key (str): Translation lookup key.
        
        Returns:
            str: Localized string corresponding to `key`, or `key` unchanged when no translation exists.
        """
        return key


class ShipManager:
    """Manage ship definitions, persistence and unlocks."""
    def __init__(self):
        """
        Initialize the ShipManager: load persisted unlocked ships and set up ship definitions and current selection.
        
        Sets self.ships_file to "ships.json", loads persisted unlocked ship IDs into self.unlocked_ships, constructs self.ships with each ship's metadata (initializing each ship's "unlocked" flag from self.unlocked_ships; "standard" is always unlocked), and sets self.current_ship to "standard".
        """
        self.ships_file = "ships.json"
        self.unlocked_ships = self.load_unlocked_ships()

        # The 'unlocked' key for each ship is initialized from self.unlocked_ships here in __init__,
        # and may be updated later by unlock_ship(), which mutates both self.unlocked_ships and ships[ship_id]['unlocked'].
        # This is not a dynamic property; it is an initial state that unlock_ship() can change.
        self.ships = {
            "standard": {
                "name": "Standard Fighter",
                "description": "Balanced ship for all pilots",
                "unlocked": True,
                "unlock_condition": "Always available",
                "speed_multiplier": 1.0,
                "turn_speed_multiplier": 1.0,
                "special_ability": "none",
                "shape": "triangle",
                "color": (255, 255, 255),
            },
            "speedster": {
                "name": "Lightning Speedster",
                "description": "Fast and agile",
                "unlocked": "speedster" in self.unlocked_ships,
                "unlock_condition": "Reach Level 50 on Easy",
                "speed_multiplier": 1.5,
                "turn_speed_multiplier": 1.3,
                "special_ability": "speed_boost",
                "shape": "arrow",
                "color": (255, 255, 0),
            },
            "tank": {
                "name": "Heavy Cruiser",
                "description": "Shoots backwards while moving forward",
                "unlocked": "tank" in self.unlocked_ships,
                "unlock_condition": "Reach Level 50 on Normal",
                "speed_multiplier": 0.7,
                "turn_speed_multiplier": 0.8,
                "special_ability": "rear_shot",
                "shape": "heavy",
                "color": (0, 255, 0),
            },
            "destroyer": {
                "name": "Plasma Destroyer",
                "description": "Powerful shots, glass cannon",
                "unlocked": "destroyer" in self.unlocked_ships,
                "unlock_condition": "Reach Level 50 on Hard",
                "speed_multiplier": 0.9,
                "turn_speed_multiplier": 1.1,
                "special_ability": "double_damage",
                "shape": "destroyer",
                "color": (255, 0, 0),
            },
        }

        self.current_ship = "standard"

    def load_unlocked_ships(self):
        """Load the list of unlocked ships from the ships file on disk."""
        if os.path.exists(self.ships_file):
            try:
                with open(self.ships_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("unlocked_ships", [])
            except Exception as e:  # pylint: disable=broad-exception-caught
                print(f"Error loading ships file {self.ships_file}: {e}")
                return []
        return []

    def save_unlocked_ships(self):
        """Persist the unlocked ships list to disk, handling IO errors."""
        data = {"unlocked_ships": self.unlocked_ships}
        try:
            with open(self.ships_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error saving ships: {e}")

    def unlock_ship(self, ship_id):
        """Mark a ship as unlocked and persist the change."""
        if ship_id not in self.unlocked_ships and ship_id in self.ships:
            self.unlocked_ships.append(ship_id)
            self.ships[ship_id]["unlocked"] = True
            self.save_unlocked_ships()
            return True
        return False

    def unlock_ship_with_notification(self, ship_id, notification_callback=None):
        """
        Unlock the ship identified by ship_id and optionally send a user-facing notification via a callback.
        
        Parameters:
            ship_id (str): Identifier of the ship to unlock.
            notification_callback (callable, optional): If provided and the ship is unlocked, called with two string arguments
                (short_message, detailed_message) describing the unlock. Example: (f" {ship_name} unlocked!", "New ship available in ship selection!")
        
        Returns:
            bool: `True` if the ship was unlocked by this call, `False` otherwise.
        """
        if self.unlock_ship(ship_id):
            ship_name = self.ships[ship_id]["name"]
            print(f"🚀 {ship_name} unlocked!")
            if notification_callback:
                notification_callback(f" {ship_name} unlocked!", "New ship available in ship selection!")
            return True
        return False

    def check_unlock_conditions(self, level, difficulty, notification_callback=None):
        """
        Unlock ships when the player reaches the required level for the given difficulty and notify if an unlock occurs.
        
        If `level` is at least 50, maps `difficulty` to a specific ship ("easy"→"speedster", "normal"→"tank", "hard"→"destroyer") and attempts to unlock that ship if it is not already unlocked. When an unlock occurs and `notification_callback` is provided, the callback is invoked with a pair of strings (title, message).
        
        Parameters:
            level (int): The player's current level.
            difficulty (str): Difficulty identifier; expected values are "easy", "normal", or "hard".
            notification_callback (callable, optional): Function called on successful unlock with signature callback(title: str, message: str).
        
        Returns:
            bool: `true` if a ship was unlocked by this call, `false` otherwise.
        """
        unlocked_any = False
        if level >= 50:
            ship_key = None
            if difficulty == "easy":
                ship_key = "speedster"
            elif difficulty == "normal":
                ship_key = "tank"
            elif difficulty == "hard":
                ship_key = "destroyer"
            if ship_key and not self.ships[ship_key]["unlocked"]:
                if self.unlock_ship_with_notification(ship_key, notification_callback):
                    unlocked_any = True
        return unlocked_any

    def get_ship_data(self, ship_id):
        """
        Get the ship data dictionary for the given ship_id, falling back to the standard ship if not found.
        
        Returns:
            dict: The ship data for ship_id, or the "standard" ship data when ship_id is not defined.
        """
        return self.ships.get(ship_id, self.ships["standard"])

    def get_available_ships(self):
        """Return the list of available ship IDs."""
        return list(self.ships.keys())

    def get_unlocked_ships(self):
        """Return a list of currently unlocked ship IDs (including standard)."""
        return ["standard"] + [ship_id for ship_id in self.unlocked_ships if ship_id in self.ships]

    def set_current_ship(self, ship_id):
        """Set the currently selected ship if unlocked."""
        if ship_id in self.ships and self.ships[ship_id]["unlocked"]:
            self.current_ship = ship_id
            return True
        return False

    def get_current_ship_data(self):
        """Return the data for the currently selected ship."""
        return self.get_ship_data(self.current_ship)

    def is_ship_unlocked(self, ship_id):
        """Return whether the given ship_id is unlocked."""
        return ship_id in self.ships and self.ships[ship_id]["unlocked"]

    def check_all_ships_unlocked(self, achievement_system):
        """
        Unlock the "Fleet Commander" achievement when every non-default ship has been unlocked.
        
        Checks all ships defined in self.ships except the default "standard" and, if each non-default ship ID is present in self.unlocked_ships, invokes achievement_system.unlock("Fleet Commander").
        
        Parameters:
            achievement_system: An object exposing an unlock(achievement_id: str) method; called with "Fleet Commander" when the condition is met.
        """
        # Consider the default 'standard' ship which is always available.
        # Trigger the achievement when every non-default ship is present in
        # the unlocked_ships list.
        all_non_default = all(
            ship_id == "standard" or ship_id in self.unlocked_ships for ship_id in self.ships
        )
        if all_non_default:
            achievement_system.unlock("Fleet Commander")


class ShipRenderer:
    """Utility class that draws different ship shapes to a surface."""

    @staticmethod
    def draw_ship(screen, x, y, rotation, ship_type, scale=1.0, color=(255, 255, 255)):
        """Draw the specified `ship_type` at position with rotation and color."""
        if ship_type == "triangle" or ship_type == "standard":
            ShipRenderer.draw_triangle_ship(screen, x, y, rotation, scale, color)
        elif ship_type == "arrow":
            ShipRenderer.draw_arrow_ship(screen, x, y, rotation, scale, color)
        elif ship_type == "heavy":
            ShipRenderer.draw_heavy_ship(screen, x, y, rotation, scale, color)
        elif ship_type == "destroyer":
            ShipRenderer.draw_destroyer_ship(screen, x, y, rotation, scale, color)
        else:
            ShipRenderer.draw_question_mark(screen, x, y, scale, color)

    @staticmethod
    def draw_triangle_ship(screen, x, y, rotation, scale, color):
        """Draw the triangle/standard ship shape with rotation and scale."""
        points = [(0, -15 * scale), (-12 * scale, 15 * scale), (12 * scale, 15 * scale)]

        rotated_points = []
        for px, py in points:
            cos_r = math.cos(math.radians(rotation))
            sin_r = math.sin(math.radians(rotation))
            new_x = px * cos_r - py * sin_r + x
            new_y = px * sin_r + py * cos_r + y
            rotated_points.append((new_x, new_y))

        pygame.draw.polygon(screen, color, rotated_points, 2)

    @staticmethod
    def draw_arrow_ship(screen, x, y, rotation, scale, color):
        """Draw an arrow-shaped ship used for the speedster."""
        points = [
            (0, -18 * scale),
            (-9 * scale, 3 * scale),
            (-6 * scale, 12 * scale),
            (0, 9 * scale),
            (6 * scale, 12 * scale),
            (9 * scale, 3 * scale),
        ]

        rotated_points = []
        for px, py in points:
            cos_r = math.cos(math.radians(rotation))
            sin_r = math.sin(math.radians(rotation))
            new_x = px * cos_r - py * sin_r + x
            new_y = px * sin_r + py * cos_r + y
            rotated_points.append((new_x, new_y))

        pygame.draw.polygon(screen, color, rotated_points, 2)

    @staticmethod
    def draw_heavy_ship(screen, x, y, rotation, scale, color):
        """Draw the heavy cruiser ship shape with decorative details."""
        points = [
            (0, -12 * scale),
            (-18 * scale, 0),
            (-15 * scale, 18 * scale),
            (0, 12 * scale),
            (15 * scale, 18 * scale),
            (18 * scale, 0),
        ]

        rotated_points = []
        for px, py in points:
            cos_r = math.cos(math.radians(rotation))
            sin_r = math.sin(math.radians(rotation))
            new_x = px * cos_r - py * sin_r + x
            new_y = px * sin_r + py * cos_r + y
            rotated_points.append((new_x, new_y))

        pygame.draw.polygon(screen, color, rotated_points, 2)

        detail_points = [(-12 * scale, -3 * scale), (12 * scale, -3 * scale)]
        for px, py in detail_points:
            cos_r = math.cos(math.radians(rotation))
            sin_r = math.sin(math.radians(rotation))
            new_x = px * cos_r - py * sin_r + x
            new_y = px * sin_r + py * cos_r + y
            pygame.draw.circle(screen, color, (int(new_x), int(new_y)), 3)

    @staticmethod
    def draw_destroyer_ship(screen, x, y, rotation, scale, color):
        """Draw the destroyer ship shape including weapon nodes."""
        points = [
            (0, -15 * scale),
            (-9 * scale, 0),
            (-12 * scale, 15 * scale),
            (0, 9 * scale),
            (12 * scale, 15 * scale),
            (9 * scale, 0),
        ]

        rotated_points = []
        for px, py in points:
            cos_r = math.cos(math.radians(rotation))
            sin_r = math.sin(math.radians(rotation))
            new_x = px * cos_r - py * sin_r + x
            new_y = px * sin_r + py * cos_r + y
            rotated_points.append((new_x, new_y))

        pygame.draw.polygon(screen, color, rotated_points, 2)

        weapon_points = [(-6 * scale, -9 * scale), (6 * scale, -9 * scale), (-9 * scale, 6 * scale), (9 * scale, 6 * scale)]

        for px, py in weapon_points:
            cos_r = math.cos(math.radians(rotation))
            sin_r = math.sin(math.radians(rotation))
            new_x = px * cos_r - py * sin_r + x
            new_y = px * sin_r + py * cos_r + y
            pygame.draw.circle(screen, color, (int(new_x), int(new_y)), 1)

    @staticmethod
    def draw_question_mark(screen, x, y, scale, color):
        """
        Render a localized question-mark glyph (or "?" fallback) centered at (x, y) to represent unknown ship types.
        
        Parameters:
            screen (pygame.Surface): Destination surface to draw onto.
            x (int|float): X coordinate of the glyph center.
            y (int|float): Y coordinate of the glyph center.
            scale (float): Scale factor multiplied by the base font size (36) to compute the rendered size.
            color (tuple[int, int, int]): RGB color used to render the glyph.
        
        Notes:
            Uses `gettext("question_mark")` and falls back to "?" if the translation is missing or equals the key.
        """
        font = pygame.font.Font(None, int(36 * scale))
        symbol = gettext("question_mark")
        # Treat the untranslated key as missing (gettext often returns the key)
        if not symbol or symbol == "question_mark":
            symbol = "?"
        text = font.render(symbol, True, color)
        text_rect = text.get_rect(center=(x, y))
        screen.blit(text, text_rect)


ship_manager = ShipManager()