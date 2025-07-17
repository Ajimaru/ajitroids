import pygame
import random
from asteroid import Asteroid
from constants import *


class AsteroidField:
    edges = [
        [
            pygame.Vector2(1, 0),
            lambda y: pygame.Vector2(-ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT),
        ],
        [
            pygame.Vector2(-1, 0),
            lambda y: pygame.Vector2(
                SCREEN_WIDTH + ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT
            ),
        ],
        [
            pygame.Vector2(0, 1),
            lambda x: pygame.Vector2(x * SCREEN_WIDTH, -ASTEROID_MAX_RADIUS),
        ],
        [
            pygame.Vector2(0, -1),
            lambda x: pygame.Vector2(
                x * SCREEN_WIDTH, SCREEN_HEIGHT + ASTEROID_MAX_RADIUS
            ),
        ],
    ]

    def __init__(self):
        self.spawn_timer = 0
        self.asteroid_count = 5  # Standardwert
        self.spawn_interval = 5.0  # Sekunden

    def spawn(self, radius, position, velocity):
        asteroid = Asteroid(position.x, position.y, radius)
        asteroid.velocity = velocity

    def update(self, dt):
        """Aktualisiert das Asteroidenfeld und spawnt neue Asteroiden nach Bedarf"""
        self.spawn_timer += dt

        # Wenn der Timer abgelaufen ist und weniger Asteroiden als vorgegeben vorhanden sind
        if self.spawn_timer >= self.spawn_interval:
            from asteroid import Asteroid  # Vermeidet Zirkelimport
            asteroid_count = len([obj for obj in Asteroid.containers[0]])

            # Nur spawnen wenn weniger als die vorgegebene Anzahl
            if asteroid_count < self.asteroid_count:
                self.spawn_random()
                print(f"Neuer Asteroid gespawnt. Aktuelle Anzahl: {asteroid_count + 1}/{self.asteroid_count}")

            # Timer zurücksetzen, unabhängig davon, ob ein Asteroid gespawnt wurde
            self.spawn_timer = 0

    def spawn_random(self):
        """Spawnt einen zufälligen Asteroiden am Rand des Bildschirms"""
        # Zufällige Seite wählen (0-3: links, rechts, oben, unten)
        edge_index = random.randint(0, 3)

        # Zufällige Position entlang der gewählten Kante
        rand_pos = random.random()

        # Velocity-Richtung (von der Kante weg)
        direction = self.edges[edge_index][0]

        # Position berechnen (entlang der Kante)
        position = self.edges[edge_index][1](rand_pos)

        # Geschwindigkeit berechnen (von der Kante weg mit zufälliger Variation)
        velocity = direction.rotate(random.uniform(-45, 45)) * random.uniform(30, 70)

        # Großen Asteroiden erstellen
        self.spawn(ASTEROID_MAX_RADIUS, position, velocity)
        print(f"Asteroid gespawnt bei {position} mit Geschwindigkeit {velocity}")