# Game Mechanics

This document explains the core game mechanics and algorithms used in Ajitroids.

## Physics System

### Movement and Velocity

All entities use basic 2D physics:

```python
# Position update
position += velocity * delta_time

# Velocity update with acceleration
velocity += acceleration * delta_time
```

### Player Controls

The player ship uses rotation and thrust:

```python
# Rotation
if left_key:
    rotation -= ROTATION_SPEED * dt
if right_key:
    rotation += ROTATION_SPEED * dt

# Thrust
if up_key:
    direction = Vector2(0, -1).rotate(rotation)
    velocity += direction * ACCELERATION * dt
```

### Friction and Damping

To prevent infinite acceleration:

```python
# Apply friction
velocity *= (1 - FRICTION * dt)

# Clamp maximum velocity
if velocity.length() > MAX_SPEED:
    velocity = velocity.normalize() * MAX_SPEED
```

## Collision Detection

### Circle-Circle Collision

All game entities use circular hitboxes:

```python
def collides_with(self, other):
    distance = self.position.distance_to(other.position)
    return distance < self.radius + other.radius
```

### Collision Response

Different collision pairs have different effects:

**Player vs Asteroid:**

```python
if player.collides_with(asteroid):
    if not player.invulnerable:
        player.take_damage()
        asteroid.destroy()
        create_explosion(asteroid.position)
```

**Shot vs Asteroid:**

```python
if shot.collides_with(asteroid):
    shot.kill()
    asteroid.split()  # Create smaller asteroids
    add_score(asteroid.points)
```

## Asteroid Mechanics

### Asteroid Types

Ajitroids features four distinct asteroid types, each with unique properties and
behaviors:

**Normal Asteroids (White)**

- Standard asteroids with balanced properties
- Split into 2 pieces when destroyed
- Most common type (50% spawn rate)

**Ice Asteroids (Light Blue)**

- Slippery and fast-moving
- Split into 2 pieces with 1.4x velocity multiplier
- Harder to predict trajectory after splitting
- Spawn rate: 20%

**Metal Asteroids (Gray)**

- Reinforced and tough
- Require 2 hits to destroy
- First hit damages but doesn't split the asteroid
- Split into 2 pieces on final hit
- Spawn rate: 15%

**Crystal Asteroids (Purple)**

- Brittle and shatter dramatically
- Split into 3 pieces instead of 2
- Creates more chaotic asteroid fields
- Spawn rate: 15%

All asteroid types maintain their properties when split - ice asteroids spawn
ice fragments, metal asteroids spawn tougher metal fragments, and crystal
asteroids spawn crystal fragments.

### Spawning

Asteroids spawn in waves:

```python
def spawn_asteroid():
    # Spawn at random edge position
    edge = random.choice(['top', 'bottom', 'left', 'right'])
    position = get_edge_position(edge)

    # Random velocity toward center
    direction = (screen_center - position).normalize()
    velocity = direction * random.uniform(MIN_SPEED, MAX_SPEED)

    # Random size
    size = random.choice([LARGE, MEDIUM, SMALL])

    return Asteroid(position, velocity, size)
```

### Splitting

When hit, asteroids split into smaller pieces with type-specific behavior:

```python
def split(self):
    # Metal asteroids require multiple hits
    if self.type == METAL and self.health > 1 and not at_min_size:
        self.health -= 1
        create_damage_particles()
        return  # Don't split yet

    if self.size == LARGE:
        # Normal/Ice/Metal: Create 2 asteroids
        # Crystal: Create 3 asteroids
        split_count = 3 if self.type == CRYSTAL else 2

        for i in range(split_count):
            angle = calculate_split_angle(i, split_count)

            # Ice asteroids have higher velocity multiplier
            velocity_mult = 1.4 if self.type == ICE else 1.2
            velocity = Vector2(SPLIT_SPEED, 0).rotate(angle) * velocity_mult

            # New asteroid inherits parent type
            Asteroid(self.position, velocity, MEDIUM, self.type)

    elif self.size == MEDIUM:
        # Same splitting logic for medium asteroids
        # ...

    # Small asteroids just disappear
    self.kill()
```

Type-specific splitting behaviors:

- **Normal**: Standard 2-way split with 1.2x velocity
- **Ice**: 2-way split with 1.4x velocity (slippery/fast)
- **Metal**: Requires 2 hits before splitting normally
- **Crystal**: 3-way split for more chaotic asteroid fields

## Boss Mechanics

### Boss AI

Bosses follow attack patterns:

```python
def update_boss(self, dt):
    # Pattern state machine
    if self.pattern == "circle":
        self.move_in_circle(dt)
    elif self.pattern == "chase":
        self.chase_player(dt)
    elif self.pattern == "shoot":
        self.shoot_at_player()

    # Change pattern after time
    self.pattern_timer -= dt
    if self.pattern_timer <= 0:
        self.pattern = random.choice(PATTERNS)
        self.pattern_timer = PATTERN_DURATION
```

