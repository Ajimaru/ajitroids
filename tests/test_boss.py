import pytest
import pygame
from unittest.mock import patch, MagicMock
from modul.boss import Boss
from modul.constants import *


@pytest.fixture
def mock_pygame():
    """Mock pygame components for isolated testing"""
    with patch('pygame.sprite.Sprite.__init__'), \
         patch('modul.boss.Particle'):
        yield


class TestBoss:
    """Test suite for Boss class functionality"""
    
    def test_boss_initialization(self, mock_pygame):
        """Test boss initializes with correct properties for level"""
        level = 50  # Use level 50 to get boss_level 5
        boss = Boss(level)
        
        expected_boss_level = level // 10
        expected_health = BOSS_BASE_HEALTH + (expected_boss_level - 1) * BOSS_HEALTH_PER_LEVEL
        
        assert boss.boss_level == expected_boss_level
        assert boss.max_health == expected_health
        assert boss.health == boss.max_health
        assert boss.radius == BOSS_RADIUS
        assert boss.movement_phase == "center"
        assert boss.death_timer < 0  # Not dead yet
        
    def test_boss_health_scaling(self, mock_pygame):
        """Test boss health scales correctly with level"""
        level_10_boss = Boss(10)  # boss_level = 1
        level_100_boss = Boss(100)  # boss_level = 10
        
        expected_level_10_health = BOSS_BASE_HEALTH + (1 - 1) * BOSS_HEALTH_PER_LEVEL  # 20
        expected_level_100_health = BOSS_BASE_HEALTH + (10 - 1) * BOSS_HEALTH_PER_LEVEL  # 20 + 90 = 110
        
        assert level_10_boss.max_health == expected_level_10_health
        assert level_100_boss.max_health == expected_level_100_health
        assert level_100_boss.max_health > level_10_boss.max_health
        
    def test_boss_take_damage(self, mock_pygame):
        """Test boss takes damage and dies when health reaches zero"""
        boss = Boss(1)
        initial_health = boss.health
        
        # Deal some damage
        is_defeated = boss.take_damage(5)
        assert boss.health == initial_health - 5
        assert not is_defeated
        
        # Deal fatal damage
        is_defeated = boss.take_damage(boss.health)
        assert boss.health <= 0
        assert is_defeated
        assert boss.death_timer >= 0
        
    def test_boss_movement_phases(self, mock_pygame):
        """Test boss cycles through movement phases"""
        boss = Boss(1)
        player_pos = pygame.Vector2(100, 100)
        
        # Initially in center phase
        assert boss.movement_phase == "center"
        
        # Simulate time progression to trigger phase changes
        boss.movement_timer = 4.0  # Beyond center phase duration
        boss._update_movement(0.1, player_pos)
        
        # Should transition to next phase
        assert boss.movement_phase in ["random", "chase"]
        
    def test_boss_attack_generation(self, mock_pygame):
        """Test boss generates attacks at intervals"""
        boss = Boss(1)
        
        # Set up for attack
        boss.attack_timer = 0  # Ready to attack
        
        attack = boss.attack()
        
        # Should return attack data
        assert attack is not None
        assert "type" in attack
        assert "count" in attack
        assert attack["type"] in ["circle", "spiral", "targeted"]
        
    def test_boss_death_sequence(self, mock_pygame):
        """Test boss death sequence and particle emission"""
        boss = Boss(1)
        boss.kill = MagicMock()
        
        # Kill the boss
        boss.take_damage(boss.health)
        
        # Update through death sequence
        boss.update(BOSS_DEATH_DURATION + 0.1)
        
        # Should be killed after death duration
        boss.kill.assert_called_once()
        
    def test_boss_screen_constraints(self, mock_pygame):
        """Test boss stays within screen boundaries"""
        boss = Boss(1)
        
        # Move boss outside screen
        boss.position.x = -100
        boss.position.y = SCREEN_HEIGHT + 100
        
        boss._constrain_to_screen()
        
        # Should be constrained to screen
        assert boss.position.x >= boss.radius
        assert boss.position.y <= SCREEN_HEIGHT - boss.radius
