def test_player_respawn(mock_mixer_init):
"""Tests for player respawn behavior."""

import pytest
from unittest.mock import patch

from modul.player import Player
import pygame


@patch("pygame.mixer.init")
def test_player_respawn(mock_mixer_init):
    # mixer wird gemockt, damit kein Audio-Gerät benötigt wird
    player = Player(100, 100)
    player.position = pygame.Vector2(0, 0)
    player.respawn()
    assert player.position.x == 640
    assert player.position.y == 360
