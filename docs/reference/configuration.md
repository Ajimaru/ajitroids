# Configuration Reference

Complete reference for all configuration options in Ajitroids.

## Configuration Files

### Settings File

**Location**: `~/.ajitroids/settings.json`

User preferences and game settings.

### High Scores File

**Location**: `~/.ajitroids/highscores.json`

Saved high scores.

### Achievements File

**Location**: `~/.ajitroids/achievements.json`

Unlocked achievements.

## Settings Schema

### Default Configuration

```json
{
  "video": {
    "fullscreen": false,
    "resolution": [1280, 720],
    "vsync": true,
    "fps_display": false
  },
  "audio": {
    "master_volume": 0.7,
    "music_volume": 0.5,
    "sfx_volume": 0.8,
    "music_enabled": true,
    "sfx_enabled": true
  },
  "gameplay": {
    "difficulty": "normal",
    "show_fps": false,
    "screen_shake": true,
    "particle_effects": true
  },
  "controls": {
    "rotate_left": "LEFT",
    "rotate_right": "RIGHT",
    "thrust": "UP",
    "shoot": "SPACE",
    "switch_weapon": "b",
    "pause": "ESCAPE"
  }
}
```

## Video Settings

### `video.fullscreen`

**Type**: `boolean` **Default**: `false` **Description**: Enable fullscreen mode

**Values**:

- `false`: Windowed mode
- `true`: Fullscreen mode

### `video.resolution`

**Type**: `[number, number]` **Default**: `[1280, 720]` **Description**:
Window/screen resolution in pixels [width, height]

**Common values**:

- `[1280, 720]`: 720p
- `[1920, 1080]`: 1080p
- `[2560, 1440]`: 1440p
- `[3840, 2160]`: 4K

### `video.vsync`

**Type**: `boolean` **Default**: `true` **Description**: Enable vertical sync to
prevent screen tearing

**Values**:

- `true`: Enable VSync (recommended)
- `false`: Disable VSync (may cause tearing)

### `video.fps_display`

**Type**: `boolean` **Default**: `false` **Description**: Show FPS counter on
screen

**Values**:

- `false`: Hide FPS counter
- `true`: Show FPS counter in top-right corner

## Audio Settings

### `audio.master_volume`

**Type**: `number` **Default**: `0.7` **Range**: `0.0` to `1.0` **Description**:
Master volume level (affects all sounds)

### `audio.music_volume`

**Type**: `number` **Default**: `0.5` **Range**: `0.0` to `1.0` **Description**:
Background music volume

### `audio.sfx_volume`

**Type**: `number` **Default**: `0.8` **Range**: `0.0` to `1.0` **Description**:
Sound effects volume

### `audio.music_enabled`

**Type**: `boolean` **Default**: `true` **Description**: Enable/disable
background music

### `audio.sfx_enabled`

**Type**: `boolean` **Default**: `true` **Description**: Enable/disable sound
effects

## Gameplay Settings

### `gameplay.difficulty`

**Type**: `string` **Default**: `"normal"` **Description**: Game difficulty
level

**Values**:

- `"easy"`: 5 lives, slower asteroids, more power-ups
- `"normal"`: 3 lives, normal speed
- `"hard"`: 1 life, faster asteroids, fewer power-ups

### `gameplay.show_fps`

**Type**: `boolean` **Default**: `false` **Description**: Display FPS counter
(same as video.fps_display)

### `gameplay.screen_shake`

**Type**: `boolean` **Default**: `true` **Description**: Enable screen shake
effect on impacts

### `gameplay.particle_effects`

**Type**: `boolean` **Default**: `true` **Description**: Enable particle effects
(explosions, trails)

**Note**: Disable for better performance on low-end systems

## Control Settings

### `controls.rotate_left`

**Type**: `string` **Default**: `"LEFT"` **Description**: Key to rotate ship
counter-clockwise

**Valid keys**: Any pygame key constant name (e.g., "LEFT", "a", "j")

### `controls.rotate_right`

**Type**: `string` **Default**: `"RIGHT"` **Description**: Key to rotate ship
clockwise

### `controls.thrust`

**Type**: `string` **Default**: `"UP"` **Description**: Key to apply forward
thrust

### `controls.shoot`

**Type**: `string` **Default**: `"SPACE"` **Description**: Key to fire weapons

