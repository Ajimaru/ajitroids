import pytest
import pygame
import time
from unittest.mock import MagicMock, patch
from modul.achievement_notification import AchievementNotification, AchievementNotificationManager
from modul.constants import SCREEN_WIDTH


@pytest.fixture(autouse=True)
def init_pygame():
    """Initialize pygame for each test"""
    pygame.init()
    pygame.font.init()
    yield
    pygame.quit()


class TestAchievementNotification:
    """Test suite for AchievementNotification class"""

    def test_notification_initialization(self):
        """Test notification initializes with correct values"""
        notification = AchievementNotification("Test Achievement", "Test description")
        
        assert notification.name == "Test Achievement"
        assert notification.description == "Test description"
        assert notification.display_time == 4.0
        assert notification.fade_time == 1.0
        assert notification.animation_progress == 0.0
        assert notification.is_fading_out is False
        assert notification.target_x == SCREEN_WIDTH - 350
        assert notification.target_y == 80
        assert notification.current_x == SCREEN_WIDTH
        assert notification.current_y == notification.target_y
        assert notification.sound_played is False

    def test_notification_update_fade_in(self):
        """Test notification fades in during first second"""
        notification = AchievementNotification("Test", "Description")
        
        # Update during fade-in period
        result = notification.update(0.5)
        
        assert result is True
        assert notification.animation_progress > 0
        assert notification.animation_progress < 1.0
        assert notification.current_x < SCREEN_WIDTH
        assert notification.current_x > notification.target_x

    def test_notification_update_display_phase(self):
        """Test notification stays visible during display phase"""
        notification = AchievementNotification("Test", "Description")
        notification.start_time = time.time() - 2.0  # Simulate 2 seconds elapsed
        
        result = notification.update(0.1)
        
        assert result is True
        assert notification.animation_progress == 1.0
        assert notification.current_x == notification.target_x

    def test_notification_update_fade_out(self):
        """Test notification fades out at the end"""
        notification = AchievementNotification("Test", "Description")
        notification.start_time = time.time() - 3.5  # Near end of display
        
        result = notification.update(0.1)
        
        assert result is True
        assert notification.is_fading_out is True
        assert notification.animation_progress < 1.0

    def test_notification_update_expired(self):
        """Test notification returns False when expired"""
        notification = AchievementNotification("Test", "Description")
        notification.start_time = time.time() - 5.0  # Past display time
        
        result = notification.update(0.1)
        
        assert result is False

    def test_notification_ease_out_function(self):
        """Test ease out animation function"""
        notification = AchievementNotification("Test", "Description")
        
        # Test at various points
        assert notification._ease_out(0.0) == 0.0
        assert notification._ease_out(1.0) == 1.0
        assert 0 < notification._ease_out(0.5) < 1.0

    def test_notification_draw_visible(self):
        """Test drawing when animation_progress > 0"""
        notification = AchievementNotification("Test", "Description")
        notification.animation_progress = 1.0
        screen = pygame.Surface((800, 600))
        
        notification.draw(screen)  # Should not raise exception

    def test_notification_draw_invisible(self):
        """Test drawing when animation_progress <= 0"""
        notification = AchievementNotification("Test", "Description")
        notification.animation_progress = 0.0
        screen = pygame.Surface((800, 600))
        
        notification.draw(screen)  # Should return early without error

    def test_notification_draw_with_long_description(self):
        """Test drawing with long description (truncation)"""
        long_desc = "A" * 50  # Longer than 35 chars
        notification = AchievementNotification("Test", long_desc)
        notification.animation_progress = 1.0
        screen = pygame.Surface((800, 600))
        
        notification.draw(screen)  # Should handle truncation

    def test_notification_draw_with_partial_alpha(self):
        """Test drawing with partial alpha during fade"""
        notification = AchievementNotification("Test", "Description")
        notification.animation_progress = 0.5
        screen = pygame.Surface((800, 600))
        
        notification.draw(screen)  # Should handle partial alpha


