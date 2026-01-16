"""Replay system for recording and playing back game sessions."""
import json
import os
import time
import logging
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


@dataclass
class GameFrame:
    """Single frame of game state."""
    timestamp: float
    player_pos: tuple  # (x, y)
    player_rotation: float
    player_velocity: tuple  # (x, y)
    score: int
    lives: int
    level: int
    asteroids: List[Dict[str, Any]] = field(default_factory=list)
    shots: List[Dict[str, Any]] = field(default_factory=list)
    powerups: List[Dict[str, Any]] = field(default_factory=list)
    enemies: List[Dict[str, Any]] = field(default_factory=list)
    particles: List[Dict[str, Any]] = field(default_factory=list)
    

@dataclass
class GameEvent:
    """Records a significant game event."""
    timestamp: float
    event_type: str  # 'asteroid_destroyed', 'powerup_collected', 'level_up', 'boss_spawn', etc.
    data: Dict[str, Any] = field(default_factory=dict)


class ReplayRecorder:
    """Records game sessions for later playback."""
    
    def __init__(self):
        self.recording = False
        self.frames: List[GameFrame] = []
        self.events: List[GameEvent] = []
        self.start_time = 0
        self.metadata = {}
        self.frame_interval = 0.1  # Record every 100ms
        self.last_frame_time = 0
        
    def start_recording(self, difficulty: str, ship_type: str):
        """Start recording a new game session."""
        self.recording = True
        self.frames = []
        self.events = []
        self.start_time = time.time()
        self.last_frame_time = 0
        self.metadata = {
            'version': '1.0',
            'difficulty': difficulty,
            'ship_type': ship_type,
            'start_time': self.start_time,
        }
        
    def stop_recording(self, final_score: int, final_level: int):
        """Stop recording and finalize metadata."""
        self.recording = False
        end_time = time.time()
        start_time = self.start_time or end_time
        self.metadata.update({
            'end_time': end_time,
            'duration': max(0.0, end_time - start_time),
            'final_score': final_score,
            'final_level': final_level,
            'frame_count': len(self.frames),
            'event_count': len(self.events),
        })
        
    def record_frame(self, game_state: Dict[str, Any], current_time: float):
        """Record a single frame of game state."""
        if not self.recording:
            return

        # Calculate relative timestamp
        relative_time = max(0, current_time - self.start_time)

        # Only record frames at specified interval
        if self.last_frame_time > 0 and relative_time - self.last_frame_time < self.frame_interval:
            return

        required = (
            'player_x', 'player_y', 'player_rotation', 'player_vx', 'player_vy',
            'score', 'lives', 'level'
        )
        if any(k not in game_state for k in required):
            logger.debug("Skipping replay frame due to missing required fields")
            return

        self.last_frame_time = relative_time

        frame = GameFrame(
            timestamp=relative_time,
            player_pos=(game_state['player_x'], game_state['player_y']),
            player_rotation=game_state['player_rotation'],
            player_velocity=(game_state['player_vx'], game_state['player_vy']),
            score=game_state['score'],
            lives=game_state['lives'],
            level=game_state['level'],
            asteroids=game_state.get('asteroids', []),
            shots=game_state.get('shots', []),
            powerups=game_state.get('powerups', []),
            enemies=game_state.get('enemies', []),
            particles=game_state.get('particles', []),
        )
        self.frames.append(frame)
        
    def record_event(self, event_type: str, data: Dict[str, Any], current_time: float):
        """Record a significant game event."""
        if not self.recording:
            return
        
        # Calculate relative timestamp
        relative_time = max(0, current_time - self.start_time)
            
        event = GameEvent(
            timestamp=relative_time,
            event_type=event_type,
            data=data
        )
        self.events.append(event)
        
    def save_replay(self, filename: str = None) -> str:
        """Save the replay to a file."""
        try:
            if filename is None:
                # Generate filename from timestamp (millisecond resolution)
                filename = f"replay_{int(self.start_time * 1000)}.json"

            # Ensure replays directory exists
            os.makedirs("replays", exist_ok=True)
            filepath = os.path.join("replays", filename)

            # Ensure we never overwrite an existing replay
            if os.path.exists(filepath):
                base, ext = os.path.splitext(filename)
                i = 1
                while True:
                    candidate = os.path.join("replays", f"{base}_{i}{ext}")
                    if not os.path.exists(candidate):
                        filepath = candidate
                        break
                    i += 1

            replay_data = {
                'metadata': self.metadata,
                'frames': [asdict(frame) for frame in self.frames],
                'events': [asdict(event) for event in self.events],
            }

            with open(filepath, 'w') as f:
                json.dump(replay_data, f, indent=2)
                
            logger.info(f"Successfully saved replay to: {filepath}")
            return filepath
        except OSError as e:
            logger.error(f"Failed to create replays directory or save file: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error saving replay: {e}")
            raise


