import pygame
from constants import *
from circleshape import CircleShape
from shot import Shot
from sounds import Sounds


class Player(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.shoot_timer = 0  # Neuer Timer startet bei 0
        self.invincible = False
        self.invincible_timer = 0
        self.sounds = Sounds()

    def draw(self, screen):
        # Blinken während Unverwundbarkeit
        if not self.invincible or pygame.time.get_ticks() % 200 < 100:
            pygame.draw.polygon(screen, "white", self.triangle(), 2)

    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def update(self, dt):
        # Timer reduzieren
        if self.shoot_timer > 0:
            self.shoot_timer -= dt

        if self.invincible:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                self.invincible = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.move(dt)
        if keys[pygame.K_s]:
            self.move(-dt)
        if keys[pygame.K_a]:
            self.rotate(-dt)
        if keys[pygame.K_d]:
            self.rotate(dt)
        if keys[pygame.K_SPACE] and self.shoot_timer <= 0:
            self.shoot()

    def shoot(self):
        if self.shoot_timer <= 0:
            shot = Shot(self.position.x, self.position.y)
            shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOOT_SPEED
            self.shoot_timer = PLAYER_SHOOT_COOLDOWN  # Timer zurücksetzen
            self.sounds.play_shoot()  # Schuss-Sound

    def rotate(self, dt):
        self.rotation += PLAYER_TURN_SPEED * dt

    def move(self, dt):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        self.position += forward * PLAYER_SPEED * dt

    def make_invincible(self):
        self.invincible = True
        self.invincible_timer = INVINCIBILITY_TIME

    def respawn(self):
        self.position.x = RESPAWN_POSITION_X
        self.position.y = RESPAWN_POSITION_Y
        self.velocity = pygame.Vector2(0, 0)
        self.rotation = 0
        self.make_invincible()
