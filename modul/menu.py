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
    Get the localized string for a translation key.
    
    Parameters:
        key (str): Translation identifier to look up.
    
    Returns:
        The translated string for `key`, or `key` unchanged if no translation is available.
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
        """Initialize a MenuItem with text, action, and optional shortcut."""
        self.text = text
        self.action = action
        self.selected = False
        self.hover_animation = 0
        self.opacity = 255
        self.delay = 0
        self.shortcut = shortcut

    def update(self, dt):
        """
        Animate the item's hover state toward the selected target and handle delayed opacity restoration.
        
        When `delay` is greater than zero it is decreased by `dt`; if `delay` reaches zero, `opacity` is set to 255.
        
        Parameters:
            dt (float): Time elapsed since the last update, in seconds.
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
        Render the menu item's text centered at the given screen position, visually reflecting its hover/selection state.
        
        Parameters:
            screen (pygame.Surface): Target surface to draw the text on.
            position (tuple[int, int]): (x, y) coordinates for the center of the rendered text.
            font (pygame.font.Font | None): Optional font to use; when None a size-scaled default font is used based on hover state.
        
        Returns:
            pygame.Rect: Rectangle of the rendered text, positioned with its center at `position`.
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
        Create a menu with a title and optional sounds manager.
        
        Parameters:
            title (str): Text displayed at the top of the menu.
            sounds: Optional sounds manager used for menu navigation and selection sounds; stored on the instance.
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
        Append a new MenuItem to this menu and mark it selected if it is the first item.
        
        Parameters:
            text (str): Display text for the menu item.
            action: Identifier or callable invoked when the item is activated.
            shortcut (str | None): Optional keyboard/shortcut label for the item.
        """
        item = MenuItem(text, action, shortcut)
        self.items.append(item)
        if len(self.items) == 1:
            self.items[0].selected = True

    def activate(self):
        """Activate the menu and start fade-in animation."""
        self.active = True
        self.fade_in = True
        self.background_alpha = 0
        for i, item in enumerate(self.items):
            item.opacity = 0
            item.delay = i * 0.1

    def update(self, dt, events):
        """
        Advance menu animations and process input (keyboard, joystick, and item shortcuts) to change selection or activate an item.
        
        Parameters:
            dt (float): Time elapsed since last update, in seconds.
            events (iterable): Iterable of pygame event objects to process.
        
        Returns:
            str or None: The action identifier of the activated menu item when an activation input is received, or `None` if no item was activated.
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
        """
        Advance the selection to the next menu item.
        
        Updates the current MenuItem `selected` flags and advances `selected_index` with wrap-around. If a `sounds` attribute is present, attempts to play the menu-move sound; any exceptions from sound playback are logged.
        """
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
        Move selection to the previous menu item, wrapping to the last item when currently at the first.
        
        Updates the selected state on the previously and newly selected MenuItem objects. If a `sounds` attribute is present and truthy, attempts to play the menu-move sound; errors raised by the sound playback are caught and logged (using the instance `logger` if available, otherwise the module logger).
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
        Render this menu to the provided screen surface, including the translucent backdrop, the menu title, and the menu items centered vertically.
        
        Parameters:
            screen (pygame.Surface): The target surface on which the menu will be drawn.
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
        Initialize the main menu with a localized title and menu entries.
        
        Sets the menu title to "AJITROIDS" and adds localized items for start_game, tutorial, replays, highscores, statistics, achievements, options, credits, and exit.
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
        Render the main menu and the application version in the bottom-right corner.
        
        Calls the base Menu.draw to render title and items, then draws the version string at the screen's bottom-right.
        
        Parameters:
            screen (pygame.Surface): Surface to render the menu and version text onto.
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
        Create the pause menu titled with the localized "PAUSE" label and populate it with standard pause actions.
        
        Adds menu items:
        - localized "resume" -> action "continue"
        - localized "restart" -> action "restart"
        - localized "main_menu" -> action "main_menu"
        """
        title = _gettext("pause").upper()
        super().__init__(title)
        self.add_item(gettext("resume"), "continue")
        self.add_item(gettext("restart"), "restart")
        self.add_item(gettext("main_menu"), "main_menu")

    def draw(self, screen):
        """
        Render the pause menu and its list of common keyboard shortcuts.
        
        Renders the base menu contents and then draws a vertically stacked list of localized shortcut labels at a fixed offset.
        
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
        """
        Initialize TutorialScreen instance state and fonts.
        
        Sets up the title and body text fonts, initializes the background alpha used for fade-in, and enables the fade-in flag.
        """
        self.title_font = pygame.font.Font(None, C.MENU_TITLE_FONT_SIZE)
        self.text_font = pygame.font.Font(None, C.MENU_ITEM_FONT_SIZE)
        self.background_alpha = 0
        self.fade_in = True

    def update(self, dt, events):
        """
        Advance the tutorial screen fade-in and handle input to exit to the main menu.
        
        Parameters:
        	dt (float): Time elapsed since the last update in seconds.
        	events (iterable): Iterable of pygame Event objects to process.
        
        Returns:
        	str or None: "main_menu" if the Escape key was pressed, otherwise None.
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
        Render the tutorial screen: draws a translucent backdrop, the localized title, and a vertically centered list of instruction lines.
        
        Parameters:
            screen (pygame.Surface): Surface to render the tutorial screen onto.
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
        Create an OptionsMenu bound to user settings and an optional sounds manager.
        
        Populates menu entries for music on/off, sound on/off, music and sound volume (formatted as percent),
        fullscreen toggle, controls, language selection, and Back. If the settings object exposes
        `show_tts_in_options`, a toggle for showing TTS voice selection in Options is added.
        
        Parameters:
            settings: An object providing current option state (expected attributes include
                `music_on`, `sound_on`, `music_volume`, `sound_volume`, `fullscreen`, `language`)
                and optionally `show_tts_in_options`.
            sounds: Optional sounds manager used for menu feedback; may be None.
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
        Handle a selected options action, update settings and menu entries, and optionally return a navigation target.
        
        This method applies the given options `action` (toggles, volume adjustments, fullscreen switch, TTS visibility, or navigation commands), persists changed settings, updates menu item labels to reflect new state, and invokes sound or display side effects when applicable. It may insert or remove the live TTS voice entry in the options list when TTS visibility is toggled.
        
        Parameters:
        	action (str): The action identifier produced by a menu item (e.g., 'toggle_music', 'adjust_sound_volume', 'toggle_fullscreen', 'tts_voice', 'back').
        	sounds: Optional sound manager used to apply volume and toggle operations; may be None.
        
        Returns:
        	str or None: A navigation target string (for example 'voice_announcements', 'tts_voice', 'controls', 'language', 'sound_test', 'main_menu') when the action requests a screen change, or `None` when the action is handled in-place.
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
        Handle keyboard input for the options menu and apply volume/fullscreen/control changes.
        
        Processes KEYDOWN events in events: Escape returns "main_menu"; Left/Right decrease or increase music or sound volume when the selected item action is "adjust_music_volume" or "adjust_sound_volume", persistently saving the settings, updating the sounds manager if present, and refreshing the item's displayed label. Delegates other navigation and activation handling to the base Menu.update.
        
        Parameters:
            dt (float): Time elapsed since the last update, in seconds.
            events (Iterable[pygame.Event]): Iterable of pygame events to process.
        
        Returns:
            str or dict or None: An action/navigation result produced by this menu or its superclass (for example "main_menu" or a rebuild instruction), or `None` if no navigation action was triggered.
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
        Set up the credits screen state: create title and text fonts, start background fade-in, and position the scroll.
        
        Title font uses C.MENU_TITLE_FONT_SIZE; text font uses C.MENU_ITEM_FONT_SIZE - 8. background_alpha is initialized to 0, fade_in to True, and scroll_position to 250.
        """
        self.title_font = pygame.font.Font(None, C.MENU_TITLE_FONT_SIZE)
        self.text_font = pygame.font.Font(None, C.MENU_ITEM_FONT_SIZE - 8)
        self.background_alpha = 0
        self.fade_in = True
        self.scroll_position = 250

    def update(self, dt, events):
        """
        Advance fade-in, scroll the credits, and handle keyboard input to exit the credits screen.
        
        Updates the instance's background_alpha toward the configured MENU_BACKGROUND_ALPHA and decreases scroll_position by the configured CREDITS_SCROLL_SPEED scaled by dt. Processes keyboard events and requests navigation back to the main menu when Space or Escape is pressed.
        
        Parameters:
            dt (float): Time delta in seconds since the last update.
            events (iterable): Iterable of pygame events to process.
        
        Returns:
            str or None: "main_menu" if the user pressed Space or Escape to leave the credits, `None` otherwise.
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
        Render the credits screen: a translucent backdrop, centered title, and vertically scrolling credit lines.
        
        The title is drawn with self.title_font and the credit lines with self.text_font; vertical position is offset by self.scroll_position and lines are centered horizontally.
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
        Derives a canonical binding name from a pygame input event for use when capturing control bindings.
        
        Parameters:
            event (pygame.Event): The input event to convert into a binding identifier.
        
        Returns:
            binding_name (str or None): A normalized binding string for keyboard or joystick inputs (examples: 'a', 'JOY0_BUTTON1', 'JOY0_AXIS2_POS', 'JOY0_HAT0_UP_RIGHT'), or `None` if the event cannot be mapped.
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
        Check whether a proposed input binding name is already assigned to any existing action.
        
        Parameters:
            new_name (str): Candidate binding identifier (e.g., a key, joystick button, or axis name).
        
        Returns:
            bool: True if another action is already bound to `new_name`, False otherwise.
        """
        for a_key, _ in self.actions:
            if self.settings.controls.get(a_key) == new_name:
                return True
        return False

    def _apply_binding(self, action, new_name):
        """
        Bind a new input name to a control action, persist the change, and clear capture state.
        
        Parameters:
            action (str): The identifier of the control action to rebind.
            new_name (str): The input binding name to assign to the action.
        
        Description:
            Updates settings.controls[action] with the provided binding, saves settings,
            stops capture mode, clears the capture target, and sets a user-visible
            confirmation message indicating the newly bound key.
        """
        self.settings.controls[action] = new_name
        self.settings.save()
        self.capturing = False
        self.capture_action = None
        self.message = gettext("bound_key").format(key=new_name)

    def __init__(self, settings):
        """
        Create a controls configuration menu tied to the given settings and populate menu items for each configurable action.
        
        Parameters:
            settings: Settings object exposing a `controls` mapping (action -> key name) used to build each item's label and to persist any remapped bindings.
        
        Notes:
            Initializes internal state used for capturing a new binding (`capturing`, `capture_action`) and a user-facing `message`.
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
        Update the controls menu state and handle input for navigation and key rebinding.
        
        Parameters:
            dt (float): Time elapsed since the last update, in seconds.
            events (iterable): Iterable of pygame events to process.
        
        Returns:
            str or None: `'options'` when the menu requests returning to the options screen, `None` otherwise.
        
        Behavior:
            - Refreshes each menu item label from self.settings.controls.
            - When in capture mode, interprets input events to cancel capture (Escape),
              detect a new binding, reject duplicate bindings (sets self.message),
              or apply a new binding via self._apply_binding.
            - When not capturing, delegates navigation to the base menu update and
              enters capture mode if the user selects a control action to rebind
              (sets self.capturing, self.capture_action, and self.message).
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
        Render the controls menu onto the given Pygame surface.
        
        When a status message is set, draw it centered near the bottom of the screen.
        
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
        Create a language selection menu bound to the given settings.
        
        Initializes the menu title from the localized "language" label (uppercased), stores the provided settings object, builds menu items for the available languages (English and Deutsch) marking the active language with " (current)", and appends a Back item. When a language item is activated, the menu will set settings.language and persist the change via settings.save().
        
        Parameters:
            settings: Settings object that exposes `language` (current language code) and `save()` for persistence.
        """
        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(key):
                """
                Return the localized string for the given message key, falling back to the key if translation is unavailable.
                
                Parameters:
                    key (str): Message identifier to translate.
                
                Returns:
                    str: Translated string for `key`, or `key` itself when no translation is available.
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
        Update the language menu labels and process input to select a language or navigate back.
        
        Updates each menu item's text to append " (current)" for the active language. If the user selects a language, updates settings.language, persists settings via settings.save(), and returns a dict signaling that menus should be rebuilt. If the user selects the back item, returns "options". Otherwise returns None.
        
        Returns:
            dict: `{"action": "rebuild_menus", "target": "options"}` when a new language is chosen and menus must be rebuilt.
            str: `"options"` when the back item is selected.
            None: when no navigation or language change occurred.
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
        Initialize a GameOverScreen instance and set up its visual state.
        
        Sets title and text fonts, initializes background fade state and final score storage.
        
        Attributes:
            title_font: pygame Font used for the title.
            text_font: pygame Font used for body and item text.
            background_alpha (int): Current alpha for the darkened backdrop (0..255).
            fade_in (bool): Whether the screen is currently fading in.
            final_score (int): Score to display on the game over screen.
        """
        self.title_font = pygame.font.Font(None, C.MENU_TITLE_FONT_SIZE)
        self.text_font = pygame.font.Font(None, C.MENU_ITEM_FONT_SIZE)
        self.background_alpha = 0
        self.fade_in = True
        self.final_score = 0

    def set_score(self, score):
        """
        Store the final score to be shown on the Game Over screen.
        
        Parameters:
            score (int): Final score value to display.
        """
        self.final_score = score

    def update(self, dt, events):
        """
        Advance the fade-in background animation and process keyboard events to navigate between screens.
        
        Parameters:
            dt (float): Time elapsed since the last frame, in seconds.
            events (list): Iterable of pygame events to process.
        
        Returns:
            str or None: Navigation target — one of "highscore_display", "main_menu", or "quick_restart" when triggered by keypresses, otherwise None.
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
        Render the game-over screen: draws a translucent backdrop, a red "GAME OVER" title, the final score, and three localized instruction lines.
        
        Parameters:
            screen (pygame.Surface): Surface to draw onto.
        """
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((0, 0, 0, self.background_alpha))
        screen.blit(background, (0, 0))

        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(key):
                """
                Provide a fallback translation function that returns the input key when no i18n subsystem is available.
                
                Parameters:
                    key (str): Translation key or literal text.
                
                Returns:
                    str: The original `key` unchanged.
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
        """
        Initialize the difficulty selection menu with localized labels and keyboard shortcuts.
        
        Adds menu items for Easy, Normal, and Hard difficulty levels (shortcuts "L", "N", "S" respectively) and a Back option that returns to the main menu (shortcut "Z"). Uses the module i18n gettext when available and falls back to raw keys if localization is unavailable.
        """
        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(key):
                """
                Return the localized string for the given message key, falling back to the key if translation is unavailable.
                
                Parameters:
                    key (str): Message identifier to translate.
                
                Returns:
                    str: Translated string for `key`, or `key` itself when no translation is available.
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
        Create the TTS voice configuration menu and populate its items from available settings and translations.
        
        Builds menu entries for voice announcement toggles, a selectable TTS voice entry (showing the current setting or "default"), a spacer, and a Back item. Attempts to use the module i18n gettext and falls back to identity translation if unavailable. Initializes visual state (selection, fade-in, background alpha) and refreshes item labels.
        
        Parameters:
            settings: Settings object used to read and persist TTS-related preferences (e.g., `tts_voice` and announcement toggles).
        """
        self.settings = settings
        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(key):
                """Fallback gettext used when i18n cannot be imported.

                Returns the key unchanged so the UI remains functional.
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
        Update each announcement menu item's label to show its current state.
        
        Sets each MenuItem.text to "<localized_label>: ON" if the corresponding key in self.settings.announcement_types is True (using per-key defaults), otherwise "<localized_label>: OFF". Labels are localized via modul.i18n.gettext when available; if i18n is unavailable the raw keys are used as labels.
        """
        announcements = self.settings.announcement_types
        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(key):
                """
                Provide a fallback translation function that returns the input key when no i18n subsystem is available.
                
                Parameters:
                    key (str): Translation key or literal text.
                
                Returns:
                    str: The original `key` unchanged.
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
        Process keyboard input to navigate the announcements menu and trigger item actions.
        
        Parameters:
            dt (float): Time elapsed since the last update (seconds).
            events (Iterable[pygame.Event]): Sequence of pygame events to handle.
        
        Returns:
            str | None: The selected item's action key if activated, the string `'back'` if Escape was pressed, or `None` if no action was taken.
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
        Handle a selected menu action by toggling voice-announcement settings, persisting changes, or requesting submenu navigation.
        
        This updates self.settings.announcement_types for toggle actions and calls self.settings.save() and self.update_menu_texts() to persist and refresh labels.
        
        Returns:
            str or None: "tts_voice" to open the TTS voice selection, "options" to go back to options, or `None` if no navigation is requested.
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
        Draws the voice announcements menu (title and menu items) centered on the given screen and highlights the currently selected item.
        
        Parameters:
            screen (pygame.Surface): Surface to render the menu onto.
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
        Create the TTS voice selection menu from the given settings.
        
        Adds a "Default" option, attempts to enumerate available system TTS voices and adds each as a selectable item, and always adds a "Back" item. The chosen voice id is stored in and read from settings.tts_voice.
        
        Parameters:
            settings: Application settings object whose `tts_voice` attribute is used to persist the selected voice.
        """
        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(key):
                """
                Provide a fallback lookup that returns the input key unchanged when no i18n implementation is available.
                
                Parameters:
                    key (str): Translation key to resolve.
                
                Returns:
                    str: The unchanged input `key`.
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
        Process the menu update and input events, returning any selected action.
        
        Parameters:
            dt (float): Time delta since the last frame.
            events (iterable): Iterable of pygame events to process.
        
        Returns:
            Optional[str]: Action key selected by the menu, or `None` if no action occurred.
        """
        result = super().update(dt, events)
        if result:
            return result
        return None

    def handle_action(self, action):
        # Expected action formats: 'tts_voice:<id>' or 'tts_voice:__default__'
        """
        Apply a selected TTS voice to settings and attempt to detect and apply its language.
        
        Parameters:
            action (str): Navigation or selection command. Expected formats:
                - "tts_voice:<id>" — select a voice by id or name
                - "tts_voice:__default__" — reset to default voice (clears custom voice and uses settings.language)
                - "back" — navigate back to the options menu
        
        Behavior:
            - Updates settings.tts_voice and settings.tts_voice_language according to the chosen voice.
            - If a specific voice is chosen, attempts to derive a language code from available TTS voices and applies the preferred voice to the running TTS manager if present.
            - Persists the updated settings by calling settings.save().
        
        Returns:
            str or None: "options" when action is "back", otherwise None.
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
        Initialize sound test menu state and resources.
        
        Sets up a thread lock for sound state, localizes the menu title, builds the list of testable sound items, and initializes UI state used for selection, scrolling, playback tracking, and fade-in rendering.
        
        Attributes:
            _sound_state_lock: threading.Lock protecting playback state during threaded operations.
            title: Localized title for the sound test screen.
            sounds: Optional sound manager (initially None).
            last_played: Identifier of the most recently played sound.
            last_played_timer: Countdown timer for how long the last_played label is shown.
            scroll_offset: Vertical index offset for the visible items window.
            max_visible_items: Maximum number of items shown at once.
            current_selection: Index of the currently highlighted item.
            playing_all_sounds: True when the background thread is cycling through all sounds.
            stop_all_sounds_thread: Flag to request termination of the background play-all thread.
            sound_items: Ordered list of (label, action) tuples for available test sounds and navigation entries.
            background_alpha: Current alpha used for backdrop fade-in.
            fade_in: Whether the screen is currently fading in.
        """
        import threading
        self._sound_state_lock = threading.Lock()
        try:
            from modul.i18n import gettext
        except Exception:
            def gettext(key):
                """
                Lookup a localized string for the given message key, falling back to the key itself when no translation is available.
                
                Parameters:
                    key (str): The message identifier to translate.
                
                Returns:
                    str: Translated text for `key` when a localization provider is available, otherwise `key` itself.
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
        Prepare the menu for display by resetting visual and playback state.
        
        Resets the fade-in flag and background alpha, clears scrolling and selection to the initial positions, resets sound playback control flags, and refreshes the set of visible items.
        """
        self.fade_in = True
        self.background_alpha = 0
        self.scroll_offset = 0
        self.current_selection = 0
        self.stop_all_sounds_thread = False
        self.playing_all_sounds = False
        self.update_visible_items()

    def set_sounds(self, sounds):
        """
        Attach a Sounds-like object to this menu for playing audio effects.
        
        Parameters:
            sounds: An object exposing sound methods (for example `play_move`, `play_select`, `play_shoot`, `play_explosion`). May be `None` to disable sound playback.
        """
        self.sounds = sounds

    def update_visible_items(self):
        """
        Update the list of sound items currently visible in the menu.
        
        Rebuilds self.visible_items to contain the slice of self.sound_items determined by
        self.scroll_offset and self.max_visible_items, and clamps self.current_selection
        to be a valid index within the updated visible_items list.
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
        Process input and advance the sound-test screen state, returning a navigation action when selected.
        
        Updates fade-in progress and last-played timers, handles up/down navigation and scrolling through sound items, and activates the selected sound or the back action.
        
        Parameters:
            dt (float): Time elapsed since the last update, in seconds.
            events (iterable): Iterable of pygame events to process.
        
        Returns:
            Optional[str]: The action key for the selected sound or "back" if leaving the screen, or `None` if no action was triggered.
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
        Execute a sound test action, update the UI status for the last played sound, and handle threaded "play all" playback or navigation.
        
        Parameters:
            action (str): Key identifying which sound test or control action to perform (e.g., "test_shoot", "test_explosion", "test_all", "back").
        
        Returns:
            str or None: The navigation target "options" when the "back" action was requested, otherwise `None`.
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
                    Lookup a translation for the given message key, falling back to the key when no translation is available.
                    
                    Parameters:
                        k (str): Message key or default text to translate.
                    
                    Returns:
                        str: Translated text for `k` if available, otherwise `k`.
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
                    Lookup a translation for the given message key, falling back to the key when no translation is available.
                    
                    Parameters:
                        k (str): Message key or default text to translate.
                    
                    Returns:
                        str: Translated text for `k` if available, otherwise `k`.
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
                    Lookup a translation for the given message key, falling back to the key when no translation is available.
                    
                    Parameters:
                        k (str): Message key or default text to translate.
                    
                    Returns:
                        str: Translated text for `k` if available, otherwise `k`.
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
                    Lookup a translation for the given message key, falling back to the key when no translation is available.
                    
                    Parameters:
                        k (str): Message key or default text to translate.
                    
                    Returns:
                        str: Translated text for `k` if available, otherwise `k`.
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
                    Lookup a translation for the given message key, falling back to the key when no translation is available.
                    
                    Parameters:
                        k (str): Message key or default text to translate.
                    
                    Returns:
                        str: Translated text for `k` if available, otherwise `k`.
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
                    Lookup a translation for the given message key, falling back to the key when no translation is available.
                    
                    Parameters:
                        k (str): Message key or default text to translate.
                    
                    Returns:
                        str: Translated text for `k` if available, otherwise `k`.
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
                    Lookup a translation for the given message key, falling back to the key when no translation is available.
                    
                    Parameters:
                        k (str): Message key or default text to translate.
                    
                    Returns:
                        str: Translated text for `k` if available, otherwise `k`.
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
                    Lookup a translation for the given message key, falling back to the key when no translation is available.
                    
                    Parameters:
                        k (str): Message key or default text to translate.
                    
                    Returns:
                        str: Translated text for `k` if available, otherwise `k`.
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
                    Lookup a translation for the given message key, falling back to the key when no translation is available.
                    
                    Parameters:
                        k (str): Message key or default text to translate.
                    
                    Returns:
                        str: Translated text for `k` if available, otherwise `k`.
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
                    Lookup a translation for the given message key, falling back to the key when no translation is available.
                    
                    Parameters:
                        k (str): Message key or default text to translate.
                    
                    Returns:
                        str: Translated text for `k` if available, otherwise `k`.
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
                    Lookup a translation for the given message key, falling back to the key when no translation is available.
                    
                    Parameters:
                        k (str): Message key or default text to translate.
                    
                    Returns:
                        str: Translated text for `k` if available, otherwise `k`.
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
                    Lookup a translation for the given message key, falling back to the key when no translation is available.
                    
                    Parameters:
                        k (str): Message key or default text to translate.
                    
                    Returns:
                        str: Translated text for `k` if available, otherwise `k`.
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
                    Lookup a translation for the given message key, falling back to the key when no translation is available.
                    
                    Parameters:
                        k (str): Message key or default text to translate.
                    
                    Returns:
                        str: Translated text for `k` if available, otherwise `k`.
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
                    Lookup a translation for the given message key, falling back to the key when no translation is available.
                    
                    Parameters:
                        k (str): Message key or default text to translate.
                    
                    Returns:
                        str: Translated text for `k` if available, otherwise `k`.
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
                    Lookup a translation for the given message key, falling back to the key when no translation is available.
                    
                    Parameters:
                        k (str): Message key or default text to translate.
                    
                    Returns:
                        str: Translated text for `k` if available, otherwise `k`.
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
                    Lookup a translation for the given message key, falling back to the key when no translation is available.
                    
                    Parameters:
                        k (str): Message key or default text to translate.
                    
                    Returns:
                        str: Translated text for `k` if available, otherwise `k`.
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
                    Lookup a translation for the given message key, falling back to the key when no translation is available.
                    
                    Parameters:
                        k (str): Message key or default text to translate.
                    
                    Returns:
                        str: Translated text for `k` if available, otherwise `k`.
                    """
                    return k
            self.last_played = gettext("sound_played").format(name=gettext("menu_confirm"))
            self.last_played_timer = 2.0


        elif action == "test_all":
            import threading
            import time

            def play_all_sounds():
                """
                Play each configured sound in sequence on the current thread while coordinating safe state updates for a concurrent stopper.
                
                If a sounds manager is available on self.sounds, calls its play methods for a predefined set of sound events in order, pausing 0.8 seconds between each. Periodically checks self.stop_all_sounds_thread under self._sound_state_lock and aborts early if set. Exceptions raised while playing individual sounds are caught and printed. Ensures self.playing_all_sounds is set to False under the same lock when finished or aborted.
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
        Render the menu backdrop and title onto the provided screen and prepare fonts and localization fallback.
        
        Parameters:
            screen (pygame.Surface): Target surface on which the menu background and title are drawn.
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
                Lookup a localized string for the given message key, falling back to the key itself when no translation is available.
                
                Parameters:
                    key (str): The message identifier to translate.
                
                Returns:
                    str: Translated text for `key` when a localization provider is available, otherwise `key` itself.
                """
                return key

