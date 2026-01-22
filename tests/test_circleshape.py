"""Tests for the CircleShape utility."""

import pytest
import pygame

from modul.circleshape import CircleShape


@pytest.fixture(autouse=True)
def init_pygame():
    """Initialize pygame for each test"""
    pygame.init()
    yield
    pygame.quit()


class TestCircleShape:
    def test_circleshape_initialization(self):
        """Test CircleShape initialization"""
        shape = CircleShape(100, 200, 50)
        assert shape.position.x == 100
        assert shape.position.y == 200
        assert shape.radius == 50
        assert shape.rotation == 0
        assert shape.velocity.x == 0
        assert shape.velocity.y == 0

    def test_circleshape_collides_with_no_collision(self):
        """Test collision detection when shapes don't collide"""
        shape1 = CircleShape(0, 0, 10)
        shape2 = CircleShape(100, 100, 10)
        assert not shape1.collides_with(shape2)

    def test_circleshape_collides_with_collision(self):
        """Test collision detection when shapes collide"""
        shape1 = CircleShape(0, 0, 10)
        shape2 = CircleShape(15, 0, 10)
        assert shape1.collides_with(shape2)

    def test_circleshape_collides_with_touching(self):
        """Test collision detection when shapes are exactly touching"""
        shape1 = CircleShape(0, 0, 10)
        shape2 = CircleShape(20, 0, 10)
        assert shape1.collides_with(shape2)

    def test_circleshape_rotate(self):
        """Test rotation method"""
        shape = CircleShape(0, 0, 10)
        shape.rotate(45)
        assert shape.rotation == 45
        shape.rotate(45)
        assert shape.rotation == 90

    def test_circleshape_forward(self):
        """Test forward vector calculation"""
        shape = CircleShape(0, 0, 10)
        forward = shape.forward()
        assert forward.x == pytest.approx(0, abs=0.01)
        assert forward.y == pytest.approx(-1, abs=0.01)

        shape.rotate(90)
        forward = shape.forward()
        assert forward.x == pytest.approx(1, abs=0.01)
        assert forward.y == pytest.approx(0, abs=0.01)

    def test_circleshape_draw(self):
        """Test draw method (should not raise exception)"""
        shape = CircleShape(100, 100, 10)
        screen = pygame.Surface((800, 600))
        shape.draw(screen)  # Should not raise exception

    def test_circleshape_update(self):
        """Test update method (should not raise exception)"""
        shape = CircleShape(100, 100, 10)
        shape.update(0.1)  # Should not raise exception

    def test_circleshape_with_containers(self):
        """Test CircleShape initialization with containers"""
        group = pygame.sprite.Group()

        class TestShape(CircleShape):
            containers = (group,)

        shape = TestShape(50, 60, 20)
        assert shape in group
        assert shape.position.x == 50
        assert shape.position.y == 60
        assert shape.radius == 20
