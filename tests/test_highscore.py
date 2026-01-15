import pytest
import pygame
import os
import json
import sys
from modul.highscore import HighscoreManager, HighscoreInput, HighscoreDisplay
from modul.constants import HIGHSCORE_FILE, HIGHSCORE_MAX_ENTRIES, HIGHSCORE_NAME_LENGTH


@pytest.fixture(autouse=True)
def init_pygame():
    """Initialize pygame for each test"""
    pygame.init()
    pygame.font.init()
    yield
    pygame.quit()


@pytest.fixture
def clean_highscore_file(tmp_path, monkeypatch):
    """Isolate highscore file per test run"""
    hs_file = tmp_path / "highscores.json"
    monkeypatch.setattr("modul.constants.HIGHSCORE_FILE", str(hs_file), raising=False)
    # Also patch any locally imported constant within this module
    monkeypatch.setattr(sys.modules[__name__], "HIGHSCORE_FILE", str(hs_file), raising=False)

    if hs_file.exists():
        hs_file.unlink()
    yield
    if hs_file.exists():
        hs_file.unlink()


class TestHighscoreManager:
    def test_highscore_add(self):
        hs = HighscoreManager()
        hs.add_highscore("Player1", 99999)
        assert any(entry["score"] == 99999 for entry in hs.highscores)

    def test_highscore_order(self):
        hs = HighscoreManager()
        hs.add_highscore("A", 10000)
        hs.add_highscore("B", 20000)
        scores = hs.highscores
        assert scores[0]["score"] >= scores[1]["score"]

    def test_highscore_initialization(self, clean_highscore_file):
        """Test HighscoreManager initialization"""
        manager = HighscoreManager()
        assert len(manager.highscores) == HIGHSCORE_MAX_ENTRIES
        assert os.path.exists(HIGHSCORE_FILE)

    def test_highscore_load_existing_file(self, clean_highscore_file):
        """Test loading existing highscore file"""
        # Create highscore file
        data = [
            {"name": "AAA", "score": 5000},
            {"name": "BBB", "score": 3000}
        ]
        with open(HIGHSCORE_FILE, "w") as f:
            json.dump(data, f)
        
        manager = HighscoreManager()
        assert len(manager.highscores) == 2
        assert manager.highscores[0]["name"] == "AAA"
        assert manager.highscores[0]["score"] == 5000

    def test_highscore_load_no_file(self, clean_highscore_file):
        """Test loading when no file exists creates default scores"""
        manager = HighscoreManager()
        assert len(manager.highscores) == HIGHSCORE_MAX_ENTRIES
        # Default scores should be in descending order
        for i in range(len(manager.highscores) - 1):
            assert manager.highscores[i]["score"] >= manager.highscores[i+1]["score"]

    def test_highscore_save(self, clean_highscore_file):
        """Test saving highscores"""
        manager = HighscoreManager()
        manager.highscores = [{"name": "TST", "score": 1234}]
        manager.save_highscores()
        
        # Verify saved
        with open(HIGHSCORE_FILE, "r") as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]["name"] == "TST"
        assert data[0]["score"] == 1234

    def test_highscore_is_highscore_yes(self, clean_highscore_file):
        """Test is_highscore returns True for high score"""
        manager = HighscoreManager()
        manager.highscores = [{"name": "AAA", "score": 1000}]
        
        assert manager.is_highscore(2000) is True

    def test_highscore_is_highscore_no(self, clean_highscore_file):
        """Test is_highscore returns False for low score"""
        manager = HighscoreManager()
        manager.highscores = [{"name": "AAA", "score": i * 1000} for i in range(HIGHSCORE_MAX_ENTRIES, 0, -1)]
        
        assert manager.is_highscore(100) is False

    def test_highscore_is_highscore_not_full(self, clean_highscore_file):
        """Test is_highscore returns True when list not full"""
        manager = HighscoreManager()
        manager.highscores = [{"name": "AAA", "score": 1000}]
        
        assert manager.is_highscore(100) is True

    def test_highscore_add_formats_name(self, clean_highscore_file):
        """Test add_highscore formats name correctly"""
        manager = HighscoreManager()
        manager.highscores = []
        
        manager.add_highscore("test", 1000)
        
        assert manager.highscores[0]["name"] == "TES"
        assert len(manager.highscores[0]["name"]) == HIGHSCORE_NAME_LENGTH

    def test_highscore_add_pads_short_name(self, clean_highscore_file):
        """Test add_highscore pads short names"""
        manager = HighscoreManager()
        manager.highscores = []
        
        manager.add_highscore("X", 1000)
        
        assert len(manager.highscores[0]["name"]) == HIGHSCORE_NAME_LENGTH
        assert manager.highscores[0]["name"].startswith("X")

    def test_highscore_add_filters_invalid_chars(self, clean_highscore_file):
        """Test add_highscore filters invalid characters"""
        manager = HighscoreManager()
        manager.highscores = []
        
        manager.add_highscore("A!@#B$C", 1000)
        
        # Should only keep valid chars
        assert "!" not in manager.highscores[0]["name"]
        assert "@" not in manager.highscores[0]["name"]

    def test_highscore_add_sorts_by_score(self, clean_highscore_file):
        """Test add_highscore maintains sorted order"""
        manager = HighscoreManager()
        manager.highscores = []
        
        manager.add_highscore("AAA", 1000)
        manager.add_highscore("BBB", 5000)
        manager.add_highscore("CCC", 3000)
        
        assert manager.highscores[0]["score"] == 5000
        assert manager.highscores[1]["score"] == 3000
        assert manager.highscores[2]["score"] == 1000

    def test_highscore_add_limits_entries(self, clean_highscore_file):
        """Test add_highscore limits to max entries"""
        manager = HighscoreManager()
        manager.highscores = []
        
        # Add more than max
        for i in range(HIGHSCORE_MAX_ENTRIES + 5):
            manager.add_highscore(f"A{i:02d}", i * 100)
        
        assert len(manager.highscores) == HIGHSCORE_MAX_ENTRIES

    def test_highscore_add_returns_position(self, clean_highscore_file):
        """Test add_highscore returns correct position"""
        manager = HighscoreManager()
        manager.highscores = []
        
        pos = manager.add_highscore("AAA", 5000)
        assert pos == 0
        
        pos = manager.add_highscore("BBB", 3000)
        assert pos == 1
        
        pos = manager.add_highscore("CCC", 7000)
        assert pos == 0

    def test_highscore_load_error_handling(self, clean_highscore_file):
        """Test error handling when loading corrupted file"""
        # Create corrupted file
        with open(HIGHSCORE_FILE, "w") as f:
            f.write("invalid json {")
        
        manager = HighscoreManager()
        # Should have fallback scores
        assert len(manager.highscores) == HIGHSCORE_MAX_ENTRIES


