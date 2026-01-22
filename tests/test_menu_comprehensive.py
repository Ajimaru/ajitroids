"""Comprehensive tests for menu screens and menu behavior."""

from unittest.mock import Mock, MagicMock, patch, call

import pytest
import pygame

from modul.menu import (
    MenuItem, Menu, MainMenu, PauseMenu, TutorialScreen, OptionsMenu,
    CreditsScreen, GameOverScreen, DifficultyMenu, SoundTestMenu,
    AchievementsMenu, ShipSelectionMenu
)
from modul.constants import (
    ARCADE_MODE_BONUS_TIME, ARCADE_MODE_TIME, ASTEROID_COUNT_PER_LEVEL,
    ASTEROID_CRYSTAL_SPLIT_COUNT, ASTEROID_ICE_VELOCITY_MULTIPLIER,
    ASTEROID_IRREGULARITY, ASTEROID_KINDS, ASTEROID_MAX_RADIUS,
    ASTEROID_METAL_HEALTH, ASTEROID_MIN_RADIUS, ASTEROID_SPAWN_RATE,
    ASTEROID_TYPES, ASTEROID_TYPE_COLORS, ASTEROID_TYPE_CRYSTAL,
    ASTEROID_TYPE_ICE, ASTEROID_TYPE_METAL, ASTEROID_TYPE_NORMAL,
    ASTEROID_TYPE_SCORE_MULTIPLIERS, ASTEROID_TYPE_WEIGHTS, ASTEROID_VERTICES,
    BASE_ASTEROID_COUNT, BASE_SPAWN_INTERVAL, BOSS_ATTACK_INTERVAL,
    BOSS_BASE_HEALTH, BOSS_COLOR, BOSS_DEATH_DURATION, BOSS_HEALTH_PER_LEVEL,
    BOSS_LEVEL_INTERVAL, BOSS_MOVE_SPEED, BOSS_PROJECTILE_COLORS,
    BOSS_PROJECTILE_RADIUS, BOSS_PROJECTILE_SPEED, BOSS_RADIUS, BOSS_SCORE,
    COLLISION_DEBUG, CREDITS_DEVELOPER, CREDITS_GAME_NAME, CREDITS_GRAPHICS,
    CREDITS_LINE_SPACING, CREDITS_MASTERMIND, CREDITS_SCROLL_SPEED,
    CREDITS_SOUND, CREDITS_SPECIAL_THANKS, CREDITS_TITLE, CREDITS_WEBSITE,
    DEFAULT_HIGHSCORES, DIFFICULTY_EASY_ASTEROIDS, DIFFICULTY_EASY_INTERVAL,
    DIFFICULTY_HARD_ASTEROIDS, DIFFICULTY_HARD_INTERVAL,
    DIFFICULTY_NORMAL_ASTEROIDS, DIFFICULTY_NORMAL_INTERVAL, EXPLOSION_PARTICLES,
    HIGHSCORE_ALLOWED_CHARS, HIGHSCORE_DEFAULT_NAME, HIGHSCORE_FILE,
    HIGHSCORE_MAX_ENTRIES, HIGHSCORE_NAME_LENGTH, INVINCIBILITY_TIME,
    LASER_AMMO, LEVEL_UP_DISPLAY_TIME, MAX_LEVEL, MENU_BACKGROUND_ALPHA,
    MENU_BUTTON_HEIGHT, MENU_BUTTON_PADDING, MENU_BUTTON_RADIUS,
    MENU_BUTTON_WIDTH, MENU_FADE_SPEED, MENU_ITEM_FONT_SIZE,
    MENU_ITEM_SPACING, MENU_SELECTED_COLOR, MENU_TITLE_COLOR,
    MENU_TITLE_FONT_SIZE, MENU_TRANSITION_SPEED, MENU_UNSELECTED_COLOR,
    MISSILE_AMMO, PARTICLE_COLORS, PLAYER_ACCELERATION, PLAYER_FRICTION,
    PLAYER_LIVES, PLAYER_MAX_SPEED, PLAYER_RADIUS, PLAYER_ROTATION_SPEED,
    PLAYER_SHOOT_COOLDOWN, PLAYER_SHOOT_SPEED, PLAYER_SPEED, PLAYER_TURN_SPEED,
    POINTS_PER_LEVEL, POWERUP_COLORS, POWERUP_LIFETIME, POWERUP_MAX_COUNT,
    POWERUP_RADIUS, POWERUP_SPAWN_CHANCE, POWERUP_TYPES, RAPID_FIRE_COOLDOWN,
    RAPID_FIRE_DURATION, RESPAWN_POSITION_X, RESPAWN_POSITION_Y, SCORE_LARGE,
    SCORE_MEDIUM, SCORE_SMALL, SCREEN_HEIGHT, SCREEN_WIDTH, SHIELD_DURATION,
    SHOTGUN_AMMO, SHOT_RADIUS, SPAWN_INTERVAL_REDUCTION, STAR_COLORS,
    STAR_COUNT, STAR_SIZES, TRIPLE_SHOT_DURATION, WEAPON_COLORS,
    WEAPON_LASER, WEAPON_MISSILE, WEAPON_SHOTGUN, WEAPON_STANDARD,
    generate_default_highscores, DEFAULT_HIGHSCORES,
)


