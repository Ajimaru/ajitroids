# Data Flow

This document describes how data flows through the Ajitroids game, from user
input to screen rendering.

## Game Loop Data Flow

```mermaid
sequenceDiagram
    participant User
    participant Main
    participant EventHandler
    participant GameState
    participant Entities
    participant Renderer

    User->>Main: Input (keyboard/mouse)
    Main->>EventHandler: Process events
    EventHandler->>GameState: Update state
    GameState->>Entities: Update all entities
    Entities->>Entities: Check collisions
    Entities->>GameState: Update scores/lives
    GameState->>Renderer: Prepare render data
    Renderer->>User: Display frame
```

## Main Game Loop

The main loop in `main.py` coordinates all game systems:

```python
while running:
    # 1. Handle Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. Get Input State
    keys = pygame.key.get_pressed()

    # 3. Update Phase
    for obj in updatable:
        obj.update(dt)

    # 4. Collision Detection
    check_collisions()

    # 5. Render Phase
    screen.fill(BLACK)
    for obj in drawable:
        obj.draw(screen)
    pygame.display.flip()

    # 6. Frame Rate Control
    dt = clock.tick(60) / 1000
```

## Player Input Flow

```mermaid
graph LR
    A[Keyboard Input] --> B{Key Pressed?}
    B -->|Arrow Left| C[Rotate Left]
    B -->|Arrow Right| D[Rotate Right]
    B -->|Arrow Up| E[Thrust Forward]
    B -->|Space| F[Fire Shot]
    B -->|B| G[Switch Weapon]
    B -->|ESC| H[Pause Menu]

    C --> I[Update Player]
    D --> I
    E --> I
    F --> J[Create Shot]
    G --> K[Change Weapon]
    H --> L[Menu State]
```

### Input Processing

1. **Event Queue**: Pygame events are polled each frame
2. **Key State**: Current keyboard state is checked
3. **Player Update**: Player responds to input
4. **Action Execution**: Actions are performed (shooting, moving, etc.)

## Entity Update Flow

Each game entity updates independently but follows a common pattern:

### Update Cycle

```mermaid
graph TD
    A[Entity.update] --> B[Update Position]
    B --> C[Apply Velocity]
    C --> D[Check Boundaries]
    D --> E[Wrap Around Screen]
    E --> F[Update Animation]
    F --> G[Check Timers]
    G --> H[Perform AI Logic]
    H --> I[Update Complete]
```

### Example: Asteroid Update

```python
def update(self, dt):
    # 1. Move based on velocity
    self.position += self.velocity * dt

    # 2. Rotate
    self.rotation += self.rotation_speed * dt

    # 3. Wrap around screen
    if self.position.x < 0:
        self.position.x = SCREEN_WIDTH

    # 4. Update sprite
    self.rect.center = self.position
```

## Collision Detection Flow

```mermaid
graph TD
    A[Check Collisions] --> B{Player vs Asteroids}
    A --> C{Player vs Enemies}
    A --> D{Player vs PowerUps}
    A --> E{Shots vs Asteroids}
    A --> F{Shots vs Enemies}

    B -->|Collision| G[Damage Player]
    C -->|Collision| G
    D -->|Collision| H[Activate PowerUp]
    E -->|Collision| I[Destroy Asteroid]
    F -->|Collision| J[Damage Enemy]

    G --> K[Check Lives]
    I --> L[Add Score]
    I --> M[Spawn Smaller Asteroids]
    J --> N[Check Enemy Health]
```

### Collision Detection Algorithm

Ajitroids uses circular collision detection:

```python
def collides_with(self, other):
    distance = self.position.distance_to(other.position)
    return distance < self.radius + other.radius
```

## Score and Achievement Flow