### `controls.switch_weapon`

**Type**: `string` **Default**: `"b"` **Description**: Key to switch between
weapons (when power-ups active)

### `controls.pause`

**Type**: `string` **Default**: `"ESCAPE"` **Description**: Key to pause game
and open menu

## Game Constants

These are defined in `modul/constants.py` and are not user-configurable:

### Screen

```python
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
```

### Player

```python
PLAYER_RADIUS = 20
PLAYER_TURN_SPEED = 300  # degrees per second
PLAYER_SPEED = 200  # pixels per second
PLAYER_SHOOT_SPEED = 500
PLAYER_SHOOT_COOLDOWN = 0.3  # seconds
PLAYER_STARTING_LIVES = 3
PLAYER_INVULNERABILITY_TIME = 3.0  # seconds after respawn
```

### Asteroids

```python
ASTEROID_MIN_RADIUS = 20
ASTEROID_KINDS = 3  # Small, Medium, Large
ASTEROID_SPAWN_RATE = 0.8  # seconds between spawns
ASTEROID_MAX_RADIUS = 40
```

### Boss

```python
BOSS_RADIUS = 60
BOSS_HEALTH = 10
BOSS_SPEED = 50
BOSS_SHOOT_COOLDOWN = 1.5
```

### Power-ups

```python
POWERUP_RADIUS = 15
POWERUP_SPAWN_CHANCE = 0.1  # 10% chance on asteroid destruction
POWERUP_DURATION = 10.0  # seconds
```

### Scoring

```python
POINTS_ASTEROID_SMALL = 100
POINTS_ASTEROID_MEDIUM = 50
POINTS_ASTEROID_LARGE = 20
POINTS_BOSS = 1000
POINTS_POWERUP = 50
```

## Environment Variables

### `AJITROIDS_DATA_DIR`

Override the default data directory:

```bash
export AJITROIDS_DATA_DIR="/custom/path"
```

Default: `~/.ajitroids/`

### `AJITROIDS_DEBUG`

Enable debug mode:

```bash
export AJITROIDS_DEBUG=1
```

Features:

- Debug logging
- FPS display
- Collision visualizations

## High Scores Format

```json
{
  "scores": [
    {
      "name": "Player1",
      "score": 10000,
      "date": "2024-01-15T12:00:00"
    }
  ]
}
```

**Fields**:

- `name`: Player name (string, max 20 chars)
- `score`: Final score (integer)
- `date`: ISO 8601 timestamp

**Max entries**: 10 (top 10 scores)

## Achievements Format

```json
{
  "unlocked": ["first_kill", "sharpshooter", "survivor"],
  "progress": {
    "asteroids_destroyed": 150,
    "bosses_defeated": 3,
    "distance_traveled": 50000
  }
}
```

**Structure**:

- `unlocked`: Array of achievement IDs
- `progress`: Dictionary of progress counters

## File Permissions

Settings files should have:

- **Permissions**: `644` (readable by user, writable by user)
- **Owner**: Current user

If permissions are wrong:

```bash
chmod 644 ~/.ajitroids/settings.json
```

## Configuration Validation

Invalid configurations are reset to defaults with a warning.

**Validation rules**:

- Volume values must be 0.0 to 1.0
- Resolution values must be positive integers
- Difficulty must be "easy", "normal", or "hard"
- Control keys must be valid pygame key names

## Resetting Configuration

### Via Menu

1. Open game
2. Go to Settings
3. Select "Reset to Defaults"
4. Confirm

### Manual Reset

Delete configuration files:

```bash
rm -rf ~/.ajitroids/
```

Game will recreate with defaults on next launch.

## Troubleshooting

### Settings Not Persisting

1. Check file permissions
2. Verify disk space
3. Check for file system errors

### Invalid Configuration

If settings file is corrupted, delete it:

```bash
rm ~/.ajitroids/settings.json
```

### Performance Issues

Adjust these settings:

```json
{
  "video": {
    "resolution": [1280, 720],
    "vsync": false
  },
  "gameplay": {
    "particle_effects": false,
    "screen_shake": false
  }
}
```

## Next Steps

- [Settings Architecture](../architecture/settings.md): How settings work
  internally
- [Dev Scripts](cli-dev-scripts.md): Development tools
- [Contributing](../development/contributing.md): Modifying configuration system
