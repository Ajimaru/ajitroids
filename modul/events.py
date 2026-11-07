"""Random in-run events that add variety without changing the core loop.

An event is a one-shot twist (helpful or briefly challenging) picked by the
EventScheduler on a cooldown. Events are gated by the current level so new
players meet them only after the basics. They never replace the asteroid loop:
the field, the score curve and the mode pacing stay in charge.
"""

import random

import modul.constants as C


class EventScheduler:
    """Pick a random event on a cooldown, gated by the current level."""

    def __init__(self):
        """Initialize the scheduler with its first cooldown running."""
        self.cooldown = C.EVENT_FIRST_DELAY

    def update(self, dt, level):
        """Return the next event name once the cooldown elapses, else None."""
        self.cooldown -= dt
        if self.cooldown > 0:
            return None
        available = [
            name for name, min_level in C.EVENT_LEVEL_UNLOCK.items()
            if level >= min_level
        ]
        if not available:
            self.cooldown = C.EVENT_MIN_INTERVAL
            return None
        event = random.choices(
            available, weights=[C.EVENT_WEIGHTS[name] for name in available]
        )[0]
        self.cooldown = random.uniform(C.EVENT_MIN_INTERVAL, C.EVENT_MAX_INTERVAL)
        return event
