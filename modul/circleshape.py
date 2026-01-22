"""Simple circle-shaped sprite helper."""

import pygame


class CircleShape(pygame.sprite.Sprite):
    """TODO: add docstring."""
    def __init__(self, x, y, radius):
        """TODO: add docstring."""
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius
        self.rotation = 0

    def draw(self, screen):
        """TODO: add docstring."""

    def update(self, dt):
        """TODO: add docstring."""

    def collides_with(self, other):
        """TODO: add docstring."""
        return self.position.distance_to(other.position) <= self.radius + other.radius

    def rotate(self, angle):
        """TODO: add docstring."""
        self.rotation += angle

    def forward(self):
        """TODO: add docstring."""
        return pygame.Vector2(0, -1).rotate(self.rotation)
