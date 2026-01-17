# flake8: noqa
# pylint: disable=all
# pyright: reportUndefinedVariable=false
# pyright: reportWildcardImportFromLibrary=false
import math

import pygame

from modul.version import __version__
from modul.constants import *
from modul.ships import ship_manager, ShipRenderer

sounds = None


class MenuItem:
    def __init__(self, text, action):
        self.text = text
        self.action = action
        self.selected = False
        self.hover_animation = 0
        self.opacity = 255
        self.delay = 0

    def update(self, dt):
        target = 1.0 if self.selected else 0.0
        animation_speed = 12.0
        self.hover_animation = self.hover_animation + (target - self.hover_animation) * dt * animation_speed
        if self.delay > 0:
            self.delay -= dt
            if self.delay <= 0:
                self.delay = 0
                self.opacity = 255

    def draw(self, screen, position, font):
        color = pygame.Color(MENU_UNSELECTED_COLOR)
        selected_color = pygame.Color(MENU_SELECTED_COLOR)
        r = max(0, min(255, int(color.r + (selected_color.r - color.r) * self.hover_animation)))
        g = max(0, min(255, int(color.g + (selected_color.g - color.g) * self.hover_animation)))
        b = max(0, min(255, int(color.b + (selected_color.b - color.b) * self.hover_animation)))
        size_multiplier = 1.0 + 0.2 * self.hover_animation
        scaled_font = pygame.font.Font(None, int(MENU_ITEM_FONT_SIZE * size_multiplier))
        text_surface = scaled_font.render(self.text, True, (r, g, b))
        text_rect = text_surface.get_rect(center=(position[0], position[1]))
        screen.blit(text_surface, text_rect)
        return text_rect


class Menu:
    def __init__(self, title):
        self.title = title
        self.items = []
        self.selected_index = 0
        self.background_alpha = 0
        self.title_font = pygame.font.Font(None, MENU_TITLE_FONT_SIZE)
        self.item_font = pygame.font.Font(None, MENU_ITEM_FONT_SIZE)
        self.active = False
        self.fade_in = False
        self.input_cooldown = 0

    def add_item(self, text, action, shortcut=None):
        item = MenuItem(text, action)
        item.shortcut = shortcut
        self.items.append(item)
        if len(self.items) == 1:
            self.items[0].selected = True

    def activate(self):
        self.active = True
        self.fade_in = True
        self.background_alpha = 0
        for i, item in enumerate(self.items):
            item.opacity = 0
            item.delay = i * 0.1

    def update(self, dt, events):
        if self.fade_in:
            self.background_alpha = min(255, self.background_alpha + 255 * dt / MENU_TRANSITION_SPEED)
            if self.background_alpha >= MENU_BACKGROUND_ALPHA:
                self.fade_in = False
                self.background_alpha = MENU_BACKGROUND_ALPHA

        for item in self.items:
            item.update(dt)

        if self.input_cooldown > 0:
            self.input_cooldown -= dt

        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.input_cooldown <= 0:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self._select_previous()
                        self.input_cooldown = 0.15
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self._select_next()
                        self.input_cooldown = 0.15
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        return self.items[self.selected_index].action

        for event in events:
            if event.type == pygame.KEYDOWN:
                for i, item in enumerate(self.items):
                    if hasattr(item, "shortcut") and item.shortcut and event.unicode.lower() == item.shortcut.lower():
                        self.selected_index = i
                        self.items[self.selected_index].selected = True
                        return item.action

        keys = pygame.key.get_pressed()
        if self.input_cooldown <= 0:
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self._select_previous()
                self.input_cooldown = 0.15
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self._select_next()
                self.input_cooldown = 0.15

        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()

            axis_y = joystick.get_axis(1)
            if axis_y < -0.5 and self.input_cooldown <= 0:
                self._select_previous()
                self.input_cooldown = 0.15
            elif axis_y > 0.5 and self.input_cooldown <= 0:
                self._select_next()
                self.input_cooldown = 0.15

            if joystick.get_button(0) and self.input_cooldown <= 0:
                self.input_cooldown = 0.15
                return self.items[self.selected_index].action

        return None

    def _select_next(self):
        self.items[self.selected_index].selected = False
        self.selected_index = (self.selected_index + 1) % len(self.items)
        self.items[self.selected_index].selected = True
        if "sounds" in globals() or hasattr(self, "sounds"):
            try:
                sounds.play_menu_move()
            except Exception:
                pass

    def _select_previous(self):
        self.items[self.selected_index].selected = False
        self.selected_index = (self.selected_index - 1) % len(self.items)
        self.items[self.selected_index].selected = True
        if "sounds" in globals() or hasattr(self, "sounds"):
            try:
                sounds.play_menu_move()
            except Exception:
                pass

    def draw(self, screen):
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((0, 0, 0, self.background_alpha))
        screen.blit(background, (0, 0))

        title_surf = self.title_font.render(self.title, True, pygame.Color(MENU_TITLE_COLOR))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 8))
        screen.blit(title_surf, title_rect)

        # Center items vertically so long lists still fit
        total_height = (len(self.items) - 1) * MENU_ITEM_SPACING
        start_y = SCREEN_HEIGHT / 2 - total_height / 2
        for i, item in enumerate(self.items):
            position = (SCREEN_WIDTH / 2, start_y + i * MENU_ITEM_SPACING)
            item.draw(screen, position, self.item_font)