class TestAchievementNotificationManager:
    """Test suite for AchievementNotificationManager class"""

    def test_manager_initialization(self):
        """Test manager initializes correctly"""
        manager = AchievementNotificationManager()
        
        assert manager.notifications == []
        assert manager.max_notifications == 3
        assert manager.sounds is None

    def test_manager_initialization_with_sounds(self):
        """Test manager initializes with sounds object"""
        sounds_mock = MagicMock()
        manager = AchievementNotificationManager(sounds=sounds_mock)
        
        assert manager.sounds is sounds_mock

    def test_manager_set_sounds(self):
        """Test setting sounds after initialization"""
        manager = AchievementNotificationManager()
        sounds_mock = MagicMock()
        
        manager.set_sounds(sounds_mock)
        
        assert manager.sounds is sounds_mock

    def test_manager_add_notification(self):
        """Test adding a notification"""
        manager = AchievementNotificationManager()
        
        manager.add_notification("Achievement 1", "Description 1")
        
        assert len(manager.notifications) == 1
        assert manager.notifications[0].name == "Achievement 1"
        assert manager.notifications[0].description == "Description 1"

    def test_manager_add_notification_plays_sound(self):
        """Test adding notification plays achievement sound"""
        sounds_mock = MagicMock()
        sounds_mock.play_achievement = MagicMock()
        manager = AchievementNotificationManager(sounds=sounds_mock)
        
        manager.add_notification("Test", "Description")
        
        sounds_mock.play_achievement.assert_called_once()

    def test_manager_add_notification_no_sounds(self):
        """Test adding notification without sounds doesn't crash"""
        manager = AchievementNotificationManager()
        
        manager.add_notification("Test", "Description")
        
        assert len(manager.notifications) == 1

    def test_manager_add_duplicate_notification(self):
        """Test adding duplicate notification is ignored"""
        manager = AchievementNotificationManager()
        
        manager.add_notification("Achievement 1", "Description 1")
        manager.add_notification("Achievement 1", "Description 1")
        
        assert len(manager.notifications) == 1

    def test_manager_add_multiple_notifications(self):
        """Test adding multiple notifications"""
        manager = AchievementNotificationManager()
        
        manager.add_notification("Achievement 1", "Description 1")
        manager.add_notification("Achievement 2", "Description 2")
        manager.add_notification("Achievement 3", "Description 3")
        
        assert len(manager.notifications) == 3

    def test_manager_max_notifications_limit(self):
        """Test manager limits notifications to max_notifications"""
        manager = AchievementNotificationManager()
        
        # Add more than max
        for i in range(5):
            manager.add_notification(f"Achievement {i}", f"Description {i}")
        
        assert len(manager.notifications) == manager.max_notifications

    def test_manager_notification_positioning(self):
        """Test notifications are positioned correctly"""
        manager = AchievementNotificationManager()
        
        manager.add_notification("Achievement 1", "Description 1")
        manager.add_notification("Achievement 2", "Description 2")
        
        # Second notification should be below first
        assert manager.notifications[1].target_y > manager.notifications[0].target_y
        assert manager.notifications[1].target_y == 80 + 90

    def test_manager_update_removes_expired(self):
        """Test update removes expired notifications"""
        manager = AchievementNotificationManager()
        notification = AchievementNotification("Test", "Description")
        notification.start_time = time.time() - 10.0  # Expired
        manager.notifications.append(notification)
        
        manager.update(0.1)
        
        assert len(manager.notifications) == 0

    def test_manager_update_keeps_active(self):
        """Test update keeps active notifications"""
        manager = AchievementNotificationManager()
        manager.add_notification("Test", "Description")
        
        manager.update(0.1)
        
        assert len(manager.notifications) == 1

    def test_manager_update_repositions_notifications(self):
        """Test update repositions notifications smoothly"""
        manager = AchievementNotificationManager()
        manager.add_notification("Achievement 1", "Description 1")
        manager.add_notification("Achievement 2", "Description 2")
        
        # Set notification positions away from target
        manager.notifications[0].current_y = 0
        manager.notifications[1].current_y = 0
        
        manager.update(0.1)
        
        # Should move towards target
        assert manager.notifications[0].current_y > 0
        assert manager.notifications[1].current_y > 0

    def test_manager_draw(self):
        """Test drawing all notifications"""
        manager = AchievementNotificationManager()
        manager.add_notification("Achievement 1", "Description 1")
        manager.add_notification("Achievement 2", "Description 2")
        screen = pygame.Surface((800, 600))
        
        manager.draw(screen)  # Should not raise exception

    def test_manager_draw_empty(self):
        """Test drawing with no notifications"""
        manager = AchievementNotificationManager()
        screen = pygame.Surface((800, 600))
        
        manager.draw(screen)  # Should not raise exception

    def test_manager_clear_all(self):
        """Test clearing all notifications"""
        manager = AchievementNotificationManager()
        manager.add_notification("Achievement 1", "Description 1")
        manager.add_notification("Achievement 2", "Description 2")
        
        manager.clear_all()
        
        assert len(manager.notifications) == 0

    def test_manager_clear_all_empty(self):
        """Test clearing when already empty"""
        manager = AchievementNotificationManager()
        
        manager.clear_all()
        
        assert len(manager.notifications) == 0
