"""Module modul.menu — minimal module docstring."""

import math
import pygame
import modul.constants as C
from modul.version import __version__
from modul.ships import ShipRenderer, ship_manager
from modul import input_utils

# Backwards-compatibility: expose uppercase constants into module globals
for _const_name in dir(C):
    if _const_name.isupper():
        globals()[_const_name] = getattr(C, _const_name)

SOUNDS = None

# Menu-related constants (add or adjust as needed)
CREDITS_SCROLL_SPEED = 40  # pixels per second (adjust to desired scroll speed)


def _gettext(key):
    """
    Translate the given key using modul.i18n.gettext, falling back to the key if translation is unavailable.
    
    Parameters:
        key (str): The lookup key for the translated string.
    
    Returns:
        The translated string for `key`, or `key` itself if no translation provider is available.
    """
    try:
        from modul.i18n import gettext as _g
        return _g(key)
    except Exception:
        return key

# Backwards-compatibility: expose a `gettext` name to call the helper
gettext = _gettext


class MenuItem:
    """Represents a selectable item in a menu."""
    def __init__(self, text, action, shortcut=None):
        """
        Create a MenuItem representing a selectable menu entry.
        
        Parameters:
            text (str): Display string shown for the menu item.
            action (str): Identifier returned when the item is activated.
            shortcut (str | None): Optional short key label shown/used for quick activation (e.g., "Z", "L"). When None, no shortcut is associated.
        
        Notes:
            Initializes selection state and visual properties:
            - selected: False
            - hover_animation: 0
            - opacity: 255
            - delay: 0
        """
        self.text = text
        self.action = action
        self.selected = False
        self.hover_animation = 0
        self.opacity = 255
        self.delay = 0
        self.shortcut = shortcut

    def update(self, dt):
        """
        Update the menu item's hover animation and resolve its opacity delay.
        
        Parameters:
            dt (float): Time elapsed in seconds since the last update.
        """
        target = 1.0 if self.selected else 0.0
        animation_speed = 12.0
        self.hover_animation = self.hover_animation + (target - self.hover_animation) * dt * animation_speed
        if self.delay > 0:
            self.delay -= dt
            if self.delay <= 0:
                self.delay = 0
                self.opacity = 255

    def draw(self, screen, position, font=None):
        """
        Render this menu item's text centered at the given position.
        
        Parameters:
            position (tuple): (x, y) coordinates used as the center point for the rendered text.
            font (pygame.font.Font | None): Optional font to use; if None a font scaled by the item's hover animation is created.
        
        Returns:
            pygame.Rect: Rectangle of the rendered text (positioned with its center at `position`).
        """
        color = pygame.Color(C.MENU_UNSELECTED_COLOR)
        selected_color = pygame.Color(C.MENU_SELECTED_COLOR)
        r = max(0, min(255, int(color.r + (selected_color.r - color.r) * self.hover_animation)))
        g = max(0, min(255, int(color.g + (selected_color.g - color.g) * self.hover_animation)))
        b = max(0, min(255, int(color.b + (selected_color.b - color.b) * self.hover_animation)))
        size_multiplier = 1.0 + 0.2 * self.hover_animation
        if font is None:
            scaled_font = pygame.font.Font(None, int(C.MENU_ITEM_FONT_SIZE * size_multiplier))
        else:
            scaled_font = font
        text_surface = scaled_font.render(self.text, True, (r, g, b))
        text_rect = text_surface.get_rect(center=(position[0], position[1]))
        screen.blit(text_surface, text_rect)
        return text_rect


class Menu:
    """Base class for game menus with selectable items."""
    def __init__(self, title, sounds=None):
        """
        Create a Menu with the given title and optional sounds controller.
        
        Parameters:
            title (str): The menu's displayed title.
            sounds (optional): An object providing menu sound effects; may be None.
        """
        self.title = title
        self.items = []
        self.selected_index = 0
        self.background_alpha = 0
        self.title_font = pygame.font.Font(None, C.MENU_TITLE_FONT_SIZE)
        self.item_font = pygame.font.Font(None, C.MENU_ITEM_FONT_SIZE)
        self.active = False
        self.fade_in = False
        self.input_cooldown = 0
        self.sounds = sounds

    def add_item(self, text, action, shortcut=None):
        """
        Append a selectable entry to the menu.
        
        If this is the first item added, it becomes the selected item.
        
        Parameters:
            text (str): Display label for the menu item.
            action (str): Action identifier returned when the item is activated.
            shortcut (str | None): Optional shortcut label shown for the item.
        """
        item = MenuItem(text, action, shortcut)
        self.items.append(item)
        if len(self.items) == 1:
            self.items[0].selected = True

    def activate(self):
        """
        Enable the menu and begin its fade-in reveal.
        
        Sets the menu active, starts the fade-in state, resets the background alpha to 0, and initializes each item's opacity to 0 with a staggered reveal delay.
        """
        self.active = True
        self.fade_in = True
        self.background_alpha = 0
        for i, item in enumerate(self.items):
            item.opacity = 0
            item.delay = i * 0.1

    def update(self, dt, events):
        """
        Update menu animation, process input events, and advance selection state.
        
        Parameters:
            dt (float): Time elapsed since the last update, in seconds.
            events (iterable): Iterable of pygame event objects to consume for navigation and selection.
        
        Returns:
            action (str or dict or None): The selected menu action identifier (or a dict with navigation details) when an item is activated, or `None` if no action was triggered.
        """
        if self.fade_in:
            self.background_alpha = min(255, self.background_alpha + 255 * dt / C.MENU_TRANSITION_SPEED)
            if self.background_alpha >= C.MENU_BACKGROUND_ALPHA:
                self.fade_in = False
                self.background_alpha = C.MENU_BACKGROUND_ALPHA

        for item in self.items:
            item.update(dt)

        if self.input_cooldown > 0:
            self.input_cooldown -= dt

        shoot_key = input_utils.get_action_keycode("shoot")

        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.input_cooldown <= 0:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self._select_previous()
                        self.input_cooldown = 0.15
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self._select_next()
                        self.input_cooldown = 0.15
                    elif (event.key == pygame.K_RETURN or event.key == pygame.K_SPACE
                          or (shoot_key is not None and event.key == shoot_key)):
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
        """Select the next menu item."""
        self.items[self.selected_index].selected = False
        self.selected_index = (self.selected_index + 1) % len(self.items)
        self.items[self.selected_index].selected = True
        if hasattr(self, "sounds") and self.sounds:
            try:
                self.sounds.play_menu_move()
            except Exception as e:
                logger = getattr(self, 'logger', None)
                if logger is None:
                    import logging
                    logger = logging.getLogger(__name__)
                logger.debug("Exception in play_menu_move in _select_next: %s", e, exc_info=True)

    def _select_previous(self):
        """
        Move selection to the previous menu item, wrapping to the end if currently at the first item.
        
        Updates the previously selected item's state and the newly selected item's state accordingly. If a `sounds` attribute is present, attempts to play the menu-move sound and logs any exception at debug level.
        """
        self.items[self.selected_index].selected = False
        self.selected_index = (self.selected_index - 1) % len(self.items)
        self.items[self.selected_index].selected = True
        if hasattr(self, "sounds") and self.sounds:
            try:
                self.sounds.play_menu_move()
            except Exception as e:
                logger = getattr(self, 'logger', None)
                if logger is None:
                    import logging
                    logger = logging.getLogger(__name__)
                logger.debug("Exception in play_menu_move in _select_previous: %s", e, exc_info=True)

    def draw(self, screen):
        """
        Render the menu: a translucent background, a centered title near the top, and all menu items centered horizontally and distributed vertically.
        
        Parameters:
            screen (pygame.Surface): Destination surface to draw the menu onto.
        """
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((0, 0, 0, self.background_alpha))
        screen.blit(background, (0, 0))

        title_surf = self.title_font.render(self.title, True, pygame.Color(C.MENU_TITLE_COLOR))
        title_rect = title_surf.get_rect(center=(C.SCREEN_WIDTH / 2, C.SCREEN_HEIGHT / 8))
        screen.blit(title_surf, title_rect)

        # Center items vertically so long lists still fit
        total_height = (len(self.items) - 1) * C.MENU_ITEM_SPACING
        start_y = C.SCREEN_HEIGHT / 2 - total_height / 2
        for i, item in enumerate(self.items):
            position = (C.SCREEN_WIDTH / 2, start_y + i * C.MENU_ITEM_SPACING)
            item.draw(screen, position)


class MainMenu(Menu):
    """Main menu for the game."""
    def __init__(self):
        """
        Create the main menu and populate it with primary navigation entries.
        
        Sets the menu title to "AJITROIDS" and adds localized items for: start game, tutorial, replays, highscores, statistics, achievements, options, credits, and exit.
        """
        super().__init__("AJITROIDS")
        self.add_item(gettext("start_game"), "start_game")
        self.add_item(gettext("tutorial"), "tutorial")
        self.add_item(gettext("replays"), "replays")
        self.add_item(gettext("highscores"), "highscores")
        self.add_item(gettext("statistics"), "statistics")
        self.add_item(gettext("achievements"), "achievements")
        self.add_item(gettext("options"), "options")
        self.add_item(gettext("credits"), "credits")
        self.add_item(gettext("exit"), "exit")

    def draw(self, screen):
        """
        Render the main menu and the game's version string at the bottom-right of the screen.
        
        Parameters:
            screen (pygame.Surface): Surface to draw the menu and version text onto.
        """
        super().draw(screen)

        version_font = pygame.font.Font(None, int(C.MENU_ITEM_FONT_SIZE / 1.5))
        version_text = version_font.render(__version__, True, pygame.Color(C.MENU_UNSELECTED_COLOR))
        version_rect = version_text.get_rect(bottomright=(C.SCREEN_WIDTH - 20, C.SCREEN_HEIGHT - 20))
        screen.blit(version_text, version_rect)


