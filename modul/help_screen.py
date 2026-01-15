"""Help screen showing keyboard shortcuts and game information."""
import pygame
from modul.constants import SCREEN_WIDTH, SCREEN_HEIGHT


class HelpScreen:
    """Display keyboard shortcuts and game help."""

    def __init__(self):
        self.active = False
        self.title_font = pygame.font.Font(None, 64)
        self.section_font = pygame.font.Font(None, 40)
        self.text_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 24)
        
        self.shortcuts = [
            ("GAME CONTROLS", [
                ("Arrow Keys", "Control ship (rotation and thrust)"),
                ("Space", "Shoot / Fire weapon"),
                ("B", "Cycle weapons (when available)"),
                ("ESC", "Pause game / Back"),
            ]),
            ("FUNCTION KEYS", [
                ("F1 / H", "Toggle this help screen"),
                ("F8", "Toggle FPS display"),
                ("F9", "Toggle sound effects"),
                ("F10", "Toggle music"),
                ("F11", "Toggle fullscreen"),
            ]),
        ]
        
        self.background_alpha = 200

    def activate(self):
        """Activate the help screen."""
        self.active = True

    def deactivate(self):
        """Deactivate the help screen."""
        self.active = False

    def toggle(self):
        """Toggle help screen visibility."""
        self.active = not self.active

    def update(self, dt, events):
        """Update help screen state."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_h, pygame.K_F1):
                    self.deactivate()
                    return "close"
        return None

    def draw(self, screen):
        """Draw the help screen."""
        if not self.active:
            return

        # Semi-transparent background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(self.background_alpha)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Title
        title_surface = self.title_font.render("KEYBOARD SHORTCUTS", True, (255, 215, 0))
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH / 2, 60))
        screen.blit(title_surface, title_rect)

        # Draw shortcuts in columns
        y_pos = 140
        x_left = SCREEN_WIDTH / 2 - 350
        
        for section_title, shortcuts in self.shortcuts:
            # Section title
            section_surface = self.section_font.render(section_title, True, (100, 200, 255))
            screen.blit(section_surface, (x_left, y_pos))
            y_pos += 50

            # Shortcuts
            for key, description in shortcuts:
                # Key name (highlighted)
                key_surface = self.text_font.render(key, True, (255, 255, 0))
                screen.blit(key_surface, (x_left + 20, y_pos))
                
                # Description
                desc_surface = self.text_font.render(f"- {description}", True, (200, 200, 200))
                screen.blit(desc_surface, (x_left + 250, y_pos))
                
                y_pos += 35
            
            y_pos += 20

        # Tips section
        y_pos += 10
        tips_title = self.section_font.render("TIPS", True, (100, 200, 255))
        screen.blit(tips_title, (x_left, y_pos))
        y_pos += 50

        tips = [
            "• Collect power-ups from destroyed large asteroids",
            "• Use different weapons for different situations",
            "• Boss fights occur every 10 levels",
            "• Unlock new ships by reaching level 50",
            "• Check achievements menu for special challenges",
        ]
        
        for tip in tips:
            tip_surface = self.text_font.render(tip, True, (180, 180, 180))
            screen.blit(tip_surface, (x_left + 20, y_pos))
            y_pos += 35

        # Footer
        footer_text = "Press ESC, H, or F1 to close"
        footer_surface = self.small_font.render(footer_text, True, (150, 150, 150))
        footer_rect = footer_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 30))
        screen.blit(footer_surface, footer_rect)
