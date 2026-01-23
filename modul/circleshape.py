"""Simple circle-shaped sprite helper."""

import pygame


class CircleShape(pygame.sprite.Sprite):
    """Base class for circular game objects."""
    def __init__(self, x, y, radius):
        """
        Initialize the sprite's circular geometry, kinematics, and group membership.
        
        Parameters:
            x (number): Initial x-coordinate of the sprite's position.
            y (number): Initial y-coordinate of the sprite's position.
            radius (number): Circle radius in pixels.
        
        Details:
            - Stores position as a pygame.Vector2(x, y).
            - Initializes velocity to a zero Vector2 and rotation to 0.
            - If the class has a `containers` attribute, adds this instance to that
              pygame.sprite group or iterable of groups.
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
        """
        Update the shape's state for the given time step. Intended to be overridden by subclasses to implement per-frame behavior.
        
        Parameters:
            dt (float): Time elapsed since the last update, in seconds.
        """

    def collides_with(self, other):
        """
        Determine whether this circle intersects another circle.
        
        Parameters:
            other (CircleShape): The other circle-shaped sprite to test collision against.
        
        Returns:
            bool: True if the distance between centers is less than or equal to the sum of radii (circles intersect or touch), False otherwise.
        """
        return self.position.distance_to(other.position) <= self.radius + other.radius

    def rotate(self, angle):
        """
        Rotate the shape by adding the given angle to its current rotation.
        
        Parameters:
            angle (float): Angle in degrees to add to the shape's rotation.
        """
        self.rotation += angle

    def forward(self):
        """
        Get the sprite's forward direction as a unit vector rotated by its rotation.
        
        Returns:
            pygame.Vector2: Unit vector pointing in the sprite's forward direction after applying `rotation` (degrees) to the base vector (0, -1).
        """
        return pygame.Vector2(0, -1).rotate(self.rotation)

    def draw(self, surface):
        """
        Placeholder drawing method; subclasses should draw the circle onto the given surface.
        
        Parameters:
            surface (pygame.Surface): Target surface to render the circle on. The base implementation performs no drawing and returns None.
        """
        return None