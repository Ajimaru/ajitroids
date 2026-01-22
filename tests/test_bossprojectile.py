"""Tests for boss projectiles and their behavior."""

from unittest.mock import patch, MagicMock

import pytest
import pygame

from modul.bossprojectile import BossProjectile
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
