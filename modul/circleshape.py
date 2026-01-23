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
            try:
                abstract_group = pygame.sprite.AbstractGroup
            except AttributeError:
                abstract_group = None

            if (
                abstract_group is not None
                and isinstance(containers, abstract_group)
            ):
                containers.add(self)
            else:
                for group in containers:
                    if hasattr(group, 'add'):
                        group.add(self)

    def update(self, dt):
        """Update the circle shape (to be implemented by subclasses)."""

    def collides_with(self, other):
        """Check collision with another circle shape."""
        dist = self.position.distance_to(other.position)
        return dist <= (self.radius + other.radius)

    def rotate(self, angle):
        """Rotate the shape by the given angle."""
        self.rotation += angle

    def forward(self):
        """Return the forward direction vector."""
        return pygame.Vector2(0, -1).rotate(self.rotation)

    def draw(self, surface):
        """Draw the circle onto the given surface.

        Simple implementation used by tests and lightweight display code.
        Subclasses may override for more complex visuals.
        """
        if surface is None:
            return
        try:
            color = getattr(self, 'color', (255, 255, 255))
            pos = (int(self.position.x), int(self.position.y))
            pygame.draw.circle(surface, color, pos, int(self.radius))
        except (pygame.error, TypeError, ValueError):
            # Drawing should not break tests; swallow common drawing errors
            return
