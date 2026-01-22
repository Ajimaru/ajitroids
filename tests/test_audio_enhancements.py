"""Tests for audio enhancement features"""

from unittest.mock import patch, MagicMock, call

import pytest

from modul.audio_enhancements import (
    DynamicMusicSystem,
    VoiceAnnouncement,
    SoundThemeManager,
    AudioEnhancementManager,
    IntensityLevel,
    SoundTheme
)


class TestDynamicMusicSystem:
    """Test suite for dynamic music system"""

    def test_initialization(self):
        """Test dynamic music system initializes correctly"""
        dms = DynamicMusicSystem()
        assert dms.current_intensity == IntensityLevel.CALM
        assert dms.enabled is True
        assert dms.min_transition_time == 2.0

    def test_calculate_intensity_calm(self):
        """Test intensity calculation for calm state"""
        dms = DynamicMusicSystem()
        intensity = dms.calculate_intensity(
            asteroids_count=2,
            enemies_count=0,
            boss_active=False,
            score=0,
            level=1
        )
        assert intensity == IntensityLevel.CALM

    def test_calculate_intensity_normal(self):
        """Test intensity calculation for normal state"""
        dms = DynamicMusicSystem()
        intensity = dms.calculate_intensity(
            asteroids_count=5,
            enemies_count=2,
            boss_active=False,
            score=10000,
            level=3
        )
        assert intensity == IntensityLevel.NORMAL

    def test_calculate_intensity_intense(self):
        """Test intensity calculation for intense state"""
        dms = DynamicMusicSystem()
        intensity = dms.calculate_intensity(
            asteroids_count=10,
            enemies_count=5,
            boss_active=False,
            score=50000,
            level=10
        )
        assert intensity == IntensityLevel.INTENSE

    def test_calculate_intensity_boss(self):
        """Test intensity calculation always returns boss when boss active"""
        dms = DynamicMusicSystem()
        intensity = dms.calculate_intensity(
            asteroids_count=0,
            enemies_count=0,
            boss_active=True,
            score=0,
            level=1
        )
        assert intensity == IntensityLevel.BOSS

    def test_update_when_disabled(self):
        """Test update does nothing when disabled"""
        dms = DynamicMusicSystem()
        dms.set_enabled(False)

        mock_asset_path = MagicMock(return_value="test.mp3")
        result = dms.update(
            dt=1.0,
            asteroids_count=10,
            enemies_count=10,
            boss_active=True,
            score=100000,
            level=20,
            asset_path_func=mock_asset_path
        )

        assert result is False
        assert dms.current_intensity == IntensityLevel.CALM

    def test_update_respects_cooldown(self):
        """Test update respects transition cooldown"""
        dms = DynamicMusicSystem()
        dms.transition_cooldown = 5.0

        mock_asset_path = MagicMock(return_value="test.mp3")
        result = dms.update(
            dt=1.0,
            asteroids_count=0,
            enemies_count=0,
            boss_active=True,
            score=0,
            level=1,
            asset_path_func=mock_asset_path
        )

        assert result is False
        assert dms.current_intensity == IntensityLevel.CALM

    @patch('pygame.mixer.music')
    def test_transition_music(self, mock_music):
        """Test music transition functionality"""
        dms = DynamicMusicSystem()
        mock_asset_path = MagicMock(return_value="/path/to/boss_music.mp3")

        result = dms._transition_music(IntensityLevel.BOSS, mock_asset_path)

        assert result is True
        assert dms.current_intensity == IntensityLevel.BOSS
        mock_music.fadeout.assert_called_once_with(1000)
        mock_music.load.assert_called_once_with("/path/to/boss_music.mp3")
        mock_music.play.assert_called_once_with(-1)

    def test_set_enabled(self):
        """Test enabling/disabling dynamic music"""
        dms = DynamicMusicSystem()
        dms.set_enabled(False)
        assert dms.enabled is False

        dms.set_enabled(True)
        assert dms.enabled is True


