import pytest
import pygame
from unittest.mock import patch, MagicMock
from modul.shot import Shot
from modul.constants import *


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
        
    def test_shot_update_movement(self, mock_pygame):
        """Test shot moves according to velocity"""
        shot = Shot(0, 0)
        shot.velocity = pygame.Vector2(100, 0)  # 100 pixels/second right
        
        # Update for 0.1 seconds
        shot.update(0.1)
        
        # Should move 10 pixels right
        assert shot.position.x == 10
        assert shot.position.y == 0
        
    def test_shot_lifetime_expiry(self, mock_pygame):
        """Test shot gets killed when lifetime expires"""
        shot = Shot(0, 0)
        shot.lifetime = 0.5
        shot.kill = MagicMock()
        
        # Update past lifetime
        shot.update(1.0)
        
        # Should be killed
        shot.kill.assert_called_once()
        
    def test_shot_different_weapon_types(self, mock_pygame):
        """Test different weapon types have appropriate properties"""
        weapons = [WEAPON_STANDARD, WEAPON_LASER, WEAPON_MISSILE, WEAPON_SHOTGUN]
        
        for weapon_type in weapons:
            shot = Shot(0, 0, weapon_type)
            assert shot.shot_type == weapon_type
            assert shot.damage >= 1
            assert shot.radius >= 2
