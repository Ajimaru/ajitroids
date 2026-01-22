"""Tests for stats dashboard functionality."""

from unittest.mock import MagicMock

import pytest
import pygame

from modul.session_stats import SessionStats
from modul.stats_dashboard import StatsDashboard


@pytest.fixture(autouse=True)
def init_pygame(monkeypatch):
    """Initialize pygame for each test (headless-safe)"""
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")
    pygame.init()
    pygame.font.init()
    yield
    pygame.quit()


@pytest.fixture
def session_stats():
    """Create a session stats instance with some data."""
    stats = SessionStats()
    stats.games_played = 5
    stats.total_score = 50000
    stats.highest_score = 15000
    stats.highest_level = 25
    stats.total_asteroids_destroyed = 200
    stats.total_enemies_destroyed = 10
    stats.total_bosses_defeated = 2
    stats.total_powerups_collected = 30
    stats.total_lives_lost = 8
    stats.total_shots_fired = 500
    stats.total_playtime = 3600.0
    return stats


def test_stats_dashboard_initialization(session_stats):
    """Test that stats dashboard initializes correctly."""
    dashboard = StatsDashboard(session_stats)

    assert dashboard.session_stats == session_stats
    assert dashboard.background_alpha == 0
    assert dashboard.fade_in is False


def test_stats_dashboard_activate(session_stats):
    """Test that activating the dashboard sets fade_in."""
    dashboard = StatsDashboard(session_stats)
    dashboard.activate()

    assert dashboard.fade_in is True
    assert dashboard.background_alpha == 0


def test_stats_dashboard_fade_in(session_stats):
    """Test that dashboard fades in over time."""
    dashboard = StatsDashboard(session_stats)
    dashboard.activate()

    initial_alpha = dashboard.background_alpha
    action = dashboard.update(0.5, [])

    assert dashboard.background_alpha > initial_alpha
    assert action is None


def test_stats_dashboard_escape_key(session_stats):
    """Test that ESC key returns back action."""
    dashboard = StatsDashboard(session_stats)

    events = [MagicMock(type=pygame.KEYDOWN, key=pygame.K_ESCAPE)]
    action = dashboard.update(0.016, events)

    assert action == "back"


def test_stats_dashboard_space_key(session_stats):
    """Test that SPACE key returns back action."""
    dashboard = StatsDashboard(session_stats)

    events = [MagicMock(type=pygame.KEYDOWN, key=pygame.K_SPACE)]
    action = dashboard.update(0.016, events)

    assert action == "back"


def test_stats_dashboard_draw(session_stats):
    """Test that drawing the dashboard doesn't raise errors."""
    screen = pygame.display.set_mode((1280, 720))
    dashboard = StatsDashboard(session_stats)
    dashboard.background_alpha = 180

    # Should not raise an error
    dashboard.draw(screen)
    assert True


def test_stats_dashboard_with_no_games(session_stats):
    """Test stats dashboard with no games played."""
    stats = SessionStats()
    dashboard = StatsDashboard(stats)
    screen = pygame.display.set_mode((1280, 720))
    dashboard.background_alpha = 180

    # Should handle zero values gracefully
    dashboard.draw(screen)
    assert True


def test_stats_dashboard_get_summary(session_stats):
    """Test that stats summary has all required fields."""
    summary = session_stats.get_summary()

    required_fields = [
        'games_played', 'total_score', 'highest_score', 'highest_level',
        'average_score', 'total_asteroids_destroyed', 'total_enemies_destroyed',
        'total_bosses_defeated', 'total_powerups_collected', 'total_lives_lost',
        'total_playtime', 'session_duration'
    ]

    for field in required_fields:
        assert field in summary


def test_stats_dashboard_accuracy_calculation(session_stats):
    """Test that accuracy is calculated correctly."""
    accuracy = session_stats.get_accuracy()

    # With 200 asteroids + 10 enemies = 210 hits, 500 shots fired
    expected_accuracy = (210 / 500) * 100
    assert accuracy == pytest.approx(expected_accuracy, rel=0.01)


def test_stats_dashboard_average_score(session_stats):
    """Test average score calculation."""
    avg_score = session_stats.get_average_score()

    # 50000 total / 5 games = 10000 average
    assert avg_score == 10000.0


def test_stats_dashboard_format_time(session_stats):
    """Test time formatting."""
    # Test 1 hour
    formatted = session_stats.format_time(3600)
    assert formatted == "01:00:00"

    # Test 90 minutes
    formatted = session_stats.format_time(5400)
    assert formatted == "01:30:00"

    # Test 30 seconds
    formatted = session_stats.format_time(30)
    assert formatted == "00:00:30"


def test_session_stats_record_methods(session_stats):
    """Test that record methods increment correctly."""
    initial_asteroids = session_stats.total_asteroids_destroyed
    session_stats.record_asteroid_destroyed()
    assert session_stats.total_asteroids_destroyed == initial_asteroids + 1

    initial_enemies = session_stats.total_enemies_destroyed
    session_stats.record_enemy_destroyed()
    assert session_stats.total_enemies_destroyed == initial_enemies + 1

    initial_bosses = session_stats.total_bosses_defeated
    session_stats.record_boss_defeated()
    assert session_stats.total_bosses_defeated == initial_bosses + 1

    initial_powerups = session_stats.total_powerups_collected
    session_stats.record_powerup_collected()
    assert session_stats.total_powerups_collected == initial_powerups + 1

    initial_shots = session_stats.total_shots_fired
    session_stats.record_shot_fired()
    assert session_stats.total_shots_fired == initial_shots + 1

    initial_lives = session_stats.total_lives_lost
    session_stats.record_life_lost()
    assert session_stats.total_lives_lost == initial_lives + 1
