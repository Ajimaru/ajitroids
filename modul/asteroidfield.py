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
        """
        Set up spawn timing and limits for the asteroid field.
        
        Initializes internal state used to control when and how many asteroids are spawned.
        
        Attributes:
            spawn_timer (float): Accumulated time (in seconds) since the last spawn check.
            asteroid_count (int): Maximum number of asteroids allowed before spawning is suppressed.
            spawn_interval (float): Time interval (in seconds) between spawn checks.
        """
        self.spawn_timer = 0
        self.asteroid_count = 5
        self.spawn_interval = 5.0

    def spawn(self, radius, position, velocity):
        """
        Create a new asteroid at the specified position with the given radius and velocity.
        
        The asteroid's type is chosen using the weighted probabilities defined in C.ASTEROID_TYPE_WEIGHTS. If the Asteroid class exposes a `containers` attribute, its contents are passed into the Asteroid constructor (test injection hook). The created asteroid's velocity is then set to the provided vector.
        
        Parameters:
            radius (float): Radius to assign to the new asteroid.
            position (pygame.Vector2): Spawn position; the asteroid is created at position.x, position.y.
            velocity (pygame.Vector2): Velocity vector to assign to the new asteroid.
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
        """
        Advance the spawn timer and spawn a new asteroid when conditions are met.
        
        Increments the field's spawn timer by dt. If the timer is greater than or equal to the configured spawn_interval and the current asteroid count is less than the field's asteroid_count limit, spawns one asteroid via spawn_random() and resets the timer. The current asteroid count is read from Asteroid.containers[0] when the class attribute exists; when absent it is treated as 0.
        
        Parameters:
            dt (float): Elapsed time in seconds since the last update.
        """
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
        Spawn an asteroid at a random position along a screen edge with a randomized inward velocity.
        
        Selects one of the four screen edges uniformly, chooses a position along that edge, rotates the edge's outward direction by a random angle between -45 and 45 degrees, scales the resulting vector by a random speed between 30 and 70, and spawns an asteroid with the configured maximum radius using that position and velocity.
        """
        edge_index = random.randint(0, 3)

        rand_pos = random.random()

        direction = self.edges[edge_index][0]

        position = self.edges[edge_index][1](rand_pos)

        velocity = direction.rotate(random.uniform(-45, 45)) * random.uniform(30, 70)

        self.spawn(C.ASTEROID_MAX_RADIUS, position, velocity)