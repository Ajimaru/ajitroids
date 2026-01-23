"""Replay system for recording and playing back game sessions."""
import gzip
import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, TextIO, cast

logger = logging.getLogger(__name__)


MIN_REPLAY_FPS = 30
DEFAULT_FRAME_INTERVAL = 1.0 / MIN_REPLAY_FPS
QUANTIZE_DIGITS = 3


def _quantize(value, ndigits: int = QUANTIZE_DIGITS):
    """Recursively round floats and leave other types unchanged."""
    if isinstance(value, float):
        return round(value, ndigits)
    if isinstance(value, (list, tuple)):
        return type(value)(_quantize(v, ndigits) for v in value)
    if isinstance(value, dict):
        return {k: _quantize(v, ndigits) for k, v in value.items()}
    return value


def _open_replay(path: str, mode: str = "rt", encoding: str = "utf-8"):
    """Open replay file with gzip support based on extension.

    When opening text-mode replay files, pass an explicit `encoding` to avoid
    platform-dependent defaults.
    """
    if path.endswith(".gz"):
        return gzip.open(path, mode, encoding=encoding)
    return open(path, mode, encoding=encoding)


def _quantize_float(value: float) -> float:
    """Round float inputs to a fixed precision."""
    return round(float(value), QUANTIZE_DIGITS)


