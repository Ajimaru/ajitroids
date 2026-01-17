# Testing

This guide covers testing practices and guidelines for Ajitroids.

## Testing Framework

Ajitroids uses **pytest** for testing. Pytest is configured in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-v"
testpaths = ["tests"]
```

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_player_respawn.py

# Run specific test function
pytest tests/test_player_respawn.py::test_player_respawn

# Stop on first failure
pytest -x

# Show local variables in tracebacks
pytest -l
```

### Coverage Reports

```bash
# Install coverage
pip install pytest-cov

# Run tests with coverage
pytest --cov=modul

# Generate HTML coverage report
pytest --cov=modul --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Test Structure

### Test Directory

```
tests/
├── __init__.py
├── test_player_respawn.py
├── test_asteroid.py
├── test_collision.py
├── test_powerups.py
└── fixtures.py
```

### Test File Naming

- Test files should start with `test_`
- Test functions should start with `test_`
- Test classes should start with `Test`

## Writing Tests

### Basic Test Example

```python
import pytest
from pygame import Vector2
from modul.player import Player

def test_player_creation():
    """Test that player is created with correct initial state."""
    player = Player(100, 100)

    assert player.position.x == 100
    assert player.position.y == 100
    assert player.lives == 3
    assert player.score == 0
```

### Testing with Fixtures

```python
import pytest
from modul.player import Player

@pytest.fixture
def player():
    """Create a player instance for testing."""
    return Player(100, 100)

def test_player_movement(player):
    """Test player movement."""
    initial_pos = player.position.copy()
    player.velocity = Vector2(10, 0)
    player.update(1.0)  # 1 second

    assert player.position.x == initial_pos.x + 10
```

### Testing Collisions

```python
def test_player_asteroid_collision():
    """Test collision between player and asteroid."""
    player = Player(100, 100)
    asteroid = Asteroid(Vector2(100, 100), Vector2(0, 0), 50)

    initial_lives = player.lives

    # Simulate collision
    if player.collides_with(asteroid):
        player.take_damage()

    assert player.lives == initial_lives - 1
```

### Testing Game Mechanics

```python
def test_asteroid_splitting():
    """Test that large asteroids split into smaller ones."""
    from modul.asteroid import Asteroid
    from modul.groups import asteroids

    # Clear group
    asteroids.empty()

    # Create large asteroid
    large_asteroid = Asteroid(Vector2(100, 100), Vector2(0, 0), size=3)
    asteroids.add(large_asteroid)

    initial_count = len(asteroids)

    # Split asteroid
    large_asteroid.split()

    # Should have more asteroids now
    assert len(asteroids) > initial_count
```

### Testing with Mock Objects

```python
from unittest.mock import Mock, patch

def test_sound_playback():
    """Test that sounds are played correctly."""
    with patch('pygame.mixer.Sound') as mock_sound:
        # Create mock sound
        sound_instance = Mock()
        mock_sound.return_value = sound_instance

        # Test sound playing
        from modul.sounds import SoundManager
        sound_mgr = SoundManager()
        sound_mgr.play_sound('shoot')

        # Verify sound was played
        sound_instance.play.assert_called_once()
```

## Testing Patterns

### Arrange-Act-Assert (AAA)

```python
def test_player_shooting():
    # Arrange
    player = Player(100, 100)
    initial_shot_count = len(shots)

    # Act
    player.shoot()

    # Assert
    assert len(shots) == initial_shot_count + 1
```

### Parameterized Tests

```python
@pytest.mark.parametrize("size,expected_score", [
    (3, 20),   # Large asteroid
    (2, 50),   # Medium asteroid
    (1, 100),  # Small asteroid
])
def test_asteroid_scoring(size, expected_score):
    """Test scoring for different asteroid sizes."""
    asteroid = Asteroid(Vector2(0, 0), Vector2(0, 0), size)
    assert asteroid.points == expected_score
```

### Testing Exceptions

```python
def test_invalid_ship_type():
    """Test that invalid ship types raise an error."""
    with pytest.raises(ValueError):
        player = Player(100, 100, ship_type="invalid")
