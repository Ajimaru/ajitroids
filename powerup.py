import pygame
import random
import math
from constants import *
from circleshape import CircleShape

class PowerUp(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, POWERUP_RADIUS)
        self.type = random.choice(POWERUP_TYPES)
        self.color = POWERUP_COLORS[self.type]
        self.rotation = 0
        self.velocity = pygame.Vector2(random.uniform(-30, 30), 
                                       random.uniform(-30, 30))
        self.lifetime = POWERUP_LIFETIME  # Timer für Lebensdauer
        
    def update(self, dt):
        self.position += self.velocity * dt
        self.rotation += 90 * dt  # Rotiere für visuellen Effekt
        
        # Lebensdauer reduzieren
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()  # Entferne das Power-up nach Ablauf der Zeit
    
    def draw(self, screen):
        # Äußerer Kreis
        pygame.draw.circle(screen, self.color, self.position, self.radius, 2)
        
        # Symbol je nach Power-up-Typ
        if self.type == "shield":
            # Schild-Symbol (innerer Kreis)
            pygame.draw.circle(screen, self.color, self.position, self.radius * 0.6, 1)
        elif self.type == "triple_shot":
            # Dreifachschuss-Symbol (drei Linien)
            center = pygame.Vector2(self.position)
            angle = self.rotation
            for i in range(3):
                direction = pygame.Vector2(0, 1).rotate(angle + i * 120)
                end_point = center + direction * self.radius * 0.7
                pygame.draw.line(screen, self.color, center, end_point, 2)
        elif self.type == "rapid_fire":
            # Schnellfeuer-Symbol (Blitz)
            points = []
            points.append(self.position + pygame.Vector2(-self.radius * 0.5, -self.radius * 0.7))
            points.append(self.position + pygame.Vector2(0, -self.radius * 0.1))
            points.append(self.position + pygame.Vector2(-self.radius * 0.2, self.radius * 0.1))
            points.append(self.position + pygame.Vector2(self.radius * 0.5, self.radius * 0.7))
            points.append(self.position + pygame.Vector2(0, self.radius * 0.1))
            points.append(self.position + pygame.Vector2(self.radius * 0.2, -self.radius * 0.1))
            pygame.draw.polygon(screen, self.color, points, 1)
        
        # Lebenszeit-Indikator hinzufügen
        remaining_percent = self.lifetime / POWERUP_LIFETIME
        radius_inner = self.radius * 0.3
        start_angle = -90  # Start at top
        end_angle = start_angle + 360 * remaining_percent
        
        # Zeichne Kreisbogen für verbleibende Zeit
        if remaining_percent < 0.25:  # Rot bei wenig Zeit
            time_color = (255, 0, 0)
        else:
            time_color = self.color
            
        if remaining_percent > 0:  # Nur zeichnen wenn noch Zeit übrig
            pygame.draw.arc(screen, time_color,
                          (self.position.x - radius_inner, 
                           self.position.y - radius_inner,
                           radius_inner * 2, radius_inner * 2),
                          math.radians(start_angle), 
                          math.radians(end_angle), 
                          2)