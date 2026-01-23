"""Module modul.asteroid — minimal module docstring."""

import math
import random
import pygame
import logging

from modul.circleshape import CircleShape
from modul.constants import (ASTEROID_CRYSTAL_SPLIT_COUNT,
                             ASTEROID_ICE_VELOCITY_MULTIPLIER,
                             ASTEROID_IRREGULARITY, ASTEROID_METAL_HEALTH,
                             ASTEROID_MIN_RADIUS, ASTEROID_TYPE_COLORS,
                             ASTEROID_TYPE_CRYSTAL, ASTEROID_TYPE_ICE,
                             ASTEROID_TYPE_METAL, ASTEROID_TYPE_NORMAL,
                             ASTEROID_TYPES, ASTEROID_VERTICES,
                             COLLISION_DEBUG, PLAYER_RADIUS, POWERUP_MAX_COUNT,
                             POWERUP_SPAWN_CHANCE, SCREEN_HEIGHT, SCREEN_WIDTH)
from modul.groups import collidable, drawable, updatable
from modul.particle import Particle
from modul.powerup import PowerUp
from modul.shot import Shot

# Toggle to enable verbose enemy-ship debug output during development.
# Set to True locally when you need per-frame tracing; keep False in production.
DEBUG = False
logger = logging.getLogger(__name__)


