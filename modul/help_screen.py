"""Help screen showing keyboard shortcuts and game information."""
import pygame

from modul.constants import SCREEN_HEIGHT, SCREEN_WIDTH


# Module-level optional runtime helpers to satisfy linters (C0415)
try:
    from modul import input_utils  # type: ignore
except Exception:  # pragma: no cover - provide minimal stub for tests
    class _InputUtilsStub:
        @staticmethod
        def get_action_keycode(name):
            return None

    input_utils = _InputUtilsStub()

try:
    from modul.i18n import gettext  # type: ignore
except Exception:  # pragma: no cover - fallback for tests
    def gettext(k):
        return k


class HelpScreen:
    """Display keyboard shortcuts and game help."""

    def __init__(self):
        """TODO: add docstring."""
        self.active = False

        # Fonts are initialized lazily to avoid crashes when HelpScreen is
        # created before pygame/font initialization (e.g., during tests).
        self.title_font = None
        self.section_font = None
        self.text_font = None
        self.small_font = None

        self.shortcuts = [
            ("GAME CONTROLS", [
                ("arrow_keys", "desc_control_ship"),
                ("space", "desc_shoot"),
                ("b", "desc_cycle_weapons"),
                ("r", "desc_quick_restart"),
                ("esc", "desc_pause_back"),
            ]),
            ("FUNCTION KEYS", [
                ("f1_h", "desc_f1_help"),
                ("f8", "desc_f8"),
                ("f9", "desc_f9"),
                ("f10", "desc_f10"),
                ("f11", "desc_f11"),
            ]),
        ]

        self.background_alpha = 200

    def _ensure_fonts(self):
        """TODO: add docstring."""
        if not pygame.font.get_init():
            pygame.font.init()
        if self.title_font is None:
            self.title_font = pygame.font.Font(None, 64)
            self.section_font = pygame.font.Font(None, 40)
            self.text_font = pygame.font.Font(None, 28)
            self.small_font = pygame.font.Font(None, 24)

    def activate(self):
        """Activate the help screen."""
        self._ensure_fonts()
        self.active = True

    def toggle(self):
        """Toggle help screen visibility."""
        if not self.active:
            self._ensure_fonts()
        self.active = not self.active

    def deactivate(self):
        """Deactivate the help screen."""
        self.active = False

    def update(self, dt, events):
        """Update help screen state."""
        if self.active:
            self._ensure_fonts()

        for event in events:
            if event.type == pygame.KEYDOWN:
                pause_key = input_utils.get_action_keycode("pause")
                if ((pause_key is not None and event.key == pause_key)
                        or event.key in (pygame.K_h, pygame.K_F1, pygame.K_ESCAPE)):
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
        title_label = gettext("help").upper()
        title_surface = self.title_font.render(title_label, True, (255, 215, 0))
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH / 2, 60))
        screen.blit(title_surface, title_rect)

        # Draw shortcuts in columns
        y_pos = 140
        x_left = SCREEN_WIDTH / 2 - 350

        for section_title, shortcuts in self.shortcuts:
            # Section title
            section_surface = self.section_font.render(gettext(section_title.lower().replace(' ', '_')), True, (100, 200, 255))
            screen.blit(section_surface, (x_left, y_pos))
            y_pos += 50

            # Shortcuts
            for key, description in shortcuts:
                # Key name (highlighted)
                key_surface = self.text_font.render(gettext(key), True, (255, 255, 0))
                screen.blit(key_surface, (x_left + 20, y_pos))

                # Description
                desc_surface = self.text_font.render(f"- {gettext(description)}", True, (200, 200, 200))
                screen.blit(desc_surface, (x_left + 250, y_pos))

                y_pos += 35

            y_pos += 20

        # Tips section
        y_pos += 10
        tips_title = self.section_font.render(gettext("tips").upper(), True, (100, 200, 255))
        screen.blit(tips_title, (x_left, y_pos))
        y_pos += 50

        tips = [
            gettext("tip_collect_powerups"),
            gettext("tip_use_weapons"),
            gettext("tip_boss_fights"),
            gettext("tip_unlock_ships"),
            gettext("tip_check_achievements"),
        ]

        for tip in tips:
            tip_surface = self.text_font.render(tip, True, (180, 180, 180))
            screen.blit(tip_surface, (x_left + 20, y_pos))
            y_pos += 35

        # Footer
        footer_text = gettext("help_footer")
        footer_surface = self.small_font.render(footer_text, True, (150, 150, 150))
        footer_rect = footer_surface.get_rect(
            center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 30)
        )
        screen.blit(footer_surface, footer_rect)
