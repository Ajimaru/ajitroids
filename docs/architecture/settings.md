# Settings

This document describes the configuration system and available settings in
Ajitroids.

## Settings System

Ajitroids uses a JSON-based settings system that persists user preferences
between game sessions.

## Settings File Location

Settings are stored in the user's home directory:

- **Linux/macOS**: `~/.ajitroids/settings.json`
- **Windows**: `%USERPROFILE%\.ajitroids\settings.json`

## Configuration Structure

### Default Settings

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

## Settings Categories

### Video Settings

#### Fullscreen Mode

```python
# Toggle fullscreen
settings.video.fullscreen = True
pygame.display.set_mode((width, height), pygame.FULLSCREEN)
```

**Options:**

- `false`: Windowed mode (default)
- `true`: Fullscreen mode

#### Resolution

```python
# Set resolution
settings.video.resolution = [1920, 1080]
```

**Common options:**

- `[1280, 720]`: 720p (default)
- `[1920, 1080]`: 1080p
- `[2560, 1440]`: 1440p
- `[3840, 2160]`: 4K

#### VSync

```python
# Enable VSync
settings.video.vsync = True
```

**Options:**

- `true`: Enable VSync (default)
- `false`: Disable VSync

#### FPS Display

```python
# Show FPS counter
settings.video.fps_display = True
```

**Options:**

- `false`: Hidden (default)
- `true`: Show FPS in corner

### Audio Settings

#### Master Volume

```python
# Set master volume
settings.audio.master_volume = 0.7  # 0.0 to 1.0
```

**Range:** 0.0 (muted) to 1.0 (max) **Default:** 0.7

#### Music Volume

```python
# Set music volume
settings.audio.music_volume = 0.5
pygame.mixer.music.set_volume(settings.audio.music_volume)
```

**Range:** 0.0 (muted) to 1.0 (max) **Default:** 0.5

#### Sound Effects Volume

```python
# Set SFX volume
settings.audio.sfx_volume = 0.8
```

**Range:** 0.0 (muted) to 1.0 (max) **Default:** 0.8

#### Enable/Disable Audio

```python
# Toggle music
settings.audio.music_enabled = False

# Toggle sound effects
settings.audio.sfx_enabled = False
```

### Gameplay Settings

#### Difficulty

```python
# Set difficulty level
settings.gameplay.difficulty = "hard"
```

**Options:**

- `"easy"`: More lives, slower enemies
- `"normal"`: Balanced gameplay (default)
- `"hard"`: Fewer lives, faster enemies

#### Screen Shake

```python
# Toggle screen shake on impacts
settings.gameplay.screen_shake = True
```

**Options:**

- `true`: Enable screen shake (default)
- `false`: Disable screen shake

#### Particle Effects

```python
# Toggle particle effects
settings.gameplay.particle_effects = True
```

**Options:**

- `true`: Enable particles (default)
- `false`: Disable particles (better performance)

### Control Settings

#### Key Bindings

```python
# Customize controls
settings.controls.rotate_left = "a"
settings.controls.rotate_right = "d"
settings.controls.thrust = "w"
settings.controls.shoot = "SPACE"
```

**Default bindings:**

- `rotate_left`: LEFT arrow
- `rotate_right`: RIGHT arrow
- `thrust`: UP arrow
- `shoot`: SPACE
- `switch_weapon`: B
- `pause`: ESCAPE

### Gamepad / Joystick bindings

Controls can also be bound to gamepad inputs. Bindings saved in
`settings.controls` may contain joystick identifiers using the following
readable formats:

- `JOY{n}_BUTTON{b}` — button `b` on joystick `n` (e.g. `JOY0_BUTTON1`)
- `JOY{n}_AXIS{a}_POS` / `JOY{n}_AXIS{a}_NEG` — positive/negative deflection on
  axis `a`
- `JOY{n}_HAT{h}_UP|DOWN|LEFT|RIGHT` — D-pad (hat) directions

The game detects and persists these readable strings; the input layer will
recognize them at runtime.

### Language / Localization

Ajitroids supports runtime language selection. Set the language code in
`settings.language` (e.g. `"en"` or `"de"`) and the UI will load the
corresponding JSON locale from `modul/locales/`.

The Controls menu and other UI elements are localized; when changing
`settings.language`, call `settings.save()` and restart the UI where necessary.

## Settings API

### Loading Settings

```python
from modul.settings import Settings

# Load settings from file
settings = Settings.load()

# Access settings
if settings.audio.music_enabled:
    play_music()
```

### Saving Settings

```python
# Modify settings
settings.audio.master_volume = 0.8
settings.video.fullscreen = True

# Save to file
settings.save()
```

### Resetting to Defaults

```python
# Reset all settings
settings.reset_to_defaults()
settings.save()

# Reset specific category
settings.audio = AudioSettings.defaults()
settings.save()
```

## Settings in Code

### Accessing Settings

```python
# Import settings
from modul.settings import settings

# Use in game code
def update_volume():
    volume = settings.audio.master_volume * settings.audio.music_volume
    pygame.mixer.music.set_volume(volume)
```

### Listening for Changes

```python
# Settings observer pattern
class SettingsObserver:
    def on_settings_changed(self, category, key, value):
        if category == "audio" and key == "music_volume":
            update_music_volume(value)

settings.add_observer(observer)
```

## In-Game Settings Menu

The settings menu allows players to change settings without editing files:

1. **Navigate to Settings** from main menu
2. **Select Category**: Video, Audio, Gameplay, Controls
3. **Adjust Values**: Use arrow keys or sliders
4. **Apply Changes**: Settings are saved automatically
5. **Test Settings**: Changes take effect immediately

## Performance Settings

### Low-End Hardware

For better performance on older systems:

```json
{
  "video": {
    "resolution": [1280, 720],
    "vsync": false,
    "fps_display": true
  },
  "gameplay": {
    "particle_effects": false,
    "screen_shake": false
  }
}
```

### High-End Hardware

For the best visual experience:

```json
{
  "video": {
    "resolution": [1920, 1080],
    "vsync": true,
    "fullscreen": true
  },
  "gameplay": {
    "particle_effects": true,
    "screen_shake": true
  }
}
```

## Troubleshooting

### Settings Not Saving

1. Check file permissions on settings directory
2. Ensure settings file is not read-only
3. Check disk space availability

### Settings Corrupted

If the settings file becomes corrupted:

```bash
# Delete settings file to reset
rm ~/.ajitroids/settings.json  # Linux/macOS
del %USERPROFILE%\.ajitroids\settings.json  # Windows
```

The game will recreate it with defaults on next launch.

### Audio Issues

If audio is not working:

1. Check `audio.music_enabled` and `audio.sfx_enabled`
2. Verify volumes are not set to 0.0
3. Check system audio settings

## Constants

Game constants are defined in `modul/constants.py`:

```python
# Screen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Gameplay
PLAYER_TURN_SPEED = 300
PLAYER_SPEED = 200
PLAYER_SHOOT_COOLDOWN = 0.3

# Physics
ASTEROID_MIN_RADIUS = 20
ASTEROID_KINDS = 3
ASTEROID_SPAWN_RATE = 0.8
```

These constants are not user-configurable but can be modified for
development/modding.

## Next Steps

- [Pygame Integration](pygame-integration.md): How settings integrate with
  Pygame
- [Configuration Reference](../reference/configuration.md): Complete settings
  reference
- [Contributing](../development/contributing.md): Modifying default settings