```

## Integration Tests

### Testing Game Loop

```python
def test_game_loop_iteration():
    """Test a single game loop iteration."""
    # Initialize game
    pygame.init()
    screen = pygame.display.set_mode((800, 600))

    # Create game objects
    player = Player(400, 300)
    asteroid = Asteroid(Vector2(100, 100), Vector2(1, 0), 50)

    # Update game state
    dt = 0.016  # ~60 FPS
    player.update(dt)
    asteroid.update(dt)

    # Check that objects updated
    assert asteroid.position.x > 100  # Moved

    pygame.quit()
```

### Testing State Persistence

```python
def test_highscore_persistence(tmp_path):
    """Test that high scores are saved and loaded correctly."""
    from modul.highscore import HighscoreManager

    # Create highscore manager with temp file
    save_file = tmp_path / "highscores.json"
    hsm = HighscoreManager(str(save_file))

    # Add score
    hsm.add_score("TestPlayer", 1000)
    hsm.save()

    # Load in new instance
    hsm2 = HighscoreManager(str(save_file))
    scores = hsm2.get_scores()

    assert len(scores) == 1
    assert scores[0]["name"] == "TestPlayer"
    assert scores[0]["score"] == 1000
```

## Testing Best Practices

### DO's

✅ **Write descriptive test names**

```python
def test_player_becomes_invulnerable_after_respawn():
    # Good: Clear what is being tested
    pass
```

✅ **Test one thing per test**

```python
def test_player_loses_life_on_collision():
    # Focus on one behavior
    pass

def test_player_respawns_at_center():
    # Separate test for different behavior
    pass
```

✅ **Use fixtures for common setup**

```python
@pytest.fixture
def game_setup():
    pygame.init()
    yield
    pygame.quit()
```

✅ **Clean up after tests**

```python
def test_something():
    sprite_group.empty()  # Clean state
    # ... test code ...
    sprite_group.empty()  # Clean up
```

### DON'Ts

❌ **Don't test implementation details**

```python
# Bad: Testing internal state
def test_player_rotation_variable():
    assert player._rotation == 90

# Good: Testing behavior
def test_player_rotates_left():
    player.rotate_left(1.0)
    assert player.rotation < initial_rotation
```

❌ **Don't use hard-coded values**

```python
# Bad
assert player.position.x == 314.159

# Good
assert abs(player.position.x - expected_x) < 0.01
```

❌ **Don't test external libraries**

```python
# Bad: Testing Pygame internals or complex behavior
def test_pygame_display_creation():
    screen = pygame.display.set_mode((800, 600))
    assert screen is not None

# Good: Testing your code that uses Pygame
def test_player_movement_calculation():
    result = player.calculate_movement(dt)
    assert result.length() > 0
```

## Continuous Integration

Tests run automatically on GitHub Actions for every push and pull request. See
`.github/workflows/python-package.yml`.

## Test Coverage Goals

- **Critical paths**: 90%+ coverage
- **Game mechanics**: 80%+ coverage
- **UI code**: 60%+ coverage (harder to test)
- **Overall**: 70%+ coverage

## Debugging Tests

### Print Debugging

```python
def test_something():
    player = Player(100, 100)
    print(f"Player position: {player.position}")  # Will show in pytest output
    assert player.position.x == 100
```

### Using pdb

```python
def test_something():
    player = Player(100, 100)
    import pdb; pdb.set_trace()  # Breakpoint
    player.update(1.0)
```

Run with: `pytest -s` to see output

### Pytest Flags for Debugging

```bash
# Show print statements
pytest -s

# Drop into debugger on failure
pytest --pdb

# Show local variables on failure
pytest -l

# More verbose output
pytest -vv
```

## Performance Testing

```python
import time

def test_update_performance():
    """Test that updates complete in reasonable time."""
    player = Player(100, 100)

    start = time.time()
    for _ in range(1000):
        player.update(0.016)
    elapsed = time.time() - start

    # Should complete in under 1 second
    assert elapsed < 1.0
```

## Next Steps

- [Contributing Guide](contributing.md): Contribution workflow
- [Release Process](release-process.md): How releases are made
- [Python API](../api/python.md): Code reference for testing
