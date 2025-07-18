from modul.sounds import Sounds

def test_play_sound_function():
    sounds = Sounds()
    try:
        sounds.play_explosion()
    except Exception as e:
        assert False, f"play_explosion hat eine Exception ausgelöst: {e}"
