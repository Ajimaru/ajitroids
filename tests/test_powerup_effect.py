from modul.player import Player
from modul.powerup import PowerUp


def test_powerup_shield_type():
    powerup = PowerUp(0, 0, "shield")
    assert powerup.type == "shield"