def _quantize_dict_list(values: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Quantize nested dict structures while preserving list typing."""
    return [cast(Dict[str, Any], _quantize(value)) for value in values]


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
    event_type: str
    data: Dict[str, Any] = field(default_factory=dict)


class ReplayRecorder:
    """Records game sessions for later playback."""

    def __init__(self):
        """
        Create a ReplayRecorder and initialize its internal recording state and defaults.
        
        Initializes:
        - recording: whether recording is active (False).
        - frames: list to store recorded GameFrame objects.
        - events: list to store recorded GameEvent objects.
        - start_time: reference start timestamp for the recording (0).
        - metadata: dictionary for replay metadata (version, difficulty, etc.).
        - frame_interval: minimum time between recorded frames (DEFAULT_FRAME_INTERVAL).
        - last_frame_time: timestamp of the most recently recorded frame (0).
        """
        self.recording = False
        self.frames: List[GameFrame] = []
        self.events: List[GameEvent] = []
        self.start_time = 0
        self.metadata = {}
        self.frame_interval = DEFAULT_FRAME_INTERVAL
        self.last_frame_time = 0

    def start_recording(self, difficulty: str, ship_type: str):
        """Start recording a new game session."""
        self.recording = True
        self.frames = []
        self.events = []
        self.start_time = time.time()
        self.last_frame_time = 0
        self.metadata = {
            'version': '1.1',
            'difficulty': difficulty,
            'ship_type': ship_type,
            'start_time': self.start_time,
            'frame_rate_hz': round(1.0 / self.frame_interval, 2),
            'format': 'json',
            'compression': 'gzip',
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
        if (self.last_frame_time > 0 and
                relative_time - self.last_frame_time < self.frame_interval):
            return

        required = (
            'player_x', 'player_y', 'player_rotation',
            'player_vx', 'player_vy', 'score', 'lives', 'level'
        )
        if any(k not in game_state for k in required):
            logger.debug("Skipping frame; missing required fields")
            return

        self.last_frame_time = relative_time

        px = _quantize(game_state['player_x'])
        py = _quantize(game_state['player_y'])
        vx = _quantize(game_state['player_vx'])
        vy = _quantize(game_state['player_vy'])

        frame = GameFrame(
            timestamp=_quantize_float(relative_time),
            player_pos=(px, py),
            player_rotation=_quantize_float(game_state['player_rotation']),
            player_velocity=(vx, vy),
            score=game_state['score'],
            lives=game_state['lives'],
            level=game_state['level'],
            asteroids=_quantize_dict_list(
                cast(List[Dict[str, Any]], game_state.get('asteroids', []))
            ),
            shots=_quantize_dict_list(
                cast(List[Dict[str, Any]], game_state.get('shots', []))
            ),
            powerups=_quantize_dict_list(
                cast(List[Dict[str, Any]], game_state.get('powerups', []))
            ),
            enemies=_quantize_dict_list(
                cast(List[Dict[str, Any]], game_state.get('enemies', []))
            ),
            particles=_quantize_dict_list(
                cast(List[Dict[str, Any]], game_state.get('particles', []))
            ),
        )
        self.frames.append(frame)

    def record_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        current_time: float,
    ):
        """Record a significant game event."""
        if not self.recording:
            return

        # Calculate relative timestamp
        relative_time = _quantize_float(max(0, current_time - self.start_time))

        event = GameEvent(
            timestamp=relative_time,
            event_type=event_type,
            data=data
        )
        self.events.append(event)

    def save_replay(self, filename: Optional[str] = None) -> str:
        """
        Save the recorded replay to a file in the "replays" directory.
        
        If `filename` is omitted, a timestamped filename `replay_<start_time_ms>.json.gz` is used.
        The function ensures the replays directory exists, appends `.json.gz` when needed, avoids overwriting
        by adding a numeric suffix if a file already exists, and writes replay metadata, frames, and events as JSON
        (uses gzip when the filename ends with `.gz`).
        
        Parameters:
            filename (Optional[str]): Desired filename or path relative to the "replays" directory. May end with
                `.json` or `.json.gz`. If omitted, a generated timestamped `.json.gz` name is used.
        
        Returns:
            str: The full filepath where the replay was saved.
        
        Raises:
            OSError: If a filesystem error occurs while creating directories or writing the file.
            Exception: Propagates other unexpected errors encountered during serialization or file I/O.
        """
        try:
            if filename is None:
                filename = f"replay_{int(self.start_time * 1000)}.json.gz"
            elif not filename.endswith(('.json', '.json.gz')):
                filename = f"{filename}.json.gz"

            # Ensure replays directory exists
            os.makedirs("replays", exist_ok=True)
            filepath = os.path.join("replays", filename)

            # Ensure we never overwrite an existing replay
            if os.path.exists(filepath):
                base, ext = os.path.splitext(filename)
                # Handle double extensions like .json.gz
                if ext == '.gz' and base.endswith('.json'):
                    base, _ = os.path.splitext(base)
                    ext = '.json.gz'
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

            def _json_default(obj):
                """
                Serialize non-JSON objects into JSON-friendly representations.
                
                If the object has `x` and `y` attributes that can be converted to floats, return a dictionary with those values as floats. Otherwise return the object's string representation.
                
                Returns:
                    dict: `{"x": float, "y": float}` when `x` and `y` are present and convertible to float, otherwise a `str` representation of `obj`.
                """
                if hasattr(obj, "x") and hasattr(obj, "y"):
                    try:
                        return {"x": float(obj.x), "y": float(obj.y)}
                    except (TypeError, ValueError, AttributeError):
                        pass
                return str(obj)

            with cast(TextIO, _open_replay(filepath, 'wt')) as f:
                json.dump(
                    replay_data,
                    f,
                    indent=None,
                    separators=(",", ":"),
                    default=_json_default,
                )

            logger.info("Successfully saved replay to: %s", filepath)
            return filepath
        except OSError as e:
            logger.exception("Failed to save replay: %s", e)
            raise
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.exception("Unexpected error saving replay: %s", e)
            raise


class ReplayPlayer:
    """Plays back recorded game sessions."""

    def __init__(self):
        """
        Create a ReplayPlayer with default playback state.
        
        Initializes these attributes:
            playing: bool — whether playback is active.
            paused: bool — whether playback is paused.
            frames: List[GameFrame] — loaded frames for playback (initially empty).
            events: List[GameEvent] — loaded events for playback (initially empty).
            metadata: dict — replay metadata.
            current_frame_index: int — index of the current frame.
            playback_speed: float — playback speed multiplier.
            start_playback_time: float — reference start time for playback timing.
            _paused_timestamp: Optional[float] — timestamp captured when paused, or None.
        """
        self.playing = False
        self.paused = False
        self.frames: List[GameFrame] = []
        self.events: List[GameEvent] = []
        self.metadata = {}
        self.current_frame_index = 0
        self.playback_speed = 1.0
        self.start_playback_time = 0
        # Track paused timestamp when toggling pause; initialize here to
        # avoid attributes created outside __init__ (W0201).
        self._paused_timestamp: Optional[float] = None

    def load_replay(self, filepath: str):
        """
        Load a replay file into the player, replacing any current playback state.
        
        Parameters:
            filepath (str): Path to a replay file (.json or .json.gz).
        
        Raises:
            FileNotFoundError: If the file does not exist.
            json.JSONDecodeError: If the file is not valid JSON.
            KeyError: If required top-level fields ('metadata', 'frames', 'events') are missing.
            Exception: For other I/O or parsing errors encountered while loading.
        """
        try:
            self.stop_playback()

            with _open_replay(filepath, 'rt') as f:
                replay_data = json.load(f)

            self.metadata = replay_data['metadata']
            self.frames = [
                GameFrame(**frame_data)
                for frame_data in replay_data['frames']
            ]
            self.events = [
                GameEvent(**event_data)
                for event_data in replay_data['events']
            ]

            # Ensure chronological order
            self.frames.sort(key=lambda fr: fr.timestamp)
            self.events.sort(key=lambda ev: ev.timestamp)

            self.current_frame_index = 0
            logger.info("Successfully loaded replay: %s", filepath)
        except FileNotFoundError:
            logger.exception("Replay file not found: %s", filepath)
            raise
        except json.JSONDecodeError as e:
            logger.exception("Invalid JSON in replay '%s': %s", filepath, e)
            raise
        except KeyError as e:
            logger.exception("Missing field in replay '%s': %s", filepath, e)
            raise
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.exception("Failed to load replay '%s': %s", filepath, e)
            raise

    def start_playback(self):
        """
        Begin playback from the start of the loaded frames.
        
        If there are no frames, stops playback and returns. Otherwise sets the player to playing, clears the paused state, resets the current frame index to 0, and records the playback start time.
        """
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
        """
        Toggle the player's paused state.
        
        If playback is not active or there are no frames, this is a no-op. When pausing, captures the timestamp of the current frame (or 0.0 if unavailable) so playback can resume from the same point. When resuming, adjusts internal playback timing so playback continues from the captured timestamp at the current speed (treating a speed of 0 as 1.0) and clears the stored paused timestamp.
        """
        if not self.playing or not self.frames:
            return

        if not self.paused:
            # Pausing: capture a frame timestamp if available
            if 0 <= self.current_frame_index < len(self.frames):
                self._paused_timestamp = (
                    self.frames[self.current_frame_index].timestamp
                )
            else:
                self._paused_timestamp = 0.0
            self.paused = True
            return

        # Resuming: continue from the captured timestamp
        resume_ts = self._paused_timestamp if self._paused_timestamp is not None else 0.0
        self.paused = False
        safe_speed = (
            self.playback_speed if self.playback_speed not in (0, 0.0) else 1.0
        )
        self.start_playback_time = time.time() - (resume_ts / safe_speed)
        self._paused_timestamp = None

    def set_speed(self, speed: float):
        """
        Set the playback speed and adjust internal timing so the current playback position remains unchanged.
        
        When playback is active and not paused, updates the internal start time to preserve the current playback timestamp after changing the speed. Otherwise, only updates the stored speed.
        
        Parameters:
            speed (float): New playback speed multiplier (e.g., 0.5 for half-speed, 2.0 for double speed).
        """
        if self.playing and not self.paused:
            # Adjust start time for new speed
            elapsed = (
                (time.time() - self.start_playback_time) * self.playback_speed
            )
            self.playback_speed = speed
            self.start_playback_time = time.time() - (
                elapsed / self.playback_speed
            )
        else:
            self.playback_speed = speed

    def get_current_timestamp(self) -> float:
        """Get current playback timestamp."""
        if self.paused:
            if not self.frames or not (
                0 <= self.current_frame_index < len(self.frames)
            ):
                return 0.0
            return self.frames[self.current_frame_index].timestamp
        return (time.time() - self.start_playback_time) * self.playback_speed

    def get_current_frame(self) -> Optional[GameFrame]:
        """Get the current frame based on playback time."""
        if not self.playing or not self.frames:
            return None

        current_time = self.get_current_timestamp()

        # Find the appropriate frame for current timestamp
        while (
            self.current_frame_index < len(self.frames) - 1 and
            self.frames[self.current_frame_index + 1].timestamp <= current_time
        ):
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
        self.start_playback_time = time.time() - (
            timestamp / self.playback_speed
        )

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
        """Initialize the replay manager."""
        self.replays_dir = "replays"

    def _validate_filepath(self, filepath: str) -> bool:
        """
        Determine whether the given filepath is located inside the replay directory.
        
        Parameters:
            filepath (str): Path to validate; may be absolute or relative.
        
        Returns:
            bool: True if the resolved filepath is inside self.replays_dir, False otherwise (returns False on error).
        """
        try:
            replays_abs = os.path.realpath(self.replays_dir)
            file_abs = os.path.realpath(filepath)
            return os.path.commonpath([replays_abs, file_abs]) == replays_abs
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.exception("Error validating filepath '%s': %s", filepath, e)
            return False

    def list_replays(self) -> List[Dict[str, Any]]:
        """
        Return a list of available replay files in the replays directory with their basic metadata.
        
        Files that are not valid JSON or are missing required fields are skipped; errors reading individual files are logged but do not stop listing.
        
        Returns:
            List[Dict[str, Any]]: A list of dictionaries sorted by `metadata['start_time']` descending. Each dictionary contains:
                - 'filename' (str): The file name.
                - 'filepath' (str): The full path to the file.
                - 'metadata' (dict): The parsed metadata object from the replay file (empty dict if absent).
        """
        if not os.path.exists(self.replays_dir):
            return []

        replays = []
        for filename in os.listdir(self.replays_dir):
            if filename.endswith('.json') or filename.endswith('.json.gz'):
                filepath = os.path.join(self.replays_dir, filename)
                try:
                    with _open_replay(filepath, 'rt') as f:
                        data = json.load(f)
                        replays.append({
                            'filename': filename,
                            'filepath': filepath,
                            'metadata': data.get('metadata', {}),
                        })
                except json.JSONDecodeError as e:
                    logger.warning(
                        "Skipping replay '%s': Invalid JSON - %s",
                        filename,
                        e,
                    )
                except KeyError as e:
                    logger.warning(
                        "Skipping replay '%s': Missing field - %s",
                        filename,
                        e,
                    )
                except Exception as e:  # pylint: disable=broad-exception-caught
                    logger.exception(
                        "Error reading replay '%s': %s",
                        filename,
                        e,
                    )

        # Sort by timestamp (newest first)
        replays.sort(
            key=lambda replay: replay['metadata'].get('start_time', 0),
            reverse=True,
        )
        return replays

    def delete_replay(self, filepath: str):
        """
        Delete the replay file at the given filepath if it resides inside the replays directory.
        
        If the filepath is outside the configured replays directory, the function does nothing.
        If the file does not exist, the function does nothing. If the file exists and is valid,
        it is removed; errors during removal are caught and logged.
        
        Parameters:
            filepath (str): Path to the replay file to delete. Only paths inside the manager's
                replays directory will be acted upon.
        """
        if not self._validate_filepath(filepath):
            logger.warning(
                "Attempted to delete file outside replays directory: %s",
                filepath,
            )
            return

        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                logger.info("Deleted replay file: %s", filepath)
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.exception("Failed to delete replay file '%s': %s", filepath, e)

    def get_replay_count(self) -> int:
        """Get the number of replay files."""
        return len(self.list_replays())