class MainMenu(Menu):
    def __init__(self):
        super().__init__("AJITROIDS")
        self.add_item("Start Game", "start_game")
        self.add_item("Tutorial", "tutorial")
        self.add_item("Replays", "replays")
        self.add_item("Highscores", "highscores")
        self.add_item("Statistics", "statistics")
        self.add_item("Achievements", "achievements")
        self.add_item("Optionen", "options")
        self.add_item("Credits", "credits")
        self.add_item("Exit", "exit")

    def draw(self, screen):
        super().draw(screen)

        version_font = pygame.font.Font(None, int(MENU_ITEM_FONT_SIZE / 1.5))
        version_text = version_font.render(__version__, True, pygame.Color(MENU_UNSELECTED_COLOR))
        version_rect = version_text.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
        screen.blit(version_text, version_rect)


class PauseMenu(Menu):
    def __init__(self):
        super().__init__("PAUSE")
        self.add_item("Continue", "continue")
        self.add_item("Restart", "restart")
        self.add_item("Main Menu", "main_menu")

    def draw(self, screen):
        super().draw(screen)

        # Show common keyboard shortcuts while paused
        shortcuts_font = pygame.font.Font(None, int(MENU_ITEM_FONT_SIZE * 0.8))
        shortcuts = [
            "Arrow Up: Accelerate",
            "Arrow Left/Right: Turn",
            "Arrow Down: Reverse",
            "Spacebar: Shoot",
            "ESC: Pause",
            "B: Switch weapons",
            "R: Quick restart",
            "F1 / H: Help",
            "F8: Toggle FPS",
            "F9: Toggle SFX",
            "F10: Toggle music",
            "F11: Fullscreen",
            "F12: Performance profiler",
            "P: Screenshot",
        ]

        shortcuts_x = 30
        shortcuts_y = 150
        for i, shortcut in enumerate(shortcuts):
            shortcut_surf = shortcuts_font.render(shortcut, True, (200, 200, 200))
            screen.blit(shortcut_surf, (shortcuts_x, shortcuts_y + i * 35))


class TutorialScreen:
    def __init__(self):
        self.title_font = pygame.font.Font(None, MENU_TITLE_FONT_SIZE)
        self.text_font = pygame.font.Font(None, MENU_ITEM_FONT_SIZE)
        self.background_alpha = 0
        self.fade_in = True

    def update(self, dt, events):
        if self.fade_in:
            self.background_alpha = min(255, self.background_alpha + 255 * dt / MENU_TRANSITION_SPEED)
            if self.background_alpha >= MENU_BACKGROUND_ALPHA:
                self.fade_in = False
                self.background_alpha = MENU_BACKGROUND_ALPHA

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "main_menu"

        return None

    def draw(self, screen):
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((0, 0, 0, self.background_alpha))
        screen.blit(background, (0, 0))

        title_surf = self.title_font.render("How to Play", True, pygame.Color(MENU_TITLE_COLOR))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH / 2, 100))
        screen.blit(title_surf, title_rect)

        instructions = [
            "Arrow Up: Accelerate",
            "Arrow Left: Turn left",
            "Arrow Right: Turn right",
            "Arrow Down: Reverse",
            "Spacebar: Shoot / In menu: Return to main menu",
            "ESC: Pause",
            "",
            "Destroy all asteroids and collect power-ups:",
            "Shield (Blue): Temporary invincibility",
            "Triple Shot (Magenta): Three shots at once",
            "Rapid Fire (Yellow): Increased fire rate",
            "",
            "SPACEBAR to go back",
        ]
        y = 180
        for line in instructions:
            text_surf = self.text_font.render(line, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH / 2, y))
            screen.blit(text_surf, text_rect)
            y += 40