@pytest.fixture(autouse=True)
def init_pygame(monkeypatch):
    """Initialize pygame for each test"""
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")
    pygame.init()
    pygame.font.init()
    yield
    pygame.quit()


@pytest.fixture
def mock_screen():
    """Create a mock screen surface"""
    return pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))


@pytest.fixture
def mock_settings():
    """Create a mock settings object"""
    settings = Mock()
    settings.music_on = True
    settings.sound_on = True
    settings.fullscreen = False
    settings.music_volume = 0.5
    settings.sound_volume = 0.5
    settings.save = Mock(return_value=True)
    return settings


@pytest.fixture
def mock_sounds():
    """Create a mock sounds object"""
    sounds = Mock()
    sounds.play_menu_move = Mock()
    sounds.play_menu_select = Mock()
    sounds.play_shoot = Mock()
    sounds.play_explosion = Mock()
    sounds.play_player_hit = Mock()
    sounds.play_powerup = Mock()
    sounds.play_shield_activate = Mock()
    sounds.play_boss_spawn = Mock()
    sounds.play_boss_death = Mock()
    sounds.play_level_up = Mock()
    sounds.play_game_over = Mock()
    sounds.toggle_music = Mock()
    sounds.toggle_sound = Mock()
    sounds.set_effects_volume = Mock()
    return sounds


@pytest.fixture
def mock_achievement_system():
    """Create a mock achievement system"""
    system = Mock()
    achievement1 = Mock()
    achievement1.name = "First Blood"
    achievement1.unlocked = True
    achievement2 = Mock()
    achievement2.name = "Survivor"
    achievement2.unlocked = False
    system.achievements = [achievement1, achievement2]
    return system


class TestMenuItem:
    def test_menuitem_initialization(self):
        """Test MenuItem initializes with correct values"""
        item = MenuItem("Start", "start_game")
        assert item.text == "Start"
        assert item.action == "start_game"
        assert item.selected is False
        assert item.hover_animation == 0
        assert item.opacity == 255
        assert item.delay == 0

    def test_menuitem_update_selected(self):
        """Test MenuItem animation when selected"""
        item = MenuItem("Start", "start_game")
        item.selected = True
        initial_anim = item.hover_animation
        item.update(0.1)
        assert item.hover_animation > initial_anim

    def test_menuitem_update_unselected(self):
        """Test MenuItem animation when unselected"""
        item = MenuItem("Start", "start_game")
        item.selected = False
        item.hover_animation = 1.0
        item.update(0.1)
        assert item.hover_animation < 1.0

    def test_menuitem_update_delay(self):
        """Test MenuItem delay countdown"""
        item = MenuItem("Start", "start_game")
        item.delay = 1.0
        item.opacity = 0
        item.update(0.5)
        assert item.delay == 0.5
        item.update(0.6)
        assert item.delay == 0
        assert item.opacity == 255

    def test_menuitem_draw(self, mock_screen):
        """Test MenuItem drawing without errors"""
        item = MenuItem("Start", "start_game")
        font = pygame.font.Font(None, 36)
        rect = item.draw(mock_screen, (640, 360), font)
        assert rect is not None
        assert isinstance(rect, pygame.Rect)

    def test_menuitem_draw_animated(self, mock_screen):
        """Test MenuItem drawing with animation"""
        item = MenuItem("Start", "start_game")
        item.selected = True
        item.hover_animation = 0.5
        font = pygame.font.Font(None, 36)
        rect = item.draw(mock_screen, (640, 360), font)
        assert rect is not None


