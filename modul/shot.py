import pygame
import math
from modul.constants import *
from modul.circleshape import CircleShape


class Shot(CircleShape):
    asteroids_group = None
    
    @classmethod
    def set_asteroids(cls, asteroids):
        cls.asteroids_group = asteroids
    
    def __init__(self, x, y, shot_type=WEAPON_STANDARD):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = 3
        self.shot_type = shot_type
        self.lifetime = 2.0
        self.damage = 1
        self.target = None
        self.homing_power = 0

        if shot_type == WEAPON_LASER:
            self.radius = 2
            self.damage = 2
            self.penetrating = True

        elif shot_type == WEAPON_MISSILE:
            self.radius = 4
            self.damage = 3
            self.penetrating = False
            self.homing_power = 150
            self.target = None
            self.max_turn_rate = 2.0

        elif shot_type == WEAPON_SHOTGUN:
            self.radius = 2
            self.damage = 1
            self.penetrating = False
            self.lifetime = 0.5

        self.color = WEAPON_COLORS[shot_type]

    def update(self, dt):
        if self.shot_type == WEAPON_MISSILE and self.homing_power > 0 and Shot.asteroids_group:
            self.seek_target(dt)

        self.position += self.velocity * dt

        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()

    def draw(self, screen):
        if self.shot_type == WEAPON_LASER:
            end_pos = self.position + self.velocity.normalize() * 20
            pygame.draw.line(screen, self.color,
                            (int(self.position.x), int(self.position.y)),
                            (int(end_pos.x), int(end_pos.y)), 3)
        elif self.shot_type == WEAPON_MISSILE:
            pygame.draw.circle(screen, self.color,
                              (int(self.position.x), int(self.position.y)), self.radius)

            tail_end = self.position - self.velocity.normalize() * 8
            pygame.draw.line(screen, (255, 128, 0),
                            (int(self.position.x), int(self.position.y)),
                            (int(tail_end.x), int(tail_end.y)), 2)
        else:
            pygame.draw.circle(screen, self.color,
                              (int(self.position.x), int(self.position.y)), self.radius)

    def seek_target(self, dt):
        if not Shot.asteroids_group:
            return

        if not self.target or not self.target.alive():
            closest_dist = float('inf')
            self.target = None

            for asteroid in Shot.asteroids_group:
                dist = (asteroid.position - self.position).length()
                if dist < closest_dist:
                    closest_dist = dist
                    self.target = asteroid

        if self.target and self.target.alive():
            target_dir = (self.target.position - self.position).normalize()
            current_dir = self.velocity.normalize()

            dot = current_dir.x * target_dir.x + current_dir.y * target_dir.y
            dot = max(-1.0, min(1.0, dot))
            angle = math.degrees(math.acos(dot))

            cross = current_dir.x * target_dir.y - current_dir.y * target_dir.x

            turn_amount = min(angle, self.max_turn_rate)

            if cross < 0:
                turn_amount = -turn_amount

            speed = self.velocity.length()
            self.velocity.rotate_ip(turn_amount)
            self.velocity.scale_to_length(speed)
