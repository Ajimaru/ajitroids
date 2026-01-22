"""Tests for replay recording, playback and replay UI."""

import pytest
import pygame
import os
import json
import tempfile
from unittest.mock import MagicMock, patch
from modul.replay_system import ReplayRecorder, ReplayPlayer, ReplayManager, GameFrame, GameEvent
from modul.replay_ui import ReplayListMenu, ReplayViewer


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
def temp_replay_dir(tmp_path, monkeypatch):
    """Create a temporary replay directory."""
    replay_dir = tmp_path / "replays"
    replay_dir.mkdir()
    monkeypatch.setattr('modul.replay_system.ReplayManager.replays_dir', str(replay_dir))
    return str(replay_dir)


def test_replay_recorder_initialization():
    """Test that replay recorder initializes correctly."""
    recorder = ReplayRecorder()
    assert recorder.recording is False
    assert len(recorder.frames) == 0
    assert len(recorder.events) == 0


def test_replay_recorder_start_recording():
    """Test starting a recording session."""
    recorder = ReplayRecorder()
    recorder.start_recording("normal", "default")

    assert recorder.recording is True
    assert recorder.metadata['difficulty'] == "normal"
    assert recorder.metadata['ship_type'] == "default"
    assert 'start_time' in recorder.metadata


def test_replay_recorder_stop_recording():
    """Test stopping a recording session."""
    recorder = ReplayRecorder()
    recorder.start_recording("normal", "default")
    recorder.stop_recording(1000, 5)

    assert recorder.recording is False
    assert recorder.metadata['final_score'] == 1000
    assert recorder.metadata['final_level'] == 5


def test_replay_recorder_record_frame():
    """Test recording game frames."""
    recorder = ReplayRecorder()
    recorder.start_recording("normal", "default")

    game_state = {
        'player_x': 100.0,
        'player_y': 200.0,
        'player_rotation': 45.0,
        'player_vx': 10.0,
        'player_vy': 20.0,
        'score': 500,
        'lives': 3,
        'level': 2,
    }

    recorder.record_frame(game_state, 1.0)

    # Should have recorded a frame
    assert len(recorder.frames) > 0


def test_replay_recorder_record_event():
    """Test recording game events."""
    recorder = ReplayRecorder()
    recorder.start_recording("normal", "default")

    recorder.record_event("asteroid_destroyed", {"score": 100}, 1.0)

    assert len(recorder.events) == 1
    assert recorder.events[0].event_type == "asteroid_destroyed"


def test_replay_recorder_frame_interval():
    """Test that frames are recorded at specified intervals."""
    import time as time_module

    recorder = ReplayRecorder()
    recorder.frame_interval = 0.5  # Only record every 0.5 seconds

    # Manually set start time for predictable testing
    start = time_module.time()
    recorder.start_recording("normal", "default")
    recorder.start_time = start  # Override to known value

    game_state = {
        'player_x': 100.0,
        'player_y': 200.0,
        'player_rotation': 45.0,
        'player_vx': 10.0,
        'player_vy': 20.0,
        'score': 500,
        'lives': 3,
        'level': 2,
    }

    # Record first frame at start + 0.1
    recorder.record_frame(game_state, start + 0.1)
    assert len(recorder.frames) == 1

    # Try to record frames quickly (should be ignored due to interval)
    recorder.record_frame(game_state, start + 0.2)
    recorder.record_frame(game_state, start + 0.3)
    assert len(recorder.frames) == 1  # Should still be 1

    # Record after interval has passed (0.6 seconds from start)
    recorder.record_frame(game_state, start + 0.7)
    assert len(recorder.frames) == 2  # Now should be 2


def test_replay_player_initialization():
    """Test that replay player initializes correctly."""
    player = ReplayPlayer()
    assert player.playing is False
    assert player.paused is False
    assert len(player.frames) == 0