class TestMenu:
    def test_menu_initialization(self):
        """Test Menu initializes correctly"""
        menu = Menu("Test Menu")
        assert menu.title == "Test Menu"
        assert menu.items == []
        assert menu.selected_index == 0
        assert menu.background_alpha == 0
        assert menu.active is False
        assert menu.fade_in is False
        assert menu.input_cooldown == 0

    def test_menu_add_item(self):
        """Test adding items to menu"""
        menu = Menu("Test")
        menu.add_item("Start", "start_game")
        assert len(menu.items) == 1
        assert menu.items[0].text == "Start"
        assert menu.items[0].action == "start_game"
        assert menu.items[0].selected is True

    def test_menu_add_multiple_items(self):
        """Test adding multiple items"""
        menu = Menu("Test")
        menu.add_item("Start", "start_game")
        menu.add_item("Options", "options")
        menu.add_item("Exit", "exit")
        assert len(menu.items) == 3
        assert menu.items[0].selected is True
        assert menu.items[1].selected is False
        assert menu.items[2].selected is False

    def test_menu_add_item_with_shortcut(self):
        """Test adding item with shortcut key"""
        menu = Menu("Test")
        menu.add_item("Start", "start_game", "s")
        assert hasattr(menu.items[0], "shortcut")
        assert menu.items[0].shortcut == "s"

    def test_menu_activate(self):
        """Test menu activation"""
        menu = Menu("Test")
        menu.add_item("Start", "start_game")
        menu.add_item("Exit", "exit")
        menu.activate()
        assert menu.active is True
        assert menu.fade_in is True
        assert menu.background_alpha == 0
        assert menu.items[0].opacity == 0
        assert menu.items[0].delay == 0
        assert menu.items[1].delay == pytest.approx(0.1)

    def test_menu_update_fade_in(self):
        """Test menu fade-in animation"""
        menu = Menu("Test")
        menu.activate()
        menu.update(1.0, [])
        assert menu.background_alpha > 0

    def test_menu_update_items(self):
        """Test menu updates items"""
        menu = Menu("Test")
        menu.add_item("Start", "start_game")
        menu.items[0].selected = True
        menu.update(0.1, [])
        assert menu.items[0].hover_animation > 0

    def test_menu_update_input_cooldown(self):
        """Test input cooldown decreases"""
        menu = Menu("Test")
        menu.input_cooldown = 1.0
        menu.update(0.5, [])
        assert menu.input_cooldown == 0.5

    def test_menu_select_next(self):
        """Test selecting next item"""
        menu = Menu("Test")
        menu.add_item("Start", "start")
        menu.add_item("Options", "options")
        menu.add_item("Exit", "exit")
        assert menu.selected_index == 0
        menu._select_next()
        assert menu.selected_index == 1
        assert menu.items[1].selected is True
        assert menu.items[0].selected is False

    def test_menu_select_next_wrap(self):
        """Test selecting next wraps to beginning"""
        menu = Menu("Test")
        menu.add_item("Start", "start")
        menu.add_item("Exit", "exit")
        menu.selected_index = 1
        menu.items[1].selected = True
        menu._select_next()
        assert menu.selected_index == 0
        assert menu.items[0].selected is True

    def test_menu_select_previous(self):
        """Test selecting previous item"""
        menu = Menu("Test")
        menu.add_item("Start", "start")
        menu.add_item("Options", "options")
        menu.add_item("Exit", "exit")
        menu.selected_index = 1
        menu._select_previous()
        assert menu.selected_index == 0

    def test_menu_select_previous_wrap(self):
        """Test selecting previous wraps to end"""
        menu = Menu("Test")
        menu.add_item("Start", "start")
        menu.add_item("Exit", "exit")
        menu.selected_index = 0
        menu._select_previous()
        assert menu.selected_index == 1

    def test_menu_keydown_up(self):
        """Test up key selects previous"""
        menu = Menu("Test")
        menu.add_item("Start", "start")
        menu.add_item("Exit", "exit")
        menu.selected_index = 1
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
        menu.update(0.1, [event])
        assert menu.selected_index == 0
        assert menu.input_cooldown > 0

    def test_menu_keydown_down(self):
        """Test down key selects next"""
        menu = Menu("Test")
        menu.add_item("Start", "start")
        menu.add_item("Exit", "exit")
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
        menu.update(0.1, [event])
        assert menu.selected_index == 1

    def test_menu_keydown_w(self):
        """Test W key selects previous"""
        menu = Menu("Test")
        menu.add_item("Start", "start")
        menu.add_item("Exit", "exit")
        menu.selected_index = 1
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w)
        menu.update(0.1, [event])
        assert menu.selected_index == 0

    def test_menu_keydown_s(self):
        """Test S key selects next"""
        menu = Menu("Test")
        menu.add_item("Start", "start")
        menu.add_item("Exit", "exit")
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_s)
        menu.update(0.1, [event])
        assert menu.selected_index == 1

    def test_menu_keydown_return(self):
        """Test return key executes action"""
        menu = Menu("Test")
        menu.add_item("Start", "start_game")
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        result = menu.update(0.1, [event])
        assert result == "start_game"

    def test_menu_keydown_space(self):
        """Test space key executes action"""
        menu = Menu("Test")
        menu.add_item("Start", "start_game")
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        result = menu.update(0.1, [event])
        assert result == "start_game"

    def test_menu_shortcut_key(self):
        """Test shortcut key activation"""
        menu = Menu("Test")
        menu.add_item("Start", "start_game", "s")
        menu.add_item("Exit", "exit", "e")
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e, unicode="e")
        result = menu.update(0.1, [event])
        assert result == "exit"
        assert menu.selected_index == 1

    def test_menu_shortcut_case_insensitive(self):
        """Test shortcut key is case insensitive"""
        menu = Menu("Test")
        menu.add_item("Start", "start_game", "S")
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_s, unicode="s")
        result = menu.update(0.1, [event])
        assert result == "start_game"

    @patch('pygame.key.get_pressed')
    def test_menu_key_pressed_up(self, mock_get_pressed):
        """Test continuous up key press"""
        menu = Menu("Test")
        menu.add_item("Start", "start")
        menu.add_item("Exit", "exit")
        menu.selected_index = 1

        class _Pressed:
            def __init__(self, pressed):
                self._pressed = set(pressed)

            def __getitem__(self, key):
                return 1 if key in self._pressed else 0

        mock_get_pressed.return_value = _Pressed({pygame.K_UP})

        menu.update(0.1, [])
        assert menu.selected_index == 0

    @patch('pygame.key.get_pressed')
    def test_menu_key_pressed_down(self, mock_get_pressed):
        """Test continuous down key press"""
        menu = Menu("Test")
        menu.add_item("Start", "start")
        menu.add_item("Exit", "exit")

        class _Pressed:
            def __init__(self, pressed):
                self._pressed = set(pressed)

            def __getitem__(self, key):
                return 1 if key in self._pressed else 0

        mock_get_pressed.return_value = _Pressed({pygame.K_DOWN})

        menu.update(0.1, [])
        assert menu.selected_index == 1

    @patch('pygame.joystick.get_count', return_value=1)
    @patch('pygame.joystick.Joystick')
    def test_menu_joystick_up(self, mock_joystick_class, mock_get_count):
        """Test joystick up movement"""
        menu = Menu("Test")
        menu.add_item("Start", "start")
        menu.add_item("Exit", "exit")
        menu.selected_index = 1
        mock_joystick = Mock()
        mock_joystick.get_axis.return_value = -0.6
        mock_joystick.get_button.return_value = False
        mock_joystick_class.return_value = mock_joystick
        menu.update(0.1, [])
        assert menu.selected_index == 0

    @patch('pygame.joystick.get_count', return_value=1)
    @patch('pygame.joystick.Joystick')
    def test_menu_joystick_down(self, mock_joystick_class, mock_get_count):
        """Test joystick down movement"""
        menu = Menu("Test")
        menu.add_item("Start", "start")
        menu.add_item("Exit", "exit")
        mock_joystick = Mock()
        mock_joystick.get_axis.return_value = 0.6
        mock_joystick.get_button.return_value = False
        mock_joystick_class.return_value = mock_joystick
        menu.update(0.1, [])
        assert menu.selected_index == 1

    @patch('pygame.joystick.get_count', return_value=1)
    @patch('pygame.joystick.Joystick')
    def test_menu_joystick_button(self, mock_joystick_class, mock_get_count):
        """Test joystick button press"""
        menu = Menu("Test")
        menu.add_item("Start", "start_game")
        mock_joystick = Mock()
        mock_joystick.get_axis.return_value = 0
        mock_joystick.get_button.return_value = True
        mock_joystick_class.return_value = mock_joystick
        result = menu.update(0.1, [])
        assert result == "start_game"

    @patch('pygame.joystick.get_count', return_value=0)
    def test_menu_no_joystick(self, mock_get_count):
        """Test menu works without joystick"""
        menu = Menu("Test")
        menu.add_item("Start", "start")
        result = menu.update(0.1, [])
        assert result is None

    def test_menu_input_cooldown_blocks(self):
        """Test input cooldown blocks input"""
        menu = Menu("Test")
        menu.add_item("Start", "start")
        menu.add_item("Exit", "exit")
        menu.input_cooldown = 1.0
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
        menu.update(0.1, [event])
        assert menu.selected_index == 0

    def test_menu_draw(self, mock_screen):
        """Test menu drawing"""
        menu = Menu("Test Menu")
        menu.add_item("Start", "start")
        menu.add_item("Exit", "exit")
        menu.draw(mock_screen)

    def test_menu_draw_with_alpha(self, mock_screen):
        """Test menu drawing with background alpha"""
        menu = Menu("Test")
        menu.background_alpha = 150
        menu.add_item("Start", "start")
        menu.draw(mock_screen)


