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
        """
        Configure the class-level asteroid target group used for homing and collision checks.
        
        Parameters:
            asteroids: A container (e.g., sprite group or iterable) of asteroid objects that Shot instances will consider when acquiring targets.
        """
        cls.asteroids_group = asteroids

    @classmethod
    def set_enemy_ships(cls, enemy_ships):
        """
        Configure the class-level group of enemy ships used as potential homing targets.
        
        Parameters:
            enemy_ships (iterable): A collection (e.g., a sprite Group or list) of enemy ship objects that will be used by Shot instances for target acquisition.
        """
        cls.enemy_ships_group = enemy_ships

    def __init__(self, x, y, shot_type=C.WEAPON_STANDARD):
        """
        Create a Shot positioned at (x, y) configured for the given weapon type.
        
        Parameters:
            x (number): X coordinate of the shot's initial position.
            y (number): Y coordinate of the shot's initial position.
            shot_type (int): Weapon type constant that selects size, damage, lifetime,
                penetration, and homing behavior (defaults to C.WEAPON_STANDARD).
        
        Description:
            Initializes common shot attributes (velocity, lifetime, damage, target,
            homing_power, color) and adjusts properties according to `shot_type`:
              - WEAPON_LASER: smaller radius, increased damage, penetrating.
              - WEAPON_MISSILE: larger radius, higher damage, non-penetrating,
                enables homing (sets `homing_power` and `max_turn_rate`) and uses
                `target` for seeking.
              - WEAPON_SHOTGUN: small radius, standard damage, non-penetrating,
                shorter lifetime.
        
        Attributes set:
            velocity (pygame.Vector2), radius (int), lifetime (float), damage (int),
            penetrating (bool, if applicable), target (object or None),
            homing_power (int), max_turn_rate (float, for missiles), color (tuple).
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
        Advance the shot's state by the given time step.
        
        If this shot is a homing missile with homing power and target groups set, attempt to seek a target. Then move the shot by its velocity scaled by dt, decrement its lifetime, and destroy the shot when lifetime is less than or equal to zero.
        
        Parameters:
            dt (float): Time step in seconds used to advance movement and lifetime.
        """
        if self.shot_type == C.WEAPON_MISSILE and self.homing_power > 0 and (Shot.asteroids_group or Shot.enemy_ships_group):
            self.seek_target(dt)

        self.position += self.velocity * dt

        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()

    def draw(self, screen):
        """
        Render the shot on the given surface using appearance determined by the shot type.
        
        Parameters:
            screen (pygame.Surface): Surface to draw the shot onto.
        
        Description:
            - Laser: draws a short line in the shot color along the velocity direction; if velocity is zero, defaults direction to the right.
            - Missile: draws a filled circle at the shot position and a short tail opposite the velocity; if velocity is zero, uses a downward tail direction.
            - Other shot types: draws a filled circle at the shot position.
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
        Selects a nearest live target from configured target groups and steers the shot toward it.
        
        If the shot has no current live target, searches Shot.asteroids_group and Shot.enemy_ships_group for the closest living object and sets it as self.target. If a live target is present, adjusts self.velocity to turn toward the target by interpolating between the current direction and the direction to the target; the interpolation fraction is capped by self.max_turn_rate * dt (maximum 1.0), preserving the shot's speed. If no target groups are configured or no live targets exist, the method does nothing.
        
        Parameters:
            dt (float): Time step (in seconds) used to scale the maximum turning amount.
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