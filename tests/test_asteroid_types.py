import pytest
import pygame
from unittest.mock import patch
from modul.asteroid import Asteroid
from modul.constants import (
    ASTEROID_MIN_RADIUS,
    ASTEROID_MAX_RADIUS,
    ASTEROID_TYPE_NORMAL,
    ASTEROID_TYPE_ICE,
    ASTEROID_TYPE_METAL,
    ASTEROID_TYPE_CRYSTAL,
    ASTEROID_TYPE_COLORS,
    ASTEROID_ICE_VELOCITY_MULTIPLIER,
    ASTEROID_METAL_HEALTH,
    ASTEROID_CRYSTAL_SPLIT_COUNT,
)
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
    powerup_group = pygame.sprite.Group()
    
    Asteroid.containers = (asteroid_group,)
    PowerUp.containers = (powerup_group,)
    
    yield asteroid_group, powerup_group
    
    Asteroid.containers = ()
    PowerUp.containers = ()


class TestAsteroidTypes:
    def test_normal_asteroid_creation(self):
        """Test creating a normal asteroid"""
        asteroid = Asteroid(100, 100, 50, ASTEROID_TYPE_NORMAL)
        assert asteroid.asteroid_type == ASTEROID_TYPE_NORMAL
        assert asteroid.health == 1
    
    def test_ice_asteroid_creation(self):
        """Test creating an ice asteroid"""
        asteroid = Asteroid(100, 100, 50, ASTEROID_TYPE_ICE)
        assert asteroid.asteroid_type == ASTEROID_TYPE_ICE
        assert asteroid.health == 1
    
    def test_metal_asteroid_creation(self):
        """Test creating a metal asteroid with higher health"""
        asteroid = Asteroid(100, 100, 50, ASTEROID_TYPE_METAL)
        assert asteroid.asteroid_type == ASTEROID_TYPE_METAL
        assert asteroid.health == ASTEROID_METAL_HEALTH
        assert asteroid.health == 2
    
    def test_crystal_asteroid_creation(self):
        """Test creating a crystal asteroid"""
        asteroid = Asteroid(100, 100, 50, ASTEROID_TYPE_CRYSTAL)
        assert asteroid.asteroid_type == ASTEROID_TYPE_CRYSTAL
        assert asteroid.health == 1
    
    def test_default_asteroid_type(self):
        """Test asteroid defaults to normal type when not specified"""
        asteroid = Asteroid(100, 100, 50)
        assert asteroid.asteroid_type == ASTEROID_TYPE_NORMAL
        assert asteroid.health == 1


class TestAsteroidTypeColors:
    def test_normal_asteroid_color(self):
        """Test normal asteroid uses white color"""
        asteroid = Asteroid(100, 100, 50, ASTEROID_TYPE_NORMAL)
        expected_color = ASTEROID_TYPE_COLORS[ASTEROID_TYPE_NORMAL]
        assert expected_color == "white"
    
    def test_ice_asteroid_color(self):
        """Test ice asteroid has light blue color"""
        asteroid = Asteroid(100, 100, 50, ASTEROID_TYPE_ICE)
        color = ASTEROID_TYPE_COLORS[ASTEROID_TYPE_ICE]
        assert color == (150, 200, 255)  # Light blue
    
    def test_metal_asteroid_color(self):
        """Test metal asteroid has gray color"""
        asteroid = Asteroid(100, 100, 50, ASTEROID_TYPE_METAL)
        color = ASTEROID_TYPE_COLORS[ASTEROID_TYPE_METAL]
        assert color == (180, 180, 200)  # Gray-blue
    
    def test_crystal_asteroid_color(self):
        """Test crystal asteroid has purple color"""
        asteroid = Asteroid(100, 100, 50, ASTEROID_TYPE_CRYSTAL)
        color = ASTEROID_TYPE_COLORS[ASTEROID_TYPE_CRYSTAL]
        assert color == (200, 150, 255)  # Purple
    
    def test_asteroid_draw_with_type_color(self):
        """Test asteroid drawing uses type-specific color"""
        asteroid = Asteroid(100, 100, 50, ASTEROID_TYPE_ICE)
        screen = pygame.Surface((800, 600))
        # Should not raise exception and should use ice color
        asteroid.draw(screen)


