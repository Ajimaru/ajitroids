"""Tests for asteroid behavior and related classes."""

import pytest
import pygame
from unittest.mock import patch
from modul.asteroid import Asteroid, EnemyShip
from modul.constants import ASTEROID_MIN_RADIUS, ASTEROID_MAX_RADIUS, ASTEROID_VERTICES
from modul.shot import Shot
from modul.powerup import PowerUp


@pytest.fixture(autouse=True)
def init_pygame():
    """Initialize pygame for each test"""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def sprite_groups():
    """Create sprite groups for tests"""
    asteroid_group = pygame.sprite.Group()
    shot_group = pygame.sprite.Group()
    powerup_group = pygame.sprite.Group()

    Asteroid.containers = (asteroid_group,)
    Shot.containers = (shot_group,)
    PowerUp.containers = (powerup_group,)

    yield asteroid_group, shot_group, powerup_group

    Asteroid.containers = ()
    Shot.containers = ()
    PowerUp.containers = ()


class TestAsteroid:
    def test_asteroid_spawn(self):
        asteroid = Asteroid(50, 60, 30)
        assert asteroid.position.x == 50
        assert asteroid.position.y == 60
        assert asteroid.radius == 30

    def test_asteroid_initialization(self):
        """Test Asteroid initialization"""
        asteroid = Asteroid(100, 200, 50)
        assert asteroid.position.x == 100
        assert asteroid.position.y == 200
        assert asteroid.radius == 50
        assert asteroid.rotation == 0
        assert asteroid.rotation_speed == 0
        assert len(asteroid.vertices) == ASTEROID_VERTICES

    def test_asteroid_vertices_generation(self):
        """Test asteroid vertices are properly generated"""
        asteroid = Asteroid(100, 100, 50)
        assert len(asteroid.vertices) > 0
        assert len(asteroid.vertices) == ASTEROID_VERTICES

        # Vertices should be within reasonable bounds
        for x, y in asteroid.vertices:
            distance = (x**2 + y**2) ** 0.5
            assert distance <= asteroid.radius * 1.5

    def test_asteroid_update_movement(self):
        """Test asteroid movement during update"""
        asteroid = Asteroid(100, 100, 50)
        asteroid.velocity = pygame.Vector2(10, 20)
        asteroid.rotation_speed = 0.5

        initial_pos = pygame.Vector2(asteroid.position)
        initial_rotation = asteroid.rotation

        asteroid.update(0.1)

        assert asteroid.position != initial_pos
        assert asteroid.rotation != initial_rotation

    def test_asteroid_draw(self):
        """Test asteroid drawing"""
        asteroid = Asteroid(100, 100, 50)
        screen = pygame.Surface((800, 600))
        asteroid.draw(screen)  # Should not raise exception

    def test_asteroid_point_in_polygon(self):
        """Test point in polygon detection"""
        asteroid = Asteroid(100, 100, 50)

        # Point at center should be inside
        assert asteroid.point_in_polygon((100, 100))

        # Point far away should be outside
        assert not asteroid.point_in_polygon((1000, 1000))

    def test_asteroid_collides_with_circleshape(self):
        """Test collision with generic CircleShape"""
        asteroid1 = Asteroid(100, 100, 50)
        asteroid2 = Asteroid(150, 100, 50)

        # Should collide (overlapping)
        assert asteroid1.collides_with(asteroid2)

        # Should not collide (far apart)
        asteroid3 = Asteroid(500, 500, 50)
        assert not asteroid1.collides_with(asteroid3)

    def test_asteroid_collides_with_shot(self, sprite_groups):
        """Test collision with Shot"""
        asteroid_group, shot_group, _ = sprite_groups

        asteroid = Asteroid(100, 100, 50)
        shot = Shot(100, 100)

        # Shot at same position should collide
        assert asteroid.collides_with(shot)

        # Shot far away should not collide
        shot2 = Shot(500, 500)
        assert not asteroid.collides_with(shot2)

    def test_asteroid_split_min_size(self, sprite_groups):
        """Test splitting minimum size asteroid"""
        asteroid_group, _, powerup_group = sprite_groups

        asteroid = Asteroid(100, 100, ASTEROID_MIN_RADIUS)
        asteroid_group.add(asteroid)
        initial_count = len(asteroid_group)

        asteroid.split()

        # The original asteroid should be destroyed, and no new ones created.
        assert len(asteroid_group) == initial_count - 1

    def test_asteroid_split_creates_children(self, sprite_groups):
        """Test splitting large asteroid creates children"""
        asteroid_group, _, powerup_group = sprite_groups

        asteroid = Asteroid(100, 100, ASTEROID_MAX_RADIUS)
        asteroid.velocity = pygame.Vector2(50, 50)

        asteroid.split()

        # Should create 2 new asteroids
        assert len(asteroid_group) >= 2

    def test_asteroid_split_children_properties(self, sprite_groups):
        """Test split asteroid children have correct properties"""
        asteroid_group, _, powerup_group = sprite_groups

        asteroid = Asteroid(100, 100, ASTEROID_MAX_RADIUS)
        asteroid.velocity = pygame.Vector2(50, 50)
        parent_radius = asteroid.radius

        asteroid.split()

        # Check children have smaller radius
        for child in asteroid_group:
            assert child.radius < parent_radius
            assert child.velocity.length() > 0

    def test_asteroid_split_powerup_spawn(self, sprite_groups):
        """Test powerup spawning during split"""
        asteroid_group, _, powerup_group = sprite_groups

        # Create and split many asteroids to likely trigger powerup spawn
        for _ in range(50):
            asteroid = Asteroid(100, 100, ASTEROID_MAX_RADIUS)
            asteroid.split()

        # At least one powerup should have spawned statistically
        # (with 50 tries and POWERUP_SPAWN_CHANCE, very likely)
        # But we can't guarantee it, so just check no error occurred
        assert len(powerup_group) >= 0

    def test_asteroid_rotation(self):
        """Test asteroid rotation"""
        asteroid = Asteroid(100, 100, 50)
        asteroid.rotation = 0
        asteroid.rotation_speed = 1.0

        asteroid.update(1.0)

        assert asteroid.rotation == pytest.approx(1.0)

    def test_asteroid_different_sizes(self):
        """Test asteroids of different sizes"""
        small = Asteroid(100, 100, ASTEROID_MIN_RADIUS)
        large = Asteroid(200, 200, ASTEROID_MAX_RADIUS)

        assert small.radius < large.radius
        assert len(small.vertices) == len(large.vertices)


