"""Particle effects used for explosions and visual feedback."""

import random
import pygame
import modul.constants as C


class Particle(pygame.sprite.Sprite):
    """Represents a visual particle for effects like explosions."""
    def __init__(self, x, y, color):
        """
        Create a particle at the given position with the specified color and an initial randomized velocity.
        
        Parameters:
            x (float): X coordinate in pixels for the particle's starting position.
            y (float): Y coordinate in pixels for the particle's starting position.
            color (str | tuple): Color name or RGB(A) tuple used to render the particle.
        
        Notes:
            The particle is initialized with an alpha of 255 and a lifetime of 0.5 seconds. Its velocity is set from a randomized speed and angle. If the class attribute `containers` is defined, the new particle is added to each group in that iterable.
        """
        super().__init__()
        self.position = pygame.Vector2(x, y)
        speed = random.uniform(50, 150)
        angle = random.uniform(0, 360)
        self.velocity = pygame.Vector2()
        self.velocity.from_polar((speed, angle))
        self.color = color
        self.alpha = 255
        self.lifetime = 0.5
        # Add to containers if set (for test group injection)
        containers = getattr(type(self), 'containers', ())
        if containers:
            for group in containers:
                group.add(self)

    def update(self, dt):
        """
        Advance the particle's state for the elapsed time step.
        
        Parameters:
            dt (float): Time step in seconds since the last update.
        
        Description:
            Moves the particle according to its velocity scaled by `dt`, decrements its remaining lifetime by `dt`, removes the particle when lifetime is zero or below, and updates its alpha to reflect remaining lifetime (0–255).
        """
        self.position += self.velocity * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
        self.alpha = max(0, int(255 * (self.lifetime)))

    def draw(self, screen):
        """
        Render the particle as a small filled circle at its current integer position.
        
        Parameters:
            screen (pygame.Surface): Destination surface to draw the particle onto; the particle is drawn using its color at radius 2.
        """
        pos = (int(self.position.x), int(self.position.y))
        pygame.draw.circle(screen, self.color, pos, 2)

    @classmethod
    def create_ship_explosion(cls, x, y):
        """
        Create a burst of ship-explosion particles at the given position.
        
        Creates C.EXPLOSION_PARTICLES particles centered at (x, y). Each particle is white, given a random direction (0–360 degrees) and speed between 100 and 200 units, and has its lifetime set to 0.5 seconds.
        
        Parameters:
            x (float): X coordinate of the explosion center.
            y (float): Y coordinate of the explosion center.
        """
        for _ in range(C.EXPLOSION_PARTICLES):
            angle = random.uniform(0, 360)
            speed = random.uniform(100, 200)
            particle = cls(x, y, "white")
            particle.velocity.from_polar((speed, angle))
            particle.lifetime = 0.5

    @classmethod
    def create_asteroid_explosion(cls, x, y):
        """
        Spawn multiple particles at the given position to simulate an asteroid explosion.
        
        Each created particle is assigned a random color from C.PARTICLE_COLORS, a random speed between 50 and 150, and a random direction between 0 and 360 degrees; the particle's velocity is set from those polar coordinates.
        
        Parameters:
            x (int | float): X coordinate of the explosion center.
            y (int | float): Y coordinate of the explosion center.
        """
        for _ in range(C.EXPLOSION_PARTICLES):
            color = random.choice(C.PARTICLE_COLORS)
            particle = cls(x, y, color)
            speed = random.uniform(50, 150)
            angle = random.uniform(0, 360)
            particle.velocity.from_polar((speed, angle))