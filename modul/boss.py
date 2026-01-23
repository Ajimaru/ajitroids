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
        Create a Boss positioned at screen center and initialize level-scaled stats and runtime state.
        
        Parameters:
            level (int): Game progression value; used to compute boss_level (level // 10) and scale max health.
        
        Description:
            - Sets position to screen center and radius from constants.
            - Computes boss_level and max_health, and sets current health to max_health.
            - Initializes visual and gameplay state: color, pulse_timer, rotation, velocity, target_position.
            - Initializes behavior timers and modes: movement_timer, movement_phase, attack_timer, attack_interval, attack_pattern.
            - Initializes transient state for hit flash and death handling (death_timer, death_particles_emitted).
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
        Advance the boss's state for the current frame.
        
        Updates timers and visual state, processes the death sequence (emitting particles and removing the boss when finished), advances movement and attack logic, applies velocity to position, and enforces screen bounds.
        
        Parameters:
            dt (float): Elapsed time since the last update in seconds.
            player_position (Vector2 | None): Current player position used for chasing behavior; pass None if unavailable.
        
        Side effects:
            May emit death particles and call self.kill() when the boss's death sequence completes.
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
        Update the boss's movement phase and set its movement target and velocity.
        
        Manages three movement phases with timed transitions: "center" → "random" after 3.0s, "random" → "chase" after 5.0s (or back to "center" if no player_position is provided), and "chase" → "center" after 4.0s. In "center" the boss moves toward the screen center at the base move speed. In "random" the boss occasionally (≈ every 1.5s) picks a new random on-screen target and moves toward it at 70% of base speed; the chosen target is stored in `self.target_position`. In "chase" (only when player_position is provided) the boss moves toward the player's position at 120% of base speed.
        
        Parameters:
        	dt (float): Time delta in seconds used to advance phase timers.
        	player_position (pygame.Vector2 | None): Current player position to target while in the "chase" phase; if None, the boss will not enter or remain in "chase".
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
        Move the boss toward a target position and decay velocity when already at the target.
        
        Parameters:
            target: A vector-like position to move toward.
            speed (float): Movement speed applied when moving toward the target.
            dt (float, optional): Time delta used to scale velocity decay when the boss is already at `target`. If `dt` is zero or omitted, a legacy fixed decay factor (0.9) is applied.
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
        Ensure the boss remains within the screen bounds by clamping its position to a margin equal to its radius and damping velocity on boundary contact.
        
        If the boss crosses a screen edge, its corresponding coordinate is set to the nearest allowed value (radius inside the edge) and that velocity component is reversed and reduced to half its magnitude.
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
        Advance the internal attack timer and trigger attacks when the interval elapses.
        
        Increments the attack timer by dt; when the timer reaches or exceeds attack_interval, calls attack(), resets the timer to 0, and advances attack_pattern cyclically (0 → 1 → 2 → 0).
        """
        self.attack_timer += dt
        if self.attack_timer >= self.attack_interval:
            self.attack()
            self.attack_timer = 0
            self.attack_pattern = (self.attack_pattern + 1) % 3

    def attack(self):
        """
        Return the boss's current attack pattern description.
        
        Returns:
            dict: Pattern descriptor with keys:
                - type (str): "circle", "spiral", or "targeted".
                - count (int): Number of projectiles — for "circle": 8 + boss_level * 2; for "spiral": 12 + boss_level * 3; for "targeted": 3 + boss_level.
        """
        if self.attack_pattern == 0:
            return {"type": "circle", "count": 8 + self.boss_level * 2}
        elif self.attack_pattern == 1:
            return {"type": "spiral", "count": 12 + self.boss_level * 3}
        else:
            return {"type": "targeted", "count": 3 + self.boss_level}

    def take_damage(self, damage):
        """
        Apply damage to the boss, emit hit effects, and initiate the death sequence when health is depleted.
        
        Reduces the boss's health by the given damage amount, sets a short hit flash for visual feedback, and emits three asteroid-explosion particles at the boss's current position. If health falls to zero or below and the death sequence has not already started, begins the death sequence.
        
        Returns:
            bool: True if the death sequence was started, False otherwise.
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
        Render the boss and its health bar onto the provided screen surface.
        
        When the boss was recently hit it is briefly drawn with a white flash. If the boss is in its death sequence, the visual drawn reflects the death state. This method draws only; it does not modify boss health or state.
        
        Parameters:
            screen (pygame.Surface): Surface to draw the boss and its health bar onto.
        """
        color = self.color
        if self.hit_flash > 0:
            color = (255, 255, 255)
        self._draw_boss_shape(screen, color)
        self._draw_health_bar(screen)

    def _draw_boss_shape(self, screen, color):
        """
        Render the boss visual (outer ring, inner core, satellites) or its death effect onto the provided surface.
        
        When the boss is in its death sequence, draws a single pulsating, fading circle centered at the boss position. Otherwise draws a pulsing layered boss composed of an outer ring, dark inner core, a colored core, and a ring of satellite shapes that orbit based on the boss rotation and level.
        
        Parameters:
            screen (pygame.Surface): Destination surface to draw onto.
            color (tuple[int, int, int]): RGB color used for the boss's colored layers and satellites.
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
        Render the boss's above-head health bar when the boss is alive.
        
        Draws a gray background bar above the boss and fills it proportionally to current health.
        Uses green for >60% health, yellow for 30–60%, and red for <=30%. Does nothing while the boss is in its death sequence.
        
        Parameters:
            screen (pygame.Surface): Surface to draw the health bar onto.
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