"""Player class, input handling and player-related mechanics."""

import math

import pygame

import modul.constants as C
from modul.circleshape import CircleShape
from modul.ships import ShipRenderer, ship_manager
from modul.shot import Shot
from modul.sounds import Sounds


# Bind optional runtime helpers at module import time to avoid repeated
# dynamic imports inside methods and to satisfy linters (C0415).
try:
    from modul import input_utils  # type: ignore
except Exception:  # pragma: no cover - provide minimal runtime stub
    class _InputUtilsStub:  # pylint: disable=too-few-public-methods
        @staticmethod
        def is_action_pressed(name):
            return False

        @staticmethod
        def get_action_keycode(name):
            return None

    input_utils = _InputUtilsStub()

try:
    from modul.i18n import gettext  # type: ignore
except Exception:  # pragma: no cover - fallback when i18n unavailable
    def gettext(k):
        return k


class Player(CircleShape):
    """TODO: add docstring."""
    def __init__(self, x, y, ship_type="standard"):
        """TODO: add docstring."""
        super().__init__(x, y, C.PLAYER_RADIUS)
        self.rotation = 0
        self.velocity = pygame.Vector2(0, 0)
        self.shoot_timer = 0
        self.invincible = False
        self.invincible_timer = 0
        self.sounds = Sounds()
        self.shield_active = False

        self.shield_timer = 0
        self.triple_shot_active = False
        self.triple_shot_timer = 0
        self.rapid_fire_active = False
        self.rapid_fire_timer = 0
        self.original_cooldown = C.PLAYER_SHOOT_COOLDOWN
        self.current_weapon = C.WEAPON_STANDARD
        self.weapon_switch_timer = 0
        self.weapons = {C.WEAPON_STANDARD: -1, C.WEAPON_LASER: 0, C.WEAPON_MISSILE: 0, C.WEAPON_SHOTGUN: 0}

        self.ship_type = ship_type
        self.ship_data = ship_manager.get_ship_data(ship_type)
        self.apply_ship_modifiers()

    def apply_ship_modifiers(self):
        """TODO: add docstring."""
        self.base_speed = C.PLAYER_SPEED * self.ship_data["speed_multiplier"]
        self.base_turn_speed = C.PLAYER_TURN_SPEED * self.ship_data["turn_speed_multiplier"]

        special = self.ship_data["special_ability"]
        if special == "rear_shot":
            self.shield_duration_multiplier = 1.0
            self.damage_multiplier = 1.0
            self.has_rear_shot = True
        elif special == "speed_boost":
            self.base_speed *= 1.2
            self.shield_duration_multiplier = 1.0
            self.damage_multiplier = 1.0
            self.has_rear_shot = False
        elif special == "double_damage":
            self.damage_multiplier = 2.0
            self.shield_duration_multiplier = 1.0
            self.has_rear_shot = False
        else:
            self.shield_duration_multiplier = 1.0
            self.damage_multiplier = 1.0
            self.has_rear_shot = False

    def draw(self, screen):
        """TODO: add docstring."""
        if (not self.invincible or pygame.time.get_ticks() % 200 < 100) or self.shield_active:
            if self.shield_active:
                ship_color = C.POWERUP_COLORS.get("shield", "cyan")
            else:
                ship_color = self.ship_data.get("color", (255, 255, 255))
            ShipRenderer.draw_ship(
                screen, self.position.x, self.position.y, self.rotation, self.ship_data["shape"], 1.0, ship_color
            )

        if self.shield_active:
            alpha = int(128 + 127 * abs(math.sin(pygame.time.get_ticks() * 0.005)))
            shield_color = C.POWERUP_COLORS["shield"]
            shield_surf = pygame.Surface((self.radius * 3, self.radius * 3), pygame.SRCALPHA)

            color_obj = pygame.Color(shield_color)
            rgba_color = (color_obj.r, color_obj.g, color_obj.b, alpha)

            pygame.draw.circle(shield_surf, rgba_color, (self.radius * 1.5, self.radius * 1.5), self.radius * 1.4, 2)
            screen.blit(shield_surf, (self.position.x - self.radius * 1.5, self.position.y - self.radius * 1.5))

    def triangle(self):
        """TODO: add docstring."""
        forward = pygame.Vector2(0, -1).rotate(self.rotation)
        right = pygame.Vector2(1, 0).rotate(self.rotation) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def update(self, dt):
        # Use input utilities which consult runtime settings for remappable controls
        """TODO: add docstring."""
        # use module-level `input_utils` bound at import time

        current_speed = self.base_speed
        current_turn_speed = self.base_turn_speed

        if input_utils.is_action_pressed("rotate_left"):
            self.rotate(-current_turn_speed * dt)
        if input_utils.is_action_pressed("rotate_right"):
            self.rotate(current_turn_speed * dt)
        if input_utils.is_action_pressed("thrust"):
            self.velocity += self.forward() * current_speed * dt
        if input_utils.is_action_pressed("reverse"):
            self.velocity -= self.forward() * current_speed * dt

        if input_utils.is_action_pressed("shoot"):
            self.shoot()

        if input_utils.is_action_pressed("switch_weapon"):
            self.cycle_weapon()

        max_speed = getattr(self, "max_speed", 400)
        if self.velocity.length() > max_speed:
            self.velocity = self.velocity.normalize() * max_speed

        friction = 0.98
        self.velocity *= friction

        self.position += self.velocity * dt

        if self.shoot_timer > 0:
            self.shoot_timer -= dt

        if self.invincible_timer > 0:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                self.invincible = False

        if self.shield_timer > 0:
            self.shield_timer -= dt
            if self.shield_timer <= 0:
                self.shield_active = False
                self.invincible = False

        if self.triple_shot_timer > 0:
            self.triple_shot_timer -= dt
            if self.triple_shot_timer <= 0:
                self.triple_shot_active = False

        if self.rapid_fire_timer > 0:
            self.rapid_fire_timer -= dt
            if self.rapid_fire_timer <= 0:
                self.rapid_fire_active = False

        if self.weapon_switch_timer > 0:
            self.weapon_switch_timer -= dt

    def shoot(self):
        """TODO: add docstring."""
        if self.shoot_timer <= 0:

            if self.current_weapon != C.WEAPON_STANDARD and self.weapons[self.current_weapon] <= 0:

                found_alternative = False
                for weapon_type, ammo in self.weapons.items():
                    if weapon_type != C.WEAPON_STANDARD and weapon_type != self.current_weapon and ammo > 0:
                        self.current_weapon = weapon_type
                        print(f"Auto-switched to {weapon_type} (Ammo: {ammo})")
                        found_alternative = True
                        break

                if not found_alternative:
                    self.current_weapon = C.WEAPON_STANDARD
                    print("Auto-switched to standard weapon (no special weapons with ammo)")

            if self.current_weapon == C.WEAPON_STANDARD:
                if self.triple_shot_active:
                    self.fire_triple_shot()
                else:
                    shot = Shot(self.position.x, self.position.y)
                    shot.velocity = pygame.Vector2(0, -1).rotate(self.rotation) * C.PLAYER_SHOOT_SPEED

                    if hasattr(self, "has_rear_shot") and self.has_rear_shot:
                        rear_shot = Shot(self.position.x, self.position.y)
                        rear_shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * C.PLAYER_SHOOT_SPEED * 0.8

            elif self.current_weapon == C.WEAPON_LASER:
                shot = Shot(self.position.x, self.position.y, C.WEAPON_LASER)
                shot.velocity = pygame.Vector2(0, -1).rotate(self.rotation) * C.PLAYER_SHOOT_SPEED * 1.5
                self.weapons[C.WEAPON_LASER] -= 1

                if hasattr(self, "has_rear_shot") and self.has_rear_shot:
                    rear_shot = Shot(self.position.x, self.position.y)
                    rear_shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * C.PLAYER_SHOOT_SPEED * 0.8

            elif self.current_weapon == C.WEAPON_MISSILE:
                shot = Shot(self.position.x, self.position.y, C.WEAPON_MISSILE)
                shot.velocity = pygame.Vector2(0, -1).rotate(self.rotation) * C.PLAYER_SHOOT_SPEED * 0.8
                self.weapons[C.WEAPON_MISSILE] -= 1

                if hasattr(self, "has_rear_shot") and self.has_rear_shot:
                    rear_shot = Shot(self.position.x, self.position.y)
                    rear_shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * C.PLAYER_SHOOT_SPEED * 0.8

            elif self.current_weapon == C.WEAPON_SHOTGUN:
                spread = 30
                for i in range(5):
                    angle = self.rotation + (i - 2) * (spread / 4)
                    shot = Shot(self.position.x, self.position.y, C.WEAPON_SHOTGUN)
                    shot.velocity = pygame.Vector2(0, -1).rotate(angle) * C.PLAYER_SHOOT_SPEED
                self.weapons[C.WEAPON_SHOTGUN] -= 1

                if hasattr(self, "has_rear_shot") and self.has_rear_shot:
                    rear_shot = Shot(self.position.x, self.position.y)
                    rear_shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * C.PLAYER_SHOOT_SPEED * 0.8

            if hasattr(self, "sounds") and self.sounds:
                self.sounds.play_shoot()

            if self.rapid_fire_active:
                self.shoot_timer = C.RAPID_FIRE_COOLDOWN
            else:
                self.shoot_timer = C.PLAYER_SHOOT_COOLDOWN

    def fire_triple_shot(self):
        """TODO: add docstring."""
        shot1 = Shot(self.position.x, self.position.y)
        shot1.velocity = pygame.Vector2(0, -1).rotate(self.rotation) * C.PLAYER_SHOOT_SPEED

        shot2 = Shot(self.position.x, self.position.y)
        shot2.velocity = pygame.Vector2(0, -1).rotate(self.rotation - 15) * C.PLAYER_SHOOT_SPEED

        shot3 = Shot(self.position.x, self.position.y)
        shot3.velocity = pygame.Vector2(0, -1).rotate(self.rotation + 15) * C.PLAYER_SHOOT_SPEED

        if hasattr(self, "has_rear_shot") and self.has_rear_shot:
            rear_shot = Shot(self.position.x, self.position.y)
            rear_shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * C.PLAYER_SHOOT_SPEED * 0.8

    def make_invincible(self):
        """TODO: add docstring."""
        self.invincible = True
        self.invincible_timer = C.INVINCIBILITY_TIME

    def respawn(self):
        """TODO: add docstring."""
        self.position.x = C.SCREEN_WIDTH / 2
        self.position.y = C.SCREEN_HEIGHT / 2
        self.velocity = pygame.Vector2(0, 0)
        self.rotation = 0

        self.invincible = True
        self.invincible_timer = 3.0

        self.shield_active = False
        self.shield_timer = 0
        self.triple_shot_active = False
        self.triple_shot_timer = 0
        self.rapid_fire_active = False
        self.rapid_fire_timer = 0
        self.shoot_timer = 0

        print("Player respawned with 3 seconds of invincibility")

    def activate_powerup(self, powerup_type):
        """TODO: add docstring."""
        if powerup_type == "shield":
            self.shield_active = True
            self.shield_timer = C.SHIELD_DURATION
            self.invincible = True

        elif powerup_type == "triple_shot":
            self.triple_shot_active = True
            self.triple_shot_timer = C.TRIPLE_SHOT_DURATION

        elif powerup_type == "rapid_fire":
            self.rapid_fire_active = True
            self.rapid_fire_timer = C.RAPID_FIRE_DURATION

        elif powerup_type == "laser_weapon":
            self.weapons[C.WEAPON_LASER] = min(self.weapons[C.WEAPON_LASER] + C.LASER_AMMO, C.LASER_AMMO)
            self.current_weapon = C.WEAPON_LASER
            print(f"Laser weapon activated! Ammo: {self.weapons[C.WEAPON_LASER]}")

        elif powerup_type == "missile_weapon":
            self.weapons[C.WEAPON_MISSILE] = min(self.weapons[C.WEAPON_MISSILE] + C.MISSILE_AMMO, C.MISSILE_AMMO)
            self.current_weapon = C.WEAPON_MISSILE
            print(f"Missile weapon activated! Ammo: {self.weapons[C.WEAPON_MISSILE]}")

        elif powerup_type == "shotgun_weapon":
            self.weapons[C.WEAPON_SHOTGUN] = min(self.weapons[C.WEAPON_SHOTGUN] + C.SHOTGUN_AMMO, C.SHOTGUN_AMMO)
            self.current_weapon = C.WEAPON_SHOTGUN
            print(f"Shotgun activated! Ammo: {self.weapons[C.WEAPON_SHOTGUN]}")

    def cycle_weapon(self):
        """TODO: add docstring."""
        if self.weapon_switch_timer > 0:
            return

        self.weapon_switch_timer = 0.2

        weapon_list = list(self.weapons.keys())
        current_index = weapon_list.index(self.current_weapon)

        for i in range(1, len(weapon_list)):
            next_index = (current_index + i) % len(weapon_list)
            next_weapon = weapon_list[next_index]

            if next_weapon == C.WEAPON_STANDARD or self.weapons[next_weapon] > 0:
                self.current_weapon = next_weapon
                if next_weapon == C.WEAPON_STANDARD:
                    print(f"Switched to standard weapon: {self.current_weapon}")
                else:
                    print(f"Weapon switched to: {self.current_weapon}, Ammo: {self.weapons[self.current_weapon]}")
                return

        self.current_weapon = C.WEAPON_STANDARD
        print(f"Fallback to standard weapon: {self.current_weapon}")

    def draw_weapon_hud(self, screen):
        """TODO: add docstring."""
        font_small = pygame.font.Font(None, 18)

        weapons_panel_x = C.SCREEN_WIDTH - 120
        weapons_panel_y = 10
        panel_width = 100
        panel_height = len(self.weapons) * 28 + 15

        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 120))
        pygame.draw.rect(panel_surface, (60, 60, 60), (0, 0, panel_width, panel_height), 1)
        screen.blit(panel_surface, (weapons_panel_x, weapons_panel_y))

        title_label = gettext("weapons")
        title_text = font_small.render(title_label, True, (200, 200, 200))
        screen.blit(title_text, (weapons_panel_x + 5, weapons_panel_y + 5))

        y_offset = 35
        max_ammo = {C.WEAPON_STANDARD: -1, C.WEAPON_LASER: C.LASER_AMMO, C.WEAPON_MISSILE: C.MISSILE_AMMO, C.WEAPON_SHOTGUN: C.SHOTGUN_AMMO}

        for weapon_type, ammo in self.weapons.items():
            weapon_y = weapons_panel_y + y_offset

            weapon_radius = 5
            weapon_icon_x = weapons_panel_x + 15

            if weapon_type == self.current_weapon:
                icon_color = C.WEAPON_COLORS[weapon_type]
                text_color = (255, 255, 255)
                pygame.draw.rect(screen, (255, 255, 0), (weapons_panel_x + 3, weapon_y - 9, panel_width - 6, 20), 1)
            elif weapon_type == C.WEAPON_STANDARD or ammo > 0:
                icon_color = C.WEAPON_COLORS[weapon_type]
                text_color = (200, 200, 200)
            else:
                icon_color = (80, 80, 80)
                text_color = (100, 100, 100)

            pygame.draw.circle(screen, icon_color, (weapon_icon_x, weapon_y), weapon_radius)

            weapon_name = weapon_type.replace("_", " ").title()
            if weapon_name == "Standard":
                weapon_name = "STD"
            elif weapon_name == "Laser":
                weapon_name = "LSR"
            elif weapon_name == "Missile":
                weapon_name = "MSL"
            elif weapon_name == "Shotgun":
                weapon_name = "SHG"

            name_text = font_small.render(weapon_name, True, text_color)
            screen.blit(name_text, (weapons_panel_x + 28, weapon_y - 5))

            if weapon_type == C.WEAPON_STANDARD:
                ammo_display = "99 / 99"
            else:
                max_ammo_val = max_ammo[weapon_type]
                ammo_display = f"{ammo}/{max_ammo_val}"

            ammo_text = font_small.render(ammo_display, True, text_color)
            ammo_rect = ammo_text.get_rect()
            screen.blit(ammo_text, (weapons_panel_x + panel_width - ammo_rect.width - 5, weapon_y - 5))

            y_offset += 25

        hint_label = gettext("b_to_switch")
        hint_text = font_small.render(hint_label, True, (120, 120, 120))
        screen.blit(hint_text, (weapons_panel_x + 5, weapons_panel_y + panel_height + 3))
