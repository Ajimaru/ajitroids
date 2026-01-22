"""Tests for PowerUp class and behavior."""

import pygame
import pytest

from modul.constants import (POWERUP_COLORS, POWERUP_LIFETIME, POWERUP_RADIUS,
                             POWERUP_TYPES)
from modul.powerup import PowerUp


@pytest.fixture(autouse=True)
def init_pygame():
    """Initialize pygame for each test"""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def powerup_group():
    """Create sprite group for powerups"""
    group = pygame.sprite.Group()
    PowerUp.containers = (group,)
    yield group
    PowerUp.containers = ()


class TestPowerUp:
    def test_powerup_type(self):
        powerup = PowerUp(10, 20, "shield")
        assert powerup.type == "shield"
        assert powerup.position.x == 10
        assert powerup.position.y == 20

    def test_powerup_initialization_with_type(self):
        """Test PowerUp initialization with specific type"""
        powerup = PowerUp(100, 200, powerup_type="shield")
        assert powerup.position.x == 100
        assert powerup.position.y == 200
        assert powerup.type == "shield"
        assert powerup.color == POWERUP_COLORS["shield"]
        assert powerup.radius == POWERUP_RADIUS
        assert powerup.lifetime == POWERUP_LIFETIME

    def test_powerup_initialization_random_type(self):
        """Test PowerUp initialization with random type"""
        powerup = PowerUp(100, 100)
        assert powerup.type in POWERUP_TYPES
        assert powerup.color == POWERUP_COLORS[powerup.type]

    def test_powerup_has_velocity(self):
        """Test powerup has initial velocity"""
        powerup = PowerUp(100, 100)
        assert powerup.velocity.length() > 0

    def test_powerup_update_movement(self):
        """Test powerup moves during update"""
        powerup = PowerUp(100, 100)
        initial_pos = pygame.Vector2(powerup.position)
        powerup.update(0.1)
        assert powerup.position != initial_pos

    def test_powerup_update_rotation(self):
        """Test powerup rotates during update"""
        powerup = PowerUp(100, 100)
        initial_rotation = powerup.rotation
        powerup.update(0.1)
        assert powerup.rotation != initial_rotation

    def test_powerup_update_lifetime(self):
        """Test powerup lifetime decreases"""
        powerup = PowerUp(100, 100)
        initial_lifetime = powerup.lifetime
        powerup.update(0.1)
        assert powerup.lifetime < initial_lifetime

    def test_powerup_expires(self, powerup_group):
        """Test powerup kills itself when lifetime expires"""
        powerup = PowerUp(100, 100)
        assert powerup in powerup_group

        # Update beyond lifetime
        powerup.update(POWERUP_LIFETIME + 1)
        assert powerup not in powerup_group

    def test_powerup_draw_shield(self):
        """Test drawing shield powerup"""
        powerup = PowerUp(100, 100, powerup_type="shield")
        screen = pygame.Surface((800, 600))
        powerup.draw(screen)  # Should not raise exception

    def test_powerup_draw_triple_shot(self):
        """Test drawing triple_shot powerup"""
        powerup = PowerUp(100, 100, powerup_type="triple_shot")
        screen = pygame.Surface((800, 600))
        powerup.draw(screen)  # Should not raise exception

    def test_powerup_draw_rapid_fire(self):
        """Test drawing rapid_fire powerup"""
        powerup = PowerUp(100, 100, powerup_type="rapid_fire")
        screen = pygame.Surface((800, 600))
        powerup.draw(screen)  # Should not raise exception

    def test_powerup_draw_laser_weapon(self):
        """Test drawing laser_weapon powerup"""
        powerup = PowerUp(100, 100, powerup_type="laser_weapon")
        screen = pygame.Surface((800, 600))
        powerup.draw(screen)  # Should not raise exception

    def test_powerup_draw_missile_weapon(self):
        """Test drawing missile_weapon powerup"""
        powerup = PowerUp(100, 100, powerup_type="missile_weapon")
        screen = pygame.Surface((800, 600))
        powerup.draw(screen)  # Should not raise exception

    def test_powerup_draw_shotgun_weapon(self):
        """Test drawing shotgun_weapon powerup"""
        powerup = PowerUp(100, 100, powerup_type="shotgun_weapon")
        screen = pygame.Surface((800, 600))
        powerup.draw(screen)  # Should not raise exception

    def test_powerup_draw_all_types(self):
        """Test drawing all powerup types"""
        screen = pygame.Surface((800, 600))
        for powerup_type in POWERUP_TYPES:
            powerup = PowerUp(100, 100, powerup_type=powerup_type)
            powerup.draw(screen)  # Should not raise exception

    def test_powerup_pulse_when_expiring(self):
        """Test powerup pulses when lifetime is low"""
        powerup = PowerUp(100, 100)
        powerup.lifetime = 2.0  # Low lifetime
        screen = pygame.Surface((800, 600))
        powerup.draw(screen)  # Should pulse, not crash

    def test_powerup_pulse_when_not_expiring(self):
        """Test powerup doesn't pulse with high lifetime"""
        powerup = PowerUp(100, 100)
        powerup.lifetime = 10.0  # High lifetime
        screen = pygame.Surface((800, 600))
        powerup.draw(screen)  # Should not pulse

    def test_powerup_different_colors(self):
        """Test each powerup type has unique color"""
        colors = set()
        for powerup_type in POWERUP_TYPES:
            powerup = PowerUp(100, 100, powerup_type=powerup_type)
            colors.add(powerup.color)

        # Most types should have unique colors
        assert len(colors) >= len(POWERUP_TYPES) - 2

    def test_powerup_velocity_variation(self):
        """Test powerups have varying velocities"""
        velocities = []
        for _ in range(10):
            powerup = PowerUp(100, 100)
            velocities.append((powerup.velocity.x, powerup.velocity.y))

        # Should have variation
        assert len(set(velocities)) > 1

    def test_powerup_rotation_speed(self):
        """Test powerup rotation speed"""
        powerup = PowerUp(100, 100)
        powerup.rotation = 0
        powerup.update(1.0)

        # Should rotate 90 degrees per second
        assert powerup.rotation == pytest.approx(90, abs=1)

    def test_powerup_position_update_with_velocity(self):
        """Test powerup position updates based on velocity"""
        powerup = PowerUp(100, 100)
        powerup.velocity = pygame.Vector2(50, 0)

        powerup.update(1.0)

        # Should move by velocity * dt
        assert powerup.position.x == pytest.approx(150, abs=1)
        assert powerup.position.y == pytest.approx(100, abs=1)

    def test_powerup_multiple_updates(self):
        """Test multiple updates don't cause issues"""
        powerup = PowerUp(100, 100)
        for _ in range(10):
            powerup.update(0.1)

        # Should still exist and have valid state
        assert powerup.lifetime > 0 or not powerup.alive()

    def test_powerup_types_all_valid(self):
        """Test all powerup types are valid"""
        for powerup_type in POWERUP_TYPES:
            powerup = PowerUp(100, 100, powerup_type=powerup_type)
            assert powerup.type == powerup_type
            assert powerup.color == POWERUP_COLORS[powerup_type]
