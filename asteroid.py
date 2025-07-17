import random
import math
import pygame
from circleshape import CircleShape
from constants import *
from shot import Shot
from powerup import PowerUp

class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.vertices = self._generate_vertices()
        
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
        points = [(self.position.x + x, self.position.y + y) 
                 for x, y in self.vertices]
        pygame.draw.polygon(screen, "white", points, 2)
        if COLLISION_DEBUG:
            pygame.draw.circle(screen, "red", self.position, self.radius, 1)
            for point in [(self.position.x + x, self.position.y + y) 
                         for x, y in self.vertices]:
                pygame.draw.circle(screen, "yellow", point, 2)

    def update(self, dt):
        self.position += self.velocity * dt

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
        
        new_asteroid1 = Asteroid(self.position.x, self.position.y, new_radius)
        new_asteroid2 = Asteroid(self.position.x, self.position.y, new_radius)
        
        new_asteroid1.velocity = velocity1
        new_asteroid2.velocity = velocity2

        new_asteroid1.vertices = new_asteroid1._generate_vertices()
        new_asteroid2.vertices = new_asteroid2._generate_vertices()