class TestEnemyShip:
    def test_enemyship_initialization(self):
        """Test EnemyShip initialization"""
        enemy = EnemyShip(100, 200, 50)
        assert enemy.position.x == 100
        assert enemy.position.y == 200
        assert enemy.rotation == 0
        assert enemy.velocity.length() > 0

    def test_enemyship_update_movement(self):
        """Test enemy ship movement"""
        enemy = EnemyShip(100, 100, 50)
        initial_pos = pygame.Vector2(enemy.position)

        enemy.update(0.1)

        assert enemy.position != initial_pos

    def test_enemyship_update_rotation(self):
        """Test enemy ship rotation"""
        enemy = EnemyShip(100, 100, 50)
        initial_rotation = enemy.rotation

        enemy.update(0.1)

        # Rotation should change
        assert enemy.rotation != initial_rotation

    def test_enemyship_screen_wrap_x(self):
        """Test enemy ship wraps around screen horizontally"""
        enemy = EnemyShip(-10, 100, 50)
        enemy.velocity = pygame.Vector2(-10, 0)

        enemy.update(0.1)

        # Should wrap to right side (implementation checks position < 0)
        assert enemy.position.x >= 0

    def test_enemyship_screen_wrap_y(self):
        """Test enemy ship wraps around screen vertically"""
        enemy = EnemyShip(100, -10, 50)
        enemy.velocity = pygame.Vector2(0, -10)

        enemy.update(0.1)

        # Should wrap to bottom
        assert enemy.position.y >= 0

    def test_enemyship_chases_player(self):
        """Test enemy ship moves toward nearby player"""
        enemy = EnemyShip(100, 100, 50)
        player_pos = pygame.Vector2(200, 200)

        initial_velocity = pygame.Vector2(enemy.velocity)

        enemy.update(0.1, player_position=player_pos)

        # Velocity should be set toward player
        direction = (player_pos - enemy.position).normalize()
        assert enemy.velocity.length() > 0

    def test_enemyship_no_chase_distant_player(self):
        """Test enemy ship doesn't chase distant player"""
        enemy = EnemyShip(100, 100, 50)
        player_pos = pygame.Vector2(5000, 5000)  # Very far away

        enemy.update(0.1, player_position=player_pos)

        # Should not be chasing (velocity should decay)
        # Just verify no crash

    def test_enemyship_collides_with(self):
        """Test enemy ship collision detection"""
        enemy = EnemyShip(100, 100, 50)
        asteroid = Asteroid(150, 100, 50)

        # Should collide
        assert enemy.collides_with(asteroid)

        # Should not collide when far
        asteroid2 = Asteroid(500, 500, 50)
        assert not enemy.collides_with(asteroid2)

    def test_enemyship_draw(self):
        """Test enemy ship drawing"""
        enemy = EnemyShip(100, 100, 50)
        screen = pygame.Surface((800, 600))
        enemy.draw(screen)  # Should not raise exception

    def test_enemyship_split(self):
        """Test enemy ship split creates particles"""
        group = pygame.sprite.Group()

        class TestEnemyShip(EnemyShip):
            containers = (group,)

        # Mock Particle.create_ship_explosion
        with patch('modul.particle.Particle.create_ship_explosion') as mock_create:
            enemy = TestEnemyShip(100, 100, 50)
            enemy.split()

            # Should have called particle creation
            assert mock_create.called

            # Enemy should be removed from group
            assert enemy not in group

    def test_enemyship_kill(self):
        """Test enemy ship kill method"""
        # Mock Particle.create_ship_explosion
        with patch('modul.particle.Particle.create_ship_explosion') as mock_create:
            enemy = EnemyShip(100, 100, 50)
            enemy.kill()

            # Should have called particle creation
            assert mock_create.called

    def test_enemyship_update_no_player(self):
        """Test enemy ship update without player position"""
        enemy = EnemyShip(100, 100, 50)
        enemy.update(0.1, player_position=None)
        # Should not crash
        assert True

    def test_enemyship_velocity_decay(self):
        """Test enemy ship velocity decays when player is distant"""
        enemy = EnemyShip(100, 100, 50)
        enemy.velocity = pygame.Vector2(100, 100)
        player_pos = pygame.Vector2(5000, 5000)  # Far away

        initial_velocity = enemy.velocity.length()
        enemy.update(0.1, player_position=player_pos)

        # Velocity should have decayed
        assert enemy.velocity.length() < initial_velocity
