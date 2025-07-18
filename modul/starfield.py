import random
import pygame
import math
from modul.constants import *


class Star:
    def __init__(self):
        self.position = pygame.Vector2(random.randint(
            0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
        self.size = random.choice(STAR_SIZES)
        self.color = random.choice(STAR_COLORS)
        self.twinkle_timer = random.random() * 2 * math.pi

    def update(self, dt):
        self.twinkle_timer += dt
        brightness = abs(math.sin(self.twinkle_timer))
        self.current_color = [int(c * brightness)
                              for c in pygame.Color(self.color)]

    def draw(self, screen):
        pygame.draw.circle(screen, self.current_color,
                           self.position, self.size)


class Starfield:
    def __init__(self):
        self.stars = [Star() for _ in range(STAR_COUNT)]

    def update(self, dt):
        for star in self.stars:
            star.update(dt)

    def draw(self, screen):
        for star in self.stars:
            star.draw(screen)


class MenuStarfield:
    def __init__(self, num_stars=150):
        self.stars = []
        self.speed = 0.4
        self.respawn_counter = 0
        self.max_respawns_per_frame = 1
        self.respawn_delay = 0
        self.respawn_delay_max = 0.2
        for _ in range(num_stars):
            if random.random() < 0.7:
                distance = random.uniform(50, SCREEN_WIDTH / 2)
                angle = random.random() * 2 * math.pi
                x = SCREEN_WIDTH / 2 + math.cos(angle) * distance
                y = SCREEN_HEIGHT / 2 + math.sin(angle) * distance
            else:
                distance = random.random() * 50
                angle = random.random() * 2 * math.pi
                x = SCREEN_WIDTH / 2 + math.cos(angle) * distance
                y = SCREEN_HEIGHT / 2 + math.sin(angle) * distance
            z = random.randint(1, 8)
            brightness = random.uniform(100, 255)
            self.stars.append([x, y, z, brightness])

    def update(self, dt):
        center_x = SCREEN_WIDTH / 2
        center_y = SCREEN_HEIGHT / 2
        stars_to_respawn = []
        for star in self.stars:
            dx = star[0] - center_x
            dy = star[1] - center_y
            speed_factor = (star[2] / 2) * self.speed * dt * 60
            star[0] += dx * speed_factor * 0.01
            star[1] += dy * speed_factor * 0.01
            if star[0] < -50 or star[0] > SCREEN_WIDTH + 50 or star[1] < -50 or star[1] > SCREEN_HEIGHT + 50:
                stars_to_respawn.append(star)
        self.respawn_delay -= dt
        if self.respawn_delay <= 0 and stars_to_respawn:
            self.respawn_delay = self.respawn_delay_max
            star = stars_to_respawn.pop(0)
            angle = random.random() * 2 * math.pi
            distance = random.uniform(5, 15)
            star[0] = center_x + math.cos(angle) * distance
            star[1] = center_y + math.sin(angle) * distance
            star[2] = random.randint(1, 8)
            if len(star) >= 4:
                star[3] = random.uniform(100, 255)

    def draw(self, screen):
        for star in self.stars:
            try:
                if len(star) >= 4:
                    x, y, z, brightness = star[0], star[1], star[2], star[3]
                    if not all(isinstance(val, (int, float)) for val in [x, y, z, brightness]):
                        continue
                    scale = 200 / (z + 200)
                    screen_x = SCREEN_WIDTH / 2 + \
                        (x - SCREEN_WIDTH / 2) * scale
                    screen_y = SCREEN_HEIGHT / 2 + \
                        (y - SCREEN_HEIGHT / 2) * scale
                    size = max(1, int(3 * scale))
                    color_value = min(255, int(brightness * scale))
                    color = (color_value, color_value, color_value)
                    if (
                        0 <= screen_x < SCREEN_WIDTH
                        and 0 <= screen_y < SCREEN_HEIGHT
                        and isinstance(screen_x, (int, float))
                        and isinstance(screen_y, (int, float))
                    ):
                        pygame.draw.circle(
                            screen, color, (int(screen_x), int(screen_y)), max(1, size))
            except (IndexError, TypeError, ValueError) as e:
                print(f"Skipped faulty star: {star}, Error: {e}")
                continue
