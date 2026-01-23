"""Projectile (Shot) implementation used by the player and enemies."""

import pygame
import modul.constants as C
from modul.circleshape import CircleShape


class Shot(CircleShape):
    """Represents a projectile shot."""
    asteroids_group = None
    enemy_ships_group = None

    @classmethod
    def set_asteroids(cls, asteroids):
        """Set asteroids group for collision."""
        cls.asteroids_group = asteroids

    @classmethod
    def set_enemy_ships(cls, enemy_ships):
        """
        Configure the class-level group of enemy ships used for collision and homing.
        
        Parameters:
            enemy_ships: A collection or group object containing enemy ship instances to be used for collision checks and target acquisition by Shot instances.
        """
        cls.enemy_ships_group = enemy_ships

    def __init__(self, x, y, shot_type=C.WEAPON_STANDARD):
        """
        Create a Shot at the given position configured for the specified weapon type.
        
        Initializes public instance attributes used by the shot's lifecycle and behavior including:
        - velocity: 2D velocity vector (pygame.Vector2).
        - shot_type: weapon type constant.
        - lifetime: seconds before the shot expires.
        - damage: damage dealt on impact.
        - target: current homing target (or None).
        - homing_power: homing strength (nonzero for missiles).
        - radius, penetrating, and max_turn_rate as applicable per weapon type.
        - color: rendering color selected from weapon palette.
        
        Parameters:
            x (float): Initial x-coordinate of the shot.
            y (float): Initial y-coordinate of the shot.
            shot_type (int): Weapon type constant that selects per-type properties (e.g., laser, missile, shotgun).
        """
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
        """
        Advance the shot's state: optionally seek a target, move by velocity, and decrease lifetime.
        
        If the shot is a missile with homing enabled and collision groups are available, this will attempt to acquire/adjust toward a target before moving. Then the shot's position is advanced by velocity * dt. The shot's lifetime is reduced by dt and the shot is removed when lifetime is less than or equal to zero.
        
        Parameters:
            dt (float): Time step in seconds to advance the shot.
        """
        if self.shot_type == C.WEAPON_MISSILE and self.homing_power > 0 and (Shot.asteroids_group or Shot.enemy_ships_group):
            self.seek_target(dt)

        self.position += self.velocity * dt

        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()

    def draw(self, screen):
        """
        Render the shot to the given Pygame surface according to its weapon type.
        
        For lasers this draws a short line in the shot's direction (falls back to right when velocity is zero). For missiles this draws a circle and an orange tail behind the missile (falls back to downward tail when velocity is zero). For other shot types this draws a filled circle at the shot position.
        
        Parameters:
            screen (pygame.Surface): Surface to draw the shot onto.
        """
        if self.shot_type == C.WEAPON_LASER:
            # Guard against zero-length velocity before normalizing
            if self.velocity.length() > 0:
                direction = self.velocity.normalize()
            else:
                # fallback: point to the right if velocity is zero
                direction = pygame.Vector2(1, 0)
            end_pos = self.position + direction * 20
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
        """
        Acquire the nearest alive target from asteroid and enemy ship groups and steer the shot toward it.
        
        If neither collision group exists the method does nothing. If there is no current valid target, it selects the closest alive object from Shot.asteroids_group and Shot.enemy_ships_group and assigns it to `self.target`. If `self.target` is alive, adjusts `self.velocity` by rotating its direction toward the target by at most `self.max_turn_rate * dt`, preserving the current speed.
        
        Parameters:
            dt (float): Time step in seconds used to scale the maximum turn applied this update.
        """
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