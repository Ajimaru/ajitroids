"""Projectile class used by Boss entities."""

import math
import pygame
import modul.constants as C
from modul.circleshape import CircleShape


class BossProjectile(CircleShape):
    """Projectile fired by boss enemies."""
    def __init__(self, x, y, velocity, projectile_type="normal"):
        """
        Create a boss-fired projectile at (x, y) with a given velocity and visual/behavior type.
        
        Parameters:
            x (float): Initial horizontal position of the projectile.
            y (float): Initial vertical position of the projectile.
            velocity (pygame.math.Vector2 | tuple): Initial velocity vector in pixels per second.
            projectile_type (str): Visual/behavior type; commonly "normal", "homing", or "explosive". Defaults to "normal".
        
        Initial state:
            - lifetime is set to 5.0 seconds.
            - damage is set to 1.
            - color is selected from C.BOSS_PROJECTILE_COLORS by type, falling back to C.BOSS_COLOR.
            - rotation is set to 0 degrees and rotation_speed to 180 degrees/second.
        """
        super().__init__(x, y, C.BOSS_PROJECTILE_RADIUS)
        self.velocity = velocity
        self.type = projectile_type
        self.lifetime = 5.0
        self.damage = 1
        self.color = C.BOSS_PROJECTILE_COLORS.get(self.type, C.BOSS_COLOR)
        self.rotation = 0
        self.rotation_speed = 180

    def update(self, dt):
        """
        Advance the projectile's state for the given time step.
        
        Updates position and rotation, decrements remaining lifetime, and terminates the projectile when its lifetime reaches zero or when it moves outside the screen bounds (20 px margin).
        
        Parameters:
            dt (float): Time step in seconds.
        """
        self.position += self.velocity * dt
        self.rotation += self.rotation_speed * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
        if (
            self.position.x < -20
            or self.position.x > C.SCREEN_WIDTH + 20
            or self.position.y < -20
            or self.position.y > C.SCREEN_HEIGHT + 20
        ):
            self.kill()

    def draw(self, screen):
        """
        Render the projectile onto the provided pygame surface.
        
        Renders visual representation according to the projectile's `type`:
        - "normal": filled circle in `self.color` with an inner stroked white ring.
        - "homing": rotated four-point polygon (diamond-like) using `self.rotation` and `self.radius`.
        - "explosive": filled circle in `self.color` with two concentric stroked white rings.
        
        Parameters:
            screen (pygame.Surface): Surface to draw the projectile on.
        """
        if self.type == "normal":
            pygame.draw.circle(screen, self.color, self.position, self.radius)
            pygame.draw.circle(screen, (255, 255, 255), self.position, self.radius * 0.7, 1)
        elif self.type == "homing":
            points = []
            for i in range(4):
                angle = math.radians(self.rotation + i * 90)
                points.append(
                    (self.position.x + math.cos(angle) * self.radius, self.position.y + math.sin(angle) * self.radius)
                )
            pygame.draw.polygon(screen, self.color, points)
        elif self.type == "explosive":
            pygame.draw.circle(screen, self.color, self.position, self.radius)
            pygame.draw.circle(screen, (255, 255, 255), self.position, self.radius * 0.7, 1)
            pygame.draw.circle(screen, (255, 255, 255), self.position, self.radius * 0.4, 1)