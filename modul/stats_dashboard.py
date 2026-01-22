"""Stats Dashboard UI for displaying detailed game statistics."""
import pygame

from modul.constants import (MENU_BACKGROUND_ALPHA, MENU_TITLE_COLOR,
                             MENU_TITLE_FONT_SIZE, MENU_TRANSITION_SPEED,
                             SCREEN_HEIGHT, SCREEN_WIDTH)
try:
    from modul.i18n import gettext
except (ImportError, ModuleNotFoundError):  # pragma: no cover - fallback when i18n unavailable
    def gettext(k):
        """Fallback gettext used in tests when i18n is not available."""
        return k

try:
    from modul import input_utils
except (ImportError, ModuleNotFoundError):  # pragma: no cover - minimal stub for tests
    class _InputUtilsStub:
        @staticmethod
        def get_action_keycode(_name):
            """Return None for mapped keys when input utilities are unavailable."""
            return None

    input_utils = _InputUtilsStub()


class StatsDashboard:
    """Display detailed session statistics with visual elements."""

    def __init__(self, session_stats):
        """TODO: add docstring."""
        self.session_stats = session_stats
        self.title_font = pygame.font.Font(None, MENU_TITLE_FONT_SIZE)
        self.section_font = pygame.font.Font(None, 40)
        self.text_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 24)
        self.background_alpha = 0
        self.fade_in = False

    def activate(self):
        """Activate the stats dashboard."""
        self.fade_in = True
        self.background_alpha = 0

    def update(self, dt, events):
        """Update stats dashboard state."""
        if self.fade_in:
            self.background_alpha = min(255, self.background_alpha + 255 * dt / MENU_TRANSITION_SPEED)
            if self.background_alpha >= MENU_BACKGROUND_ALPHA:
                self.fade_in = False
                self.background_alpha = MENU_BACKGROUND_ALPHA

        for event in events:
            if event.type == pygame.KEYDOWN:
                pause_key = input_utils.get_action_keycode("pause")
                shoot_key = input_utils.get_action_keycode("shoot")
                if ((pause_key is not None and event.key == pause_key)
                        or event.key in (pygame.K_ESCAPE, pygame.K_SPACE)
                        or (shoot_key is not None and event.key == shoot_key)):
                    return "back"
        return None

    def draw(self, screen):
        """Draw the stats dashboard."""
        # Semi-transparent background
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((0, 0, 0, self.background_alpha))
        screen.blit(background, (0, 0))

        # Title
        title_surf = self.title_font.render(gettext("session_statistics"), True, pygame.Color(MENU_TITLE_COLOR))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH / 2, 60))
        screen.blit(title_surf, title_rect)

        stats = self.session_stats.get_summary()

        # Left column - Game Statistics
        left_x = SCREEN_WIDTH / 4
        y_pos = 140

        self._draw_section(screen, gettext("game_stats"), left_x, y_pos)
        y_pos += 50

        game_stats = [
            (gettext("games_played"), f"{stats.get('games_played', 0)}"),
            (gettext("highest_score"), f"{stats.get('highest_score', 0):,}"),
            (gettext("average_score"), f"{stats.get('average_score', 0.0):.0f}"),
            (gettext("highest_level"), f"{stats.get('highest_level', 0)}"),
            (gettext("total_playtime"), self.session_stats.format_time(stats.get('total_playtime', 0.0))),
        ]

        for label, value in game_stats:
            self._draw_stat_line(screen, label, value, left_x, y_pos)
            y_pos += 35

        # Right column - Combat Statistics
        right_x = SCREEN_WIDTH * 3 / 4
        y_pos = 140

        self._draw_section(screen, gettext("combat_stats"), right_x, y_pos)
        y_pos += 50

        combat_stats = [
            (gettext("asteroids_destroyed"), f"{stats['total_asteroids_destroyed']:,}"),
            (gettext("enemies_destroyed"), f"{stats['total_enemies_destroyed']:,}"),
            (gettext("bosses_defeated"), f"{stats['total_bosses_defeated']}"),
            (gettext("powerups_collected"), f"{stats['total_powerups_collected']:,}"),
            (gettext("lives_lost"), f"{stats['total_lives_lost']}"),
        ]

        for label, value in combat_stats:
            self._draw_stat_line(screen, label, value, right_x, y_pos)
            y_pos += 35

        # Accuracy and efficiency bars
        y_pos = 400
        self._draw_progress_bars(screen, stats, y_pos)

        # Session duration
        y_pos = 560
        session_time = self.session_stats.format_time(stats['session_duration'])
        time_text = gettext("session_duration_format").format(time=session_time)
        time_surf = self.section_font.render(time_text, True, (100, 200, 255))
        time_rect = time_surf.get_rect(center=(SCREEN_WIDTH / 2, y_pos))
        screen.blit(time_surf, time_rect)

        # Footer instructions
        footer_text = gettext("press_esc_space_return")
        footer_surf = self.small_font.render(footer_text, True, (150, 150, 150))
        footer_rect = footer_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 30))
        screen.blit(footer_surf, footer_rect)

    def _draw_section(self, screen, title, x, y):
        """Draw a section header."""
        section_surf = self.section_font.render(title, True, (100, 200, 255))
        section_rect = section_surf.get_rect(center=(x, y))
        screen.blit(section_surf, section_rect)

    def _draw_stat_line(self, screen, label, value, x, y):
        """Draw a single stat line."""
        label_surf = self.text_font.render(f"{label}:", True, (200, 200, 200))
        label_rect = label_surf.get_rect(midright=(x - 20, y))
        screen.blit(label_surf, label_rect)

        value_surf = self.text_font.render(str(value), True, (255, 255, 255))
        value_rect = value_surf.get_rect(midleft=(x + 20, y))
        screen.blit(value_surf, value_rect)

    def _draw_progress_bars(self, screen, stats, y_pos):
        """Draw visual progress bars for key metrics."""
        
        bar_width = 400
        bar_height = 30
        center_x = SCREEN_WIDTH / 2

        # Accuracy bar
        accuracy = self.session_stats.get_accuracy()
        y = y_pos

        label_surf = self.text_font.render(gettext("accuracy"), True, (255, 255, 255))
        label_rect = label_surf.get_rect(center=(center_x, y - 25))
        screen.blit(label_surf, label_rect)

        self._draw_bar(screen, center_x - bar_width / 2, y, bar_width, bar_height,
                      accuracy, 100, (255, 100, 100), (255, 215, 0))

        value_surf = self.small_font.render(f"{accuracy:.1f}%", True, (255, 255, 255))
        value_rect = value_surf.get_rect(center=(center_x, y + bar_height / 2))
        screen.blit(value_surf, value_rect)

        # Average score vs highest score indicator
        y = y_pos + 80

        label_surf = self.text_font.render(gettext("performance"), True, (255, 255, 255))
        label_rect = label_surf.get_rect(center=(center_x, y - 25))
        screen.blit(label_surf, label_rect)

        avg_score = float(stats.get('average_score', 0.0) or 0.0)
        high_score = float(stats.get('highest_score', 0.0) or 0.0)
        high_score = max(high_score, 1.0)
        performance = min(100.0, max(0.0, (avg_score / high_score) * 100.0))

        self._draw_bar(screen, center_x - bar_width / 2, y, bar_width, bar_height,
                      performance, 100, (100, 100, 255), (100, 255, 100))

        perf_text = gettext("performance_ratio_format").format(performance=performance)
        perf_surf = self.small_font.render(perf_text, True, (255, 255, 255))
        perf_rect = perf_surf.get_rect(center=(center_x, y + bar_height / 2))
        screen.blit(perf_surf, perf_rect)

    def _draw_bar(self, screen, x, y, width, height, value, max_value, start_color, end_color):
        """Draw a progress bar with gradient."""
        # Background
        pygame.draw.rect(screen, (50, 50, 50), (x, y, width, height))
        pygame.draw.rect(screen, (100, 100, 100), (x, y, width, height), 2)

        # Fill
        if max_value > 0:
            fill_width = (value / max_value) * width
            if fill_width > 0:
                # Simple gradient effect
                progress = value / max_value
                r = int(start_color[0] + (end_color[0] - start_color[0]) * progress)
                g = int(start_color[1] + (end_color[1] - start_color[1]) * progress)
                b = int(start_color[2] + (end_color[2] - start_color[2]) * progress)

                pygame.draw.rect(screen, (r, g, b), (x, y, fill_width, height))
