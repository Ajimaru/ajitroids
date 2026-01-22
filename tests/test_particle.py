"""Tests for particle effects and particle behavior."""

import pytest
import pygame
from modul.particle import Particle
from modul.constants import EXPLOSION_PARTICLES


@pytest.fixture(autouse=True)
def init_pygame():
    """Initialize pygame for each test"""
    pygame.init()
    yield
    pygame.quit()


class TestParticle:
    def test_particle_initialization(self):
        """Test particle initialization"""
        particle = Particle(100, 200, "red")
        assert particle.position.x == 100
        assert particle.position.y == 200
        assert particle.color == "red"
        assert particle.alpha == 255
        assert particle.lifetime == 0.5
        assert particle.velocity.length() > 0  # Should have some velocity

    def test_particle_update_movement(self):
        """Test particle moves during update"""
        particle = Particle(100, 100, "blue")
        initial_pos = pygame.Vector2(particle.position)
        particle.update(0.1)
        # Position should change
        assert particle.position != initial_pos

    def test_particle_update_lifetime(self):
        """Test particle lifetime decreases"""
        particle = Particle(100, 100, "green")
        initial_lifetime = particle.lifetime
        particle.update(0.1)
        assert particle.lifetime < initial_lifetime

    def test_particle_update_alpha(self):
        """Test particle alpha decreases with lifetime"""
        particle = Particle(100, 100, "white")
        particle.update(0.1)
        assert particle.alpha < 255

    def test_particle_expires_and_kills(self):
        """Test particle kills itself when lifetime expires"""
        group = pygame.sprite.Group()

        class TestParticle(Particle):
            containers = (group,)

        particle = TestParticle(100, 100, "red")
        assert particle in group

        # Update beyond lifetime
        particle.update(1.0)
        assert particle not in group

    def test_particle_draw(self):
        """Test particle drawing"""
        particle = Particle(100, 100, "yellow")
        screen = pygame.Surface((800, 600))
        particle.draw(screen)  # Should not raise exception

    def test_particle_with_containers(self):
        """Test particle with containers"""
        group = pygame.sprite.Group()

        class TestParticle(Particle):
            containers = (group,)

        particle = TestParticle(50, 60, "cyan")
        assert particle in group

    def test_create_ship_explosion(self):
        """Test ship explosion particle creation"""
        group = pygame.sprite.Group()

        class TestParticle(Particle):
            containers = (group,)

        initial_count = len(group)
        TestParticle.create_ship_explosion(100, 100)

        # Should create EXPLOSION_PARTICLES particles
        assert len(group) == initial_count + EXPLOSION_PARTICLES

        # All particles should be white
        for particle in group:
            if isinstance(particle, TestParticle):
                assert particle.color == "white"
                assert particle.lifetime == 0.5

    def test_create_asteroid_explosion(self):
        """Test asteroid explosion particle creation"""
        group = pygame.sprite.Group()

        class TestParticle(Particle):
            containers = (group,)

        initial_count = len(group)
        TestParticle.create_asteroid_explosion(150, 150)

        # Should create EXPLOSION_PARTICLES particles
        assert len(group) == initial_count + EXPLOSION_PARTICLES

    def test_particle_different_colors(self):
        """Test particles with different colors"""
        colors = ["red", "blue", "green", "yellow", "white"]
        for color in colors:
            particle = Particle(100, 100, color)
            assert particle.color == color

    def test_particle_velocity_variation(self):
        """Test that particles have varying velocities"""
        velocities = []
        for _ in range(10):
            particle = Particle(100, 100, "red")
            velocities.append(particle.velocity.length())

        # Should have variation in velocities
        assert len(set(velocities)) > 1
        # All velocities should be in expected range (50-150)
        for vel in velocities:
            assert 50 <= vel <= 150
