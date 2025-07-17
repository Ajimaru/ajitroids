import random
import pygame
from circleshape import CircleShape
from constants import *

class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)

    def draw(self, screen):
        pygame.draw.circle(screen, "white", self.position, self.radius, 2)

    def update(self, dt):
        self.position += self.velocity * dt

    def split(self):
        self.kill()  # Zerstöre den aktuellen Asteroiden
        
        # Wenn der Asteroid zu klein ist, nicht weiter aufteilen
        if self.radius <= ASTEROID_MIN_RADIUS:
            return
            
        # Berechne den neuen Radius für die kleineren Asteroiden
        new_radius = self.radius - ASTEROID_MIN_RADIUS
        
        # Generiere zufälligen Winkel zwischen 20 und 50 Grad
        random_angle = random.uniform(20, 50)
        
        # Erstelle zwei neue Geschwindigkeitsvektoren
        velocity1 = self.velocity.rotate(random_angle) * 1.2
        velocity2 = self.velocity.rotate(-random_angle) * 1.2
        
        # Erstelle die neuen Asteroiden
        asteroid1 = Asteroid(self.position.x, self.position.y, new_radius)
        asteroid2 = Asteroid(self.position.x, self.position.y, new_radius)
        
        # Setze ihre Geschwindigkeiten
        asteroid1.velocity = velocity1
        asteroid2.velocity = velocity2