def test_replay_player_start_playback():
    """Test starting playback."""
    player = ReplayPlayer()
    player.frames = [
        GameFrame(0.0, (100, 100), 0, (0, 0), 0, 3, 1),
        GameFrame(0.1, (110, 110), 0, (0, 0), 0, 3, 1),
    ]

    player.start_playback()
    assert player.playing is True
    assert player.paused is False
    assert player.current_frame_index == 0


def test_replay_player_stop_playback():
    """Test stopping playback."""
    player = ReplayPlayer()
    player.playing = True
    player.stop_playback()

    assert player.playing is False
    assert player.current_frame_index == 0


def test_replay_player_toggle_pause():
    """Test pausing and resuming playback."""
    player = ReplayPlayer()
    player.playing = True
    player.paused = False
    # Add frames so toggle_pause doesn't return early
    player.frames = [
        GameFrame(0.0, (100, 100), 0, (0, 0), 0, 3, 1),
        GameFrame(0.1, (110, 110), 0, (0, 0), 0, 3, 1),
    ]

    player.toggle_pause()
    assert player.paused is True

    player.toggle_pause()
    assert player.paused is False


def test_replay_player_toggle_pause_empty_frames():
    """Test that toggle_pause safely handles empty frames list."""
    player = ReplayPlayer()
    player.playing = True
    player.paused = False
    player.frames = []  # Empty frames

    # Should not crash and should not change pause state
    player.toggle_pause()
    assert player.paused is False


def test_replay_player_toggle_pause_not_playing():
    """Test that toggle_pause does nothing when not playing."""
    player = ReplayPlayer()
    player.playing = False
    player.paused = False
    player.frames = [GameFrame(0.0, (100, 100), 0, (0, 0), 0, 3, 1)]

    # Should not change pause state
    player.toggle_pause()
    assert player.paused is False


def test_replay_player_set_speed():
    """Test setting playback speed."""
    player = ReplayPlayer()
    player.set_speed(2.0)
    assert player.playback_speed == 2.0

    player.set_speed(0.5)
    assert player.playback_speed == 0.5


def test_replay_player_get_progress_percentage():
    """Test getting playback progress."""
    player = ReplayPlayer()
    player.metadata = {'duration': 100.0}
    player.frames = [
        GameFrame(0.0, (100, 100), 0, (0, 0), 0, 3, 1),
        GameFrame(50.0, (110, 110), 0, (0, 0), 0, 3, 1),
    ]
    player.current_frame_index = 1

    # Should be around 50% progress
    progress = player.get_progress_percentage()
    assert 0 <= progress <= 100


def test_replay_manager_initialization():
    """Test replay manager initialization."""
    manager = ReplayManager()
    assert manager.replays_dir == "replays"


def test_replay_manager_list_replays_empty(tmp_path):
    """Test listing replays when directory is empty."""
    replay_dir = tmp_path / "replays"
    replay_dir.mkdir()

    manager = ReplayManager()
    manager.replays_dir = str(replay_dir)
    replays = manager.list_replays()
    assert len(replays) == 0


def test_replay_manager_get_replay_count(tmp_path):
    """Test getting replay count."""
    replay_dir = tmp_path / "replays"
    replay_dir.mkdir()

    manager = ReplayManager()
    manager.replays_dir = str(replay_dir)
    count = manager.get_replay_count()
    assert count == 0


def test_replay_list_menu_initialization():
    """Test replay list menu initialization."""
    manager = ReplayManager()
    menu = ReplayListMenu(manager)

    assert menu.replay_manager == manager
    assert menu.selected_index == 0


def test_replay_list_menu_activate():
    """Test activating replay list menu."""
    manager = ReplayManager()
    menu = ReplayListMenu(manager)
    menu.activate()

    assert menu.fade_in is True
    assert menu.background_alpha == 0


