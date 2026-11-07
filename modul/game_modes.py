"""Progression rules for the alternative game modes.

Both modes reuse the classic game loop but replace the score-driven level
setup with their own pacing:

* survival runs endless waves that get bigger and faster,
* time attack hands out a kill quota per round while a clock runs down.

The classes here hold no pygame state, so the rules can be unit-tested without
booting the game.
"""

import math

import modul.constants as C


class SurvivalProgression:
    """Endless wave bookkeeping for survival mode."""

    def __init__(self, difficulty="normal"):
        """Start at wave 1 with no kills."""
        self.difficulty = difficulty if difficulty in C.SURVIVAL_DIFFICULTY_TARGET_FACTORS else "normal"
        self.wave = 1
        self.kills = 0

    def set_difficulty(self, difficulty):
        """Pick the multiplier used for wave quotas and spawn pacing."""
        self.difficulty = difficulty if difficulty in C.SURVIVAL_DIFFICULTY_TARGET_FACTORS else "normal"

    def reset(self):
        """Restart the run at wave 1."""
        self.wave = 1
        self.kills = 0

    @property
    def target(self):
        """Asteroids that have to be destroyed to clear this wave."""
        base = C.SURVIVAL_WAVE_BASE_TARGET + (self.wave - 1) * C.SURVIVAL_WAVE_TARGET_STEP
        scaled = math.ceil(base * C.SURVIVAL_DIFFICULTY_TARGET_FACTORS[self.difficulty])
        return min(scaled, C.SURVIVAL_WAVE_MAX_TARGET)

    @property
    def asteroid_count(self):
        """Concurrent asteroids the field keeps alive in this wave."""
        return min(
            C.SURVIVAL_WAVE_BASE_COUNT + (self.wave - 1) * C.SURVIVAL_WAVE_COUNT_STEP,
            C.SURVIVAL_WAVE_MAX_COUNT,
        )

    @property
    def spawn_interval(self):
        """Seconds between replacement spawns in this wave."""
        base = C.SURVIVAL_WAVE_BASE_INTERVAL - (self.wave - 1) * C.SURVIVAL_WAVE_INTERVAL_STEP
        scaled = base * C.SURVIVAL_DIFFICULTY_INTERVAL_FACTORS[self.difficulty]
        return max(scaled, C.SURVIVAL_WAVE_MIN_INTERVAL)

    @property
    def bonus(self):
        """Score awarded for clearing the current wave."""
        return C.SURVIVAL_WAVE_SCORE_BONUS * self.wave

    @property
    def remaining(self):
        """Asteroids still missing for the current wave."""
        return max(0, self.target - self.kills)

    def register_kill(self):
        """Count one asteroid kill and report whether the wave is cleared."""
        self.kills += 1
        return self.kills >= self.target

    def next_wave(self):
        """Advance to the next wave and reset the kill counter."""
        self.wave += 1
        self.kills = 0


class TimeAttackProgression:
    """Round and clock bookkeeping for time attack mode."""

    def __init__(self, difficulty="normal"):
        """Start at round 1 with a full clock."""
        self.difficulty = difficulty if difficulty in C.TIME_ATTACK_DIFFICULTY_TARGET_FACTORS else "normal"
        self.round = 1
        self.kills = 0
        self.remaining = C.TIME_ATTACK_ROUND_TIME

    def set_difficulty(self, difficulty):
        """Pick the multiplier used for the round quota."""
        self.difficulty = difficulty if difficulty in C.TIME_ATTACK_DIFFICULTY_TARGET_FACTORS else "normal"

    def reset(self):
        """Restart the run at round 1 with a full clock."""
        self.round = 1
        self.kills = 0
        self.remaining = C.TIME_ATTACK_ROUND_TIME

    @property
    def target(self):
        """Asteroids required to clear the current round."""
        base = C.TIME_ATTACK_BASE_TARGET + (self.round - 1) * C.TIME_ATTACK_TARGET_STEP
        scaled = math.ceil(base * C.TIME_ATTACK_DIFFICULTY_TARGET_FACTORS[self.difficulty])
        return min(scaled, C.TIME_ATTACK_MAX_TARGET)

    @property
    def bonus(self):
        """Score awarded for clearing the current round."""
        return C.TIME_ATTACK_SCORE_BONUS * self.round

    @property
    def ratio(self):
        """Remaining share of the round clock, clamped to 0..1."""
        full = C.TIME_ATTACK_ROUND_TIME + C.TIME_ATTACK_BONUS_TIME
        if full <= 0:
            return 0.0
        return max(0.0, min(1.0, self.remaining / full))

    def update(self, dt):
        """Advance the clock and report whether time ran out."""
        self.remaining -= dt
        if self.remaining <= 0:
            self.remaining = 0.0
            return True
        return False

    def register_kill(self):
        """Count one asteroid kill and report whether the round is cleared."""
        self.kills += 1
        return self.kills >= self.target

    def next_round(self):
        """Advance to the next round, keeping leftover time plus the bonus."""
        self.round += 1
        self.kills = 0
        self.remaining = min(
            self.remaining + C.TIME_ATTACK_BONUS_TIME,
            C.TIME_ATTACK_ROUND_TIME + C.TIME_ATTACK_BONUS_TIME,
        )
