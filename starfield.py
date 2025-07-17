import random
import pygame
import math  # Für die Schweif-Berechnung
from constants import *

class Star:
    def __init__(self):
        self.position = pygame.Vector2(
            random.randint(0, SCREEN_WIDTH),
            random.randint(0, SCREEN_HEIGHT)
        )
        self.size = random.choice(STAR_SIZES)
        self.color = random.choice(STAR_COLORS)
        self.twinkle_timer = random.random() * 2 * math.pi  # Zufällige Startphase

    def update(self, dt):
        self.twinkle_timer += dt
        # Helligkeit variiert mit Sinus für Glitzereffekt
        brightness = abs(math.sin(self.twinkle_timer))
        self.current_color = [int(c * brightness) for c in pygame.Color(self.color)]

    def draw(self, screen):
        pygame.draw.circle(screen, self.current_color, self.position, self.size)

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
    def __init__(self, num_stars=150):  # Reduzierte Anzahl auf 150
        self.stars = []
        self.speed = 0.4  # Leicht reduzierte Basisgeschwindigkeit
        self.respawn_counter = 0
        self.max_respawns_per_frame = 1  # Nur 1 neuer Stern pro Frame
        self.respawn_delay = 0  # Verzögerung zwischen Respawns
        self.respawn_delay_max = 0.2  # Sekunden zwischen Respawns
        
        # Sterne gleichmäßiger im Raum verteilen
        for _ in range(num_stars):
            # Noch breitere Anfangsverteilung
            if random.random() < 0.7:  # 70% der Sterne weiter außen platzieren
                # Weiter außen platzieren
                distance = random.uniform(50, SCREEN_WIDTH / 2)
                angle = random.random() * 2 * math.pi
                x = SCREEN_WIDTH / 2 + math.cos(angle) * distance
                y = SCREEN_HEIGHT / 2 + math.sin(angle) * distance
            else:
                # Rest näher zur Mitte
                distance = random.random() * 50
                angle = random.random() * 2 * math.pi
                x = SCREEN_WIDTH / 2 + math.cos(angle) * distance
                y = SCREEN_HEIGHT / 2 + math.sin(angle) * distance
                
            z = random.randint(1, 8)  # Tiefe
            brightness = random.uniform(100, 255)  # Helligkeit hinzufügen
            self.stars.append([x, y, z, brightness])  # 4 Werte statt 3
    
    def update(self, dt):
        center_x = SCREEN_WIDTH / 2
        center_y = SCREEN_HEIGHT / 2
        
        stars_to_respawn = []
        
        for star in self.stars:
            # Vektor vom Zentrum zum Stern
            dx = star[0] - center_x
            dy = star[1] - center_y
            
            # Geschwindigkeit basierend auf Tiefe
            speed_factor = (star[2] / 2) * self.speed * dt * 60
            
            # Bewegung
            star[0] += dx * speed_factor * 0.01
            star[1] += dy * speed_factor * 0.01
            
            # Außerhalb des Bildschirms?
            if (star[0] < -50 or star[0] > SCREEN_WIDTH + 50 or 
                star[1] < -50 or star[1] > SCREEN_HEIGHT + 50):
                stars_to_respawn.append(star)
        
        # Verzögerte Respawn-Logik
        self.respawn_delay -= dt
        if self.respawn_delay <= 0 and stars_to_respawn:
            self.respawn_delay = self.respawn_delay_max
            
            # Nur ein Stern pro Zeiteinheit
            star = stars_to_respawn.pop(0)
            
            # Variierter Respawn-Punkt näher zur Mitte
            angle = random.random() * 2 * math.pi
            distance = random.uniform(5, 15)
            star[0] = center_x + math.cos(angle) * distance
            star[1] = center_y + math.sin(angle) * distance
            star[2] = random.randint(1, 8)
            if len(star) >= 4:  # Wenn Helligkeit vorhanden
                star[3] = random.uniform(100, 255)
    
    def draw(self, screen):
        """Zeichnet alle Sterne"""
        for star in self.stars:
            try:
                # Sichere Extraktion der Stern-Daten
                if len(star) >= 4:
                    x, y, z, brightness = star[0], star[1], star[2], star[3]
                    
                    # Prüfe, ob alle Werte Zahlen sind
                    if not all(isinstance(val, (int, float)) for val in [x, y, z, brightness]):
                        continue
                    
                    # Perspektive berechnen
                    scale = 200 / (z + 200)
                    screen_x = SCREEN_WIDTH / 2 + (x - SCREEN_WIDTH / 2) * scale
                    screen_y = SCREEN_HEIGHT / 2 + (y - SCREEN_HEIGHT / 2) * scale
                    
                    # Stern-Größe basierend auf Entfernung
                    size = max(1, int(3 * scale))
                    
                    # Farbe basierend auf Helligkeit und Entfernung
                    color_value = min(255, int(brightness * scale))
                    color = (color_value, color_value, color_value)
                    
                    # Prüfe, ob die Koordinaten gültig sind
                    if (0 <= screen_x < SCREEN_WIDTH and 
                        0 <= screen_y < SCREEN_HEIGHT and
                        isinstance(screen_x, (int, float)) and 
                        isinstance(screen_y, (int, float))):
                        
                        pygame.draw.circle(screen, color, 
                                         (int(screen_x), int(screen_y)), 
                                         max(1, size))
                    
            except (IndexError, TypeError, ValueError) as e:
                # Fehlerhafte Stern-Daten überspringen
                print(f"Fehlerhafter Stern übersprungen: {star}, Fehler: {e}")
                continue