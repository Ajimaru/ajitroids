"""Utilities for mapping actions to input bindings and keycodes."""

import pygame
from typing import Optional
from modul import settings as settings_mod


def key_name_to_keycode(name: str) -> Optional[int]:
    """Convert a readable pygame key name (e.g. 'K_SPACE' or 'space')
    to a pygame key constant.
    """
    if not name:
        return None

    # If already a pygame constant name like 'K_SPACE'
    # `hasattr` is safe and should not raise; directly check
    if hasattr(pygame, name):
        try:
            return getattr(pygame, name)
        except AttributeError:
            pass

    # Try pygame.key.key_code for common names like 'space', 'left'
    try:
        return pygame.key.key_code(name)
    except (AttributeError, ValueError):
        return None


def keycode_to_display_name(keycode: int) -> str:
    """Return a human-friendly name for a pygame keycode."""
    try:
        return pygame.key.name(keycode)
    except (AttributeError, TypeError):
        return str(keycode)


# Default hardcoded fallbacks matching previous behavior
_DEFAULT_ACTION_TO_KEY = {
    "rotate_left": "K_LEFT",
    "rotate_right": "K_RIGHT",
    "thrust": "K_UP",
    "reverse": "K_DOWN",
    "shoot": "K_SPACE",
    "switch_weapon": "K_b",
    "pause": "K_ESCAPE",
}


def get_action_keycode(action: str) -> Optional[int]:
    """Get the pygame keycode for an action using current settings when
    available; otherwise fall back to defaults.
    """
    # Prefer runtime settings singleton when present
    settings = getattr(settings_mod, "current_settings", None)
    key_name = None
    if settings and hasattr(settings, "controls"):
        key_name = settings.controls.get(action)
    if not key_name:
        key_name = _DEFAULT_ACTION_TO_KEY.get(action)
    # Only return a pygame keycode for keyboard bindings
    if key_name and not key_name.startswith("JOY"):
        return key_name_to_keycode(key_name)
    return None


def get_action_binding(action: str) -> Optional[str]:
    """Return raw readable binding (keyboard name or JOY... string)
    for the given action.
    """
    settings = getattr(settings_mod, "current_settings", None)
    binding = None
    if settings and hasattr(settings, "controls"):
        binding = settings.controls.get(action)
    if not binding:
        binding = _DEFAULT_ACTION_TO_KEY.get(action)
    return binding


def is_action_pressed(action: str) -> bool:
    """Return True if the mapped key for `action` is currently pressed."""
    binding = get_action_binding(action)
    if not binding:
        return False

    try:
        # Joystick binding patterns:
        #  - JOY{n}_BUTTON{b}
        #  - JOY{n}_AXIS{a}_POS/NEG
        #  - JOY{n}_HAT{h}_UP/LEFT
        if binding.startswith("JOY"):
            parts = binding.split("_")
            joy_part = parts[0]
            try:
                joy_id = int(joy_part[3:])
            except ValueError:
                return False

            if pygame.joystick.get_count() <= joy_id:
                return False
            joy = pygame.joystick.Joystick(joy_id)
            try:
                joy.init()
            except Exception:
                # Some joysticks may not initialize; treat as not pressed
                return False

            if len(parts) >= 2 and parts[1].startswith("BUTTON"):
                try:
                    btn = int(parts[1][6:])
                    return bool(joy.get_button(btn))
                except (ValueError, IndexError, AttributeError):
                    return False

            if len(parts) >= 2 and parts[1].startswith("AXIS"):
                try:
                    axis = int(parts[1][4:])
                    direction = parts[2] if len(parts) > 2 else "POS"
                    val = joy.get_axis(axis)
                    if direction == "POS":
                        return val >= 0.6
                    return val <= -0.6
                except (ValueError, IndexError, AttributeError):
                    return False

            if len(parts) >= 2 and parts[1].startswith("HAT"):
                try:
                    hat = int(parts[1][3:])
                    hat_val = joy.get_hat(hat)
                    if len(parts) > 2:
                        dirs = parts[2].split("_")
                        x, y = hat_val
                        for d in dirs:
                            if d == "UP" and y != 1:
                                return False
                            if d == "DOWN" and y != -1:
                                return False
                            if d == "LEFT" and x != -1:
                                return False
                            if d == "RIGHT" and x != 1:
                                return False
                        return True
                    return hat_val != (0, 0)
                except (ValueError, IndexError, AttributeError):
                    return False

            return False

        # Fallback to keyboard
        keycode = key_name_to_keycode(binding)
        if keycode is None:
            return False
        keys = pygame.key.get_pressed()
        try:
            return bool(keys[keycode])
        except (IndexError, TypeError):
            return False
    except Exception:
        # Unexpected errors in input handling should be treated as not-pressed
        return False
