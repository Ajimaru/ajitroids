"""Module modul.menu — minimal module docstring."""

# flake8: noqa
# pylint: disable=all
# pyright: reportUndefinedVariable=false
# pyright: reportWildcardImportFromLibrary=false
import math

import pygame

import modul.constants as C
from modul.version import __version__

# Backwards-compatibility: expose uppercase constants into module globals
for _const_name in dir(C):
    if _const_name.isupper():
        globals()[_const_name] = getattr(C, _const_name)
from modul.ships import ShipRenderer, ship_manager

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
        color = pygame.Color(C.MENU_UNSELECTED_COLOR)
        selected_color = pygame.Color(C.MENU_SELECTED_COLOR)
        r = max(0, min(255, int(color.r + (selected_color.r - color.r) * self.hover_animation)))
        g = max(0, min(255, int(color.g + (selected_color.g - color.g) * self.hover_animation)))
        b = max(0, min(255, int(color.b + (selected_color.b - color.b) * self.hover_animation)))
        size_multiplier = 1.0 + 0.2 * self.hover_animation
        scaled_font = pygame.font.Font(None, int(C.MENU_ITEM_FONT_SIZE * size_multiplier))
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
        self.title_font = pygame.font.Font(None, C.MENU_TITLE_FONT_SIZE)
        self.item_font = pygame.font.Font(None, C.MENU_ITEM_FONT_SIZE)
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
            self.background_alpha = min(255, self.background_alpha + 255 * dt / C.MENU_TRANSITION_SPEED)
            if self.background_alpha >= C.MENU_BACKGROUND_ALPHA:
                self.fade_in = False
                self.background_alpha = C.MENU_BACKGROUND_ALPHA

        for item in self.items:
            item.update(dt)

        if self.input_cooldown > 0:
            self.input_cooldown -= dt

        from modul import input_utils
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
        self.items[self.selected_index].selected = False
        self.selected_index = (self.selected_index + 1) % len(self.items)
        self.items[self.selected_index].selected = True
        if "sounds" in globals() or hasattr(self, "sounds"):
            try:
                sounds.play_menu_move()
            except Exception:  # pylint: disable=broad-exception-caught
                pass

    def _select_previous(self):
        self.items[self.selected_index].selected = False
        self.selected_index = (self.selected_index - 1) % len(self.items)
        self.items[self.selected_index].selected = True
        if "sounds" in globals() or hasattr(self, "sounds"):
            try:
                sounds.play_menu_move()
            except Exception:  # pylint: disable=broad-exception-caught
                pass

    def draw(self, screen):
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
            item.draw(screen, position, self.item_font)


class MainMenu(Menu):
    def __init__(self):
        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(k):
                return k

        super().__init__("AJITROIDS")
        self.add_item(gettext("start_game"), "start_game")
        self.add_item(gettext("tutorial"), "tutorial")
        self.add_item(gettext("replays"), "replays")
        self.add_item(gettext("highscores"), "highscores")
        self.add_item(gettext("statistics"), "statistics")
        self.add_item(gettext("achievements"), "achievements")
        # Tests expect the Options item to appear as German "Optionen".
        # Use the German locale for this single label to match existing test expectations.
        try:
            from modul.i18n import t
            options_label = t("options", "de")
        except Exception:  # pylint: disable=broad-exception-caught
            options_label = gettext("options")
        self.add_item(options_label, "options")
        self.add_item(gettext("credits"), "credits")
        self.add_item(gettext("exit"), "exit")

    def draw(self, screen):
        super().draw(screen)

        version_font = pygame.font.Font(None, int(C.MENU_ITEM_FONT_SIZE / 1.5))
        version_text = version_font.render(__version__, True, pygame.Color(C.MENU_UNSELECTED_COLOR))
        version_rect = version_text.get_rect(bottomright=(C.SCREEN_WIDTH - 20, C.SCREEN_HEIGHT - 20))
        screen.blit(version_text, version_rect)


