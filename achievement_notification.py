import pygame
import time
from constants import *

class AchievementNotification:
    def __init__(self, achievement_name, achievement_description):
        self.name = achievement_name
        self.description = achievement_description
        self.display_time = 4.0  # 4 Sekunden anzeigen
        self.fade_time = 1.0     # 1 Sekunde zum Ein-/Ausblenden
        self.start_time = time.time()
        self.animation_progress = 0.0
        self.is_fading_out = False
        
        # Position und Animation
        self.target_x = SCREEN_WIDTH - 350  # Rechts auf dem Bildschirm
        self.target_y = 80                   # Oben rechts
        self.current_x = SCREEN_WIDTH       # Startet außerhalb des Bildschirms
        self.current_y = self.target_y
        
        # Schriftarten
        self.title_font = pygame.font.Font(None, 32)
        self.desc_font = pygame.font.Font(None, 20)
        
        # Sound-Effekt (wird später von außen gesetzt)
        self.sound_played = False
        
    def update(self, dt):
        """Aktualisiert die Animation der Benachrichtigung"""
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        # Verschiedene Phasen der Animation
        if elapsed < self.fade_time:
            # Einblenden und hereinrutschen
            self.animation_progress = elapsed / self.fade_time
            self.current_x = SCREEN_WIDTH - (SCREEN_WIDTH - self.target_x) * self._ease_out(self.animation_progress)
            
        elif elapsed < self.display_time - self.fade_time:
            # Vollständig sichtbar
            self.animation_progress = 1.0
            self.current_x = self.target_x
            
        elif elapsed < self.display_time:
            # Ausblenden
            if not self.is_fading_out:
                self.is_fading_out = True
            fade_progress = (elapsed - (self.display_time - self.fade_time)) / self.fade_time
            self.animation_progress = 1.0 - fade_progress
            self.current_x = self.target_x + (SCREEN_WIDTH - self.target_x) * fade_progress
            
        else:
            # Animation beendet
            return False
            
        return True
    
    def _ease_out(self, t):
        """Easing-Funktion für sanfte Animation"""
        return 1 - (1 - t) ** 3
    
    def draw(self, screen):
        """Zeichnet die Achievement-Benachrichtigung"""
        if self.animation_progress <= 0:
            return
            
        # Hintergrund-Rechteck mit Transparenz
        notification_width = 320
        notification_height = 80
        
        # Alpha-Wert basierend auf Animation
        alpha = int(255 * self.animation_progress)
        
        # Hintergrund erstellen
        bg_surface = pygame.Surface((notification_width, notification_height), pygame.SRCALPHA)
        
        # Gradient-Hintergrund (dunkel nach hell)
        for i in range(notification_height):
            gradient_alpha = int(alpha * 0.9 * (1 - i / notification_height * 0.3))
            color = (20, 20, 60, gradient_alpha)
            pygame.draw.rect(bg_surface, color, (0, i, notification_width, 1))
        
        # Goldener Rand für Achievement
        border_color = (255, 215, 0, alpha)  # Gold
        pygame.draw.rect(bg_surface, border_color, (0, 0, notification_width, notification_height), 3)
        
        # Position berechnen
        rect_x = int(self.current_x)
        rect_y = int(self.current_y)
        
        # Hintergrund zeichnen
        screen.blit(bg_surface, (rect_x, rect_y))
        
        # "ACHIEVEMENT UNLOCKED!" Text
        header_color = (255, 215, 0, alpha)  # Gold
        header_text = "ACHIEVEMENT UNLOCKED!"
        header_surf = self.title_font.render(header_text, True, header_color)
        header_rect = header_surf.get_rect(center=(rect_x + notification_width // 2, rect_y + 20))
        
        # Text mit Alpha rendern
        if alpha < 255:
            header_surf.set_alpha(alpha)
        screen.blit(header_surf, header_rect)
        
        # Achievement-Name
        name_color = (255, 255, 255, alpha)  # Weiß
        name_surf = self.desc_font.render(self.name, True, name_color)
        name_rect = name_surf.get_rect(center=(rect_x + notification_width // 2, rect_y + 45))
        
        if alpha < 255:
            name_surf.set_alpha(alpha)
        screen.blit(name_surf, name_rect)
        
        # Achievement-Beschreibung (gekürzt falls zu lang)
        desc_text = self.description
        if len(desc_text) > 35:
            desc_text = desc_text[:32] + "..."
            
        desc_color = (200, 200, 200, alpha)  # Hellgrau
        desc_surf = self.desc_font.render(desc_text, True, desc_color)
        desc_rect = desc_surf.get_rect(center=(rect_x + notification_width // 2, rect_y + 65))
        
        if alpha < 255:
            desc_surf.set_alpha(alpha)
        screen.blit(desc_surf, desc_rect)


class AchievementNotificationManager:
    def __init__(self, sounds=None):
        self.notifications = []
        self.max_notifications = 3  # Maximal 3 Benachrichtigungen gleichzeitig
        self.sounds = sounds
    
    def set_sounds(self, sounds):
        """Setzt das Sounds-Objekt"""
        self.sounds = sounds
        
    def add_notification(self, achievement_name, achievement_description):
        """Fügt eine neue Achievement-Benachrichtigung hinzu"""
        # Prüfen ob bereits eine Benachrichtigung für dieses Achievement existiert
        for notification in self.notifications:
            if notification.name == achievement_name:
                return  # Keine Duplikate
        
        # Neue Benachrichtigung erstellen
        notification = AchievementNotification(achievement_name, achievement_description)
        
        # Position anpassen wenn mehrere Benachrichtigungen da sind
        notification.target_y = 80 + len(self.notifications) * 90
        notification.current_y = notification.target_y
        
        self.notifications.append(notification)
        
        # Achievement-Sound abspielen
        if self.sounds and hasattr(self.sounds, 'play_achievement'):
            self.sounds.play_achievement()
        
        # Zu alte Benachrichtigungen entfernen
        if len(self.notifications) > self.max_notifications:
            self.notifications.pop(0)
            
        print(f"Achievement-Benachrichtigung hinzugefügt: {achievement_name}")
    
    def update(self, dt):
        """Aktualisiert alle aktiven Benachrichtigungen"""
        # Benachrichtigungen aktualisieren und abgelaufene entfernen
        self.notifications = [
            notification for notification in self.notifications 
            if notification.update(dt)
        ]
        
        # Positionen neu anordnen
        for i, notification in enumerate(self.notifications):
            target_y = 80 + i * 90
            notification.target_y = target_y
            # Sanfte Bewegung zur neuen Position
            notification.current_y += (target_y - notification.current_y) * dt * 5
    
    def draw(self, screen):
        """Zeichnet alle aktiven Benachrichtigungen"""
        for notification in self.notifications:
            notification.draw(screen)
    
    def clear_all(self):
        """Entfernt alle Benachrichtigungen"""
        self.notifications.clear()
