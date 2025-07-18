import random
import math
import pygame
from modul.circleshape import CircleShape
from modul.constants import *
from modul.shot import Shot
from modul.powerup import PowerUp
from modul.player import Player
import modul.particle as Particle
from modul.groups import collidable, drawable, updatable

class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.vertices = self._generate_vertices()
        self.rotation_speed = 0
        self.rotation = 0
        
    def _generate_vertices(self):
        vertices = []
        for i in range(ASTEROID_VERTICES):
            angle = (i / ASTEROID_VERTICES) * 2 * math.pi
            distance = self.radius * (1 - ASTEROID_IRREGULARITY + 
                                   random.random() * ASTEROID_IRREGULARITY * 2)
            x = math.cos(angle) * distance
            y = math.sin(angle) * distance
            vertices.append((x, y))
        return vertices

    def point_in_polygon(self, point):
        px, py = point
        vertices = [(self.position.x + vx, self.position.y + vy) 
                    for vx, vy in self.vertices]
        
        crosses = 0
        for i in range(len(vertices)):
            j = (i + 1) % len(vertices)
            
            xi, yi = vertices[i]
            xj, yj = vertices[j]
            
            if ((yi > py) != (yj > py) and
                px < xi + (xj - xi) * (py - yi) / (yj - yi)):
                crosses += 1
        
        return crosses % 2 == 1

    def collides_with(self, other):
        if (self.position - other.position).length() > (self.radius + other.radius):
            return False
        
        if isinstance(other, Shot):
            shot_pos = other.position
            shot_radius = other.radius
            
            points = [(self.position.x + vx, self.position.y + vy) 
                     for vx, vy in self.vertices]
            
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
                math.sin(self.rotation) * x + math.cos(self.rotation) * y
            )
            for x, y in self.vertices
        ]
        points = [(self.position.x + x, self.position.y + y) for x, y in rotated_vertices]
        pygame.draw.polygon(screen, "white", points, 2)
        if COLLISION_DEBUG:
            pygame.draw.circle(screen, "red", self.position, self.radius, 1)
            for point in points:
                pygame.draw.circle(screen, "yellow", point, 2)

    def split(self):
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

        random_angle = random.uniform(20, 50)

        velocity1 = self.velocity.rotate(random_angle) * 1.2
        velocity2 = self.velocity.rotate(-random_angle) * 1.2

        rotation_speed1 = (random.uniform(-0.25, 0.25) + self.velocity.length() * math.sin(math.radians(random_angle))) * 0.1
        rotation_speed2 = (random.uniform(-0.25, 0.25) + self.velocity.length() * math.sin(math.radians(-random_angle))) * 0.1

        new_asteroid1 = Asteroid(self.position.x, self.position.y, new_radius)
        new_asteroid2 = Asteroid(self.position.x, self.position.y, new_radius)

        new_asteroid1.velocity = velocity1
        new_asteroid2.velocity = velocity2

        new_asteroid1.rotation_speed = rotation_speed1
        new_asteroid2.rotation_speed = rotation_speed2

        new_asteroid1.vertices = new_asteroid1._generate_vertices()
        new_asteroid2.vertices = new_asteroid2._generate_vertices()

    def update(self, dt):
        self.position += self.velocity * dt
        self.rotation += self.rotation_speed * dt  # Rotation der Asteroiden

class EnemyShip(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.radius = PLAYER_RADIUS  # Setze den Radius auf die Größe des Player-Sprites
        self.rotation_speed = random.uniform(-0.1, 0.1)
        self.rotation = 0
        self.velocity = pygame.Vector2(random.uniform(-50, 50), random.uniform(-50, 50))

    def update(self, dt):
        self.position += self.velocity * dt
        self.rotation += self.rotation_speed * dt

        # Bildschirmgrenzen überprüfen und Wrap-around anwenden
        if self.position.x < 0:
            self.position.x = SCREEN_WIDTH
        elif self.position.x > SCREEN_WIDTH:
            self.position.x = 0

        if self.position.y < 0:
            self.position.y = SCREEN_HEIGHT
        elif self.position.y > SCREEN_HEIGHT:
            self.position.y = 0

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
            (-self.radius, self.radius),
            (self.radius, self.radius)
        ]

        rotated_points = [
            (
                math.cos(self.rotation) * x - math.sin(self.rotation) * y,
                math.sin(self.rotation) * x + math.cos(self.rotation) * y
            )
            for x, y in points
        ]

        points = [(self.position.x + x, self.position.y + y) for x, y in rotated_points]
        pygame.draw.polygon(screen, "red", points, 2)

    def update(self, dt):
        self.position += self.velocity * dt
        self.rotation += self.rotation_speed * dt

        # Bildschirmgrenzen überprüfen und Wrap-around anwenden
        if self.position.x < 0:
            self.position.x = SCREEN_WIDTH
        elif self.position.x > SCREEN_WIDTH:
            self.position.x = 0

        if self.position.y < 0:
            self.position.y = SCREEN_HEIGHT
        elif self.position.y > SCREEN_HEIGHT:
            self.position.y = 0

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
