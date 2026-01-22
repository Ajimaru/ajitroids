"""AsteroidField generation and management."""

import random

import pygame

import modul.constants as C
from modul.asteroid import Asteroid


class AsteroidField:
    """TODO: add docstring."""
    edges = [
        [
            pygame.Vector2(1, 0),
            lambda y: pygame.Vector2(-C.ASTEROID_MAX_RADIUS, y * C.SCREEN_HEIGHT),
        ],
        [
            pygame.Vector2(-1, 0),
            lambda y: pygame.Vector2(C.SCREEN_WIDTH + C.ASTEROID_MAX_RADIUS, y * C.SCREEN_HEIGHT),
        ],
        [
            pygame.Vector2(0, 1),
            lambda x: pygame.Vector2(x * C.SCREEN_WIDTH, -C.ASTEROID_MAX_RADIUS),
        ],
        [
            pygame.Vector2(0, -1),
            lambda x: pygame.Vector2(x * C.SCREEN_WIDTH, C.SCREEN_HEIGHT + C.ASTEROID_MAX_RADIUS),
        ],
    ]

    def __init__(self):
        """TODO: add docstring."""
        self.spawn_timer = 0
        self.asteroid_count = 5
        self.spawn_interval = 5.0

    def spawn(self, radius, position, velocity):
        # Randomly select asteroid type based on weights
        """TODO: add docstring."""
        asteroid_type = random.choices(
            list(C.ASTEROID_TYPE_WEIGHTS.keys()),
            weights=list(C.ASTEROID_TYPE_WEIGHTS.values())
        )[0]

        asteroid = Asteroid(position.x, position.y, radius, asteroid_type)
        asteroid.velocity = velocity

    def update(self, dt):
        """TODO: add docstring."""
        self.spawn_timer += dt

        if self.spawn_timer >= self.spawn_interval:
            from modul.asteroid import Asteroid

            asteroid_count = len([obj for obj in Asteroid.containers[0]])

            if asteroid_count < self.asteroid_count:
                self.spawn_random()

            self.spawn_timer = 0

    def spawn_random(self):
        """TODO: add docstring."""
        edge_index = random.randint(0, 3)

        rand_pos = random.random()

        direction = self.edges[edge_index][0]

        position = self.edges[edge_index][1](rand_pos)

        velocity = direction.rotate(random.uniform(-45, 45)) * random.uniform(30, 70)

        self.spawn(C.ASTEROID_MAX_RADIUS, position, velocity)
