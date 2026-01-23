"""Projectile class used by Boss entities."""

import math
import pygame
import modul.constants as C
from modul.circleshape import CircleShape


class BossProjectile(CircleShape):
    """Projectile fired by boss enemies."""
    def __init__(self, x, y, velocity, projectile_type="normal"):
        """
        Create a boss projectile at the given position with the specified velocity and type.
        
        Parameters:
            x (float): Horizontal position of the projectile.
            y (float): Vertical position of the projectile.
            velocity (tuple | Vector2): Movement vector applied each second.
            projectile_type (str): Visual/behavior type of the projectile (e.g., "normal", "homing", "explosive").
        
        Initializes the following public attributes:
            lifetime (float): Time in seconds before the projectile is automatically removed (default 5.0).
            damage (int): Damage dealt on impact (default 1).
            color (tuple): Draw color selected from configuration based on `projectile_type`.
            rotation (float): Current rotation angle in degrees (initially 0).
            rotation_speed (float): Rotation speed in degrees per second (default 180).
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
        Update the projectile's position, rotation, and remaining lifetime; deactivate the projectile when expired or off-screen.
        
        This advances the projectile by its velocity scaled by dt, increments rotation by rotation_speed scaled by dt, and subtracts dt from lifetime. If lifetime becomes less than or equal to zero, or the projectile's position moves outside the screen bounds with a 20-pixel margin, the projectile is killed (deactivated).
        
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
        Render this projectile onto the given surface according to its `type`.
        
        - "normal": filled circle using the projectile color with a smaller white ring near the center.
        - "homing": four-point rotated shape (square-like) sized to the projectile radius and rotated by `self.rotation`.
        - "explosive": filled circle using the projectile color with two concentric white rings.
        
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