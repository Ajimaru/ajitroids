import pygame
import random
from constants import *

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()
        self.position = pygame.Vector2(x, y)
        speed = random.uniform(50, 150)
        angle = random.uniform(0, 360)
        self.velocity = pygame.Vector2()
        self.velocity.from_polar((speed, angle))
        self.color = color
        self.alpha = 255
        self.lifetime = 0.5

    def update(self, dt):
        self.position += self.velocity * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
        self.alpha = max(0, int(255 * (self.lifetime)))

    def draw(self, screen):
        pos = (int(self.position.x), int(self.position.y))
        pygame.draw.circle(screen, self.color, pos, 2)

    @classmethod
    def create_ship_explosion(cls, x, y):
        for _ in range(EXPLOSION_PARTICLES):
            angle = random.uniform(0, 360)
            speed = random.uniform(100, 200)
            particle = cls(x, y, "white")
            particle.velocity.from_polar((speed, angle))
            particle.lifetime = 0.5

    @classmethod
    def create_asteroid_explosion(cls, x, y):
        for _ in range(EXPLOSION_PARTICLES):
            color = random.choice(PARTICLE_COLORS)
            particle = cls(x, y, color)
            speed = random.uniform(50, 150)
            angle = random.uniform(0, 360)
            particle.velocity.from_polar((speed, angle))