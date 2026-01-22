"""Module modul.asteroid — minimal module docstring."""

import math
import random

import pygame

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


class Asteroid(CircleShape):
    def __init__(self, x, y, radius, asteroid_type=ASTEROID_TYPE_NORMAL):
        if asteroid_type not in ASTEROID_TYPES:
            raise ValueError(f"Invalid asteroid_type: {asteroid_type}")
        super().__init__(x, y, radius)
        self.asteroid_type = asteroid_type
        self.vertices = self._generate_vertices()
        self.rotation_speed = 0
        self.rotation = 0
        # Metal asteroids require multiple hits
        self.health = ASTEROID_METAL_HEALTH if asteroid_type == ASTEROID_TYPE_METAL else 1

    def _generate_vertices(self):
        vertices = []
        for i in range(ASTEROID_VERTICES):
            angle = (i / ASTEROID_VERTICES) * 2 * math.pi
            distance = self.radius * (1 - ASTEROID_IRREGULARITY + random.random() * ASTEROID_IRREGULARITY * 2)
            x = math.cos(angle) * distance
            y = math.sin(angle) * distance
            vertices.append((x, y))
        return vertices

    def point_in_polygon(self, point):
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
        # Create visual feedback for metal asteroid hits
        if self.asteroid_type == ASTEROID_TYPE_METAL:
            for _ in range(2):
                Particle.create_asteroid_explosion(self.position.x, self.position.y)

        # For large metal asteroids, reduce health and survive the first hit
        if self.asteroid_type == ASTEROID_TYPE_METAL and self.health > 1 and self.radius > ASTEROID_MIN_RADIUS:
            self.health -= 1
            return

        self.kill()

        powerup_group = None
        for container in PowerUp.containers:
            if isinstance(container, pygame.sprite.Group):
                powerup_group = container
                break

        powerups_count = len(powerup_group) if powerup_group else 0

        if random.random() < POWERUP_SPAWN_CHANCE and powerups_count < POWERUP_MAX_COUNT:
            PowerUp(self.position.x, self.position.y)

        if self.radius <= ASTEROID_MIN_RADIUS:
            return

        new_radius = self.radius - ASTEROID_MIN_RADIUS

        base_angle = random.uniform(20, 50)

        # Determine how many pieces to split into based on type
        split_count = ASTEROID_CRYSTAL_SPLIT_COUNT if self.asteroid_type == ASTEROID_TYPE_CRYSTAL else 2

        # Ice asteroids move faster when split (slippery)
        velocity_multiplier = ASTEROID_ICE_VELOCITY_MULTIPLIER if self.asteroid_type == ASTEROID_TYPE_ICE else 1.2

        # Create split asteroids
        for i in range(split_count):
            # Spread shards evenly: crystals into 3 directions, others into 2 opposite angles
            if split_count == ASTEROID_CRYSTAL_SPLIT_COUNT:
                angle = base_angle + (i - 1) * 60  # -60, 0, 60 degrees approximately
            else:
                angle = base_angle if i == 0 else -base_angle

            velocity = self.velocity.rotate(angle) * velocity_multiplier
            rotation_speed = (random.uniform(-0.25, 0.25) + self.velocity.length() * math.sin(math.radians(angle))) * 0.1

            new_asteroid = Asteroid(self.position.x, self.position.y, new_radius, self.asteroid_type)
            new_asteroid.velocity = velocity
            new_asteroid.rotation_speed = rotation_speed
            new_asteroid.vertices = new_asteroid._generate_vertices()

    def update(self, dt):
        self.position += self.velocity * dt
        self.rotation += self.rotation_speed * dt


class EnemyShip(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.radius = PLAYER_RADIUS
        self.rotation_speed = random.uniform(-0.1, 0.1)
        self.rotation = 0
        self.velocity = pygame.Vector2(random.uniform(-50, 50), random.uniform(-50, 50))

    def update(self, dt, player_position=None):
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

        if player_position:
            detection_radius = SCREEN_WIDTH * 0.45
            direction_vector = player_position - self.position
            distance_to_player = direction_vector.length()
            if distance_to_player < detection_radius:
                if distance_to_player != 0:
                    direction_to_player = direction_vector.normalize()
                else:
                    direction_to_player = pygame.Vector2(0, 0)
                self.velocity = direction_to_player * 100
                print(f"EnemyShip moving towards player! Distance: {distance_to_player}")

            else:
                self.velocity *= 0.8

        print(f"EnemyShip Position: {self.position}, Velocity: {self.velocity}")

    def collides_with(self, other):
        distance = (self.position - other.position).length()
        return distance < (self.radius + other.radius)

    def split(self):
        from modul.particle import Particle

        Particle.create_ship_explosion(self.position.x, self.position.y)
        self.kill()

    def draw(self, screen):
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
        super().kill()
        from modul.particle import Particle

        Particle.create_ship_explosion(self.position.x, self.position.y)
        if self in collidable:
            collidable.remove(self)
        if self in drawable:
            drawable.remove(self)
        if self in updatable:
            updatable.remove(self)