class OptionsMenu(Menu):
    def __init__(self, settings, sounds):
        super().__init__("OPTIONS")
        self.settings = settings
        self.sounds = sounds
        self.add_item("Music: ON" if settings.music_on else "Music: OFF", "toggle_music")
        self.add_item("Sound: ON" if settings.sound_on else "Sound: OFF", "toggle_sound")
        self.add_item(f"Music Volume: {settings.music_volume * 100:.0f}%", "adjust_music_volume")
        self.add_item(f"Sound Volume: {settings.sound_volume * 100:.0f}%", "adjust_sound_volume")
        self.add_item("Fullscreen: ON" if settings.fullscreen else "Fullscreen: OFF", "toggle_fullscreen")
        self.add_item("Voice Announcements...", "voice_announcements")
        self.add_item("Sound Test", "sound_test")
        self.add_item("Back", "back")

    def handle_action(self, action, sounds):
        if action == "toggle_music":
            self.settings.music_on = not self.settings.music_on
            self.settings.save()
            sounds.toggle_music(self.settings.music_on)
            self.items[0].text = "Music: ON" if self.settings.music_on else "Music: OFF"
            return None

        elif action == "toggle_sound":
            self.settings.sound_on = not self.settings.sound_on
            self.settings.save()
            sounds.toggle_sound(self.settings.sound_on)
            self.items[1].text = "Sound: ON" if self.settings.sound_on else "Sound: OFF"
            return None

        elif action == "adjust_music_volume":
            self.settings.music_volume = min(1.0, max(0.0, self.settings.music_volume + 0.1))
            self.settings.save()
            if self.sounds:
                self.sounds.set_music_volume(self.settings.music_volume)
            self.items[2].text = f"Music Volume: {self.settings.music_volume * 100:.0f}%"
            return None

        elif action == "adjust_sound_volume":
            self.settings.sound_volume = min(1.0, max(0.0, self.settings.sound_volume + 0.1))
            self.settings.save()
            if self.sounds:
                self.sounds.set_effects_volume(self.settings.sound_volume)
            self.items[3].text = f"Sound Volume: {self.settings.sound_volume * 100:.0f}%"
            return None

        elif action == "toggle_fullscreen":
            self.settings.fullscreen = not self.settings.fullscreen
            self.settings.save()

            try:
                if self.settings.fullscreen:
                    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                    print("Fullscreen aktiviert")
                else:
                    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                    print("Windowed mode activated")
            except Exception as e:
                print(f"Error switching screen mode: {e}")
                self.settings.fullscreen = not self.settings.fullscreen
                self.settings.save()

            self.items[4].text = "Fullscreen: ON" if self.settings.fullscreen else "Fullscreen: OFF"
            return None

        elif action == "voice_announcements":
            return "voice_announcements"

        elif action == "sound_test":
            return "sound_test"

        elif action == "back":
            return "main_menu"

        return None

    def update(self, dt, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "main_menu"
                elif event.key == pygame.K_LEFT:
                    if self.items[self.selected_index].action == "adjust_music_volume":
                        self.settings.music_volume = max(0.0, self.settings.music_volume - 0.1)
                        self.settings.save()
                        if self.sounds:
                            self.sounds.set_music_volume(self.settings.music_volume)
                        self.items[self.selected_index].text = f"Music Volume: {self.settings.music_volume * 100:.0f}%"
                    elif self.items[self.selected_index].action == "adjust_sound_volume":
                        self.settings.sound_volume = max(0.0, self.settings.sound_volume - 0.1)
                        self.settings.save()
                        if self.sounds:
                            self.sounds.set_effects_volume(self.settings.sound_volume)
                        self.items[self.selected_index].text = f"Sound Volume: {self.settings.sound_volume * 100:.0f}%"
                elif event.key == pygame.K_RIGHT:
                    if self.items[self.selected_index].action == "adjust_music_volume":
                        self.settings.music_volume = min(1.0, self.settings.music_volume + 0.1)
                        self.settings.save()
                        if self.sounds:
                            self.sounds.set_music_volume(self.settings.music_volume)
                        self.items[self.selected_index].text = f"Music Volume: {self.settings.music_volume * 100:.0f}%"
                    elif self.items[self.selected_index].action == "adjust_sound_volume":
                        self.settings.sound_volume = min(1.0, self.settings.sound_volume + 0.1)
                        self.settings.save()
                        if self.sounds:
                            self.sounds.set_effects_volume(self.settings.sound_volume)
                        self.items[self.selected_index].text = f"Sound Volume: {self.settings.sound_volume * 100:.0f}%"
        result = super().update(dt, events)
        if result:
            return result
        return None


class CreditsScreen:
    def __init__(self):
        self.title_font = pygame.font.Font(None, MENU_TITLE_FONT_SIZE)
        self.text_font = pygame.font.Font(None, MENU_ITEM_FONT_SIZE - 8)
        self.background_alpha = 0
        self.fade_in = True
        self.scroll_position = 250

    def update(self, dt, events):
        if self.fade_in:
            self.background_alpha = min(255, self.background_alpha + 255 * dt / MENU_TRANSITION_SPEED)
            if self.background_alpha >= MENU_BACKGROUND_ALPHA:
                self.fade_in = False
                self.background_alpha = MENU_BACKGROUND_ALPHA

        self.scroll_position -= CREDITS_SCROLL_SPEED * dt

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                    return "main_menu"

        return None

    def draw(self, screen):
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((0, 0, 0, self.background_alpha))
        screen.blit(background, (0, 0))

        title_surf = self.title_font.render(CREDITS_TITLE, True, pygame.Color(MENU_TITLE_COLOR))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH / 2, 100))
        screen.blit(title_surf, title_rect)

        credits = [
            CREDITS_GAME_NAME,
            "",
            f"A game by {CREDITS_MASTERMIND}",
            "",
            "Programming",
            CREDITS_DEVELOPER,
            "",
            "Graphics & Design",
            CREDITS_GRAPHICS,
            "",
            "Sound & Music",
            CREDITS_SOUND,
            "",
            "Special thanks to",
        ]

        credits.extend(CREDITS_SPECIAL_THANKS)

        credits.extend(
            [
                "",
                f"Download & Updates: {CREDITS_WEBSITE}",
                "",
                "Thank you for playing!",
            ]
        )

        y = self.scroll_position
        for line in credits:
            text_surf = self.text_font.render(line, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH / 2, y))
            if y >= SCREEN_HEIGHT / 4:
                screen.blit(text_surf, text_rect)
            y += CREDITS_LINE_SPACING

        if y < 0:
            self.scroll_position = SCREEN_HEIGHT


