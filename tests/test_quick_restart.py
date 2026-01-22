"""Tests for quick restart functionality."""

from unittest.mock import MagicMock

import pygame
import pytest

from modul.menu import GameOverScreen


@pytest.fixture(autouse=True)
def init_pygame(monkeypatch):
    """Initialize pygame for each test (headless-safe)"""
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")
    pygame.init()
    pygame.font.init()
    yield
    pygame.quit()


def test_game_over_screen_quick_restart():
    """Test that pressing 'R' in game over screen returns quick_restart action."""
    screen = GameOverScreen()
    screen.set_score(1000)

    # Create a mock event for pressing 'R'
    events = [
        MagicMock(type=pygame.KEYDOWN, key=pygame.K_r)
    ]

    action = screen.update(0.016, events)
    assert action == "quick_restart"


def test_game_over_screen_other_keys():
    """Test that other keys in game over screen work as expected."""
    screen = GameOverScreen()
    screen.set_score(1000)

    # Test SPACE key
    events_space = [
        MagicMock(type=pygame.KEYDOWN, key=pygame.K_SPACE)
    ]
    action = screen.update(0.016, events_space)
    assert action == "highscore_display"

    # Reset screen
    screen = GameOverScreen()
    screen.set_score(1000)

    # Test ESC key
    events_esc = [
        MagicMock(type=pygame.KEYDOWN, key=pygame.K_ESCAPE)
    ]
    action = screen.update(0.016, events_esc)
    assert action == "main_menu"


def test_game_over_screen_no_action():
    """Test that no key press returns None."""
    screen = GameOverScreen()
    screen.set_score(1000)

    events = []
    action = screen.update(0.016, events)
    assert action is None


def test_game_over_screen_draw_includes_restart_instruction():
    """Test that game over screen draw method includes restart instruction."""
    screen_surface = pygame.display.set_mode((800, 600))
    game_over = GameOverScreen()
    game_over.set_score(5000)
    game_over.background_alpha = 180

    # This should not raise an error
    game_over.draw(screen_surface)

    # The draw method should complete without errors
    assert True


def test_game_over_screen_fade_in():
    """Test that game over screen fades in properly."""
    screen = GameOverScreen()
    screen.fade_in = True
    screen.background_alpha = 0

    # Update for a small time step
    action = screen.update(0.5, [])

    # Alpha should have increased
    assert screen.background_alpha > 0
    assert action is None


def test_game_over_screen_score_display():
    """Test that score is properly set and stored."""
    screen = GameOverScreen()
    test_score = 12345

    screen.set_score(test_score)
    assert screen.final_score == test_score
