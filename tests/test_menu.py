import pytest


@pytest.fixture(autouse=True)
def init_pygame(monkeypatch):
    """Initialize pygame for each test (headless-safe)"""
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")
    """Tests for the simple Menu class behavior."""

    import pygame
    import pytest

    from modul.menu import Menu


    @pytest.fixture(autouse=True)
    def init_pygame(monkeypatch):
        """Initialize pygame for each test (headless-safe)"""
        monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
        monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")
        pygame.init()
        pygame.font.init()
        yield
        pygame.quit()


    def test_menu_initial_state():
        menu = Menu(title="Test")
        assert menu.selected_index == 0
        assert isinstance(menu.items, list)


    def test_menu_select_index():
        menu = Menu(title="Test")
        menu.selected_index = 2
        assert menu.selected_index == 2


    def test_menu_add_and_select_item():
        menu = Menu(title="Test")
        menu.items.append("Start")
        menu.items.append("Optionen")
        menu.items.append("Beenden")
        menu.selected_index = 1
        assert menu.items[menu.selected_index] == "Optionen"
