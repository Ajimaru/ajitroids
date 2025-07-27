import pygame
import math
import random
from modul.constants import *
from modul.circleshape import CircleShape
from modul.particle import Particle


class Boss(CircleShape):
    def __init__(self, level):
        super().__init__(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, BOSS_RADIUS)
        self.boss_level = level // 10
        self.max_health = BOSS_BASE_HEALTH + (self.boss_level - 1) * BOSS_HEALTH_PER_LEVEL
        self.health = self.max_health
        self.color = BOSS_COLOR
        self.pulse_timer = 0
        self.rotation = 0
        self.velocity = pygame.Vector2(0, 0)
        self.target_position = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.movement_timer = 0
        self.movement_phase = "center"
        self.attack_timer = 0
        self.attack_interval = BOSS_ATTACK_INTERVAL
        self.attack_pattern = 0
        self.hit_flash = 0
        self.death_timer = -1
        self.death_particles_emitted = False

    def update(self, dt, player_position=None):
        if self.death_timer >= 0:
            self.death_timer += dt
            if self.death_timer >= BOSS_DEATH_DURATION:
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
            target = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            self._move_towards(target, BOSS_MOVE_SPEED, dt)
        elif self.movement_phase == "random":
            if self.movement_timer % 1.5 < dt:
                margin = 100
                self.target_position = pygame.Vector2(
                    random.randint(margin, SCREEN_WIDTH - margin), random.randint(margin, SCREEN_HEIGHT - margin)
                )
            self._move_towards(self.target_position, BOSS_MOVE_SPEED * 0.7, dt)
        elif self.movement_phase == "chase" and player_position:
            self._move_towards(player_position, BOSS_MOVE_SPEED * 1.2, dt)

    def _move_towards(self, target, speed, dt):
        direction = target - self.position
        if direction.length() > 0:
            direction = direction.normalize()
            self.velocity = direction * speed
        else:
            self.velocity *= 0.9

    def _constrain_to_screen(self):
        margin = self.radius
        if self.position.x < margin:
            self.position.x = margin
            self.velocity.x = abs(self.velocity.x) * 0.5
        elif self.position.x > SCREEN_WIDTH - margin:
            self.position.x = SCREEN_WIDTH - margin
            self.velocity.x = -abs(self.velocity.x) * 0.5
        if self.position.y < margin:
            self.position.y = margin
            self.velocity.y = abs(self.velocity.y) * 0.5
        elif self.position.y > SCREEN_HEIGHT - margin:
            self.position.y = SCREEN_HEIGHT - margin
            self.velocity.y = -abs(self.velocity.y) * 0.5

    def _update_attack(self, dt):
        self.attack_timer += dt
        if self.attack_timer >= self.attack_interval:
            self.attack()
            self.attack_timer = 0
            self.attack_pattern = (self.attack_pattern + 1) % 3

    def attack(self):
        if self.attack_pattern == 0:
            return {"type": "circle", "count": 8 + self.boss_level * 2}
        elif self.attack_pattern == 1:
            return {"type": "spiral", "count": 12 + self.boss_level * 3}
        else:
            return {"type": "targeted", "count": 3 + self.boss_level}

    def take_damage(self, damage):
        self.health -= damage
        self.hit_flash = 0.1
        for _ in range(3):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            velocity = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed
            Particle.create_asteroid_explosion(self.position.x, self.position.y)
        if self.health <= 0 and self.death_timer < 0:
            self.death_timer = 0
            return True
        return False

    def draw(self, screen):
        color = self.color
        if self.hit_flash > 0:
            color = (255, 255, 255)
        self._draw_boss_shape(screen, color)
        self._draw_health_bar(screen)

    def _draw_boss_shape(self, screen, color):
        if self.death_timer >= 0:
            alpha = int(255 * (1 - self.death_timer / BOSS_DEATH_DURATION))
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
