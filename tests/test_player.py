import pytest
import pygame
from unittest.mock import patch, MagicMock
from modul.player import Player
from modul.constants import *


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


class TestPlayer:
    """Test suite for Player class functionality"""
    
    def test_player_initialization(self, mock_pygame):
        """Test player initializes with correct default values"""
        player = Player(100, 200)
        
        assert player.position.x == 100
        assert player.position.y == 200
        assert player.radius == PLAYER_RADIUS
        assert player.rotation == 0
        assert player.velocity == pygame.Vector2(0, 0)
        assert not player.invincible
        assert not player.shield_active
        assert player.current_weapon == WEAPON_STANDARD
        
    def test_player_respawn(self, mock_pygame):
        """Test player respawn resets position and state"""
        player = Player(100, 100)
        player.position = pygame.Vector2(0, 0)
        player.velocity = pygame.Vector2(50, 50)
        player.rotation = 45
        
        player.respawn()
        
        assert player.position.x == SCREEN_WIDTH / 2
        assert player.position.y == SCREEN_HEIGHT / 2
        assert player.velocity == pygame.Vector2(0, 0)
        assert player.rotation == 0
        assert player.invincible is True
        assert player.invincible_timer == 3.0
        
    def test_player_weapon_cycling(self, mock_pygame):
        """Test weapon cycling functionality"""
        player = Player(100, 100)
        
        # Give player some ammo
        player.weapons[WEAPON_LASER] = 5
        player.weapons[WEAPON_MISSILE] = 3
        
        initial_weapon = player.current_weapon
        player.cycle_weapon()
        
        # Should switch to next available weapon
        assert player.current_weapon != initial_weapon
        assert player.current_weapon in [WEAPON_LASER, WEAPON_MISSILE]
        
    def test_player_powerup_activation(self, mock_pygame):
        """Test powerup effects are applied correctly"""
        player = Player(100, 100)
        
        # Test shield powerup
        player.activate_powerup("shield")
        assert player.shield_active is True
        assert player.shield_timer == SHIELD_DURATION
        assert player.invincible is True
        
        # Test triple shot powerup
        player.activate_powerup("triple_shot")
        assert player.triple_shot_active is True
        assert player.triple_shot_timer == TRIPLE_SHOT_DURATION
        
    def test_player_update_timers(self, mock_pygame):
        """Test that timers are properly decremented"""
        player = Player(100, 100)
        
        # Set up timers
        player.invincible_timer = 1.0
        player.shield_timer = 1.0
        player.triple_shot_timer = 1.0
        
        # Update with 0.5 second delta
        player.update(0.5)
        
        # Timers should be decremented
        assert player.invincible_timer == 0.5
        assert player.shield_timer == 0.5
        assert player.triple_shot_timer == 0.5
        
    def test_player_weapon_auto_switch(self, mock_pygame):
        """Test automatic weapon switching when ammo runs out"""
        player = Player(100, 100)
        
        # Set current weapon to laser with no ammo
        player.current_weapon = WEAPON_LASER
        player.weapons[WEAPON_LASER] = 0
        player.weapons[WEAPON_MISSILE] = 5  # Alternative weapon
        
        # Try to shoot - should auto-switch
        with patch.object(player, 'sounds', MagicMock()):
            player.shoot()
            
        # Should have switched to missile or standard
        assert player.current_weapon != WEAPON_LASER
