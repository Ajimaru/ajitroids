"""AsteroidField generation and management."""

import random
import pygame
import modul.constants as C
from modul.asteroid import Asteroid


class AsteroidField:
    """Manages asteroid spawning and field generation."""
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
        """Initialize the asteroid field with spawn parameters."""
        self.spawn_timer = 0
        self.asteroid_count = 5
        self.spawn_interval = 5.0

    def spawn(self, radius, position, velocity):
        """
        Create and add a new asteroid at the given position and set its initial velocity.
        
        Chooses an asteroid type according to C.ASTEROID_TYPE_WEIGHTS and constructs an Asteroid. If the class attribute `Asteroid.containers` exists, its contents are passed to the Asteroid constructor before the asteroid_type keyword.
        
        Parameters:
            radius (float): Radius of the spawned asteroid.
            position (pygame.Vector2): Spawn coordinates; x and y are used as the asteroid's position.
            velocity (pygame.Vector2): Initial velocity vector assigned to the asteroid.
        """
        asteroid_type = random.choices(
            list(C.ASTEROID_TYPE_WEIGHTS.keys()),
            weights=list(C.ASTEROID_TYPE_WEIGHTS.values())
        )[0]

        # Add to containers if set (for test group injection)
        containers = getattr(Asteroid, 'containers', ())
        asteroid = Asteroid(position.x, position.y, radius, *containers, asteroid_type=asteroid_type)
        asteroid.velocity = velocity

    def update(self, dt):
        """Update the spawn timer and spawn asteroids as needed."""
        self.spawn_timer += dt

        # Use containers if set, otherwise fallback to 0
        containers = getattr(Asteroid, 'containers', ())
        if containers:
            asteroid_count = len(containers[0])
        else:
            asteroid_count = 0

        if self.spawn_timer >= self.spawn_interval:
            if asteroid_count < self.asteroid_count:
                self.spawn_random()

            self.spawn_timer = 0

    def spawn_random(self):
        """
        Spawn a single asteroid at a random screen edge with randomized position and velocity.
        
        Selects one of the four screen edges, picks a position along that edge, computes a velocity by rotating the edge's direction by a random angle between -45 and 45 degrees and scaling it to a random speed between 30 and 70, then spawns an asteroid with C.ASTEROID_MAX_RADIUS at the computed position.
        """
        edge_index = random.randint(0, 3)

        rand_pos = random.random()

        direction = self.edges[edge_index][0]

        position = self.edges[edge_index][1](rand_pos)

        velocity = direction.rotate(random.uniform(-45, 45)) * random.uniform(30, 70)

        self.spawn(C.ASTEROID_MAX_RADIUS, position, velocity)