class Asteroid(CircleShape, pygame.sprite.Sprite):
    """Represents an asteroid in the game with various types and behaviors."""
    def __init__(self, x, y, radius, *args, asteroid_type=None):
        """
        Create an Asteroid at (x, y) with the given radius and type.
        
        Supports legacy positional usage where the last element of *args may be an asteroid_type string; any remaining positional args are treated as pygame sprite groups to add this sprite to. If asteroid_type is omitted, defaults to ASTEROID_TYPE_NORMAL. Metal asteroids receive ASTEROID_METAL_HEALTH; other types receive health 1. Also initializes polygon vertices, rotation properties, a minimal pygame image/rect for sprite compatibility, and adds the instance to any class-level containers.
        
        Parameters:
            asteroid_type (str, optional): Name of the asteroid type; must be one of ASTEROID_TYPES.
            *args: Optional pygame sprite groups and/or a trailing asteroid_type for backwards compatibility.
        
        Raises:
            ValueError: If asteroid_type is not a valid member of ASTEROID_TYPES.
        """
        # Args parsing: support older callers that passed asteroid_type
        # positionally as 4th argument, or callers that pass groups first
        groups = ()
        if args:
            # If last positional arg is a valid asteroid type string and no
            # explicit keyword was provided, treat it as the asteroid_type.
            if asteroid_type is None and isinstance(args[-1], str) and args[-1] in ASTEROID_TYPES:
                asteroid_type = args[-1]
                groups = args[:-1]
            else:
                groups = args
        if asteroid_type is None:
            asteroid_type = ASTEROID_TYPE_NORMAL
        if asteroid_type not in ASTEROID_TYPES:
            raise ValueError(f"Invalid asteroid_type: {asteroid_type}")

        # Explicitly call both base class initializers in correct order
        CircleShape.__init__(self, x, y, radius)
        pygame.sprite.Sprite.__init__(self, *groups)
        self.asteroid_type = asteroid_type
        self.vertices = self._generate_vertices()
        self.rotation_speed = 0
        self.rotation = 0
        # Metal asteroids require multiple hits
        self.health = ASTEROID_METAL_HEALTH if asteroid_type == ASTEROID_TYPE_METAL else 1

        # Minimal image and rect for pygame.sprite.Sprite compatibility
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(self.position.x, self.position.y))

        # Add to containers if set (for test group injection)
        containers = getattr(type(self), 'containers', ())
        if containers:
            for group in containers:
                group.add(self)

    def _generate_vertices(self):
        """
        Create an irregular polygonal vertex list representing this asteroid's shape.
        
        Each returned item is an (x, y) tuple of floats giving a vertex offset in local coordinates.
        The list contains ASTEROID_VERTICES entries and describes a roughly circular polygon whose vertex distances from the center vary to produce irregularity.
        
        Returns:
            list[tuple[float, float]]: Vertex offsets for the asteroid polygon in local coordinates.
        """
        vertices = []
        for i in range(ASTEROID_VERTICES):
            angle = (i / ASTEROID_VERTICES) * 2 * math.pi
            distance = self.radius * (1 - ASTEROID_IRREGULARITY + random.random() * ASTEROID_IRREGULARITY * 2)
            x = math.cos(angle) * distance
            y = math.sin(angle) * distance
            vertices.append((x, y))
        return vertices

    def point_in_polygon(self, point):
        """
        Determine whether a world-space point lies inside the asteroid's polygon.
        
        Parameters:
            point (tuple[float, float]): (x, y) coordinates in world space.
        
        Returns:
            true if the point is inside the polygon, false otherwise.
        """
        px, py = point
        vertices = [(self.position.x + vx, self.position.y + vy) for vx, vy in self.vertices]

        crosses = 0
        for i in range(len(vertices)):
            j = (i + 1) % len(vertices)

            xi, yi = vertices[i]
            xj, yj = vertices[j]

            if (yi > py) != (yj > py) and px < xi + (xj - xi) * (py - yi) / (yj - yi):
                crosses += 1

        return crosses % 2 == 1

    def collides_with(self, other):
        """
        Determine whether this asteroid intersects another object, using polygon-edge checks for shots.
        
        Parameters:
            other: The other object to test for collision. If `other` is a `Shot`, collision is computed against the asteroid's polygon edges using the shot's radius; for other types the method delegates to the superclass collision logic.
        
        Returns:
            bool: `True` if the asteroid intersects `other`, `False` otherwise.
        """
        if (self.position - other.position).length() > (self.radius + other.radius):
            return False

        if isinstance(other, Shot):
            shot_pos = other.position
            shot_radius = other.radius

            points = [(self.position.x + vx, self.position.y + vy) for vx, vy in self.vertices]

            for i in range(len(points)):
                j = (i + 1) % len(points)

                p1 = pygame.Vector2(points[i])
                p2 = pygame.Vector2(points[j])

                line_vec = p2 - p1
                line_len = line_vec.length()
                if line_len == 0:
                    continue

                line_vec_normalized = line_vec / line_len

                point_vec = shot_pos - p1

                projection = point_vec.dot(line_vec_normalized)

                projection = max(0, min(line_len, projection))

                closest_point = p1 + line_vec_normalized * projection

                if (closest_point - shot_pos).length() <= shot_radius:
                    return True

        return super().collides_with(other)

    def draw(self, screen):
        """
        Render the asteroid as a rotated, type-colored polygon onto the provided surface.
        
        The polygon is drawn using the asteroid's vertices transformed by its current rotation and position. The outline color is selected from ASTEROID_TYPE_COLORS based on the asteroid's type. When COLLISION_DEBUG is enabled, also draw the collision circle and small markers at each vertex for debugging.
        
        Parameters:
            screen (pygame.Surface): Surface to draw the asteroid on.
        """
        rotated_vertices = [
            (
                math.cos(self.rotation) * x - math.sin(self.rotation) * y,
                math.sin(self.rotation) * x + math.cos(self.rotation) * y,
            )
            for x, y in self.vertices
        ]
        points = [(self.position.x + x, self.position.y + y) for x, y in rotated_vertices]

        # Get color based on asteroid type
        color = ASTEROID_TYPE_COLORS.get(
            self.asteroid_type,
            ASTEROID_TYPE_COLORS[ASTEROID_TYPE_NORMAL]
        )

        pygame.draw.polygon(screen, color, points, 2)
        if COLLISION_DEBUG:
            pygame.draw.circle(screen, "red", self.position, self.radius, 1)
            for point in points:
                pygame.draw.circle(screen, "yellow", point, 2)

    def split(self):
        """
        Handle destruction of this asteroid: either absorb damage (metal), produce effects, remove itself, and optionally create smaller child asteroids and a power-up.
        
        If the asteroid is metal and still has extra health and sufficiently large radius, decrement health and do not split. Otherwise, emit explosion particles for metal asteroids, remove this asteroid from all groups (kill), and possibly spawn a PowerUp with probability POWERUP_SPAWN_CHANCE subject to POWERUP_MAX_COUNT. If the asteroid's radius is greater than ASTEROID_MIN_RADIUS, create a set of child Asteroid instances with strictly smaller radii; the number of children, their velocities, and rotation speeds depend on the asteroid type (crystal produces more fragments, ice uses a different velocity multiplier). Child asteroids inherit this asteroid's type and are placed into the same containers/groups as the parent.
        """
        # Metal asteroid: show explosion effect
        if self.asteroid_type == ASTEROID_TYPE_METAL:
            for _ in range(2):
                Particle.create_asteroid_explosion(self.position.x, self.position.y)

        # Metal asteroid: survive first hit if large enough
        if self.asteroid_type == ASTEROID_TYPE_METAL and self.health > 1 and self.radius > ASTEROID_MIN_RADIUS:
            self.health -= 1
            return

        # Remove self from all groups (containers and sprite groups)
        containers = getattr(type(self), 'containers', ())
        sprite_groups = self.groups()
        all_groups = set(containers) | set(sprite_groups)
        for group in all_groups:
            try:
                group.remove(self)
            except (ValueError, KeyError):
                pass
        self.kill()

        # PowerUp spawn logic
        powerup_group = collidable
        powerups_count = len([sprite for sprite in powerup_group if isinstance(sprite, PowerUp)])
        if random.random() < POWERUP_SPAWN_CHANCE and powerups_count < POWERUP_MAX_COUNT:
            PowerUp(self.position.x, self.position.y)

        # If minimum size, do not split further
        if self.radius <= ASTEROID_MIN_RADIUS:
            return

        # Always create children with strictly smaller radius
        new_radius = max(self.radius - ASTEROID_MIN_RADIUS, ASTEROID_MIN_RADIUS - 1)
        if new_radius >= self.radius:
            new_radius = self.radius - 1
        if new_radius < ASTEROID_MIN_RADIUS:
            new_radius = ASTEROID_MIN_RADIUS

        base_angle = random.uniform(20, 50)
        split_count = ASTEROID_CRYSTAL_SPLIT_COUNT if self.asteroid_type == ASTEROID_TYPE_CRYSTAL else 2
        velocity_multiplier = ASTEROID_ICE_VELOCITY_MULTIPLIER if self.asteroid_type == ASTEROID_TYPE_ICE else 1.2
        containers = getattr(type(self), 'containers', ())
        child_groups = tuple(containers) if containers else self.groups()

        for i in range(split_count):
            if split_count == ASTEROID_CRYSTAL_SPLIT_COUNT:
                angle = base_angle + (i - 1) * 60
            else:
                angle = base_angle if i == 0 else -base_angle
            velocity = self.velocity.rotate(angle) * velocity_multiplier
            rotation_speed = (random.uniform(-0.25, 0.25) + self.velocity.length() * math.sin(math.radians(angle))) * 0.1
            # Ensure children have strictly smaller radius
            child_radius = new_radius
            if child_radius >= self.radius:
                child_radius = self.radius - 1
            if child_radius < ASTEROID_MIN_RADIUS:
                child_radius = ASTEROID_MIN_RADIUS
            new_asteroid = Asteroid(self.position.x, self.position.y, child_radius, *child_groups, asteroid_type=self.asteroid_type)
            new_asteroid.velocity = velocity
            new_asteroid.rotation_speed = rotation_speed
            if self.asteroid_type == ASTEROID_TYPE_METAL:
                new_asteroid.health = ASTEROID_METAL_HEALTH

    def update(self, dt):
        """
        Advance the asteroid's position and rotation by the given time step.
        
        Parameters:
            dt (float): Time step in seconds used to scale linear movement and angular rotation.
        """
        self.position += self.velocity * dt
        self.rotation += self.rotation_speed * dt


