"""Power-up entities and their behaviors."""

import math
import random
import pygame
import modul.constants as C
from modul.circleshape import CircleShape


class PowerUp(CircleShape):
    """Represents a power-up item that can be collected by the player."""
    def __init__(self, x, y, powerup_type=None):
        """
        Create a PowerUp at the given position and initialize its visual and runtime properties.
        
        Parameters:
            x (float): X coordinate of the power-up's center.
            y (float): Y coordinate of the power-up's center.
            powerup_type (str, optional): Specific power-up type (one of C.POWERUP_TYPES). If omitted, a type is chosen at random.
        
        Description:
            Sets the power-up's type and color, initializes rotation to 0, assigns a random velocity with each component in the range [-30, 30], and sets the lifetime to C.POWERUP_LIFETIME.
        """
        super().__init__(x, y, C.POWERUP_RADIUS)
        self.type = powerup_type if powerup_type else random.choice(C.POWERUP_TYPES)
        self.color = C.POWERUP_COLORS[self.type]
        self.rotation = 0
        self.velocity = pygame.Vector2(random.uniform(-30, 30), random.uniform(-30, 30))
        self.lifetime = C.POWERUP_LIFETIME

    def update(self, dt):
        """
        Advance the power-up's state over a time step.
        
        Updates position by moving along the current velocity, increments rotation at 90 degrees per second, decreases remaining lifetime by the elapsed time, and removes the power-up if its lifetime is less than or equal to zero.
        
        Parameters:
            dt (float): Time step in seconds.
        """
        self.position += self.velocity * dt
        self.rotation += 90 * dt

        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()

    def draw(self, screen):
        """
        Render the power-up at its position with a pulsing scale that accelerates as lifetime nears zero and draw type-specific decorative graphics.
        
        The visual pulse increases in frequency when lifetime is less than or equal to 3 seconds. The method draws a base outlined circle scaled by the pulse and additional decorative shapes depending on the power-up type (recognized types: "shield", "triple_shot", "rapid_fire", "laser_weapon", "missile_weapon", "shotgun_weapon").
        
        Parameters:
            screen (pygame.Surface): Surface to draw the power-up onto.
        """
        pulse_scale = 1.0
        if self.lifetime <= 3.0:
            pulse_frequency = 2.0 + (3.0 - self.lifetime) * 2
            pulse_scale = 0.7 + 0.3 * abs(math.sin(pulse_frequency * pygame.time.get_ticks() * 0.001))

        draw_radius = self.radius * pulse_scale
        pygame.draw.circle(screen, self.color, self.position, draw_radius, 2)

        if self.type == "shield":
            pygame.draw.circle(screen, self.color, self.position, draw_radius * 0.6, 1)

        elif self.type == "triple_shot":
            center = pygame.Vector2(self.position)
            for angle in [-30, 0, 30]:
                start_point = center
                angle_offset = angle
                segment_length = draw_radius * 0.15

                for i in range(5):
                    end_point = start_point + pygame.Vector2(0, -segment_length).rotate(angle_offset)
                    pygame.draw.line(screen, self.color, start_point, end_point, 2)
                    angle_offset += 5 if angle < 0 else (-5 if angle > 0 else 0)
                    start_point = end_point

            pygame.draw.circle(screen, self.color, center, draw_radius * 0.2, 1)

        elif self.type == "rapid_fire":
            center = pygame.Vector2(self.position)
            hex_points = []
            for i in range(6):
                angle = math.radians(i * 60)
                hex_points.append(
                    (center.x + math.cos(angle) * draw_radius * 0.25, center.y + math.sin(angle) * draw_radius * 0.25)
                )
            pygame.draw.polygon(screen, self.color, hex_points, 1)

            for angle in [30, 90, 150, 210, 270, 330]:
                points = []
                radius = draw_radius * 0.25
                points.append(center + pygame.Vector2(math.cos(math.radians(angle)), math.sin(math.radians(angle))) * radius)

                zigzag = 15
                distance = draw_radius * 0.6
                segments = 3

                direction = pygame.Vector2(math.cos(math.radians(angle)), math.sin(math.radians(angle)))

                for i in range(segments):
                    offset_angle = angle + (zigzag if i % 2 == 0 else -zigzag)
                    offset_dir = pygame.Vector2(math.cos(math.radians(offset_angle)), math.sin(math.radians(offset_angle)))

                    next_point = points[-1] + offset_dir * (distance / segments)
                    points.append(next_point)

                if len(points) >= 2:
                    for i in range(len(points) - 1):
                        pygame.draw.line(screen, self.color, points[i], points[i + 1], 1)

        elif self.type == "laser_weapon":
            rect = pygame.Rect(
                self.position.x - draw_radius * 0.25, self.position.y - draw_radius * 0.6, draw_radius * 0.5, draw_radius * 1.2
            )
            pygame.draw.rect(screen, self.color, rect, 1)

            for i in range(3):
                y = self.position.y - draw_radius * 0.4 + i * draw_radius * 0.4
                pygame.draw.line(
                    screen, self.color, (self.position.x - draw_radius * 0.25, y), (self.position.x + draw_radius * 0.25, y), 1
                )

            beam_start = self.position - pygame.Vector2(0, draw_radius * 0.6)
            beam_end = beam_start - pygame.Vector2(0, draw_radius * 0.3)
            pygame.draw.line(screen, self.color, beam_start, beam_end, 3)

        elif self.type == "missile_weapon":
            pygame.draw.line(
                screen,
                self.color,
                self.position - pygame.Vector2(0, draw_radius * 0.3),
                self.position + pygame.Vector2(0, draw_radius * 0.5),
                2,
            )

            head_points = []
            head_points.append(self.position - pygame.Vector2(0, draw_radius * 0.6))
            head_points.append(self.position - pygame.Vector2(draw_radius * 0.3, draw_radius * 0.3))
            head_points.append(self.position - pygame.Vector2(-draw_radius * 0.3, draw_radius * 0.3))
            pygame.draw.polygon(screen, self.color, head_points, 1)

            wing_l = []
            wing_l.append(self.position + pygame.Vector2(-draw_radius * 0.1, 0))
            wing_l.append(self.position + pygame.Vector2(-draw_radius * 0.4, draw_radius * 0.3))
            wing_l.append(self.position + pygame.Vector2(-draw_radius * 0.1, draw_radius * 0.3))
            pygame.draw.polygon(screen, self.color, wing_l, 1)

            wing_r = []
            wing_r.append(self.position + pygame.Vector2(draw_radius * 0.1, 0))
            wing_r.append(self.position + pygame.Vector2(draw_radius * 0.4, draw_radius * 0.3))
            wing_r.append(self.position + pygame.Vector2(draw_radius * 0.1, draw_radius * 0.3))
            pygame.draw.polygon(screen, self.color, wing_r, 1)

        elif self.type == "shotgun_weapon":
            center = pygame.Vector2(self.position)

            pygame.draw.line(screen, self.color, center, center - pygame.Vector2(0, draw_radius * 0.6), 2)

            for angle in [-30, 0, 30]:
                start = center - pygame.Vector2(0, draw_radius * 0.4)
                direction = pygame.Vector2(0, -1).rotate(angle)
                end = start + direction * draw_radius * 0.4
                pygame.draw.line(screen, self.color, start, end, 2)