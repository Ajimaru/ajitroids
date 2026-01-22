"""Tests for Shot class and projectile behavior."""

from unittest.mock import patch, MagicMock

import pytest
import pygame
from modul.shot import Shot
from modul.constants import WEAPON_COLORS, WEAPON_LASER, WEAPON_MISSILE, WEAPON_SHOTGUN, WEAPON_STANDARD


@pytest.fixture
def mock_pygame():
    """Mock pygame components for isolated testing"""
    with patch('pygame.sprite.Sprite.__init__'):
        yield


class TestShot:
    """Test suite for Shot class functionality"""

    def test_shot_initialization_standard(self, mock_pygame):
        """Test standard shot initialization"""
        shot = Shot(10, 20)

        assert shot.position.x == 10
        assert shot.position.y == 20
        assert shot.radius == 3
        assert shot.shot_type == WEAPON_STANDARD
        assert shot.lifetime == 2.0
        assert shot.damage == 1
        assert shot.target is None
        assert shot.homing_power == 0

    def test_shot_initialization_laser(self, mock_pygame):
        """Test laser shot has different properties"""
        shot = Shot(10, 20, WEAPON_LASER)

        assert shot.shot_type == WEAPON_LASER
        assert shot.radius == 2
        assert shot.damage == 2
        assert hasattr(shot, 'penetrating')
        assert shot.penetrating is True

    def test_shot_initialization_missile(self, mock_pygame):
        """Test missile shot has homing capabilities"""
        shot = Shot(10, 20, WEAPON_MISSILE)

        assert shot.shot_type == WEAPON_MISSILE
        assert shot.radius == 4
        assert shot.damage == 3
        assert shot.homing_power == 150
        assert hasattr(shot, 'max_turn_rate')
        assert shot.max_turn_rate == 2.0
        assert shot.penetrating is False

    def test_shot_initialization_shotgun(self, mock_pygame):
        """Test shotgun shot properties"""
        shot = Shot(10, 20, WEAPON_SHOTGUN)

        assert shot.shot_type == WEAPON_SHOTGUN
        assert shot.radius == 2
        assert shot.damage == 1
        assert shot.penetrating is False
        assert shot.lifetime == 0.5

    def test_shot_colors(self, mock_pygame):
        """Test shots have correct colors"""
        for weapon_type in [WEAPON_STANDARD, WEAPON_LASER, WEAPON_MISSILE, WEAPON_SHOTGUN]:
            shot = Shot(0, 0, weapon_type)
            assert shot.color == WEAPON_COLORS[weapon_type]

    def test_shot_update_movement(self, mock_pygame):
        """Test shot moves according to velocity"""
        shot = Shot(0, 0)
        shot.velocity = pygame.Vector2(100, 0)  # 100 pixels/second right

        # Update for 0.1 seconds
        shot.update(0.1)

        # Should move 10 pixels right
        assert shot.position.x == 10
        assert shot.position.y == 0

    def test_shot_update_decrements_lifetime(self, mock_pygame):
        """Test lifetime decrements on update"""
        shot = Shot(0, 0)
        shot.lifetime = 1.0

        shot.update(0.5)

        assert shot.lifetime == 0.5

    def test_shot_lifetime_expiry(self, mock_pygame):
        """Test shot gets killed when lifetime expires"""
        shot = Shot(0, 0)
        shot.lifetime = 0.5
        shot.kill = MagicMock()

        # Update past lifetime
        shot.update(1.0)

        # Should be killed
        shot.kill.assert_called_once()

    def test_shot_update_missile_homing(self, mock_pygame, monkeypatch):
        """Test missile homes in on target"""
        shot = Shot(0, 0, WEAPON_MISSILE)
        shot.velocity = pygame.Vector2(100, 0)

        # Create mock target
        target = MagicMock()
        target.position = pygame.Vector2(100, 100)
        target.alive = MagicMock(return_value=True)

        monkeypatch.setattr(Shot, "asteroids_group", [target], raising=False)

        shot.update(0.1)

        # Velocity should have changed direction

    def test_shot_update_standard_no_homing(self, mock_pygame):
        """Test standard shot doesn't home"""
        shot = Shot(0, 0, WEAPON_STANDARD)
        shot.velocity = pygame.Vector2(100, 0)
        initial_velocity = shot.velocity.copy()

        shot.update(0.1)

        # Velocity direction should be unchanged (only position changes)
        assert shot.velocity.x == initial_velocity.x
        assert shot.velocity.y == initial_velocity.y

    def test_shot_set_asteroids_class_method(self, mock_pygame):
        """Test setting asteroids group"""
        asteroids_group = MagicMock()

        Shot.set_asteroids(asteroids_group)

        assert Shot.asteroids_group is asteroids_group

    def test_shot_set_enemy_ships_class_method(self, mock_pygame):
        """Test setting enemy ships group"""
        enemy_ships_group = MagicMock()

        Shot.set_enemy_ships(enemy_ships_group)

        assert Shot.enemy_ships_group is enemy_ships_group

    def test_shot_seek_target_no_groups(self, mock_pygame):
        """Test seek_target when no groups are set"""
        shot = Shot(0, 0, WEAPON_MISSILE)
        Shot.asteroids_group = None
        Shot.enemy_ships_group = None

        shot.seek_target(0.1)  # Should not crash

    def test_shot_seek_target_finds_closest(self, mock_pygame):
        """Test seek_target finds closest target"""
        shot = Shot(0, 0, WEAPON_MISSILE)
        shot.velocity = pygame.Vector2(100, 0)

        # Create mock targets at different distances
        target1 = MagicMock()
        target1.position = pygame.Vector2(50, 0)
        target1.alive = MagicMock(return_value=True)

        target2 = MagicMock()
        target2.position = pygame.Vector2(200, 0)
        target2.alive = MagicMock(return_value=True)

        Shot.asteroids_group = [target1, target2]

        shot.seek_target(0.1)

        # Should target the closer one
        assert shot.target is target1

        Shot.asteroids_group = None

    def test_shot_seek_target_retargets_dead(self, mock_pygame):
        """Test seek_target retargets when current target is dead"""
        shot = Shot(0, 0, WEAPON_MISSILE)
        shot.velocity = pygame.Vector2(100, 0)  # Give it velocity

        # Set dead target
        dead_target = MagicMock()
        dead_target.alive = MagicMock(return_value=False)
        shot.target = dead_target

        # Create new target
        new_target = MagicMock()
        new_target.position = pygame.Vector2(100, 100)
        new_target.alive = MagicMock(return_value=True)

        Shot.asteroids_group = [new_target]

        shot.seek_target(0.1)

        assert shot.target is new_target

        Shot.asteroids_group = None

    def test_shot_seek_target_turns_towards(self, mock_pygame):
        """Test missile turns towards target"""
        shot = Shot(0, 0, WEAPON_MISSILE)
        shot.velocity = pygame.Vector2(100, 0)  # Moving right

        # Create target above
        target = MagicMock()
        target.position = pygame.Vector2(0, -100)
        target.alive = MagicMock(return_value=True)

        Shot.asteroids_group = [target]

        initial_angle = shot.velocity.angle_to(pygame.Vector2(0, -1))
        shot.seek_target(0.1)
        new_angle = shot.velocity.angle_to(pygame.Vector2(0, -1))

        # Angle should have changed
        assert new_angle != initial_angle

        Shot.asteroids_group = None

    def test_shot_seek_target_from_enemy_ships(self, mock_pygame):
        """Test seeking targets from enemy ships group"""
        shot = Shot(0, 0, WEAPON_MISSILE)
        shot.velocity = pygame.Vector2(100, 0)

        enemy = MagicMock()
        enemy.position = pygame.Vector2(100, 0)
        enemy.alive = MagicMock(return_value=True)

        Shot.enemy_ships_group = [enemy]
        Shot.asteroids_group = None

        shot.seek_target(0.1)

        assert shot.target is enemy

        Shot.enemy_ships_group = None

    def test_shot_different_weapon_types(self, mock_pygame):
        """Test different weapon types have appropriate properties"""
        weapons = [WEAPON_STANDARD, WEAPON_LASER, WEAPON_MISSILE, WEAPON_SHOTGUN]

        for weapon_type in weapons:
            shot = Shot(0, 0, weapon_type)
            assert shot.shot_type == weapon_type
            assert shot.damage >= 1
            assert shot.radius >= 2

    def test_shot_draw_standard(self, mock_pygame):
        """Test drawing standard shot"""
        shot = Shot(100, 100, WEAPON_STANDARD)
        screen = pygame.Surface((800, 600))

        shot.draw(screen)  # Should not raise exception

    def test_shot_draw_laser(self, mock_pygame):
        """Test drawing laser shot"""
        shot = Shot(100, 100, WEAPON_LASER)
        shot.velocity = pygame.Vector2(100, 0)
        screen = pygame.Surface((800, 600))

        shot.draw(screen)

    def test_shot_draw_missile(self, mock_pygame):
        """Test drawing missile shot"""
        shot = Shot(100, 100, WEAPON_MISSILE)
        shot.velocity = pygame.Vector2(100, 0)
        screen = pygame.Surface((800, 600))

        shot.draw(screen)

    def test_shot_draw_shotgun(self, mock_pygame):
        """Test drawing shotgun shot"""
        shot = Shot(100, 100, WEAPON_SHOTGUN)
        screen = pygame.Surface((800, 600))

        shot.draw(screen)