### Boss Health

Bosses have multi-stage health:

```python
def take_damage(self, amount):
    self.health -= amount

    # Phase changes
    if self.health < self.max_health * 0.5:
        self.enter_rage_mode()

    if self.health <= 0:
        self.defeat()
        spawn_explosion(self.position, size='large')
        player.add_score(self.reward)
```

## Power-Up System

### Power-Up Types

Power-ups drop from shattered asteroids (`PowerUp.spawn_drop`) and are collected
on contact. The types live in `modul/constants.py`:

```python
POWERUP_TYPES = [
    "shield",          # temporary invulnerability, drawn as a pulsing shell
    "triple_shot",     # three projectiles per shot
    "rapid_fire",      # shortened shoot cooldown
    "laser_weapon",    # grants laser ammo and switches to it
    "missile_weapon",  # grants missile ammo and switches to it
    "shotgun_weapon",  # grants shotgun ammo and switches to it
    "speed_boost",     # temporary thrust multiplier
]

SHIELD_DURATION = 3.0
TRIPLE_SHOT_DURATION = 10.0
RAPID_FIRE_DURATION = 8.0
SPEED_BOOST_DURATION = 8.0
SPEED_BOOST_MULTIPLIER = 1.5
```

At most `POWERUP_MAX_COUNT` (3) drops exist at once, each rolls
`POWERUP_SPAWN_CHANCE` (0.3) and expires after `POWERUP_LIFETIME` (15 s).

### Power-Up Activation

`Player.activate_powerup` switches on a timer-backed effect or hands out ammo:

```python
def activate_powerup(self, powerup_type):
    if powerup_type == "shield":
        self.shield_active = True
        self.shield_timer = C.SHIELD_DURATION
    elif powerup_type == "speed_boost":
        self.speed_boost_active = True
        self.speed_boost_timer = C.SPEED_BOOST_DURATION
    # ... triple_shot / rapid_fire use the same pattern,
    # weapon power-ups raise ammo and switch `current_weapon`
```

Timed effects tick down in `Player.update(dt)`, so they pause with the game. A
respawn resets all of them.

## Scoring System

### Point Values

```python
SCORE_LARGE = 20      # large asteroid
SCORE_MEDIUM = 50     # medium asteroid shard, enemy ship
SCORE_SMALL = 100     # small asteroid shard
BOSS_SCORE = 500      # boss defeat (also grants a life)
```

Asteroid points are additionally scaled by `ASTEROID_TYPE_SCORE_MULTIPLIERS`
(normal 1.0, ice 0.9, metal 1.5, crystal 0.6).

### Combo Chain

Consecutive kills inside a short window raise the score multiplier. The chain
lives in `modul/combo.py` and is advanced with gameplay time (`dt`), so pausing
the game freezes it instead of breaking it, and replays stay deterministic.

| Constant                  | Value               | Meaning                                  |
| ------------------------- | ------------------- | ---------------------------------------- |
| `COMBO_WINDOW`            | 2.5 s               | Time after a kill until the chain drops  |
| `COMBO_TIERS`             | `((12, 3), (5, 2))` | `(kills, multiplier)`, resolved top-down |
| `COMBO_HUD_MIN`           | 2                   | Chain length from which the HUD shows it |
| `COMBO_CHAIN_ACHIEVEMENT` | 25                  | Kills needed for "Chain Reaction"        |

Asteroid, enemy-ship and boss kills all feed the chain, and the multiplier is
resolved after the counter is raised, so the kill that reaches a tier already
earns it. Taking a hit or quick-restarting resets the chain; the session best
survives and is reported in the end-of-session statistics.

```python
score += int(round(base_score * type_multiplier * combo.register_kill()))
```

## Game Modes

`--mode` (or the mode menu between main menu and difficulty select) picks the
progression rules. All modes share the same entities and rendering; only the
pacing differs.

| Mode          | Progression                                                                                                 |
| ------------- | ----------------------------------------------------------------------------------------------------------- |
| `classic`     | Score-driven levels, boss fight every 10 levels                                                             |
| `survival`    | Endless waves: every wave raises the kill quota, keeps more asteroids alive and shortens the spawn interval |
| `time_attack` | Kill quota per round against a clock; a cleared round adds bonus time, an expired clock ends the run        |

The rules live in `modul/game_modes.py` as `SurvivalProgression` and
`TimeAttackProgression`. They hold no pygame state, so the pacing can be
unit-tested without booting the game.

Boss fights and the score-based `AsteroidField` scaling are classic-only; the
alternative modes drive the field themselves via the progression objects.
Cleared waves/rounds award `SURVIVAL_WAVE_SCORE_BONUS * wave` and
`TIME_ATTACK_SCORE_BONUS * round` respectively.

