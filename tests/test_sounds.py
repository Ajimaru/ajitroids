from modul.sounds import Sounds
import pytest
from unittest.mock import patch

@patch("pygame.mixer.init")
def test_play_sound_function(mock_mixer_init):
    # mixer wird gemockt, damit kein Audio-Gerät benötigt wird
    sounds = Sounds()
    try:
        sounds.play_explosion()
    except Exception as e:
        assert False, f"play_explosion hat eine Exception ausgelöst: {e}"
