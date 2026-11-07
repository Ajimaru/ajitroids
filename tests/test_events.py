"""Tests for the in-run event scheduler."""

import pytest

import modul.constants as C
from modul.events import EventScheduler


def test_scheduler_waits_out_the_first_delay():
    """No event may fire before the initial cooldown has elapsed."""
    scheduler = EventScheduler()
    assert scheduler.update(0.1, 99) is None  # nosec B101


def test_scheduler_returns_none_below_min_level():
    """No event may fire below the minimum unlock level."""
    scheduler = EventScheduler()
    scheduler.cooldown = 0
    assert scheduler.update(0.0, 0) is None  # nosec B101
    assert scheduler.cooldown == pytest.approx(C.EVENT_MIN_INTERVAL)  # nosec B101


def test_scheduler_returns_known_event():
    """Once unlocked, the scheduler must return a configured event type."""
    scheduler = EventScheduler()
    scheduler.cooldown = 0
    event = scheduler.update(0.0, C.EVENT_LEVEL_UNLOCK["emp"] + 1)
    assert event in C.EVENT_TYPES  # nosec B101


def test_scheduler_resets_cooldown_after_event():
    """After firing, the scheduler must go quiet for the cooldown window."""
    scheduler = EventScheduler()
    scheduler.cooldown = 0
    assert scheduler.update(0.0, 99) in C.EVENT_TYPES  # nosec B101
    assert scheduler.update(0.01, 99) is None  # nosec B101
