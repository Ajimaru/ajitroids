"""Tests for replay system functionality."""
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
    recorder = ReplayRecorder()
    recorder.frame_interval = 1.0  # Only record every second
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
    
    # Record multiple frames quickly
    recorder.record_frame(game_state, 0.5)
    recorder.record_frame(game_state, 0.6)
    recorder.record_frame(game_state, 0.7)
    
    # Should have recorded only 1 frame due to interval
    assert len(recorder.frames) <= 1


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
    
    player.toggle_pause()
    assert player.paused is True
    
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