class GameOverScreen:
    def __init__(self):
        self.title_font = pygame.font.Font(None, MENU_TITLE_FONT_SIZE)
        self.text_font = pygame.font.Font(None, MENU_ITEM_FONT_SIZE)
        self.background_alpha = 0
        self.fade_in = True
        self.final_score = 0

    def set_score(self, score):
        self.final_score = score

    def update(self, dt, events):
        if self.fade_in:
            self.background_alpha = min(255, self.background_alpha + 255 * dt / MENU_TRANSITION_SPEED)
            if self.background_alpha >= MENU_BACKGROUND_ALPHA:
                self.fade_in = False
                self.background_alpha = MENU_BACKGROUND_ALPHA

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    return "highscore_display"
                elif event.key == pygame.K_ESCAPE:
                    return "main_menu"
                elif event.key == pygame.K_r:
                    return "quick_restart"

        return None

    def draw(self, screen):
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((0, 0, 0, self.background_alpha))
        screen.blit(background, (0, 0))

        title_surf = self.title_font.render("GAME OVER", True, pygame.Color("red"))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3))
        screen.blit(title_surf, title_rect)

        score_surf = self.text_font.render(f"Your Score: {self.final_score}", True, (255, 255, 255))
        score_rect = score_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        screen.blit(score_surf, score_rect)

        instruction1 = self.text_font.render("Press SPACE to view the Highscores", True, (200, 200, 200))
        instruction1_rect = instruction1.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 60))
        screen.blit(instruction1, instruction1_rect)

        instruction2 = self.text_font.render("Press R to restart instantly", True, (200, 200, 200))
        instruction2_rect = instruction2.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100))
        screen.blit(instruction2, instruction2_rect)

        instruction3 = self.text_font.render("Press ESC to return to the Main Menu", True, (200, 200, 200))
        instruction3_rect = instruction3.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 140))
        screen.blit(instruction3, instruction3_rect)


class DifficultyMenu(Menu):
    def __init__(self):
        super().__init__("DIFFICULTY")
        self.add_item("Easy", "difficulty_easy", "L")
        self.add_item("Normal", "difficulty_normal", "N")
        self.add_item("Hard", "difficulty_hard", "S")
        self.add_item("Back", "main_menu", "Z")


class VoiceAnnouncementsMenu:
    """Menu to configure voice announcement toggles"""

    def __init__(self, settings):
        self.settings = settings
        self.title = "Voice Announcements"
        self.items = [
            MenuItem("Level Up: ON", "toggle_level_up"),
            MenuItem("Boss Incoming: ON", "toggle_boss_incoming"),
            MenuItem("Boss Defeated: ON", "toggle_boss_defeated"),
            MenuItem("Game Over: ON", "toggle_game_over"),
            MenuItem("Extra Life: ON", "toggle_extra_life"),
            MenuItem("Achievement: ON", "toggle_achievement"),
            MenuItem("High Score: ON", "toggle_high_score"),
            MenuItem("New Weapon: OFF", "toggle_new_weapon"),
            MenuItem("Shield Active: OFF", "toggle_shield_active"),
            MenuItem("Low Health: OFF", "toggle_low_health"),
            MenuItem("PowerUp: OFF", "toggle_powerup"),
            MenuItem("", None),
            MenuItem("Back", "back"),
        ]
        self.current_selection = 0
        self.fade_in = True
        self.background_alpha = 0
        self.update_menu_texts()

    def update_menu_texts(self):
        announcements = self.settings.announcement_types
        self.items[0].text = f"Level Up: {'ON' if announcements.get('level_up', True) else 'OFF'}"
        self.items[1].text = f"Boss Incoming: {'ON' if announcements.get('boss_incoming', True) else 'OFF'}"
        self.items[2].text = f"Boss Defeated: {'ON' if announcements.get('boss_defeated', True) else 'OFF'}"
        self.items[3].text = f"Game Over: {'ON' if announcements.get('game_over', True) else 'OFF'}"
        self.items[4].text = f"Extra Life: {'ON' if announcements.get('extra_life', True) else 'OFF'}"
        self.items[5].text = f"Achievement: {'ON' if announcements.get('achievement', True) else 'OFF'}"
        self.items[6].text = f"High Score: {'ON' if announcements.get('high_score', True) else 'OFF'}"
        self.items[7].text = f"New Weapon: {'ON' if announcements.get('new_weapon', False) else 'OFF'}"
        self.items[8].text = f"Shield Active: {'ON' if announcements.get('shield_active', False) else 'OFF'}"
        self.items[9].text = f"Low Health: {'ON' if announcements.get('low_health', False) else 'OFF'}"
        self.items[10].text = f"PowerUp: {'ON' if announcements.get('powerup', False) else 'OFF'}"

    def update(self, dt, events):
        if self.fade_in:
            self.background_alpha = min(255, self.background_alpha + 255 * dt / MENU_TRANSITION_SPEED)
            if self.background_alpha >= MENU_BACKGROUND_ALPHA:
                self.fade_in = False
                self.background_alpha = MENU_BACKGROUND_ALPHA

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.current_selection -= 1
                    if self.current_selection < 0:
                        self.current_selection = len(self.items) - 1
                    if self.items[self.current_selection].text == "":
                        self.current_selection -= 1
                        if self.current_selection < 0:
                            self.current_selection = len(self.items) - 1

                elif event.key == pygame.K_DOWN:
                    self.current_selection += 1
                    if self.current_selection >= len(self.items):
                        self.current_selection = 0
                    if self.items[self.current_selection].text == "":
                        self.current_selection += 1
                        if self.current_selection >= len(self.items):
                            self.current_selection = 0

                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    return self.items[self.current_selection].action

                elif event.key == pygame.K_ESCAPE:
                    return "back"

        return None

    def handle_action(self, action):
        if action == "back":
            return "options"

        # Toggle announcements
        announcement_map = {
            "toggle_level_up": "level_up",
            "toggle_boss_incoming": "boss_incoming",
            "toggle_boss_defeated": "boss_defeated",
            "toggle_game_over": "game_over",
            "toggle_extra_life": "extra_life",
            "toggle_achievement": "achievement",
            "toggle_high_score": "high_score",
            "toggle_new_weapon": "new_weapon",
            "toggle_shield_active": "shield_active",
            "toggle_low_health": "low_health",
            "toggle_powerup": "powerup",
        }

        if action in announcement_map:
            announcement_type = announcement_map[action]
            current_value = self.settings.announcement_types.get(announcement_type, True)
            self.settings.announcement_types[announcement_type] = not current_value
            self.settings.save()
            self.update_menu_texts()

        return None

    def draw(self, screen):
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((0, 0, 0, self.background_alpha))
        screen.blit(background, (0, 0))

        title_font = pygame.font.Font(None, MENU_TITLE_FONT_SIZE)
        title_surface = title_font.render(self.title, True, pygame.Color(MENU_TITLE_COLOR))
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH / 2, 60))
        screen.blit(title_surface, title_rect)

        font = pygame.font.Font(None, MENU_ITEM_FONT_SIZE)
        start_y = 130

        visible_count = 0
        for i, item in enumerate(self.items):
            if item.text == "":
                visible_count += 0.5
                continue

            y = start_y + visible_count * MENU_ITEM_SPACING
            is_selected = i == self.current_selection
            color = MENU_SELECTED_COLOR if is_selected else MENU_UNSELECTED_COLOR

            text_surface = font.render(item.text, True, pygame.Color(color))
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH / 2, y))
            screen.blit(text_surface, text_rect)

            visible_count += 1


