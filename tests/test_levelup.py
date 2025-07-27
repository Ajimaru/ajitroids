from modul.player import Player


def test_player_has_position():
    player = Player(0, 0)
    assert hasattr(player, "position")
    assert player.position.x == 0
    assert player.position.y == 0
