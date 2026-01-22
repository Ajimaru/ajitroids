"""Tests for powerup effects and interactions with player."""

from unittest.mock import patch

import pygame
import pytest

from modul.constants import (RAPID_FIRE_DURATION, SHIELD_DURATION,
                             TRIPLE_SHOT_DURATION, WEAPON_LASER,
                             WEAPON_MISSILE, WEAPON_SHOTGUN)
from modul.player import Player


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
