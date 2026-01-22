"""Tests for powerup effects and interactions with player."""

from unittest.mock import patch, MagicMock

import pytest
import pygame
from modul.player import Player
from modul.powerup import PowerUp
from modul.constants import (
    ARCADE_MODE_BONUS_TIME, ARCADE_MODE_TIME, ASTEROID_COUNT_PER_LEVEL,
    ASTEROID_CRYSTAL_SPLIT_COUNT, ASTEROID_ICE_VELOCITY_MULTIPLIER,
    ASTEROID_IRREGULARITY, ASTEROID_KINDS, ASTEROID_MAX_RADIUS,
    ASTEROID_METAL_HEALTH, ASTEROID_MIN_RADIUS, ASTEROID_SPAWN_RATE,
    ASTEROID_TYPES, ASTEROID_TYPE_COLORS, ASTEROID_TYPE_CRYSTAL,
    ASTEROID_TYPE_ICE, ASTEROID_TYPE_METAL, ASTEROID_TYPE_NORMAL,
    ASTEROID_TYPE_SCORE_MULTIPLIERS, ASTEROID_TYPE_WEIGHTS, ASTEROID_VERTICES,
    BASE_ASTEROID_COUNT, BASE_SPAWN_INTERVAL, BOSS_ATTACK_INTERVAL,
    BOSS_BASE_HEALTH, BOSS_COLOR, BOSS_DEATH_DURATION, BOSS_HEALTH_PER_LEVEL,
    BOSS_LEVEL_INTERVAL, BOSS_MOVE_SPEED, BOSS_PROJECTILE_COLORS,
    BOSS_PROJECTILE_RADIUS, BOSS_PROJECTILE_SPEED, BOSS_RADIUS, BOSS_SCORE,
    COLLISION_DEBUG, CREDITS_DEVELOPER, CREDITS_GAME_NAME, CREDITS_GRAPHICS,
    CREDITS_LINE_SPACING, CREDITS_MASTERMIND, CREDITS_SCROLL_SPEED,
    CREDITS_SOUND, CREDITS_SPECIAL_THANKS, CREDITS_TITLE, CREDITS_WEBSITE,
    DEFAULT_HIGHSCORES, DIFFICULTY_EASY_ASTEROIDS, DIFFICULTY_EASY_INTERVAL,
    DIFFICULTY_HARD_ASTEROIDS, DIFFICULTY_HARD_INTERVAL,
    DIFFICULTY_NORMAL_ASTEROIDS, DIFFICULTY_NORMAL_INTERVAL, EXPLOSION_PARTICLES,
    HIGHSCORE_ALLOWED_CHARS, HIGHSCORE_DEFAULT_NAME, HIGHSCORE_FILE,
    HIGHSCORE_MAX_ENTRIES, HIGHSCORE_NAME_LENGTH, INVINCIBILITY_TIME,
    LASER_AMMO, LEVEL_UP_DISPLAY_TIME, MAX_LEVEL, MENU_BACKGROUND_ALPHA,
    MENU_BUTTON_HEIGHT, MENU_BUTTON_PADDING, MENU_BUTTON_RADIUS,
    MENU_BUTTON_WIDTH, MENU_FADE_SPEED, MENU_ITEM_FONT_SIZE,
    MENU_ITEM_SPACING, MENU_SELECTED_COLOR, MENU_TITLE_COLOR,
    MENU_TITLE_FONT_SIZE, MENU_TRANSITION_SPEED, MENU_UNSELECTED_COLOR,
    MISSILE_AMMO, PARTICLE_COLORS, PLAYER_ACCELERATION, PLAYER_FRICTION,
    PLAYER_LIVES, PLAYER_MAX_SPEED, PLAYER_RADIUS, PLAYER_ROTATION_SPEED,
    PLAYER_SHOOT_COOLDOWN, PLAYER_SHOOT_SPEED, PLAYER_SPEED, PLAYER_TURN_SPEED,
    POINTS_PER_LEVEL, POWERUP_COLORS, POWERUP_LIFETIME, POWERUP_MAX_COUNT,
    POWERUP_RADIUS, POWERUP_SPAWN_CHANCE, POWERUP_TYPES, RAPID_FIRE_COOLDOWN,
    RAPID_FIRE_DURATION, RESPAWN_POSITION_X, RESPAWN_POSITION_Y, SCORE_LARGE,
    SCORE_MEDIUM, SCORE_SMALL, SCREEN_HEIGHT, SCREEN_WIDTH, SHIELD_DURATION,
    SHOTGUN_AMMO, SHOT_RADIUS, SPAWN_INTERVAL_REDUCTION, STAR_COLORS,
    STAR_COUNT, STAR_SIZES, TRIPLE_SHOT_DURATION, WEAPON_COLORS,
    WEAPON_LASER, WEAPON_MISSILE, WEAPON_SHOTGUN, WEAPON_STANDARD,
    generate_default_highscores, DEFAULT_HIGHSCORES,
)


