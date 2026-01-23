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
        """
        Create a Boss positioned at screen center and initialize its level-dependent stats and runtime state.
        
        Parameters:
            level (int): Global game level used to derive boss difficulty; boss_level is computed as level // 10.
        
        Notes:
            - max_health is computed as C.BOSS_BASE_HEALTH + (boss_level - 1) * C.BOSS_HEALTH_PER_LEVEL and health is set to max_health.
            - Visual and runtime state initialized: color, pulse and rotation timers, velocity, target_position, movement and attack timers/phases, hit flash, and death sequence flags.
        """
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
        """
        Advance the boss's timers, handle death sequence, update movement and attack state, and apply velocity for this frame.
        
        Parameters:
        	dt (float): Time elapsed since the last update, in seconds.
        	player_position (pygame.Vector2 or None): Current player position used for chase behavior; pass None if unavailable.
        """
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
        """
        Advance the boss's movement state and update its target velocity according to the current movement phase.
        
        Parameters:
            dt (float): Time elapsed since the last update in seconds; used to advance the movement timer and to time random target selection.
            player_position (pygame.Vector2 | None): Player world position used when in the "chase" phase; if None, the boss will not chase the player.
        
        Detailed behavior:
            - Phases: "center", "random", "chase". Each phase runs for a fixed duration before transitioning:
                - "center": move toward the screen center at normal speed.
                - "random": periodically pick a new random target within screen margins and move toward it at reduced speed.
                - "chase": move toward the provided player_position at increased speed.
            - Transitions cycle between phases based on the movement timer; if no player_position is available when a transition would select "chase", the boss returns to "center".
        """
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
        """
        Move the boss toward a target point.
        
        Sets the boss's velocity to a vector pointing at `target` with magnitude `speed`. If the boss is already at `target`, reduces the current velocity by a decay factor; when `dt` is provided the decay is scaled by time, otherwise a fixed decay factor is used.
        
        Parameters:
            target (Vector2): Destination position to move toward.
            speed (float): Desired speed when moving toward the target.
            dt (float, optional): Elapsed time used to scale the velocity decay when at the target. If zero or omitted, a fixed decay factor is applied.
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
        """
        Keep the boss inside the screen bounds and reflect velocity when it crosses an edge.
        
        If the boss position moves beyond the screen margin equal to its radius, clamp the position to that margin and invert the corresponding velocity component while halving its magnitude.
        """
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
        """
        Advance the boss's attack timing and trigger the next attack pattern when the interval elapses.
        
        Parameters:
        	dt (float): Elapsed time in seconds since the last update; added to the internal attack timer.
        
        Description:
        	If the internal attack timer meets or exceeds the configured attack interval, this increments
        	the attack pattern (cycling through available patterns), resets the attack timer to zero,
        	and invokes the boss's attack behavior.
        """
        self.attack_timer += dt
        if self.attack_timer >= self.attack_interval:
            self.attack()
            self.attack_timer = 0
            self.attack_pattern = (self.attack_pattern + 1) % 3

    def attack(self):
        """
        Selects the next attack pattern and returns a configuration describing that attack.
        
        The returned configuration describes the attack kind and how many projectiles it will produce; the projectile count scales with the boss's level.
        
        Returns:
            dict: {
                'type': one of 'circle', 'spiral', 'targeted',
                'count': int — number of projectiles for this attack (scaled by boss level)
            }
        """
        if self.attack_pattern == 0:
            return {"type": "circle", "count": 8 + self.boss_level * 2}
        elif self.attack_pattern == 1:
            return {"type": "spiral", "count": 12 + self.boss_level * 3}
        else:
            return {"type": "targeted", "count": 3 + self.boss_level}

    def take_damage(self, damage):
        """
        Reduce the boss's health by a given amount, emit hit effects, and initiate the death sequence if health is depleted.
        
        Parameters:
            damage (float): Amount of health to subtract from the boss.
        
        Returns:
            bool: `True` if this call started the death sequence (health <= 0 and death was not already triggered), `False` otherwise.
        """
        self.health -= damage
        self.hit_flash = 0.1
        for _ in range(3):
            Particle.create_asteroid_explosion(self.position.x, self.position.y)
        if self.health <= 0 and self.death_timer < 0:
            self.death_timer = 0
            return True
        return False

    def draw(self, screen):
        """
        Render the boss and its health bar onto the given surface.
        
        Renders the boss's visual representation (including a brief white flash when recently hit) and the health bar positioned above the boss.
        
        Parameters:
            screen (pygame.Surface): Surface to draw the boss and its health bar on.
        """
        color = self.color
        if self.hit_flash > 0:
            color = (255, 255, 255)
        self._draw_boss_shape(screen, color)
        self._draw_health_bar(screen)

    def _draw_boss_shape(self, screen, color):
        """
        Render the boss's circular body, inner core, orbiting satellites, or its death animation.
        
        Parameters:
            screen (pygame.Surface): Surface to draw the boss on.
            color (tuple[int, int, int]): RGB color used for the boss visuals.
        """
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
        """
        Draws the boss's health bar above its position and skips rendering during the death sequence.
        
        The bar's width scales with the boss radius and shows a dark background with a foreground whose width is proportional to current health. Foreground color is green when health > 0.6, yellow when health > 0.3, and red otherwise. The bar is positioned above the boss and is not drawn if the death sequence is active.
        
        Parameters:
            screen (pygame.Surface): Surface to draw the health bar on.
        """
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