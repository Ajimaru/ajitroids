"""Simple circle-shaped sprite helper."""

import pygame


class CircleShape(pygame.sprite.Sprite):
    """Base class for circular game objects."""
    def __init__(self, x, y, radius):
        """
        Create a circular sprite positioned at (x, y) with the given radius.
        
        Parameters:
        	x (int | float): Horizontal coordinate of the sprite's center.
        	y (int | float): Vertical coordinate of the sprite's center.
        	radius (int | float): Radius of the circle in pixels.
        
        Notes:
        	If the class attribute `containers` is set to a pygame.sprite.Group or an iterable of groups,
        	the instance is automatically added to those group(s) during initialization.
        """
        super().__init__()
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius
        self.rotation = 0
        # Add to containers if set (for test group injection)
        containers = getattr(type(self), 'containers', ())
        if containers:
            if isinstance(containers, pygame.sprite.AbstractGroup):
                containers.add(self)
            else:
                for group in containers:
                    group.add(self)

    def update(self, dt):
        """Update the circle shape (to be implemented by subclasses)."""

    def collides_with(self, other):
        """
        Determine whether this circle intersects another circle.
        
        Parameters:
            other (CircleShape or pygame.sprite.Sprite): Object with `position` (pygame.Vector2) and `radius` attributes representing the other circle.
        
        Returns:
            bool: True if the distance between centers is less than or equal to the sum of radii, False otherwise.
        """
        return self.position.distance_to(other.position) <= self.radius + other.radius

    def rotate(self, angle):
        """
        Adjust the shape's rotation by the given angle.
        
        Parameters:
            angle (float): Amount to add to the current rotation value.
        """
        self.rotation += angle

    def forward(self):
        """
        Get the unit forward direction vector for the sprite's current rotation.
        
        Returns:
            direction (pygame.Vector2): Unit vector initially pointing up (0, -1) rotated by self.rotation degrees to represent the sprite's forward direction.
        """
        return pygame.Vector2(0, -1).rotate(self.rotation)

    def draw(self, surface):
        """
        Render the shape onto the given surface and, on first invocation, register this instance with any class-level `containers`.
        
        The base implementation performs no drawing; subclasses should override to provide visual rendering. If the class defines a `containers` attribute that is a pygame.sprite.AbstractGroup or an iterable of groups, the instance will be added to those groups the first time `draw` is called.
        Parameters:
            surface (pygame.Surface): Destination surface to draw onto.
        """
        return None