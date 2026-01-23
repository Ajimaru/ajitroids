"""Starfield background rendering utilities."""

import math
import random
import pygame
import modul.constants as C


class Star:
    """Represents a twinkling star."""
    def __init__(self):
        """
        Initialize a Star with randomized position, size, color, and twinkle state.
        
        Sets these instance attributes:
        - position: random on-screen Vector2.
        - size: chosen from STAR_SIZES.
        - color: original color value chosen from STAR_COLORS.
        - twinkle_timer: random phase in [0, 2π).
        - _parsed_color: cached RGB list parsed from `color`, falls back to white `[255, 255, 255]` if parsing fails.
        - current_color: a copy of `_parsed_color` used for animated brightness updates.
        """
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
        """
        Update the star's twinkle state and recompute its displayed color.
        
        Parameters:
            dt (float): Time in seconds since the last update; advances the internal twinkle timer and updates the star's current color based on the resulting periodic brightness.
        """
        self.twinkle_timer += dt
        brightness = abs(math.sin(self.twinkle_timer))
        # Use cached parsed color for safety
        self.current_color = [int(c * brightness) for c in self._parsed_color]

    def draw(self, screen):
        """
        Draws this star as a filled circle onto the given surface.
        
        Parameters:
            screen (pygame.Surface): Surface to render the star on.
        """
        pygame.draw.circle(screen, self.current_color, self.position, self.size)


class Starfield:
    """Manages background starfield."""
    def __init__(self):
        """
        Create a Starfield populated with Star instances.
        
        Initializes self.stars as a list containing C.STAR_COUNT newly constructed Star objects.
        """
        self.stars = [Star() for _ in range(C.STAR_COUNT)]

    def update(self, dt):
        """
        Advance the animation state of every star by the given time step.
        
        Parameters:
            dt (float): Time elapsed in seconds to apply to each star's update.
        """
        for star in self.stars:
            star.update(dt)

    def draw(self, screen):
        """
        Render every star in this starfield onto the provided surface.
        
        Parameters:
            screen (pygame.Surface): Surface to render the stars onto.
        """
        for star in self.stars:
            star.draw(screen)


class MenuStarfield:
    """Manages animated starfield for menus."""
    def __init__(self, num_stars=150):
        """
        Create an animated starfield used for menus.
        
        Initializes internal animation parameters and populates the star list. Each star is represented as a list [x, y, z, brightness]:
        - x, y: world coordinates centered around the screen center.
        - z: depth (integer between 1 and 8) affecting apparent scale and motion.
        - brightness: float between 100 and 255.
        
        Parameters:
        	num_stars (int): Number of stars to create. For each star, with 70% probability the star is placed in a ring-like distribution at a distance between 50 and SCREEN_WIDTH/2 from the center; otherwise it is placed within 0–50 pixels of the center.
        
        Side effects:
        	Sets these instance attributes: stars, speed, respawn_counter, max_respawns_per_frame, respawn_delay, respawn_delay_max.
        """
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
        """
        Advance the animated menu starfield by dt seconds.
        
        Moves each star radially from the screen center based on its depth and the field's speed, and marks stars that leave a 50-pixel margin for respawn. When the internal respawn delay elapses, one marked star is reinitialized near the center with a new depth and randomized brightness.
        
        Parameters:
            dt (float): Time elapsed since the last update, in seconds.
        """
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
        """
        Render menu starfield onto the provided pygame surface.
        
        Iterates over internally stored stars and projects each star's world position to screen space using a simple depth scale; visible stars are drawn as grayscale filled circles whose size and brightness depend on the star's depth and stored brightness. Faulty star entries (missing/invalid values) are skipped and reported to stdout.
        Parameters:
            screen (pygame.Surface): Surface to draw the starfield on.
        """
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