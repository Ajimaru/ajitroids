"""Help screen showing keyboard shortcuts and game information."""
import pygame
from modul.constants import SCREEN_HEIGHT, SCREEN_WIDTH
try:
    from modul import input_utils  # type: ignore
except (ImportError, ModuleNotFoundError):  # pragma: no cover - provide minimal stub for tests
    class _InputUtilsStub:
        @staticmethod
        def get_action_keycode(_name):
            """Stub for get_action_keycode; returns None."""
            return None

    input_utils = _InputUtilsStub()
try:
    from modul.i18n import gettext  # type: ignore
except (ImportError, ModuleNotFoundError):  # pragma: no cover - fallback for tests
    def gettext(k):
        """Fallback gettext function that returns the input key unchanged."""
        return k


class HelpScreen:
    """Display keyboard shortcuts and game help."""

    def __init__(self):
        """Initialize the help screen with fonts and shortcut data."""
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
                ("f7", "desc_f7"),
                ("f8", "desc_f8"),
                ("f9", "desc_f9"),
                ("f10", "desc_f10"),
                ("f11", "desc_f11"),
            ]),
        ]

        self.background_alpha = 200

    def _ensure_fonts(self):
        """Ensure pygame fonts are initialized and cached on the instance."""
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

    def update(self, _dt, events):
        """Update help screen state. `_dt` accepted for API compatibility."""
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
        x_left = 60
        desc_x = x_left + 250

        # Tips get their own column. Stacked underneath the shortcut list they
        # started at y=690, so the last four entries landed outside the 720px
        # canvas and the footer was drawn on top of the rest. Their x is
        # measured rather than hardcoded so longer translations cannot collide
        # with the descriptions.
        tips = [
            gettext("tip_collect_powerups"),
            gettext("tip_use_weapons"),
            gettext("tip_boss_fights"),
            gettext("tip_unlock_ships"),
            gettext("tip_check_achievements"),
            gettext("tip_hazards_events"),
        ]
        widest_desc = max(
            (self.text_font.size(f"- {gettext(description)}")[0]
             for _, items in self.shortcuts for _, description in items),
            default=0,
        )
        # Reserve space for tips even when descriptions need fitting.
        x_tips = min(desc_x + widest_desc + 48, SCREEN_WIDTH - 320)
        description_width = x_tips - desc_x - 24
        tips_width = SCREEN_WIDTH - x_tips - 40

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
                if desc_surface.get_width() > description_width:
                    scale = description_width / desc_surface.get_width()
                    desc_surface = pygame.transform.smoothscale(
                        desc_surface, (description_width, max(1, int(desc_surface.get_height() * scale)))
                    )
                screen.blit(desc_surface, (desc_x, y_pos))

                y_pos += 35

            y_pos += 20

        # Wrap even unbroken translated words to the available column width.
        lines = []
        for tip in tips:
            remaining = tip
            while remaining:
                end = len(remaining)
                while end > 1 and self.small_font.size(remaining[:end])[0] > tips_width - 20:
                    end -= 1
                if end < len(remaining):
                    space = remaining.rfind(" ", 0, end + 1)
                    if space > 0:
                        end = space
                lines.append(remaining[:end])
                remaining = remaining[end:].lstrip()
            lines.append("")

        tips_panel = pygame.Surface((tips_width, 50 + len(lines) * 24), pygame.SRCALPHA)
        tips_title = self.section_font.render(gettext("tips").upper(), True, (100, 200, 255))
        if tips_title.get_width() > tips_width:
            scale = tips_width / tips_title.get_width()
            tips_title = pygame.transform.smoothscale(
                tips_title, (tips_width, max(1, int(tips_title.get_height() * scale)))
            )
        tips_panel.blit(tips_title, (0, 0))
        for index, line in enumerate(lines):
            tip_surface = self.small_font.render(line, True, (180, 180, 180))
            tips_panel.blit(tip_surface, (20, 50 + index * 24))
        available_height = SCREEN_HEIGHT - 210
        if tips_panel.get_height() > available_height:
            scale = available_height / tips_panel.get_height()
            tips_panel = pygame.transform.smoothscale(
                tips_panel, (max(1, int(tips_width * scale)), available_height)
            )
        screen.blit(tips_panel, (x_tips, 140))

        # Footer
        footer_text = gettext("help_footer")
        footer_surface = self.small_font.render(footer_text, True, (150, 150, 150))
        footer_rect = footer_surface.get_rect(
            center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 30)
        )
        screen.blit(footer_surface, footer_rect)
