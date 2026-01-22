"""Tests for player respawn behavior."""

from unittest.mock import patch

import pygame

from modul.player import Player


@patch("pygame.mixer.init")
def test_player_respawn(mock_mixer_init):
    # mixer wird gemockt, damit kein Audio-Gerät benötigt wird
    player = Player(100, 100)
    player.position = pygame.Vector2(0, 0)
    player.respawn()
    assert player.position.x == 640
    assert player.position.y == 360