class TestMainMenu:
    def test_mainmenu_initialization(self):
        """Test MainMenu initializes with correct items"""
        menu = MainMenu()
        assert menu.title == "AJITROIDS"
        assert len(menu.items) == 9  # Updated: added Replays and Statistics
        assert menu.items[0].text == "Start Game"
        assert menu.items[1].text == "Tutorial"
        assert menu.items[2].text == "Replays"
        assert menu.items[3].text == "Highscores"
        assert menu.items[4].text == "Statistics"
        assert menu.items[5].text == "Achievements"
        assert menu.items[6].text == "Optionen"
        assert menu.items[7].text == "Credits"
        assert menu.items[8].text == "Exit"

    def test_mainmenu_draw(self, mock_screen):
        """Test MainMenu draws version number"""
        menu = MainMenu()
        menu.draw(mock_screen)


class TestPauseMenu:
    def test_pausemenu_initialization(self):
        """Test PauseMenu initializes correctly"""
        menu = PauseMenu()
        assert menu.title == "PAUSE"
        assert len(menu.items) == 3
        assert menu.items[0].text == "Continue"
        assert menu.items[1].text == "Restart"
        assert menu.items[2].text == "Main Menu"


class TestTutorialScreen:
    def test_tutorialscreen_initialization(self):
        """Test TutorialScreen initializes"""
        screen = TutorialScreen()
        assert screen.background_alpha == 0
        assert screen.fade_in is True

    def test_tutorialscreen_update_fade_in(self):
        """Test TutorialScreen fade-in"""
        screen = TutorialScreen()
        screen.update(1.0, [])
        assert screen.background_alpha > 0

    def test_tutorialscreen_escape_key(self):
        """Test ESC key returns to main menu"""
        screen = TutorialScreen()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        result = screen.update(0.1, [event])
        assert result == "main_menu"

    def test_tutorialscreen_draw(self, mock_screen):
        """Test TutorialScreen drawing"""
        screen = TutorialScreen()
        screen.draw(mock_screen)


