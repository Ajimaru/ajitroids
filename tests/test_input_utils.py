"""Tests for input utilities and action bindings."""

import types

import modul.input_utils as input_utils
import modul.settings as settings_mod


def test_get_action_binding_default(monkeypatch):
    # Ensure no runtime settings
    monkeypatch.delattr(settings_mod, "current_settings", raising=False)
    assert input_utils.get_action_binding("shoot") == "K_SPACE"


def test_get_action_binding_from_settings(monkeypatch):
    s = types.SimpleNamespace(controls={"shoot": "space"})
    monkeypatch.setattr(settings_mod, "current_settings", s)
    assert input_utils.get_action_binding("shoot") == "space"


def test_get_action_keycode_keyboard(monkeypatch):
    # Mock pygame.key.key_code
    monkeypatch.setattr(input_utils.pygame.key, "key_code", lambda name: 32)
    s = types.SimpleNamespace(controls={"shoot": "space"})
    monkeypatch.setattr(settings_mod, "current_settings", s)
    assert input_utils.get_action_keycode("shoot") == 32


def test_is_action_pressed_keyboard(monkeypatch):
    # Simulate key pressed array where index 32 is True
    keys = [False] * 512
    keys[32] = True
    monkeypatch.setattr(input_utils.pygame.key, "key_code", lambda name: 32)
    monkeypatch.setattr(input_utils.pygame.key, "get_pressed", lambda: keys)
    s = types.SimpleNamespace(controls={"shoot": "space"})
    monkeypatch.setattr(settings_mod, "current_settings", s)
    assert input_utils.is_action_pressed("shoot") is True


def test_is_action_pressed_joy_button(monkeypatch):
    # Mock joystick
    class DummyJoy:
        def __init__(self):
            pass

        def init(self):
            pass

        def get_button(self, b):
            return 1 if b == 1 else 0

        def get_axis(self, a):
            return 0.0

        def get_hat(self, h):
            return (0, 0)

    monkeypatch.setattr(input_utils.pygame.joystick, "get_count", lambda: 1)
    monkeypatch.setattr(input_utils.pygame.joystick, "Joystick", lambda idx: DummyJoy())

    s = types.SimpleNamespace(controls={"shoot": "JOY0_BUTTON1"})
    monkeypatch.setattr(settings_mod, "current_settings", s)
    assert input_utils.is_action_pressed("shoot") is True