class PauseMenu(Menu):
    """Pause menu shown during gameplay."""
    def __init__(self):
        """
        Create the pause menu and populate it with localized resume, restart, and main menu entries.
        
        Sets the menu title to the translated "pause" (uppercased) and adds items labeled with the localized strings for resume, restart, and main menu that trigger actions "continue", "restart", and "main_menu" respectively.
        """
        title = _gettext("pause").upper()
        super().__init__(title)
        self.add_item(gettext("resume"), "continue")
        self.add_item(gettext("restart"), "restart")
        self.add_item(gettext("main_menu"), "main_menu")

    def draw(self, screen):
        """
        Render the pause menu and a list of common keyboard shortcuts.
        
        Parameters:
            screen (pygame.Surface): Surface to draw the menu and shortcuts onto.
        """
        super().draw(screen)

        # Show common keyboard shortcuts while paused
        shortcuts_font = pygame.font.Font(None, int(C.MENU_ITEM_FONT_SIZE * 0.8))
        # Use module-level gettext helper

        shortcuts = [
            gettext("shortcut_arrow_up_accelerate"),
            gettext("shortcut_arrow_turn"),
            gettext("shortcut_arrow_down_reverse"),
            gettext("shortcut_space_shoot"),
            gettext("shortcut_esc_pause"),
            gettext("shortcut_b_switch"),
            gettext("shortcut_r_restart"),
            gettext("shortcut_f1_help"),
            gettext("shortcut_f8_fps"),
            gettext("shortcut_f9_sfx"),
            gettext("shortcut_f10_music"),
            gettext("shortcut_f11_fullscreen"),
            gettext("shortcut_f12_profiler"),
            gettext("shortcut_p_screenshot"),
        ]

        shortcuts_x = 30
        shortcuts_y = 150
        for i, shortcut in enumerate(shortcuts):
            shortcut_surf = shortcuts_font.render(shortcut, True, (200, 200, 200))
            screen.blit(shortcut_surf, (shortcuts_x, shortcuts_y + i * 35))


class TutorialScreen:
    """Screen displaying tutorial instructions."""
    def __init__(self):
        """Initialize fonts and state for the tutorial screen."""
        self.title_font = pygame.font.Font(None, C.MENU_TITLE_FONT_SIZE)
        self.text_font = pygame.font.Font(None, C.MENU_ITEM_FONT_SIZE)
        self.background_alpha = 0
        self.fade_in = True

    def update(self, dt, events):
        """
        Handle the tutorial screen's fade-in transition and keyboard input.
        
        Parameters:
            dt (float): Time elapsed since the last update, in seconds.
            events (iterable): Iterable of pygame events to process.
        
        Returns:
            str or None: "main_menu" if the user pressed Escape to return to the main menu, `None` otherwise.
        """
        if self.fade_in:
            self.background_alpha = min(255, self.background_alpha + 255 * dt / C.MENU_TRANSITION_SPEED)
            if self.background_alpha >= C.MENU_BACKGROUND_ALPHA:
                self.background_alpha = C.MENU_BACKGROUND_ALPHA
                self.fade_in = False
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "main_menu"

        return None

    def draw(self, screen):
        """
        Render the tutorial screen: a translucent background, localized title, and centered instruction lines.
        
        Parameters:
            screen (pygame.Surface): Destination surface to draw the tutorial UI onto.
        """
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((0, 0, 0, self.background_alpha))
        screen.blit(background, (0, 0))

        title_surf = self.title_font.render(gettext("tutorial_title"), True, pygame.Color(C.MENU_TITLE_COLOR))
        title_rect = title_surf.get_rect(center=(C.SCREEN_WIDTH / 2, 100))
        screen.blit(title_surf, title_rect)

        instructions = [
            gettext("tutorial_move"),
            gettext("tutorial_rotate"),
            gettext("tutorial_rotate_right"),
            gettext("tutorial_thrust"),
            gettext("tutorial_shoot"),
            gettext("tutorial_pause"),
            "",
            gettext("tutorial_objective"),
            gettext("tutorial_shield"),
            gettext("tutorial_tripleshot"),
            gettext("tutorial_rapidfire"),
            "",
            gettext("tutorial_nav"),
        ]
        y = 180
        for line in instructions:
            text_surf = self.text_font.render(line, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(C.SCREEN_WIDTH / 2, y))
            screen.blit(text_surf, text_rect)
            y += 40


class OptionsMenu(Menu):
    """Menu for adjusting game options and settings."""
    def __init__(self, settings, sounds):
        """
        Create an Options menu populated from the provided settings and optional sounds.
        
        The constructor builds menu items that reflect the current settings (music on/off and volume, sound on/off and volume, fullscreen state, language) and conditionally includes a toggle for showing TTS options if the settings object exposes `show_tts_in_options`.
        
        Parameters:
            settings: An object exposing at least the attributes `music_on` (bool), `sound_on` (bool),
                `music_volume` (float, 0.0–1.0), `sound_volume` (float, 0.0–1.0), `fullscreen` (bool),
                and `language` (str). If present, `show_tts_in_options` (bool) is used to add a TTS toggle item.
            sounds: Optional sounds manager used for UI feedback; may be None.
        """
        super().__init__("OPTIONS")
        self.settings = settings
        self.sounds = sounds
        # Use module-level gettext helper

        music_state = gettext("on") if settings.music_on else gettext("off")
        sound_state = gettext("on") if settings.sound_on else gettext("off")
        self.add_item(f"{gettext('music')}: {music_state}", "toggle_music")
        self.add_item(f"{gettext('sound')}: {sound_state}", "toggle_sound")
        self.add_item(gettext('music_volume_format').format(percent=int(settings.music_volume * 100)), "adjust_music_volume")
        self.add_item(gettext('sound_volume_format').format(percent=int(settings.sound_volume * 100)), "adjust_sound_volume")
        self.add_item(gettext('fullscreen_on') if settings.fullscreen else gettext('fullscreen_off'), "toggle_fullscreen")
        self.add_item(gettext('controls_menu_label'), "controls")
        # Small toggle: whether to show the TTS voice selection directly in Options
        # Only add this toggle if the settings object actually exposes the
        # `show_tts_in_options` attribute so tests that don't include the
        # feature flag keep the original menu length.
        if "show_tts_in_options" in getattr(settings, "__dict__", {}):
            tts_toggle_state = gettext('on') if getattr(settings, 'show_tts_in_options', False) else gettext('off')
            self.add_item(f"{gettext('show_tts_in_options')}: {tts_toggle_state}", "toggle_show_tts")

        lang_label = gettext('language_label').format(lang=("Deutsch" if settings.language == "de" else "English"))
        self.add_item(lang_label, "language")
        self.add_item(gettext('back'), "back")

    def handle_action(self, action, sounds):
        """
        Handle an options-menu action by applying setting changes, updating menu text, and returning navigation targets when appropriate.
        
        Parameters:
            action (str): Action identifier from the selected menu item (e.g. "toggle_music", "adjust_sound_volume", "toggle_fullscreen", "toggle_show_tts", "language", "back", etc.).
        
        Returns:
            str or None: A navigation target string when the action requests a screen change (possible values include "voice_announcements", "tts_voice", "controls", "language", "sound_test", "main_menu"), or `None` when the action only updates settings or UI state.
        """
        # Use module-level gettext helper
        if action == "toggle_music":
            self.settings.music_on = not self.settings.music_on
            self.settings.save()
            sounds.toggle_music(self.settings.music_on)
            state = gettext('on') if self.settings.music_on else gettext('off')
            self.items[0].text = f"{gettext('music')}: {state}"
            return None

        elif action == "toggle_sound":
            self.settings.sound_on = not self.settings.sound_on
            self.settings.save()
            sounds.toggle_sound(self.settings.sound_on)
            state = gettext('on') if self.settings.sound_on else gettext('off')
            self.items[1].text = f"{gettext('sound')}: {state}"
            return None

        elif action == "adjust_music_volume":
            self.settings.music_volume = min(1.0, max(0.0, self.settings.music_volume + 0.1))
            self.settings.save()
            if self.sounds:
                self.sounds.set_music_volume(self.settings.music_volume)
            self.items[2].text = gettext('music_volume_format').format(percent=int(self.settings.music_volume * 100))
            return None

        elif action == "adjust_sound_volume":
            self.settings.sound_volume = min(1.0, max(0.0, self.settings.sound_volume + 0.1))
            self.settings.save()
            if self.sounds:
                self.sounds.set_effects_volume(self.settings.sound_volume)
            self.items[3].text = gettext('sound_volume_format').format(percent=int(self.settings.sound_volume * 100))
            return None

        elif action == "toggle_fullscreen":
            self.settings.fullscreen = not self.settings.fullscreen
            self.settings.save()

            try:
                if self.settings.fullscreen:
                    pygame.display.set_mode((C.SCREEN_WIDTH, C.SCREEN_HEIGHT), pygame.FULLSCREEN)
                    print("Fullscreen aktiviert")
                else:
                    pygame.display.set_mode((C.SCREEN_WIDTH, C.SCREEN_HEIGHT))
                    print("Windowed mode activated")
            except Exception as e:  # pylint: disable=broad-exception-caught
                print(f"Error switching screen mode: {e}")
                self.settings.fullscreen = not self.settings.fullscreen
                self.settings.save()

            self.items[4].text = gettext('fullscreen_on') if self.settings.fullscreen else gettext('fullscreen_off')
            return None

        elif action == "toggle_show_tts":
            # Toggle whether the TTS voice selection appears in Options
            self.settings.show_tts_in_options = not getattr(self.settings, 'show_tts_in_options', False)
            self.settings.save()
            try:
                state = gettext('on') if self.settings.show_tts_in_options else gettext('off')
            except Exception:  # pylint: disable=broad-exception-caught
                state = "ON" if self.settings.show_tts_in_options else "OFF"
            # Update the toggle item's text
            for i, it in enumerate(self.items):
                if it.action == 'toggle_show_tts':
                    self.items[i].text = f"{gettext('show_tts_in_options')}: {state}"
                    break

            # Insert or remove the live TTS entry in the options list
            try:
                from modul.tts import get_tts_manager
                mgr = get_tts_manager()
                has_voices = bool(mgr and getattr(mgr, 'engine', None) and (mgr.engine.getProperty('voices') or []))
            except Exception:  # pylint: disable=broad-exception-caught
                has_voices = False

            # Find existing tts item
            existing_index = None
            for idx, it in enumerate(self.items):
                if getattr(it, 'action', None) == 'tts_voice':
                    existing_index = idx
                    break

            if self.settings.show_tts_in_options and has_voices and existing_index is None:
                # insert before language item
                lang_index = next((i for i, it in enumerate(self.items) if it.action == 'language'), len(self.items))
                tts_display = getattr(self.settings, 'tts_voice', '') or gettext('default')
                self.items.insert(lang_index, MenuItem(f"{gettext('tts_voice_label')}: {tts_display}", 'tts_voice'))
            elif not self.settings.show_tts_in_options and existing_index is not None:
                self.items.pop(existing_index)

            return None

        elif action == "voice_announcements":
            return "voice_announcements"
        elif action == "tts_voice":
            return "tts_voice"

        elif action == "controls":
            return "controls"

        elif action == "language":
            return "language"

        elif action == "sound_test":
            return "sound_test"

        elif action == "back":
            return "main_menu"

        return None

    def update(self, dt, events):
        """
        Handle input for the options menu: adjust music/sound volume with left/right keys, save and apply changes, update item labels, and return navigation signals (e.g., escape to main menu).
        
        Parameters:
            dt (float): Time elapsed since last update in seconds.
            events (iterable): Iterable of pygame events to process.
        
        Returns:
            str or dict or None: A navigation action (for example, `"main_menu"`), a dict returned by delegated handlers, or `None` if no navigation change occurred.
        """
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
                        # use module-level gettext
                        self.items[self.selected_index].text = (
                            gettext('music_volume_format').format(
                                percent=int(self.settings.music_volume * 100)
                            )
                        )
                    elif self.items[self.selected_index].action == "adjust_sound_volume":
                        self.settings.sound_volume = max(0.0, self.settings.sound_volume - 0.1)
                        self.settings.save()
                        if self.sounds:
                            self.sounds.set_effects_volume(self.settings.sound_volume)
                        # use module-level gettext
                        self.items[self.selected_index].text = (
                            gettext('sound_volume_format').format(
                                percent=int(self.settings.sound_volume * 100)
                            )
                        )
                elif event.key == pygame.K_RIGHT:
                    if self.items[self.selected_index].action == "adjust_music_volume":
                        self.settings.music_volume = min(1.0, self.settings.music_volume + 0.1)
                        self.settings.save()
                        if self.sounds:
                            self.sounds.set_music_volume(self.settings.music_volume)
                        # use module-level gettext
                        self.items[self.selected_index].text = (
                            gettext('music_volume_format').format(
                                percent=int(self.settings.music_volume * 100)
                            )
                        )
                    elif self.items[self.selected_index].action == "adjust_sound_volume":
                        self.settings.sound_volume = min(1.0, self.settings.sound_volume + 0.1)
                        self.settings.save()
                        if self.sounds:
                            self.sounds.set_effects_volume(self.settings.sound_volume)
                        # use module-level gettext
                        self.items[self.selected_index].text = (
                            gettext('sound_volume_format').format(
                                percent=int(self.settings.sound_volume * 100)
                            )
                        )
        result = super().update(dt, events)
        if result:
            return result
        return None