class EnemyShip(CircleShape):
    """Represents an enemy ship that pursues the player."""
    def __init__(self, x, y, radius):
        """
        Create an EnemyShip positioned at (x, y) with a given size hint.
        
        Initializes the ship's base CircleShape state, forces the logical radius to PLAYER_RADIUS (ignoring the provided `radius`), sets a small random rotation speed, a zero initial rotation, and assigns a non-zero random velocity vector to ensure movement (useful for tests).
        
        Parameters:
            x (float): Initial x-coordinate of the ship.
            y (float): Initial y-coordinate of the ship.
            radius (float): Size hint (ignored; the ship's radius is set to PLAYER_RADIUS).
        """
        super().__init__(x, y, radius)
        self.radius = PLAYER_RADIUS
        self.rotation_speed = random.uniform(-0.1, 0.1)
        self.rotation = 0
        # Ensure velocity is nonzero for tests
        self.velocity = pygame.Vector2(random.choice([-1, 1]) * random.uniform(30, 60), random.choice([-1, 1]) * random.uniform(30, 60))

    def update(self, dt, player_position=None):
        """
        Update the ship's position, rotation, screen-wrapping, and simple pursuit behavior.
        
        Parameters:
            dt (float): Time step used to scale position and rotation updates (seconds).
            player_position (pygame.Vector2 | None): If provided, the world position of the player; when the player is within 45% of the screen width the ship sets its velocity toward the player, otherwise the velocity is dampened.
        """
        self.position += self.velocity * dt
        self.rotation += self.rotation_speed * dt

        if self.position.x < 0:
            self.position.x = SCREEN_WIDTH
        elif self.position.x > SCREEN_WIDTH:
            self.position.x = 0

        if self.position.y < 0:
            self.position.y = SCREEN_HEIGHT
        elif self.position.y > SCREEN_HEIGHT:
            self.position.y = 0

        if player_position is not None:
            detection_radius = SCREEN_WIDTH * 0.45
            direction_vector = player_position - self.position
            distance_to_player = direction_vector.length()
            if distance_to_player < detection_radius:
                if distance_to_player != 0:
                    direction_to_player = direction_vector.normalize()
                else:
                    direction_to_player = pygame.Vector2(0, 0)
                self.velocity = direction_to_player * 100
                if DEBUG:
                    logger.debug("EnemyShip moving towards player! Distance: %s", distance_to_player)

            else:
                self.velocity *= 0.8

        if DEBUG:
            logger.debug("EnemyShip Position: %s, Velocity: %s", self.position, self.velocity)

    def collides_with(self, other):
        """
        Determine whether this object intersects another by comparing center-to-center distance with the sum of their radii.
        
        Returns:
            `true` if the distance between centers is less than the sum of the two radii, `false` otherwise.
        """
        distance = (self.position - other.position).length()
        return distance < (self.radius + other.radius)

    def split(self):
        """Destroy the enemy ship with explosion effect."""
        # Use module-level `Particle` imported at top
        Particle.create_ship_explosion(self.position.x, self.position.y)
        self.kill()

    def draw(self, screen):
        """
        Draw the enemy ship polygon rotated to the ship's current rotation and translated to its position.
        
        Parameters:
            screen (pygame.Surface): Surface to draw the ship on.
        """
        points = [
            (0, -self.radius),
            (-self.radius * 0.8, self.radius * 0.5),
            (-self.radius * 0.4, self.radius * 0.8),
            (self.radius * 0.4, self.radius * 0.8),
            (self.radius * 0.8, self.radius * 0.5),
        ]

        rotated_points = [
            (
                math.cos(self.rotation) * x - math.sin(self.rotation) * y,
                math.sin(self.rotation) * x + math.cos(self.rotation) * y,
            )
            for x, y in points
        ]

        points = [(self.position.x + x, self.position.y + y) for x, y in rotated_points]
        pygame.draw.polygon(screen, "red", points, 2)

    def kill(self):
        """Remove the enemy ship from all groups with explosion effect."""
        super().kill()
        Particle.create_ship_explosion(self.position.x, self.position.y)
        if self in collidable:
            collidable.remove(self)
        if self in drawable:
            drawable.remove(self)
        if self in updatable:
            updatable.remove(self)