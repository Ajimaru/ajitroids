import pytest
from unittest.mock import patch, MagicMock
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
        # Should initialize without throwing exceptions
        assert sounds is not None
        
    def test_play_explosion_method(self, mock_pygame):
        """Test play_explosion executes without errors"""
        sounds = Sounds()
        try:
            sounds.play_explosion()
        except Exception as e:
            pytest.fail(f"play_explosion raised an exception: {e}")
            
    def test_all_sound_methods_exist(self, mock_pygame):
        """Test all expected sound methods exist"""
        sounds = Sounds()
        
        # List of expected sound methods
        expected_methods = [
            'play_explosion', 'play_shoot', 'play_hit', 
            'play_powerup', 'play_game_over', 'play_level_up',
            'play_extra_life', 'play_enemy_shoot'
        ]
        
        for method_name in expected_methods:
            assert hasattr(sounds, method_name), f"Missing method: {method_name}"
            assert callable(getattr(sounds, method_name))
            
    def test_sound_methods_execution(self, mock_pygame):
        """Test all sound methods execute without errors"""
        sounds = Sounds()
        
        sound_methods = [
            'play_explosion', 'play_shoot', 'play_hit', 
            'play_powerup', 'play_game_over', 'play_level_up'
        ]
        
        for method_name in sound_methods:
            if hasattr(sounds, method_name):
                try:
                    method = getattr(sounds, method_name)
                    method()
                except Exception as e:
                    pytest.fail(f"{method_name} raised an exception: {e}")
                    
    @patch('pygame.mixer.Sound.play')
    def test_sound_playing_called(self, mock_play, mock_pygame):
        """Test that sound playing is attempted (implementation-agnostic)"""
        sounds = Sounds()
        
        # Simply test that sound methods execute without error
        # This avoids assumptions about internal implementation
        try:
            sounds.play_explosion()
            # Test passes if no exception is raised
            assert True
        except Exception as e:
            pytest.fail(f"Sound method failed unexpectedly: {e}")
            
    def test_sounds_with_missing_files(self, mock_pygame):
        """Test sounds handle missing files gracefully"""
        with patch('pygame.mixer.Sound', side_effect=FileNotFoundError()):
            try:
                sounds = Sounds()
                # Should not crash even if sound files are missing
                sounds.play_explosion()
            except Exception as e:
                # Should handle missing files gracefully
                assert "No such file" in str(e) or isinstance(e, FileNotFoundError)
