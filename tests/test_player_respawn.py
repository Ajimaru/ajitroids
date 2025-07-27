from modul.player import Player
import pygame


def test_player_respawn():
    player = Player(100, 100)
    player.position = pygame.Vector2(0, 0)
    player.respawn()
    assert player.position.x == 640
    assert player.position.y == 360
