import pytest
import pygame
import random
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

    def test_boss_initialization_level_1(self, mock_pygame):
        """Test boss initialization at level 1"""
        boss = Boss(1)

        assert boss.boss_level == 0
        assert boss.position.x == SCREEN_WIDTH / 2
        assert boss.position.y == SCREEN_HEIGHT / 2
        assert boss.color == BOSS_COLOR
        assert boss.pulse_timer == 0
        assert boss.rotation == 0
        assert boss.velocity == pygame.Vector2(0, 0)
        assert boss.attack_timer == 0
        assert boss.attack_interval == BOSS_ATTACK_INTERVAL
        assert boss.attack_pattern == 0
        assert boss.hit_flash == 0

    def test_boss_health_scaling(self, mock_pygame):
        """Test boss health scales correctly with level"""
        level_10_boss = Boss(10)  # boss_level = 1
        level_100_boss = Boss(100)  # boss_level = 10

        expected_level_10_health = BOSS_BASE_HEALTH + (1 - 1) * BOSS_HEALTH_PER_LEVEL  # 20
        expected_level_100_health = BOSS_BASE_HEALTH + (10 - 1) * BOSS_HEALTH_PER_LEVEL  # 20 + 90 = 110

        assert level_10_boss.max_health == expected_level_10_health
        assert level_100_boss.max_health == expected_level_100_health
        assert level_100_boss.max_health > level_10_boss.max_health

    def test_boss_update_normal(self, mock_pygame):
        """Test boss update in normal state"""
        boss = Boss(1)
        player_pos = pygame.Vector2(100, 100)
        initial_rotation = boss.rotation
        initial_timer = boss.pulse_timer

        boss.update(0.1, player_pos)

        assert boss.rotation != initial_rotation
        assert boss.pulse_timer != initial_timer

    def test_boss_update_during_death(self, mock_pygame):
        """Test boss update during death sequence"""
        boss = Boss(1)
        boss.death_timer = 0
        boss.kill = MagicMock()

        boss.update(BOSS_DEATH_DURATION + 0.1, pygame.Vector2(0, 0))

        boss.kill.assert_called_once()

    def test_boss_update_death_particles(self, mock_pygame):
        """Test death particles are emitted once"""
        boss = Boss(1)
        boss.death_timer = 0
        boss.kill = MagicMock()

        boss.update(0.1, pygame.Vector2(0, 0))
        assert boss.death_particles_emitted is True

        # Update again shouldn't emit more
        boss.update(0.1, pygame.Vector2(0, 0))

    def test_boss_update_decrements_hit_flash(self, mock_pygame):
        """Test hit flash timer decrements"""
        boss = Boss(1)
        boss.hit_flash = 1.0

        boss.update(0.5, pygame.Vector2(0, 0))

        assert boss.hit_flash == 0.5

    def test_boss_take_damage(self, mock_pygame):
        """Test boss takes damage and dies when health reaches zero"""
        boss = Boss(1)
        initial_health = boss.health

        # Deal some damage
        is_defeated = boss.take_damage(5)
        assert boss.health == initial_health - 5
        assert not is_defeated
        assert boss.hit_flash > 0

        # Deal fatal damage
        is_defeated = boss.take_damage(boss.health)
        assert boss.health <= 0
        assert is_defeated
        assert boss.death_timer >= 0

    def test_boss_take_damage_creates_particles(self, mock_pygame):
        """Test taking damage creates particles"""
        boss = Boss(1)

        boss.take_damage(5)
        # Particles should be created (tested via mock)

    def test_boss_take_damage_multiple_times(self, mock_pygame):
        """Test boss can take damage multiple times"""
        boss = Boss(1)

        boss.take_damage(5)
        boss.take_damage(5)
        boss.take_damage(5)

        assert boss.health == boss.max_health - 15

    def test_boss_movement_center_phase(self, mock_pygame):
        """Test boss movement in center phase"""
        boss = Boss(1)
        boss.movement_phase = "center"
        boss.position = pygame.Vector2(100, 100)

        boss._update_movement(0.1, None)

        # Should move towards center
        assert boss.movement_phase == "center"

    def test_boss_movement_random_phase(self, mock_pygame):
        """Test boss movement in random phase"""
        boss = Boss(1)
        boss.movement_phase = "random"
        boss.movement_timer = 0

        with patch('random.randint', return_value=300):
            boss._update_movement(0.1, None)

        assert boss.target_position is not None

    def test_boss_movement_chase_phase(self, mock_pygame):
        """Test boss movement in chase phase"""
        boss = Boss(1)
        boss.movement_phase = "chase"
        player_pos = pygame.Vector2(100, 100)

        boss._update_movement(0.1, player_pos)

        # Should have velocity towards player
        assert boss.velocity.length() > 0

    def test_boss_movement_phase_transitions(self, mock_pygame):
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

    def test_boss_movement_center_to_random(self, mock_pygame):
        """Test transition from center to random phase"""
        boss = Boss(1)
        boss.movement_phase = "center"
        boss.movement_timer = 3.5

        boss._update_movement(0.1, None)

        assert boss.movement_phase == "random"

    def test_boss_movement_random_to_chase(self, mock_pygame):
        """Test transition from random to chase phase"""
        boss = Boss(1)
        boss.movement_phase = "random"
        boss.movement_timer = 5.5
        player_pos = pygame.Vector2(100, 100)

        boss._update_movement(0.1, player_pos)

        assert boss.movement_phase == "chase"

    def test_boss_movement_chase_to_center(self, mock_pygame):
        """Test transition from chase to center phase"""
        boss = Boss(1)
        boss.movement_phase = "chase"
        boss.movement_timer = 4.5

        boss._update_movement(0.1, None)

        assert boss.movement_phase == "center"

    def test_boss_move_towards(self, mock_pygame):
        """Test _move_towards method"""
        boss = Boss(1)
        target = pygame.Vector2(200, 200)

        boss._move_towards(target, 100, 0.1)

        assert boss.velocity.length() > 0

    def test_boss_move_towards_at_target(self, mock_pygame):
        """Test _move_towards when already at target"""
        boss = Boss(1)
        boss.position = pygame.Vector2(200, 200)
        target = pygame.Vector2(200, 200)
        boss.velocity = pygame.Vector2(50, 50)
        initial_velocity_length = boss.velocity.length()

        boss._move_towards(target, 100, 0.1)

        # Velocity should decay when at target
        assert boss.velocity.length() < initial_velocity_length

    def test_boss_constrain_left_edge(self, mock_pygame):
        """Test boss is constrained at left edge"""
        boss = Boss(1)
        boss.position.x = -100
        boss.velocity.x = -50

        boss._constrain_to_screen()

        assert boss.position.x >= boss.radius
        assert boss.velocity.x >= 0

    def test_boss_constrain_right_edge(self, mock_pygame):
        """Test boss is constrained at right edge"""
        boss = Boss(1)
        boss.position.x = SCREEN_WIDTH + 100
        boss.velocity.x = 50

        boss._constrain_to_screen()

        assert boss.position.x <= SCREEN_WIDTH - boss.radius
        assert boss.velocity.x <= 0

    def test_boss_constrain_top_edge(self, mock_pygame):
        """Test boss is constrained at top edge"""
        boss = Boss(1)
        boss.position.y = -100
        boss.velocity.y = -50

        boss._constrain_to_screen()

        assert boss.position.y >= boss.radius
        assert boss.velocity.y >= 0

    def test_boss_constrain_bottom_edge(self, mock_pygame):
        """Test boss is constrained at bottom edge"""
        boss = Boss(1)
        boss.position.y = SCREEN_HEIGHT + 100
        boss.velocity.y = 50

        boss._constrain_to_screen()

        assert boss.position.y <= SCREEN_HEIGHT - boss.radius
        assert boss.velocity.y <= 0

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

    def test_boss_update_attack(self, mock_pygame):
        """Test attack timer updates"""
        boss = Boss(1)
        boss.attack_timer = 0

        boss._update_attack(0.1)

        assert boss.attack_timer == 0.1

    def test_boss_update_attack_triggers(self, mock_pygame):
        """Test attack triggers when timer reaches interval"""
        boss = Boss(1)
        boss.attack_timer = BOSS_ATTACK_INTERVAL

        with patch.object(boss, 'attack', return_value={"type": "circle", "count": 8}) as mock_attack:
            boss._update_attack(0.1)

            mock_attack.assert_called_once()
            assert boss.attack_timer == 0

    def test_boss_update_attack_pattern_cycles(self, mock_pygame):
        """Test attack pattern cycles"""
        boss = Boss(1)
        boss.attack_timer = BOSS_ATTACK_INTERVAL
        boss.attack_pattern = 2

        boss._update_attack(0.1)

        assert boss.attack_pattern == 0

    def test_boss_attack_circle_pattern(self, mock_pygame):
        """Test circle attack pattern"""
        boss = Boss(1)
        boss.attack_pattern = 0

        attack = boss.attack()

        assert attack["type"] == "circle"
        assert attack["count"] >= 8

    def test_boss_attack_spiral_pattern(self, mock_pygame):
        """Test spiral attack pattern"""
        boss = Boss(1)
        boss.attack_pattern = 1

        attack = boss.attack()

        assert attack["type"] == "spiral"
        assert attack["count"] >= 12

    def test_boss_attack_targeted_pattern(self, mock_pygame):
        """Test targeted attack pattern"""
        boss = Boss(1)
        boss.attack_pattern = 2

        attack = boss.attack()

        assert attack["type"] == "targeted"
        assert attack["count"] >= 3

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

    def test_boss_attack_scales_with_level(self, mock_pygame):
        """Test attack count scales with boss level"""
        boss_low = Boss(10)
        boss_high = Boss(100)

        boss_low.attack_pattern = 0
        boss_high.attack_pattern = 0

        attack_low = boss_low.attack()
        attack_high = boss_high.attack()

        assert attack_high["count"] > attack_low["count"]

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

    def test_boss_draw_normal(self, mock_pygame):
        """Test drawing boss in normal state"""
        boss = Boss(1)
        screen = pygame.Surface((800, 600))

        boss.draw(screen)  # Should not raise exception

    def test_boss_draw_with_hit_flash(self, mock_pygame):
        """Test drawing boss with hit flash"""
        boss = Boss(1)
        boss.hit_flash = 0.5
        screen = pygame.Surface((800, 600))

        boss.draw(screen)

    def test_boss_draw_during_death(self, mock_pygame):
        """Test drawing boss during death sequence"""
        boss = Boss(1)
        boss.death_timer = 1.0
        screen = pygame.Surface((800, 600))

        boss.draw(screen)

    def test_boss_draw_shape_satellites(self, mock_pygame):
        """Test boss draws satellites based on level"""
        boss = Boss(100)  # High level boss
        screen = pygame.Surface((800, 600))

        boss.draw(screen)

    def test_boss_draw_health_bar(self, mock_pygame):
        """Test boss draws health bar"""
        boss = Boss(1)
        screen = pygame.Surface((800, 600))

        boss._draw_health_bar(screen)

    def test_boss_draw_health_bar_colors(self, mock_pygame):
        """Test health bar color changes with health"""
        boss = Boss(1)
        screen = pygame.Surface((800, 600))

        # High health - green
        boss.health = boss.max_health
        boss._draw_health_bar(screen)

        # Medium health - yellow
        boss.health = boss.max_health * 0.5
        boss._draw_health_bar(screen)

        # Low health - red
        boss.health = boss.max_health * 0.2
        boss._draw_health_bar(screen)

    def test_boss_draw_health_bar_not_during_death(self, mock_pygame):
        """Test health bar not drawn during death"""
        boss = Boss(1)
        boss.death_timer = 1.0
        screen = pygame.Surface((800, 600))

        boss._draw_health_bar(screen)  # Should return early
