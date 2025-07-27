import pytest
from modul.asteroid import Asteroid


def test_asteroid_spawn():
    asteroid = Asteroid(50, 60, 30)
    assert asteroid.position.x == 50
    assert asteroid.position.y == 60
    assert asteroid.radius == 30