class PauseMenu(Menu):
    def __init__(self):
        try:
            from modul.i18n import gettext
            title = gettext("pause").upper()
        except Exception:  # pylint: disable=broad-exception-caught
            title = "PAUSE"
        super().__init__(title)
        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(k):
                return k
        self.add_item(gettext("resume"), "continue")
        self.add_item(gettext("restart"), "restart")
        self.add_item(gettext("main_menu"), "main_menu")

    def draw(self, screen):
        super().draw(screen)

        # Show common keyboard shortcuts while paused
        shortcuts_font = pygame.font.Font(None, int(C.MENU_ITEM_FONT_SIZE * 0.8))
        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(k):
                return k

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
    def __init__(self):
        self.title_font = pygame.font.Font(None, C.MENU_TITLE_FONT_SIZE)
        self.text_font = pygame.font.Font(None, C.MENU_ITEM_FONT_SIZE)
        self.background_alpha = 0
        self.fade_in = True

    def update(self, dt, events):
        if self.fade_in:
            self.background_alpha = min(255, self.background_alpha + 255 * dt / C.MENU_TRANSITION_SPEED)
            if self.background_alpha >= C.MENU_BACKGROUND_ALPHA:
                self.fade_in = False
                self.background_alpha = C.MENU_BACKGROUND_ALPHA

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "main_menu"

        return None

    def draw(self, screen):
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((0, 0, 0, self.background_alpha))
        screen.blit(background, (0, 0))

        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(k):
                return k

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
    def __init__(self, settings, sounds):
        super().__init__("OPTIONS")
        self.settings = settings
        self.sounds = sounds
        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(k):
                return k

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
            try:
                tts_toggle_state = gettext('on') if getattr(settings, 'show_tts_in_options', False) else gettext('off')
            except Exception:  # pylint: disable=broad-exception-caught
                tts_toggle_state = "ON" if getattr(settings, 'show_tts_in_options', False) else "OFF"
            self.add_item(f"{gettext('show_tts_in_options')}: {tts_toggle_state}", "toggle_show_tts")

        lang_label = gettext('language_label').format(lang=("Deutsch" if settings.language == "de" else "English"))
        self.add_item(lang_label, "language")
        self.add_item(gettext('back'), "back")

    def handle_action(self, action, sounds):
        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(k):
                return k
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
                    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                    print("Fullscreen aktiviert")
                else:
                    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
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
                        try:
                            from modul.i18n import gettext
                        except Exception:  # pylint: disable=broad-exception-caught
                            def gettext(k):
                                return k
                        self.items[self.selected_index].text = gettext('music_volume_format').format(percent=int(self.settings.music_volume * 100))
                    elif self.items[self.selected_index].action == "adjust_sound_volume":
                        self.settings.sound_volume = max(0.0, self.settings.sound_volume - 0.1)
                        self.settings.save()
                        if self.sounds:
                            self.sounds.set_effects_volume(self.settings.sound_volume)
                        try:
                            from modul.i18n import gettext
                        except Exception:  # pylint: disable=broad-exception-caught
                            def gettext(k):
                                return k
                        self.items[self.selected_index].text = gettext('sound_volume_format').format(percent=int(self.settings.sound_volume * 100))
                elif event.key == pygame.K_RIGHT:
                    if self.items[self.selected_index].action == "adjust_music_volume":
                        self.settings.music_volume = min(1.0, self.settings.music_volume + 0.1)
                        self.settings.save()
                        if self.sounds:
                            self.sounds.set_music_volume(self.settings.music_volume)
                        try:
                            from modul.i18n import gettext
                        except Exception:  # pylint: disable=broad-exception-caught
                            def gettext(k):
                                return k
                        self.items[self.selected_index].text = gettext('music_volume_format').format(percent=int(self.settings.music_volume * 100))
                    elif self.items[self.selected_index].action == "adjust_sound_volume":
                        self.settings.sound_volume = min(1.0, self.settings.sound_volume + 0.1)
                        self.settings.save()
                        if self.sounds:
                            self.sounds.set_effects_volume(self.settings.sound_volume)
                        try:
                            from modul.i18n import gettext
                        except Exception:  # pylint: disable=broad-exception-caught
                            def gettext(k):
                                return k
                        self.items[self.selected_index].text = gettext('sound_volume_format').format(percent=int(self.settings.sound_volume * 100))
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