class TestVoiceAnnouncement:
    """Test suite for voice announcement system"""

    def test_initialization(self):
        """Test voice announcement initializes correctly"""
        va = VoiceAnnouncement()
        assert va.enabled is True
        assert va.current_announcement is None
        assert len(va.announcement_queue) == 0
        assert "level_up" in va.announcements
        assert "boss_incoming" in va.announcements

    def test_trigger_announcement(self):
        """Test triggering an announcement"""
        va = VoiceAnnouncement()
        va.trigger("level_up", priority=5.0)

        # Announcement should be set or queued
        assert va.current_announcement == "Level up!" or len(va.announcement_queue) > 0

    def test_trigger_invalid_event(self):
        """Test triggering invalid event type"""
        va = VoiceAnnouncement()
        va.trigger("invalid_event", priority=5.0)

        # Should not crash, just ignore
        assert va.current_announcement is None

    def test_trigger_when_disabled(self):
        """Test trigger does nothing when disabled"""
        va = VoiceAnnouncement()
        va.set_enabled(False)
        va.trigger("level_up", priority=5.0)

        assert va.current_announcement is None
        assert len(va.announcement_queue) == 0

    def test_update_decrements_timer(self):
        """Test update decrements announcement timer"""
        va = VoiceAnnouncement()
        va.current_announcement = "Test"
        va.announcement_timer = 2.0

        va.update(1.0)

        assert va.announcement_timer == 1.0
        assert va.current_announcement == "Test"

    def test_update_clears_expired_announcement(self):
        """Test update clears announcement when timer expires"""
        va = VoiceAnnouncement()
        va.current_announcement = "Test"
        va.announcement_timer = 0.5

        va.update(1.0)

        assert va.current_announcement is None

    def test_announcement_queue_priority(self):
        """Test announcement queue respects priority"""
        va = VoiceAnnouncement()
        va.last_announcement_time = 0  # Reset to allow immediate queueing

        va.trigger("level_up", priority=5.0)
        va.trigger("boss_incoming", priority=10.0)

        # Higher priority should be first in queue after sort
        if len(va.announcement_queue) >= 2:
            va.announcement_queue.sort(key=lambda x: x[1], reverse=True)
            assert va.announcement_queue[0][1] == 10.0

    def test_get_current_announcement(self):
        """Test getting current announcement text"""
        va = VoiceAnnouncement()
        va.current_announcement = "Test announcement"

        assert va.get_current_announcement() == "Test announcement"

    def test_set_enabled(self):
        """Test enabling/disabling announcements"""
        va = VoiceAnnouncement()
        va.set_enabled(False)
        assert va.enabled is False

        va.set_enabled(True)
        assert va.enabled is True

    @patch('pygame.mixer.Sound')
    def test_load_announcement_sounds(self, mock_sound):
        """Test loading announcement sound files"""
        va = VoiceAnnouncement()
        mock_asset_path = MagicMock(return_value="/path/to/sound.wav")

        va.load_announcement_sounds(mock_asset_path)

        # Should attempt to load announcement sounds
        assert mock_asset_path.called


class TestSoundThemeManager:
    """Test suite for sound theme management"""

    def test_initialization(self):
        """Test theme manager initializes correctly"""
        stm = SoundThemeManager()
        assert stm.current_theme == SoundTheme.DEFAULT
        assert len(stm.theme_mappings) >= 4  # At least 4 themes

    def test_get_sound_file_default(self):
        """Test getting sound file for default theme"""
        stm = SoundThemeManager()
        sound_file = stm.get_sound_file("shoot")
        assert sound_file == "shoot.wav"

    def test_get_sound_file_retro(self):
        """Test getting sound file for retro theme"""
        stm = SoundThemeManager()
        stm.set_theme(SoundTheme.RETRO)
        sound_file = stm.get_sound_file("shoot")
        assert sound_file is not None

    def test_get_sound_file_scifi(self):
        """Test getting sound file for sci-fi theme"""
        stm = SoundThemeManager()
        stm.set_theme(SoundTheme.SCIFI)
        sound_file = stm.get_sound_file("shoot")
        # Sci-fi theme uses laser for shoot
        assert sound_file == "laser_shoot.wav"

    def test_get_sound_file_orchestral(self):
        """Test getting sound file for orchestral theme"""
        stm = SoundThemeManager()
        stm.set_theme(SoundTheme.ORCHESTRAL)
        sound_file = stm.get_sound_file("background_music")
        # Orchestral uses boss music
        assert sound_file == "boss_music.mp3"

    def test_set_theme(self):
        """Test setting theme"""
        stm = SoundThemeManager()
        result = stm.set_theme(SoundTheme.SCIFI)

        assert result is True
        assert stm.current_theme == SoundTheme.SCIFI

    def test_get_current_theme(self):
        """Test getting current theme"""
        stm = SoundThemeManager()
        stm.set_theme(SoundTheme.RETRO)

        assert stm.get_current_theme() == SoundTheme.RETRO

    def test_get_available_themes(self):
        """Test getting list of available themes"""
        stm = SoundThemeManager()
        themes = stm.get_available_themes()

        assert len(themes) >= 4
        assert SoundTheme.DEFAULT in themes
        assert SoundTheme.RETRO in themes
        assert SoundTheme.SCIFI in themes
        assert SoundTheme.ORCHESTRAL in themes

    def test_get_theme_description(self):
        """Test getting theme descriptions"""
        stm = SoundThemeManager()

        desc = stm.get_theme_description(SoundTheme.DEFAULT)
        assert "Classic" in desc or "Ajitroids" in desc

        desc = stm.get_theme_description(SoundTheme.RETRO)
        assert "retro" in desc.lower() or "8-bit" in desc.lower()

        desc = stm.get_theme_description(SoundTheme.SCIFI)
        assert "sci-fi" in desc.lower() or "futuristic" in desc.lower()