@pytest.fixture
def mock_pygame():
    """Mock pygame components for isolated testing"""
    # Create a mock for key states that returns False for all keys
    mock_keys = {
        pygame.K_LEFT: False,
        pygame.K_RIGHT: False,
        pygame.K_UP: False,
        pygame.K_DOWN: False,
        pygame.K_SPACE: False,
        pygame.K_b: False
    }
    with patch('pygame.mixer.init'), \
         patch('pygame.key.get_pressed', return_value=mock_keys), \
         patch('pygame.sprite.Sprite.__init__'):
        yield


class TestPowerupEffects:
    """Test suite for powerup effects on player"""

    def test_shield_powerup_effect(self, mock_pygame):
        """Test shield powerup activates protection"""
        player = Player(0, 0)

        # Apply shield powerup
        player.activate_powerup("shield")

        assert player.shield_active is True
        assert player.shield_timer == SHIELD_DURATION
        assert player.invincible is True

    def test_triple_shot_powerup_effect(self, mock_pygame):
        """Test triple shot powerup enables multiple shots"""
        player = Player(0, 0)

        # Apply triple shot powerup
        player.activate_powerup("triple_shot")

        assert player.triple_shot_active is True
        assert player.triple_shot_timer == TRIPLE_SHOT_DURATION

    def test_rapid_fire_powerup_effect(self, mock_pygame):
        """Test rapid fire powerup reduces cooldown"""
        player = Player(0, 0)

        # Apply rapid fire powerup
        player.activate_powerup("rapid_fire")

        assert player.rapid_fire_active is True
        assert player.rapid_fire_timer == RAPID_FIRE_DURATION

    def test_laser_weapon_powerup_effect(self, mock_pygame):
        """Test laser weapon powerup gives ammo and switches weapon"""
        player = Player(0, 0)
        initial_laser_ammo = player.weapons[WEAPON_LASER]

        # Apply laser weapon powerup
        player.activate_powerup("laser_weapon")

        assert player.weapons[WEAPON_LASER] > initial_laser_ammo
        assert player.current_weapon == WEAPON_LASER

    def test_missile_weapon_powerup_effect(self, mock_pygame):
        """Test missile weapon powerup gives ammo and switches weapon"""
        player = Player(0, 0)
        initial_missile_ammo = player.weapons[WEAPON_MISSILE]

        # Apply missile weapon powerup
        player.activate_powerup("missile_weapon")

        assert player.weapons[WEAPON_MISSILE] > initial_missile_ammo
        assert player.current_weapon == WEAPON_MISSILE

    def test_shotgun_weapon_powerup_effect(self, mock_pygame):
        """Test shotgun weapon powerup gives ammo and switches weapon"""
        player = Player(0, 0)
        initial_shotgun_ammo = player.weapons[WEAPON_SHOTGUN]

        # Apply shotgun weapon powerup
        player.activate_powerup("shotgun_weapon")

        assert player.weapons[WEAPON_SHOTGUN] > initial_shotgun_ammo
        assert player.current_weapon == WEAPON_SHOTGUN

    def test_powerup_timer_expiration(self, mock_pygame):
        """Test powerup effects expire after time"""
        player = Player(0, 0)

        # Activate shield
        player.activate_powerup("shield")
        assert player.shield_active is True

        # Simulate time passing to expire shield (set timer to small positive value, then update)
        player.shield_timer = 0.01  # Very small positive value
        player.update(0.1)  # Update with larger delta to expire it

        assert player.shield_active is False
        assert player.invincible is False

    def test_multiple_powerup_stacking(self, mock_pygame):
        """Test multiple powerups can be active simultaneously"""
        player = Player(0, 0)

        # Apply multiple powerups
        player.activate_powerup("shield")
        player.activate_powerup("triple_shot")
        player.activate_powerup("rapid_fire")

        assert player.shield_active is True
        assert player.triple_shot_active is True
        assert player.rapid_fire_active is True
