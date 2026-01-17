"""Tests for new features: help screen and session statistics."""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_help_screen_imports():
    """Test that help_screen module can be imported."""
    try:
        from modul.help_screen import HelpScreen
        help_screen = HelpScreen()
        assert hasattr(help_screen, 'activate')
        assert hasattr(help_screen, 'deactivate')
        assert hasattr(help_screen, 'toggle')
        assert hasattr(help_screen, 'update')
        assert hasattr(help_screen, 'draw')
        assert help_screen.active is False
    except ImportError as e:
        assert False, f"Failed to import help_screen: {e}"


def test_help_screen_toggle():
    """Test help screen toggle functionality."""
    from modul.help_screen import HelpScreen
    help_screen = HelpScreen()

    assert help_screen.active is False
    help_screen.toggle()
    assert help_screen.active is True
    help_screen.toggle()
    assert help_screen.active is False


def test_help_screen_activation():
    """Test help screen activation/deactivation."""
    from modul.help_screen import HelpScreen
    help_screen = HelpScreen()

    help_screen.activate()
    assert help_screen.active is True

    help_screen.deactivate()
    assert help_screen.active is False


def test_session_stats_imports():
    """Test that session_stats module can be imported."""
    try:
        from modul.session_stats import SessionStats
        stats = SessionStats()
        assert hasattr(stats, 'reset')
        assert hasattr(stats, 'start_game')
        assert hasattr(stats, 'end_game')
        assert hasattr(stats, 'record_asteroid_destroyed')
        assert hasattr(stats, 'record_enemy_destroyed')
        assert hasattr(stats, 'record_boss_defeated')
        assert hasattr(stats, 'record_powerup_collected')
        assert hasattr(stats, 'record_shot_fired')
        assert hasattr(stats, 'record_life_lost')
        assert hasattr(stats, 'get_summary')
        assert hasattr(stats, 'get_formatted_summary')
    except ImportError as e:
        assert False, f"Failed to import session_stats: {e}"


def test_session_stats_initialization():
    """Test session stats initialization."""
    from modul.session_stats import SessionStats
    stats = SessionStats()

    assert stats.games_played == 0
    assert stats.total_score == 0
    assert stats.highest_score == 0
    assert stats.total_asteroids_destroyed == 0
    assert stats.total_enemies_destroyed == 0
    assert stats.total_bosses_defeated == 0
    assert stats.total_powerups_collected == 0


def test_session_stats_game_tracking():
    """Test game statistics tracking."""
    from modul.session_stats import SessionStats
    stats = SessionStats()

    stats.start_game()
    assert stats.games_played == 1

    stats.end_game(1000, 5)
    assert stats.total_score == 1000
    assert stats.highest_score == 1000
    assert stats.highest_level == 5


def test_session_stats_combat_tracking():
    """Test combat statistics tracking."""
    from modul.session_stats import SessionStats
    stats = SessionStats()

    stats.record_asteroid_destroyed()
    stats.record_asteroid_destroyed()
    assert stats.total_asteroids_destroyed == 2

    stats.record_enemy_destroyed()
    assert stats.total_enemies_destroyed == 1

    stats.record_boss_defeated()
    assert stats.total_bosses_defeated == 1


def test_session_stats_powerup_tracking():
    """Test power-up collection tracking."""
    from modul.session_stats import SessionStats
    stats = SessionStats()

    stats.record_powerup_collected()
    stats.record_powerup_collected()
    stats.record_powerup_collected()
    assert stats.total_powerups_collected == 3


def test_session_stats_life_tracking():
    """Test life lost tracking."""
    from modul.session_stats import SessionStats
    stats = SessionStats()

    stats.record_life_lost()
    stats.record_life_lost()
    assert stats.total_lives_lost == 2


def test_session_stats_average_score():
    """Test average score calculation."""
    from modul.session_stats import SessionStats
    stats = SessionStats()

    stats.start_game()
    stats.end_game(1000, 5)
    stats.start_game()
    stats.end_game(2000, 10)

    avg = stats.get_average_score()
    assert avg == 1500.0


def test_session_stats_summary():
    """Test statistics summary generation."""
    from modul.session_stats import SessionStats
    stats = SessionStats()

    stats.start_game()
    stats.record_asteroid_destroyed()
    stats.record_powerup_collected()
    stats.end_game(500, 3)

    summary = stats.get_summary()
    assert isinstance(summary, dict)
    assert 'games_played' in summary
    assert 'highest_score' in summary
    assert 'total_asteroids_destroyed' in summary
    assert 'total_powerups_collected' in summary
    assert summary['games_played'] == 1
    assert summary['highest_score'] == 500


def test_session_stats_formatted_summary():
    """Test formatted statistics summary."""
    from modul.session_stats import SessionStats
    stats = SessionStats()

    stats.start_game()
    stats.end_game(1000, 5)

    formatted = stats.get_formatted_summary()
    assert isinstance(formatted, str)
    assert 'SESSION STATISTICS' in formatted
    assert 'Games Played:' in formatted
    assert 'Highest Score:' in formatted


def test_session_stats_time_formatting():
    """Test time formatting."""
    from modul.session_stats import SessionStats
    stats = SessionStats()

    formatted = stats.format_time(3665)  # 1 hour, 1 minute, 5 seconds
    assert formatted == "01:01:05"

    formatted = stats.format_time(125)  # 2 minutes, 5 seconds
    assert formatted == "00:02:05"


def test_parse_arguments_function():
    """Test argument parsing function exists."""
    import main
    assert callable(main.parse_arguments)


def test_setup_logging_function():
    """Test logging setup function exists."""
    import main
    assert callable(main.setup_logging)