class TestHighscoreInput:
    def test_highscore_input_initialization(self):
        """Test HighscoreInput initialization"""
        input_handler = HighscoreInput(1000)
        assert input_handler.score == 1000
        assert len(input_handler.name) == HIGHSCORE_NAME_LENGTH
        assert all(isinstance(ch, str) and len(ch) == 1 for ch in input_handler.name)
        assert input_handler.current_pos == 0
        assert input_handler.done is False

    def test_highscore_input_return_key(self):
        """Test RETURN key completes input"""
        input_handler = HighscoreInput(1000)
        input_handler.name = ["B", "O", "B"]
        
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN})
        result = input_handler.update([event])
        
        assert result == "BOB"
        assert input_handler.done is True

    def test_highscore_input_left_key(self):
        """Test LEFT key moves cursor"""
        input_handler = HighscoreInput(1000)
        input_handler.current_pos = 2
        
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_LEFT})
        input_handler.update([event])
        
        assert input_handler.current_pos == 1

    def test_highscore_input_right_key(self):
        """Test RIGHT key moves cursor"""
        input_handler = HighscoreInput(1000)
        input_handler.current_pos = 0
        
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RIGHT})
        input_handler.update([event])
        
        assert input_handler.current_pos == 1

    def test_highscore_input_backspace_key(self):
        """Test BACKSPACE key moves cursor back"""
        input_handler = HighscoreInput(1000)
        input_handler.current_pos = 2
        
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_BACKSPACE})
        input_handler.update([event])
        
        assert input_handler.current_pos == 1

    def test_highscore_input_backspace_at_start(self):
        """Test BACKSPACE at start doesn't go negative"""
        input_handler = HighscoreInput(1000)
        input_handler.current_pos = 0
        
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_BACKSPACE})
        input_handler.update([event])
        
        assert input_handler.current_pos == 0

    def test_highscore_input_right_at_end(self):
        """Test RIGHT at end doesn't exceed limit"""
        input_handler = HighscoreInput(1000)
        input_handler.current_pos = HIGHSCORE_NAME_LENGTH - 1
        
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RIGHT})
        input_handler.update([event])
        
        assert input_handler.current_pos == HIGHSCORE_NAME_LENGTH - 1

    def test_highscore_input_draw(self):
        """Test drawing highscore input"""
        input_handler = HighscoreInput(1000)
        screen = pygame.Surface((800, 600))
        input_handler.draw(screen)  # Should not raise exception

    def test_highscore_input_up_key_cycles_chars(self):
        """Test UP key cycles characters forward"""
        input_handler = HighscoreInput(1000)
        input_handler.current_pos = 0
        initial_char = input_handler.name[0]
        
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_UP})
        input_handler.update([event])
        
        # Character should have changed
        assert input_handler.name[0] != initial_char

    def test_highscore_input_down_key_cycles_chars(self):
        """Test DOWN key cycles characters backward"""
        input_handler = HighscoreInput(1000)
        input_handler.current_pos = 0
        initial_char = input_handler.name[0]
        
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_DOWN})
        input_handler.update([event])
        
        # Character should have changed
        assert input_handler.name[0] != initial_char

    def test_highscore_input_no_events(self):
        """Test update with no events"""
        input_handler = HighscoreInput(1000)
        
        result = input_handler.update([])
        
        assert result is None
        assert input_handler.done is False


