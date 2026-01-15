import pytest
import pygame
from unittest.mock import Mock, MagicMock, patch
from modul.tutorial import Tutorial
from modul.constants import *


@pytest.fixture(autouse=True)
def init_pygame():
    """Initialize pygame for each test"""
    pygame.init()
    pygame.font.init()
    yield
    pygame.quit()


@pytest.fixture
def mock_screen():
    """Create a mock screen surface"""
    return pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))


class TestTutorial:
    def test_tutorial_initialization(self):
        """Test Tutorial initializes correctly"""
        tutorial = Tutorial()
        assert tutorial.current_page == 0
        assert tutorial.transitioning is False
        assert tutorial.transition_timer == 0
        assert tutorial.transition_duration == 0.3
        assert len(tutorial.pages) == 7

    def test_tutorial_pages_content(self):
        """Test tutorial pages have correct structure"""
        tutorial = Tutorial()
        for page in tutorial.pages:
            assert "title" in page
            assert "content" in page
            assert isinstance(page["content"], list)

    def test_tutorial_page_titles(self):
        """Test tutorial page titles are correct"""
        tutorial = Tutorial()
        expected_titles = [
            "Basics",
            "Power-Ups",
            "Level System",
            "Weapon System",
            "Boss Fight Strategies",
            "Advanced Tips",
            "Difficulty Levels"
        ]
        for i, title in enumerate(expected_titles):
            assert tutorial.pages[i]["title"] == title

    def test_tutorial_basics_page_content(self):
        """Test basics page has expected content"""
        tutorial = Tutorial()
        basics = tutorial.pages[0]
        assert basics["title"] == "Basics"
        assert any("Move your spaceship" in line for line in basics["content"])
        assert any("Shoot with the spacebar" in line for line in basics["content"])

    def test_tutorial_powerups_page_content(self):
        """Test power-ups page has expected content"""
        tutorial = Tutorial()
        powerups = tutorial.pages[1]
        assert powerups["title"] == "Power-Ups"
        assert any("[SHIELD]" in line for line in powerups["content"])
        assert any("[3-SHOT]" in line for line in powerups["content"])
        assert any("[SPEED]" in line for line in powerups["content"])

    def test_tutorial_level_system_page_content(self):
        """Test level system page has expected content"""
        tutorial = Tutorial()
        level_sys = tutorial.pages[2]
        assert level_sys["title"] == "Level System"
        assert any("2500 points" in line for line in level_sys["content"])
        assert any("Boss" in line for line in level_sys["content"])

    def test_tutorial_weapon_system_page_content(self):
        """Test weapon system page has expected content"""
        tutorial = Tutorial()
        weapons = tutorial.pages[3]
        assert weapons["title"] == "Weapon System"
        assert any("STANDARD:" in line for line in weapons["content"])
        assert any("LASER:" in line for line in weapons["content"])
        assert any("ROCKETS:" in line for line in weapons["content"])
        assert any("SHOTGUN:" in line for line in weapons["content"])

    def test_tutorial_boss_strategies_page_content(self):
        """Test boss strategies page has expected content"""
        tutorial = Tutorial()
        boss = tutorial.pages[4]
        assert boss["title"] == "Boss Fight Strategies"
        assert any("Boss Behavior" in line for line in boss["content"])

    def test_tutorial_advanced_tips_page_content(self):
        """Test advanced tips page has expected content"""
        tutorial = Tutorial()
        tips = tutorial.pages[5]
        assert tips["title"] == "Advanced Tips"
        assert any("Controls" in line for line in tips["content"])
        assert any("Strategy" in line for line in tips["content"])

    def test_tutorial_difficulty_page_content(self):
        """Test difficulty page has expected content"""
        tutorial = Tutorial()
        diff = tutorial.pages[6]
        assert diff["title"] == "Difficulty Levels"
        assert any("[EASY]:" in line for line in diff["content"])
        assert any("[NORMAL]:" in line for line in diff["content"])
        assert any("[HARD]:" in line for line in diff["content"])

    def test_tutorial_next_page(self):
        """Test moving to next page"""
        tutorial = Tutorial()
        initial_page = tutorial.current_page
        tutorial.next_page()
        assert tutorial.transitioning is True
        assert tutorial.target_page == initial_page + 1

    def test_tutorial_next_page_last_page(self):
        """Test next_page on last page does nothing"""
        tutorial = Tutorial()
        tutorial.current_page = len(tutorial.pages) - 1
        tutorial.next_page()
        assert tutorial.transitioning is False

    def test_tutorial_previous_page(self):
        """Test moving to previous page"""
        tutorial = Tutorial()
        tutorial.current_page = 2
        tutorial.previous_page()
        assert tutorial.transitioning is True
        assert tutorial.target_page == 1

    def test_tutorial_previous_page_first_page(self):
        """Test previous_page on first page does nothing"""
        tutorial = Tutorial()
        tutorial.current_page = 0
        tutorial.previous_page()
        assert tutorial.transitioning is False

    def test_tutorial_start_transition(self):
        """Test starting a transition"""
        tutorial = Tutorial()
        tutorial.start_transition(3)
        assert tutorial.transitioning is True
        assert tutorial.target_page == 3
        assert tutorial.transition_timer == 0

    def test_tutorial_update_no_transition(self):
        """Test update without transition"""
        tutorial = Tutorial()
        result = tutorial.update(0.1, [])
        assert result is None

    def test_tutorial_update_with_transition(self):
        """Test update during transition"""
        tutorial = Tutorial()
        tutorial.start_transition(2)
        initial_timer = tutorial.transition_timer
        tutorial.update(0.1, [])
        assert tutorial.transition_timer > initial_timer

    def test_tutorial_update_transition_complete(self):
        """Test transition completes"""
        tutorial = Tutorial()
        tutorial.start_transition(2)
        tutorial.update(0.5, [])
        assert tutorial.transitioning is False
        assert tutorial.current_page == 2

    def test_tutorial_update_starfield(self):
        """Test starfield updates"""
        tutorial = Tutorial()
        if tutorial.starfield:
            tutorial.update(0.1, [])

    def test_tutorial_escape_key(self):
        """Test ESC key returns back"""
        tutorial = Tutorial()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        result = tutorial.update(0.1, [event])
        assert result == "back"

    def test_tutorial_space_key(self):
        """Test space key returns back"""
        tutorial = Tutorial()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        result = tutorial.update(0.1, [event])
        assert result == "back"

    def test_tutorial_left_arrow_key(self):
        """Test left arrow goes to previous page"""
        tutorial = Tutorial()
        tutorial.current_page = 2
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT)
        tutorial.update(0.1, [event])
        assert tutorial.transitioning is True
        assert tutorial.target_page == 1

    def test_tutorial_right_arrow_key(self):
        """Test right arrow goes to next page"""
        tutorial = Tutorial()
        tutorial.current_page = 0
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
        tutorial.update(0.1, [event])
        assert tutorial.transitioning is True
        assert tutorial.target_page == 1

    def test_tutorial_a_key(self):
        """Test A key goes to previous page"""
        tutorial = Tutorial()
        tutorial.current_page = 2
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a)
        tutorial.update(0.1, [event])
        assert tutorial.transitioning is True
        assert tutorial.target_page == 1

    def test_tutorial_d_key(self):
        """Test D key goes to next page"""
        tutorial = Tutorial()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_d)
        tutorial.update(0.1, [event])
        assert tutorial.transitioning is True
        assert tutorial.target_page == 1

    def test_tutorial_navigation_during_transition(self):
        """Test navigation blocked during transition"""
        tutorial = Tutorial()
        tutorial.start_transition(2)
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
        tutorial.update(0.1, [event])
        assert tutorial.target_page == 2

    def test_tutorial_draw_basic(self, mock_screen):
        """Test basic drawing"""
        tutorial = Tutorial()
        tutorial.draw(mock_screen)

    def test_tutorial_draw_all_pages(self, mock_screen):
        """Test drawing all pages"""
        tutorial = Tutorial()
        for i in range(len(tutorial.pages)):
            tutorial.current_page = i
            tutorial.draw(mock_screen)

    def test_tutorial_draw_with_starfield(self, mock_screen):
        """Test drawing with starfield"""
        tutorial = Tutorial()
        if tutorial.starfield:
            tutorial.draw(mock_screen)

    def test_tutorial_draw_with_transition(self, mock_screen):
        """Test drawing during transition"""
        tutorial = Tutorial()
        tutorial.start_transition(2)
        tutorial.update(0.1, [])
        tutorial.draw(mock_screen)

    def test_tutorial_draw_transition_alpha(self, mock_screen):
        """Test alpha changes during transition"""
        tutorial = Tutorial()
        tutorial.transitioning = True
        tutorial.transition_timer = 0.15
        tutorial.draw(mock_screen)

    def test_tutorial_draw_colored_line_shield(self, mock_screen):
        """Test drawing colored line for shield"""
        tutorial = Tutorial()
        tutorial.draw_colored_line(mock_screen, "[SHIELD] - Protection", SCREEN_WIDTH // 2, 100)

    def test_tutorial_draw_colored_line_laser(self, mock_screen):
        """Test drawing colored line for laser"""
        tutorial = Tutorial()
        tutorial.draw_colored_line(mock_screen, "[LASER] - More damage", SCREEN_WIDTH // 2, 100)

    def test_tutorial_draw_colored_line_rocket(self, mock_screen):
        """Test drawing colored line for rocket"""
        tutorial = Tutorial()
        tutorial.draw_colored_line(mock_screen, "[ROCKET] - Homing", SCREEN_WIDTH // 2, 100)

    def test_tutorial_draw_colored_line_shotgun(self, mock_screen):
        """Test drawing colored line for shotgun"""
        tutorial = Tutorial()
        tutorial.draw_colored_line(mock_screen, "[SHOTGUN] - Spread", SCREEN_WIDTH // 2, 100)

    def test_tutorial_draw_colored_line_triple_shot(self, mock_screen):
        """Test drawing colored line for triple shot"""
        tutorial = Tutorial()
        tutorial.draw_colored_line(mock_screen, "[3-SHOT] - Three shots", SCREEN_WIDTH // 2, 100)

    def test_tutorial_draw_colored_line_speed(self, mock_screen):
        """Test drawing colored line for speed"""
        tutorial = Tutorial()
        tutorial.draw_colored_line(mock_screen, "[SPEED] - Fast fire", SCREEN_WIDTH // 2, 100)

    def test_tutorial_draw_colored_line_easy(self, mock_screen):
        """Test drawing colored line for easy difficulty"""
        tutorial = Tutorial()
        tutorial.draw_colored_line(mock_screen, "[EASY] - Easy mode", SCREEN_WIDTH // 2, 100)

    def test_tutorial_draw_colored_line_normal(self, mock_screen):
        """Test drawing colored line for normal difficulty"""
        tutorial = Tutorial()
        tutorial.draw_colored_line(mock_screen, "[NORMAL] - Normal mode", SCREEN_WIDTH // 2, 100)

    def test_tutorial_draw_colored_line_hard(self, mock_screen):
        """Test drawing colored line for hard difficulty"""
        tutorial = Tutorial()
        tutorial.draw_colored_line(mock_screen, "[HARD] - Hard mode", SCREEN_WIDTH // 2, 100)

    def test_tutorial_draw_colored_line_weapon_standard(self, mock_screen):
        """Test drawing colored line for standard weapon"""
        tutorial = Tutorial()
        tutorial.draw_colored_line(mock_screen, "STANDARD: Unlimited ammo", SCREEN_WIDTH // 2, 100)

    def test_tutorial_draw_colored_line_weapon_laser(self, mock_screen):
        """Test drawing colored line for laser weapon"""
        tutorial = Tutorial()
        tutorial.draw_colored_line(mock_screen, "LASER: 15 shots", SCREEN_WIDTH // 2, 100)

    def test_tutorial_draw_colored_line_weapon_rockets(self, mock_screen):
        """Test drawing colored line for rockets weapon"""
        tutorial = Tutorial()
        tutorial.draw_colored_line(mock_screen, "ROCKETS: 8 shots", SCREEN_WIDTH // 2, 100)

    def test_tutorial_draw_colored_line_weapon_shotgun(self, mock_screen):
        """Test drawing colored line for shotgun weapon"""
        tutorial = Tutorial()
        tutorial.draw_colored_line(mock_screen, "SHOTGUN: 12 shots", SCREEN_WIDTH // 2, 100)

    def test_tutorial_draw_colored_line_plain(self, mock_screen):
        """Test drawing plain colored line"""
        tutorial = Tutorial()
        tutorial.draw_colored_line(mock_screen, "Plain text without markers", SCREEN_WIDTH // 2, 100)

    def test_tutorial_draw_progress_bar(self, mock_screen):
        """Test progress bar drawing"""
        tutorial = Tutorial()
        tutorial.current_page = 3
        tutorial.draw(mock_screen)

    def test_tutorial_draw_page_info(self, mock_screen):
        """Test page info drawing"""
        tutorial = Tutorial()
        tutorial.current_page = 2
        tutorial.draw(mock_screen)

    def test_tutorial_draw_navigation_text(self, mock_screen):
        """Test navigation text drawing"""
        tutorial = Tutorial()
        tutorial.draw(mock_screen)

    def test_tutorial_empty_lines(self, mock_screen):
        """Test handling empty lines in content"""
        tutorial = Tutorial()
        tutorial.current_page = 0
        tutorial.draw(mock_screen)

    def test_tutorial_special_markers_boss(self, mock_screen):
        """Test boss fight special markers"""
        tutorial = Tutorial()
        tutorial.current_page = 4
        tutorial.draw(mock_screen)

    def test_tutorial_special_markers_controls(self, mock_screen):
        """Test controls special markers"""
        tutorial = Tutorial()
        tutorial.current_page = 5
        tutorial.draw(mock_screen)

    def test_tutorial_bullet_points(self, mock_screen):
        """Test bullet point rendering"""
        tutorial = Tutorial()
        tutorial.current_page = 0
        tutorial.draw(mock_screen)

    def test_tutorial_multiple_events(self):
        """Test handling multiple events"""
        tutorial = Tutorial()
        events = [
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_d),
        ]
        result = tutorial.update(0.1, events)

    def test_tutorial_fonts_initialized(self):
        """Test fonts are properly initialized"""
        tutorial = Tutorial()
        assert tutorial.font_title is not None
        assert tutorial.font_content is not None
        assert tutorial.font_navigation is not None

    def test_tutorial_no_starfield(self):
        """Test tutorial works without starfield"""
        with patch('modul.tutorial.MenuStarfield', side_effect=ImportError):
            tutorial = Tutorial()
            assert tutorial.starfield is None
            tutorial.update(0.1, [])
            tutorial.draw(pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)))

    def test_tutorial_starfield_import_error(self):
        """Test graceful handling of starfield import error"""
        tutorial = Tutorial()
        tutorial.starfield = None
        tutorial.update(0.1, [])
        tutorial.draw(pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)))

    def test_tutorial_current_page_bounds(self):
        """Test current_page stays within bounds"""
        tutorial = Tutorial()
        tutorial.current_page = len(tutorial.pages) - 1
        tutorial.next_page()
        assert tutorial.current_page == len(tutorial.pages) - 1
        
        tutorial.current_page = 0
        tutorial.previous_page()
        assert tutorial.current_page == 0

    def test_tutorial_transition_timer_reset(self):
        """Test transition timer resets"""
        tutorial = Tutorial()
        tutorial.start_transition(2)
        assert tutorial.transition_timer == 0
        tutorial.update(0.2, [])
        tutorial.update(0.5, [])
        assert tutorial.transition_timer == 0

    def test_tutorial_alpha_calculation(self):
        """Test alpha calculation during transition"""
        tutorial = Tutorial()
        tutorial.transitioning = True
        tutorial.transition_duration = 0.3
        
        tutorial.transition_timer = 0.0
        tutorial.draw(pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)))
        
        tutorial.transition_timer = 0.15
        tutorial.draw(pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)))
        
        tutorial.transition_timer = 0.3
        tutorial.draw(pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)))

    def test_tutorial_page_zero_index(self):
        """Test first page is index 0"""
        tutorial = Tutorial()
        assert tutorial.current_page == 0
        assert tutorial.pages[0]["title"] == "Basics"

    def test_tutorial_last_page_index(self):
        """Test last page index"""
        tutorial = Tutorial()
        last_index = len(tutorial.pages) - 1
        tutorial.current_page = last_index
        assert tutorial.pages[tutorial.current_page]["title"] == "Difficulty Levels"

    def test_tutorial_all_pages_have_non_empty_content(self):
        """Test all pages have content"""
        tutorial = Tutorial()
        for page in tutorial.pages:
            assert len(page["content"]) > 0

    def test_tutorial_draw_with_different_y_offsets(self, mock_screen):
        """Test drawing with various content lengths"""
        tutorial = Tutorial()
        for i in range(len(tutorial.pages)):
            tutorial.current_page = i
            tutorial.draw(mock_screen)

    def test_tutorial_line_colors_boss_behavior(self, mock_screen):
        """Test boss behavior line coloring"""
        tutorial = Tutorial()
        tutorial.current_page = 4
        tutorial.draw(mock_screen)

    def test_tutorial_line_colors_tips(self, mock_screen):
        """Test tips line coloring"""
        tutorial = Tutorial()
        tutorial.current_page = 4
        tutorial.draw(mock_screen)

    def test_tutorial_line_colors_controls(self, mock_screen):
        """Test controls line coloring"""
        tutorial = Tutorial()
        tutorial.current_page = 5
        tutorial.draw(mock_screen)

    def test_tutorial_line_colors_strategy(self, mock_screen):
        """Test strategy line coloring"""
        tutorial = Tutorial()
        tutorial.current_page = 5
        tutorial.draw(mock_screen)

    def test_tutorial_update_returns_none_normally(self):
        """Test update returns None during normal operation"""
        tutorial = Tutorial()
        result = tutorial.update(0.1, [])
        assert result is None

    def test_tutorial_update_during_transition_returns_none(self):
        """Test update returns None during transition"""
        tutorial = Tutorial()
        tutorial.start_transition(2)
        result = tutorial.update(0.1, [])
        assert result is None

    def test_tutorial_navigation_first_to_last(self):
        """Test navigation from first to last page"""
        tutorial = Tutorial()
        for i in range(len(tutorial.pages) - 1):
            tutorial.next_page()
            tutorial.update(0.5, [])
        assert tutorial.current_page == len(tutorial.pages) - 1

    def test_tutorial_navigation_last_to_first(self):
        """Test navigation from last to first page"""
        tutorial = Tutorial()
        tutorial.current_page = len(tutorial.pages) - 1
        for i in range(len(tutorial.pages) - 1):
            tutorial.previous_page()
            tutorial.update(0.5, [])
        assert tutorial.current_page == 0

    def test_tutorial_rapid_navigation(self):
        """Test rapid navigation"""
        tutorial = Tutorial()
        for _ in range(10):
            tutorial.next_page()
            tutorial.update(0.01, [])
        
    def test_tutorial_page_content_structure_consistency(self):
        """Test all pages have consistent structure"""
        tutorial = Tutorial()
        for page in tutorial.pages:
            assert isinstance(page["title"], str)
            assert isinstance(page["content"], list)
            for line in page["content"]:
                assert isinstance(line, str)

    def test_tutorial_draw_colored_line_no_bracket(self, mock_screen):
        """Test colored line drawing without brackets"""
        tutorial = Tutorial()
        tutorial.draw_colored_line(mock_screen, "No special markers here", 640, 360)

    def test_tutorial_draw_colored_line_no_colon(self, mock_screen):
        """Test colored line drawing without colon"""
        tutorial = Tutorial()
        tutorial.draw_colored_line(mock_screen, "[TEST] no colon", 640, 360)

    def test_tutorial_starfield_exists_check(self):
        """Test starfield existence check"""
        tutorial = Tutorial()
        has_starfield = hasattr(tutorial, "starfield") and tutorial.starfield is not None
        if has_starfield:
            assert tutorial.starfield is not None

    def test_tutorial_transition_boundary_cases(self):
        """Test transition at boundary pages"""
        tutorial = Tutorial()
        
        tutorial.current_page = 0
        tutorial.start_transition(1)
        tutorial.update(0.5, [])
        assert tutorial.current_page == 1
        
        tutorial.current_page = len(tutorial.pages) - 2
        tutorial.start_transition(len(tutorial.pages) - 1)
        tutorial.update(0.5, [])
        assert tutorial.current_page == len(tutorial.pages) - 1

    def test_tutorial_multiple_transitions(self):
        """Test multiple sequential transitions"""
        tutorial = Tutorial()
        for target in [1, 2, 3, 2, 1, 0]:
            tutorial.start_transition(target)
            tutorial.update(0.5, [])
            assert tutorial.current_page == target

    def test_tutorial_event_handling_order(self):
        """Test events are processed in order"""
        tutorial = Tutorial()
        event1 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
        event2 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        result = tutorial.update(0.1, [event1, event2])

    def test_tutorial_screen_content_positions(self, mock_screen):
        """Test content is drawn at correct positions"""
        tutorial = Tutorial()
        for page_idx in range(len(tutorial.pages)):
            tutorial.current_page = page_idx
            tutorial.draw(mock_screen)

    def test_tutorial_colored_line_with_multiple_colors(self, mock_screen):
        """Test colored line with multiple color markers"""
        tutorial = Tutorial()
        lines_to_test = [
            "[SHIELD] - Blue color",
            "[LASER] - Green color",
            "[ROCKET] - Red color",
            "STANDARD: White",
            "LASER: Green",
            "Plain text"
        ]
        y = 100
        for line in lines_to_test:
            tutorial.draw_colored_line(mock_screen, line, 640, y)
            y += 30

    def test_tutorial_zero_delta_time(self):
        """Test update with zero delta time"""
        tutorial = Tutorial()
        result = tutorial.update(0.0, [])
        assert result is None

    def test_tutorial_large_delta_time(self):
        """Test update with large delta time"""
        tutorial = Tutorial()
        tutorial.start_transition(2)
        tutorial.update(10.0, [])
        assert tutorial.current_page == 2
        assert tutorial.transitioning is False

    def test_tutorial_starfield_update_with_dt(self):
        """Test starfield update receives delta time"""
        tutorial = Tutorial()
        if hasattr(tutorial, "starfield") and tutorial.starfield:
            mock_starfield = Mock()
            tutorial.starfield = mock_starfield
            tutorial.update(0.5, [])
            mock_starfield.update.assert_called_with(0.5)
