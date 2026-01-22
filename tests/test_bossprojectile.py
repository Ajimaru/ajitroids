"""Tests for boss projectiles and their behavior."""

import pytest
import pygame
from unittest.mock import patch, MagicMock
from modul.bossprojectile import BossProjectile
from modul.constants import *


@pytest.fixture
def mock_pygame():
    """Mock pygame components for isolated testing"""
    with patch('pygame.sprite.Sprite.__init__'):
        yield


class TestBossProjectile:
    """Test suite for BossProjectile class functionality"""

    def test_boss_projectile_initialization(self, mock_pygame):
        """Test boss projectile initializes correctly"""
        x, y = 100, 200
        velocity = pygame.Vector2(50, -50)

        projectile = BossProjectile(x, y, velocity)

        assert projectile.position.x == x
        assert projectile.position.y == y
        assert projectile.velocity == velocity
        assert projectile.radius == BOSS_PROJECTILE_RADIUS
        assert projectile.type == "normal"
        assert projectile.lifetime == 5.0
        assert projectile.damage == 1
        assert projectile.rotation == 0
        assert projectile.rotation_speed == 180

    def test_boss_projectile_initialization_with_type(self, mock_pygame):
        """Test boss projectile initializes with specified type"""
        projectile = BossProjectile(0, 0, pygame.Vector2(0, 0), "homing")

        assert projectile.type == "homing"

    def test_boss_projectile_types(self, mock_pygame):
        """Test different projectile types have correct colors"""
        types_to_test = ["normal", "homing", "explosive"]

        for proj_type in types_to_test:
            projectile = BossProjectile(0, 0, pygame.Vector2(0, 0), proj_type)
            assert projectile.type == proj_type
            assert projectile.color == BOSS_PROJECTILE_COLORS.get(proj_type, BOSS_COLOR)

    def test_boss_projectile_movement(self, mock_pygame):
        """Test projectile moves according to velocity"""
        velocity = pygame.Vector2(100, 0)  # 100 pixels/second right
        projectile = BossProjectile(0, 0, velocity)

        # Update for 0.1 seconds
        projectile.update(0.1)

        # Should move 10 pixels right
        assert projectile.position.x == 10
        assert projectile.position.y == 0

    def test_boss_projectile_movement_diagonal(self, mock_pygame):
        """Test projectile moves diagonally"""
        velocity = pygame.Vector2(100, 100)
        projectile = BossProjectile(0, 0, velocity)

        projectile.update(0.1)

        assert projectile.position.x == 10
        assert projectile.position.y == 10

    def test_boss_projectile_rotation(self, mock_pygame):
        """Test projectile rotates over time"""
        projectile = BossProjectile(0, 0, pygame.Vector2(0, 0))
        initial_rotation = projectile.rotation

        # Update for some time
        projectile.update(0.1)

        # Rotation should have changed
        assert projectile.rotation != initial_rotation
        assert projectile.rotation == initial_rotation + 180 * 0.1

    def test_boss_projectile_rotation_multiple_updates(self, mock_pygame):
        """Test rotation accumulates over multiple updates"""
        projectile = BossProjectile(0, 0, pygame.Vector2(0, 0))

        projectile.update(0.1)
        projectile.update(0.1)

        assert projectile.rotation == 180 * 0.2

    def test_boss_projectile_lifetime_decrements(self, mock_pygame):
        """Test lifetime decrements over time"""
        projectile = BossProjectile(0, 0, pygame.Vector2(0, 0))
        initial_lifetime = projectile.lifetime

        projectile.update(0.5)

        assert projectile.lifetime == initial_lifetime - 0.5

    def test_boss_projectile_lifetime_expiry(self, mock_pygame):
        """Test projectile gets killed when lifetime expires"""
        projectile = BossProjectile(0, 0, pygame.Vector2(0, 0))
        projectile.lifetime = 0.1
        projectile.kill = MagicMock()

        # Update past lifetime
        projectile.update(0.2)

        # Should be killed
        projectile.kill.assert_called_once()

    def test_boss_projectile_screen_bounds_left(self, mock_pygame):
        """Test projectile killed when leaving left edge"""
        projectile = BossProjectile(0, 0, pygame.Vector2(-1000, 0))
        projectile.kill = MagicMock()

        projectile.update(1.0)

        projectile.kill.assert_called_once()

    def test_boss_projectile_screen_bounds_right(self, mock_pygame):
        """Test projectile killed when leaving right edge"""
        projectile = BossProjectile(SCREEN_WIDTH, 0, pygame.Vector2(1000, 0))
        projectile.kill = MagicMock()

        projectile.update(1.0)

        projectile.kill.assert_called_once()

    def test_boss_projectile_screen_bounds_top(self, mock_pygame):
        """Test projectile killed when leaving top edge"""
        projectile = BossProjectile(100, 0, pygame.Vector2(0, -1000))
        projectile.kill = MagicMock()

        projectile.update(1.0)

        projectile.kill.assert_called_once()

    def test_boss_projectile_screen_bounds_bottom(self, mock_pygame):
        """Test projectile killed when leaving bottom edge"""
        projectile = BossProjectile(100, SCREEN_HEIGHT, pygame.Vector2(0, 1000))
        projectile.kill = MagicMock()

        projectile.update(1.0)

        projectile.kill.assert_called_once()

    def test_boss_projectile_screen_bounds(self, mock_pygame):
        """Test projectile gets killed when leaving screen"""
        projectile = BossProjectile(0, 0, pygame.Vector2(-1000, 0))  # Fast left movement
        projectile.kill = MagicMock()

        # Update to move off screen
        projectile.update(1.0)

        # Should be killed when off screen
        projectile.kill.assert_called_once()

    def test_boss_projectile_screen_bounds_margin(self, mock_pygame):
        """Test screen bounds check has margin"""
        projectile = BossProjectile(-25, 0, pygame.Vector2(0, 0))
        projectile.kill = MagicMock()

        projectile.update(0.1)

        # Should be killed (outside -20 margin)
        projectile.kill.assert_called_once()

    def test_boss_projectile_damage_values(self, mock_pygame):
        """Test all projectile types have appropriate damage"""
        for proj_type in ["normal", "homing", "explosive"]:
            projectile = BossProjectile(0, 0, pygame.Vector2(0, 0), proj_type)
            assert projectile.damage >= 1

    def test_boss_projectile_draw_normal(self, mock_pygame):
        """Test drawing normal projectile"""
        projectile = BossProjectile(100, 100, pygame.Vector2(0, 0), "normal")
        screen = pygame.Surface((800, 600))

        projectile.draw(screen)  # Should not raise exception

    def test_boss_projectile_draw_homing(self, mock_pygame):
        """Test drawing homing projectile"""
        projectile = BossProjectile(100, 100, pygame.Vector2(0, 0), "homing")
        screen = pygame.Surface((800, 600))

        projectile.draw(screen)

    def test_boss_projectile_draw_explosive(self, mock_pygame):
        """Test drawing explosive projectile"""
        projectile = BossProjectile(100, 100, pygame.Vector2(0, 0), "explosive")
        screen = pygame.Surface((800, 600))

        projectile.draw(screen)

    def test_boss_projectile_draw_with_rotation(self, mock_pygame):
        """Test drawing projectile with rotation"""
        projectile = BossProjectile(100, 100, pygame.Vector2(0, 0), "homing")
        projectile.rotation = 45
        screen = pygame.Surface((800, 600))

        projectile.draw(screen)