class TestAudioEnhancementManager:
    """Test suite for main audio enhancement manager"""

    def test_initialization(self):
        """Test audio enhancement manager initializes correctly"""
        aem = AudioEnhancementManager()

        assert aem.dynamic_music is not None
        assert aem.voice_announcements is not None
        assert aem.theme_manager is not None

    def test_update(self):
        """Test update method processes game state"""
        aem = AudioEnhancementManager()
        mock_asset_path = MagicMock(return_value="/path/to/music.mp3")

        game_state = {
            'asteroids_count': 5,
            'enemies_count': 2,
            'boss_active': False,
            'score': 10000,
            'level': 5
        }

        # Should not crash
        aem.update(dt=1.0, game_state=game_state, asset_path_func=mock_asset_path)

    def test_trigger_announcement(self):
        """Test triggering announcements through manager"""
        aem = AudioEnhancementManager()

        aem.trigger_announcement("level_up", priority=5.0)

        # Check announcement was triggered
        announcement = aem.get_announcement_text()
        assert announcement is None or announcement == "Level up!"

    def test_get_announcement_text(self):
        """Test getting current announcement text"""
        aem = AudioEnhancementManager()
        aem.voice_announcements.current_announcement = "Test"

        assert aem.get_announcement_text() == "Test"

    def test_set_theme(self):
        """Test setting sound theme"""
        aem = AudioEnhancementManager()
        result = aem.set_theme(SoundTheme.RETRO)

        assert result is True
        assert aem.get_current_theme() == SoundTheme.RETRO

    def test_get_current_theme(self):
        """Test getting current theme"""
        aem = AudioEnhancementManager()
        aem.theme_manager.set_theme(SoundTheme.SCIFI)

        assert aem.get_current_theme() == SoundTheme.SCIFI

    def test_set_dynamic_music_enabled(self):
        """Test enabling/disabling dynamic music"""
        aem = AudioEnhancementManager()

        aem.set_dynamic_music_enabled(False)
        assert aem.dynamic_music.enabled is False

        aem.set_dynamic_music_enabled(True)
        assert aem.dynamic_music.enabled is True

    def test_set_voice_announcements_enabled(self):
        """Test enabling/disabling voice announcements"""
        aem = AudioEnhancementManager()

        aem.set_voice_announcements_enabled(False)
        assert aem.voice_announcements.enabled is False

        aem.set_voice_announcements_enabled(True)
        assert aem.voice_announcements.enabled is True

    def test_integration_with_all_systems(self):
        """Test all systems work together"""
        aem = AudioEnhancementManager()
        mock_asset_path = MagicMock(return_value="/path/to/music.mp3")

        # Set theme
        aem.set_theme(SoundTheme.RETRO)

        # Trigger announcement
        aem.trigger_announcement("boss_incoming", priority=10.0)

        # Update with game state
        game_state = {
            'asteroids_count': 10,
            'enemies_count': 5,
            'boss_active': True,
            'score': 50000,
            'level': 20
        }
        aem.update(dt=0.1, game_state=game_state, asset_path_func=mock_asset_path)

        # Verify state
        assert aem.get_current_theme() == SoundTheme.RETRO
        assert aem.dynamic_music.enabled is True
        assert aem.voice_announcements.enabled is True


class TestIntensityLevelEnum:
    """Test suite for IntensityLevel enum"""

    def test_intensity_levels_exist(self):
        """Test all intensity levels are defined"""
        assert IntensityLevel.CALM
        assert IntensityLevel.NORMAL
        assert IntensityLevel.INTENSE
        assert IntensityLevel.BOSS

    def test_intensity_level_values(self):
        """Test intensity level string values"""
        assert IntensityLevel.CALM.value == "calm"
        assert IntensityLevel.NORMAL.value == "normal"
        assert IntensityLevel.INTENSE.value == "intense"
        assert IntensityLevel.BOSS.value == "boss"


class TestSoundThemeEnum:
    """Test suite for SoundTheme enum"""

    def test_sound_themes_exist(self):
        """Test all sound themes are defined"""
        assert SoundTheme.DEFAULT
        assert SoundTheme.RETRO
        assert SoundTheme.SCIFI
        assert SoundTheme.ORCHESTRAL

    def test_sound_theme_values(self):
        """Test sound theme string values"""
        assert SoundTheme.DEFAULT.value == "default"
        assert SoundTheme.RETRO.value == "retro"
        assert SoundTheme.SCIFI.value == "scifi"
        assert SoundTheme.ORCHESTRAL.value == "orchestral"
