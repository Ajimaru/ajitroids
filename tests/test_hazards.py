"""Tests for environmental hazards (black holes and their base class)."""

import pygame
import pytest

import modul.constants as C
from modul.circleshape import CircleShape
from modul.hazards import BlackHole, Hazard, SolarFlare


def test_gravity_points_toward_core():
    """The pull must accelerate objects toward the hole's centre."""
    hole = BlackHole(0, 0)
    vec = hole.gravity_vector(pygame.Vector2(100, 0))
    assert vec.x < 0  # nosec B101
    assert vec.y == pytest.approx(0.0)  # nosec B101


def test_gravity_is_zero_beyond_pull_radius():
    """Objects outside the pull radius must be unaffected."""
    hole = BlackHole(0, 0)
    vec = hole.gravity_vector(pygame.Vector2(C.BLACK_HOLE_PULL_RADIUS + 100, 0))
    assert vec.x == pytest.approx(0.0)  # nosec B101
    assert vec.y == pytest.approx(0.0)  # nosec B101


def test_gravity_falls_off_with_distance():
    """The pull must weaken as the distance from the core grows."""
    hole = BlackHole(0, 0)
    near = hole.gravity_vector(pygame.Vector2(50, 0)).length()
    far = hole.gravity_vector(pygame.Vector2(150, 0)).length()
    assert near > far > 0  # nosec B101


def test_apply_forces_accelerates_toward_core():
    """apply_forces must add velocity in the direction of the hole."""
    hole = BlackHole(0, 0)
    obj = CircleShape(100, 0, 5)
    obj.velocity = pygame.Vector2(10, 0)
    hole.apply_forces([obj], 1.0)
    assert obj.velocity.x < 10  # nosec B101


def test_apply_forces_skips_self_and_unmovable_objects():
    """The hole must not pull itself or objects without a velocity."""
    hole = BlackHole(0, 0)
    obj = CircleShape(100, 0, 5)
    obj.velocity = pygame.Vector2(0, 0)
    hole.apply_forces([hole, obj], 1.0)
    assert hole.velocity == pygame.Vector2(0, 0)  # nosec B101
    assert obj.velocity.length() > 0  # nosec B101


def test_hazard_dies_after_lifetime():
    """A hazard must leave its group once the lifetime is spent."""
    group = pygame.sprite.Group()
    old_containers = getattr(BlackHole, "containers", None)
    BlackHole.containers = (group,)
    try:
        hole = BlackHole(0, 0)
        assert hole in group  # nosec B101
        hole.update(C.BLACK_HOLE_LIFETIME + 1.0)
        assert hole not in group  # nosec B101
    finally:
        BlackHole.containers = old_containers


def test_hazard_base_uses_default_draw_safely():
    """The base draw path must tolerate a missing colour and a None surface."""
    hazard = Hazard(0, 0, 10, 5.0)
    hazard.draw(None)
    assert hazard.lifetime == pytest.approx(5.0)  # nosec B101


def test_solar_flare_holds_during_warning():
    """The band must stay put while the warning is counting down."""
    flare = SolarFlare()
    y_before = flare.position.y
    flare.update(0.5)
    assert flare.position.y == y_before  # nosec B101
    assert flare.warning_remaining == pytest.approx(C.SOLAR_FLARE_WARNING - 0.5)  # nosec B101


def test_solar_flare_sweeps_after_warning():
    """Once the warning is over, the band must move at its configured speed."""
    flare = SolarFlare(warning=0.0)
    y_before = flare.position.y
    flare.update(1.0)
    assert flare.position.y == pytest.approx(y_before + C.SOLAR_FLARE_SPEED)  # nosec B101


def test_solar_flare_dies_off_screen():
    """The flare must leave its group once it has swept past the bottom."""
    group = pygame.sprite.Group()
    old_containers = getattr(SolarFlare, "containers", None)
    SolarFlare.containers = (group,)
    try:
        flare = SolarFlare(warning=0.0, speed=100000.0)
        assert flare in group  # nosec B101
        flare.update(1.0)
        assert flare not in group  # nosec B101
    finally:
        SolarFlare.containers = old_containers


def test_solar_flare_collision_is_vertical_band():
    """Contact must depend on the vertical band, not on horizontal position."""
    flare = SolarFlare(warning=0.0)
    inside = CircleShape(0, flare.position.y, 5)
    outside = CircleShape(0, flare.position.y - C.SOLAR_FLARE_THICKNESS, 5)
    assert flare.collides_with(inside)  # nosec B101
    assert not flare.collides_with(outside)  # nosec B101