class SoundTestMenu:
    def __init__(self):
        self.title = "SOUND TEST"
        self.sounds = None
        self.last_played = ""
        self.last_played_timer = 0

        self.scroll_offset = 0
        self.max_visible_items = 16
        self.current_selection = 0

        self.playing_all_sounds = False
        self.stop_all_sounds_thread = False

        self.sound_items = [
            ("Standard Shoot", "test_shoot"),
            ("Laser Shoot", "test_laser_shoot"),
            ("Rocket Shoot", "test_rocket_shoot"),
            ("Shotgun Shoot", "test_shotgun_shoot"),
            ("Triple Shoot", "test_triple_shoot"),
            ("", ""),
            ("Explosion", "test_explosion"),
            ("Player Hit", "test_player_hit"),
            ("PowerUp", "test_powerup"),
            ("Shield Activate", "test_shield_activate"),
            ("Weapon Pickup", "test_weapon_pickup"),
            ("", ""),
            ("Boss Spawn", "test_boss_spawn"),
            ("Boss Death", "test_boss_death"),
            ("Boss Attack", "test_boss_attack"),
            ("", ""),
            ("Level Up", "test_level_up"),
            ("Game Over", "test_game_over"),
            ("Menu Select", "test_menu_select"),
            ("Menu Confirm", "test_menu_confirm"),
            ("", ""),
            ("Test All Sounds", "test_all"),
            ("", ""),
            ("Back", "back"),
        ]

        self.update_visible_items()

        self.background_alpha = 0
        self.fade_in = False

    def activate(self):
        self.fade_in = True
        self.background_alpha = 0
        self.scroll_offset = 0
        self.current_selection = 0
        self.stop_all_sounds_thread = False
        self.playing_all_sounds = False
        self.update_visible_items()

    def set_sounds(self, sounds):
        self.sounds = sounds

    def update_visible_items(self):
        self.visible_items = []
        start_index = self.scroll_offset
        end_index = min(start_index + self.max_visible_items, len(self.sound_items))

        for i in range(start_index, end_index):
            self.visible_items.append(self.sound_items[i])

        if self.current_selection >= len(self.visible_items):
            self.current_selection = max(0, len(self.visible_items) - 1)
        if self.current_selection < 0:
            self.current_selection = 0

    def update(self, dt, events):
        if self.fade_in:
            self.background_alpha = min(255, self.background_alpha + 255 * dt / MENU_TRANSITION_SPEED)
            if self.background_alpha >= MENU_BACKGROUND_ALPHA:
                self.fade_in = False
                self.background_alpha = MENU_BACKGROUND_ALPHA

        if self.last_played_timer > 0:
            self.last_played_timer -= dt
            if self.last_played_timer <= 0:
                self.last_played = ""

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.current_selection -= 1

                    if self.current_selection < 0:
                        if self.scroll_offset > 0:
                            self.scroll_offset -= 1
                            self.current_selection = 0
                            self.update_visible_items()
                        else:
                            self.scroll_offset = max(0, len(self.sound_items) - self.max_visible_items)
                            self.current_selection = min(
                                self.max_visible_items - 1, len(self.sound_items) - 1 - self.scroll_offset
                            )
                            self.update_visible_items()

                elif event.key == pygame.K_DOWN:
                    self.current_selection += 1

                    if self.current_selection >= len(self.visible_items):
                        if self.scroll_offset + self.max_visible_items < len(self.sound_items):
                            self.scroll_offset += 1
                            self.current_selection = len(self.visible_items) - 1
                            self.update_visible_items()
                        else:
                            self.scroll_offset = 0
                            self.current_selection = 0
                            self.update_visible_items()

                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    if 0 <= self.current_selection < len(self.visible_items):
                        return self.visible_items[self.current_selection][1]

                elif event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:

                    if self.playing_all_sounds:
                        self.stop_all_sounds_thread = True
                        self.playing_all_sounds = False
                        self.last_played = ""
                    return "back"

        return None

    def handle_action(self, action):
        if not self.sounds:
            return None

        if action == "test_shoot":
            self.sounds.play_shoot()
            self.last_played = "Standard Shoot played"
            self.last_played_timer = 2.0

        elif action == "test_laser_shoot":
            if hasattr(self.sounds, "play_laser_shoot"):
                self.sounds.play_laser_shoot()
            else:
                self.sounds.play_shoot()
            self.last_played = "Laser Shoot played"
            self.last_played_timer = 2.0

        elif action == "test_rocket_shoot":
            if hasattr(self.sounds, "play_rocket_shoot"):
                self.sounds.play_rocket_shoot()
            else:
                self.sounds.play_shoot()
            self.last_played = "Rocket Shoot played"
            self.last_played_timer = 2.0

        elif action == "test_shotgun_shoot":
            if hasattr(self.sounds, "play_shotgun_shoot"):
                self.sounds.play_shotgun_shoot()
            else:
                self.sounds.play_shoot()
            self.last_played = "Shotgun Shoot played"
            self.last_played_timer = 2.0

        elif action == "test_triple_shoot":
            if hasattr(self.sounds, "play_triple_shoot"):
                self.sounds.play_triple_shoot()
            else:
                self.sounds.play_shoot()
            self.last_played = "Triple Shoot played"
            self.last_played_timer = 2.0

        elif action == "test_explosion":
            self.sounds.play_explosion()
            self.last_played = "Explosion played"
            self.last_played_timer = 2.0

        elif action == "test_player_hit":
            self.sounds.play_player_hit()
            self.last_played = "Player Hit played"
            self.last_played_timer = 2.0

        elif action == "test_powerup":
            self.sounds.play_powerup()
            self.last_played = "PowerUp played"
            self.last_played_timer = 2.0

        elif action == "test_shield_activate":
            self.sounds.play_shield_activate()
            self.last_played = "Shield Activate played"
            self.last_played_timer = 2.0

        elif action == "test_weapon_pickup":
            if hasattr(self.sounds, "play_weapon_pickup"):
                self.sounds.play_weapon_pickup()
            else:
                self.sounds.play_powerup()
            self.last_played = "Weapon Pickup played"
            self.last_played_timer = 2.0

        elif action == "test_boss_spawn":
            self.sounds.play_boss_spawn()
            self.last_played = "Boss Spawn played"
            self.last_played_timer = 2.0

        elif action == "test_boss_death":
            self.sounds.play_boss_death()
            self.last_played = "Boss Death played"
            self.last_played_timer = 2.0

        elif action == "test_boss_attack":
            if hasattr(self.sounds, "play_boss_attack"):
                self.sounds.play_boss_attack()
            else:
                self.sounds.play_explosion()
            self.last_played = "Boss Attack played"
            self.last_played_timer = 2.0

        elif action == "test_level_up":
            self.sounds.play_level_up()
            self.last_played = "Level Up played"
            self.last_played_timer = 2.0

        elif action == "test_game_over":
            self.sounds.play_game_over()
            self.last_played = "Game Over played"
            self.last_played_timer = 2.0

        elif action == "test_menu_select":
            self.sounds.play_menu_move()
            self.last_played = "Menu Select played"
            self.last_played_timer = 2.0

        elif action == "test_menu_confirm":
            self.sounds.play_menu_select()
            self.last_played = "Menu Confirm played"
            self.last_played_timer = 2.0

        elif action == "test_all":
            import threading
            import time

            def play_all_sounds():
                sound_list = [
                    ("Standard Shoot", self.sounds.play_shoot),
                    ("Explosion", self.sounds.play_explosion),
                    ("Player Hit", self.sounds.play_player_hit),
                    ("PowerUp", self.sounds.play_powerup),
                    ("Level Up", self.sounds.play_level_up),
                    ("Game Over", self.sounds.play_game_over),
                ]

                for name, sound_func in sound_list:
                    if self.stop_all_sounds_thread:
                        break
                    try:
                        sound_func()
                        time.sleep(0.8)
                    except:
                        pass

                self.playing_all_sounds = False

            if not self.playing_all_sounds:
                self.playing_all_sounds = True
                self.stop_all_sounds_thread = False
                threading.Thread(target=play_all_sounds, daemon=True).start()
                self.last_played = "Playing all sounds..."
                self.last_played_timer = 8.0

        elif action == "back":

            if self.playing_all_sounds:
                self.stop_all_sounds_thread = True
                self.playing_all_sounds = False
                self.last_played = ""
            return "options"

        return None

    def draw(self, screen):
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((0, 0, 0, self.background_alpha))
        screen.blit(background, (0, 0))

        title_font = pygame.font.Font(None, MENU_TITLE_FONT_SIZE)
        title_surface = title_font.render(self.title, True, pygame.Color(MENU_TITLE_COLOR))
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH / 2, 60))
        screen.blit(title_surface, title_rect)

        indicator_font = pygame.font.Font(None, int(MENU_ITEM_FONT_SIZE * 0.7))

        if self.scroll_offset > 0:
            up_text = indicator_font.render("Scroll UP", True, pygame.Color("yellow"))
            up_rect = up_text.get_rect(center=(SCREEN_WIDTH / 2, 100))
            screen.blit(up_text, up_rect)

        if self.scroll_offset + self.max_visible_items < len(self.sound_items):
            down_text = indicator_font.render("Scroll DOWN", True, pygame.Color("yellow"))
            down_rect = down_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 100))
            screen.blit(down_text, down_rect)

        font = pygame.font.Font(None, MENU_ITEM_FONT_SIZE)
        small_font = pygame.font.Font(None, int(MENU_ITEM_FONT_SIZE * 0.9))
        start_y = 130

        visible_item_count = 0

        for i, (text, action) in enumerate(self.visible_items):
            current_y = start_y + visible_item_count * 35

            if text == "":
                visible_item_count += 0.3
                continue

            is_selected = i == self.current_selection

            base_color = MENU_UNSELECTED_COLOR
            if "Shoot" in text:
                base_color = "lightblue"
            elif text in ["Explosion", "Player Hit", "PowerUp", "Shield Activate", "Weapon Pickup"]:
                base_color = "lightgreen"
            elif "Boss" in text:
                base_color = "orange"
            elif text in ["Level Up", "Game Over", "Menu Select", "Menu Confirm"]:
                base_color = "yellow"
            elif text == "Test All Sounds":
                base_color = "magenta"
            elif text == "Back":
                base_color = "white"

            if is_selected:
                color = MENU_SELECTED_COLOR
                scaled_font = pygame.font.Font(None, int(MENU_ITEM_FONT_SIZE * 1.1))
                surface = scaled_font.render(f"► {text}", True, pygame.Color(color))
            else:
                color = base_color
                surface = small_font.render(f"  {text}", True, pygame.Color(color))

            text_rect = surface.get_rect(center=(SCREEN_WIDTH / 2, current_y))
            screen.blit(surface, text_rect)

            visible_item_count += 1

        if self.last_played:
            played_font = pygame.font.Font(None, int(MENU_ITEM_FONT_SIZE * 0.8))

            played_text = played_font.render(self.last_played, True, pygame.Color("lightgreen"))
            played_rect = played_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 128))
            screen.blit(played_text, played_rect)

        instructions = ["UP / DOWN to Navigate - ENTER to play sound - SPACE to go back"]

        instruction_font = pygame.font.Font(None, int(MENU_ITEM_FONT_SIZE * 0.65))
        for i, instruction in enumerate(instructions):
            text = instruction_font.render(instruction, True, pygame.Color("lightgray"))
            text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 70 + i * 25))
            screen.blit(text, text_rect)


