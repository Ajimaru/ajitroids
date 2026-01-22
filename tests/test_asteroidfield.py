"""Tests for asteroid field generation and behavior."""

import pygame
import pytest

from modul.asteroid import Asteroid
from modul.asteroidfield import AsteroidField
from modul.constants import ASTEROID_MAX_RADIUS


@pytest.fixture(autouse=True)
def init_pygame():
    """Initialize pygame for each test"""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def asteroid_group():
    """Create a sprite group for asteroids"""
    group = pygame.sprite.Group()
    Asteroid.containers = (group,)
    yield group
    Asteroid.containers = ()


class TestAsteroidField:
    def test_asteroidfield_initialization(self):
        """Test AsteroidField initialization"""
        field = AsteroidField()
        assert field.spawn_timer == 0
        assert field.asteroid_count == 5
        assert field.spawn_interval == 5.0

    def test_asteroidfield_edges_structure(self):
        """Test that edges are properly structured"""
        assert len(AsteroidField.edges) == 4
        for edge in AsteroidField.edges:
            assert len(edge) == 2
            assert isinstance(edge[0], pygame.Vector2)
            assert callable(edge[1])

    def test_asteroidfield_spawn(self, asteroid_group):
        """Test asteroid spawning"""
        field = AsteroidField()
        position = pygame.Vector2(100, 100)
        velocity = pygame.Vector2(50, 50)

        field.spawn(ASTEROID_MAX_RADIUS, position, velocity)

        # Check that an asteroid was created
        assert len(asteroid_group) == 1
        asteroid = list(asteroid_group)[0]
        assert isinstance(asteroid, Asteroid)

    def test_asteroidfield_update_timer(self, asteroid_group):
        """Test that update increments spawn timer"""
        field = AsteroidField()
        initial_timer = field.spawn_timer
        field.update(1.0)
        assert field.spawn_timer == initial_timer + 1.0

    def test_asteroidfield_update_spawns_when_needed(self, asteroid_group):
        """Test that update spawns asteroids when timer expires"""
        field = AsteroidField()
        field.spawn_timer = 4.9

        # Update to trigger spawn
        field.update(0.2)

        # Should have spawned an asteroid
        assert len(asteroid_group) >= 1
        assert field.spawn_timer == 0

    def test_asteroidfield_update_no_spawn_when_enough_asteroids(self, asteroid_group):
        """Test that no spawn occurs when enough asteroids exist"""
        field = AsteroidField()
        field.asteroid_count = 2

        # Create enough asteroids
        for i in range(5):
            Asteroid(100 + i * 10, 100, ASTEROID_MAX_RADIUS)

        initial_count = len(asteroid_group)
        field.spawn_timer = 5.0
        field.update(0.1)

        # Should not spawn more asteroids
        assert len(asteroid_group) == initial_count

    def test_asteroidfield_spawn_random(self, asteroid_group):
        """Test random asteroid spawning"""
        field = AsteroidField()

        # Spawn several random asteroids
        for _ in range(5):
            field.spawn_random()

        assert len(asteroid_group) == 5

    def test_asteroidfield_spawn_random_velocities(self, asteroid_group):
        """Test that randomly spawned asteroids have velocities"""
        field = AsteroidField()
        field.spawn_random()

        asteroid = list(asteroid_group)[0]
        # Asteroid should have a velocity
        assert asteroid.velocity.length() > 0

    def test_asteroidfield_edge_positions(self):
        """Test that edge position functions return valid positions"""
        field = AsteroidField()

        for edge in field.edges:
            position_func = edge[1]
            position = position_func(0.5)  # Test with middle value
            assert isinstance(position, pygame.Vector2)
            assert position.x is not None
            assert position.y is not None

    def test_asteroidfield_multiple_updates(self, asteroid_group):
        """Test multiple update cycles"""
        field = AsteroidField()

        for i in range(10):
            field.update(0.5)

        # Timer should have cycled
        assert field.spawn_timer < field.spawn_interval