def test_replay_list_menu_escape_key():
    """Test ESC key returns back action."""
    manager = ReplayManager()
    menu = ReplayListMenu(manager)

    events = [MagicMock(type=pygame.KEYDOWN, key=pygame.K_ESCAPE)]
    result = menu.update(0.016, events)

    assert result is not None
    assert result.get("action") == "back"


def test_replay_list_menu_draw_empty():
    """Test drawing menu with no replays."""
    screen = pygame.display.set_mode((1280, 720))
    manager = ReplayManager()
    menu = ReplayListMenu(manager)
    menu.background_alpha = 180

    # Should not raise an error
    menu.draw(screen)
    assert True


def test_replay_viewer_initialization():
    """Test replay viewer initialization."""
    player = ReplayPlayer()
    viewer = ReplayViewer(player)

    assert viewer.replay_player == player


def test_replay_viewer_escape_key():
    """Test ESC key stops playback."""
    player = ReplayPlayer()
    viewer = ReplayViewer(player)
    player.playing = True

    events = [MagicMock(type=pygame.KEYDOWN, key=pygame.K_ESCAPE)]
    action = viewer.update(0.016, events)

    assert action == "back"
    assert player.playing is False


def test_replay_viewer_space_key():
    """Test SPACE key toggles pause."""
    player = ReplayPlayer()
    viewer = ReplayViewer(player)
    player.playing = True
    player.paused = False
    # Add frames so toggle_pause doesn't return early
    player.frames = [
        GameFrame(0.0, (100, 100), 0, (0, 0), 0, 3, 1),
        GameFrame(0.1, (110, 110), 0, (0, 0), 0, 3, 1),
    ]

    events = [MagicMock(type=pygame.KEYDOWN, key=pygame.K_SPACE)]
    viewer.update(0.016, events)

    # Pause state should be toggled
    assert player.paused is True


def test_replay_viewer_speed_keys():
    """Test speed control keys."""
    player = ReplayPlayer()
    viewer = ReplayViewer(player)
    player.playing = True

    # Test 0.5x speed
    events = [MagicMock(type=pygame.KEYDOWN, key=pygame.K_1)]
    viewer.update(0.016, events)
    assert player.playback_speed == 0.5

    # Test 1x speed
    events = [MagicMock(type=pygame.KEYDOWN, key=pygame.K_2)]
    viewer.update(0.016, events)
    assert player.playback_speed == 1.0

    # Test 2x speed
    events = [MagicMock(type=pygame.KEYDOWN, key=pygame.K_3)]
    viewer.update(0.016, events)
    assert player.playback_speed == 2.0


def test_replay_viewer_draw_hud():
    """Test drawing replay viewer HUD."""
    screen = pygame.display.set_mode((1280, 720))
    player = ReplayPlayer()
    viewer = ReplayViewer(player)
    player.metadata = {'duration': 100.0}

    # Should not raise an error
    viewer.draw_hud(screen)
    assert True


def test_game_frame_creation():
    """Test creating a game frame."""
    frame = GameFrame(
        timestamp=1.0,
        player_pos=(100, 200),
        player_rotation=45.0,
        player_velocity=(10, 20),
        score=500,
        lives=3,
        level=2
    )

    assert frame.timestamp == 1.0
    assert frame.player_pos == (100, 200)
    assert frame.score == 500


def test_game_event_creation():
    """Test creating a game event."""
    event = GameEvent(
        timestamp=1.0,
        event_type="asteroid_destroyed",
        data={"score": 100}
    )

    assert event.timestamp == 1.0
    assert event.event_type == "asteroid_destroyed"
    assert event.data["score"] == 100


def test_replay_manager_corrupted_json(tmp_path):
    """Test that corrupted JSON files are logged and skipped."""
    replay_dir = tmp_path / "replays"
    replay_dir.mkdir()

    # Create a corrupted JSON file
    corrupted_file = replay_dir / "corrupted.json"
    corrupted_file.write_text("{ invalid json }")

    manager = ReplayManager()
    manager.replays_dir = str(replay_dir)

    # Should not crash, should skip corrupted file
    with patch('modul.replay_system.logger') as mock_logger:
        replays = manager.list_replays()
        assert len(replays) == 0
        # Verify warning was logged
        mock_logger.warning.assert_called_once()
        assert "corrupted" in str(mock_logger.warning.call_args).lower()


