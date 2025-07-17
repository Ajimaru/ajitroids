import random
import math
import pygame
from circleshape import CircleShape
from constants import *
from shot import Shot  # Füge diesen Import hinzu

class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.vertices = self._generate_vertices()
        
    def _generate_vertices(self):
        vertices = []
        for i in range(ASTEROID_VERTICES):
            # Winkel für diesen Vertex
            angle = (i / ASTEROID_VERTICES) * 2 * math.pi
            # Zufällige Abweichung vom Radius
            distance = self.radius * (1 - ASTEROID_IRREGULARITY + 
                                   random.random() * ASTEROID_IRREGULARITY * 2)
            # Position berechnen
            x = math.cos(angle) * distance
            y = math.sin(angle) * distance
            vertices.append((x, y))
        return vertices

    def point_in_polygon(self, point):
        """Alternative Implementierung der Punkt-in-Polygon Prüfung"""
        px, py = point
        vertices = [(self.position.x + vx, self.position.y + vy) 
                    for vx, vy in self.vertices]
        
        crosses = 0
        for i in range(len(vertices)):
            j = (i + 1) % len(vertices)
            
            # Aktuelle und nächste Vertex-Koordinaten
            xi, yi = vertices[i]
            xj, yj = vertices[j]
            
            # Prüfe ob Strahl nach rechts die Linie schneidet
            if ((yi > py) != (yj > py) and
                px < xi + (xj - xi) * (py - yi) / (yj - yi)):
                crosses += 1
        
        return crosses % 2 == 1

    def collides_with(self, other):
        """Verbesserte Kollisionserkennung für Asteroiden."""
        # Erste schnelle Prüfung mit Kreisen
        if (self.position - other.position).length() > (self.radius + other.radius):
            return False
            
        # Falls der andere Gegenstand ein Schuss ist
        if isinstance(other, Shot):
            # Prüfe, ob der Schuss eines der Polygon-Segmente des Asteroiden schneidet
            shot_pos = other.position
            shot_radius = other.radius
            
            # Erstelle die Polygon-Punkte des Asteroiden
            points = [(self.position.x + vx, self.position.y + vy) 
                     for vx, vy in self.vertices]
            
            # Prüfe jeden Abschnitt des Polygons
            for i in range(len(points)):
                j = (i + 1) % len(points)
                
                # Liniensegment
                p1 = pygame.Vector2(points[i])
                p2 = pygame.Vector2(points[j])
                
                # Berechne den kürzesten Abstand vom Punkt zur Linie
                line_vec = p2 - p1
                line_len = line_vec.length()
                if line_len == 0:  # Vermeidet Division durch Null
                    continue
                    
                # Normalisiere den Vektor
                line_vec_normalized = line_vec / line_len
                
                # Vektor vom Linienstartpunkt zum Schuss
                point_vec = shot_pos - p1
                
                # Projiziere den Punkt auf die Linie
                projection = point_vec.dot(line_vec_normalized)
                
                # Begrenze die Projektion auf die Linienlänge
                projection = max(0, min(line_len, projection))
                
                # Finde den nächsten Punkt auf der Linie
                closest_point = p1 + line_vec_normalized * projection
                
                # Prüfe, ob der Abstand kleiner als der Radius des Schusses ist
                if (closest_point - shot_pos).length() <= shot_radius:
                    return True
        
        # Für andere Objekte (z.B. Spieler) oder wenn keine Liniensegmentkollision gefunden wurde
        return super().collides_with(other)

    def draw(self, screen):
        # Transformiere Vertices zur aktuellen Position
        points = [(self.position.x + x, self.position.y + y) 
                 for x, y in self.vertices]
        # Zeichne den unregelmäßigen Asteroiden
        pygame.draw.polygon(screen, "white", points, 2)
        if COLLISION_DEBUG:
            # Zeige Hitbox im Debug-Modus
            pygame.draw.circle(screen, "red", self.position, self.radius, 1)
            for point in [(self.position.x + x, self.position.y + y) 
                         for x, y in self.vertices]:
                pygame.draw.circle(screen, "yellow", point, 2)

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
        new_asteroid1 = Asteroid(self.position.x, self.position.y, new_radius)
        new_asteroid2 = Asteroid(self.position.x, self.position.y, new_radius)
        
        # Setze ihre Geschwindigkeiten
        new_asteroid1.velocity = velocity1
        new_asteroid2.velocity = velocity2

        # Beim Splitten neue Vertices für die kleineren Asteroiden generieren
        new_asteroid1.vertices = new_asteroid1._generate_vertices()
        new_asteroid2.vertices = new_asteroid2._generate_vertices()