class TestMetalAsteroidBehavior:
    def test_metal_asteroid_survives_first_hit(self, sprite_groups):
        """Test metal asteroid survives first hit"""
        asteroid_group, powerup_group = sprite_groups
        
        asteroid = Asteroid(100, 100, ASTEROID_MAX_RADIUS, ASTEROID_TYPE_METAL)
        asteroid_group.add(asteroid)
        asteroid.velocity = pygame.Vector2(50, 50)
        
        initial_health = asteroid.health
        assert initial_health == 2
        
        # First hit
        asteroid.split()
        
        # Should still be alive with reduced health
        assert asteroid.health == 1
        assert asteroid in asteroid_group
    
    def test_metal_asteroid_destroyed_on_second_hit(self, sprite_groups):
        """Test metal asteroid is destroyed on second hit"""
        asteroid_group, powerup_group = sprite_groups
        
        asteroid = Asteroid(100, 100, ASTEROID_MAX_RADIUS, ASTEROID_TYPE_METAL)
        asteroid_group.add(asteroid)
        asteroid.velocity = pygame.Vector2(50, 50)
        
        # First hit - survives
        asteroid.split()
        assert asteroid.health == 1
        
        # Second hit - destroyed and splits
        asteroid.split()
        
        # Original should be killed
        assert asteroid not in asteroid_group
        # New asteroids should be created
        assert len(asteroid_group) >= 2
    
    def test_metal_asteroid_min_size_destroyed_first_hit(self, sprite_groups):
        """Test small metal asteroid is destroyed on first hit"""
        asteroid_group, powerup_group = sprite_groups
        
        asteroid = Asteroid(100, 100, ASTEROID_MIN_RADIUS, ASTEROID_TYPE_METAL)
        asteroid_group.add(asteroid)
        
        # Even with 2 health, minimum size asteroids don't split
        asteroid.split()
        
        # Should be destroyed without splitting
        assert asteroid not in asteroid_group


class TestIceAsteroidBehavior:
    def test_ice_asteroid_splits_with_higher_velocity(self, sprite_groups):
        """Test ice asteroids split with higher velocity (slippery)"""
        asteroid_group, powerup_group = sprite_groups
        
        asteroid = Asteroid(100, 100, ASTEROID_MAX_RADIUS, ASTEROID_TYPE_ICE)
        asteroid.velocity = pygame.Vector2(50, 50)
        initial_velocity_length = asteroid.velocity.length()
        
        asteroid.split()
        
        # Check that new asteroids have higher velocity
        for new_asteroid in asteroid_group:
            # Ice asteroids should be faster due to multiplier
            expected_min_velocity = initial_velocity_length * ASTEROID_ICE_VELOCITY_MULTIPLIER * 0.9
            assert new_asteroid.velocity.length() >= expected_min_velocity
    
    def test_ice_asteroid_velocity_multiplier(self):
        """Test ice asteroid velocity multiplier constant"""
        assert ASTEROID_ICE_VELOCITY_MULTIPLIER > 1.0
        assert ASTEROID_ICE_VELOCITY_MULTIPLIER == 1.4
    
    def test_ice_asteroid_splits_into_two(self, sprite_groups):
        """Test ice asteroids still split into 2 pieces"""
        asteroid_group, powerup_group = sprite_groups
        
        asteroid = Asteroid(100, 100, ASTEROID_MAX_RADIUS, ASTEROID_TYPE_ICE)
        asteroid.velocity = pygame.Vector2(50, 50)
        
        asteroid.split()
        
        # Should create 2 new asteroids (not 3 like crystal)
        assert len(asteroid_group) == 2