class TestHighscoreDisplay:
    """Test suite for HighscoreDisplay class"""

    def test_highscore_display_initialization(self):
        """Test HighscoreDisplay initialization"""
        manager = HighscoreManager()
        display = HighscoreDisplay(manager)
        
        assert display.highscore_manager is manager
        assert display.background_alpha == 0
        assert display.fade_in is True
        assert display.input_cooldown == 0
        assert display.back_button["selected"] is True

    def test_highscore_display_update_fade_in(self):
        """Test fade-in animation"""
        manager = HighscoreManager()
        display = HighscoreDisplay(manager)
        
        display.update(0.1, [])
        
        assert display.background_alpha > 0

    def test_highscore_display_update_fade_complete(self):
        """Test fade-in completes"""
        manager = HighscoreManager()
        display = HighscoreDisplay(manager)
        
        display.update(1.0, [])
        
        assert display.fade_in is False
        assert display.background_alpha == 200

    def test_highscore_display_update_button_animation(self):
        """Test button hover animation"""
        manager = HighscoreManager()
        display = HighscoreDisplay(manager)
        
        display.update(0.1, [])
        
        assert display.back_button["hover_animation"] > 0

    def test_highscore_display_update_input_cooldown(self):
        """Test input cooldown decrements"""
        manager = HighscoreManager()
        display = HighscoreDisplay(manager)
        display.input_cooldown = 1.0
        
        display.update(0.5, [])
        
        assert display.input_cooldown == 0.5

    def test_highscore_display_update_space_returns_main_menu(self):
        """Test SPACE key returns to main menu"""
        manager = HighscoreManager()
        display = HighscoreDisplay(manager)
        
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE})
        result = display.update(0.1, [event])
        
        assert result == "main_menu"

    def test_highscore_display_update_return_returns_main_menu(self):
        """Test RETURN key returns to main menu"""
        manager = HighscoreManager()
        display = HighscoreDisplay(manager)
        
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN})
        result = display.update(0.1, [event])
        
        assert result == "main_menu"

    def test_highscore_display_update_escape_returns_main_menu(self):
        """Test ESCAPE key returns to main menu"""
        manager = HighscoreManager()
        display = HighscoreDisplay(manager)
        
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})
        result = display.update(0.1, [event])
        
        assert result == "main_menu"

    def test_highscore_display_update_cooldown_blocks_input(self):
        """Test input cooldown blocks repeated input"""
        manager = HighscoreManager()
        display = HighscoreDisplay(manager)
        display.input_cooldown = 1.0
        
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE})
        result = display.update(0.1, [event])
        
        assert result is None

    def test_highscore_display_draw(self):
        """Test drawing highscore display"""
        manager = HighscoreManager()
        display = HighscoreDisplay(manager)
        screen = pygame.Surface((800, 600))
        
        display.draw(screen)  # Should not raise exception

    def test_highscore_display_draw_with_entries(self):
        """Test drawing with highscore entries"""
        manager = HighscoreManager()
        manager.highscores = [
            {"name": "AAA", "score": 5000},
            {"name": "BBB", "score": 4000},
            {"name": "CCC", "score": 3000}
        ]
        display = HighscoreDisplay(manager)
        screen = pygame.Surface((800, 600))
        
        display.draw(screen)

    def test_highscore_display_draw_medal_colors(self):
        """Test first three places have medal colors"""
        manager = HighscoreManager()
        manager.highscores = [
            {"name": "1ST", "score": 5000},
            {"name": "2ND", "score": 4000},
            {"name": "3RD", "score": 3000},
            {"name": "4TH", "score": 2000}
        ]
        display = HighscoreDisplay(manager)
        screen = pygame.Surface((800, 600))
        
        display.draw(screen)  # Gold, silver, bronze should be rendered
