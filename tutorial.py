import pygame
import math
from constants import *
try:
    from starfield import MenuStarfield
except ImportError:
    MenuStarfield = None

class Tutorial:
    def __init__(self):
        self.pages = [
            {
                "title": "Grundlagen",
                "content": [
                    "Bewege dein Raumschiff mit den Pfeiltasten",
                    "Schieße mit der Leertaste",
                    "Drehe dich mit Links/Rechts-Pfeiltasten", 
                    "Bewege dich vor/zurück mit Hoch/Runter-Pfeiltasten",
                    "Zerstöre Asteroiden für Punkte!",
                    "",
                    "Große Asteroiden zerfallen in kleinere Teile",
                    "Sammle PowerUps für spezielle Fähigkeiten"
                ]
            },
            {
                "title": "PowerUps",
                "content": [
                    "[SCHILD] - Schutz vor einem Treffer (3 Sek.)",
                    "[3-SHOT] - Drei Schüsse gleichzeitig",
                    "[SPEED] - Erhöhte Feuerrate",
                    "[LASER] - Durchdringt mehrere Asteroiden",
                    "[ROCKET] - Verfolgen nahe Asteroiden",
                    "[SHOTGUN] - Mehrere Schüsse in einem Winkel",
                    "",
                    "PowerUps erscheinen nur von großen Asteroiden!",
                    "Sie verschwinden nach 10 Sekunden"
                ]
            },
            {
                "title": "Level-System",
                "content": [
                    "Sammle 2500 Punkte für ein Level-Up",
                    "Höhere Level = mehr und schnellere Asteroiden",
                    "Maximales Level: 999",
                    "",
                    "*** BOSS-KÄMPFE ***",
                    "Alle 10 Level erscheint ein Boss!",
                    "Bosse haben viel Gesundheit und Angriffsmuster",
                    "Belohnung: +1 Leben und 500 Punkte",
                    "",
                    "Bosse werden mit jedem Level stärker!"
                ]
            },
            {
                "title": "Waffen-System",
                "content": [
                    "STANDARD: Unbegrenzte Munition",
                    "LASER: 15 Schuss, durchdringt Asteroiden",
                    "RAKETEN: 8 Schuss, verfolgen Ziele automatisch",
                    "SCHROTFLINTE: 12 Schuss, Streufeuer",
                    "",
                    "Munition wird im HUD angezeigt",
                    "Sammle die gleiche Waffe für mehr Munition",
                    "Waffen wechseln automatisch zurück zur Standard-Waffe"
                ]
            },
            {
                "title": "Boss-Kampf Strategien",
                "content": [
                    "*** Boss-Verhalten ***",
                    "• Bewegt sich in verschiedenen Phasen",
                    "• Wechselt zwischen Angriffsmuster",
                    "• Wird mit höherem Level gefährlicher",
                    "",
                    "### Tipps ###",
                    "• Nutze Bewegung um Projektilen auszuweichen",
                    "• Sammle PowerUps vor dem Boss-Kampf",
                    "• Konzentriere dich auf den Boss-Kern",
                    "• Die Gesundheitsleiste zeigt den Fortschritt"
                ]
            },
            {
                "title": "Erweiterte Tipps",
                "content": [
                    "*** Steuerung ***",
                    "• ESC für Pause",
                    "• F11 für Vollbild",
                    "• Pfeiltasten für Bewegung",
                    "• Leertaste zum Schießen",
                    "",
                    "*** Strategie ***",
                    "• Große Asteroiden geben mehr Punkte",
                    "• PowerUPs pulsieren in den letzten 3 Sekunden",
                    "• Unverwundbarkeit nach Respawn nutzen",
                    "• Boss-Kämpfe sind optional - aber lohnend!"
                ]
            },
            {
                "title": "Schwierigkeitsgrade",
                "content": [
                    "[LEICHT]:",
                    "• Langsamere Asteroiden",
                    "• Weniger Asteroiden pro Level",
                    "• Mehr PowerUp-Chancen",
                    "",
                    "[NORMAL]:",
                    "• Ausgewogenes Gameplay",
                    "• Standard-Einstellungen",
                    "",
                    "[SCHWER]:",
                    "• Schnellere Asteroiden",
                    "• Mehr Asteroiden pro Level",
                    "• Weniger PowerUp-Chancen",
                    "• Härtere Boss-Kämpfe"
                ]
            }
        ]
        
        self.current_page = 0
        self.transitioning = False
        self.transition_timer = 0
        self.transition_duration = 0.3
        
        # Schriftarten
        self.font_title = pygame.font.Font(None, 48)
        self.font_content = pygame.font.Font(None, 28)
        self.font_navigation = pygame.font.Font(None, 24)
        
        # NEU: Starfield für Hintergrund hinzufügen
        try:
            from starfield import MenuStarfield
            self.starfield = MenuStarfield(num_stars=80)
        except ImportError:
            self.starfield = None
            print("Starfield konnte nicht importiert werden")

    def next_page(self):
        """Wechselt zur nächsten Seite"""
        if self.current_page < len(self.pages) - 1:
            self.start_transition(self.current_page + 1)
    
    def previous_page(self):
        """Wechselt zur vorherigen Seite"""
        if self.current_page > 0:
            self.start_transition(self.current_page - 1)
    
    def start_transition(self, target_page):
        """Startet eine animierte Transition zur Zielseite"""
        self.transitioning = True
        self.target_page = target_page
        self.transition_timer = 0
    
    def update(self, dt, events):
        # Starfield aktualisieren
        if hasattr(self, 'starfield') and self.starfield:
            self.starfield.update(dt)
        
        # Transition-Animation
        if self.transitioning:
            self.transition_timer += dt
            if self.transition_timer >= self.transition_duration:
                self.transitioning = False
                self.current_page = self.target_page
                self.transition_timer = 0
                return None
    
        # Event-Handling
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                    return "back"
                
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    if not self.transitioning:
                        self.previous_page()
                
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    if not self.transitioning:
                        self.next_page()
        
        return None
    
    def draw(self, screen):
        # Schwarzer Hintergrund
        screen.fill((0, 0, 0))
        
        # NEU: Starfield zeichnen (falls vorhanden)
        if hasattr(self, 'starfield') and self.starfield:
            self.starfield.draw(screen)
        
        # Transition-Effekt
        alpha = 255
        if self.transitioning:
            progress = self.transition_timer / self.transition_duration
            alpha = int(255 * (1 - abs(progress - 0.5) * 2))
        
        # Aktueller Content
        page = self.pages[self.current_page]
        y_offset = 80
        
        # Titel
        title_color = (100, 200, 255) if alpha == 255 else (100, 200, 255, alpha)
        title_surface = self.font_title.render(page["title"], True, title_color)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH/2, y_offset))
        
        if alpha < 255:
            title_surface.set_alpha(alpha)
        screen.blit(title_surface, title_rect)
        
        y_offset += 80
        
        # Content - VERWENDE draw_colored_line() für PowerUps, Waffen UND Schwierigkeitsgrade
        for line in page["content"]:
            if line == "":
                y_offset += 15
                continue
            
            # Prüfe ob es sich um PowerUp-, Waffen- oder Schwierigkeitsgrad-Zeilen handelt
            if ((line.startswith("[") and "]" in line) or 
                (":" in line and any(weapon in line for weapon in ["STANDARD", "LASER", "RAKETEN", "SCHROTFLINTE"]))):
                # Verwende die spezielle Färbungs-Methode
                self.draw_colored_line(screen, line, SCREEN_WIDTH//2, y_offset)
            else:
                # Normale Zeilen mit einfacher Formatierung
                color = (255, 255, 255)  # Standard weiß
                
                # Boss-bezogene Hervorhebungen
                if line.startswith("*** BOSS-KÄMPFE ***") or line.startswith("*** Boss-Verhalten ***"):
                    color = (128, 0, 128)  # Lila - wie Boss-Farbe
                elif line.startswith("### Tipps ###"):
                    color = (255, 215, 0)  # Gold für wichtige Tipps
                elif line.startswith("*** Steuerung ***") or line.startswith("*** Strategie ***"):
                    color = (100, 200, 255)  # Hellblau für Kategorien
                
                # Unterpunkte
                elif line.startswith("•"):
                    color = (200, 200, 200)  # Grau für Unterpunkte
                
                content_surface = self.font_content.render(line, True, color)
                if alpha < 255:
                    content_surface.set_alpha(alpha)
                    
                content_rect = content_surface.get_rect(center=(SCREEN_WIDTH/2, y_offset))
                screen.blit(content_surface, content_rect)
            
            y_offset += 35
        
        # Navigation
        nav_y = SCREEN_HEIGHT - 80
        
        # Seitenanzeige
        page_info = f"Seite {self.current_page + 1} von {len(self.pages)}"
        page_surface = self.font_navigation.render(page_info, True, (150, 150, 150))
        page_rect = page_surface.get_rect(center=(SCREEN_WIDTH/2, nav_y))
        screen.blit(page_surface, page_rect)
        
        # Navigation-Hinweise
        nav_text = "← A/D/Pfeiltasten zum Navigieren →    ESC/Leertaste: Zurück"
        nav_surface = self.font_navigation.render(nav_text, True, (100, 100, 100))
        nav_rect = nav_surface.get_rect(center=(SCREEN_WIDTH/2, nav_y + 30))
        screen.blit(nav_surface, nav_rect)
        
        # Fortschrittsbalken
        progress_width = 300
        progress_height = 4
        progress_x = (SCREEN_WIDTH - progress_width) // 2
        progress_y = nav_y - 30
        
        # Hintergrund des Fortschrittsbalkens
        pygame.draw.rect(screen, (50, 50, 50), 
                        (progress_x, progress_y, progress_width, progress_height))
        
        # Aktueller Fortschritt
        current_progress = (self.current_page + 1) / len(self.pages)
        progress_fill_width = int(progress_width * current_progress)
        pygame.draw.rect(screen, (100, 200, 255), 
                        (progress_x, progress_y, progress_fill_width, progress_height))
    
    def draw_colored_line(self, screen, line, x, y):
        """Zeichnet eine Zeile mit farbigem Name-Teil und weißem Beschreibungs-Teil"""
        
        # PowerUp-Namen extrahieren und färben
        if line.startswith("[") and "]" in line:
            bracket_end = line.find("]") + 1
            name_part = line[:bracket_end]
            desc_part = line[bracket_end:]
            
            # Name-Farbe bestimmen
            name_color = (255, 255, 255)  # Standard
            if "[SCHILD]" in name_part:
                name_color = (0, 255, 255)
            elif "[LASER]" in name_part:
                name_color = (0, 255, 0)
            elif "[ROCKET]" in name_part:
                name_color = (255, 0, 0)
            elif "[SHOTGUN]" in name_part:
                name_color = (255, 165, 0)
            elif "[3-SHOT]" in name_part or "[SPEED]" in name_part:
                name_color = (255, 255, 0)
            # NEU: Schwierigkeitsgrade hinzufügen
            elif "[LEICHT]" in name_part:
                name_color = (0, 255, 0)  # Grün
            elif "[NORMAL]" in name_part:
                name_color = (255, 255, 0)  # Gelb
            elif "[SCHWER]" in name_part:
                name_color = (255, 0, 0)  # Rot
            
            # Name zeichnen
            name_surface = self.font_content.render(name_part, True, name_color)
            name_width = name_surface.get_width()
            
            # Beschreibung zeichnen (weiß)
            desc_surface = self.font_content.render(desc_part, True, (255, 255, 255))
            
            # Beide Teile zentriert zeichnen
            total_width = name_width + desc_surface.get_width()
            start_x = x - total_width // 2
            
            screen.blit(name_surface, (start_x, y))
            screen.blit(desc_surface, (start_x + name_width, y))

        # Waffen-Namen (mit Doppelpunkt) 
        elif ":" in line:
            colon_pos = line.find(":") + 1
            name_part = line[:colon_pos]
            desc_part = line[colon_pos:]
            
            # Waffen-Farbe bestimmen
            name_color = (255, 255, 255)  # Standard
            if "STANDARD:" in name_part:
                name_color = (255, 255, 255)
            elif "LASER:" in name_part:
                name_color = (0, 255, 0)
            elif "RAKETEN:" in name_part:
                name_color = (255, 0, 0)
            elif "SCHROTFLINTE:" in name_part:
                name_color = (255, 165, 0)
            
            # Name zeichnen
            name_surface = self.font_content.render(name_part, True, name_color)
            name_width = name_surface.get_width()
            
            # Beschreibung zeichnen (weiß)
            desc_surface = self.font_content.render(desc_part, True, (255, 255, 255))
            
            # Beide Teile zentriert zeichnen
            total_width = name_width + desc_surface.get_width()
            start_x = x - total_width // 2
            
            screen.blit(name_surface, (start_x, y))
            screen.blit(desc_surface, (start_x + name_width, y))
            
        else:
            # Normale Zeile
            content_surface = self.font_content.render(line, True, (255, 255, 255))
            content_rect = content_surface.get_rect(center=(x, y))
            screen.blit(content_surface, content_rect)