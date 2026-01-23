"""Tests for the simple Menu class behavior."""

import pygame
import pytest

from modul.menu import Menu


@pytest.fixture(autouse=True)
def init_pygame(monkeypatch):
    """Initialize pygame for each test (headless-safe)"""
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")
    pygame.init()
    pygame.font.init()
    yield
    pygame.quit()


def test_menu_initial_state():
    """Test that the menu initializes with the correct default state."""
    menu = Menu(title="Test")
    assert menu.selected_index == 0
    assert isinstance(menu.items, list)


def test_menu_select_index():
    """Test setting the selected index of the menu."""
    menu = Menu(title="Test")
    menu.add_item("A", "a")
    menu.add_item("B", "b")
    menu.add_item("C", "c")
    menu.selected_index = 2
    assert menu.selected_index == 2
    assert menu.items[menu.selected_index].text == "C"


def test_menu_add_and_select_item():
    menu = Menu(title="Test")
    menu.add_item("Start", "start")
    menu.add_item("Optionen", "options")
    menu.add_item("Beenden", "quit")
    menu.selected_index = 1
    # Menu stores MenuItem objects; check the displayed text property.
    assert menu.items[menu.selected_index].text == "Optionen"
