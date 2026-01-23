"""Tutorial screens and tutorial page management."""

import pygame
import modul.constants as C

# Ensure `MenuStarfield` is available at module level so tests can patch it
try:
    from modul.starfield import MenuStarfield  # type: ignore
except (ImportError, ModuleNotFoundError):  # pragma: no cover - best-effort
    MenuStarfield = None


# Module-level runtime helpers to avoid imports inside methods and to satisfy
# linters (C0415).
try:
    from modul.i18n import gettext  # type: ignore
except (ImportError, ModuleNotFoundError):  # pragma: no cover - fallback for tests
    def gettext(k):
        """Fallback gettext returning the key when i18n is unavailable."""
        return k

try:
    from modul import input_utils  # type: ignore
except (ImportError, ModuleNotFoundError):  # pragma: no cover - provide minimal stub for tests
    class _InputUtilsStub:
        @staticmethod
        def get_action_keycode(_name):
            """Return None for keycodes when input utils are not available."""
            return None

    input_utils = _InputUtilsStub()


class Tutorial:
    """Manages tutorial pages and navigation."""

    def should_go_back(self, event):
        """Return True if the given event should trigger going back from the tutorial."""
        pause_key = input_utils.get_action_keycode("pause")
        shoot_key = input_utils.get_action_keycode("shoot")
        return (
            (pause_key is not None and event.key == pause_key)
            or event.key == pygame.K_ESCAPE
            or (shoot_key is not None and event.key == shoot_key)
            or event.key == pygame.K_SPACE
        )

    def __init__(self):
        """Initialize tutorial with pages."""
        # initialize attributes created later to avoid W0201
        self.target_page = 0
        # Use module-level `gettext` bound at import time
        self.pages = [
            {
                "title": gettext("tutorial_title_basics"),
                "content": [
                    gettext("tutorial_move"),
                    gettext("tutorial_shoot"),
                    gettext("tutorial_rotate"),
                    gettext("tutorial_thrust"),
                    gettext("tutorial_destroy_asteroids"),
                    gettext("tutorial_switch_b"),
                    "",
                    gettext("tutorial_large_asteroids"),
                    gettext("tutorial_collect_powerups"),
                ],
            },
            {
                "title": gettext("tutorial_title_powerups"),
                "content": [
                    gettext("tutorial_powerup_shield"),
                    gettext("tutorial_powerup_tripleshot"),
                    gettext("tutorial_powerup_speed"),
                    gettext("tutorial_powerup_laser"),
                    gettext("tutorial_powerup_rocket"),
                    gettext("tutorial_powerup_shotgun"),
                    "",
                    gettext("tutorial_powerups_note1"),
                    gettext("tutorial_powerups_note2"),
                ],
            },
            {
                "title": gettext("tutorial_title_level_system"),
                "content": [
                    gettext("tutorial_level_collect_points"),
                    gettext("tutorial_level_higher_levels"),
                    gettext("tutorial_level_max"),
                    "",
                    gettext("tutorial_boss_heading"),
                    gettext("tutorial_boss_every"),
                    gettext("tutorial_boss_health"),
                    gettext("tutorial_boss_reward"),
                    "",
                    gettext("tutorial_boss_strengthen"),
                ],
            },
            {
                "title": gettext("tutorial_title_weapon_system"),
                "content": [
                    gettext("tutorial_weapon_standard"),
                    gettext("tutorial_weapon_laser"),
                    gettext("tutorial_weapon_rockets"),
                    gettext("tutorial_weapon_shotgun"),
                    "",
                    gettext("tutorial_weapon_refill"),
                    gettext("tutorial_weapon_auto_switch"),
                ],
            },
            {
                "title": gettext("tutorial_title_boss_strategies"),
                "content": [
                    gettext("tutorial_boss_behavior"),
                    gettext("tutorial_boss_phases"),
                    gettext("tutorial_boss_patterns"),
                    gettext("tutorial_boss_more_dangerous"),
                    "",
                    gettext("tutorial_boss_tips_heading"),
                    gettext("tutorial_boss_tip_dodge"),
                    gettext("tutorial_boss_tip_collect"),
                    gettext("tutorial_boss_tip_focus"),
                    gettext("tutorial_boss_tip_healthbar"),
                ],
            },
            {
                "title": gettext("tutorial_title_advanced_tips"),
                "content": [
                    gettext("tutorial_controls_heading"),
                    gettext("tutorial_control_pause"),
                    gettext("tutorial_control_fullscreen"),
                    gettext("tutorial_control_music"),
                    gettext("tutorial_control_sound"),
                    gettext("tutorial_control_movement"),
                    gettext("tutorial_control_shoot"),
                    "",
                    gettext("tutorial_strategy_heading"),
                    gettext("tutorial_strategy_large_asteroids"),
                    gettext("tutorial_strategy_powerup_pulse"),
                    gettext("tutorial_strategy_invuln_after_respawn"),
                    gettext("tutorial_strategy_boss_optional"),
                ],
            },
            {
                "title": gettext("tutorial_title_difficulty_levels"),
                "content": [
                    gettext("tutorial_diff_easy_title"),
                    gettext("tutorial_diff_easy_lines"),
                    "",
                    gettext("tutorial_diff_normal_title"),
                    gettext("tutorial_diff_normal_lines"),
                    "",
                    gettext("tutorial_diff_hard_title"),
                    gettext("tutorial_diff_hard_lines"),
                ],
            },
        ]

        self.current_page = 0
        self.transitioning = False
        self.transition_timer = 0
        self.transition_duration = 0.3

        self.font_title = pygame.font.Font(None, 48)
        self.font_content = pygame.font.Font(None, 28)
        self.font_navigation = pygame.font.Font(None, 24)

        # Use the module-level `MenuStarfield` symbol so tests can patch it.
        if MenuStarfield is None:
            self.starfield = None
            print("Could not import starfield")
        else:
            try:
                self.starfield = MenuStarfield(num_stars=80)
            except (ImportError, TypeError):
                self.starfield = None
                print("Could not import starfield")

    def next_page(self):
        """Advance to the next tutorial page, starting transition animation."""
        if self.current_page < len(self.pages) - 1:
            self.start_transition(self.current_page + 1)

    def previous_page(self):
        """Go back to the previous tutorial page, starting transition."""
        if self.current_page > 0:
            self.start_transition(self.current_page - 1)

    def start_transition(self, target_page):
        """Begin a page transition animation toward `target_page`."""
        self.transitioning = True
        self.target_page = target_page
        self.transition_timer = 0

    def update(self, dt, events):
        """Process input events and update transition state for the tutorial."""
        if hasattr(self, "starfield") and self.starfield:
            self.starfield.update(dt)

        if self.transitioning:
            self.transition_timer += dt
            if self.transition_timer >= self.transition_duration:
                self.transitioning = False
                self.current_page = self.target_page
                self.transition_timer = 0
                return None

        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.should_go_back(event):
                    return "back"
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    if not self.transitioning:
                        self.previous_page()

                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    if not self.transitioning:
                        self.next_page()

        return None

    def draw(self, screen):
        """Render the current tutorial page and navigation UI to `screen`."""
        screen.fill((0, 0, 0))

        if hasattr(self, "starfield") and self.starfield:
            self.starfield.draw(screen)

        alpha = 255
        if self.transitioning:
            progress = self.transition_timer / self.transition_duration
            alpha = int(255 * (1 - abs(progress - 0.5) * 2))

        page = self.pages[self.current_page]
        y_offset = 80

        title_color = (100, 200, 255) if alpha == 255 else (100, 200, 255, alpha)
        title_surface = self.font_title.render(page["title"], True, title_color)
        title_rect = title_surface.get_rect(center=(C.SCREEN_WIDTH / 2, y_offset))

        if alpha < 255:
            title_surface.set_alpha(alpha)
        screen.blit(title_surface, title_rect)

        y_offset += 80

        for line in page["content"]:
            if line == "":
                y_offset += 15
                continue

            if (line.startswith("[") and "]" in line) or (
                ":" in line and any(weapon in line for weapon in ["STANDARD", "LASER", "ROCKET", "SHOTGUN"])
            ):
                self.draw_colored_line(screen, line, C.SCREEN_WIDTH // 2, y_offset)
            else:
                color = (255, 255, 255)

                if line.startswith("*** Boss Fights ***") or line.startswith("*** Boss Behavior ***"):
                    color = (128, 0, 128)
                elif line.startswith("*** Tips ***"):
                    color = (255, 215, 0)
                elif line.startswith("*** Controls ***") or line.startswith("*** Strategy ***"):
                    color = (100, 200, 255)

                elif line.startswith("•"):
                    color = (200, 200, 200)

                content_surface = self.font_content.render(line, True, color)
                if alpha < 255:
                    content_surface.set_alpha(alpha)

                content_rect = content_surface.get_rect(center=(C.SCREEN_WIDTH / 2, y_offset))
                screen.blit(content_surface, content_rect)

            y_offset += 35

        nav_y = C.SCREEN_HEIGHT - 80

        page_info = f"Page {self.current_page + 1} of {len(self.pages)}"
        page_surface = self.font_navigation.render(page_info, True, (150, 150, 150))
        page_rect = page_surface.get_rect(center=(C.SCREEN_WIDTH / 2, nav_y))
        screen.blit(page_surface, page_rect)

        nav_text = gettext("tutorial_nav")
        nav_surface = self.font_navigation.render(nav_text, True, (100, 100, 100))
        nav_rect = nav_surface.get_rect(center=(C.SCREEN_WIDTH / 2, nav_y + 30))
        screen.blit(nav_surface, nav_rect)

        progress_width = 300
        progress_height = 4
        progress_x = (C.SCREEN_WIDTH - progress_width) // 2
        progress_y = nav_y - 30

        pygame.draw.rect(screen, (50, 50, 50), (progress_x, progress_y, progress_width, progress_height))

        current_progress = (self.current_page + 1) / len(self.pages)
        progress_fill_width = int(progress_width * current_progress)
        pygame.draw.rect(screen, (100, 200, 255), (progress_x, progress_y, progress_fill_width, progress_height))

    def draw_colored_line(self, screen, line, x, y):
        """Render a colored title/content line used in tutorial pages."""
        if line.startswith("[") and "]" in line:
            bracket_end = line.find("]") + 1
            name_part = line[:bracket_end]
            desc_part = line[bracket_end:]

            name_color = (255, 255, 255)
            if "[SHIELD]" in name_part:
                name_color = (0, 255, 255)
            elif "[LASER]" in name_part:
                name_color = (0, 255, 0)
            elif "[ROCKET]" in name_part:
                name_color = (255, 0, 0)
            elif "[SHOTGUN]" in name_part:
                name_color = (255, 170, 0)
            elif "[3-SHOT]" in name_part:
                name_color = (255, 0, 255)
            elif "[SPEED]" in name_part:
                name_color = (255, 255, 0)
            elif "[LEASY]" in name_part:
                name_color = (0, 255, 0)
            elif "[NORMAL]" in name_part:
                name_color = (255, 255, 0)
            elif "[HARD]" in name_part:
                name_color = (255, 0, 0)

            name_surface = self.font_content.render(name_part, True, name_color)
            name_width = name_surface.get_width()

            desc_surface = self.font_content.render(desc_part, True, (255, 255, 255))

            total_width = name_width + desc_surface.get_width()
            start_x = x - total_width // 2

            screen.blit(name_surface, (start_x, y))
            screen.blit(desc_surface, (start_x + name_width, y))

        elif ":" in line:
            colon_pos = line.find(":") + 1
            name_part = line[:colon_pos]
            desc_part = line[colon_pos:]

            name_color = (255, 255, 255)
            if "STANDARD:" in name_part:
                name_color = (255, 255, 255)
            elif "LASER:" in name_part:
                name_color = (0, 255, 0)
            elif "ROCKETS:" in name_part:
                name_color = (255, 0, 0)
            elif "SHOTGUN:" in name_part:
                name_color = (255, 165, 0)

            name_surface = self.font_content.render(name_part, True, name_color)
            name_width = name_surface.get_width()

            desc_surface = self.font_content.render(desc_part, True, (255, 255, 255))

            total_width = name_width + desc_surface.get_width()
            start_x = x - total_width // 2

            screen.blit(name_surface, (start_x, y))
            screen.blit(desc_surface, (start_x + name_width, y))

        else:

            content_surface = self.font_content.render(line, True, (255, 255, 255))
            content_rect = content_surface.get_rect(center=(x, y))
            screen.blit(content_surface, content_rect)