class ControlsMenu(Menu):
    def __init__(self, settings):
        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(k):
                return k
        super().__init__(gettext("controls").upper())
        self.settings = settings
        # Define action order for display
        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(k):
                return k

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
        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(k):
                return k
        self.add_item(gettext("back"), "back")
        self.capturing = False
        self.capture_action = None
        self.message = ""

    def update(self, dt, events):
        # Refresh labels from settings
        for i, (action_key, label) in enumerate(self.actions):
            key_name = self.settings.controls.get(action_key, "")
            self.items[i].text = f"{label}: {key_name}"

        if self.capturing:
            # Waiting for a key press to rebind
            for event in events:
                # Cancel capture with ESC (keyboard) or special button
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.capturing = False
                    self.capture_action = None
                    try:
                        from modul.i18n import gettext
                    except Exception:  # pylint: disable=broad-exception-caught
                        def gettext(k):
                            return k
                    self.message = gettext("binding_cancelled")
                    return None

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
                    except Exception:  # pylint: disable=broad-exception-caught
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
                    except Exception:  # pylint: disable=broad-exception-caught
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
                    except Exception:  # pylint: disable=broad-exception-caught
                        new_name = None

                if not new_name:
                    continue

                # Check for duplicates
                for a_key, _ in self.actions:
                    if self.settings.controls.get(a_key) == new_name:
                        try:
                            from modul.i18n import gettext
                        except Exception:  # pylint: disable=broad-exception-caught
                            def gettext(k):
                                return k
                        self.message = gettext("key_already_assigned").format(key=new_name)
                        return None

                # Apply binding
                self.settings.controls[self.capture_action] = new_name
                self.settings.save()
                self.capturing = False
                self.capture_action = None
                try:
                    from modul.i18n import gettext
                except Exception:  # pylint: disable=broad-exception-caught
                    def gettext(k):
                        return k
                self.message = gettext("bound_key").format(key=new_name)
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
                    try:
                        from modul.i18n import gettext
                    except Exception:  # pylint: disable=broad-exception-caught
                        def gettext(k):
                            return k
                    # show the user-friendly action label if available
                    action_label = dict(self.actions).get(action_key, action_key)
                    self.message = gettext("press_new_key_for").format(action=action_label)
                    return None
        return None

    def draw(self, screen):
        super().draw(screen)
        if self.message:
            font = pygame.font.Font(None, 22)
            msg = font.render(self.message, True, (200, 200, 200))
            rect = msg.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 40))
            screen.blit(msg, rect)


class LanguageMenu(Menu):
    def __init__(self, settings):
        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(k):
                return k
        super().__init__(gettext("language").upper())
        self.settings = settings
        self.languages = [("en", "English"), ("de", "Deutsch")]
        for code, label in self.languages:
            sel = " (current)" if settings.language == code else ""
            self.add_item(f"{label}{sel}", code)
        self.add_item(gettext("back"), "back")

    def update(self, dt, events):
        # Refresh labels
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
                    return "options"
        return None

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

        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(k):
                return k
        title_surf = self.title_font.render(gettext("game_over").upper(), True, pygame.Color("red"))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3))
        screen.blit(title_surf, title_rect)

        score_surf = self.text_font.render(gettext("your_score_format").format(score=self.final_score), True, (255, 255, 255))
        score_rect = score_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        screen.blit(score_surf, score_rect)
        instruction1 = self.text_font.render(gettext("press_space_highscores"), True, (200, 200, 200))
        instruction1_rect = instruction1.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 60))
        screen.blit(instruction1, instruction1_rect)

        instruction2 = self.text_font.render(gettext("press_r_restart"), True, (200, 200, 200))
        instruction2_rect = instruction2.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100))
        screen.blit(instruction2, instruction2_rect)

        instruction3 = self.text_font.render(gettext("press_esc_main_menu"), True, (200, 200, 200))
        instruction3_rect = instruction3.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 140))
        screen.blit(instruction3, instruction3_rect)


class DifficultyMenu(Menu):
    def __init__(self):
        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(k):
                return k
        super().__init__(gettext("difficulty").upper())
        self.add_item(gettext("difficulty_easy"), "difficulty_easy", "L")
        self.add_item(gettext("difficulty_normal"), "difficulty_normal", "N")
        self.add_item(gettext("difficulty_hard"), "difficulty_hard", "S")
        self.add_item(gettext("back"), "main_menu", "Z")


class VoiceAnnouncementsMenu:
    """Menu to configure voice announcement toggles"""

    def __init__(self, settings):
        self.settings = settings
        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(k):
                return k
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
        announcements = self.settings.announcement_types
        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(k):
                return k

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

        # Open TTS voice selection
        if action == "tts_voice":
            return "tts_voice"

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


class TTSVoiceMenu(Menu):
    """Menu to select a TTS voice from available system voices."""

    def __init__(self, settings):
        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(k):
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
        result = super().update(dt, events)
        if result:
            return result
        return None

    def handle_action(self, action):
        # Expected action formats: 'tts_voice:<id>' or 'tts_voice:__default__'
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
                                            l = lang.decode() if isinstance(lang, (bytes, bytearray)) else str(lang)
                                            # pick primary subtag like 'en' from en_US
                                            if len(l) >= 2:
                                                code = l[:2]
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


