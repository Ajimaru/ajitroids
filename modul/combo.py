"""Kill-chain combo tracking.

A combo counts consecutive kills. Every kill refreshes the chain timer; when
the timer runs out the chain drops back to zero and the score multiplier
returns to 1x.

The tracker is driven by gameplay time (`dt`) instead of the wall clock, so
pausing the game also freezes the chain and recorded replays stay consistent.
"""

import modul.constants as C


class ComboTracker:
    """Count consecutive kills and turn them into a score multiplier."""

    def __init__(self, window=None, tiers=None):
        """Create a tracker; defaults come from the constants module."""
        self.window = C.COMBO_WINDOW if window is None else window
        self.tiers = C.COMBO_TIERS if tiers is None else tiers
        self.asteroid_count = 0
        self.count = 0
        self.timer = 0.0
        self.best = 0

    def update(self, dt):
        """Advance the countdown and drop the chain once it expires."""
        if self.timer <= 0:
            return

        self.timer -= dt
        if self.timer <= 0:
            self.reset()

    def register_kill(self, *, asteroid=False):
        """Count one kill and return the multiplier this kill scores with.

        The multiplier is resolved after the counter was raised, so the kill
        that reaches a tier already earns the new multiplier.
        """
        self.timer = self.window
        self.count += 1
        if asteroid:
            self.asteroid_count += 1
        self.best = max(self.best, self.count)
        return self.multiplier

    def reset(self):
        """Drop the current chain; the session best is kept."""
        self.asteroid_count = 0
        self.count = 0
        self.timer = 0.0

    @property
    def multiplier(self):
        """Score multiplier for the current chain length."""
        for kills, multiplier in self.tiers:
            if self.count >= kills:
                return multiplier
        return 1

    @property
    def active(self):
        """True while the chain is long enough to be worth showing."""
        return self.count >= C.COMBO_HUD_MIN

    @property
    def ratio(self):
        """Remaining share of the chain window, clamped to 0..1."""
        if self.window <= 0:
            return 0.0
        return max(0.0, min(1.0, self.timer / self.window))
