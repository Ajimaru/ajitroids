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
        self.asteroid_count = 5
        self.spawn_interval = 5.0

    def spawn(self, radius, position, velocity):
        asteroid = Asteroid(position.x, position.y, radius)
        asteroid.velocity = velocity

    def update(self, dt):
        self.spawn_timer += dt

        if self.spawn_timer >= self.spawn_interval:
            from asteroid import Asteroid
            asteroid_count = len([obj for obj in Asteroid.containers[0]])

            if asteroid_count < self.asteroid_count:
                self.spawn_random()

            self.spawn_timer = 0

    def spawn_random(self):
        edge_index = random.randint(0, 3)

        rand_pos = random.random()

        direction = self.edges[edge_index][0]

        position = self.edges[edge_index][1](rand_pos)

        velocity = direction.rotate(random.uniform(-45, 45)) * random.uniform(30, 70)

        self.spawn(ASTEROID_MAX_RADIUS, position, velocity)