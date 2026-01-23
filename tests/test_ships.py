"""Tests for ShipManager persistence and Ship rendering utilities."""

import json
import os

import pygame
import pytest

from modul.ships import ShipManager, ShipRenderer


@pytest.fixture(autouse=True)
def init_pygame():
    """Initialize pygame for each test"""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def clean_ships_file(tmp_path, monkeypatch):
    """Run ship persistence tests in an isolated directory"""
    monkeypatch.chdir(tmp_path)
    ships_file = tmp_path / "ships.json"
    monkeypatch.setattr("modul.ships.SHIPS_FILE", str(ships_file), raising=False)

    if ships_file.exists():
        ships_file.unlink()
    yield
    if ships_file.exists():
        ships_file.unlink()


class TestShipManager:
    def test_ship_manager_initialization(self, clean_ships_file):
        """Test ShipManager initialization"""
        manager = ShipManager()
        assert manager.current_ship == "standard"
        assert len(manager.ships) >= 4
        assert "standard" in manager.ships
        assert manager.ships["standard"]["unlocked"] is True

    def test_load_unlocked_ships_no_file(self, clean_ships_file):
        """Test loading unlocked ships when no file exists"""
        manager = ShipManager()
        assert manager.unlocked_ships == []

    def test_load_unlocked_ships_with_file(self, clean_ships_file):
        """Test loading unlocked ships from file"""
        # Create ships file
        data = {"unlocked_ships": ["speedster", "tank"]}
        with open("ships.json", "w") as f:
            json.dump(data, f)

        manager = ShipManager()
        assert "speedster" in manager.unlocked_ships
        assert "tank" in manager.unlocked_ships

    def test_save_unlocked_ships(self, clean_ships_file):
        """Test saving unlocked ships"""
        manager = ShipManager()
        manager.unlocked_ships = ["speedster", "destroyer"]
        manager.save_unlocked_ships()

        assert os.path.exists("ships.json")

        # Verify saved data
        with open("ships.json", "r") as f:
            data = json.load(f)
        assert "speedster" in data["unlocked_ships"]
        assert "destroyer" in data["unlocked_ships"]

    def test_unlock_ship(self, clean_ships_file):
        """Test unlocking a ship"""
        manager = ShipManager()
        result = manager.unlock_ship("speedster")

        assert result is True
        assert "speedster" in manager.unlocked_ships
        assert manager.ships["speedster"]["unlocked"] is True

    def test_unlock_ship_already_unlocked(self, clean_ships_file):
        """Test unlocking already unlocked ship"""
        manager = ShipManager()
        manager.unlock_ship("speedster")
        result = manager.unlock_ship("speedster")

        assert result is False

    def test_unlock_ship_invalid(self, clean_ships_file):
        """Test unlocking invalid ship"""
        manager = ShipManager()
        result = manager.unlock_ship("nonexistent")

        assert result is False

    def test_unlock_ship_with_notification(self, clean_ships_file):
        """Test unlocking ship with notification callback"""
        manager = ShipManager()
        called = []

        def callback(title, message):
            called.append((title, message))

        result = manager.unlock_ship_with_notification("tank", callback)

        assert result is True
        assert len(called) == 1
        assert "tank" in manager.unlocked_ships

    def test_unlock_ship_with_notification_already_unlocked(self, clean_ships_file):
        """Test notification not called for already unlocked ship"""
        manager = ShipManager()
        manager.unlock_ship("destroyer")

        called = []

        def callback(title, message):
            """
            Append the given title and message as a tuple to the outer `called` list.
            
            Parameters:
                title (str): The title to record.
                message (str): The message to record.
            """
            called.append((title, message))

        result = manager.unlock_ship_with_notification("destroyer", callback)

        assert result is False
        assert len(called) == 0

    def test_check_unlock_conditions_speedster(self, clean_ships_file):
        """Test unlock condition for speedster"""
        manager = ShipManager()
        result = manager.check_unlock_conditions(50, "easy")

        assert result is True
        assert manager.ships["speedster"]["unlocked"] is True

    def test_check_unlock_conditions_tank(self, clean_ships_file):
        """Test unlock condition for tank"""
        manager = ShipManager()
        result = manager.check_unlock_conditions(50, "normal")

        assert result is True
        assert manager.ships["tank"]["unlocked"] is True

    def test_check_unlock_conditions_destroyer(self, clean_ships_file):
        """Test unlock condition for destroyer"""
        manager = ShipManager()
        result = manager.check_unlock_conditions(50, "hard")

        assert result is True
        assert manager.ships["destroyer"]["unlocked"] is True

    def test_check_unlock_conditions_insufficient_level(self, clean_ships_file):
        """Test no unlock with insufficient level"""
        manager = ShipManager()
        result = manager.check_unlock_conditions(30, "easy")

        assert result is False

    def test_check_unlock_conditions_with_callback(self, clean_ships_file):
        """Test unlock conditions with callback"""
        manager = ShipManager()
        called = []

        def callback(title, message):
            called.append((title, message))

        manager.check_unlock_conditions(50, "easy", callback)

        assert len(called) >= 1

    def test_get_ship_data(self, clean_ships_file):
        """Test getting ship data"""
        manager = ShipManager()
        data = manager.get_ship_data("standard")

        assert data["name"] == "Standard Fighter"
        assert "speed_multiplier" in data

    def test_get_ship_data_invalid(self, clean_ships_file):
        """Test getting data for invalid ship returns standard"""
        manager = ShipManager()
        data = manager.get_ship_data("nonexistent")

        assert data["name"] == "Standard Fighter"

    def test_get_available_ships(self, clean_ships_file):
        """Test getting all available ships"""
        manager = ShipManager()
        ships = manager.get_available_ships()

        assert len(ships) >= 4
        assert "standard" in ships
        assert "speedster" in ships

    def test_get_unlocked_ships(self, clean_ships_file):
        """Test getting unlocked ships"""
        manager = ShipManager()
        manager.unlock_ship("tank")

        unlocked = manager.get_unlocked_ships()

        assert "standard" in unlocked
        assert "tank" in unlocked
        assert "speedster" not in unlocked

    def test_set_current_ship(self, clean_ships_file):
        """Test setting current ship"""
        manager = ShipManager()
        manager.unlock_ship("speedster")

        result = manager.set_current_ship("speedster")

        assert result is True
        assert manager.current_ship == "speedster"

    def test_set_current_ship_locked(self, clean_ships_file):
        """Test cannot set locked ship as current"""
        manager = ShipManager()
        result = manager.set_current_ship("destroyer")

        assert result is False
        assert manager.current_ship == "standard"

    def test_set_current_ship_invalid(self, clean_ships_file):
        """Test cannot set invalid ship as current"""
        manager = ShipManager()
        result = manager.set_current_ship("nonexistent")

        assert result is False

    def test_get_current_ship_data(self, clean_ships_file):
        """Test getting current ship data"""
        manager = ShipManager()
        data = manager.get_current_ship_data()

        assert data["name"] == "Standard Fighter"

    def test_is_ship_unlocked(self, clean_ships_file):
        """Test checking if ship is unlocked"""
        manager = ShipManager()

        assert manager.is_ship_unlocked("standard") is True
        assert manager.is_ship_unlocked("speedster") is False

        manager.unlock_ship("speedster")
        assert manager.is_ship_unlocked("speedster") is True

    def test_is_ship_unlocked_invalid(self, clean_ships_file):
        """Test checking invalid ship"""
        manager = ShipManager()
        assert manager.is_ship_unlocked("nonexistent") is False

    def test_check_all_ships_unlocked(self, clean_ships_file):
        """Test checking all ships unlocked achievement"""
        manager = ShipManager()

        # Mock achievement system
        class MockAchievements:
            def __init__(self):
                self.unlocked = []

            def unlock(self, achievement):
                self.unlocked.append(achievement)

        achievements = MockAchievements()

        # Unlock all ships (standard is always unlocked, so skip it)
        for ship_id in manager.ships.keys():
            if ship_id != "standard":
                manager.unlock_ship(ship_id)

        # Ensure `unlocked_ships` includes every ship id (including `standard`)
        manager.unlocked_ships = list(manager.ships.keys())
        for ship_id in manager.ships:
            manager.ships[ship_id]["unlocked"] = True

        manager.check_all_ships_unlocked(achievements)

        # Verify the correct achievement is unlocked when all ships are unlocked.
        assert any(
            a == "Fleet Commander" or getattr(a, "name", None) == "Fleet Commander"
            for a in achievements.unlocked
        )

    def test_ship_properties(self, clean_ships_file):
        """Test ship properties are complete"""
        manager = ShipManager()

        for ship_id, ship_data in manager.ships.items():
            assert "name" in ship_data
            assert "description" in ship_data
            assert "unlocked" in ship_data
            assert "speed_multiplier" in ship_data
            assert "turn_speed_multiplier" in ship_data
            assert "special_ability" in ship_data


