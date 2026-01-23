"""Particle effects used for explosions and visual feedback."""

import random
import pygame
import modul.constants as C


class Particle(pygame.sprite.Sprite):
    """Represents a visual particle for effects like explosions."""
    def __init__(self, x, y, color):
        """
        Create a particle at the given position with a randomized outward velocity, color, and a short fading lifetime.
        
        Parameters:
            x (float): X coordinate of the initial particle position.
            y (float): Y coordinate of the initial particle position.
            color (tuple|str): Color used when rendering the particle.
        
        Details:
            - Velocity direction is chosen uniformly; speed is randomized (approximately 50–150 units).
            - Lifetime is initialized to 0.5 seconds and alpha starts at 255; the particle is expected to fade as lifetime decreases.
            - If the class defines a `containers` attribute (an iterable of Sprite groups), the instance is added to those groups on creation for test-friendly injection.
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
        Advance the particle's state by a timestep: move by velocity, decrease lifetime, fade alpha, and remove when expired.
        
        Parameters:
            dt (float): Time step in seconds since the last update.
        
        Notes:
            If lifetime becomes less than or equal to zero, the particle is removed via self.kill().
        """
        self.position += self.velocity * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
        self.alpha = max(0, int(255 * (self.lifetime)))

    def draw(self, screen):
        """
        Render the particle as a small filled circle at its current position.
        
        Parameters:
            screen (pygame.Surface): Destination surface to draw the particle on.
        
        Detailed behavior:
            The particle's position is converted to integer pixel coordinates before drawing.
            The circle is filled, uses the particle's `color`, and has a fixed radius of 2 pixels.
        """
        pos = (int(self.position.x), int(self.position.y))
        pygame.draw.circle(screen, self.color, pos, 2)

    @classmethod
    def create_ship_explosion(cls, x, y):
        """
        Create a burst of particles representing a ship explosion at the given position.
        
        Creates C.EXPLOSION_PARTICLES particles centered at (x, y). Each particle is white, given a random direction (0–360°) and speed (100–200), assigned a velocity from those polar coordinates, and a lifetime of 0.5 seconds. If the class defines a `containers` attribute, each new particle is added to those sprite groups.
         
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
        Create multiple colored particles at the given position to simulate an asteroid explosion.
        
        Each particle is instantiated from the class and given a random color and a randomized velocity and lifetime; particles are automatically added to any sprite groups defined on the class (via a `containers` attribute), if present.
        
        Parameters:
            cls: The particle class to instantiate.
            x (int | float): X coordinate of the explosion center.
            y (int | float): Y coordinate of the explosion center.
        """
        for _ in range(C.EXPLOSION_PARTICLES):
            color = random.choice(C.PARTICLE_COLORS)
            particle = cls(x, y, color)
            speed = random.uniform(50, 150)
            angle = random.uniform(0, 360)
            particle.velocity.from_polar((speed, angle))