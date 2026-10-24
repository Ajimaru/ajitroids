"""Boss enemy behavior, spawning and attack logic."""

import math
import random
import pygame
import modul.constants as C
from modul.circleshape import CircleShape
from modul.particle import Particle


class Boss(CircleShape):
    """Boss enemy with health, movement, and attack patterns."""

    # Attack rotation per boss type. Each entry is cycled through by
    # `attack_pattern`, so types differ in how they pressure the player.
    ATTACK_PATTERNS = {
        "sentinel": ("circle", "spiral", "targeted"),
        "spiral": ("spiral", "spiral", "circle"),
        "hunter": ("targeted", "targeted", "circle"),
        "bulwark": ("circle", "circle", "spiral"),
    }

    # Visual signature per boss type.
    SATELLITES = {"sentinel": 3, "spiral": 6, "hunter": 4, "bulwark": 8}
    SATELLITE_SCALE = {"sentinel": 0.2, "spiral": 0.15, "hunter": 0.18, "bulwark": 0.26}
    SATELLITE_ORBIT = {"sentinel": 1.2, "spiral": 1.45, "hunter": 1.1, "bulwark": 1.3}

    def __init__(self, level, boss_type=None):
        """Initialize boss with level- and type-based stats."""
        super().__init__(C.SCREEN_WIDTH / 2, C.SCREEN_HEIGHT / 2, C.BOSS_RADIUS)
        self.boss_level = level // 10
        # Encounters rotate through the boss roster so repeated fights differ.
        if boss_type is None:
            index = max(0, self.boss_level - 1) % len(C.BOSS_TYPES)
            boss_type = C.BOSS_TYPES[index]
        self.boss_type = boss_type
        base_health = C.BOSS_BASE_HEALTH + (self.boss_level - 1) * C.BOSS_HEALTH_PER_LEVEL
        health_scale = C.BOSS_TYPE_HEALTH_SCALE.get(boss_type, 1.0)
        self.max_health = max(1, int(round(base_health * health_scale)))
        self.health = self.max_health
        self.color = C.BOSS_TYPE_COLORS.get(boss_type, C.BOSS_COLOR)
        self.move_speed = C.BOSS_MOVE_SPEED * C.BOSS_TYPE_SPEED_SCALE.get(boss_type, 1.0)
        self.pulse_timer = 0
        self.rotation = 0
        self.velocity = pygame.Vector2(0, 0)
        self.target_position = pygame.Vector2(C.SCREEN_WIDTH / 2, C.SCREEN_HEIGHT / 2)
        self.movement_timer = 0
        self.movement_phase = "center"
        # Countdown to the next random-phase waypoint. A plain timer is used
        # instead of a float-modulo check so retargeting is frame-rate safe.
        self.retarget_timer = 0.0
        self.attack_timer = 0
        self.attack_interval = max(
            C.BOSS_ATTACK_INTERVAL_MIN,
            C.BOSS_ATTACK_INTERVAL - self.boss_level * 0.05,
        )
        self.attack_pattern = 0
        self.hit_flash = 0
        self.death_timer = -1
        self.death_particles_emitted = False

    def update(self, dt, player_position=None):
        """Update boss state, movement, and attacks."""
        if self.death_timer >= 0:
            self.death_timer += dt
            if self.death_timer >= C.BOSS_DEATH_DURATION:
                self.kill()
                return
            if not self.death_particles_emitted:
                for _ in range(50):
                    Particle.create_asteroid_explosion(self.position.x, self.position.y)
                self.death_particles_emitted = True
            return
        self.rotation += 20 * dt
        self.pulse_timer += dt
        if self.hit_flash > 0:
            self.hit_flash -= dt
        self._update_movement(dt, player_position)
        # Capture attack payload when an attack is triggered so callers can
        # spawn projectiles or otherwise react to the attack data.
        attack_data = self._update_attack(dt)
        self.position += self.velocity * dt
        self._constrain_to_screen()
        return attack_data

    def _update_movement(self, dt, player_position):
        """Update boss movement based on current phase."""
        self.movement_timer += dt
        if self.movement_phase == "center" and self.movement_timer >= 3.0:
            self.movement_phase = "random"
            self.movement_timer = 0
        elif self.movement_phase == "random" and self.movement_timer >= 5.0:
            self.movement_phase = "chase" if player_position else "center"
            self.movement_timer = 0
        elif self.movement_phase == "chase" and self.movement_timer >= 4.0:
            self.movement_phase = "center"
            self.movement_timer = 0
        if self.movement_phase == "center":
            target = pygame.Vector2(C.SCREEN_WIDTH / 2, C.SCREEN_HEIGHT / 2)
            self._move_towards(target, self.move_speed)
        elif self.movement_phase == "random":
            # Pick a new waypoint once the old one is reached or the dwell time
            # expires. Retargeting every 1.5s made the boss jitter in place
            # because it never got near its target before being redirected.
            self.retarget_timer -= dt
            if self.retarget_timer <= 0 or self.position.distance_to(self.target_position) < self.radius:
                margin = 100
                self.target_position = pygame.Vector2(
                    random.randint(margin, C.SCREEN_WIDTH - margin), random.randint(margin, C.SCREEN_HEIGHT - margin)
                )
                self.retarget_timer = 4.0
            self._move_towards(self.target_position, self.move_speed)
        elif self.movement_phase == "chase" and player_position:
            self._move_towards(player_position, self.move_speed * 1.2)

    def _move_towards(self, target, speed, dt=0):
        """Move the boss toward `target` at given `speed`.

        Accepts an optional `dt` parameter used to decay velocity when already
        at the target. Tests call this method with a `dt` argument, so keep
        backward-compatible behavior while making velocity decay time-aware.
        """
        direction = target - self.position
        if direction.length() > 0:
            direction = direction.normalize()
            self.velocity = direction * speed
        else:
            # Decay velocity when at target; ensure dt reduces speed deterministically.
            factor = max(0.0, 1.0 - (dt * 0.5)) if dt else 0.9
            self.velocity *= factor

    def _constrain_to_screen(self):
        """Keep boss within screen boundaries."""
        margin = self.radius
        if self.position.x < margin:
            self.position.x = margin
            self.velocity.x = abs(self.velocity.x) * 0.5
        elif self.position.x > C.SCREEN_WIDTH - margin:
            self.position.x = C.SCREEN_WIDTH - margin
            self.velocity.x = -abs(self.velocity.x) * 0.5
        if self.position.y < margin:
            self.position.y = margin
            self.velocity.y = abs(self.velocity.y) * 0.5
        elif self.position.y > C.SCREEN_HEIGHT - margin:
            self.position.y = C.SCREEN_HEIGHT - margin
            self.velocity.y = -abs(self.velocity.y) * 0.5

    def _update_attack(self, dt):
        """Update attack timer and trigger attacks."""
        self.attack_timer += dt
        if self.attack_timer >= self.attack_interval:
            # Capture data produced by the attack() call and return it so
            # external code can act on the attack payload (e.g., spawn
            # projectiles). Advance the attack pattern and reset timer.
            attack_data = self.attack()
            self.attack_timer = 0
            self.attack_pattern = (self.attack_pattern + 1) % 3
            return attack_data
        return None

    def _scaled_count(self, base, per_level, minimum):
        """Scale a projectile count with boss level but keep it readable.

        The count is capped so high-level fights stay dodgeable; `minimum`
        guarantees the pattern never degrades below its base shape.
        """
        count = base + self.boss_level * per_level
        return max(minimum, min(count, C.BOSS_ATTACK_COUNT_MAX))

    def attack(self):
        """Generate attack pattern data for this boss type."""
        patterns = self.ATTACK_PATTERNS.get(self.boss_type, self.ATTACK_PATTERNS["sentinel"])
        pattern = patterns[self.attack_pattern % len(patterns)]

        if pattern == "circle":
            return {"type": "circle", "count": self._scaled_count(8, 1, 8)}
        if pattern == "spiral":
            return {"type": "spiral", "count": self._scaled_count(12, 1, 12)}
        return {"type": "targeted", "count": self._scaled_count(3, 1, 3)}

    def take_damage(self, damage):
        """Apply damage and handle death."""
        self.health -= damage
        self.hit_flash = 0.1
        for _ in range(3):
            Particle.create_asteroid_explosion(self.position.x, self.position.y)
        if self.health <= 0 and self.death_timer < 0:
            self.death_timer = 0
            return True
        return False

    def draw(self, screen):
        """Draw the boss with health bar."""
        color = self.color
        if self.hit_flash > 0:
            color = (255, 255, 255)
        self._draw_boss_shape(screen, color)
        self._draw_health_bar(screen)

    def _draw_boss_shape(self, screen, color):
        """Draw the boss's visual shape."""
        if self.death_timer >= 0:
            alpha = int(255 * (1 - self.death_timer / C.BOSS_DEATH_DURATION))
            pulsating_radius = self.radius * (1 + 0.5 * math.sin(self.death_timer * 10))
            temp_surface = pygame.Surface((pulsating_radius * 2, pulsating_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, (*color, alpha), (pulsating_radius, pulsating_radius), pulsating_radius)
            screen.blit(temp_surface, (self.position.x - pulsating_radius, self.position.y - pulsating_radius))
            return
        pulse = 1 + 0.1 * math.sin(self.pulse_timer * 3)
        main_radius = self.radius * pulse
        pygame.draw.circle(screen, color, self.position, main_radius)
        inner_radius = self.radius * 0.7 * pulse
        pygame.draw.circle(screen, (0, 0, 0), self.position, inner_radius)
        core_radius = self.radius * 0.4 * pulse
        pygame.draw.circle(screen, color, self.position, core_radius)
        # Satellite ring differs per type so each boss reads at a glance.
        satellite_count = max(3, self.SATELLITES.get(self.boss_type, 3) + self.boss_level // 2)
        satellite_radius = self.radius * self.SATELLITE_SCALE.get(self.boss_type, 0.2)
        for i in range(satellite_count):
            angle = math.radians(self.rotation + (i * 360 / satellite_count))
            orbit_radius = self.radius * self.SATELLITE_ORBIT.get(self.boss_type, 1.2)
            satellite_pos = (
                self.position.x + math.cos(angle) * orbit_radius,
                self.position.y + math.sin(angle) * orbit_radius,
            )
            pygame.draw.circle(screen, color, satellite_pos, satellite_radius)

    def _draw_health_bar(self, screen):
        """Draw the boss's health bar."""
        if self.death_timer >= 0:
            return
        bar_width = self.radius * 2.5
        bar_height = 8
        x = self.position.x - bar_width / 2
        y = self.position.y - self.radius - 20
        pygame.draw.rect(screen, (60, 60, 60), (x, y, bar_width, bar_height))
        health_ratio = self.health / self.max_health
        current_width = bar_width * health_ratio
        if health_ratio > 0.6:
            health_color = (0, 255, 0)
        elif health_ratio > 0.3:
            health_color = (255, 255, 0)
        else:
            health_color = (255, 0, 0)
        pygame.draw.rect(screen, health_color, (x, y, current_width, bar_height))