class TestShipRenderer:
    def test_draw_ship_triangle(self):
        """Test drawing triangle ship"""
        screen = pygame.Surface((800, 600))
        ShipRenderer.draw_ship(screen, 100, 100, 0, "triangle")
        # Should not raise exception

    def test_draw_ship_standard(self):
        """Test drawing standard ship"""
        screen = pygame.Surface((800, 600))
        ShipRenderer.draw_ship(screen, 100, 100, 0, "standard")
        # Should not raise exception

    def test_draw_ship_arrow(self):
        """Test drawing arrow ship"""
        screen = pygame.Surface((800, 600))
        ShipRenderer.draw_ship(screen, 100, 100, 0, "arrow")
        # Should not raise exception

    def test_draw_ship_heavy(self):
        """Test drawing heavy ship"""
        screen = pygame.Surface((800, 600))
        ShipRenderer.draw_ship(screen, 100, 100, 0, "heavy")
        # Should not raise exception

    def test_draw_ship_destroyer(self):
        """Test drawing destroyer ship"""
        screen = pygame.Surface((800, 600))
        ShipRenderer.draw_ship(screen, 100, 100, 0, "destroyer")
        # Should not raise exception

    def test_draw_ship_with_rotation(self):
        """Test drawing ship with rotation"""
        screen = pygame.Surface((800, 600))
        for angle in [0, 45, 90, 180, 270]:
            ShipRenderer.draw_ship(screen, 100, 100, angle, "standard")
        # Should not raise exception

    def test_draw_ship_with_scale(self):
        """Test drawing ship with different scales"""
        screen = pygame.Surface((800, 600))
        for scale in [0.5, 1.0, 1.5, 2.0]:
            ShipRenderer.draw_ship(screen, 100, 100, 0, "standard", scale=scale)
        # Should not raise exception

    def test_draw_ship_with_color(self):
        """Test drawing ship with different colors"""
        screen = pygame.Surface((800, 600))
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        for color in colors:
            ShipRenderer.draw_ship(screen, 100, 100, 0, "standard", color=color)
        # Should not raise exception

    def test_draw_triangle_ship(self):
        """Test drawing triangle ship directly"""
        screen = pygame.Surface((800, 600))
        ShipRenderer.draw_triangle_ship(screen, 100, 100, 0, 1.0, (255, 255, 255))
        # Should not raise exception

    def test_draw_arrow_ship(self):
        """Test drawing arrow ship directly"""
        screen = pygame.Surface((800, 600))
        ShipRenderer.draw_arrow_ship(screen, 100, 100, 0, 1.0, (255, 255, 0))
        # Should not raise exception

    def test_draw_heavy_ship(self):
        """Test drawing heavy ship directly"""
        screen = pygame.Surface((800, 600))
        ShipRenderer.draw_heavy_ship(screen, 100, 100, 0, 1.0, (0, 255, 0))
        # Should not raise exception

    def test_draw_destroyer_ship(self):
        """Test drawing destroyer ship directly"""
        screen = pygame.Surface((800, 600))
        ShipRenderer.draw_destroyer_ship(screen, 100, 100, 0, 1.0, (255, 0, 0))
        # Should not raise exception