Difficulty scales the alternative modes as well:
`SURVIVAL_DIFFICULTY_TARGET_FACTORS`/`SURVIVAL_DIFFICULTY_INTERVAL_FACTORS`
adjust wave quotas and spawn pacing, and `TIME_ATTACK_DIFFICULTY_TARGET_FACTORS`
raises the round quota on hard so the denser asteroid field does not turn the
higher difficulty into the easier one.

The score-driven rewards follow the same rule: boss fights, the level-50 ship
unlocks, `Level Master`, `High Scorer` and `Asteroid Hunter` only trigger in
classic. Survival and time attack still track `level` internally (replay frames
record it) but it drives nothing, so the HUD hides the level row there.

## Lives and Respawn

### Taking Damage

```python
def take_damage(self):
    if self.invulnerable:
        return

    self.lives -= 1

    if self.lives > 0:
        self.respawn()
    else:
        self.game_over()
```

### Respawn Mechanic

```python
def respawn(self):
    # Reset position to center
    self.position = Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    self.velocity = Vector2(0, 0)

    # Invulnerability period
    self.invulnerable = True
    self.invulnerable_timer = INVULNERABLE_DURATION

    # Clear nearby threats
    self.clear_spawn_area()
```

## Achievement System

### Achievement Conditions

Achievements check for various conditions:

```python
ACHIEVEMENTS = {
    "first_kill": {
        "condition": lambda stats: stats.kills >= 1,
        "title": "First Blood",
        "description": "Destroy your first asteroid"
    },
    "sharpshooter": {
        "condition": lambda stats: stats.accuracy >= 0.9,
        "title": "Sharpshooter",
        "description": "Maintain 90% accuracy"
    },
    "survivor": {
        "condition": lambda stats: stats.time_survived >= 300,
        "title": "Survivor",
        "description": "Survive for 5 minutes"
    }
}
```

### Achievement Checking

```python
def check_achievements(self):
    for achievement_id, achievement in ACHIEVEMENTS.items():
        if achievement_id not in self.unlocked:
            if achievement["condition"](self.stats):
                self.unlock_achievement(achievement_id)
```

## Particle System

### Particle Creation

Explosions and effects use particles:

```python
def create_explosion(position, count=20):
    for i in range(count):
        angle = random.uniform(0, 360)
        speed = random.uniform(50, 150)
        velocity = Vector2(speed, 0).rotate(angle)

        Particle(
            position=position,
            velocity=velocity,
            lifetime=random.uniform(0.5, 1.5),
            color=random.choice([RED, ORANGE, YELLOW])
        )
```

### Particle Update

```python
def update(self, dt):
    # Update position
    self.position += self.velocity * dt

    # Apply gravity/friction
    self.velocity *= 0.95

    # Fade out
    self.lifetime -= dt
    self.alpha = self.lifetime / self.max_lifetime

    # Remove when expired
    if self.lifetime <= 0:
        self.kill()
```

## Screen Wrapping

### Toroidal World

Entities wrap around screen edges:

```python
def wrap_around_screen(self):
    if self.position.x < 0:
        self.position.x = SCREEN_WIDTH
    elif self.position.x > SCREEN_WIDTH:
        self.position.x = 0

    if self.position.y < 0:
        self.position.y = SCREEN_HEIGHT
    elif self.position.y > SCREEN_HEIGHT:
        self.position.y = 0
```

## Difficulty Scaling

### Wave System

Difficulty increases with each wave:

```python
def calculate_wave_difficulty(wave_number):
    base_asteroids = 3
    asteroids_per_wave = 1

    total_asteroids = base_asteroids + (wave_number * asteroids_per_wave)
    asteroid_speed_multiplier = 1 + (wave_number * 0.1)

    return {
        "asteroid_count": min(total_asteroids, 15),
        "speed_multiplier": min(asteroid_speed_multiplier, 2.0),
        "boss_spawn": wave_number % 5 == 0
    }
```

## Ship Types

### Ship Attributes

Different ships have unique stats:

```python
SHIPS = {
    "default": {
        "speed": 100,
        "rotation_speed": 180,
        "fire_rate": 0.3,
        "health": 3
    },
    "speedster": {
        "speed": 150,
        "rotation_speed": 220,
        "fire_rate": 0.25,
        "health": 2
    },
    "tank": {
        "speed": 80,
        "rotation_speed": 140,
        "fire_rate": 0.4,
        "health": 5,
        "dual_cannons": True
    }
}
```

## Next Steps

- [Settings](settings.md): Configuration options
- [Pygame Integration](pygame-integration.md): How Pygame is used
- [Python API](../api/python.md): Code reference