class TestCrystalAsteroidBehavior:
    def test_crystal_asteroid_splits_into_three(self, sprite_groups):
        """Test crystal asteroids split into 3 pieces"""
        asteroid_group, powerup_group = sprite_groups
        
        asteroid = Asteroid(100, 100, ASTEROID_MAX_RADIUS, ASTEROID_TYPE_CRYSTAL)
        asteroid.velocity = pygame.Vector2(50, 50)
        
        asteroid.split()
        
        # Should create 3 new asteroids
        assert len(asteroid_group) == ASTEROID_CRYSTAL_SPLIT_COUNT
        assert len(asteroid_group) == 3
    
    def test_crystal_split_count_constant(self):
        """Test crystal split count constant"""
        assert ASTEROID_CRYSTAL_SPLIT_COUNT == 3
    
    def test_crystal_asteroids_inherit_type(self, sprite_groups):
        """Test crystal asteroids inherit crystal type when split"""
        asteroid_group, powerup_group = sprite_groups
        
        asteroid = Asteroid(100, 100, ASTEROID_MAX_RADIUS, ASTEROID_TYPE_CRYSTAL)
        asteroid.velocity = pygame.Vector2(50, 50)
        
        asteroid.split()
        
        # All new asteroids should be crystal type
        for new_asteroid in asteroid_group:
            assert new_asteroid.asteroid_type == ASTEROID_TYPE_CRYSTAL
    
    def test_crystal_asteroids_spread_evenly(self, sprite_groups):
        """Test crystal asteroids split in different directions"""
        asteroid_group, powerup_group = sprite_groups
        
        asteroid = Asteroid(100, 100, ASTEROID_MAX_RADIUS, ASTEROID_TYPE_CRYSTAL)
        asteroid.velocity = pygame.Vector2(50, 0)  # Moving right
        
        asteroid.split()
        
        # Should have 3 pieces moving in different directions
        assert len(asteroid_group) == 3
        velocities = [a.velocity for a in asteroid_group]
        
        # Velocities should not all be the same
        assert not all(v == velocities[0] for v in velocities)


class TestAsteroidTypeInheritance:
    def test_normal_asteroid_children_inherit_type(self, sprite_groups):
        """Test normal asteroid children inherit normal type"""
        asteroid_group, powerup_group = sprite_groups
        
        asteroid = Asteroid(100, 100, ASTEROID_MAX_RADIUS, ASTEROID_TYPE_NORMAL)
        asteroid.velocity = pygame.Vector2(50, 50)
        
        asteroid.split()
        
        for new_asteroid in asteroid_group:
            assert new_asteroid.asteroid_type == ASTEROID_TYPE_NORMAL
    
    def test_ice_asteroid_children_inherit_type(self, sprite_groups):
        """Test ice asteroid children inherit ice type"""
        asteroid_group, powerup_group = sprite_groups
        
        asteroid = Asteroid(100, 100, ASTEROID_MAX_RADIUS, ASTEROID_TYPE_ICE)
        asteroid.velocity = pygame.Vector2(50, 50)
        
        asteroid.split()
        
        for new_asteroid in asteroid_group:
            assert new_asteroid.asteroid_type == ASTEROID_TYPE_ICE
    
    def test_metal_asteroid_children_inherit_type(self, sprite_groups):
        """Test metal asteroid children inherit metal type"""
        asteroid_group, powerup_group = sprite_groups
        
        asteroid = Asteroid(100, 100, ASTEROID_MAX_RADIUS, ASTEROID_TYPE_METAL)
        asteroid.velocity = pygame.Vector2(50, 50)
        
        # First hit to reduce health
        asteroid.split()
        # Second hit to actually split
        asteroid.split()
        
        for new_asteroid in asteroid_group:
            assert new_asteroid.asteroid_type == ASTEROID_TYPE_METAL
            assert new_asteroid.health == ASTEROID_METAL_HEALTH


class TestAsteroidFieldSpawning:
    def test_asteroid_field_spawns_different_types(self, sprite_groups):
        """Test asteroid field can spawn different types"""
        from modul.asteroidfield import AsteroidField
        
        asteroid_group, powerup_group = sprite_groups
        field = AsteroidField()
        
        # Spawn multiple asteroids and check types
        types_found = set()
        for _ in range(20):
            field.spawn_random()
            if len(asteroid_group) > 0:
                last_asteroid = list(asteroid_group)[-1]
                types_found.add(last_asteroid.asteroid_type)
        
        # Should have at least spawned some asteroids
        assert len(asteroid_group) > 0
        # Types should be from valid set
        for asteroid in asteroid_group:
            assert asteroid.asteroid_type in [
                ASTEROID_TYPE_NORMAL,
                ASTEROID_TYPE_ICE,
                ASTEROID_TYPE_METAL,
                ASTEROID_TYPE_CRYSTAL,
            ]
