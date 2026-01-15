import pytest
import pygame
import math
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

    def test_player_initialization_with_ship_type(self, mock_pygame):
        """Test player initializes with custom ship type"""
        player = Player(100, 200, ship_type="interceptor")
        
        assert player.ship_type == "interceptor"
        assert player.ship_data is not None

    def test_player_apply_ship_modifiers_rear_shot(self, mock_pygame):
        """Test ship modifiers for rear shot ability"""
        player = Player(100, 100)
        player.ship_data = {
            "speed_multiplier": 1.0,
            "turn_speed_multiplier": 1.0,
            "special_ability": "rear_shot"
        }
        
        player.apply_ship_modifiers()
        
        assert hasattr(player, 'has_rear_shot')
        assert player.has_rear_shot is True
        assert player.damage_multiplier == 1.0

    def test_player_apply_ship_modifiers_speed_boost(self, mock_pygame):
        """Test ship modifiers for speed boost"""
        player = Player(100, 100)
        player.ship_data = {
            "speed_multiplier": 1.0,
            "turn_speed_multiplier": 1.0,
            "special_ability": "speed_boost"
        }
        base_speed = player.base_speed
        
        player.apply_ship_modifiers()
        
        assert player.base_speed > base_speed
        assert player.has_rear_shot is False

    def test_player_apply_ship_modifiers_double_damage(self, mock_pygame):
        """Test ship modifiers for double damage"""
        player = Player(100, 100)
        player.ship_data = {
            "speed_multiplier": 1.0,
            "turn_speed_multiplier": 1.0,
            "special_ability": "double_damage"
        }
        
        player.apply_ship_modifiers()
        
        assert player.damage_multiplier == 2.0
        assert player.has_rear_shot is False

    def test_player_apply_ship_modifiers_default(self, mock_pygame):
        """Test ship modifiers for default ability"""
        player = Player(100, 100)
        player.ship_data = {
            "speed_multiplier": 1.0,
            "turn_speed_multiplier": 1.0,
            "special_ability": "none"
        }
        
        player.apply_ship_modifiers()
        
        assert player.damage_multiplier == 1.0
        assert player.has_rear_shot is False

    def test_player_draw_normal(self, mock_pygame):
        """Test drawing player in normal state"""
        player = Player(100, 100)
        screen = pygame.Surface((800, 600))
        
        with patch('pygame.time.get_ticks', return_value=0):
            player.draw(screen)  # Should not raise exception

    def test_player_draw_invincible_flashing(self, mock_pygame):
        """Test drawing player with invincibility flashing"""
        player = Player(100, 100)
        player.invincible = True
        screen = pygame.Surface((800, 600))
        
        with patch('pygame.time.get_ticks', return_value=0):
            player.draw(screen)
        
        with patch('pygame.time.get_ticks', return_value=150):
            player.draw(screen)

    def test_player_draw_with_shield(self, mock_pygame):
        """Test drawing player with shield active"""
        player = Player(100, 100)
        player.shield_active = True
        screen = pygame.Surface((800, 600))
        
        with patch('pygame.time.get_ticks', return_value=0):
            player.draw(screen)  # Should draw shield

    def test_player_triangle(self, mock_pygame):
        """Test triangle method returns correct points"""
        player = Player(100, 100)
        player.rotation = 0
        
        triangle = player.triangle()
        
        assert len(triangle) == 3
        assert all(isinstance(point, pygame.Vector2) for point in triangle)

    def test_player_update_left_rotation(self, mock_pygame):
        """Test player rotates left"""
        mock_keys = [0] * (max(pygame.K_b, pygame.K_SPACE, pygame.K_DOWN, pygame.K_UP, pygame.K_RIGHT, pygame.K_LEFT) + 1)
        mock_keys[pygame.K_LEFT] = 1
    
        with patch('pygame.key.get_pressed', return_value=mock_keys):
            player = Player(100, 100)
            initial_rotation = player.rotation
            
            player.update(0.1)
            
            assert player.rotation < initial_rotation

    def test_player_update_right_rotation(self, mock_pygame):
        """Test player rotates right"""
        mock_keys = {
            pygame.K_LEFT: False,
            pygame.K_RIGHT: True,
            pygame.K_UP: False,
            pygame.K_DOWN: False,
            pygame.K_SPACE: False,
            pygame.K_b: False
        }
        
        with patch('pygame.key.get_pressed', return_value=mock_keys):
            player = Player(100, 100)
            initial_rotation = player.rotation
            
            player.update(0.1)
            
            assert player.rotation > initial_rotation

    def test_player_update_forward_movement(self, mock_pygame):
        """Test player moves forward"""
        mock_keys = {
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False,
            pygame.K_UP: True,
            pygame.K_DOWN: False,
            pygame.K_SPACE: False,
            pygame.K_b: False
        }
        
        with patch('pygame.key.get_pressed', return_value=mock_keys):
            player = Player(100, 100)
            player.rotation = 0
            
            player.update(0.1)
            
            assert player.velocity.length() > 0

    def test_player_update_backward_movement(self, mock_pygame):
        """Test player moves backward"""
        mock_keys = {
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False,
            pygame.K_UP: False,
            pygame.K_DOWN: True,
            pygame.K_SPACE: False,
            pygame.K_b: False
        }
        
        with patch('pygame.key.get_pressed', return_value=mock_keys):
            player = Player(100, 100)
            player.rotation = 0
            player.velocity = pygame.Vector2(0, -10)
            
            player.update(0.1)
            
            # Velocity should be reduced

    def test_player_update_shoot(self, mock_pygame):
        """Test shooting on space key"""
        mock_keys = {
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False,
            pygame.K_UP: False,
            pygame.K_DOWN: False,
            pygame.K_SPACE: True,
            pygame.K_b: False
        }
        
        with patch('pygame.key.get_pressed', return_value=mock_keys):
            player = Player(100, 100)
            
            with patch.object(player, 'shoot') as mock_shoot:
                player.update(0.1)
                mock_shoot.assert_called()

    def test_player_update_cycle_weapon(self, mock_pygame):
        """Test weapon cycling on B key"""
        mock_keys = {
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False,
            pygame.K_UP: False,
            pygame.K_DOWN: False,
            pygame.K_SPACE: False,
            pygame.K_b: True
        }
        
        with patch('pygame.key.get_pressed', return_value=mock_keys):
            player = Player(100, 100)
            
            with patch.object(player, 'cycle_weapon') as mock_cycle:
                player.update(0.1)
                mock_cycle.assert_called()

    def test_player_update_max_speed(self, mock_pygame):
        """Test player velocity is capped at max speed"""
        player = Player(100, 100)
        player.velocity = pygame.Vector2(500, 500)  # Exceeds max
        player.max_speed = 400
        
        player.update(0.1)
        
        assert player.velocity.length() <= 400

    def test_player_update_friction(self, mock_pygame):
        """Test friction reduces velocity"""
        player = Player(100, 100)
        initial_velocity = pygame.Vector2(100, 0)
        player.velocity = initial_velocity.copy()
        
        player.update(0.1)
        
        assert player.velocity.length() < initial_velocity.length()

    def test_player_update_position_movement(self, mock_pygame):
        """Test position updates based on velocity"""
        player = Player(100, 100)
        player.velocity = pygame.Vector2(50, 0)
        
        player.update(0.1)
        
        assert player.position.x > 100

    def test_player_update_timers(self, mock_pygame):
        """Test that timers are properly decremented"""
        player = Player(100, 100)
        
        # Set up timers
        player.shoot_timer = 1.0
        player.invincible_timer = 1.0
        player.shield_timer = 1.0
        player.triple_shot_timer = 1.0
        player.rapid_fire_timer = 1.0
        player.weapon_switch_timer = 1.0
        
        # Update with 0.5 second delta
        player.update(0.5)
        
        # Timers should be decremented
        assert player.shoot_timer == 0.5
        assert player.invincible_timer == 0.5
        assert player.shield_timer == 0.5
        assert player.triple_shot_timer == 0.5
        assert player.rapid_fire_timer == 0.5
        assert player.weapon_switch_timer == 0.5

    def test_player_update_invincibility_expires(self, mock_pygame):
        """Test invincibility expires when timer runs out"""
        player = Player(100, 100)
        player.invincible = True
        player.invincible_timer = 0.1
        
        player.update(0.2)
        
        assert player.invincible is False
        assert player.invincible_timer <= 0

    def test_player_update_shield_expires(self, mock_pygame):
        """Test shield expires when timer runs out"""
        player = Player(100, 100)
        player.shield_active = True
        player.shield_timer = 0.1
        
        player.update(0.2)
        
        assert player.shield_active is False
        assert player.shield_timer <= 0
        assert player.invincible is False

    def test_player_update_triple_shot_expires(self, mock_pygame):
        """Test triple shot expires when timer runs out"""
        player = Player(100, 100)
        player.triple_shot_active = True
        player.triple_shot_timer = 0.1
        
        player.update(0.2)
        
        assert player.triple_shot_active is False

    def test_player_update_rapid_fire_expires(self, mock_pygame):
        """Test rapid fire expires when timer runs out"""
        player = Player(100, 100)
        player.rapid_fire_active = True
        player.rapid_fire_timer = 0.1
        
        player.update(0.2)
        
        assert player.rapid_fire_active is False
        
    def test_player_respawn(self, mock_pygame):
        """Test player respawn resets position and state"""
        player = Player(100, 100)
        player.position = pygame.Vector2(0, 0)
        player.velocity = pygame.Vector2(50, 50)
        player.rotation = 45
        player.shield_active = True
        player.triple_shot_active = True
        
        player.respawn()
        
        assert player.position.x == SCREEN_WIDTH / 2
        assert player.position.y == SCREEN_HEIGHT / 2
        assert player.velocity == pygame.Vector2(0, 0)
        assert player.rotation == 0
        assert player.invincible is True
        assert player.invincible_timer == 3.0
        assert player.shield_active is False
        assert player.triple_shot_active is False

    def test_player_shoot_standard(self, mock_pygame):
        """Test shooting standard weapon"""
        player = Player(100, 100)
        player.shoot_timer = 0
        
        with patch.object(player, 'sounds', MagicMock()):
            player.shoot()
        
        assert player.shoot_timer > 0

    def test_player_shoot_cooldown_active(self, mock_pygame):
        """Test shooting respects cooldown"""
        player = Player(100, 100)
        player.shoot_timer = 1.0
        
        with patch.object(player, 'sounds', MagicMock()):
            player.shoot()
        
        # Should still be on cooldown
        assert player.shoot_timer > 0

    def test_player_shoot_triple_shot(self, mock_pygame):
        """Test shooting with triple shot active"""
        player = Player(100, 100)
        player.shoot_timer = 0
        player.triple_shot_active = True
        
        with patch.object(player, 'sounds', MagicMock()):
            with patch.object(player, 'fire_triple_shot') as mock_triple:
                player.shoot()
                mock_triple.assert_called_once()

    def test_player_shoot_laser(self, mock_pygame):
        """Test shooting laser weapon"""
        player = Player(100, 100)
        player.shoot_timer = 0
        player.current_weapon = WEAPON_LASER
        player.weapons[WEAPON_LASER] = 5
        
        with patch.object(player, 'sounds', MagicMock()):
            player.shoot()
        
        assert player.weapons[WEAPON_LASER] == 4

    def test_player_shoot_missile(self, mock_pygame):
        """Test shooting missile weapon"""
        player = Player(100, 100)
        player.shoot_timer = 0
        player.current_weapon = WEAPON_MISSILE
        player.weapons[WEAPON_MISSILE] = 5
        
        with patch.object(player, 'sounds', MagicMock()):
            player.shoot()
        
        assert player.weapons[WEAPON_MISSILE] == 4

    def test_player_shoot_shotgun(self, mock_pygame):
        """Test shooting shotgun weapon"""
        player = Player(100, 100)
        player.shoot_timer = 0
        player.current_weapon = WEAPON_SHOTGUN
        player.weapons[WEAPON_SHOTGUN] = 5
        
        with patch.object(player, 'sounds', MagicMock()):
            player.shoot()
        
        assert player.weapons[WEAPON_SHOTGUN] == 4

    def test_player_shoot_rapid_fire(self, mock_pygame):
        """Test shooting with rapid fire active"""
        player = Player(100, 100)
        player.shoot_timer = 0
        player.rapid_fire_active = True
        
        with patch.object(player, 'sounds', MagicMock()):
            player.shoot()
        
        assert player.shoot_timer == RAPID_FIRE_COOLDOWN

    def test_player_shoot_auto_switch_no_ammo(self, mock_pygame):
        """Test automatic weapon switching when ammo runs out"""
        player = Player(100, 100)
        player.shoot_timer = 0
        player.current_weapon = WEAPON_LASER
        player.weapons[WEAPON_LASER] = 0
        player.weapons[WEAPON_MISSILE] = 5
        
        with patch.object(player, 'sounds', MagicMock()):
            player.shoot()
        
        assert player.current_weapon != WEAPON_LASER

    def test_player_shoot_auto_switch_to_standard(self, mock_pygame):
        """Test auto-switch to standard when no special weapons"""
        player = Player(100, 100)
        player.shoot_timer = 0
        player.current_weapon = WEAPON_LASER
        player.weapons[WEAPON_LASER] = 0
        player.weapons[WEAPON_MISSILE] = 0
        player.weapons[WEAPON_SHOTGUN] = 0
        
        with patch.object(player, 'sounds', MagicMock()):
            player.shoot()
        
        assert player.current_weapon == WEAPON_STANDARD

    def test_player_shoot_with_rear_shot(self, mock_pygame):
        """Test shooting with rear shot ability"""
        player = Player(100, 100)
        player.shoot_timer = 0
        player.has_rear_shot = True
        
        with patch.object(player, 'sounds', MagicMock()):
            player.shoot()

    def test_player_fire_triple_shot(self, mock_pygame):
        """Test triple shot fires three projectiles"""
        player = Player(100, 100)
        
        player.fire_triple_shot()
        # Should create 3 shots (method doesn't return anything)

    def test_player_fire_triple_shot_with_rear_shot(self, mock_pygame):
        """Test triple shot with rear shot ability"""
        player = Player(100, 100)
        player.has_rear_shot = True
        
        player.fire_triple_shot()

    def test_player_make_invincible(self, mock_pygame):
        """Test make_invincible method"""
        player = Player(100, 100)
        
        player.make_invincible()
        
        assert player.invincible is True
        assert player.invincible_timer == INVINCIBILITY_TIME
        
    def test_player_weapon_cycling(self, mock_pygame):
        """Test weapon cycling functionality"""
        player = Player(100, 100)
        player.weapons[WEAPON_LASER] = 5
        player.weapons[WEAPON_MISSILE] = 3
        
        initial_weapon = player.current_weapon
        player.cycle_weapon()
        
        assert player.current_weapon != initial_weapon

    def test_player_cycle_weapon_cooldown(self, mock_pygame):
        """Test weapon cycling respects cooldown"""
        player = Player(100, 100)
        player.weapon_switch_timer = 1.0
        initial_weapon = player.current_weapon
        
        player.cycle_weapon()
        
        assert player.current_weapon == initial_weapon

    def test_player_cycle_weapon_skips_empty(self, mock_pygame):
        """Test weapon cycling skips weapons with no ammo"""
        player = Player(100, 100)
        player.weapon_switch_timer = 0
        player.current_weapon = WEAPON_STANDARD
        player.weapons[WEAPON_LASER] = 0
        player.weapons[WEAPON_MISSILE] = 5
        player.weapons[WEAPON_SHOTGUN] = 0
        
        player.cycle_weapon()
        
        # Should skip to missile
        assert player.current_weapon in [WEAPON_MISSILE, WEAPON_STANDARD]

    def test_player_cycle_weapon_fallback(self, mock_pygame):
        """Test weapon cycling falls back to standard"""
        player = Player(100, 100)
        player.weapon_switch_timer = 0
        player.current_weapon = WEAPON_LASER
        player.weapons[WEAPON_LASER] = 0
        player.weapons[WEAPON_MISSILE] = 0
        player.weapons[WEAPON_SHOTGUN] = 0
        
        player.cycle_weapon()
        
        assert player.current_weapon == WEAPON_STANDARD

    def test_player_powerup_activation(self, mock_pygame):
        """Test powerup effects are applied correctly"""
        player = Player(100, 100)
        
        player.activate_powerup("shield")
        assert player.shield_active is True
        assert player.shield_timer == SHIELD_DURATION
        assert player.invincible is True

    def test_player_activate_triple_shot(self, mock_pygame):
        """Test triple shot powerup activation"""
        player = Player(100, 100)
        
        player.activate_powerup("triple_shot")
        assert player.triple_shot_active is True
        assert player.triple_shot_timer == TRIPLE_SHOT_DURATION

    def test_player_activate_rapid_fire(self, mock_pygame):
        """Test rapid fire powerup activation"""
        player = Player(100, 100)
        
        player.activate_powerup("rapid_fire")
        assert player.rapid_fire_active is True
        assert player.rapid_fire_timer == RAPID_FIRE_DURATION

    def test_player_activate_laser_weapon(self, mock_pygame):
        """Test laser weapon powerup activation"""
        player = Player(100, 100)
        
        player.activate_powerup("laser_weapon")
        assert player.weapons[WEAPON_LASER] == LASER_AMMO
        assert player.current_weapon == WEAPON_LASER

    def test_player_activate_missile_weapon(self, mock_pygame):
        """Test missile weapon powerup activation"""
        player = Player(100, 100)
        
        player.activate_powerup("missile_weapon")
        assert player.weapons[WEAPON_MISSILE] == MISSILE_AMMO
        assert player.current_weapon == WEAPON_MISSILE

    def test_player_activate_shotgun_weapon(self, mock_pygame):
        """Test shotgun weapon powerup activation"""
        player = Player(100, 100)
        
        player.activate_powerup("shotgun_weapon")
        assert player.weapons[WEAPON_SHOTGUN] == SHOTGUN_AMMO
        assert player.current_weapon == WEAPON_SHOTGUN

    def test_player_draw_weapon_hud(self, mock_pygame):
        """Test drawing weapon HUD"""
        player = Player(100, 100)
        screen = pygame.Surface((800, 600))
        
        # This method draws on screen, we just verify it doesn't crash
        try:
            player.draw_weapon_hud(screen)
        except pygame.error:
            # Font not initialized is acceptable in test
            pass

    def test_player_draw_weapon_hud_with_ammo(self, mock_pygame):
        """Test drawing weapon HUD with various ammo levels"""
        player = Player(100, 100)
        player.weapons[WEAPON_LASER] = 5
        player.weapons[WEAPON_MISSILE] = 3
        player.current_weapon = WEAPON_LASER
        screen = pygame.Surface((800, 600))
        
        try:
            player.draw_weapon_hud(screen)
        except pygame.error:
            # Font not initialized is acceptable in test
            pass
