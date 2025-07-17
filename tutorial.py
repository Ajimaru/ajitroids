import pygame
import math
from constants import *

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
                    "🔵 Schild - Schutz vor einem Treffer (3 Sek.)",
                    "🟣 Dreifachschuss - Drei Schüsse gleichzeitig",
                    "🟡 Schnellfeuer - Erhöhte Feuerrate",
                    "🟢 Laser - Durchdringt mehrere Asteroiden",
                    "🔴 Raketen - Verfolgen nahe Asteroiden",
                    "🟠 Schrotflinte - Mehrere Schüsse in einem Winkel",
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
                    "🎯 BOSS-KÄMPFE:",
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
                    "🔸 Standard: Unbegrenzte Munition",
                    "🟢 Laser: 15 Schuss, durchdringt Asteroiden",
                    "🔴 Raketen: 8 Schuss, verfolgen Ziele automatisch",
                    "🟠 Schrotflinte: 12 Schuss, Streufeuer",
                    "",
                    "Munition wird im HUD angezeigt",
                    "Sammle die gleiche Waffe für mehr Munition",
                    "Wechsle mit Q/E zwischen Waffen"
                ]
            },
            {
                "title": "Boss-Kampf Strategien",
                "content": [
                    "🎯 Boss-Verhalten:",
                    "• Bewegt sich in verschiedenen Phasen",
                    "• Wechselt zwischen Angriffsmuster",
                    "• Wird mit höherem Level gefährlicher",
                    "",
                    "💡 Tipps:",
                    "• Nutze Bewegung um Projektilen auszuweichen",
                    "• Sammle PowerUps vor dem Boss-Kampf",
                    "• Konzentriere dich auf den Boss-Kern",
                    "• Die Gesundheitsleiste zeigt den Fortschritt"
                ]
            },
            {
                "title": "Erweiterte Tipps",
                "content": [
                    "🎮 Steuerung:",
                    "• ESC für Pause",
                    "• F11 für Vollbild",
                    "• Q/E zum Waffenwechsel",
                    "",
                    "🎯 Strategie:",
                    "• Große Asteroiden geben mehr Punkte",
                    "• PowerUPs pulsieren in den letzten 3 Sekunden",
                    "• Unverwundbarkeit nach Respawn nutzen",
                    "• Boss-Kämpfe sind optional - aber lohnend!"
                ]
            },
            {
                "title": "Schwierigkeitsgrade",
                "content": [
                    "🟢 Leicht:",
                    "• Langsamere Asteroiden",
                    "• Weniger Asteroiden pro Level",
                    "• Mehr PowerUp-Chancen",
                    "",
                    "🟡 Normal:",
                    "• Ausgewogenes Gameplay",
                    "• Standard-Einstellungen",
                    "",
                    "🔴 Schwer:",
                    "• Schnellere Asteroiden",
                    "• Mehr Asteroiden pro Level",
                    "• Weniger PowerUp-Chancen",
                    "• Härtere Boss-Kämpfe"
                ]
            }
        ]
        
        self.current_page = 0
        self.font_title = pygame.font.Font(None, 48)
        self.font_content = pygame.font.Font(None, 28)
        self.font_navigation = pygame.font.Font(None, 24)
        
        # Animation für Seitenwechsel
        self.transition_timer = 0
        self.transition_duration = 0.3
        self.transitioning = False
        self.next_page = 0
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                if self.current_page < len(self.pages) - 1:
                    self.start_transition(self.current_page + 1)
                    return None
                    
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                if self.current_page > 0:
                    self.start_transition(self.current_page - 1)
                    return None
                    
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                return "main_menu"
                
        return None
    
    def start_transition(self, target_page):
        """Startet eine animierte Transition zur Zielseite"""
        self.transitioning = True
        self.next_page = target_page
        self.transition_timer = 0
    
    def update(self, dt):
        if self.transitioning:
            self.transition_timer += dt
            if self.transition_timer >= self.transition_duration:
                self.current_page = self.next_page
                self.transitioning = False
                self.transition_timer = 0
    
    def draw(self, screen):
        # Hintergrund
        screen.fill((10, 10, 30))
        
        # Sterne im Hintergrund
        for i in range(50):
            x = (i * 137) % SCREEN_WIDTH
            y = (i * 197) % SCREEN_HEIGHT
            brightness = 50 + (i * 31) % 100
            pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), 1)
        
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
        
        # Content
        for line in page["content"]:
            if line == "":
                y_offset += 15
                continue
                
            # Spezielle Formatierung für verschiedene Arten von Zeilen
            color = (255, 255, 255)
            if line.startswith("🎯") or line.startswith("💡"):
                color = (255, 215, 0)  # Gold für wichtige Hinweise
            elif line.startswith("•"):
                color = (200, 200, 200)  # Grau für Unterpunkte
            elif any(line.startswith(emoji) for emoji in ["🔵", "🟣", "🟡", "🟢", "🔴", "🟠"]):
                color = (150, 255, 150)  # Hellgrün für PowerUps
            elif line.startswith("🟢") or line.startswith("🟡") or line.startswith("🔴"):
                color = (255, 200, 100)  # Orange für Schwierigkeitsgrade
                
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