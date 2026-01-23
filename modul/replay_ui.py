"""Replay UI for listing and playing back replays."""
from datetime import datetime

import pygame

from modul.constants import (MENU_BACKGROUND_ALPHA, MENU_ITEM_FONT_SIZE,
                             MENU_SELECTED_COLOR, MENU_TITLE_COLOR,
                             MENU_TITLE_FONT_SIZE, MENU_TRANSITION_SPEED,
                             MENU_UNSELECTED_COLOR, SCREEN_HEIGHT,
                             SCREEN_WIDTH)
from modul.replay_system import ReplayManager, ReplayPlayer
try:
    from modul.i18n import gettext
except (ImportError, ModuleNotFoundError):  # pragma: no cover - fallback when i18n unavailable
    def gettext(key):
        """
        Return the translation for the given key using a no-op fallback.
        
        Parameters:
            key (str): Translation key or message identifier.
        
        Returns:
            str: The input key unchanged.
        """
        return key

try:
    from modul import input_utils
except (ImportError, ModuleNotFoundError):  # pragma: no cover - minimal stub for tests
    class _InputUtilsStub:
        @staticmethod
        def get_action_keycode(_name):
            """Return None as a placeholder for mapped keycodes in tests."""
            return None

    input_utils = _InputUtilsStub()


class ReplayListMenu:
    """Menu for listing and selecting replays."""

    def __init__(self, replay_manager: ReplayManager):
        """
        Create a ReplayListMenu bound to the provided ReplayManager.
        
        Parameters:
        	replay_manager (ReplayManager): Manager used to list, delete, and access replay files and metadata.
        """
        self.replay_manager = replay_manager
        self.title_font = pygame.font.Font(None, MENU_TITLE_FONT_SIZE)
        self.text_font = pygame.font.Font(None, MENU_ITEM_FONT_SIZE)
        self.small_font = pygame.font.Font(None, 24)
        self.background_alpha = 0
        self.fade_in = False
        self.selected_index = 0
        self.replays = []

    def activate(self):
        """Activate the replay list menu."""
        self.fade_in = True
        self.background_alpha = 0
        self.selected_index = 0
        self.replays = self.replay_manager.list_replays()

    def update(self, dt, events):
        """Update replay list menu state."""
        if self.fade_in:
            self.background_alpha = min(
                255,
                self.background_alpha + 255 * dt / MENU_TRANSITION_SPEED,
            )
            if self.background_alpha >= MENU_BACKGROUND_ALPHA:
                self.fade_in = False
                self.background_alpha = MENU_BACKGROUND_ALPHA

        # Allow mapped keys for pause/select via input_utils
        pause_key = input_utils.get_action_keycode("pause")
        shoot_key = input_utils.get_action_keycode("shoot")

        for event in events:
            if event.type == pygame.KEYDOWN:
                if (pause_key is not None and event.key == pause_key) or event.key == pygame.K_ESCAPE:
                    return {"action": "back"}

                if event.key == pygame.K_UP and len(self.replays) > 0:
                    self.selected_index = (self.selected_index - 1) % len(self.replays)
                    continue

                if event.key == pygame.K_DOWN and len(self.replays) > 0:
                    self.selected_index = (self.selected_index + 1) % len(self.replays)
                    continue

                # Play selected (Enter, Space or mapped shoot)
                if ((event.key in (pygame.K_RETURN, pygame.K_SPACE)
                        or (shoot_key is not None and event.key == shoot_key))
                        and len(self.replays) > 0):
                    return {
                        "action": "play_replay",
                        "filepath": self.replays[self.selected_index]["filepath"],
                    }

                if event.key == pygame.K_DELETE and len(self.replays) > 0:
                    filepath = self.replays[self.selected_index]["filepath"]
                    self.replay_manager.delete_replay(filepath)
                    self.replays = self.replay_manager.list_replays()
                    if self.selected_index >= len(self.replays):
                        self.selected_index = max(0, len(self.replays) - 1)

        return None

    def draw(self, screen):
        """Draw the replay list menu."""
        # Semi-transparent background
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((0, 0, 0, self.background_alpha))
        screen.blit(background, (0, 0))

        # Title
        title_surf = self.title_font.render(gettext("replay_browser"), True, pygame.Color(MENU_TITLE_COLOR))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH / 2, 60))
        screen.blit(title_surf, title_rect)

        if not self.replays:
            # No replays message
            no_replays_surf = self.text_font.render(gettext("no_replays_found"), True, (200, 200, 200))
            no_replays_rect = no_replays_surf.get_rect(
                center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            )
            screen.blit(no_replays_surf, no_replays_rect)
        else:
            # Draw replay list
            y_pos = 140
            for i, replay in enumerate(self.replays):
                metadata = replay['metadata']

                # Format timestamp
                timestamp = metadata.get('start_time', 0)
                date_str = datetime.fromtimestamp(timestamp).strftime(
                    '%Y-%m-%d %H:%M'
                )

                # Format info
                score = metadata.get('final_score', 0)
                level = metadata.get('final_level', 0)
                difficulty = metadata.get('difficulty', 'normal').capitalize()
                duration = metadata.get('duration', 0)
                duration_str = (
                    f"{int(duration // 60)}:{int(duration % 60):02d}"
                )

                info_text = (
                    f"{date_str} | Score: {score:,} | Level: {level} | "
                    f"{difficulty} | {duration_str}"
                )

                # Highlight selected
                if i == self.selected_index:
                    color = pygame.Color(MENU_SELECTED_COLOR)
                    prefix = "► "
                else:
                    color = pygame.Color(MENU_UNSELECTED_COLOR)
                    prefix = "  "

                text_surf = self.text_font.render(
                    prefix + info_text,
                    True,
                    color,
                )
                text_rect = text_surf.get_rect(
                    center=(SCREEN_WIDTH / 2, y_pos)
                )
                screen.blit(text_surf, text_rect)

                y_pos += 45

                # Don't draw too many at once
                if y_pos > SCREEN_HEIGHT - 150:
                    break

        # Instructions
        instructions = [gettext("replay_instructions")]

        y_pos = SCREEN_HEIGHT - 60
        for instruction in instructions:
            instr_surf = self.small_font.render(
                instruction,
                True,
                (150, 150, 150),
            )
            instr_rect = instr_surf.get_rect(center=(SCREEN_WIDTH / 2, y_pos))
            screen.blit(instr_surf, instr_rect)
            y_pos += 30


