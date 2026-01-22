"""Tests for player leveling and basic player properties."""

from unittest.mock import patch

import pytest

from modul.player import Player


@patch("pygame.mixer.init")
def test_player_has_position(mock_mixer_init):
    # mixer wird gemockt, damit kein Audio-Gerät benötigt wird
    player = Player(0, 0)
    assert hasattr(player, "position")
    assert player.position.x == 0
    assert player.position.y == 0