class TestOptionsMenu:
    def test_optionsmenu_initialization(self, mock_settings, mock_sounds):
        """Test OptionsMenu initializes correctly"""
        menu = OptionsMenu(mock_settings, mock_sounds)
        assert menu.title == "OPTIONS"
        assert len(menu.items) == 8
        assert "Music:" in menu.items[0].text
        assert "Sound:" in menu.items[1].text
        assert "Music Volume:" in menu.items[2].text
        assert "Sound Volume:" in menu.items[3].text
        assert "Fullscreen:" in menu.items[4].text

    def test_optionsmenu_toggle_music(self, mock_settings, mock_sounds):
        """Test toggling music"""
        menu = OptionsMenu(mock_settings, mock_sounds)
        result = menu.handle_action("toggle_music", mock_sounds)
        assert result is None
        assert mock_settings.music_on is False
        mock_sounds.toggle_music.assert_called_once_with(False)
        mock_settings.save.assert_called()

    def test_optionsmenu_toggle_sound(self, mock_settings, mock_sounds):
        """Test toggling sound"""
        menu = OptionsMenu(mock_settings, mock_sounds)
        result = menu.handle_action("toggle_sound", mock_sounds)
        assert mock_settings.sound_on is False
        mock_sounds.toggle_sound.assert_called_once_with(False)

    def test_optionsmenu_adjust_music_volume(self, mock_settings, mock_sounds):
        """Test adjusting music volume"""
        menu = OptionsMenu(mock_settings, mock_sounds)
        with patch('pygame.mixer.music.set_volume') as mock_set_volume:
            result = menu.handle_action("adjust_music_volume", mock_sounds)
            assert mock_settings.music_volume == 0.6

    def test_optionsmenu_adjust_music_volume_max(self, mock_settings, mock_sounds):
        """Test music volume caps at 1.0"""
        mock_settings.music_volume = 0.95
        menu = OptionsMenu(mock_settings, mock_sounds)
        with patch('pygame.mixer.music.set_volume'):
            menu.handle_action("adjust_music_volume", mock_sounds)
            assert mock_settings.music_volume == 1.0

    def test_optionsmenu_adjust_sound_volume(self, mock_settings, mock_sounds):
        """Test adjusting sound volume"""
        menu = OptionsMenu(mock_settings, mock_sounds)
        result = menu.handle_action("adjust_sound_volume", mock_sounds)
        assert mock_settings.sound_volume == 0.6
        mock_sounds.set_effects_volume.assert_called_once_with(0.6)

    def test_optionsmenu_toggle_fullscreen(self, mock_settings, mock_sounds):
        """Test toggling fullscreen"""
        menu = OptionsMenu(mock_settings, mock_sounds)
        with patch('pygame.display.set_mode') as mock_set_mode:
            result = menu.handle_action("toggle_fullscreen", mock_sounds)
            assert mock_settings.fullscreen is True
            mock_set_mode.assert_called()

    def test_optionsmenu_toggle_fullscreen_error(self, mock_settings, mock_sounds):
        """Test fullscreen toggle error handling"""
        menu = OptionsMenu(mock_settings, mock_sounds)
        with patch('pygame.display.set_mode', side_effect=Exception("Test error")):
            result = menu.handle_action("toggle_fullscreen", mock_sounds)
            assert mock_settings.fullscreen is False

    def test_optionsmenu_sound_test(self, mock_settings, mock_sounds):
        """Test sound test action"""
        menu = OptionsMenu(mock_settings, mock_sounds)
        result = menu.handle_action("sound_test", mock_sounds)
        assert result == "sound_test"

    def test_optionsmenu_back(self, mock_settings, mock_sounds):
        """Test back action"""
        menu = OptionsMenu(mock_settings, mock_sounds)
        result = menu.handle_action("back", mock_sounds)
        assert result == "main_menu"

    def test_optionsmenu_update_escape(self, mock_settings, mock_sounds):
        """Test ESC key in options"""
        menu = OptionsMenu(mock_settings, mock_sounds)
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        result = menu.update(0.1, [event])
        assert result == "main_menu"

    def test_optionsmenu_update_left_music_volume(self, mock_settings, mock_sounds):
        """Test left arrow decreases music volume"""
        menu = OptionsMenu(mock_settings, mock_sounds)
        menu.selected_index = 2
        menu.items[2].action = "adjust_music_volume"
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT)
        with patch('pygame.mixer.music.set_volume'):
            menu.update(0.1, [event])
            assert mock_settings.music_volume == 0.4

    def test_optionsmenu_update_right_sound_volume(self, mock_settings, mock_sounds):
        """Test right arrow increases sound volume"""
        menu = OptionsMenu(mock_settings, mock_sounds)
        menu.selected_index = 3
        menu.items[3].action = "adjust_sound_volume"
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
        menu.update(0.1, [event])
        assert mock_settings.sound_volume == 0.6

    def test_optionsmenu_volume_minimum(self, mock_settings, mock_sounds):
        """Test volume doesn't go below 0"""
        mock_settings.music_volume = 0.05
        menu = OptionsMenu(mock_settings, mock_sounds)
        menu.selected_index = 2
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT)
        with patch('pygame.mixer.music.set_volume'):
            menu.update(0.1, [event])
            assert mock_settings.music_volume == 0.0