class CreditsScreen:
    """Screen displaying game credits."""
    def __init__(self):
        """
        Set up fonts and initial visual state for the credits screen.
        
        Initializes the following attributes:
            title_font: Font used for the credits title.
            text_font: Font used for credits body text.
            background_alpha: Current background overlay alpha (starts at 0).
            fade_in: Whether the screen is currently fading in (starts True).
            scroll_position: Vertical position used to scroll the credits (start value 250).
        """
        self.title_font = pygame.font.Font(None, C.MENU_TITLE_FONT_SIZE)
        self.text_font = pygame.font.Font(None, C.MENU_ITEM_FONT_SIZE - 8)
        self.background_alpha = 0
        self.fade_in = True
        self.scroll_position = 250

    def update(self, dt, events):
        """
        Advance the credits scroll, update background fade-in, and handle input to exit to the main menu.
        
        Parameters:
            dt (float): Time elapsed since last update in seconds.
            events (iterable): Iterable of pygame events to process.
        
        Returns:
            str or None: `"main_menu"` if the user pressed Space or Escape to return to the main menu, `None` otherwise.
        """
        if self.fade_in:
            self.background_alpha = min(255, self.background_alpha + 255 * dt / C.MENU_TRANSITION_SPEED)
            if self.background_alpha >= C.MENU_BACKGROUND_ALPHA:
                self.background_alpha = C.MENU_BACKGROUND_ALPHA

        # Automatisches Scrollen der Credits
        self.scroll_position -= C.CREDITS_SCROLL_SPEED * dt

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                    return "main_menu"

        return None

    def draw(self, screen):
        """
        Render a translucent background, the credits title, and centered scrolling credit lines onto the provided screen.
        
        The credits block is positioned below the title and offset by self.scroll_position to produce vertical scrolling. The background opacity is taken from self.background_alpha and text uses the instance title and text fonts.
        
        Parameters:
            screen (pygame.Surface): Destination surface to draw the credits on.
        """
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((0, 0, 0, self.background_alpha))
        screen.blit(background, (0, 0))

        title_surf = self.title_font.render(C.CREDITS_TITLE, True, pygame.Color(C.MENU_TITLE_COLOR))
        title_rect = title_surf.get_rect(center=(C.SCREEN_WIDTH / 2, 100))
        screen.blit(title_surf, title_rect)

        credits_lines = [
            C.CREDITS_GAME_NAME,
            "",
            f"A game by {C.CREDITS_MASTERMIND}",
            "",
            "Programming",
            C.CREDITS_DEVELOPER,
            "",
            "Graphics & Design",
            C.CREDITS_GRAPHICS,
            "",
            "Sound & Music",
            C.CREDITS_SOUND,
            "",
            "Special thanks to",
        ]

        credits_lines.extend(C.CREDITS_SPECIAL_THANKS)

        credits_lines.extend(
            [
                "",
                f"Download & Updates: {C.CREDITS_WEBSITE}",
                "",
                "Thank you for playing!",
            ]
        )

        # Render each credits line centered below the title, with scrolling
        margin = 20
        line_spacing = self.text_font.get_linesize() + 4
        # start below the title and apply scroll position
        current_y = title_rect.bottom + margin + self.scroll_position
        for line in credits_lines:
            surf = self.text_font.render(line, True, pygame.Color("white"))
            rect = surf.get_rect(centerx=C.SCREEN_WIDTH / 2, y=current_y)
            screen.blit(surf, rect)
            current_y += line_spacing


class ControlsMenu(Menu):

    """Menu for remapping and displaying controls."""

    def _handle_capture_event(self, event):
        """
        Translate a pygame input event into a normalized binding name for control remapping.
        
        Parameters:
            event (pygame.Event): The input event to inspect (keyboard, joystick button/axis/hat).
        
        Returns:
            str: A binding name for the captured control, for example:
                 - keyboard key name (e.g., "space"),
                 - "JOY{joy}_BUTTON{btn}" (e.g., "JOY0_BUTTON1"),
                 - "JOY{joy}_AXIS{axis}_POS" or "..._NEG" (e.g., "JOY0_AXIS2_POS"),
                 - "JOY{joy}_HAT{hat}_{DIRS}" (e.g., "JOY0_HAT0_UP_RIGHT"),
                 or `None` if the event does not produce a captureable binding.
        """
        new_name = None
        # Keyboard binding
        if event.type == pygame.KEYDOWN:
            new_name = pygame.key.name(event.key)
        # Joystick button
        elif event.type == pygame.JOYBUTTONDOWN:
            try:
                joy_id = event.joy
                btn = event.button
                new_name = f"JOY{joy_id}_BUTTON{btn}"
            except Exception:
                new_name = None
        # Joystick axis (capture strong deflections)
        elif event.type == pygame.JOYAXISMOTION:
            try:
                val = event.value
                if abs(val) >= 0.6:
                    joy_id = event.joy
                    axis = event.axis
                    dir_s = "POS" if val > 0 else "NEG"
                    new_name = f"JOY{joy_id}_AXIS{axis}_{dir_s}"
            except Exception:
                new_name = None
        # Hat (D-pad)
        elif event.type == pygame.JOYHATMOTION:
            try:
                joy_id = event.joy
                hat = event.hat
                x, y = event.value
                if (x, y) != (0, 0):
                    dirs = []
                    if y == 1:
                        dirs.append("UP")
                    elif y == -1:
                        dirs.append("DOWN")
                    if x == 1:
                        dirs.append("RIGHT")
                    elif x == -1:
                        dirs.append("LEFT")
                    new_name = f"JOY{joy_id}_HAT{hat}_{'_'.join(dirs)}"
            except Exception:
                new_name = None
        return new_name

    def _is_duplicate_binding(self, new_name):
        """
        Check whether a proposed control binding is already assigned to any existing action.
        
        Parameters:
            new_name (str): The binding identifier to check (e.g. "K_SPACE", "JOY0_BUTTON1", or "JOY0_AXIS0_POS").
        
        Returns:
            `true` if the binding is already assigned to an action, `false` otherwise.
        """
        for a_key, _ in self.actions:
            if self.settings.controls.get(a_key) == new_name:
                return True
        return False

    def _apply_binding(self, action, new_name):
        """
        Apply a new input binding for an action and persist the change.
        
        This updates the stored control mapping for `action` to `new_name`, saves settings,
        stops key-capture mode, clears the pending capture action, and sets a user-facing
        message indicating the newly bound key.
        
        Parameters:
            action (str): The action identifier whose binding is being changed (e.g., "shoot").
            new_name (str): The canonical name of the new binding (e.g., "K_SPACE" or "JOY0_BUTTON1").
        """
        self.settings.controls[action] = new_name
        self.settings.save()
        self.capturing = False
        self.capture_action = None
        self.message = gettext("bound_key").format(key=new_name)

    def __init__(self, settings):
        """
        Create a controls menu populated with the current key bindings.
        
        Initializes the menu title from the localized "controls" label, adds one item per configured action (showing "<label>: <binding>"), appends a "back" item, and sets up capture state used for rebinding controls.
        
        Parameters:
            settings: An object exposing a `controls` mapping (action -> key name) used to read current bindings and persist changes.
        """
        super().__init__(gettext("controls").upper())
        self.settings = settings
        # Define action order for display
        # use module-level gettext helper

        self.actions = [
            ("rotate_left", gettext("rotate_left")),
            ("rotate_right", gettext("rotate_right")),
            ("thrust", gettext("thrust")),
            ("reverse", gettext("reverse")),
            ("shoot", gettext("shoot")),
            ("switch_weapon", gettext("switch_weapon")),
            ("pause", gettext("pause")),
        ]
        for action_key, label in self.actions:
            key_name = self.settings.controls.get(action_key, "")
            display = f"{label}: {key_name}"
            self.add_item(display, action_key)
        self.add_item(gettext("back"), "back")
        self.capturing = False
        self.capture_action = None
        self.message = ""

    def update(self, dt, events):
        # Refresh labels from settings
        """
        Handle input and update the controls menu state, including initiating and processing key-capture mode for rebinding controls.
        
        During a non-capturing state this processes navigation and selection; when a binding action is selected it enters capture mode and waits for a new control input. While capturing, pressing Escape cancels the capture. Successful captures update stored control bindings and the displayed labels.
        
        Parameters:
            dt (float): Time elapsed since the last update, in seconds.
            events (iterable): Iterable of pygame events to process.
        
        Returns:
            str or None: A navigation/action key (for example "options" to go back) when the menu requests navigation; `None` otherwise.
        
        Side effects:
            Updates menu item labels from self.settings.controls; may set or clear self.capturing, self.capture_action, and self.message; persists new bindings via settings when applied.
        """
        for i, (action_key, label) in enumerate(self.actions):
            key_name = self.settings.controls.get(action_key, "")
            self.items[i].text = f"{label}: {key_name}"

        if self.capturing:
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.capturing = False
                    self.capture_action = None
                    self.message = gettext("binding_cancelled")
                    return None

                new_name = self._handle_capture_event(event)
                if not new_name:
                    continue
                if self._is_duplicate_binding(new_name):
                    self.message = gettext("key_already_assigned").format(key=new_name)
                    return None
                self._apply_binding(self.capture_action, new_name)
                return None
            return None

        # Not capturing: use normal menu navigation but allow selecting an action to capture
        result = super().update(dt, events)
        if result:
            if result == "back":
                return "options"
            # Begin capture for action keys
            for action_key, _ in self.actions:
                if result == action_key:
                    self.capturing = True
                    self.capture_action = action_key
                    # show the user-friendly action label if available
                    action_label = dict(self.actions).get(action_key, action_key)
                    self.message = gettext("press_new_key_for").format(action=action_label)
                    return None
        return None

    def draw(self, screen):
        """
        Render the controls menu and an optional status message.
        
        If the menu instance has a non-empty `message`, draw that message centered near the bottom of the provided surface. Delegates the main menu rendering to the superclass.
         
        Parameters:
            screen (pygame.Surface): Surface to render the menu onto.
        """
        super().draw(screen)
        if self.message:
            font = pygame.font.Font(None, 22)
            msg = font.render(self.message, True, (200, 200, 200))
            rect = msg.get_rect(center=(C.SCREEN_WIDTH / 2, C.SCREEN_HEIGHT - 40))
            screen.blit(msg, rect)


