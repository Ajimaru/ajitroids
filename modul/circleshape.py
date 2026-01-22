"""Simple circle-shaped sprite helper."""

import pygame


class CircleShape(pygame.sprite.Sprite):
    """Base class for circular game objects."""
    def __init__(self, x, y, radius):
        """Initialize a circular sprite with position and radius."""
        super().__init__()
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius
        self.rotation = 0
        # Add to containers if set (for test group injection)
        containers = getattr(type(self), 'containers', ())
        if containers:
        containers = getattr(type(self), 'containers', ())
        if containers:
            if isinstance(containers, pygame.sprite.AbstractGroup):
                containers.add(self)
            else:
                for group in containers:
                    group.add(self)
        """Draw the circle shape (to be implemented by subclasses)."""

    def update(self, dt):
        """Update the circle shape (to be implemented by subclasses)."""

    def collides_with(self, other):
        """Check collision with another circle shape."""
        return self.position.distance_to(other.position) <= self.radius + other.radius

    def rotate(self, angle):
        """Rotate the shape by the given angle."""
        self.rotation += angle

    def forward(self):
        """Return the forward direction vector."""
        return pygame.Vector2(0, -1).rotate(self.rotation)