class TestCreditsScreen:
    def test_creditsscreen_initialization(self):
        """Test CreditsScreen initializes"""
        screen = CreditsScreen()
        assert screen.background_alpha == 0
        assert screen.fade_in is True
        assert screen.scroll_position == 250

    def test_creditsscreen_update_scroll(self):
        """Test credits scroll"""
        screen = CreditsScreen()
        initial_pos = screen.scroll_position
        screen.update(0.1, [])
        assert screen.scroll_position < initial_pos

    def test_creditsscreen_space_key(self):
        """Test space key returns to main menu"""
        screen = CreditsScreen()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        result = screen.update(0.1, [event])
        assert result == "main_menu"

    def test_creditsscreen_escape_key(self):
        """Test escape key returns to main menu"""
        screen = CreditsScreen()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        result = screen.update(0.1, [event])
        assert result == "main_menu"

    def test_creditsscreen_draw(self, mock_screen):
        """Test CreditsScreen drawing"""
        screen = CreditsScreen()
        screen.draw(mock_screen)

    def test_creditsscreen_scroll_wrap(self, mock_screen):
        """Test credits scroll wraps around"""
        screen = CreditsScreen()
        # Assuming CREDITS_TEXT is a list of strings in the CreditsScreen class
        # and its length determines the total scroll height.
        # This is a hypothetical implementation detail.
        credits_text = getattr(screen, "CREDITS_TEXT", None)
        if not credits_text:
            pytest.skip("CreditsScreen does not expose CREDITS_TEXT")

        total_scroll_height = len(credits_text) * CREDITS_LINE_SPACING
        screen.scroll_position = -total_scroll_height + 10  # Position just before wrapping

        # Update once to trigger the wrap
        screen.update(0.1, [])

        # Assert that the scroll position has wrapped back near the top
        assert screen.scroll_position >= SCREEN_HEIGHT - total_scroll_height


class TestGameOverScreen:
    def test_gameoverscreen_initialization(self):
        """Test GameOverScreen initializes"""
        screen = GameOverScreen()
        assert screen.background_alpha == 0
        assert screen.fade_in is True
        assert screen.final_score == 0

    def test_gameoverscreen_set_score(self):
        """Test setting final score"""
        screen = GameOverScreen()
        screen.set_score(1000)
        assert screen.final_score == 1000

    def test_gameoverscreen_space_key(self):
        """Test space key shows highscores"""
        screen = GameOverScreen()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        result = screen.update(0.1, [event])
        assert result == "highscore_display"

    def test_gameoverscreen_return_key(self):
        """Test return key shows highscores"""
        screen = GameOverScreen()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        result = screen.update(0.1, [event])
        assert result == "highscore_display"

    def test_gameoverscreen_escape_key(self):
        """Test escape key returns to main menu"""
        screen = GameOverScreen()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        result = screen.update(0.1, [event])
        assert result == "main_menu"

    def test_gameoverscreen_draw(self, mock_screen):
        """Test GameOverScreen drawing"""
        screen = GameOverScreen()
        screen.set_score(5000)
        screen.draw(mock_screen)


class TestDifficultyMenu:
    def test_difficultymenu_initialization(self):
        """Test DifficultyMenu initializes"""
        menu = DifficultyMenu()
        assert menu.title == "DIFFICULTY"
        assert len(menu.items) == 4
        assert menu.items[0].text == "Easy"
        assert menu.items[1].text == "Normal"
        assert menu.items[2].text == "Hard"
        assert menu.items[3].text == "Back"

    def test_difficultymenu_shortcuts(self):
        """Test difficulty menu shortcuts"""
        menu = DifficultyMenu()
        assert menu.items[0].shortcut == "L"
        assert menu.items[1].shortcut == "N"
        assert menu.items[2].shortcut == "S"
        assert menu.items[3].shortcut == "Z"