# Define global menu objects at the module level for language switching
main_menu = None
options_menu = None
controls_menu = None

class LanguageMenu(Menu):
    """
    Menu for selecting the application's language.
    Allows the user to choose between available languages, updates the settings,
    and persists the selection. Menu items are dynamically labeled to reflect the current language.
    """
    def __init__(self, settings):
        """
        Create a LanguageMenu and populate it with language selection items plus a Back option.
        
        Parameters:
            settings: An object exposing a `language` attribute (current language code) and a `save()` method. Selecting a language item will update `settings.language` and is expected to be persisted by callers (the menu itself adds the items and triggers selection handling elsewhere).
        
        Notes:
            The constructor attempts to import `modul.i18n.gettext` for localized labels and falls back to a no-op translator that returns the key unchanged if the import fails. The menu is populated with entries for English ("en") and German ("de"), marking the current language.
        """
        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(key):
                """
                Fallback translation function used when internationalization is unavailable.
                
                Parameters:
                    key (str): Translation key or message identifier.
                
                Returns:
                    str: The input `key` unchanged.
                """
                return key
        super().__init__(gettext("language").upper())
        self.settings = settings
        self.languages = [("en", "English"), ("de", "Deutsch")]
        for code, label in self.languages:
            sel = " (current)" if settings.language == code else ""
            self.add_item(f"{label}{sel}", code)
        self.add_item(gettext("back"), "back")

    def update(self, dt, events):
        """
        Update language menu labels from settings and handle user navigation.
        
        Updates each menu item's text to indicate the currently selected language, processes input events, and handles navigation. If the user selects Back, returns "options". If the user selects a language, updates settings.language, persists settings, and returns a dict signalling the caller to rebuild menus.
        
        Returns:
            "options" if the Back item was selected; a dict `{"action": "rebuild_menus", "target": "options"}` when a language was selected and saved; `None` if no navigation occurred.
        """
        for i, (code, label) in enumerate(self.languages):
            sel = " (current)" if self.settings.language == code else ""
            self.items[i].text = f"{label}{sel}"

        result = super().update(dt, events)
        if result:
            if result == "back":
                return "options"
            # Set language
            for code, _ in self.languages:
                if result == code:
                    self.settings.language = result
                    self.settings.save()
                    # Signal that menus should be rebuilt by the caller. The
                    # caller (game loop) is responsible for recreating module
                    # globals in one place to avoid scattered global writes.
                    return {"action": "rebuild_menus", "target": "options"}
        return None


class GameOverScreen:
    """Implementation detail: see method body for behavior."""
    def __init__(self):
        """
        Initialize the GameOver screen's visual state and default score.
        
        Creates title and body fonts using configured menu sizes, sets the background alpha to 0 and enables fade-in, and initializes the final score to 0.
        """
        self.title_font = pygame.font.Font(None, C.MENU_TITLE_FONT_SIZE)
        self.text_font = pygame.font.Font(None, C.MENU_ITEM_FONT_SIZE)
        self.background_alpha = 0
        self.fade_in = True
        self.final_score = 0

    def set_score(self, score):
        """
        Set the final score shown on the Game Over screen.
        
        Parameters:
            score (int): Final score value to display.
        """
        self.final_score = score

    def update(self, dt, events):
        """Update fade-in animation and handle input; return next screen or None.

        Args:
            dt (float): Delta time since last frame in seconds.
            events (list): Pygame events to process.

        Returns:
            Optional[str]: Navigation target (e.g. 'highscore_display') or None.
        """
        if self.fade_in:
            self.background_alpha = min(255, self.background_alpha + 255 * dt / C.MENU_TRANSITION_SPEED)
            if self.background_alpha >= C.MENU_BACKGROUND_ALPHA:
                self.fade_in = False
                self.background_alpha = C.MENU_BACKGROUND_ALPHA

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
        """
        Render the game over screen showing a title, the final score, and input instructions.
        
        Parameters:
            screen (pygame.Surface): Surface to draw the screen contents on.
        """
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((0, 0, 0, self.background_alpha))
        screen.blit(background, (0, 0))

        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(key):
                """
                Return the translation key unchanged when internationalization is unavailable.
                
                Parameters:
                    key (str): The translation key to resolve.
                
                Returns:
                    str: The same `key` passed in.
                """
                return key
        title_surf = self.title_font.render(gettext("game_over").upper(), True, pygame.Color("red"))
        title_rect = title_surf.get_rect(center=(C.SCREEN_WIDTH / 2, C.SCREEN_HEIGHT / 3))
        screen.blit(title_surf, title_rect)

        score_surf = self.text_font.render(gettext("your_score_format").format(score=self.final_score), True, (255, 255, 255))
        score_rect = score_surf.get_rect(center=(C.SCREEN_WIDTH / 2, C.SCREEN_HEIGHT / 2))
        screen.blit(score_surf, score_rect)
        instruction1 = self.text_font.render(gettext("press_space_highscores"), True, (200, 200, 200))
        instruction1_rect = instruction1.get_rect(center=(C.SCREEN_WIDTH / 2, C.SCREEN_HEIGHT / 2 + 60))
        screen.blit(instruction1, instruction1_rect)

        instruction2 = self.text_font.render(gettext("press_r_restart"), True, (200, 200, 200))
        instruction2_rect = instruction2.get_rect(center=(C.SCREEN_WIDTH / 2, C.SCREEN_HEIGHT / 2 + 100))
        screen.blit(instruction2, instruction2_rect)

        instruction3 = self.text_font.render(gettext("press_esc_main_menu"), True, (200, 200, 200))
        instruction3_rect = instruction3.get_rect(center=(C.SCREEN_WIDTH / 2, C.SCREEN_HEIGHT / 2 + 140))
        screen.blit(instruction3, instruction3_rect)


class DifficultyMenu(Menu):
    """Simple menu for selecting the game difficulty.

    Options are 'Easy', 'Normal' and 'Hard' and a back option to return to the
    main menu.
    """
    def __init__(self):
        """Create menu items for each difficulty level and a back option."""
        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(key):
                """
                Fallback translation function used when internationalization is unavailable.
                
                Parameters:
                    key (str): Translation key or message identifier.
                
                Returns:
                    str: The input `key` unchanged.
                """
                return key
        super().__init__(gettext("difficulty").upper())
        self.add_item(gettext("difficulty_easy"), "difficulty_easy", "L")
        self.add_item(gettext("difficulty_normal"), "difficulty_normal", "N")
        self.add_item(gettext("difficulty_hard"), "difficulty_hard", "S")
        self.add_item(gettext("back"), "main_menu", "Z")


