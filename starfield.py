import pygame
import random
import math  # Math-Modul hinzugefügt
from constants import *

class Star:
    def __init__(self):
        self.position = pygame.Vector2(
            random.randint(0, SCREEN_WIDTH),
            random.randint(0, SCREEN_HEIGHT)
        )
        self.size = random.choice(STAR_SIZES)
        self.color = random.choice(STAR_COLORS)
        self.twinkle_timer = random.random() * 2 * math.pi  # Zufällige Startphase

    def update(self, dt):
        self.twinkle_timer += dt
        # Helligkeit variiert mit Sinus für Glitzereffekt
        brightness = abs(math.sin(self.twinkle_timer))
        self.current_color = [int(c * brightness) for c in pygame.Color(self.color)]

    def draw(self, screen):
        pygame.draw.circle(screen, self.current_color, self.position, self.size)

class Starfield:
    def __init__(self):
        self.stars = [Star() for _ in range(STAR_COUNT)]

    def update(self, dt):
        for star in self.stars:
            star.update(dt)

    def draw(self, screen):
        for star in self.stars:
            star.draw(screen)