"""Boss enemy behavior, spawning and attack logic."""

import math
import random
import pygame
import modul.constants as C
from modul.circleshape import CircleShape
from modul.particle import Particle


class Boss(CircleShape):
    """Boss enemy with health, movement, and attack patterns."""
    def __init__(self, level):
        """Initialize boss with level-based stats."""
        super().__init__(C.SCREEN_WIDTH / 2, C.SCREEN_HEIGHT / 2, C.BOSS_RADIUS)
        self.boss_level = level // 10
        self.max_health = C.BOSS_BASE_HEALTH + (self.boss_level - 1) * C.BOSS_HEALTH_PER_LEVEL
        self.health = self.max_health
        self.color = C.BOSS_COLOR
        self.pulse_timer = 0
        self.rotation = 0
        self.velocity = pygame.Vector2(0, 0)
        self.target_position = pygame.Vector2(C.SCREEN_WIDTH / 2, C.SCREEN_HEIGHT / 2)
        self.movement_timer = 0
        self.movement_phase = "center"
        self.attack_timer = 0
        self.attack_interval = C.BOSS_ATTACK_INTERVAL
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
        self._update_attack(dt)
        self.position += self.velocity * dt
        self._constrain_to_screen()

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
            self._move_towards(target, C.BOSS_MOVE_SPEED)
        elif self.movement_phase == "random":
            if self.movement_timer % 1.5 < dt:
                margin = 100
                self.target_position = pygame.Vector2(
                    random.randint(margin, C.SCREEN_WIDTH - margin), random.randint(margin, C.SCREEN_HEIGHT - margin)
                )
            self._move_towards(self.target_position, C.BOSS_MOVE_SPEED * 0.7)
        elif self.movement_phase == "chase" and player_position:
            self._move_towards(player_position, C.BOSS_MOVE_SPEED * 1.2)

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
            self.attack()
            self.attack_timer = 0
            self.attack_pattern = (self.attack_pattern + 1) % 3

    def attack(self):
        """Generate attack pattern data."""
        if self.attack_pattern == 0:
            return {"type": "circle", "count": 8 + self.boss_level * 2}
        elif self.attack_pattern == 1:
            return {"type": "spiral", "count": 12 + self.boss_level * 3}
        else:
            return {"type": "targeted", "count": 3 + self.boss_level}

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
        satellite_count = 3 + self.boss_level
        satellite_radius = self.radius * 0.2
        for i in range(satellite_count):
            angle = math.radians(self.rotation + (i * 360 / satellite_count))
            orbit_radius = self.radius * 1.2
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