```mermaid
graph LR
    A[Game Event] --> B{Event Type}
    B -->|Destroy Asteroid| C[Add Score]
    B -->|Destroy Boss| D[Add Bonus Score]
    B -->|Collect PowerUp| E[Add Points]

    C --> F[Update Score Display]
    D --> F
    E --> F

    F --> G[Check Achievements]
    G --> H{Achievement Unlocked?}
    H -->|Yes| I[Show Notification]
    H -->|No| J[Continue]

    F --> K[Check High Score]
    K --> L{New High Score?}
    L -->|Yes| M[Save High Score]
```

### Achievement Triggers

The `AchievementManager` monitors various game events:

- Score milestones
- Asteroid destruction counts
- Boss defeats
- Specific action combinations
- Time-based achievements

## State Persistence Flow

```mermaid
graph TD
    A[Game Event] --> B{Save Required?}
    B -->|Yes| C[Prepare Data]
    C --> D[JSON Serialization]
    D --> E[Write to File]
    E --> F[File Saved]

    G[Game Start] --> H[Load Data]
    H --> I[Read File]
    I --> J[JSON Deserialization]
    J --> K[Restore State]
```

### Persistent Data

The following data is saved between sessions:

- **High Scores**: Top 10 scores with names
- **Achievements**: Unlocked achievements list
- **Settings**: Audio, video, and control preferences
- **Unlocked Ships**: Available ship types

Files are stored as JSON in the user's home directory.

## Sound System Flow

```mermaid
graph LR
    A[Game Event] --> B[SoundManager]
    B --> C{Sound Type}
    C -->|Effect| D[Play Sound Effect]
    C -->|Music| E[Play Music]

    D --> F[Check Volume]
    E --> G[Check Volume]

    F --> H[Pygame Mixer]
    G --> H

    H --> I[Audio Output]
```

### Sound Event Triggers

- **Player Actions**: Shooting, thrust
- **Collisions**: Asteroid hits, explosions
- **Power-ups**: Collection sounds
- **Menu**: UI interaction sounds
- **Music**: Background tracks for different game states

## Menu State Flow

```mermaid
stateDiagram-v2
    [*] --> MainMenu
    MainMenu --> Playing: Start Game
    MainMenu --> Settings: Settings
    MainMenu --> HighScores: View Scores
    MainMenu --> Tutorial: Tutorial

    Playing --> Paused: ESC
    Paused --> Playing: Resume
    Paused --> MainMenu: Quit

    Playing --> GameOver: Lives = 0
    GameOver --> MainMenu: Return
    GameOver --> Playing: Restart

    Settings --> MainMenu: Back
    HighScores --> MainMenu: Back
    Tutorial --> MainMenu: Back
```

### State Transitions

Menu states are managed by the `Menu` class, which handles:

- Rendering the appropriate UI
- Processing user input
- Transitioning between states
- Maintaining state data (scores, settings, etc.)

## Render Pipeline

```mermaid
graph TD
    A[Render Phase] --> B[Clear Screen]
    B --> C[Draw Background]
    C --> D[Draw Starfield]
    D --> E[Draw Entities]
    E --> F[Draw UI]
    F --> G[Draw Particles]
    G --> H[Draw HUD]
    H --> I[Flip Display Buffer]
    I --> J[Frame Complete]
```

### Rendering Order

1. **Background**: Fill with black
2. **Starfield**: Parallax star background
3. **Entities**: All game objects (back-to-front)
4. **Effects**: Particle systems
5. **UI**: Menu elements, HUD
6. **Overlays**: Achievements, notifications

## Performance Optimization

### Sprite Group Updates

Pygame's sprite groups batch operations:

```python
# Efficient: Update all at once
updatable.update(dt)

# Efficient: Draw all at once
drawable.draw(screen)
```

### Collision Optimization

Only check relevant collision pairs:

- Player vs asteroids/enemies/powerups
- Shots vs asteroids/enemies
- Enemies vs asteroids (optional)

### Event Batching

Process multiple similar events together to reduce overhead.

## Next Steps

- [Game Mechanics](game-mechanics.md): Understand the gameplay algorithms
- [Settings](settings.md): Configuration and customization
- [Pygame Integration](pygame-integration.md): How Pygame is used