class ReplayViewer:
    """Viewer for playing back replays."""

    def __init__(self, replay_player: ReplayPlayer):
        """
        Initialize the ReplayViewer with a ReplayPlayer and prepare fonts used by the HUD and on-screen text.
        
        Parameters:
            replay_player (ReplayPlayer): Player instance used to control playback and provide playback state (progress, time, pause/play, speed).
        """
        self.replay_player = replay_player
        self.title_font = pygame.font.Font(None, 48)
        self.text_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)

    def update(self, _dt, events):
        """Update replay viewer state. `_dt` is accepted for API compatibility."""
        pause_key = input_utils.get_action_keycode("pause")
        shoot_key = input_utils.get_action_keycode("shoot")

        for event in events:
            if event.type == pygame.KEYDOWN:
                if (pause_key is not None and event.key == pause_key) or event.key == pygame.K_ESCAPE:
                    self.replay_player.stop_playback()
                    return "back"
                elif (shoot_key is not None and event.key == shoot_key) or event.key == pygame.K_SPACE:
                    self.replay_player.toggle_pause()
                elif event.key == pygame.K_LEFT:
                    self.replay_player.skip_backward(5.0)
                elif event.key == pygame.K_RIGHT:
                    self.replay_player.skip_forward(5.0)
                elif event.key == pygame.K_1:
                    self.replay_player.set_speed(0.5)
                elif event.key == pygame.K_2:
                    self.replay_player.set_speed(1.0)
                elif event.key == pygame.K_3:
                    self.replay_player.set_speed(2.0)

        return None

    def draw_hud(self, screen):
        """
        Render the replay HUD overlay onto the given screen.
        
        Displays playback status (playing/paused), a progress bar, current and total time, playback speed, control hints, and a replay label in the top-right corner by drawing directly onto the provided pygame surface.
        
        Parameters:
            screen (pygame.Surface): Target surface to render the HUD onto.
        """
        # use module-level gettext
        # Draw control bar at bottom
        bar_height = 80
        bar_y = SCREEN_HEIGHT - bar_height

        # Semi-transparent background
        overlay = pygame.Surface((SCREEN_WIDTH, bar_height))
        overlay.set_alpha(180)
        overlay.fill((20, 20, 20))
        screen.blit(overlay, (0, bar_y))

        # Playback status
        status = gettext("paused") if self.replay_player.paused else gettext("playing")
        status_color = (
            (255, 200, 0) if self.replay_player.paused else (0, 255, 0)
        )
        status_surf = self.text_font.render(status, True, status_color)
        screen.blit(status_surf, (20, bar_y + 10))

        # Progress bar
        progress = self.replay_player.get_progress_percentage()
        bar_width = 600
        bar_x = SCREEN_WIDTH / 2 - bar_width / 2
        bar_y_pos = bar_y + 20

        # Background
        pygame.draw.rect(
            screen,
            (50, 50, 50),
            (bar_x, bar_y_pos, bar_width, 10),
        )

        # Progress
        fill_width = (progress / 100.0) * bar_width
        pygame.draw.rect(
            screen,
            (0, 200, 255),
            (bar_x, bar_y_pos, fill_width, 10),
        )

        # Time info
        current_time = self.replay_player.get_current_timestamp()
        total_time = self.replay_player.metadata.get('duration', 0)
        time_text = (
            f"{int(current_time // 60)}:{int(current_time % 60):02d} / "
            f"{int(total_time // 60)}:{int(total_time % 60):02d}"
        )
        time_surf = self.small_font.render(time_text, True, (200, 200, 200))
        time_rect = time_surf.get_rect(center=(SCREEN_WIDTH / 2, bar_y + 45))
        screen.blit(time_surf, time_rect)

        # Speed indicator
        template = gettext("replay_speed_format")
        try:
            # Defensive formatting: if the template doesn't accept 'speed', fall back
            speed_text = template.format(speed=self.replay_player.playback_speed)
        except Exception:
            # Fallback to a safe default that includes the numeric speed
            speed_text = f"{self.replay_player.playback_speed}x"
        speed_surf = self.small_font.render(speed_text, True, (200, 200, 200))
        screen.blit(speed_surf, (SCREEN_WIDTH - 150, bar_y + 10))

        # Controls hint
        controls = gettext("replay_controls")
        controls_surf = self.small_font.render(controls, True, (150, 150, 150))
        controls_rect = controls_surf.get_rect(
            center=(SCREEN_WIDTH / 2, bar_y + 65)
        )
        screen.blit(controls_surf, controls_rect)

        # Replay indicator in top-right
        replay_text = gettext("replay_label")
        replay_surf = self.title_font.render(replay_text, True, (255, 0, 0))
        screen.blit(replay_surf, (SCREEN_WIDTH - 200, 20))