def test_replay_manager_missing_metadata(tmp_path):
    """Test that files with missing metadata are handled gracefully."""
    replay_dir = tmp_path / "replays"
    replay_dir.mkdir()

    # Create a file without metadata
    invalid_file = replay_dir / "invalid.json"
    invalid_file.write_text('{"frames": [], "events": []}')

    manager = ReplayManager()
    manager.replays_dir = str(replay_dir)

    # Should handle missing metadata gracefully
    replays = manager.list_replays()
    assert len(replays) == 1
    assert replays[0]['metadata'] == {}


def test_replay_manager_validate_filepath(tmp_path):
    """Test filepath validation prevents directory traversal."""
    replay_dir = tmp_path / "replays"
    replay_dir.mkdir()

    manager = ReplayManager()
    manager.replays_dir = str(replay_dir)

    # Valid path
    valid_path = str(replay_dir / "valid.json")
    assert manager._validate_filepath(valid_path) is True

    # Invalid path (parent directory)
    invalid_path = str(tmp_path / "outside.json")
    assert manager._validate_filepath(invalid_path) is False

    # Invalid path (directory traversal attempt)
    traversal_path = str(replay_dir / ".." / "outside.json")
    assert manager._validate_filepath(traversal_path) is False


def test_replay_manager_delete_with_validation(tmp_path):
    """Test that delete only works on valid paths."""
    replay_dir = tmp_path / "replays"
    replay_dir.mkdir()

    # Create a file to delete
    valid_file = replay_dir / "valid.json"
    valid_file.write_text('{"test": "data"}')

    manager = ReplayManager()
    manager.replays_dir = str(replay_dir)

    # Try to delete file outside replays dir (should be rejected)
    outside_file = tmp_path / "outside.json"
    outside_file.write_text('{"test": "data"}')

    with patch('modul.replay_system.logger') as mock_logger:
        manager.delete_replay(str(outside_file))
        # File should still exist
        assert outside_file.exists()
        # Warning should be logged
        mock_logger.warning.assert_called_once()

    # Delete valid file (should work)
    manager.delete_replay(str(valid_file))
    assert not valid_file.exists()


def test_replay_player_load_invalid_file():
    """Test that loading invalid replay files raises appropriate errors."""
    player = ReplayPlayer()

    # Test with non-existent file
    with pytest.raises(FileNotFoundError):
        player.load_replay("/nonexistent/file.json")


def test_replay_player_load_corrupted_json(tmp_path):
    """Test that loading corrupted JSON raises JSONDecodeError."""
    corrupted_file = tmp_path / "corrupted.json"
    corrupted_file.write_text("{ invalid json }")

    player = ReplayPlayer()

    with patch('modul.replay_system.logger'):
        with pytest.raises(json.JSONDecodeError):
            player.load_replay(str(corrupted_file))


def test_replay_recorder_save_with_error_handling(tmp_path):
    """Test that save_replay handles errors appropriately."""
    recorder = ReplayRecorder()
    recorder.start_recording("normal", "default")

    # Create an invalid directory path
    invalid_dir = tmp_path / "readonly"
    invalid_dir.mkdir()

    # Make directory read-only on Unix systems
    try:
        os.chmod(invalid_dir, 0o444)

        with patch('modul.replay_system.os.makedirs', side_effect=OSError("Permission denied")):
            with patch('modul.replay_system.logger'):
                with pytest.raises(OSError):
                    recorder.save_replay()
    finally:
        # Restore permissions for cleanup
        try:
            os.chmod(invalid_dir, 0o755)
        except:
            pass
