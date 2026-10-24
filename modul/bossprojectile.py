"""Projectile class used by Boss entities."""

import math
import pygame
import modul.constants as C
from modul.circleshape import CircleShape


class BossProjectile(CircleShape):
    """Projectile fired by boss enemies."""

    debug_color = (255, 0, 255)

    @classmethod
    def spawn(cls, x, y, velocity, projectile_type="normal"):
        """Create a projectile, retiring the oldest ones past the live cap.

        Boss attacks fire faster than projectiles leave the arena, so the waves
        overlap. Without a ceiling the screen fills with bullets the player
        cannot dodge.
        """
        containers = getattr(cls, "containers", ())
        if isinstance(containers, pygame.sprite.AbstractGroup):
            group = containers
        else:
            group = containers[0] if containers else ()

        live = [obj for obj in group if isinstance(obj, cls)]
        for stale in live[: max(0, len(live) + 1 - C.BOSS_PROJECTILE_MAX_ALIVE)]:
            stale.kill()

        return cls(x, y, velocity, projectile_type)

    def __init__(self, x, y, velocity, projectile_type="normal"):
        """Initialize boss projectile with position, velocity, and type."""
        super().__init__(x, y, C.BOSS_PROJECTILE_RADIUS)
        self.velocity = velocity
        self.type = projectile_type
        self.lifetime = C.BOSS_PROJECTILE_LIFETIME
        self.damage = 1
        self.color = C.BOSS_PROJECTILE_COLORS.get(self.type, C.BOSS_COLOR)
        self.rotation = 0
        self.rotation_speed = 180

    def update(self, dt):
        """Update projectile position, rotation, and lifetime."""
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
        """Draw the projectile based on its type."""
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
        self.draw_collision_debug(screen)