class ReplayPlayer:
    """Plays back recorded game sessions."""
    
    def __init__(self):
        self.playing = False
        self.paused = False
        self.frames: List[GameFrame] = []
        self.events: List[GameEvent] = []
        self.metadata = {}
        self.current_frame_index = 0
        self.playback_speed = 1.0
        self.start_playback_time = 0
        
    def load_replay(self, filepath: str):
        """Load a replay from file."""
        try:
            # Reset any prior playback state
            self.stop_playback()

            with open(filepath, 'r') as f:
                replay_data = json.load(f)

            self.metadata = replay_data['metadata']
            self.frames = [GameFrame(**frame_data) for frame_data in replay_data['frames']]
            self.events = [GameEvent(**event_data) for event_data in replay_data['events']]

            # Ensure chronological order
            self.frames.sort(key=lambda fr: fr.timestamp)
            self.events.sort(key=lambda ev: ev.timestamp)

            self.current_frame_index = 0
            logger.info(f"Successfully loaded replay: {filepath}")
        except FileNotFoundError:
            logger.error(f"Replay file not found: {filepath}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in replay file '{filepath}': {e}")
            raise
        except KeyError as e:
            logger.error(f"Missing required field in replay file '{filepath}': {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load replay '{filepath}': {e}")
            raise
        
    def start_playback(self):
        """Start playing the replay."""
        if not self.frames:
            self.stop_playback()
            return
        self.playing = True
        self.paused = False
        self.current_frame_index = 0
        self.start_playback_time = time.time()
        
    def stop_playback(self):
        """Stop playing the replay."""
        self.playing = False
        self.paused = False
        self.current_frame_index = 0
        
    def toggle_pause(self):
        """Toggle pause state."""
        if not self.playing or not self.frames:
            return

        if not self.paused:
            # Pausing: capture a robust timestamp (frame timestamp if available)
            if 0 <= self.current_frame_index < len(self.frames):
                self._paused_timestamp = self.frames[self.current_frame_index].timestamp
            else:
                self._paused_timestamp = 0.0
            self.paused = True
            return

        # Resuming: continue from the captured timestamp
        resume_ts = getattr(self, "_paused_timestamp", 0.0)
        self.paused = False
        safe_speed = self.playback_speed if self.playback_speed not in (0, 0.0) else 1.0
        self.start_playback_time = time.time() - (resume_ts / safe_speed)
        if hasattr(self, "_paused_timestamp"):
            delattr(self, "_paused_timestamp")
                
    def set_speed(self, speed: float):
        """Set playback speed (0.5x, 1x, 2x, etc.)."""
        if self.playing and not self.paused:
            # Adjust start time for new speed
            elapsed = (time.time() - self.start_playback_time) * self.playback_speed
            self.playback_speed = speed
            self.start_playback_time = time.time() - (elapsed / self.playback_speed)
        else:
            self.playback_speed = speed
            
    def get_current_timestamp(self) -> float:
        """Get current playback timestamp."""
        if self.paused:
            if not self.frames or not (0 <= self.current_frame_index < len(self.frames)):
                return 0.0
            return self.frames[self.current_frame_index].timestamp
        return (time.time() - self.start_playback_time) * self.playback_speed
        
    def get_current_frame(self) -> GameFrame:
        """Get the current frame based on playback time."""
        if not self.playing or not self.frames:
            return None
            
        current_time = self.get_current_timestamp()
        
        # Find the appropriate frame for current timestamp
        while (self.current_frame_index < len(self.frames) - 1 and 
               self.frames[self.current_frame_index + 1].timestamp <= current_time):
            self.current_frame_index += 1
            
        if self.current_frame_index >= len(self.frames):
            self.stop_playback()
            return None
            
        return self.frames[self.current_frame_index]
        
    def seek_to_time(self, timestamp: float):
        """Seek to a specific time in the replay."""
        if not self.frames:
            self.current_frame_index = 0
            self.start_playback_time = time.time()
            return

        timestamp = max(0, min(timestamp, self.metadata.get('duration', 0)))

        # Find closest frame (or clamp to last frame)
        self.current_frame_index = len(self.frames) - 1
        for i, frame in enumerate(self.frames):
            if frame.timestamp >= timestamp:
                self.current_frame_index = i
                break

        # Adjust playback time
        self.start_playback_time = time.time() - (timestamp / self.playback_speed)
        
    def skip_forward(self, seconds: float = 5.0):
        """Skip forward by specified seconds."""
        current_time = self.get_current_timestamp()
        self.seek_to_time(current_time + seconds)
        
    def skip_backward(self, seconds: float = 5.0):
        """Skip backward by specified seconds."""
        current_time = self.get_current_timestamp()
        self.seek_to_time(current_time - seconds)
        
    def get_progress_percentage(self) -> float:
        """Get playback progress as percentage (0-100)."""
        if not self.frames:
            return 0.0
        duration = self.metadata.get('duration', 1.0)
        current = self.get_current_timestamp()
        return min(100.0, (current / duration) * 100.0)


