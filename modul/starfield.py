"""Starfield background rendering utilities."""

import math
import random
import pygame
import modul.constants as C


class Star:
    """Represents a twinkling star."""
    def __init__(self):
        """Initialize star with random properties."""
        self.position = pygame.Vector2(random.randint(0, C.SCREEN_WIDTH), random.randint(0, C.SCREEN_HEIGHT))
        self.size = random.choice(C.STAR_SIZES)
        self.color = random.choice(C.STAR_COLORS)
        self.twinkle_timer = random.random() * 2 * math.pi
        # Cache parsed color for safe use in update()
        try:
            color_obj = pygame.Color(self.color)
            self._parsed_color = [color_obj.r, color_obj.g, color_obj.b]
        except (ValueError, TypeError):
            # Fallback to white if color parsing fails
            self._parsed_color = [255, 255, 255]
        self.current_color = self._parsed_color[:]

    def update(self, dt):
        """Update star twinkling effect."""
        self.twinkle_timer += dt
        brightness = abs(math.sin(self.twinkle_timer))
        # Use cached parsed color for safety
        self.current_color = [int(c * brightness) for c in self._parsed_color]

    def draw(self, screen):
        """Draw star on screen."""
        pygame.draw.circle(screen, self.current_color, self.position, self.size)


class Starfield:
    """Manages background starfield."""
    def __init__(self):
        """Initialize starfield with stars."""
        self.stars = [Star() for _ in range(C.STAR_COUNT)]

    def update(self, dt):
        """Update all stars."""
        for star in self.stars:
            star.update(dt)

    def draw(self, screen):
        """Draw all stars."""
        for star in self.stars:
            star.draw(screen)


class MenuStarfield:
    """Manages animated starfield for menus."""
    def __init__(self, num_stars=150):
        """Initialize menu starfield."""
        self.stars = []
        self.speed = 0.4
        self.respawn_counter = 0
        self.max_respawns_per_frame = 1
        self.respawn_delay = 0.2
        self.respawn_delay_max = 0.2
        for _ in range(num_stars):
            if random.random() < 0.7:
                distance = random.uniform(50, C.SCREEN_WIDTH / 2)
                angle = random.random() * 2 * math.pi
                x = C.SCREEN_WIDTH / 2 + math.cos(angle) * distance
                y = C.SCREEN_HEIGHT / 2 + math.sin(angle) * distance
            else:
                distance = random.random() * 50
                angle = random.random() * 2 * math.pi
                x = C.SCREEN_WIDTH / 2 + math.cos(angle) * distance
                y = C.SCREEN_HEIGHT / 2 + math.sin(angle) * distance
            z = random.randint(1, 8)
            brightness = random.uniform(100, 255)
            self.stars.append([x, y, z, brightness])

    def update(self, dt):
        """Update starfield animation."""
        center_x = C.SCREEN_WIDTH / 2
        center_y = C.SCREEN_HEIGHT / 2
        stars_to_respawn = []
        for star in self.stars:
            dx = star[0] - center_x
            dy = star[1] - center_y
            speed_factor = (star[2] / 2) * self.speed * dt * 60
            star[0] += dx * speed_factor * 0.01
            star[1] += dy * speed_factor * 0.01
            if star[0] < -50 or star[0] > C.SCREEN_WIDTH + 50 or star[1] < -50 or star[1] > C.SCREEN_HEIGHT + 50:
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
        """Draw starfield on screen."""
        for star in self.stars:
            try:
                if len(star) >= 4:
                    x, y, z, brightness = star[0], star[1], star[2], star[3]
                    if not all(isinstance(val, (int, float)) for val in [x, y, z, brightness]):
                        continue
                    scale = 200 / (z + 200)
                    screen_x = C.SCREEN_WIDTH / 2 + (x - C.SCREEN_WIDTH / 2) * scale
                    screen_y = C.SCREEN_HEIGHT / 2 + (y - C.SCREEN_HEIGHT / 2) * scale
                    size = max(1, int(3 * scale))
                    color_value = min(255, int(brightness * scale))
                    color = (color_value, color_value, color_value)
                    if (
                        0 <= screen_x < C.SCREEN_WIDTH
                        and 0 <= screen_y < C.SCREEN_HEIGHT
                        and isinstance(screen_x, (int, float))
                        and isinstance(screen_y, (int, float))
                    ):
                        pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), max(1, size))
            except (IndexError, TypeError, ValueError) as e:
                print(f"Skipped faulty star: {star}, Error: {e}")
                continue