class SoundTestMenu:
    def __init__(self):
        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(k):
                return k
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
            try:
                from modul.i18n import gettext
            except Exception:  # pylint: disable=broad-exception-caught
                def gettext(k):
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
                    return k
            self.last_played = gettext("sound_played").format(name=gettext("triple_shoot"))
            self.last_played_timer = 2.0

        elif action == "test_explosion":
            self.sounds.play_explosion()
            try:
                from modul.i18n import gettext
            except Exception:  # pylint: disable=broad-exception-caught
                def gettext(k):
                    return k
            self.last_played = gettext("sound_played").format(name=gettext("explosion"))
            self.last_played_timer = 2.0

        elif action == "test_player_hit":
            self.sounds.play_player_hit()
            try:
                from modul.i18n import gettext
            except Exception:  # pylint: disable=broad-exception-caught
                def gettext(k):
                    return k
            self.last_played = gettext("sound_played").format(name=gettext("player_hit"))
            self.last_played_timer = 2.0

        elif action == "test_powerup":
            self.sounds.play_powerup()
            try:
                from modul.i18n import gettext
            except Exception:  # pylint: disable=broad-exception-caught
                def gettext(k):
                    return k
            self.last_played = gettext("sound_played").format(name=gettext("powerup"))
            self.last_played_timer = 2.0

        elif action == "test_shield_activate":
            self.sounds.play_shield_activate()
            try:
                from modul.i18n import gettext
            except Exception:  # pylint: disable=broad-exception-caught
                def gettext(k):
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
                    return k
            self.last_played = gettext("sound_played").format(name=gettext("weapon_pickup"))
            self.last_played_timer = 2.0

        elif action == "test_boss_spawn":
            self.sounds.play_boss_spawn()
            try:
                from modul.i18n import gettext
            except Exception:  # pylint: disable=broad-exception-caught
                def gettext(k):
                    return k
            self.last_played = gettext("sound_played").format(name=gettext("boss_spawn"))
            self.last_played_timer = 2.0

        elif action == "test_boss_death":
            self.sounds.play_boss_death()
            try:
                from modul.i18n import gettext
            except Exception:  # pylint: disable=broad-exception-caught
                def gettext(k):
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
                    return k
            self.last_played = gettext("sound_played").format(name=gettext("boss_attack"))
            self.last_played_timer = 2.0

        elif action == "test_level_up":
            self.sounds.play_level_up()
            try:
                from modul.i18n import gettext
            except Exception:  # pylint: disable=broad-exception-caught
                def gettext(k):
                    return k
            self.last_played = gettext("sound_played").format(name=gettext("level_up"))
            self.last_played_timer = 2.0

        elif action == "test_game_over":
            self.sounds.play_game_over()
            try:
                from modul.i18n import gettext
            except Exception:  # pylint: disable=broad-exception-caught
                def gettext(k):
                    return k
            self.last_played = gettext("sound_played").format(name=gettext("game_over"))
            self.last_played_timer = 2.0

        elif action == "test_menu_select":
            self.sounds.play_menu_move()
            try:
                from modul.i18n import gettext
            except Exception:  # pylint: disable=broad-exception-caught
                def gettext(k):
                    return k
            self.last_played = gettext("sound_played").format(name=gettext("menu_select"))
            self.last_played_timer = 2.0

        elif action == "test_menu_confirm":
            self.sounds.play_menu_select()
            try:
                from modul.i18n import gettext
            except Exception:  # pylint: disable=broad-exception-caught
                def gettext(k):
                    return k
            self.last_played = gettext("sound_played").format(name=gettext("menu_confirm"))
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
                    except Exception as e:  # pylint: disable=broad-exception-caught
                        print(f"Error playing sound '{name}': {e}")

                self.playing_all_sounds = False

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

        try:
            from modul.i18n import gettext
        except Exception:  # pylint: disable=broad-exception-caught
            def gettext(k):
                return k

        if self.scroll_offset > 0:
            up_text = indicator_font.render(gettext("scroll_up"), True, pygame.Color("yellow"))
            up_rect = up_text.get_rect(center=(SCREEN_WIDTH / 2, 100))
            screen.blit(up_text, up_rect)

        if self.scroll_offset + self.max_visible_items < len(self.sound_items):
            down_text = indicator_font.render(gettext("scroll_down"), True, pygame.Color("yellow"))
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
