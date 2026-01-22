"""Tests ensuring the main module imports and basic structures."""

import sys
import os
import unittest.mock

# Add the project root to the path so we can import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_main_module_imports():
    """Test that main.py can be imported without errors"""
    try:
        import main
        assert hasattr(main, 'main')
        assert hasattr(main, 'GameSettings')
        assert hasattr(main, 'player_hit')
        assert hasattr(main, 'toggle_fullscreen')
        assert hasattr(main, 'debug_music_status')
        assert hasattr(main, 'parse_arguments')
        assert hasattr(main, 'setup_logging')
    except ImportError as e:
        assert False, f"Failed to import main.py: {e}"

def test_game_settings_initialization():
    """Test GameSettings class initialization"""
    import main
    settings = main.GameSettings()
    assert hasattr(settings, 'fullscreen')
    assert settings.fullscreen is False

@unittest.mock.patch('main.pygame.init')
@unittest.mock.patch('main.pygame.display.set_mode')
@unittest.mock.patch('main.pygame.time.Clock')
def test_main_function_structure(mock_clock, mock_display, mock_init):
    """Test that main function can be called without actually running the game"""
    import main

    # Mock pygame to prevent actual game initialization
    mock_init.return_value = None
    mock_display.return_value = unittest.mock.MagicMock()
    mock_clock.return_value = unittest.mock.MagicMock()

    # This test just ensures main function exists and can be imported
    # We don't actually run it to avoid starting the game
    assert callable(main.main)

def test_helper_functions():
    """Test utility functions in main.py"""
    import main

    # Test that helper functions exist
    assert callable(main.player_hit)
    assert callable(main.toggle_fullscreen)
    assert callable(main.debug_music_status)