class ReplayManager:
    """Manages replay files and provides listing/deletion capabilities."""
    
    def __init__(self):
        self.replays_dir = "replays"
        
    def _validate_filepath(self, filepath: str) -> bool:
        """Validate that filepath is within the replays directory."""
        try:
            replays_abs = os.path.realpath(self.replays_dir)
            file_abs = os.path.realpath(filepath)
            return os.path.commonpath([replays_abs, file_abs]) == replays_abs
        except Exception as e:
            logger.error(f"Error validating filepath '{filepath}': {e}")
            return False
        
    def list_replays(self) -> List[Dict[str, Any]]:
        """List all available replay files."""
        if not os.path.exists(self.replays_dir):
            return []
            
        replays = []
        for filename in os.listdir(self.replays_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.replays_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        replays.append({
                            'filename': filename,
                            'filepath': filepath,
                            'metadata': data.get('metadata', {}),
                        })
                except json.JSONDecodeError as e:
                    logger.warning(f"Skipping corrupted replay file '{filename}': Invalid JSON - {e}")
                except KeyError as e:
                    logger.warning(f"Skipping replay file '{filename}': Missing required field - {e}")
                except Exception as e:
                    logger.error(f"Unexpected error reading replay file '{filename}': {e}")
                    
        # Sort by timestamp (newest first)
        replays.sort(key=lambda x: x['metadata'].get('start_time', 0), reverse=True)
        return replays
        
    def delete_replay(self, filepath: str):
        """Delete a replay file."""
        if not self._validate_filepath(filepath):
            logger.warning(f"Attempted to delete file outside replays directory: {filepath}")
            return
            
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                logger.info(f"Deleted replay file: {filepath}")
            except Exception as e:
                logger.error(f"Failed to delete replay file '{filepath}': {e}")
            
    def get_replay_count(self) -> int:
        """Get the number of replay files."""
        return len(self.list_replays())
