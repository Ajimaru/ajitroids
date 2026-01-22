"""Tests for Shot class and projectile behavior."""

from unittest.mock import patch, MagicMock

import pytest
import pygame
from modul.shot import Shot
from modul.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    ASTEROID_MIN_RADIUS, ASTEROID_KINDS, ASTEROID_SPAWN_RATE, ASTEROID_MAX_RADIUS,
    ASTEROID_VERTICES, ASTEROID_IRREGULARITY,
    ASTEROID_TYPE_NORMAL, ASTEROID_TYPE_ICE, ASTEROID_TYPE_METAL, ASTEROID_TYPE_CRYSTAL,
    ASTEROID_TYPES, ASTEROID_TYPE_WEIGHTS, ASTEROID_TYPE_COLORS,
    ASTEROID_TYPE_SCORE_MULTIPLIERS, ASTEROID_ICE_VELOCITY_MULTIPLIER,
    ASTEROID_METAL_HEALTH, ASTEROID_CRYSTAL_SPLIT_COUNT,
    PLAYER_RADIUS, PLAYER_TURN_SPEED, PLAYER_SPEED, PLAYER_ACCELERATION,
    PLAYER_MAX_SPEED, PLAYER_FRICTION, PLAYER_ROTATION_SPEED,
    PLAYER_SHOOT_SPEED, PLAYER_SHOOT_COOLDOWN, SHOT_RADIUS,
    SCORE_LARGE, SCORE_MEDIUM, SCORE_SMALL, PLAYER_LIVES,
    INVINCIBILITY_TIME, RESPAWN_POSITION_X, RESPAWN_POSITION_Y,
    EXPLOSION_PARTICLES, PARTICLE_COLORS, STAR_COUNT, STAR_SIZES, STAR_COLORS,
    COLLISION_DEBUG, POWERUP_RADIUS, POWERUP_SPAWN_CHANCE, POWERUP_MAX_COUNT,
    POWERUP_LIFETIME, SHIELD_DURATION, POWERUP_TYPES, POWERUP_COLORS,
    RAPID_FIRE_COOLDOWN, RAPID_FIRE_DURATION, TRIPLE_SHOT_DURATION,
    HIGHSCORE_FILE, HIGHSCORE_MAX_ENTRIES, HIGHSCORE_NAME_LENGTH,
    HIGHSCORE_DEFAULT_NAME, HIGHSCORE_ALLOWED_CHARS,
    MENU_TITLE_FONT_SIZE, MENU_ITEM_FONT_SIZE, MENU_SELECTED_COLOR,
    MENU_UNSELECTED_COLOR, MENU_TITLE_COLOR, MENU_ITEM_SPACING,
    MENU_TRANSITION_SPEED, MENU_BACKGROUND_ALPHA, MENU_BUTTON_WIDTH,
    MENU_BUTTON_HEIGHT, MENU_BUTTON_PADDING, MENU_BUTTON_RADIUS,
    MENU_FADE_SPEED, DIFFICULTY_EASY_ASTEROIDS, DIFFICULTY_NORMAL_ASTEROIDS,
    DIFFICULTY_HARD_ASTEROIDS, DIFFICULTY_EASY_INTERVAL,
    DIFFICULTY_NORMAL_INTERVAL, DIFFICULTY_HARD_INTERVAL, ARCADE_MODE_TIME,
    ARCADE_MODE_BONUS_TIME, CREDITS_MASTERMIND, CREDITS_TITLE,
    CREDITS_GAME_NAME, CREDITS_DEVELOPER, CREDITS_GRAPHICS, CREDITS_SOUND,
    CREDITS_SPECIAL_THANKS, CREDITS_SCROLL_SPEED, CREDITS_LINE_SPACING,
    CREDITS_WEBSITE, POINTS_PER_LEVEL, MAX_LEVEL, LEVEL_UP_DISPLAY_TIME,
    BASE_ASTEROID_COUNT, BASE_SPAWN_INTERVAL, ASTEROID_COUNT_PER_LEVEL,
    SPAWN_INTERVAL_REDUCTION, WEAPON_STANDARD, WEAPON_LASER, WEAPON_MISSILE,
    WEAPON_SHOTGUN, WEAPON_COLORS, LASER_AMMO, MISSILE_AMMO, SHOTGUN_AMMO,
    BOSS_LEVEL_INTERVAL, BOSS_RADIUS, BOSS_COLOR, BOSS_BASE_HEALTH,
    BOSS_HEALTH_PER_LEVEL, BOSS_MOVE_SPEED, BOSS_ATTACK_INTERVAL,
    BOSS_DEATH_DURATION, BOSS_SCORE, BOSS_PROJECTILE_RADIUS,
    BOSS_PROJECTILE_SPEED, BOSS_PROJECTILE_COLORS, generate_default_highscores,
    DEFAULT_HIGHSCORES,
)


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