class TTSVoiceMenu(Menu):
    """Menu to select a TTS voice from available system voices."""

    def __init__(self, settings):
        """
        Create a TTS voice selection menu and populate it with available voices.
        
        Initializes the menu title from the localized `tts_voice_label`, adds a "Default" option, attempts to enumerate installed TTS voices via the TTS manager and adds one menu item per discovered voice, and finally adds a localized "Back" item. If voice enumeration fails or no TTS manager is available, only the default and back entries are added.
        
        Parameters:
            settings: Application settings object used to read and persist the selected TTS voice.
        """
        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(k):
                """
                Return a localized string for the given translation key, falling back to the key if no translation is available.
                
                Parameters:
                    k (str): Translation key to look up.
                
                Returns:
                    str: Localized string for `k`, or `k` unchanged if a translation cannot be found.
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
        Delegate update processing to the base Menu and propagate any action result.
        
        Parameters:
            dt (float): Time elapsed since the last update, in seconds.
            events (iterable): Sequence of input events to be processed.
        
        Returns:
            action (str or dict): The navigation action or structured result produced by the base update when an item is activated, or `None` if no action occurred.
        """
        result = super().update(dt, events)
        if result:
            return result
        return None

    def handle_action(self, action):
        # Expected action formats: 'tts_voice:<id>' or 'tts_voice:__default__'
        """
        Handle a TTS voice menu action and apply the corresponding settings changes.
        
        Processes actions of the form 'tts_voice:<id>' or 'tts_voice:__default__', updates `self.settings.tts_voice` and `self.settings.tts_voice_language` accordingly, attempts to apply the selection to the runtime TTS manager when available, and persists the settings.
        
        Parameters:
            action (str): Menu action string. Expected formats: 'tts_voice:<id>' to select a specific voice, 'tts_voice:__default__' to restore the default voice, or 'back' to navigate back.
        
        Returns:
            str | None: The navigation target string 'options' when action is 'back', otherwise `None`.
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
        Initialize the achievements menu and populate it with the back action.
        
        Parameters:
            achievement_system: The achievement manager providing achievement data and optional `graphics` mapping used for rendering each achievement.
        """
        super().__init__(f"{C.CREDITS_GAME_NAME} - {gettext('achievements').upper()}")
        self.achievement_system = achievement_system
        self.achievement_graphics = getattr(achievement_system, "graphics", {})
        self.add_item(gettext("back"), "back")

    def draw(self, screen):
        """
        Render the achievements screen onto the given surface.
        
        Draws a translucent backdrop, the menu title, up to twelve achievements in two centered columns (showing ASCII graphics for unlocked achievements when available), the back/menu items, and an overall progress indicator (unlocked vs total).
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
        Process input events and return "back" when Escape or Space is pressed.
        
        Parameters:
            dt (float): Time elapsed since last update, in seconds.
            events (iterable): Iterable of pygame event objects to process.
        
        Returns:
            str or None: The action string returned by the base update if present, `"back"` if Escape or Space was pressed, or `None` otherwise.
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
        Render the ship selection screen with ship previews, the selected ship's details, and on-screen controls.
        
        Renders a dimmed backdrop, a horizontal row of available ships (highlighting the currently selected one and showing locked indicators for unavailable ships), the selected ship's name and descriptive properties (speed, agility, special), and instructional text for navigation and confirmation.
        
        Parameters:
            screen (pygame.Surface): Surface to draw the menu onto.
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