class AchievementsMenu(Menu):
    def __init__(self, achievement_system):
        super().__init__("AJITROIDS - ACHIEVEMENTS")
        self.achievement_system = achievement_system
        self.add_item("Back", "back")

        self.achievement_graphics = {
            "First Blood": [" *** ", "*.*.*", ".***.", "*.*.*", " *** "],
            "Survivor": [" *** ", "*...*", "*.*.*", "*...*", " *** "],
            "Asteroid Hunter": [" *** ", "*...*", "*.*.*", "*...*", " *** "],
            "Power User": [" *** ", "*.*.*", "*...*", "*.*.*", " *** "],
            "Boss Slayer": [" **** ", "*....*", "*.--.*", "*.**.*", " *** "],
            "Level Master": [" *** ", "*---*", "*.*.*", "*---*", " *** "],
            "High Scorer": [" *** ", "*.*.*", "*...*", "*.*.*", " *** "],
            "Shield Expert": [" *** ", "*...*", "*.*.*", "*.^.*", " *** "],
            "Speed Demon": [" *** ", "*---*", "*===*", "*---*", " *** "],
            "Triple Threat": [" * * ", "* * *", "* * *", "* * *", " * * "],
            "Fleet Commander": ["  *  ", " *** ", "*****", " *** ", "  *  "],
        }

    def draw(self, screen):
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((0, 0, 0, self.background_alpha))
        screen.blit(background, (0, 0))

        title_surf = self.title_font.render(self.title, True, pygame.Color(MENU_TITLE_COLOR))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 12))
        screen.blit(title_surf, title_rect)

        start_y = SCREEN_HEIGHT / 5
        achievement_spacing = 80
        graphics_font = pygame.font.Font(None, 18)
        name_font = pygame.font.Font(None, 28)

        achievements_per_column = 6
        column_width = SCREEN_WIDTH / 2
        left_column_x = column_width / 2
        right_column_x = column_width + column_width / 2

        for i, achievement in enumerate(self.achievement_system.achievements):
            if i >= 12:
                break

            column = i // achievements_per_column
            row = i % achievements_per_column

            if column == 0:
                center_x = left_column_x
            else:
                center_x = right_column_x

            current_y = start_y + row * achievement_spacing
            is_unlocked = achievement.unlocked

            if is_unlocked:
                name_color = pygame.Color("green")
                graphic_color = pygame.Color("lightgreen")
            else:
                name_color = pygame.Color("gray")

            if is_unlocked and achievement.name in self.achievement_graphics:
                graphics = self.achievement_graphics[achievement.name]

                ascii_start_x = center_x - 120

                for line_idx, line in enumerate(graphics):
                    graphic_surf = graphics_font.render(line, True, graphic_color)
                    graphic_rect = graphic_surf.get_rect(topleft=(ascii_start_x, current_y - 8 + line_idx * 10))
                    screen.blit(graphic_surf, graphic_rect)

                name_x = center_x - 20
            else:
                name_surf_temp = name_font.render(achievement.name, True, name_color)
                name_x = center_x - name_surf_temp.get_width() / 2

            name_surf = name_font.render(achievement.name, True, name_color)
            name_rect = name_surf.get_rect(topleft=(name_x, current_y))
            screen.blit(name_surf, name_rect)

        back_button_y = SCREEN_HEIGHT - 80
        for i, item in enumerate(self.items):
            item_rect = item.draw(screen, (SCREEN_WIDTH / 2, back_button_y + i * MENU_ITEM_SPACING), self.item_font)

        unlocked_count = sum(1 for achievement in self.achievement_system.achievements if achievement.unlocked)
        total_count = len(self.achievement_system.achievements)
        progress_text = f"Progress: {unlocked_count}/{total_count} Achievements unlocked"
        progress_font = pygame.font.Font(None, 20)
        progress_surf = progress_font.render(progress_text, True, pygame.Color("lightblue"))
        progress_rect = progress_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 12 + 35))
        screen.blit(progress_surf, progress_rect)

    def update(self, dt, events):
        result = super().update(dt, events)
        if result:
            return result

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                    return "back"

        return None