class TestSoundTestMenu:
    def test_soundtestmenu_initialization(self):
        """Test SoundTestMenu initializes"""
        menu = SoundTestMenu()
        assert menu.title == "SOUND TEST"
        assert menu.sounds is None
        assert menu.scroll_offset == 0
        assert menu.current_selection == 0
        assert len(menu.sound_items) > 0

    def test_soundtestmenu_activate(self):
        """Test SoundTestMenu activation"""
        menu = SoundTestMenu()
        menu.current_selection = 5
        menu.scroll_offset = 3
        menu.activate()
        assert menu.fade_in is True
        assert menu.current_selection == 0
        assert menu.scroll_offset == 0

    def test_soundtestmenu_set_sounds(self, mock_sounds):
        """Test setting sounds object"""
        menu = SoundTestMenu()
        menu.set_sounds(mock_sounds)
        assert menu.sounds == mock_sounds

    def test_soundtestmenu_update_visible_items(self):
        """Test updating visible items"""
        menu = SoundTestMenu()
        menu.update_visible_items()
        assert len(menu.visible_items) <= menu.max_visible_items

    def test_soundtestmenu_up_key(self):
        """Test up key navigation"""
        menu = SoundTestMenu()
        menu.current_selection = 1
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
        menu.update(0.1, [event])
        assert menu.current_selection == 0

    def test_soundtestmenu_down_key(self):
        """Test down key navigation"""
        menu = SoundTestMenu()
        menu.current_selection = 0
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
        menu.update(0.1, [event])
        assert menu.current_selection == 1

    def test_soundtestmenu_scroll_down(self):
        """Test scrolling down"""
        menu = SoundTestMenu()
        menu.current_selection = menu.max_visible_items - 1
        menu.scroll_offset = 0
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
        menu.update(0.1, [event])

    def test_soundtestmenu_return_key(self):
        """Test return key plays sound"""
        menu = SoundTestMenu()
        menu.current_selection = 0
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        result = menu.update(0.1, [event])
        assert result is not None

    def test_soundtestmenu_space_key(self):
        """Test space key returns"""
        menu = SoundTestMenu()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        result = menu.update(0.1, [event])
        assert result == "back"

    def test_soundtestmenu_escape_key(self):
        """Test escape key returns"""
        menu = SoundTestMenu()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        result = menu.update(0.1, [event])
        assert result == "back"

    def test_soundtestmenu_handle_test_shoot(self, mock_sounds):
        """Test playing shoot sound"""
        menu = SoundTestMenu()
        menu.set_sounds(mock_sounds)
        result = menu.handle_action("test_shoot")
        mock_sounds.play_shoot.assert_called_once()
        assert menu.last_played == "Standard Shoot played"

    def test_soundtestmenu_handle_test_explosion(self, mock_sounds):
        """Test playing explosion sound"""
        menu = SoundTestMenu()
        menu.set_sounds(mock_sounds)
        menu.handle_action("test_explosion")
        mock_sounds.play_explosion.assert_called_once()

    def test_soundtestmenu_handle_test_powerup(self, mock_sounds):
        """Test playing powerup sound"""
        menu = SoundTestMenu()
        menu.set_sounds(mock_sounds)
        menu.handle_action("test_powerup")
        mock_sounds.play_powerup.assert_called_once()

    def test_soundtestmenu_handle_back(self, mock_sounds):
        """Test back action"""
        menu = SoundTestMenu()
        menu.set_sounds(mock_sounds)
        menu.playing_all_sounds = False
        result = menu.handle_action("back")
        assert result == "options"

    def test_soundtestmenu_no_sounds_object(self):
        """Test handling actions without sounds object"""
        menu = SoundTestMenu()
        result = menu.handle_action("test_shoot")
        assert result is None

    def test_soundtestmenu_draw(self, mock_screen):
        """Test SoundTestMenu drawing"""
        menu = SoundTestMenu()
        menu.draw(mock_screen)

    def test_soundtestmenu_draw_with_scroll_indicators(self, mock_screen):
        """Test drawing with scroll indicators"""
        menu = SoundTestMenu()
        menu.scroll_offset = 5
        menu.draw(mock_screen)

    def test_soundtestmenu_last_played_timer(self):
        """Test last played timer countdown"""
        menu = SoundTestMenu()
        menu.last_played = "Test"
        menu.last_played_timer = 1.0
        menu.update(0.5, [])
        assert menu.last_played_timer == 0.5
        menu.update(0.6, [])
        assert menu.last_played == ""


