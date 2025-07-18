import pygame
import json
import os
import math
from modul.constants import *


class ShipManager:
    def __init__(self):
        self.ships_file = "ships.json"
        self.unlocked_ships = self.load_unlocked_ships()

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
        if os.path.exists(self.ships_file):
            try:
                with open(self.ships_file, "r") as f:
                    data = json.load(f)
                    return data.get("unlocked_ships", [])
            except:
                return []
        return []

    def save_unlocked_ships(self):
        data = {"unlocked_ships": self.unlocked_ships}
        try:
            with open(self.ships_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving ships: {e}")

    def unlock_ship(self, ship_id):
        if ship_id not in self.unlocked_ships and ship_id in self.ships:
            self.unlocked_ships.append(ship_id)
            self.ships[ship_id]["unlocked"] = True
            self.save_unlocked_ships()
            return True
        return False

    def unlock_ship_with_notification(self, ship_id, notification_callback=None):
        if self.unlock_ship(ship_id):
            ship_name = self.ships[ship_id]["name"]
            print(f"🚀 {ship_name} unlocked!")
            if notification_callback:
                notification_callback(f" {ship_name} unlocked!", "New ship available in ship selection!")
            return True
        return False

    def check_unlock_conditions(self, level, difficulty, notification_callback=None):
        unlocked_any = False

        if level >= 50:
            if difficulty == "easy" and not self.ships["speedster"]["unlocked"]:
                if self.unlock_ship("speedster"):
                    unlocked_any = True
                    ship_name = self.ships["speedster"]["name"]
                    print(f"🚀 {ship_name} unlocked!")
                    if notification_callback:
                        notification_callback(f" {ship_name} unlocked!", "New ship available in ship selection!")

            elif difficulty == "normal" and not self.ships["tank"]["unlocked"]:
                if self.unlock_ship("tank"):
                    unlocked_any = True
                    ship_name = self.ships["tank"]["name"]
                    print(f"🚀 {ship_name} unlocked!")
                    if notification_callback:
                        notification_callback(f" {ship_name} unlocked!", "New ship available in ship selection!")

            elif difficulty == "hard" and not self.ships["destroyer"]["unlocked"]:
                if self.unlock_ship("destroyer"):
                    unlocked_any = True
                    ship_name = self.ships["destroyer"]["name"]
                    print(f"🚀 {ship_name} unlocked!")
                    if notification_callback:
                        notification_callback(f" {ship_name} unlocked!", "New ship available in ship selection!")

        return unlocked_any

    def get_ship_data(self, ship_id):
        return self.ships.get(ship_id, self.ships["standard"])

    def get_available_ships(self):
        return list(self.ships.keys())

    def get_unlocked_ships(self):
        return ["standard"] + [ship_id for ship_id in self.unlocked_ships if ship_id in self.ships]

    def set_current_ship(self, ship_id):
        if ship_id in self.ships and self.ships[ship_id]["unlocked"]:
            self.current_ship = ship_id
            return True
        return False

    def get_current_ship_data(self):
        return self.get_ship_data(self.current_ship)

    def is_ship_unlocked(self, ship_id):
        return ship_id in self.ships and self.ships[ship_id]["unlocked"]

    def check_all_ships_unlocked(self, achievement_system):
        if len(self.unlocked_ships) == len(self.ships):
            achievement_system.unlock("Fleet Commander")


class ShipRenderer:

    @staticmethod
    def draw_ship(screen, x, y, rotation, ship_type, scale=1.0, color=(255, 255, 255)):

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
        font = pygame.font.Font(None, int(36 * scale))
        text = font.render("?", True, color)
        text_rect = text.get_rect(center=(x, y))
        screen.blit(text, text_rect)


ship_manager = ShipManager()
