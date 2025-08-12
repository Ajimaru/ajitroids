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
        
    def test_boss_projectile_rotation(self, mock_pygame):
        """Test projectile rotates over time"""
        projectile = BossProjectile(0, 0, pygame.Vector2(0, 0))
        initial_rotation = projectile.rotation
        
        # Update for some time
        projectile.update(0.1)
        
        # Rotation should have changed
        assert projectile.rotation != initial_rotation
        
    def test_boss_projectile_lifetime_expiry(self, mock_pygame):
        """Test projectile gets killed when lifetime expires"""
        projectile = BossProjectile(0, 0, pygame.Vector2(0, 0))
        projectile.lifetime = 0.1
        projectile.kill = MagicMock()
        
        # Update past lifetime
        projectile.update(0.2)
        
        # Should be killed
        projectile.kill.assert_called_once()
        
    def test_boss_projectile_screen_bounds(self, mock_pygame):
        """Test projectile gets killed when leaving screen"""
        projectile = BossProjectile(0, 0, pygame.Vector2(-1000, 0))  # Fast left movement
        projectile.kill = MagicMock()
        
        # Update to move off screen
        projectile.update(1.0)
        
        # Should be killed when off screen
        projectile.kill.assert_called_once()
        
    def test_boss_projectile_damage_values(self, mock_pygame):
        """Test all projectile types have appropriate damage"""
        for proj_type in ["normal", "homing", "explosive"]:
            projectile = BossProjectile(0, 0, pygame.Vector2(0, 0), proj_type)
            assert projectile.damage >= 1