class VoiceAnnouncementsMenu:
    """Menu to configure voice announcement toggles"""

    def __init__(self, settings):
        """
        Create the voice announcements menu and populate its items from the provided settings.
        
        Parameters:
            settings: Settings object used to read and persist announcement toggles and the selected TTS voice. The constructor will read current values to initialize item labels and call update_menu_texts() to synchronize displayed text. If the i18n module cannot be imported, labels fall back to the untranslated keys.
        """
        self.settings = settings
        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(key):
                """
                Provide a fallback translation when no i18n backend is available.
                
                @param key (str): The translation lookup key.
                @returns (str): The original `key` unchanged.
                """
                return key
        self.title = gettext("voice_announcements")
        self.items = [
            MenuItem(gettext("level_up") + ": ON", "toggle_level_up"),
            MenuItem(gettext("boss_incoming") + ": ON", "toggle_boss_incoming"),
            MenuItem(gettext("boss_defeated") + ": ON", "toggle_boss_defeated"),
            MenuItem(gettext("game_over") + ": ON", "toggle_game_over"),
            MenuItem(gettext("extra_life") + ": ON", "toggle_extra_life"),
            MenuItem(gettext("achievement") + ": ON", "toggle_achievement"),
            MenuItem(gettext("high_score") + ": ON", "toggle_high_score"),
            MenuItem(gettext("new_weapon") + ": OFF", "toggle_new_weapon"),
            MenuItem(gettext("shield_active") + ": OFF", "toggle_shield_active"),
            MenuItem(gettext("low_health") + ": OFF", "toggle_low_health"),
            MenuItem(gettext("powerup") + ": OFF", "toggle_powerup"),
            # TTS voice selection (if available)
            MenuItem(gettext("tts_voice_label") + f": {getattr(settings, 'tts_voice', '') or gettext('default')}", "tts_voice"),
            MenuItem("", None),
            MenuItem(gettext("back"), "back"),
        ]
        self.current_selection = 0
        self.fade_in = True
        self.background_alpha = 0
        self.update_menu_texts()

    def update_menu_texts(self):
        """
        Update menu item labels to reflect enabled/disabled voice announcement settings.
        
        Each menu item's text is set to "<label>: ON" or "<label>: OFF" according to entries in self.settings.announcement_types.
        This method attempts to use the i18n gettext translation for each label and falls back to the raw key when i18n is unavailable.
        """
        announcements = self.settings.announcement_types
        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(key):
                """
                Return the translation key unchanged when internationalization is unavailable.
                
                Parameters:
                    key (str): The translation key to resolve.
                
                Returns:
                    str: The same `key` passed in.
                """
                return key

        self.items[0].text = f"{gettext('level_up')}: {'ON' if announcements.get('level_up', True) else 'OFF'}"
        self.items[1].text = f"{gettext('boss_incoming')}: {'ON' if announcements.get('boss_incoming', True) else 'OFF'}"
        self.items[2].text = f"{gettext('boss_defeated')}: {'ON' if announcements.get('boss_defeated', True) else 'OFF'}"
        self.items[3].text = f"{gettext('game_over')}: {'ON' if announcements.get('game_over', True) else 'OFF'}"
        self.items[4].text = f"{gettext('extra_life')}: {'ON' if announcements.get('extra_life', True) else 'OFF'}"
        self.items[5].text = f"{gettext('achievement')}: {'ON' if announcements.get('achievement', True) else 'OFF'}"
        self.items[6].text = f"{gettext('high_score')}: {'ON' if announcements.get('high_score', True) else 'OFF'}"
        self.items[7].text = f"{gettext('new_weapon')}: {'ON' if announcements.get('new_weapon', False) else 'OFF'}"
        self.items[8].text = f"{gettext('shield_active')}: {'ON' if announcements.get('shield_active', False) else 'OFF'}"
        self.items[9].text = f"{gettext('low_health')}: {'ON' if announcements.get('low_health', False) else 'OFF'}"
        self.items[10].text = f"{gettext('powerup')}: {'ON' if announcements.get('powerup', False) else 'OFF'}"

    def update(self, dt, events):
        """
        Handle menu input for voice-announcement toggles and advance fade-in.
        
        Processes the fade-in of the background, moves the current selection with Up/Down keys (skipping empty items), activates the selected item with Enter, and closes the menu with Escape.
        
        Parameters:
            dt (float): Time elapsed since the last frame.
            events (iterable): Iterable of pygame events to process.
        
        Returns:
            str | None: The selected item's action key if activated, `"back"` if the user requested to go back, or `None` if no navigation action occurred.
        """
        if self.fade_in:
            self.background_alpha = min(255, self.background_alpha + 255 * dt / C.MENU_TRANSITION_SPEED)
            if self.background_alpha >= C.MENU_BACKGROUND_ALPHA:
                self.fade_in = False
                self.background_alpha = C.MENU_BACKGROUND_ALPHA

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
        """
        Handle a menu action to toggle specific voice announcement settings or request navigation to a submenu.
        
        Parameters:
            action (str): Menu action key indicating which announcement to toggle or which submenu to open.
        
        Returns:
            str | None: `'tts_voice'` to open the TTS voice selection submenu, `'options'` to return to the options menu, or `None` if no navigation is requested.
        """
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

        # Open TTS voice selection
        if action == "tts_voice":
            return "tts_voice"

        return None

    def draw(self, screen):
        """
        Render the voice announcements menu onto the given display surface.
        
        Draws a translucent background, the menu title near the top, and the menu items centered vertically with configured spacing. The currently selected item is rendered using the selected color; empty items are skipped visually and contribute half the normal vertical spacing to preserve layout. Uses the menu's background_alpha, title, and item texts for display.
        
        Parameters:
            screen (pygame.Surface): Target surface to draw the menu on.
        """
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((0, 0, 0, self.background_alpha))
        screen.blit(background, (0, 0))

        title_font = pygame.font.Font(None, C.MENU_TITLE_FONT_SIZE)
        title_surface = title_font.render(self.title, True, pygame.Color(C.MENU_TITLE_COLOR))
        title_rect = title_surface.get_rect(center=(C.SCREEN_WIDTH / 2, 60))
        screen.blit(title_surface, title_rect)

        font = pygame.font.Font(None, C.MENU_ITEM_FONT_SIZE)
        start_y = 130

        visible_count = 0
        for i, item in enumerate(self.items):
            if item.text == "":
                visible_count += 0.5
                continue

            y = start_y + visible_count * C.MENU_ITEM_SPACING
            is_selected = i == self.current_selection
            color = C.MENU_SELECTED_COLOR if is_selected else C.MENU_UNSELECTED_COLOR

            text_surface = font.render(item.text, True, pygame.Color(color))
            text_rect = text_surface.get_rect(center=(C.SCREEN_WIDTH / 2, y))
            screen.blit(text_surface, text_rect)

            visible_count += 1


class TTSVoiceMenu(Menu):
    """Menu to select a TTS voice from available system voices."""

    def __init__(self, settings):
        """
        Create the TTS voice selection menu and populate it with available voices.
        
        Adds a "default" item (action "tts_voice:__default__") and a "back" item (action "back"). If a TTS manager is available, adds one menu item per discovered voice with action "tts_voice:<id>". The chosen voice id is stored in settings.tts_voice (selecting "__default__" clears the explicit choice). Menu labels use the "tts_voice_label" i18n key when a gettext implementation is available; otherwise the raw keys are used.
        
        Parameters:
            settings: An application settings object that exposes and persists a `tts_voice` attribute.
        """
        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(key):
                """
                Return the input key unchanged when a translation lookup is not available.
                
                Parameters:
                    key (str): The message identifier or text to translate.
                
                Returns:
                    str: The same string passed in `key`.
                """
                return key

        super().__init__(gettext("tts_voice_label").upper())
        self.settings = settings
        self.add_item(gettext("default"), "tts_voice:__default__")

        # Try to enumerate voices via TTS manager
        try:
            from modul.tts import get_tts_manager
            manager = get_tts_manager()
            voices = []
            if manager and getattr(manager, "engine", None):
                voices = manager.engine.getProperty("voices") or []
            for v in voices:
                # Some voice objects expose name and id
                name = getattr(v, "name", None) or getattr(v, "id", str(v))
                vid = getattr(v, "id", name)
                self.add_item(name, f"tts_voice:{vid}")
        except Exception:  # pylint: disable=broad-exception-caught
            # If enumeration fails, provide no extra choices
            pass

        self.add_item(gettext("back"), "back")

    def update(self, dt, events):
        # Use base menu navigation
        """
        Delegate input events and time progression to the base Menu and return any resulting navigation action.
        
        Parameters:
            dt (float): Time delta since the last update.
            events (Iterable[pygame.event.Event]): Iterable of pygame events to process.
        
        Returns:
            action (str or None): Action key returned by the base Menu if one was triggered, None otherwise.
        """
        result = super().update(dt, events)
        if result:
            return result
        return None

    def handle_action(self, action):
        # Expected action formats: 'tts_voice:<id>' or 'tts_voice:__default__'
        """
        Apply a TTS voice selection to settings and persist the change.
        
        Recognizes actions of the form "tts_voice:<id>" to select a specific voice and
        "tts_voice:__default__" to clear the custom voice. When a specific voice is
        selected, this method will try to derive a language code from the voice metadata
        and, if possible, instruct the running TTS manager to use the selected voice.
        
        Parameters:
            action (str): Action string, one of:
                - "back" — navigate back to the options menu;
                - "tts_voice:<id>" — select the voice with identifier or name <id>;
                - "tts_voice:__default__" — clear the custom TTS voice and use the default.
        
        Returns:
            Optional[str]: "options" when action is "back", otherwise None.
        """
        if action == "back":
            return "options"
        if action and action.startswith("tts_voice:"):
            vid = action.split(":", 1)[1]
            if vid == "__default__":
                self.settings.tts_voice = ""
                self.settings.tts_voice_language = self.settings.language
            else:
                self.settings.tts_voice = vid
                # Try to derive language from available voices
                try:
                    from modul.tts import get_tts_manager

                    manager = get_tts_manager()
                    if manager and getattr(manager, "engine", None):
                        voices = manager.engine.getProperty("voices") or []
                        for v in voices:
                            if getattr(v, "id", None) == vid or getattr(v, "name", None) == vid:
                                langs = getattr(v, "languages", []) or []
                                for lang in langs:
                                    try:
                                        lang_str = lang.decode() if isinstance(lang, (bytes, bytearray)) else str(lang)
                                        # pick primary subtag like 'en' from en_US
                                        if len(lang_str) >= 2:
                                            code = lang_str[:2]
                                            self.settings.tts_voice_language = code
                                            break
                                    except Exception:
                                        continue
                                break
                    # Attempt to apply the voice immediately to the running manager
                    try:
                        if manager:
                            manager.set_preferred_voice(vid, self.settings.tts_voice_language)
                    except Exception:
                        pass
                except Exception:
                    pass
            # Persist selection
            self.settings.save()
        return None


