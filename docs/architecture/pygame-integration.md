# Pygame Integration

This document explains how Ajitroids integrates with the Pygame framework and
leverages its features.

## Pygame Overview

[Pygame](https://www.pygame.org/) is a cross-platform set of Python modules
designed for writing video games. It provides functionality for:

- Graphics rendering
- Event handling
- Sound/music playback
- Collision detection
- Sprite management

Ajitroids uses **Pygame 2.6.1**.

## Core Pygame Modules Used

### pygame.display

Window and screen management:

```python
import pygame

# Initialize Pygame
pygame.init()

# Create display window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ajitroids")

# Update display
pygame.display.flip()  # Full screen update
```

**Key functions:**

- `set_mode()`: Create game window
- `flip()`: Update the full display
- `update()`: Update specific areas
- `set_caption()`: Set window title
- `set_icon()`: Set window icon

### pygame.event

Event handling system:

```python
# Main event loop
for event in pygame.event.get():
    if event.type == pygame.QUIT:
        running = False
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
            player.shoot()

# Check key state
keys = pygame.key.get_pressed()
if keys[pygame.K_LEFT]:
    player.rotate_left()
```

**Event types used:**

- `QUIT`: Window close button
- `KEYDOWN`: Key press
- `KEYUP`: Key release
- `MOUSEBUTTONDOWN`: Mouse click
- `MOUSEMOTION`: Mouse movement

### pygame.sprite

Sprite and group management:

```python
# Create sprite groups
updatable = pygame.sprite.Group()
drawable = pygame.sprite.Group()
asteroids = pygame.sprite.Group()

# Add sprites to groups
player = Player()
updatable.add(player)
drawable.add(player)

# Update all sprites
updatable.update(dt)

# Draw all sprites
drawable.draw(screen)
```

**Benefits:**

- Automatic sprite management
- Efficient collision detection
- Batch rendering
- Easy sprite removal

### pygame.mixer

Audio playback:

```python
# Initialize mixer
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# Load and play music
pygame.mixer.music.load("assets/sounds/music.mp3")
pygame.mixer.music.play(-1)  # Loop forever
pygame.mixer.music.set_volume(0.5)

# Load and play sound effects
shoot_sound = pygame.mixer.Sound("assets/sounds/shoot.wav")
shoot_sound.play()
```

**Audio features:**

- Background music (streaming)
- Sound effects (loaded in memory)
- Volume control
- Multiple channels

### pygame.time

Frame rate control and timing:

```python
# Create clock
clock = pygame.time.Clock()

# Main loop
while running:
    # Limit to 60 FPS and get delta time
    dt = clock.tick(60) / 1000.0  # Convert to seconds

    # Update game with delta time
    update_game(dt)
```

**Time functions:**

- `Clock.tick()`: Limit frame rate
- `Clock.get_fps()`: Get current FPS
- `get_ticks()`: Get milliseconds since init

### pygame.draw

Drawing primitives:

```python
# Draw shapes
pygame.draw.circle(screen, color, center, radius)
pygame.draw.line(screen, color, start_pos, end_pos, width)
pygame.draw.rect(screen, color, rect)
pygame.draw.polygon(screen, color, points)
```

**Used for:**

- Debug visualization
- UI elements
- Particle effects
- Player ship rendering

## Sprite System

### Base Sprite Class

All game entities inherit from `pygame.sprite.Sprite`:

```python
class CircleShape(pygame.sprite.Sprite):
    def __init__(self, position, radius):
        super().__init__()

        # Sprite properties
        self.image = pygame.Surface((radius * 2, radius * 2))
        self.rect = self.image.get_rect(center=position)

        # Game properties
        self.position = pygame.math.Vector2(position)
        self.velocity = pygame.math.Vector2(0, 0)
        self.radius = radius

    def update(self, dt):
        # Update position
        self.position += self.velocity * dt
        self.rect.center = self.position

    def draw(self, screen):
        screen.blit(self.image, self.rect)
```

### Sprite Groups

Groups organize and manage sprites efficiently:

```python
# Define groups in groups.py
updatable = pygame.sprite.Group()
drawable = pygame.sprite.Group()
asteroids = pygame.sprite.Group()
shots = pygame.sprite.Group()

# Add sprite to multiple groups
class Asteroid(CircleShape):
    def __init__(self, position, velocity, size):
        super().__init__(position, size)
        # Add to relevant groups
        updatable.add(self)
        drawable.add(self)
        asteroids.add(self)
```

### Collision Detection

Pygame provides efficient collision detection:

```python
# Check collision between sprite and group
hits = pygame.sprite.spritecollide(player, asteroids, False)
for asteroid in hits:
    player.take_damage()
    asteroid.destroy()

# Check collisions between two groups
collisions = pygame.sprite.groupcollide(shots, asteroids, True, True)
for shot, asteroid_list in collisions.items():
    for asteroid in asteroid_list:
        add_score(asteroid.points)
```

## Vector Mathematics

Pygame provides `pygame.math.Vector2` for 2D vector operations:

```python
# Create vectors
position = pygame.math.Vector2(100, 200)
velocity = pygame.math.Vector2(50, 0)

# Vector operations
position += velocity * dt  # Movement
distance = position.distance_to(target)  # Distance
direction = (target - position).normalize()  # Direction

# Rotation
velocity = velocity.rotate(angle)
```

**Vector methods used:**

- `distance_to()`: Calculate distance
- `normalize()`: Get unit vector
- `rotate()`: Rotate vector
- `length()`: Get magnitude

## Surface and Image Handling

### Creating Surfaces

```python
# Create blank surface
surface = pygame.Surface((width, height))
surface.fill(color)

# Create with alpha channel
surface = pygame.Surface((width, height), pygame.SRCALPHA)
```

### Loading Images

```python
# Load image file
image = pygame.image.load("assets/player.png")

# Convert for better performance
image = image.convert()  # RGB
image = image.convert_alpha()  # RGBA

# Scale image
image = pygame.transform.scale(image, (width, height))
```

### Transformations

```python
# Rotate image
rotated = pygame.transform.rotate(image, angle)

# Flip image
flipped = pygame.transform.flip(image, flip_x, flip_y)

# Scale image
scaled = pygame.transform.scale(image, (new_width, new_height))
```

## Text Rendering

### Font System

```python
# Create font
font = pygame.font.Font(None, 36)  # Default font
font = pygame.font.Font("assets/font.ttf", 36)  # Custom font

# Render text
text_surface = font.render("Score: 1000", True, (255, 255, 255))
screen.blit(text_surface, (10, 10))
```

### Text in Ajitroids

```python
# Display score
def draw_score(screen, score):
    font = pygame.font.Font(None, 48)
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (10, 10))

# Display FPS
def draw_fps(screen, clock):
    fps = int(clock.get_fps())
    font = pygame.font.Font(None, 24)
    text = font.render(f"FPS: {fps}", True, YELLOW)
    screen.blit(text, (SCREEN_WIDTH - 100, 10))
```

## Game Loop Pattern

Ajitroids follows the standard Pygame game loop:

```python
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    running = True

    while running:
        # 1. Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2. Get input state
        keys = pygame.key.get_pressed()

        # 3. Update game state
        dt = clock.tick(60) / 1000.0
        updatable.update(dt)
        check_collisions()

        # 4. Render
        screen.fill(BLACK)
        drawable.draw(screen)
        pygame.display.flip()

    pygame.quit()
```

## Performance Optimization

### Surface Conversion

Convert surfaces for better blitting performance:

```python
# Convert to display format
image = pygame.image.load("sprite.png").convert_alpha()
```

### Dirty Rect Rendering

Update only changed areas:

```python
# Update specific regions
dirty_rects = drawable.draw(screen)
pygame.display.update(dirty_rects)
```

### Sprite Groups

Use groups for efficient batch operations:

```python
# Efficient: Update all sprites at once
updatable.update(dt)

# Inefficient: Update individually
for sprite in all_sprites:
    sprite.update(dt)
```

## Sound Management

### Channel Management

Pygame mixer has multiple channels:

```python
# Reserve channels for specific sounds
pygame.mixer.set_num_channels(16)
pygame.mixer.Channel(0).play(engine_sound)
pygame.mixer.Channel(1).play(shoot_sound)
```

### Sound Volume

Control individual sound volumes:

```python
# Set sound volume
shoot_sound.set_volume(0.5)

# Set music volume
pygame.mixer.music.set_volume(0.7)
```

## Platform Considerations

### Window Icons

Set custom window icon:

```python
icon = pygame.image.load("assets/icon.png")
pygame.display.set_icon(icon)
```

### Fullscreen Mode

Toggle fullscreen:

```python
# Windowed mode
screen = pygame.display.set_mode((width, height))

# Fullscreen mode
screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)

# Toggle
pygame.display.toggle_fullscreen()
```

## Debug Tools

### Drawing Debug Info

```python
def draw_debug_info(screen, entity):
    # Draw hitbox
    pygame.draw.circle(screen, RED, entity.position, entity.radius, 1)

    # Draw velocity vector
    end_pos = entity.position + entity.velocity
    pygame.draw.line(screen, GREEN, entity.position, end_pos, 2)
```

## Next Steps

- [Python API](../api/python.md): Complete code reference
- [Data Flow](data-flow.md): How Pygame integrates with game logic
- [Game Mechanics](game-mechanics.md): Gameplay algorithms
