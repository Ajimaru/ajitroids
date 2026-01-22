"""Tests for the Sounds system and sound loading."""

from unittest.mock import patch, MagicMock

import pytest

from modul.sounds import Sounds


@pytest.fixture
def mock_pygame():
    """Mock pygame components for isolated testing"""
    with patch('pygame.mixer.init'), \
         patch('pygame.mixer.Sound'), \
         patch('pygame.mixer.music'):
        yield


class TestSounds:
    """Test suite for Sounds class functionality"""

    def test_sounds_initialization(self, mock_pygame):
        """Test sounds system initializes without errors"""
        sounds = Sounds()
        assert sounds is not None
        assert sounds.sound_on is True

    def test_sounds_initialization_calls_mixer_init(self):
        """Test sounds initialization calls pygame mixer init"""
        with patch('pygame.mixer.init') as mock_init, \
             patch('pygame.mixer.Sound'), \
             patch('pygame.mixer.music'):
            sounds = Sounds()
            mock_init.assert_called_once_with(44100, -16, 2, 2048)

    def test_sounds_loads_shoot_sound(self, mock_pygame):
        """Test shoot sound is loaded"""
        sounds = Sounds()
        # Sound attributes should be set (even if None when file missing)
        assert hasattr(sounds, 'shoot')

    def test_sounds_loads_explosion_sound(self, mock_pygame):
        """Test explosion sound is loaded"""
        sounds = Sounds()
        assert hasattr(sounds, 'explosion')

    def test_sounds_loads_player_death_sound(self, mock_pygame):
        """Test player death sound is loaded"""
        sounds = Sounds()
        assert hasattr(sounds, 'player_death')

    def test_sounds_loads_menu_sounds(self, mock_pygame):
        """Test menu sounds are loaded"""
        sounds = Sounds()
        assert hasattr(sounds, 'menu_move')
        assert hasattr(sounds, 'menu_select')

    def test_sounds_load_new_sounds_method(self, mock_pygame):
        """Test load_new_sounds loads additional sounds"""
        sounds = Sounds()
        assert hasattr(sounds, 'laser_shoot')
        assert hasattr(sounds, 'rocket_shoot')
        assert hasattr(sounds, 'boss_spawn')
        assert hasattr(sounds, 'boss_death')
        assert hasattr(sounds, 'powerup')
        assert hasattr(sounds, 'shield_activate')
        assert hasattr(sounds, 'level_up')
        assert hasattr(sounds, 'game_over')
        assert hasattr(sounds, 'player_hit')

    def test_play_shoot(self, mock_pygame):
        """Test play_shoot method"""
        sounds = Sounds()
        sounds.shoot = MagicMock()
        sounds.sound_on = True

        sounds.play_shoot()

        sounds.shoot.play.assert_called_once()

    def test_play_shoot_sound_off(self, mock_pygame):
        """Test play_shoot respects sound_on flag"""
        sounds = Sounds()
        sounds.shoot = MagicMock()
        sounds.sound_on = False

        sounds.play_shoot()

        sounds.shoot.play.assert_not_called()

    def test_play_shoot_none_sound(self, mock_pygame):
        """Test play_shoot handles None sound"""
        sounds = Sounds()
        sounds.shoot = None
        sounds.sound_on = True

        sounds.play_shoot()  # Should not crash

    def test_play_explosion(self, mock_pygame):
        """Test play_explosion method"""
        sounds = Sounds()
        sounds.explosion = MagicMock()
        sounds.sound_on = True

        sounds.play_explosion()

        sounds.explosion.play.assert_called_once()

    def test_play_explosion_sound_off(self, mock_pygame):
        """Test play_explosion respects sound_on flag"""
        sounds = Sounds()
        sounds.explosion = MagicMock()
        sounds.sound_on = False

        sounds.play_explosion()

        sounds.explosion.play.assert_not_called()

    def test_play_player_death(self, mock_pygame):
        """Test play_player_death method"""
        sounds = Sounds()
        sounds.player_death = MagicMock()
        sounds.sound_on = True

        sounds.play_player_death()

        sounds.player_death.play.assert_called_once()

    def test_play_menu_move(self, mock_pygame):
        """Test play_menu_move method"""
        sounds = Sounds()
        sounds.menu_move = MagicMock()
        sounds.sound_on = True

        sounds.play_menu_move()

        sounds.menu_move.play.assert_called_once()

    def test_play_menu_select(self, mock_pygame):
        """Test play_menu_select method"""
        sounds = Sounds()
        sounds.menu_select = MagicMock()
        sounds.sound_on = True

        sounds.play_menu_select()

        sounds.menu_select.play.assert_called_once()

    def test_play_level_up(self, mock_pygame):
        """Test play_level_up method"""
        sounds = Sounds()
        sounds.level_up = MagicMock()
        sounds.sound_on = True

        sounds.play_level_up()

        sounds.level_up.play.assert_called_once()

    def test_play_achievement_uses_level_up(self, mock_pygame):
        """Test play_achievement uses level_up sound"""
        sounds = Sounds()
        sounds.level_up = MagicMock()
        sounds.sound_on = True

        sounds.play_achievement()

        sounds.level_up.play.assert_called()

    def test_play_achievement_no_sound(self, mock_pygame):
        """Test play_achievement handles missing sound"""
        sounds = Sounds()
        sounds.level_up = None
        sounds.sound_on = True

        sounds.play_achievement()  # Should not crash

    def test_play_powerup(self, mock_pygame):
        """Test play_powerup method"""
        sounds = Sounds()
        sounds.powerup = MagicMock()
        sounds.sound_on = True

        sounds.play_powerup()

        sounds.powerup.play.assert_called_once()

    def test_play_laser_shoot(self, mock_pygame):
        """Test play_laser_shoot method"""
        sounds = Sounds()
        sounds.laser_shoot = MagicMock()
        sounds.sound_on = True

        sounds.play_laser_shoot()

        sounds.laser_shoot.play.assert_called_once()

    def test_play_rocket_shoot(self, mock_pygame):
        """Test play_rocket_shoot method"""
        sounds = Sounds()
        sounds.rocket_shoot = MagicMock()
        sounds.sound_on = True

        sounds.play_rocket_shoot()

        sounds.rocket_shoot.play.assert_called_once()

    def test_play_boss_spawn(self, mock_pygame):
        """Test play_boss_spawn method"""
        sounds = Sounds()
        sounds.boss_spawn = MagicMock()
        sounds.sound_on = True

        sounds.play_boss_spawn()

        sounds.boss_spawn.play.assert_called_once()

    def test_play_boss_death(self, mock_pygame):
        """Test play_boss_death method"""
        sounds = Sounds()
        sounds.boss_death = MagicMock()
        sounds.sound_on = True

        sounds.play_boss_death()

        sounds.boss_death.play.assert_called_once()

    def test_play_shield_activate(self, mock_pygame):
        """Test play_shield_activate method"""
        sounds = Sounds()
        sounds.shield_activate = MagicMock()
        sounds.sound_on = True

        sounds.play_shield_activate()

        sounds.shield_activate.play.assert_called_once()

    def test_play_game_over(self, mock_pygame):
        """Test play_game_over method"""
        sounds = Sounds()
        sounds.game_over = MagicMock()
        sounds.sound_on = True

        sounds.play_game_over()

        sounds.game_over.play.assert_called_once()

    def test_play_game_over_none_sound(self, mock_pygame):
        """Test play_game_over handles missing sound"""
        sounds = Sounds()
        sounds.game_over = None
        sounds.sound_on = True

        sounds.play_game_over()  # Should not crash

    def test_play_hit(self, mock_pygame):
        """Test play_hit method"""
        sounds = Sounds()
        sounds.explosion = MagicMock()
        sounds.sound_on = True

        sounds.play_hit()

        sounds.explosion.play.assert_called_once()

    def test_play_extra_life(self, mock_pygame):
        """Test play_extra_life method"""
        sounds = Sounds()
        sounds.level_up = MagicMock()
        sounds.sound_on = True

        sounds.play_extra_life()

        sounds.level_up.play.assert_called_once()

    def test_play_extra_life_none_sound(self, mock_pygame):
        """Test play_extra_life handles missing sound"""
        sounds = Sounds()
        sounds.level_up = None
        sounds.sound_on = True

        sounds.play_extra_life()  # Should not crash

    def test_play_enemy_shoot_with_boss_attack(self, mock_pygame):
        """Test play_enemy_shoot with boss_attack sound"""
        sounds = Sounds()
        sounds.boss_attack = MagicMock()
        sounds.sound_on = True

        sounds.play_enemy_shoot()

        sounds.boss_attack.play.assert_called_once()

    def test_play_enemy_shoot_fallback(self, mock_pygame):
        """Test play_enemy_shoot fallback to shoot sound"""
        sounds = Sounds()
        sounds.shoot = MagicMock()
        sounds.sound_on = True

        sounds.play_enemy_shoot()

        sounds.shoot.play.assert_called_once()

    def test_play_player_hit(self, mock_pygame):
        """Test play_player_hit method"""
        sounds = Sounds()
        sounds.player_hit = MagicMock()
        sounds.sound_on = True

        sounds.play_player_hit()

        sounds.player_hit.play.assert_called_once()

    def test_play_player_hit_fallback(self, mock_pygame):
        """Test play_player_hit fallback to explosion"""
        sounds = Sounds()
        sounds.player_hit = None
        sounds.explosion = MagicMock()
        sounds.sound_on = True

        sounds.play_player_hit()

        sounds.explosion.play.assert_called_once()

    def test_toggle_music_enable(self, mock_pygame):
        """Test toggle_music enables music"""
        with patch('pygame.mixer.music.load'), \
             patch('pygame.mixer.music.play'), \
             patch('pygame.mixer.music.set_volume') as mock_volume, \
             patch('pygame.mixer.music.get_busy', return_value=False):
            sounds = Sounds()

            sounds.toggle_music(True)

            mock_volume.assert_called()

    def test_toggle_music_disable(self, mock_pygame):
        """Test toggle_music disables music"""
        with patch('pygame.mixer.music.stop') as mock_stop, \
             patch('pygame.mixer.music.set_volume') as mock_volume:
            sounds = Sounds()

            sounds.toggle_music(False)

            mock_stop.assert_called_once()
            mock_volume.assert_called_with(0.0)

    def test_toggle_music_already_playing(self, mock_pygame):
        """Test toggle_music when music already playing"""
        with patch('pygame.mixer.music.load'), \
             patch('pygame.mixer.music.play') as mock_play, \
             patch('pygame.mixer.music.set_volume'), \
             patch('pygame.mixer.music.get_busy', return_value=True):
            sounds = Sounds()

            sounds.toggle_music(True)

            # Should not restart if already playing
            mock_play.assert_not_called()

    def test_toggle_music_error_handling(self, mock_pygame):
        """Test toggle_music handles errors gracefully"""
        with patch('pygame.mixer.music.load', side_effect=Exception("Test error")):
            sounds = Sounds()

            sounds.toggle_music(True)  # Should not crash

    def test_toggle_sound_enable(self, mock_pygame):
        """Test toggle_sound enables all sounds"""
        sounds = Sounds()
        sounds.shoot = MagicMock()
        sounds.explosion = MagicMock()

        sounds.toggle_sound(True)

        assert sounds.sound_on is True
        sounds.shoot.set_volume.assert_called_with(0.5)
        sounds.explosion.set_volume.assert_called_with(0.5)

    def test_toggle_sound_disable(self, mock_pygame):
        """Test toggle_sound disables all sounds"""
        sounds = Sounds()
        sounds.shoot = MagicMock()
        sounds.explosion = MagicMock()

        sounds.toggle_sound(False)

        assert sounds.sound_on is False
        sounds.shoot.set_volume.assert_called_with(0.0)
        sounds.explosion.set_volume.assert_called_with(0.0)

    def test_toggle_sound_with_menu_sounds(self, mock_pygame):
        """Test toggle_sound affects menu sounds"""
        sounds = Sounds()
        sounds.menu_move = MagicMock()
        sounds.menu_select = MagicMock()

        sounds.toggle_sound(False)

        sounds.menu_move.set_volume.assert_called_with(0.0)
        sounds.menu_select.set_volume.assert_called_with(0.0)

    def test_toggle_sound_handles_none(self, mock_pygame):
        """Test toggle_sound handles None sounds"""
        sounds = Sounds()
        sounds.shoot = None

        sounds.toggle_sound(True)  # Should not crash

    def test_play_boss_music(self, mock_pygame):
        """Test play_boss_music method"""
        with patch('pygame.mixer.get_init', return_value=True), \
             patch('pygame.mixer.music.load') as mock_load, \
             patch('pygame.mixer.music.play') as mock_play, \
             patch('pygame.mixer.music.set_volume'):
            sounds = Sounds()
            # Reset load mock to clear background music load
            mock_load.reset_mock()

            sounds.play_boss_music()

            loaded_path = mock_load.call_args.args[0]
            assert loaded_path.endswith("boss_music.mp3")
            mock_play.assert_called_once_with(-1)

    def test_play_boss_music_mixer_not_init(self, mock_pygame):
        """Test play_boss_music when mixer not initialized"""
        with patch('pygame.mixer.get_init', return_value=None):
            sounds = Sounds()

            sounds.play_boss_music()  # Should not crash

    def test_play_boss_music_error_handling(self, mock_pygame):
        """Test play_boss_music handles errors"""
        with patch('pygame.mixer.get_init', return_value=True), \
             patch('pygame.mixer.music.load', side_effect=Exception("Test error")):
            sounds = Sounds()

            sounds.play_boss_music()  # Should not crash

    def test_set_effects_volume(self, mock_pygame):
        """Test set_effects_volume method"""
        sounds = Sounds()
        sounds.shoot = MagicMock()
        sounds.explosion = MagicMock()
        sounds.player_death = MagicMock()

        sounds.set_effects_volume(0.7)

        sounds.shoot.set_volume.assert_called_with(0.7)
        sounds.explosion.set_volume.assert_called_with(0.7)
        sounds.player_death.set_volume.assert_called_with(0.7)

    def test_set_effects_volume_all_sounds(self, mock_pygame):
        """Test set_effects_volume affects all sound attributes"""
        sounds = Sounds()
        sounds.menu_move = MagicMock()
        sounds.laser_shoot = MagicMock()
        sounds.boss_spawn = MagicMock()
        sounds.powerup = MagicMock()
        sounds.level_up = MagicMock()

        sounds.set_effects_volume(0.3)

        sounds.menu_move.set_volume.assert_called_with(0.3)
        sounds.laser_shoot.set_volume.assert_called_with(0.3)
        sounds.boss_spawn.set_volume.assert_called_with(0.3)

    def test_set_effects_volume_handles_none(self, mock_pygame):
        """Test set_effects_volume handles None sounds"""
        sounds = Sounds()
        sounds.shoot = None

        sounds.set_effects_volume(0.5)  # Should not crash

    def test_sounds_with_missing_files(self, mock_pygame):
        """Test sounds handle missing files gracefully"""
        with patch('pygame.mixer.Sound', side_effect=FileNotFoundError()):
            try:
                sounds = Sounds()
                sounds.play_explosion()
            except Exception as e:
                assert "No such file" in str(e) or isinstance(e, FileNotFoundError)
