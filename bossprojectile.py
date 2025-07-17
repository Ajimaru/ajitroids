import pygame
import math
from constants import *
from circleshape import CircleShape

class BossProjectile(CircleShape):
    def __init__(self, x, y, velocity, projectile_type="normal"):
        super().__init__(x, y, BOSS_PROJECTILE_RADIUS)
        self.position = pygame.Vector2(x, y)
        self.velocity = velocity
        self.type = projectile_type
        self.lifetime = 5.0  # Verschwinden nach 5 Sekunden
        self.damage = 1
        
        # Farbe je nach Projektil-Typ
        self.color = BOSS_PROJECTILE_COLORS.get(self.type, BOSS_COLOR)
        
        # Rotation für visuellen Effekt
        self.rotation = 0
        self.rotation_speed = 180  # Grad pro Sekunde
    
    def update(self, dt):
        # Position aktualisieren
        self.position += self.velocity * dt
        
        # Rotation für visuellen Effekt
        self.rotation += self.rotation_speed * dt
        
        # Lebensdauer reduzieren
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
        
        # Bildschirmgrenzen überprüfen
        if (self.position.x < -20 or self.position.x > SCREEN_WIDTH + 20 or
            self.position.y < -20 or self.position.y > SCREEN_HEIGHT + 20):
            self.kill()
    
    def draw(self, screen):
        if self.type == "normal":
            # Einfacher Kreis mit pulsierendem Rand
            pygame.draw.circle(screen, self.color, self.position, self.radius)
            pygame.draw.circle(screen, (255, 255, 255), self.position, self.radius * 0.7, 1)
            
        elif self.type == "homing":
            # Rhombus mit rotierendem Effekt
            points = []
            for i in range(4):
                angle = math.radians(self.rotation + i * 90)
                points.append((
                    self.position.x + math.cos(angle) * self.radius,
                    self.position.y + math.sin(angle) * self.radius
                ))
            pygame.draw.polygon(screen, self.color, points)
            
        elif self.type == "explosive":
            # Kreis mit inneren Ringen
            pygame.draw.circle(screen, self.color, self.position, self.radius)
            pygame.draw.circle(screen, (255, 255, 255), self.position, self.radius * 0.7, 1)
            pygame.draw.circle(screen, (255, 255, 255), self.position, self.radius * 0.4, 1)
            
        else:
            # Fallback: einfacher Kreis
            pygame.draw.circle(screen, self.color, self.position, self.radius)