"""Environmental hazards: screen-local dangers that pressure the player.

Hazards follow the CircleShape convention (position/velocity/radius, update,
draw, collides_with) and register themselves through the class-level
`containers` attribute, exactly like asteroids, shots and power-ups.

A hazard must never remove the core asteroid loop: it is an accent that adds
pressure for a limited time, not a replacement for asteroids. That is why every
hazard has a lifetime and a cap (see the *_MAX_COUNT constants).
"""

import pygame

from modul import constants as C
from modul.circleshape import CircleShape


class Hazard(CircleShape):
    """Base class for hazards: a CircleShape that expires after a lifetime."""

    def __init__(self, x, y, radius, lifetime):
        """Initialize the hazard and start its countdown."""
        super().__init__(x, y, radius)
        self.lifetime = lifetime

    def update(self, dt):
        """Age the hazard and kill it once the lifetime is spent."""
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()

    def draw(self, surface):
        """Draw the hazard with its collision outline when debugging."""
        super().draw(surface)
        self.draw_collision_debug(surface)


class BlackHole(Hazard):
    """Gravity well that pulls nearby objects toward its core."""

    debug_color = C.BLACK_HOLE_RING_COLOR

    def __init__(self, x, y, radius=None, lifetime=None):
        """Initialize a black hole with position and optional overrides."""
        radius = radius if radius is not None else C.BLACK_HOLE_RADIUS
        lifetime = lifetime if lifetime is not None else C.BLACK_HOLE_LIFETIME
        super().__init__(x, y, radius, lifetime)
        self.color = C.BLACK_HOLE_RING_COLOR

    def gravity_vector(self, position):
        """Return the acceleration this hole applies at `position`.

        The pull is strongest at the core and falls off linearly to zero at
        BLACK_HOLE_PULL_RADIUS; beyond that distance the hole has no effect.
        """
        delta = self.position - position
        distance = delta.length()
        if distance <= 0 or distance > C.BLACK_HOLE_PULL_RADIUS:
            return pygame.Vector2(0, 0)
        strength = C.BLACK_HOLE_GRAVITY_STRENGTH * (1.0 - distance / C.BLACK_HOLE_PULL_RADIUS)
        return delta.normalize() * strength

    def apply_forces(self, objects, dt):
        """Accelerate each object toward the core, scaled by frame time."""
        for obj in objects:
            if obj is self or not hasattr(obj, "velocity"):
                continue
            obj.velocity += self.gravity_vector(obj.position) * dt

    def draw(self, surface):
        """Draw the hole: a bright ring around a dark core."""
        if surface is None:
            return
        try:
            pos = (int(self.position.x), int(self.position.y))
            pygame.draw.circle(surface, self.color, pos, int(self.radius), 2)
            pygame.draw.circle(surface, C.BLACK_HOLE_CORE_COLOR, pos, int(self.radius * 0.7))
        except (pygame.error, TypeError, ValueError):
            return
        self.draw_collision_debug(surface)


class SolarFlare(Hazard):
    """Horizontal flare band that sweeps down the arena after a warning."""

    debug_color = C.SOLAR_FLARE_COLOR

    def __init__(self, thickness=None, speed=None, warning=None):
        """Initialize a flare band at the top edge, held during its warning."""
        thickness = thickness if thickness is not None else C.SOLAR_FLARE_THICKNESS
        speed = speed if speed is not None else C.SOLAR_FLARE_SPEED
        warning = warning if warning is not None else C.SOLAR_FLARE_WARNING
        # The band starts fully visible at the top of the screen so the warning
        # flash is telegraphed before it begins to move.
        super().__init__(C.SCREEN_WIDTH / 2, thickness / 2, thickness / 2, 0.0)
        self.thickness = thickness
        self.speed = speed
        self.warning_remaining = warning
        self.color = C.SOLAR_FLARE_COLOR

    @property
    def half_thickness(self):
        """Half the band height, used for collision and drawing."""
        return self.thickness / 2

    def update(self, dt):
        """Hold during the warning, then sweep down and despawn off-screen."""
        if self.warning_remaining > 0:
            self.warning_remaining -= dt
            return
        self.position.y += self.speed * dt
        if self.position.y - self.half_thickness > C.SCREEN_HEIGHT:
            self.kill()

    def collides_with(self, other):
        """A screen-wide band: contact depends only on vertical overlap."""
        if self.warning_remaining > 0:
            return False
        return abs(other.position.y - self.position.y) <= self.half_thickness + other.radius

    def draw(self, surface):
        """Draw the full-width flare band, flashing during the warning."""
        if surface is None:
            return
        try:
            color = self.color
            if self.warning_remaining > 0 and int(self.warning_remaining * 8) % 2 == 0:
                color = C.SOLAR_FLARE_WARNING_COLOR
            rect = pygame.Rect(
                0,
                int(self.position.y - self.half_thickness),
                C.SCREEN_WIDTH,
                int(self.thickness),
            )
            pygame.draw.rect(surface, color, rect)
        except (pygame.error, TypeError, ValueError):
            return
        self.draw_collision_debug(surface)
