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

Ajitroids features four distinct asteroid types, each with unique properties and behaviors:

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

All asteroid types maintain their properties when split - ice asteroids spawn ice fragments, metal asteroids spawn tougher metal fragments, and crystal asteroids spawn crystal fragments.

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

Different power-ups provide various benefits:

```python
POWERUP_TYPES = {
    "rapid_fire": {
        "duration": 10,
        "effect": "reduce_shot_cooldown",
        "multiplier": 0.5
    },
    "shield": {
        "duration": 15,
        "effect": "invulnerability",
    },
    "multi_shot": {
        "duration": 12,
        "effect": "shoot_multiple",
        "count": 3
    },
    "speed_boost": {
        "duration": 8,
        "effect": "increase_speed",
        "multiplier": 1.5
    }
}
```

### Power-Up Activation

```python
def activate_powerup(self, powerup_type):
    config = POWERUP_TYPES[powerup_type]
    
    # Apply effect
    if config["effect"] == "reduce_shot_cooldown":
        self.shot_cooldown *= config["multiplier"]
    
    # Set timer
    self.powerup_timer = config["duration"]
    self.active_powerup = powerup_type
```

## Scoring System

### Point Values

Different actions award different points:

```python
POINTS = {
    "asteroid_large": 20,
    "asteroid_medium": 50,
    "asteroid_small": 100,
    "boss": 1000,
    "enemy_ship": 200,
    "powerup": 50,
}
```

### Score Multipliers

Combo system increases score:

```python
def add_score(self, base_points):
    # Check time since last kill
    if time.now() - self.last_kill_time < COMBO_WINDOW:
        self.combo_multiplier += 0.1
    else:
        self.combo_multiplier = 1.0
    
    points = base_points * self.combo_multiplier
    self.score += points
    self.last_kill_time = time.now()
```

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
