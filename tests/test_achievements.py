import pytest
import json
import os
from unittest.mock import MagicMock, patch, mock_open
from modul.achievements import Achievement, AchievementSystem


@pytest.fixture
def clean_achievements_file():
    """Remove achievements file before and after test"""
    achievements_file = "achievements.json"
    if os.path.exists(achievements_file):
        os.remove(achievements_file)
    yield
    if os.path.exists(achievements_file):
        os.remove(achievements_file)


class TestAchievement:
    """Test suite for Achievement class"""

    def test_achievement_initialization(self):
        """Test achievement initializes correctly"""
        achievement = Achievement("Test Achievement", "Test description")
        
        assert achievement.name == "Test Achievement"
        assert achievement.description == "Test description"
        assert achievement.unlocked is False

    def test_achievement_unlock(self):
        """Test unlocking an achievement"""
        achievement = Achievement("Test", "Description")
        
        achievement.unlock()
        
        assert achievement.unlocked is True

    def test_achievement_unlock_idempotent(self):
        """Test unlocking an already unlocked achievement"""
        achievement = Achievement("Test", "Description")
        achievement.unlock()
        achievement.unlock()
        
        assert achievement.unlocked is True


class TestAchievementSystem:
    """Test suite for AchievementSystem class"""

    def test_achievement_system_initialization(self, clean_achievements_file):
        """Test system initializes with standard achievements"""
        system = AchievementSystem()
        
        assert len(system.achievements) > 0
        assert system.notification_callback is None

    def test_achievement_system_standard_achievements(self, clean_achievements_file):
        """Test standard achievements are initialized"""
        system = AchievementSystem()
        
        achievement_names = [a.name for a in system.achievements]
        assert "First Blood" in achievement_names
        assert "Survivor" in achievement_names
        assert "Asteroid Hunter" in achievement_names
        assert "Power User" in achievement_names
        assert "Boss Slayer" in achievement_names

    def test_achievement_system_all_locked_initially(self, clean_achievements_file):
        """Test all achievements start locked"""
        system = AchievementSystem()
        
        for achievement in system.achievements:
            assert achievement.unlocked is False

    def test_set_notification_callback(self, clean_achievements_file):
        """Test setting notification callback"""
        system = AchievementSystem()
        callback = MagicMock()
        
        system.set_notification_callback(callback)
        
        assert system.notification_callback is callback

    def test_unlock_achievement(self, clean_achievements_file):
        """Test unlocking an achievement"""
        system = AchievementSystem()
        
        result = system.unlock("First Blood")
        
        assert result is True
        assert system.is_unlocked("First Blood")

    def test_unlock_achievement_calls_callback(self, clean_achievements_file):
        """Test unlock calls notification callback"""
        system = AchievementSystem()
        callback = MagicMock()
        system.set_notification_callback(callback)
        
        system.unlock("First Blood")
        
        callback.assert_called_once()

    def test_unlock_achievement_saves(self, clean_achievements_file):
        """Test unlock saves achievements file"""
        system = AchievementSystem()
        
        system.unlock("First Blood")
        
        assert os.path.exists("achievements.json")

    def test_unlock_already_unlocked(self, clean_achievements_file):
        """Test unlocking already unlocked achievement"""
        system = AchievementSystem()
        
        system.unlock("First Blood")
        result = system.unlock("First Blood")
        
        assert result is False

    def test_unlock_nonexistent_achievement(self, clean_achievements_file):
        """Test unlocking nonexistent achievement"""
        system = AchievementSystem()
        
        result = system.unlock("Nonexistent Achievement")
        
        assert result is False

    def test_is_unlocked_true(self, clean_achievements_file):
        """Test is_unlocked returns True for unlocked achievement"""
        system = AchievementSystem()
        system.unlock("First Blood")
        
        assert system.is_unlocked("First Blood") is True

    def test_is_unlocked_false(self, clean_achievements_file):
        """Test is_unlocked returns False for locked achievement"""
        system = AchievementSystem()
        
        assert system.is_unlocked("Survivor") is False

    def test_is_unlocked_nonexistent(self, clean_achievements_file):
        """Test is_unlocked returns False for nonexistent achievement"""
        system = AchievementSystem()
        
        assert system.is_unlocked("Nonexistent") is False

    def test_save_unlocked_achievements(self, clean_achievements_file):
        """Test saving unlocked achievements"""
        system = AchievementSystem()
        system.unlock("First Blood")
        system.unlock("Survivor")
        
        system.save_unlocked_achievements()
        
        with open("achievements.json", "r") as f:
            data = json.load(f)
        
        assert len(data) == 2
        names = [item["name"] for item in data]
        assert "First Blood" in names
        assert "Survivor" in names

    def test_save_unlocked_achievements_none_unlocked(self, clean_achievements_file):
        """Test saving when no achievements unlocked"""
        system = AchievementSystem()
        
        system.save_unlocked_achievements()
        
        # Should not create file or create empty file
        if os.path.exists("achievements.json"):
            with open("achievements.json", "r") as f:
                data = json.load(f)
            assert len(data) == 0

    def test_load_unlocked_achievements_no_file(self, clean_achievements_file):
        """Test loading when no file exists"""
        system = AchievementSystem()
        
        # Should not crash
        assert len(system.achievements) > 0

    def test_load_unlocked_achievements_with_file(self, clean_achievements_file):
        """Test loading from existing file"""
        # Create achievements file
        data = [
            {"name": "First Blood", "description": "Destroy your first asteroid.", "unlocked": True}
        ]
        with open("achievements.json", "w") as f:
            json.dump(data, f)
        
        system = AchievementSystem()
        
        assert system.is_unlocked("First Blood")

    def test_load_unlocked_achievements_corrupted_file(self, clean_achievements_file):
        """Test loading from corrupted file"""
        # Create corrupted file
        with open("achievements.json", "w") as f:
            f.write("invalid json {")
        
        system = AchievementSystem()
        
        # Should handle error gracefully
        assert len(system.achievements) > 0

    def test_load_achievements_method(self, clean_achievements_file):
        """Test load_achievements method (empty implementation)"""
        system = AchievementSystem()
        
        system.load_achievements()  # Should not crash

    def test_save_achievements_method(self, clean_achievements_file):
        """Test save_achievements calls save_unlocked_achievements"""
        system = AchievementSystem()
        system.unlock("First Blood")
        
        system.save_achievements()
        
        assert os.path.exists("achievements.json")

    def test_unlock_achievement_method_with_ascii(self, clean_achievements_file):
        """Test unlock_achievement method (deprecated)"""
        system = AchievementSystem()
        callback = MagicMock()
        system.set_notification_callback(callback)
        
        system.unlock_achievement("First Blood")
        
        assert system.is_unlocked("First Blood")
        # Should call callback with ASCII art
        callback.assert_called_once()

    def test_unlock_achievement_already_unlocked(self, clean_achievements_file):
        """Test unlock_achievement with already unlocked achievement"""
        system = AchievementSystem()
        callback = MagicMock()
        system.set_notification_callback(callback)
        
        system.unlock_achievement("First Blood")
        callback.reset_mock()
        system.unlock_achievement("First Blood")
        
        # Should not call callback again
        callback.assert_not_called()

    def test_check_fleet_commander_all_ships(self, clean_achievements_file):
        """Test check_fleet_commander with all ships unlocked"""
        system = AchievementSystem()
        ships_mock = MagicMock()
        ships_mock.unlocked_ships = ["ship1", "ship2", "ship3", "ship4"]
        ships_mock.ships = {"ship1": {}, "ship2": {}, "ship3": {}, "ship4": {}}
        
        system.check_fleet_commander(ships_mock)
        
        assert system.is_unlocked("Fleet Commander")

    def test_check_fleet_commander_not_all_ships(self, clean_achievements_file):
        """Test check_fleet_commander without all ships"""
        system = AchievementSystem()
        ships_mock = MagicMock()
        ships_mock.unlocked_ships = ["ship1", "ship2"]
        ships_mock.ships = {"ship1": {}, "ship2": {}, "ship3": {}, "ship4": {}}
        
        system.check_fleet_commander(ships_mock)
        
        assert not system.is_unlocked("Fleet Commander")

    def test_initialize_standard_achievements_count(self, clean_achievements_file):
        """Test correct number of standard achievements"""
        system = AchievementSystem()
        
        assert len(system.achievements) == 11

    def test_achievements_have_descriptions(self, clean_achievements_file):
        """Test all achievements have descriptions"""
        system = AchievementSystem()
        
        for achievement in system.achievements:
            assert achievement.name
            assert achievement.description
            assert len(achievement.description) > 0


def test_achievement_unlock():
    system = AchievementSystem()
    system.unlock("First Blood")
    assert system.is_unlocked("First Blood")


def test_achievement_not_unlocked():
    system = AchievementSystem()
    assert not system.is_unlocked("Survivor")