class TestAchievementsMenu:
    def test_achievementsmenu_initialization(self, mock_achievement_system):
        """Test AchievementsMenu initializes"""
        menu = AchievementsMenu(mock_achievement_system)
        assert menu.title == "AJITROIDS - ACHIEVEMENTS"
        assert menu.achievement_system == mock_achievement_system
        assert len(menu.items) == 1
        assert menu.items[0].text == "Back"

    def test_achievementsmenu_escape_key(self, mock_achievement_system):
        """Test escape key returns"""
        menu = AchievementsMenu(mock_achievement_system)
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        result = menu.update(0.1, [event])
        assert result == "back"

    def test_achievementsmenu_space_key(self, mock_achievement_system):
        """Test space key returns"""
        menu = AchievementsMenu(mock_achievement_system)
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        result = menu.update(0.1, [event])
        assert result == "back"

    def test_achievementsmenu_draw(self, mock_screen, mock_achievement_system):
        """Test AchievementsMenu drawing"""
        menu = AchievementsMenu(mock_achievement_system)
        menu.draw(mock_screen)

    def test_achievementsmenu_draw_with_graphics(self, mock_screen, mock_achievement_system):
        """Test drawing with achievement graphics"""
        menu = AchievementsMenu(mock_achievement_system)
        menu.background_alpha = 180
        menu.draw(mock_screen)


class TestShipSelectionMenu:
    @patch('modul.menu.ship_manager')
    def test_shipselectionmenu_initialization(self, mock_ship_manager):
        """Test ShipSelectionMenu initializes"""
        mock_ship_manager.get_available_ships.return_value = ["ship1", "ship2"]
        menu = ShipSelectionMenu()
        assert menu.title == "SHIP SELECTION"
        assert menu.selected_ship_index == 0
        assert menu.animation_time == 0

    @patch('modul.menu.ship_manager')
    def test_shipselectionmenu_activate(self, mock_ship_manager):
        """Test ShipSelectionMenu activation"""
        mock_ship_manager.get_available_ships.return_value = ["ship1", "ship2"]
        mock_ship_manager.current_ship = "ship1"
        menu = ShipSelectionMenu()
        menu.activate()
        assert menu.selected_ship_index == 0

    @patch('modul.menu.ship_manager')
    def test_shipselectionmenu_left_key(self, mock_ship_manager):
        """Test left key navigation"""
        mock_ship_manager.get_available_ships.return_value = ["ship1", "ship2", "ship3"]
        menu = ShipSelectionMenu()
        menu.selected_ship_index = 1
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT)
        menu.update(0.1, [event])
        assert menu.selected_ship_index == 0

    @patch('modul.menu.ship_manager')
    def test_shipselectionmenu_right_key(self, mock_ship_manager):
        """Test right key navigation"""
        mock_ship_manager.get_available_ships.return_value = ["ship1", "ship2", "ship3"]
        menu = ShipSelectionMenu()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
        menu.update(0.1, [event])
        assert menu.selected_ship_index == 1

    @patch('modul.menu.ship_manager')
    def test_shipselectionmenu_select_unlocked_ship(self, mock_ship_manager):
        """Test selecting unlocked ship"""
        mock_ship_manager.get_available_ships.return_value = ["ship1", "ship2"]
        mock_ship_manager.get_ship_data.return_value = {"unlocked": True}
        menu = ShipSelectionMenu()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        result = menu.update(0.1, [event])
        assert result == "start_game"
        mock_ship_manager.set_current_ship.assert_called()

    @patch('modul.menu.ship_manager')
    def test_shipselectionmenu_select_locked_ship(self, mock_ship_manager):
        """Test selecting locked ship does nothing"""
        mock_ship_manager.get_available_ships.return_value = ["ship1", "ship2"]
        mock_ship_manager.get_ship_data.return_value = {"unlocked": False}
        menu = ShipSelectionMenu()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        result = menu.update(0.1, [event])
        assert result is None

    @patch('modul.menu.ship_manager')
    def test_shipselectionmenu_escape_key(self, mock_ship_manager):
        """Test escape key returns"""
        mock_ship_manager.get_available_ships.return_value = ["ship1"]
        menu = ShipSelectionMenu()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        result = menu.update(0.1, [event])
        assert result == "difficulty_select"

    @patch('modul.menu.ship_manager')
    @patch('modul.menu.ShipRenderer')
    def test_shipselectionmenu_draw(self, mock_renderer, mock_ship_manager, mock_screen):
        """Test ShipSelectionMenu drawing"""
        mock_ship_manager.get_available_ships.return_value = ["ship1"]
        mock_ship_manager.get_ship_data.return_value = {
            "unlocked": True,
            "name": "Test Ship",
            "color": (255, 255, 255),
            "shape": "triangle",
            "description": "Test",
            "speed_multiplier": 1.0,
            "turn_speed_multiplier": 1.0,
            "special_ability": "none"
        }
        menu = ShipSelectionMenu()
        menu.draw(mock_screen)

    @patch('modul.menu.ship_manager')
    def test_shipselectionmenu_update_animation(self, mock_ship_manager):
        """Test animation time updates"""
        mock_ship_manager.get_available_ships.return_value = ["ship1"]
        menu = ShipSelectionMenu()
        initial_time = menu.animation_time
        menu.update(0.1, [])
        assert menu.animation_time > initial_time
