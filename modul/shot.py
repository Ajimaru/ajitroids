"""Projectile (Shot) implementation used by the player and enemies."""

import pygame
<<<<<<< HEAD
=======

>>>>>>> origin/main
import modul.constants as C
from modul.circleshape import CircleShape


class Shot(CircleShape):
<<<<<<< HEAD
    """Represents a projectile shot."""
=======
    """TODO: add docstring."""
>>>>>>> origin/main
    asteroids_group = None
    enemy_ships_group = None

    @classmethod
    def set_asteroids(cls, asteroids):
<<<<<<< HEAD
        """Set asteroids group for collision."""
=======
        """TODO: add docstring."""
>>>>>>> origin/main
        cls.asteroids_group = asteroids

    @classmethod
    def set_enemy_ships(cls, enemy_ships):
<<<<<<< HEAD
        """Set enemy ships group for collision."""
        cls.enemy_ships_group = enemy_ships

    def __init__(self, x, y, shot_type=C.WEAPON_STANDARD):
        """Initialize shot with position and type."""
=======
        """TODO: add docstring."""
        cls.enemy_ships_group = enemy_ships

    def __init__(self, x, y, shot_type=C.WEAPON_STANDARD):
        """TODO: add docstring."""
>>>>>>> origin/main
        super().__init__(x, y, 3)
        self.velocity = pygame.Vector2(0, 0)
        self.shot_type = shot_type
        self.lifetime = 2.0
        self.damage = 1
        self.target = None
        self.homing_power = 0

        if shot_type == C.WEAPON_LASER:
            self.radius = 2
            self.damage = 2
            self.penetrating = True

        elif shot_type == C.WEAPON_MISSILE:
            self.radius = 4
            self.damage = 3
            self.penetrating = False
            self.homing_power = 150
            self.target = None
            self.max_turn_rate = 2.0

        elif shot_type == C.WEAPON_SHOTGUN:
            self.radius = 2
            self.damage = 1
            self.penetrating = False
            self.lifetime = 0.5

        self.color = C.WEAPON_COLORS[shot_type]

    def update(self, dt):
<<<<<<< HEAD
        """Update shot position and lifetime."""
=======
        """TODO: add docstring."""
>>>>>>> origin/main
        if self.shot_type == C.WEAPON_MISSILE and self.homing_power > 0 and (Shot.asteroids_group or Shot.enemy_ships_group):
            self.seek_target(dt)

        self.position += self.velocity * dt

        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()

    def draw(self, screen):
<<<<<<< HEAD
        """Draw shot on screen."""
        if self.shot_type == C.WEAPON_LASER:
            # Guard against zero-length velocity before normalizing
            if self.velocity.length() > 0:
                direction = self.velocity.normalize()
            else:
                # fallback: point to the right if velocity is zero
                direction = pygame.Vector2(1, 0)
            end_pos = self.position + direction * 20
=======
        """TODO: add docstring."""
        if self.shot_type == C.WEAPON_LASER:
            end_pos = self.position + self.velocity.normalize() * 20
>>>>>>> origin/main
            pos_tuple = (int(self.position[0]), int(self.position[1]))
            end_pos_tuple = (int(end_pos[0]), int(end_pos[1]))
            pygame.draw.line(screen, self.color, pos_tuple, end_pos_tuple, 3)
        elif self.shot_type == C.WEAPON_MISSILE:
            pos_tuple = (int(self.position[0]), int(self.position[1]))
            pygame.draw.circle(screen, self.color, pos_tuple, self.radius)

            # Guard against zero-length velocity before normalizing
            if self.velocity.length() > 0:
                tail_dir = self.velocity.normalize()
            else:
                tail_dir = pygame.Vector2(0, 1)
            tail_end = self.position - tail_dir * 8
            tail_end_tuple = (int(tail_end[0]), int(tail_end[1]))
            pygame.draw.line(screen, (255, 128, 0), pos_tuple, tail_end_tuple, 2)
        else:
            pos_tuple = (int(self.position[0]), int(self.position[1]))
            pygame.draw.circle(screen, self.color, pos_tuple, self.radius)

    def seek_target(self, dt):
<<<<<<< HEAD
        """Seek nearest target for homing."""
=======
        """TODO: add docstring."""
>>>>>>> origin/main
        if not Shot.asteroids_group and not Shot.enemy_ships_group:
            return

        if not self.target or not self.target.alive():
            closest_dist = float("inf")
            self.target = None

            for group in [Shot.asteroids_group, Shot.enemy_ships_group]:
                if group:
                    for obj in list(group):
                        dist = (obj.position - self.position).length()
                        if dist < closest_dist:
                            closest_dist = dist
                            self.target = obj

        if self.target and self.target.alive():
            target_dir = (self.target.position - self.position).normalize()
            current_dir = self.velocity.normalize()
            turn_rate = min(self.max_turn_rate * dt, 1.0)
            new_dir = current_dir.lerp(target_dir, turn_rate).normalize()
            self.velocity = new_dir * self.velocity.length()
