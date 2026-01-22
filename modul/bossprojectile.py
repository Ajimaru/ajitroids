"""Projectile class used by Boss entities."""

import math
<<<<<<< HEAD
import pygame
=======

import pygame

>>>>>>> origin/main
import modul.constants as C
from modul.circleshape import CircleShape


class BossProjectile(CircleShape):
<<<<<<< HEAD
    """Projectile fired by boss enemies."""
    def __init__(self, x, y, velocity, projectile_type="normal"):
        """Initialize boss projectile with position, velocity, and type."""
=======
    """TODO: add docstring."""
    def __init__(self, x, y, velocity, projectile_type="normal"):
        """TODO: add docstring."""
>>>>>>> origin/main
        super().__init__(x, y, C.BOSS_PROJECTILE_RADIUS)
        self.position = pygame.Vector2(x, y)
        self.velocity = velocity
        self.type = projectile_type
        self.lifetime = 5.0
        self.damage = 1
        self.color = C.BOSS_PROJECTILE_COLORS.get(self.type, C.BOSS_COLOR)
        self.rotation = 0
        self.rotation_speed = 180

    def update(self, dt):
<<<<<<< HEAD
        """Update projectile position, rotation, and lifetime."""
=======
        """TODO: add docstring."""
>>>>>>> origin/main
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
<<<<<<< HEAD
        """Draw the projectile based on its type."""
=======
        """TODO: add docstring."""
>>>>>>> origin/main
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
