"""Headless soak test: drive every mode x difficulty combo through main().

Runs the real game loop with scripted input for a bounded number of frames and
reports exceptions per combo. Ships unlocked along the way become the active
ship for the remaining combos. Intended for manual runs, not CI.

Usage: python scripts/soak_game.py [frames]
"""
import contextlib
import os
import sys
import tempfile
import traceback
from types import SimpleNamespace
from pathlib import Path
import time

FRAMES = int(sys.argv[1]) if len(sys.argv) > 1 else 36000

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import main  # noqa: E402
import modul.audio_enhancements as audio  # noqa: E402
from modul.replay_system import ReplayRecorder  # noqa: E402
from modul.session_stats import SessionStats  # noqa: E402

# Classic first so the level-50 ship unlocks (keyed by difficulty) land early;
# the survival/time-attack combos then run with the newest unlocked ship.
COMBOS = [
    ("classic", "easy"),
    ("classic", "normal"),
    ("classic", "hard"),
    ("survival", "easy"),
    ("survival", "normal"),
    ("survival", "hard"),
    ("time_attack", "easy"),
    ("time_attack", "normal"),
    ("time_attack", "hard"),
]

_ORIG_EVENT_GET = pygame.event.get
_ORIG_DELAY = pygame.time.delay
_ORIG_CLOCK = pygame.time.Clock
_ORIG_TIME = time.time
_SIM_TIME = _ORIG_TIME()


_ACTIONS = set()


def _patched_is_action_pressed(action):
    """Fake input: True only for actions the soak script currently holds."""
    return action in _ACTIONS


def _patch_runtime():
    """Replace wall-clock timing, TTS and input with scripted stand-ins."""
    audio.TTS_AVAILABLE = False
    pygame.time.delay = lambda _ms: None

    def tick(_fps):
        global _SIM_TIME
        _SIM_TIME += 0.016
        return 16

    pygame.time.Clock = lambda: SimpleNamespace(tick=tick, get_fps=lambda: 62.5)
    time.time = lambda: _SIM_TIME
    main.input_utils.is_action_pressed = _patched_is_action_pressed


def run_combo(mode, difficulty, frames):
    """Run one combo and return (status, traceback, context)."""
    stats = SessionStats()
    recorder = ReplayRecorder()
    context = SimpleNamespace(frames=0, states=set(), max_level=0, max_score=0)

    # Isolate the global sprite groups and entity containers per run so
    # successive main() calls don't leak state.
    main.collidable = pygame.sprite.Group()
    for entity in (main.Asteroid, main.Shot, main.Particle, main.PowerUp,
                   main.Player, main.Boss, main.BossProjectile):
        entity.containers = ()
    main.Shot.asteroids_group = None
    main.SessionStats = lambda: stats
    main.ReplayRecorder = lambda: recorder

    main.GameModeMenu.update = lambda _self, *_a: f"mode_{mode}"
    main.DifficultyMenu.update = lambda _self, *_a: f"difficulty_{difficulty}"
    main.ShipSelectionMenu.update = lambda _self, *_a: "start_game"
    main.MainMenu.update = lambda _self, *_a: "start_game"

    def events():
        context.frames += 1
        context.states.add(main.game_state)
        context.max_level = max(context.max_level, main.level)
        context.max_score = max(context.max_score, main.score)
        _ACTIONS.clear()
        if context.frames >= frames:
            return [pygame.event.Event(pygame.QUIT)]
        # Keep the ship alive and actively hunting so the soak scores, levels
        # up and reaches bosses, hazards and events instead of idling.
        player = getattr(main, "player", None)
        if player is not None:
            player.invincible = True
            _ACTIONS.add("shoot")
            _ACTIONS.add("thrust")
            targets = [a for a in (main.Asteroid.containers[0] if main.Asteroid.containers else ())
                       if hasattr(a, "position")]
            updatable_group = main.Boss.containers[0] if main.Boss.containers else None
            if updatable_group is not None:
                targets.extend(o for o in updatable_group if isinstance(o, main.Boss))
            if targets:
                nearest = min(targets, key=lambda a: a.position.distance_to(player.position))
                player.rotation = pygame.Vector2(0, -1).angle_to(nearest.position - player.position)
        out = []
        if main.game_state == "game_over" and context.frames % 20 == 0:
            out.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r))
        return out

    pygame.event.get = events
    args = SimpleNamespace(debug=False, log_file=None, fullscreen=False,
                           windowed=True, skip_intro=True, mode=mode)
    real_stdout = sys.stdout
    try:
        with open(os.devnull, "w", encoding="utf-8") as sink, contextlib.redirect_stdout(sink):
            main.main(args)
        return "OK", None, context
    except Exception:  # pylint: disable=broad-exception-caught
        return "FAIL", traceback.format_exc(), context
    finally:
        sys.stdout = real_stdout
        pygame.event.get = _ORIG_EVENT_GET


def newest_ship():
    """Return the most recently unlocked ship id."""
    unlocked = main.ship_manager.get_unlocked_ships()
    return unlocked[-1] if unlocked else "standard"


def main_soak():
    """Run every combo and report the outcome."""
    _patch_runtime()
    tmp = tempfile.mkdtemp(prefix="ajitroids_soak_")
    os.chdir(tmp)
    failures = 0
    for mode, difficulty in COMBOS:
        ship = newest_ship()
        main.ship_manager.set_current_ship(ship)
        status, tb, ctx = run_combo(mode, difficulty, FRAMES)
        states = ", ".join(sorted(ctx.states))
        print(f"[{status}] {mode:11s} / {difficulty:6s} ship={ship:9s} "
              f"frames={ctx.frames} max_level={ctx.max_level} "
              f"max_score={ctx.max_score} states={{{states}}}")
        if status == "FAIL":
            failures += 1
            print(tb)
    print(f"\nSoak done: {len(COMBOS)} combos, {failures} failures")
    pygame.quit()
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main_soak())
