"""Tests for the kill-chain combo tracker."""

import pytest

from modul.combo import ComboTracker
from modul.constants import COMBO_HUD_MIN, COMBO_TIERS, COMBO_WINDOW


@pytest.fixture
def combo():
    """Fresh tracker using the production constants."""
    return ComboTracker()


class TestComboTracker:
    """Combo counting, tier resolution and expiry."""

    def test_starts_inactive(self, combo):
        """A fresh tracker is empty and scores at 1x."""
        assert combo.count == 0
        assert combo.timer == 0.0
        assert combo.best == 0
        assert combo.multiplier == 1
        assert not combo.active
        assert combo.ratio == 0.0

    def test_tiers_match_constants(self, combo):
        """Multiplier follows COMBO_TIERS boundaries exactly."""
        top_kills, top_multiplier = COMBO_TIERS[0]
        low_kills, low_multiplier = COMBO_TIERS[1]

        for _ in range(low_kills - 1):
            assert combo.register_kill() == 1

        assert combo.register_kill() == low_multiplier

        while combo.count < top_kills:
            multiplier = combo.register_kill()

        assert multiplier == top_multiplier
        assert combo.multiplier == top_multiplier

    def test_kill_refreshes_timer(self, combo):
        """Every kill restarts the chain window."""
        combo.register_kill()
        combo.update(COMBO_WINDOW - 0.1)
        assert combo.count == 1

        combo.register_kill()
        assert combo.timer == COMBO_WINDOW
        assert combo.count == 2

    def test_chain_expires_after_window(self, combo):
        """Time beyond the window drops the chain back to zero."""
        combo.register_kill()
        combo.update(COMBO_WINDOW - 0.01)
        assert combo.count == 1

        combo.update(0.02)
        assert combo.count == 0
        assert combo.timer == 0.0
        assert combo.multiplier == 1

    def test_expired_timer_stays_zero(self, combo):
        """Further updates on an expired chain are a no-op."""
        combo.update(1.0)
        assert combo.count == 0
        assert combo.timer == 0.0

    def test_best_tracks_longest_chain(self, combo):
        """best remembers the peak even after the chain breaks."""
        for _ in range(6):
            combo.register_kill()
        assert combo.best == 6

        combo.update(COMBO_WINDOW + 0.1)
        combo.register_kill()

        assert combo.count == 1
        assert combo.best == 6

    def test_reset_keeps_best(self, combo):
        """reset() clears the chain but not the session best."""
        for _ in range(4):
            combo.register_kill()
        combo.reset()

        assert combo.count == 0
        assert combo.timer == 0.0
        assert combo.best == 4

    def test_active_threshold(self):
        """HUD flag flips at COMBO_HUD_MIN."""
        combo = ComboTracker()

        for _ in range(COMBO_HUD_MIN - 1):
            combo.register_kill()
        assert not combo.active

        combo.register_kill()
        assert combo.active

    def test_custom_window_and_tiers(self):
        """Constructor arguments override the defaults."""
        combo = ComboTracker(window=1.0, tiers=((2, 5),))

        assert combo.register_kill() == 1
        assert combo.register_kill() == 5

        combo.update(1.01)
        assert combo.count == 0

    def test_ratio_counts_down(self, combo):
        """ratio reports the remaining share of the window."""
        combo.register_kill()
        assert combo.ratio == pytest.approx(1.0)

        combo.update(COMBO_WINDOW / 2)
        assert combo.ratio == pytest.approx(0.5)

        combo.update(COMBO_WINDOW)
        assert combo.ratio == 0.0

    def test_zero_window_ratio_is_safe(self):
        """A zero window must not divide by zero."""
        assert ComboTracker(window=0.0).ratio == 0.0


@pytest.mark.parametrize("reset", [False, True])
def test_asteroid_count_uses_shared_chain(reset):
    combo = ComboTracker()
    combo.register_kill(asteroid=True)
    combo.update(combo.window / 2)
    combo.register_kill()
    assert combo.count == 2
    assert combo.asteroid_count == 1
    if reset:
        combo.reset()
    else:
        combo.update(combo.window)
    assert combo.asteroid_count == 0
    combo.register_kill()
    assert combo.asteroid_count == 0