class ShipSelectionMenu(Menu):
    def __init__(self):
        super().__init__("SHIP SELECTION")
        self.selected_ship_index = 0
        self.ships = ship_manager.get_available_ships()
        self.animation_time = 0

    def activate(self):
        super().activate()
        self.selected_ship_index = 0
        self.ships = ship_manager.get_available_ships()

        try:
            self.selected_ship_index = self.ships.index(ship_manager.current_ship)
        except ValueError:
            self.selected_ship_index = 0

    def update(self, dt, events):
        self.animation_time += dt

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.selected_ship_index = (self.selected_ship_index - 1) % len(self.ships)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.selected_ship_index = (self.selected_ship_index + 1) % len(self.ships)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    selected_ship = self.ships[self.selected_ship_index]
                    ship_data = ship_manager.get_ship_data(selected_ship)
                    if ship_data["unlocked"]:
                        ship_manager.set_current_ship(selected_ship)
                        return "start_game"
                elif event.key == pygame.K_ESCAPE:
                    return "difficulty_select"

        return None

    def draw(self, screen):
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((0, 0, 0, self.background_alpha))
        screen.blit(background, (0, 0))

        title_surf = self.title_font.render(self.title, True, pygame.Color(MENU_TITLE_COLOR))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH / 2, 80))
        screen.blit(title_surf, title_rect)

        ship_y = SCREEN_HEIGHT / 2 - 50
        ship_spacing = 200
        start_x = SCREEN_WIDTH / 2 - (len(self.ships) - 1) * ship_spacing / 2

        for i, ship_id in enumerate(self.ships):
            ship_data = ship_manager.get_ship_data(ship_id)
            x = start_x + i * ship_spacing

            if i == self.selected_ship_index:
                highlight_size = 80 + 10 * math.sin(self.animation_time * 4)
                pygame.draw.circle(screen, (100, 100, 100, 100), (int(x), int(ship_y)), int(highlight_size), 3)

            if ship_data["unlocked"]:

                base_color = ship_data.get("color", (255, 255, 255))
                if i == self.selected_ship_index:

                    ship_color = tuple(min(255, int(c * 1.3)) for c in base_color)
                else:
                    ship_color = base_color
                ShipRenderer.draw_ship(screen, x, ship_y, 0, ship_data["shape"], 2.0, ship_color)
            else:

                lock_color = (100, 100, 100) if i != self.selected_ship_index else (150, 150, 150)
                ShipRenderer.draw_question_mark(screen, x, ship_y, 2.0, lock_color)

            name_font = pygame.font.Font(None, 24)
            if ship_data["unlocked"]:

                base_color = ship_data.get("color", (255, 255, 255))
                if i == self.selected_ship_index:
                    name_color = tuple(min(255, int(c * 1.3)) for c in base_color)
                else:
                    name_color = base_color
                name_text = ship_data["name"]
            else:
                name_color = (100, 100, 100)
                name_text = "LOCKED"

            name_surf = name_font.render(name_text, True, name_color)
            name_rect = name_surf.get_rect(center=(x, ship_y + 60))
            screen.blit(name_surf, name_rect)

        selected_ship = self.ships[self.selected_ship_index]
        ship_data = ship_manager.get_ship_data(selected_ship)

        detail_y = SCREEN_HEIGHT - 200
        detail_font = pygame.font.Font(None, 28)
        small_font = pygame.font.Font(None, 24)

        if ship_data["unlocked"]:

            desc_surf = detail_font.render(ship_data["description"], True, (255, 255, 255))
            desc_rect = desc_surf.get_rect(center=(SCREEN_WIDTH / 2, detail_y))
            screen.blit(desc_surf, desc_rect)

            props = [
                f"Speed: {ship_data['speed_multiplier']:.1f}x",
                f"Agility: {ship_data['turn_speed_multiplier']:.1f}x",
                f"Special: {ship_data['special_ability'].replace('_', ' ').title()}",
            ]

            for i, prop in enumerate(props):
                prop_surf = small_font.render(prop, True, (200, 200, 200))
                prop_rect = prop_surf.get_rect(center=(SCREEN_WIDTH / 2, detail_y + 40 + i * 25))
                screen.blit(prop_surf, prop_rect)

        instruction_font = pygame.font.Font(None, 20)
        instructions = ["LEFT / RIGHT: Select Ship", "ENTER / SPACE: Confirm Selection", "ESC: Back to Difficulty"]

        for i, instruction in enumerate(instructions):
            instr_surf = instruction_font.render(instruction, True, (150, 150, 150))
            instr_rect = instr_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 60 + i * 20))
            screen.blit(instr_surf, instr_rect)
