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
        # Zufällige Geschwindigkeit und Richtung
        speed = random.uniform(50, 150)
        angle = random.uniform(0, 360)
        self.velocity = pygame.Vector2()
        self.velocity.from_polar((speed, angle))
        
        self.lifetime = 1.0  # 1 Sekunde Lebenszeit
        self.color = color
        self.alpha = 255  # Volle Sichtbarkeit zu Beginn

    def update(self, dt):
        self.position += self.velocity * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
        # Verblassen über Zeit
        self.alpha = max(0, int(255 * (self.lifetime)))

    def draw(self, screen):
        # Position für das Zeichnen
        pos = (int(self.position.x), int(self.position.y))
        # Zeichne einen kleinen Kreis
        pygame.draw.circle(screen, self.color, pos, 2)

    @classmethod
    def create_ship_explosion(cls, x, y):
        # Dreieckige Form simulieren mit weißen Partikeln
        for _ in range(EXPLOSION_PARTICLES):
            angle = random.uniform(0, 360)
            speed = random.uniform(100, 200)  # Schnellere Partikel
            particle = cls(x, y, "white")  # Nur weiße Partikel für das Schiff
            particle.velocity.from_polar((speed, angle))
            particle.lifetime = 0.5  # Kürzere Lebensdauer

    @classmethod
    def create_asteroid_explosion(cls, x, y):
        # Farbige Explosion für Asteroiden
        for _ in range(EXPLOSION_PARTICLES):
            color = random.choice(PARTICLE_COLORS)
            particle = cls(x, y, color)
            speed = random.uniform(50, 150)
            angle = random.uniform(0, 360)
            particle.velocity.from_polar((speed, angle))
            particle.lifetime = 1.0  # Längere Lebensdauer