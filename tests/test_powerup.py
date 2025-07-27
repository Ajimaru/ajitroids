import pytest
from modul.powerup import PowerUp


def test_powerup_type():
    powerup = PowerUp(10, 20, "shield")
    assert powerup.type == "shield"
    assert powerup.position.x == 10
    assert powerup.position.y == 20
