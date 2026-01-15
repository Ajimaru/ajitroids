import pytest
import pygame
from modul.starfield import Star, Starfield, MenuStarfield
from modul.constants import STAR_COUNT


@pytest.fixture(autouse=True)
def init_pygame(monkeypatch):
    """Initialize pygame for each test (headless-safe)"""
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")
    pygame.init()
    yield
    pygame.quit()


class TestStar:
    def test_star_initialization(self):
        """Test Star initialization"""
        star = Star()
        assert isinstance(star.position, pygame.Vector2)
        assert star.size > 0
        assert star.color is not None
        assert star.twinkle_timer >= 0

    def test_star_update(self):
        """Test Star update"""
        star = Star()
        initial_timer = star.twinkle_timer
        star.update(0.1)
        assert star.twinkle_timer > initial_timer
        assert hasattr(star, 'current_color')

    def test_star_draw(self):
        """Test Star drawing"""
        star = Star()
        star.update(0.1)  # Need to update first to set current_color
        screen = pygame.Surface((800, 600))
        star.draw(screen)  # Should not raise exception

    def test_star_brightness_variation(self):
        """Test that star brightness varies"""
        star = Star()
        brightnesses = []
        for _ in range(10):
            star.update(0.1)
            if hasattr(star, 'current_color'):
                brightnesses.append(sum(star.current_color))
        
        # Should have some variation
        assert len(set(brightnesses)) > 1


class TestStarfield:
    def test_starfield_initialization(self):
        """Test Starfield initialization"""
        starfield = Starfield()
        assert len(starfield.stars) == STAR_COUNT

    def test_starfield_all_stars_initialized(self):
        """Test all stars are Star instances"""
        starfield = Starfield()
        for star in starfield.stars:
            assert isinstance(star, Star)

    def test_starfield_update(self):
        """Test Starfield update"""
        starfield = Starfield()
        starfield.update(0.1)  # Should not raise exception

    def test_starfield_draw(self):
        """Test Starfield drawing"""
        starfield = Starfield()
        starfield.update(0.1)
        screen = pygame.Surface((800, 600))
        starfield.draw(screen)  # Should not raise exception

    def test_starfield_stars_update(self):
        """Test that all stars are updated"""
        starfield = Starfield()
        initial_timers = [star.twinkle_timer for star in starfield.stars]
        starfield.update(0.1)
        updated_timers = [star.twinkle_timer for star in starfield.stars]
        
        # All timers should have changed
        assert initial_timers != updated_timers


class TestMenuStarfield:
    def test_menustarfield_initialization_default(self):
        """Test MenuStarfield initialization with default stars"""
        starfield = MenuStarfield()
        assert len(starfield.stars) == 150
        assert starfield.speed == 0.4

    def test_menustarfield_initialization_custom(self):
        """Test MenuStarfield initialization with custom star count"""
        starfield = MenuStarfield(num_stars=50)
        assert len(starfield.stars) == 50

    def test_menustarfield_star_structure(self):
        """Test star structure in MenuStarfield"""
        starfield = MenuStarfield(num_stars=10)
        for star in starfield.stars:
            assert len(star) == 4  # [x, y, z, brightness]
            assert isinstance(star[0], (int, float))  # x
            assert isinstance(star[1], (int, float))  # y
            assert isinstance(star[2], int)  # z
            assert isinstance(star[3], (int, float))  # brightness

    def test_menustarfield_update(self):
        """Test MenuStarfield update"""
        starfield = MenuStarfield(num_stars=10)
        initial_positions = [[s[0], s[1]] for s in starfield.stars]
        starfield.update(0.1)
        updated_positions = [[s[0], s[1]] for s in starfield.stars]
        
        # At least some stars should have moved
        assert initial_positions != updated_positions

    def test_menustarfield_draw(self):
        """Test MenuStarfield drawing"""
        starfield = MenuStarfield(num_stars=20)
        screen = pygame.Surface((800, 600))
        starfield.draw(screen)  # Should not raise exception

    def test_menustarfield_respawn_delay(self):
        """Test respawn delay mechanism"""
        starfield = MenuStarfield(num_stars=10)
        # Initial delay is 0, after update it might reset to max
        starfield.update(0.1)
        # Just verify the mechanism works without crashes
        assert starfield.respawn_delay_max == 0.2

    def test_menustarfield_star_respawn(self):
        """Test star respawning when out of bounds"""
        starfield = MenuStarfield(num_stars=5)
        
        # Move a star out of bounds
        starfield.stars[0][0] = -100
        starfield.stars[0][1] = -100
        
        # Update multiple times to trigger respawn
        for _ in range(20):
            starfield.update(0.1)
        
        # Star should be back near center (not out of bounds)
        # We just check it didn't crash
        assert len(starfield.stars) == 5

    def test_menustarfield_speed_factor(self):
        """Test speed affects star movement"""
        starfield1 = MenuStarfield(num_stars=5)
        starfield1.speed = 0.1
        
        starfield2 = MenuStarfield(num_stars=5)
        starfield2.speed = 1.0
        
        # Set same initial positions
        for i in range(5):
            starfield1.stars[i][:] = starfield2.stars[i][:]
        
        initial_pos1 = starfield1.stars[0][0]
        initial_pos2 = starfield2.stars[0][0]
        
        starfield1.update(0.1)
        starfield2.update(0.1)
        
        # Faster speed should move star more (or equal if already centered)
        delta1 = abs(starfield1.stars[0][0] - initial_pos1)
        delta2 = abs(starfield2.stars[0][0] - initial_pos2)
        assert delta2 >= delta1

    def test_menustarfield_draw_with_faulty_stars(self):
        """Test drawing handles faulty star data gracefully"""
        starfield = MenuStarfield(num_stars=5)
        
        # Add some faulty data
        starfield.stars.append([None, None, 1, 100])
        starfield.stars.append([100, 100])  # Missing fields
        
        screen = pygame.Surface((800, 600))
        # Should not crash
        starfield.draw(screen)

    def test_menustarfield_z_depth_variation(self):
        """Test that stars have varying z depths"""
        starfield = MenuStarfield(num_stars=20)
        z_values = [star[2] for star in starfield.stars]
        
        # Should have variation in z values
        assert len(set(z_values)) > 1
        # All z values should be in valid range
        for z in z_values:
            assert 1 <= z <= 8

    def test_menustarfield_brightness_variation(self):
        """Test that stars have varying brightness"""
        starfield = MenuStarfield(num_stars=20)
        brightness_values = [star[3] for star in starfield.stars]
        
        # Should have variation
        assert len(set(brightness_values)) > 1
        # All brightness values should be in valid range
        for b in brightness_values:
            assert 100 <= b <= 255