class SoundTestMenu:
    """Menu that allows the developer to play and test in-game sounds.

    Supports playing individual sounds and a threaded "play all" routine.
    """
    def __init__(self):
        """
        Initialize the Sound Test screen state and populate the list of testable sounds.
        
        Sets up a threading lock used to protect sound state, establishes a gettext fallback for label translation, and initializes UI state (title, sounds placeholder, last-played tracking, scroll offset, visible-item limits, current selection). Initializes playback control flags (playing all, stop-all), constructs the ordered list of sound items as (label, action) pairs, calls update_visible_items() to prepare the visible subset, and initializes background fade state.
        """
        import threading
        self._sound_state_lock = threading.Lock()
        try:
            from modul.i18n import gettext
        except Exception:
            def gettext(key):
                """
                Return the translated text for the given message key or the key itself if no translation is available.
                
                Parameters:
                    key (str): Message identifier to translate.
                
                Returns:
                    str: Translated text for `key`, or `key` unchanged when translations are unavailable.
                """
                return key
        self.title = gettext("sound_test")
        self.sounds = None
        self.last_played = ""
        self.last_played_timer = 0

        self.scroll_offset = 0
        self.max_visible_items = 16
        self.current_selection = 0

        self.playing_all_sounds = False
        self.stop_all_sounds_thread = False

        self.sound_items = [
            (gettext("standard_shoot"), "test_shoot"),
            (gettext("laser_shoot"), "test_laser_shoot"),
            (gettext("rocket_shoot"), "test_rocket_shoot"),
            (gettext("shotgun_shoot"), "test_shotgun_shoot"),
            (gettext("triple_shoot"), "test_triple_shoot"),
            ("", ""),
            (gettext("explosion"), "test_explosion"),
            (gettext("player_hit"), "test_player_hit"),
            (gettext("powerup"), "test_powerup"),
            (gettext("shield_activate"), "test_shield_activate"),
            (gettext("weapon_pickup"), "test_weapon_pickup"),
            ("", ""),
            (gettext("boss_spawn"), "test_boss_spawn"),
            (gettext("boss_death"), "test_boss_death"),
            (gettext("boss_attack"), "test_boss_attack"),
            ("", ""),
            (gettext("level_up"), "test_level_up"),
            (gettext("game_over"), "test_game_over"),
            (gettext("menu_select"), "test_menu_select"),
            (gettext("menu_confirm"), "test_menu_confirm"),
            ("", ""),
            (gettext("test_all_sounds"), "test_all"),
            ("", ""),
            (gettext("back"), "back"),
        ]

        self.update_visible_items()

        self.background_alpha = 0
        self.fade_in = False

    def activate(self):
        """
        Prepare the menu for display by resetting visual state, selection, and sound-test playback flags, then refresh the visible items.
        
        This sets fade-in to start, clears background transparency and scroll offset, selects the first item, resets sound playback control flags, and recomputes which items are visible.
        """
        self.fade_in = True
        self.background_alpha = 0
        self.scroll_offset = 0
        self.current_selection = 0
        self.stop_all_sounds_thread = False
        self.playing_all_sounds = False
        self.update_visible_items()

    def set_sounds(self, sounds):
        """Attach a `Sounds` instance used to play effects from this menu.

        Args:
            sounds: Object exposing methods like `play_shoot`, `play_explosion`, etc.
        """
        self.sounds = sounds

    def update_visible_items(self):
        """Recompute which subset of `sound_items` is currently visible.

        Ensures `self.current_selection` remains within visible bounds.
        """
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
        """
        Handle input and update scrolling/selection for the sound test menu.
        
        Processes keyboard events to move the selection up/down with wrap and scrolling, activate the selected sound item, stop any ongoing "play all" playback, and return navigation actions. Also advances the fade-in of the background and decrements the last-played timer, clearing the last played label when it expires.
        
        Parameters:
            dt (float): Time elapsed since the last update, in seconds.
            events (Iterable): Iterable of pygame events to process.
        
        Returns:
            Optional[str]: The action key for the selected sound item or "back" when navigating out, or `None` if no action was triggered.
        """
        if self.fade_in:
            self.background_alpha = min(255, self.background_alpha + 255 * dt / C.MENU_TRANSITION_SPEED)
            if self.background_alpha >= C.MENU_BACKGROUND_ALPHA:
                self.fade_in = False
                self.background_alpha = C.MENU_BACKGROUND_ALPHA

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
        """
        Handle a sound-related menu action and update the menu's playback state.
        
        Performs the requested test playback (multiple "test_*" keys), may start a background thread to play all sounds ("test_all"), updates UI status fields (e.g., `self.last_played`, `self.last_played_timer`), and stops any running "play all" thread when navigating back.
        
        Parameters:
            action (str): Action key indicating which sound or control to perform (examples: "test_shoot", "test_explosion", "test_menu_select", "test_all", "back").
        
        Returns:
            str or None: Returns "options" when the "back" action is processed (and any running all-sounds playback is stopped); otherwise `None`.
        """
        if not self.sounds:
            return None

        if action == "test_shoot":
            self.sounds.play_shoot()
            try:
                from modul.i18n import gettext
            except Exception:  # pylint: disable=broad-exception-caught
                def gettext(k):
                    """
                    Return the translation key unchanged when the i18n system is unavailable.
                    
                    Parameters:
                        k (str): The translation key to look up.
                    
                    Returns:
                        str: The original key unchanged.
                    """
                    return k
            self.last_played = gettext("sound_played").format(name=gettext("standard_shoot"))
            self.last_played_timer = 2.0

        elif action == "test_laser_shoot":
            if hasattr(self.sounds, "play_laser_shoot"):
                self.sounds.play_laser_shoot()
            else:
                self.sounds.play_shoot()
            try:
                from modul.i18n import gettext
            except Exception:  # pylint: disable=broad-exception-caught
                def gettext(k):
                    """
                    Return the translation key unchanged when the i18n system is unavailable.
                    
                    Parameters:
                        k (str): The translation key to look up.
                    
                    Returns:
                        str: The original key unchanged.
                    """
                    return k
            self.last_played = gettext("sound_played").format(name=gettext("laser_shoot"))
            self.last_played_timer = 2.0

        elif action == "test_rocket_shoot":
            if hasattr(self.sounds, "play_rocket_shoot"):
                self.sounds.play_rocket_shoot()
            else:
                self.sounds.play_shoot()
            try:
                from modul.i18n import gettext
            except Exception:  # pylint: disable=broad-exception-caught
                def gettext(k):
                    """
                    Return the translation key unchanged when the i18n system is unavailable.
                    
                    Parameters:
                        k (str): The translation key to look up.
                    
                    Returns:
                        str: The original key unchanged.
                    """
                    return k
            self.last_played = gettext("sound_played").format(name=gettext("rocket_shoot"))
            self.last_played_timer = 2.0

        elif action == "test_shotgun_shoot":
            if hasattr(self.sounds, "play_shotgun_shoot"):
                self.sounds.play_shotgun_shoot()
            else:
                self.sounds.play_shoot()
            try:
                from modul.i18n import gettext
            except Exception:  # pylint: disable=broad-exception-caught
                def gettext(k):
                    """
                    Return the translation key unchanged when the i18n system is unavailable.
                    
                    Parameters:
                        k (str): The translation key to look up.
                    
                    Returns:
                        str: The original key unchanged.
                    """
                    return k
            self.last_played = gettext("sound_played").format(name=gettext("shotgun_shoot"))
            self.last_played_timer = 2.0

        elif action == "test_triple_shoot":
            if hasattr(self.sounds, "play_triple_shoot"):
                self.sounds.play_triple_shoot()
            else:
                self.sounds.play_shoot()
            try:
                from modul.i18n import gettext
            except Exception:  # pylint: disable=broad-exception-caught
                def gettext(k):
                    """
                    Return the translation key unchanged when the i18n system is unavailable.
                    
                    Parameters:
                        k (str): The translation key to look up.
                    
                    Returns:
                        str: The original key unchanged.
                    """
                    return k
            self.last_played = gettext("sound_played").format(name=gettext("triple_shoot"))
            self.last_played_timer = 2.0

        elif action == "test_explosion":
            self.sounds.play_explosion()
            try:
                from modul.i18n import gettext
            except Exception:  # pylint: disable=broad-exception-caught
                def gettext(k):
                    """
                    Return the translation key unchanged when the i18n system is unavailable.
                    
                    Parameters:
                        k (str): The translation key to look up.
                    
                    Returns:
                        str: The original key unchanged.
                    """
                    return k
            self.last_played = gettext("sound_played").format(name=gettext("explosion"))
            self.last_played_timer = 2.0

        elif action == "test_player_hit":
            self.sounds.play_player_hit()
            try:
                from modul.i18n import gettext
            except Exception:  # pylint: disable=broad-exception-caught
                def gettext(k):
                    """
                    Return the translation key unchanged when the i18n system is unavailable.
                    
                    Parameters:
                        k (str): The translation key to look up.
                    
                    Returns:
                        str: The original key unchanged.
                    """
                    return k
            self.last_played = gettext("sound_played").format(name=gettext("player_hit"))
            self.last_played_timer = 2.0

        elif action == "test_powerup":
            self.sounds.play_powerup()
            try:
                from modul.i18n import gettext
            except Exception:  # pylint: disable=broad-exception-caught
                def gettext(k):
                    """
                    Return the translation key unchanged when the i18n system is unavailable.
                    
                    Parameters:
                        k (str): The translation key to look up.
                    
                    Returns:
                        str: The original key unchanged.
                    """
                    return k
            self.last_played = gettext("sound_played").format(name=gettext("powerup"))
            self.last_played_timer = 2.0

        elif action == "test_shield_activate":
            self.sounds.play_shield_activate()
            try:
                from modul.i18n import gettext
            except Exception:  # pylint: disable=broad-exception-caught
                def gettext(k):
                    """
                    Return the translation key unchanged when the i18n system is unavailable.
                    
                    Parameters:
                        k (str): The translation key to look up.
                    
                    Returns:
                        str: The original key unchanged.
                    """
                    return k
            self.last_played = gettext("sound_played").format(name=gettext("shield_activate"))
            self.last_played_timer = 2.0

        elif action == "test_weapon_pickup":
            if hasattr(self.sounds, "play_weapon_pickup"):
                self.sounds.play_weapon_pickup()
            else:
                self.sounds.play_powerup()
            try:
                from modul.i18n import gettext
            except Exception:  # pylint: disable=broad-exception-caught
                def gettext(k):
                    """
                    Return the translation key unchanged when the i18n system is unavailable.
                    
                    Parameters:
                        k (str): The translation key to look up.
                    
                    Returns:
                        str: The original key unchanged.
                    """
                    return k
            self.last_played = gettext("sound_played").format(name=gettext("weapon_pickup"))
            self.last_played_timer = 2.0

        elif action == "test_boss_spawn":
            self.sounds.play_boss_spawn()
            try:
                from modul.i18n import gettext
            except Exception:  # pylint: disable=broad-exception-caught
                def gettext(k):
                    """
                    Return the translation key unchanged when the i18n system is unavailable.
                    
                    Parameters:
                        k (str): The translation key to look up.
                    
                    Returns:
                        str: The original key unchanged.
                    """
                    return k
            self.last_played = gettext("sound_played").format(name=gettext("boss_spawn"))
            self.last_played_timer = 2.0

        elif action == "test_boss_death":
            self.sounds.play_boss_death()
            try:
                from modul.i18n import gettext
            except Exception:  # pylint: disable=broad-exception-caught
                def gettext(k):
                    """
                    Return the translation key unchanged when the i18n system is unavailable.
                    
                    Parameters:
                        k (str): The translation key to look up.
                    
                    Returns:
                        str: The original key unchanged.
                    """
                    return k
            self.last_played = gettext("sound_played").format(name=gettext("boss_death"))
            self.last_played_timer = 2.0

        elif action == "test_boss_attack":
            if hasattr(self.sounds, "play_boss_attack"):
                self.sounds.play_boss_attack()
            else:
                self.sounds.play_explosion()
            try:
                from modul.i18n import gettext
            except Exception:  # pylint: disable=broad-exception-caught
                def gettext(k):
                    """
                    Return the translation key unchanged when the i18n system is unavailable.
                    
                    Parameters:
                        k (str): The translation key to look up.
                    
                    Returns:
                        str: The original key unchanged.
                    """
                    return k
            self.last_played = gettext("sound_played").format(name=gettext("boss_attack"))
            self.last_played_timer = 2.0

        elif action == "test_level_up":
            self.sounds.play_level_up()
            try:
                from modul.i18n import gettext
            except Exception:  # pylint: disable=broad-exception-caught
                def gettext(k):
                    """
                    Return the translation key unchanged when the i18n system is unavailable.
                    
                    Parameters:
                        k (str): The translation key to look up.
                    
                    Returns:
                        str: The original key unchanged.
                    """
                    return k
            self.last_played = gettext("sound_played").format(name=gettext("level_up"))
            self.last_played_timer = 2.0

        elif action == "test_game_over":
            self.sounds.play_game_over()
            try:
                from modul.i18n import gettext
            except Exception:  # pylint: disable=broad-exception-caught
                def gettext(k):
                    """
                    Return the translation key unchanged when the i18n system is unavailable.
                    
                    Parameters:
                        k (str): The translation key to look up.
                    
                    Returns:
                        str: The original key unchanged.
                    """
                    return k
            self.last_played = gettext("sound_played").format(name=gettext("game_over"))
            self.last_played_timer = 2.0

        elif action == "test_menu_select":
            self.sounds.play_menu_move()
            try:
                from modul.i18n import gettext
            except Exception:
                def gettext(k):
                    """
                    Return the translation key unchanged when the i18n system is unavailable.
                    
                    Parameters:
                        k (str): The translation key to look up.
                    
                    Returns:
                        str: The original key unchanged.
                    """
                    return k
            self.last_played = gettext("sound_played").format(name=gettext("menu_select"))
            self.last_played_timer = 2.0

        elif action == "test_menu_confirm":
            self.sounds.play_menu_select()
            try:
                from modul.i18n import gettext
            except Exception:
                def gettext(k):
                    """
                    Return the translation key unchanged when the i18n system is unavailable.
                    
                    Parameters:
                        k (str): The translation key to look up.
                    
                    Returns:
                        str: The original key unchanged.
                    """
                    return k
            self.last_played = gettext("sound_played").format(name=gettext("menu_confirm"))
            self.last_played_timer = 2.0


        elif action == "test_all":
            import threading
            import time

            def play_all_sounds():
                """
                Play the configured sequence of sound effects and clear the playing flag when finished.
                
                If the instance has a sounds object, calls each sound playback method in order with a short pause between them. The loop stops early if the `stop_all_sounds_thread` flag becomes true. Any exceptions raised by individual sound calls are caught and reported to stdout. At exit, sets `playing_all_sounds` to False while holding the instance's `_sound_state_lock`.
                """
                sound_list = []
                if self.sounds is not None:
                    sound_list = [
                        ("Standard Shoot", self.sounds.play_shoot),
                        ("Explosion", self.sounds.play_explosion),
                        ("Player Hit", self.sounds.play_player_hit),
                        ("PowerUp", self.sounds.play_powerup),
                        ("Level Up", self.sounds.play_level_up),
                        ("Game Over", self.sounds.play_game_over),
                    ]

                for name, sound_func in sound_list:
                    with self._sound_state_lock:
                        if self.stop_all_sounds_thread:
                            break
                    try:
                        sound_func()
                        time.sleep(0.8)
                    except Exception as e:  # pylint: disable=broad-exception-caught
                        print(f"Error playing sound '{name}': {e}")

                with self._sound_state_lock:
                    self.playing_all_sounds = False

            with self._sound_state_lock:
                if not self.playing_all_sounds:
                    self.playing_all_sounds = True
                    self.stop_all_sounds_thread = False
                    threading.Thread(target=play_all_sounds, daemon=True).start()
                    try:
                        from modul.i18n import gettext as _gettext
                        self.last_played = _gettext("playing_all_sounds")
                    except Exception:  # pylint: disable=broad-exception-caught
                        self.last_played = "Playing all sounds..."
                    self.last_played_timer = 8.0


        elif action == "back":
            with self._sound_state_lock:
                if self.playing_all_sounds:
                    self.stop_all_sounds_thread = True
                    self.playing_all_sounds = False
                    self.last_played = ""
            return "options"

        return None

    def draw(self, screen):
        """
        Draw the menu's translucent background and centered title onto the provided pygame surface.
        
        Renders a semi-transparent black background using the menu's current background_alpha, draws the menu title centered near the top using the configured title font and color, and prepares an indicator font for item rendering. The method also attempts to import a localized `gettext`; if that import fails, it installs a fallback that returns keys unchanged.
        
        Parameters:
            screen (pygame.Surface): Destination surface to render the menu onto.
        """
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((0, 0, 0, self.background_alpha))
        screen.blit(background, (0, 0))

        title_font = pygame.font.Font(None, C.MENU_TITLE_FONT_SIZE)
        title_surface = title_font.render(self.title, True, pygame.Color(C.MENU_TITLE_COLOR))
        title_rect = title_surface.get_rect(center=(C.SCREEN_WIDTH / 2, 60))
        screen.blit(title_surface, title_rect)

        indicator_font = pygame.font.Font(None, int(C.MENU_ITEM_FONT_SIZE * 0.7))

        try:
            from modul.i18n import gettext
        except Exception:
            def gettext(key):
                """
                Return the translated text for the given message key or the key itself if no translation is available.
                
                Parameters:
                    key (str): Message identifier to translate.
                
                Returns:
                    str: Translated text for `key`, or `key` unchanged when translations are unavailable.
                """
                return key

