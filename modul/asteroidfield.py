"""AsteroidField generation and management."""

import random
<<<<<<< HEAD
import pygame
=======

import pygame

>>>>>>> origin/main
import modul.constants as C
from modul.asteroid import Asteroid


class AsteroidField:
<<<<<<< HEAD
    """Manages asteroid spawning and field generation."""
=======
    """TODO: add docstring."""
>>>>>>> origin/main
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
<<<<<<< HEAD
        """Initialize the asteroid field with spawn parameters."""
=======
        """TODO: add docstring."""
>>>>>>> origin/main
        self.spawn_timer = 0
        self.asteroid_count = 5
        self.spawn_interval = 5.0

    def spawn(self, radius, position, velocity):
<<<<<<< HEAD
        """Spawn an asteroid at the given position with velocity."""
=======
        # Randomly select asteroid type based on weights
        """TODO: add docstring."""
>>>>>>> origin/main
        asteroid_type = random.choices(
            list(C.ASTEROID_TYPE_WEIGHTS.keys()),
            weights=list(C.ASTEROID_TYPE_WEIGHTS.values())
        )[0]

        # Add to containers if set (for test group injection)
        containers = getattr(Asteroid, 'containers', ())
        asteroid = Asteroid(position.x, position.y, radius, *containers, asteroid_type=asteroid_type)
        asteroid.velocity = velocity

    def update(self, dt):
<<<<<<< HEAD
        """Update the spawn timer and spawn asteroids as needed."""
=======
        """TODO: add docstring."""
>>>>>>> origin/main
        self.spawn_timer += dt

        # Use containers if set, otherwise fallback to 0
        containers = getattr(Asteroid, 'containers', ())
        if containers:
            asteroid_count = len(containers[0])
        else:
            asteroid_count = 0

        if self.spawn_timer >= self.spawn_interval:
<<<<<<< HEAD
=======
            asteroid_count = len([obj for obj in Asteroid.containers[0]])

>>>>>>> origin/main
            if asteroid_count < self.asteroid_count:
                self.spawn_random()

            self.spawn_timer = 0

    def spawn_random(self):
<<<<<<< HEAD
        """Spawn a random asteroid from screen edges."""
=======
        """TODO: add docstring."""
>>>>>>> origin/main
        edge_index = random.randint(0, 3)

        rand_pos = random.random()

        direction = self.edges[edge_index][0]

        position = self.edges[edge_index][1](rand_pos)

        velocity = direction.rotate(random.uniform(-45, 45)) * random.uniform(30, 70)

        self.spawn(C.ASTEROID_MAX_RADIUS, position, velocity)
