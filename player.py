import pygame
from constants import *
from circleshape import CircleShape
from shot import Shot
from sounds import Sounds
import math


class Player(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.velocity = pygame.Vector2(0, 0)
        self.shoot_timer = 0  # Neuer Timer startet bei 0
        self.invincible = False
        self.invincible_timer = 0
        self.sounds = Sounds()
        self.shield_active = False
        self.shield_timer = 0
        self.triple_shot_active = False
        self.triple_shot_timer = 0
        self.rapid_fire_active = False
        self.rapid_fire_timer = 0
        self.original_cooldown = PLAYER_SHOOT_COOLDOWN

    def draw(self, screen):
        # Blinken während Unverwundbarkeit
        if (not self.invincible or pygame.time.get_ticks() % 200 < 100) or self.shield_active:
            pygame.draw.polygon(screen, "white", self.triangle(), 2)
            
        # Schild zeichnen wenn aktiv
        if self.shield_active:
            # Pulsierender Effekt
            alpha = int(128 + 127 * abs(math.sin(pygame.time.get_ticks() * 0.005)))
            shield_color = POWERUP_COLORS["shield"]
            shield_surf = pygame.Surface((self.radius * 3, self.radius * 3), pygame.SRCALPHA)
            
            # Korrigierte Zeile - Farbe und Alpha richtig setzen
            color_obj = pygame.Color(shield_color)
            rgba_color = (color_obj.r, color_obj.g, color_obj.b, alpha)
            
            pygame.draw.circle(shield_surf, rgba_color, 
                            (self.radius * 1.5, self.radius * 1.5), self.radius * 1.4, 2)
            screen.blit(shield_surf, (self.position.x - self.radius * 1.5, 
                                    self.position.y - self.radius * 1.5))

    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def update(self, dt):
        keys = pygame.key.get_pressed()
        
        # Rotation bleibt gleich
        if keys[pygame.K_d]:
            self.rotation += PLAYER_ROTATION_SPEED * dt
        if keys[pygame.K_a]:
            self.rotation -= PLAYER_ROTATION_SPEED * dt
            
        # Beschleunigung - jetzt mit passendem Vektor
        if keys[pygame.K_w]:
            # Verwende den gleichen Vektor wie für die Dreiecksspitze
            direction = pygame.Vector2(0, 1).rotate(self.rotation)
            self.velocity += direction * PLAYER_ACCELERATION * dt
        
        # Rückwärts - jetzt mit passendem Vektor
        if keys[pygame.K_s]:
            # Entgegengesetzt zur Dreiecksspitze
            direction = pygame.Vector2(0, -1).rotate(self.rotation)
            self.velocity += direction * (PLAYER_ACCELERATION * 0.5) * dt  # Langsamer rückwärts
            
        # Geschwindigkeitsbegrenzung
        if self.velocity.length() > PLAYER_MAX_SPEED:
            self.velocity.scale_to_length(PLAYER_MAX_SPEED)
            
        # Reibung
        self.velocity *= (1 - PLAYER_FRICTION)
        
        # Position aktualisieren
        self.position += self.velocity * dt

        # Timer reduzieren
        if self.shoot_timer > 0:
            self.shoot_timer -= dt

        if self.invincible:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                self.invincible = False

        # Power-up Timer aktualisieren
        if self.shield_active:
            self.shield_timer -= dt
            if self.shield_timer <= 0:
                self.shield_active = False
        
        if self.triple_shot_active:
            self.triple_shot_timer -= dt
            if self.triple_shot_timer <= 0:
                self.triple_shot_active = False
        
        if self.rapid_fire_active:
            self.rapid_fire_timer -= dt
            if self.rapid_fire_timer <= 0:
                self.rapid_fire_active = False
                self.shoot_timer = self.original_cooldown  # Reset auf normalen Cooldown

        if keys[pygame.K_SPACE] and self.shoot_timer <= 0:
            self.shoot()

    def shoot(self):
        if self.shoot_timer <= 0:
            if self.triple_shot_active:
                # Dreifachschuss: Normal + 2 mit Winkel
                shot1 = Shot(self.position.x, self.position.y)
                shot1.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOOT_SPEED
                
                shot2 = Shot(self.position.x, self.position.y)
                shot2.velocity = pygame.Vector2(0, 1).rotate(self.rotation - 15) * PLAYER_SHOOT_SPEED
                
                shot3 = Shot(self.position.x, self.position.y)
                shot3.velocity = pygame.Vector2(0, 1).rotate(self.rotation + 15) * PLAYER_SHOOT_SPEED
            else:
                # Normaler Einzelschuss
                shot = Shot(self.position.x, self.position.y)
                shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOOT_SPEED
            
            # Cooldown basierend auf Power-up-Status
            if self.rapid_fire_active:
                self.shoot_timer = RAPID_FIRE_COOLDOWN
            else:
                self.shoot_timer = self.original_cooldown
            
            self.sounds.play_shoot()

    def make_invincible(self):
        self.invincible = True
        self.invincible_timer = INVINCIBILITY_TIME

    def respawn(self):
        # Unverwundbarkeit aktivieren
        self.invincible = True
        self.respawn_timer = 0
        
        # Position und Geschwindigkeit zurücksetzen
        self.position.x = RESPAWN_POSITION_X 
        self.position.y = RESPAWN_POSITION_Y
        self.velocity = pygame.Vector2(0, 0)
        
        # Alle Powerups deaktivieren
        self.shield_active = False
        self.shield_timer = 0
        self.triple_shot_active = False  
        self.triple_shot_timer = 0
        self.rapid_fire_active = False
        self.rapid_fire_timer = 0
        self.shot_cooldown = 0

    def activate_powerup(self, powerup_type):
        if powerup_type == "shield":
            self.shield_active = True
            self.shield_timer = SHIELD_DURATION
            self.invincible = True  # Macht auch unverwundbar
        
        elif powerup_type == "triple_shot":
            self.triple_shot_active = True
            self.triple_shot_timer = TRIPLE_SHOT_DURATION
        
        elif powerup_type == "rapid_fire":
            self.rapid_fire_active = True
            self.rapid_fire_timer = RAPID_FIRE_DURATION