class TTSVoiceMenu(Menu):
    """Menu to select a TTS voice from available system voices."""

    def __init__(self, settings):
        """
        Initialize the TTS voice selection menu and populate it with available system voices.
        
        This constructs the menu title from the localized "tts_voice_label", adds a "default" option and a "back" option, and inserts one menu item per discovered TTS voice when a TTS manager is available. If voice enumeration fails or no voices are available, the menu will contain only the default and back entries.
        
        Parameters:
            settings: Application settings object used to read and later persist the selected TTS voice (e.g., `settings.tts_voice`).
        """
        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(k):
                """
                Look up a translated string for a message key, returning the key unchanged if no translation is available.
                
                Parameters:
                    k (str): Message key to translate.
                
                Returns:
                    translated (str): The translated string for `k`, or `k` unchanged if a translation is not available.
                """
                return k

        super().__init__(gettext("tts_voice_label").upper())
        self.settings = settings
        self.add_item(gettext("default"), "tts_voice:__default__")

        # Try to enumerate voices via TTS manager
        try:
            from modul.tts import get_tts_manager
            manager = get_tts_manager()
            voices = []
            if manager and getattr(manager, "engine", None):
                voices = manager.engine.getProperty("voices") or []
            for v in voices:
                # Some voice objects expose name and id
                name = getattr(v, "name", None) or getattr(v, "id", str(v))
                vid = getattr(v, "id", name)
                self.add_item(name, f"tts_voice:{vid}")
        except Exception:  # pylint: disable=broad-exception-caught
            # If enumeration fails, provide no extra choices
            pass

        self.add_item(gettext("back"), "back")

    def update(self, dt, events):
        # Use base menu navigation
        """
        Delegate update handling to the base Menu implementation and propagate any navigation result.
        
        Parameters:
        	dt (float): Time elapsed since last frame in seconds.
        	events (list): Iterable of input/events to process (e.g., pygame events).
        
        Returns:
        	Navigation action (str or dict) if a menu action was triggered, `None` otherwise.
        """
        result = super().update(dt, events)
        if result:
            return result
        return None

    def handle_action(self, action):
        # Expected action formats: 'tts_voice:<id>' or 'tts_voice:__default__'
        """
        Apply a text-to-speech (TTS) voice selection action and persist the updated settings.
        
        Parameters:
            action (str): Action string to handle. Expected values:
                - "back": navigate back to the options menu.
                - "tts_voice:<id>": select the voice with identifier or name <id>.
                - "tts_voice:__default__": clear a specific voice selection and use the current language as the voice language.
        
        Behavior:
            - When a "tts_voice:<id>" action is provided, updates settings.tts_voice to the given id.
            - If the id is "__default__", clears settings.tts_voice and sets settings.tts_voice_language to the current settings.language.
            - When selecting a specific voice, attempts to derive and store a language code from available voice metadata and to apply the preferred voice to the running TTS manager if available.
            - Persists settings by calling settings.save() when a voice selection or clear is made.
        
        Returns:
            str or None: "options" if action is "back", otherwise None.
        """
        if action == "back":
            return "options"
        if action and action.startswith("tts_voice:"):
            vid = action.split(":", 1)[1]
            if vid == "__default__":
                self.settings.tts_voice = ""
                self.settings.tts_voice_language = self.settings.language
            else:
                self.settings.tts_voice = vid
                # Try to derive language from available voices
                try:
                    from modul.tts import get_tts_manager

                    manager = get_tts_manager()
                    if manager and getattr(manager, "engine", None):
                        voices = manager.engine.getProperty("voices") or []
                        for v in voices:
                            if getattr(v, "id", None) == vid or getattr(v, "name", None) == vid:
                                langs = getattr(v, "languages", []) or []
                                for lang in langs:
                                    try:
                                        lang_str = lang.decode() if isinstance(lang, (bytes, bytearray)) else str(lang)
                                        # pick primary subtag like 'en' from en_US
                                        if len(lang_str) >= 2:
                                            code = lang_str[:2]
                                            self.settings.tts_voice_language = code
                                            break
                                    except Exception:  # pylint: disable=broad-exception-caught
                                        continue
                                break
                    # Attempt to apply the voice immediately to the running manager
                    try:
                        if manager:
                            manager.set_preferred_voice(vid, self.settings.tts_voice_language)
                    except Exception:  # pylint: disable=broad-exception-caught
                        pass
                except Exception:  # pylint: disable=broad-exception-caught
                    pass
            # Persist selection
            self.settings.save()
        return None



# --- AchievementsMenu class ---
class AchievementsMenu(Menu):
    """Menu to display and interact with achievements."""
    def __init__(self, achievement_system):
        # Prepend game name for consistency with other menus
        """
        Initialize the achievements menu using the provided achievement system.
        
        Sets the menu title to "<game name> - ACHIEVEMENTS", stores the given achievement system, extracts an optional
        graphics mapping from achievement_system.graphics (defaults to an empty dict), and adds a "back" menu item.
        
        Parameters:
            achievement_system: An object that provides achievement data and may expose a `graphics` attribute
                (mapping achievement IDs to graphic representations) used by the menu.
        """
        super().__init__(f"{C.CREDITS_GAME_NAME} - {gettext('achievements').upper()}")
        self.achievement_system = achievement_system
        self.achievement_graphics = getattr(achievement_system, "graphics", {})
        self.add_item(gettext("back"), "back")

    def draw(self, screen):
        """
        Render the achievements screen onto the given display surface.
        
        This draws a translucent background, the centered title, a grid of up to 12 achievements arranged in two columns (each entry shows the achievement name; unlocked achievements are highlighted in green and display associated ASCII/graphic lines when available), the menu items (e.g., Back) near the bottom, and a progress line showing the number of unlocked achievements versus the total.
        
        Parameters:
            screen (pygame.Surface): The target surface to draw the menu onto.
        
        """
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((0, 0, 0, self.background_alpha))
        screen.blit(background, (0, 0))

        title_font = pygame.font.Font(None, C.MENU_TITLE_FONT_SIZE)
        title_surf = title_font.render(self.title, True, pygame.Color(C.MENU_TITLE_COLOR))
        title_rect = title_surf.get_rect(center=(C.SCREEN_WIDTH / 2, C.SCREEN_HEIGHT / 12))
        screen.blit(title_surf, title_rect)

        start_y = C.SCREEN_HEIGHT / 5
        achievement_spacing = 80
        graphics_font = pygame.font.Font(None, 18)
        name_font = pygame.font.Font(None, 28)

        achievements_per_column = 6
        column_width = C.SCREEN_WIDTH / 2
        left_column_x = column_width / 2
        right_column_x = column_width + column_width / 2

        for i, achievement in enumerate(self.achievement_system.achievements):
            if i >= 12:
                break
            column = i // achievements_per_column
            row = i % achievements_per_column
            center_x = left_column_x if column == 0 else right_column_x
            current_y = start_y + row * achievement_spacing
            is_unlocked = achievement.unlocked
            if is_unlocked:
                name_color = pygame.Color("green")
                graphic_color = pygame.Color("lightgreen")
            else:
                name_color = pygame.Color("gray")
                graphic_color = pygame.Color("gray")
            # Guard: `achievement_graphics` may be a Mock in tests; ensure it's a
            # mapping before using `in` to avoid TypeError when iterating.
            if is_unlocked and isinstance(self.achievement_graphics, dict) and achievement.name in self.achievement_graphics:
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

        back_button_y = C.SCREEN_HEIGHT - 80
        for i, item in enumerate(self.items):
            item.draw(screen, (C.SCREEN_WIDTH / 2, back_button_y + i * C.MENU_ITEM_SPACING))

        unlocked_count = sum(1 for achievement in self.achievement_system.achievements if achievement.unlocked)
        total_count = len(self.achievement_system.achievements)
        progress_text = f"Progress: {unlocked_count}/{total_count} Achievements unlocked"
        progress_font = pygame.font.Font(None, 20)
        progress_surf = progress_font.render(progress_text, True, pygame.Color("lightblue"))
        progress_rect = progress_surf.get_rect(center=(C.SCREEN_WIDTH / 2, C.SCREEN_HEIGHT / 12 + 35))
        screen.blit(progress_surf, progress_rect)

    def update(self, dt, events):
        """
        Process per-frame updates and handle immediate "back" navigation.
        
        Parameters:
            dt (float): Time elapsed since the last update in seconds.
            events (iterable): Sequence of pygame events to process.
        
        Returns:
            navigation (str or None): A navigation target string when a navigation action occurred (for example, `'back'` when Escape or Space is pressed), `None` otherwise.
        """
        result = super().update(dt, events)
        if result:
            return result
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                    return "back"
        return None


class ShipSelectionMenu(Menu):
    """TODO: add docstring."""
    def __init__(self):
        """TODO: add docstring."""
        super().__init__("SHIP SELECTION")
        self.selected_ship_index = 0
        self.ships = ship_manager.get_available_ships()
        self.animation_time = 0

    def activate(self):
        """TODO: add docstring."""
        super().activate()
        self.selected_ship_index = 0
        self.ships = ship_manager.get_available_ships()

        try:
            self.selected_ship_index = self.ships.index(ship_manager.current_ship)
        except ValueError:
            self.selected_ship_index = 0

    def update(self, dt, events):
        """TODO: add docstring."""
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
        """
        Render the ship selection screen including ships, details for the selected ship, and UI instructions.
        
        Parameters:
            screen (pygame.Surface): Target surface to draw the entire ship selection UI onto.
        
        Description:
            Draws a translucent background, the menu title, a horizontal list of available ships (highlighting the selected one),
            each ship's name (or "LOCKED" if unavailable), and detailed information for the currently selected ship if unlocked.
            Also renders selection instructions at the bottom of the screen. No value is returned.
        """
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((0, 0, 0, self.background_alpha))
        screen.blit(background, (0, 0))

        title_surf = self.title_font.render(self.title, True, pygame.Color(C.MENU_TITLE_COLOR))
        title_rect = title_surf.get_rect(center=(C.SCREEN_WIDTH / 2, 80))
        screen.blit(title_surf, title_rect)

        ship_y = C.SCREEN_HEIGHT / 2 - 50
        ship_spacing = 200
        start_x = C.SCREEN_WIDTH / 2 - (len(self.ships) - 1) * ship_spacing / 2

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

        detail_y = C.SCREEN_HEIGHT - 200
        detail_font = pygame.font.Font(None, 28)
        small_font = pygame.font.Font(None, 24)

        if ship_data["unlocked"]:

            desc_surf = detail_font.render(ship_data["description"], True, (255, 255, 255))
            desc_rect = desc_surf.get_rect(center=(C.SCREEN_WIDTH / 2, detail_y))
            screen.blit(desc_surf, desc_rect)

            props = [
                f"Speed: {ship_data['speed_multiplier']:.1f}x",
                f"Agility: {ship_data['turn_speed_multiplier']:.1f}x",
                f"Special: {ship_data['special_ability'].replace('_', ' ').title()}",
            ]

            for i, prop in enumerate(props):
                prop_surf = small_font.render(prop, True, (200, 200, 200))
                prop_rect = prop_surf.get_rect(center=(C.SCREEN_WIDTH / 2, detail_y + 40 + i * 25))
                screen.blit(prop_surf, prop_rect)

        instruction_font = pygame.font.Font(None, 20)
        instructions = ["LEFT / RIGHT: Select Ship", "ENTER / SPACE: Confirm Selection", "ESC: Back to Difficulty"]

        for i, instruction in enumerate(instructions):
            instr_surf = instruction_font.render(instruction, True, (150, 150, 150))
            instr_rect = instr_surf.get_rect(center=(C.SCREEN_WIDTH / 2, C.SCREEN_HEIGHT - 60 + i * 20))
            screen.blit(instr_surf, instr_rect)