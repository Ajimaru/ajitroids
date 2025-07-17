import pygame
from modul.constants import *
from modul.circleshape import CircleShape
from modul.shot import Shot
from modul.sounds import Sounds
import math

class Player(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.velocity = pygame.Vector2(0, 0)
        self.shoot_timer = 0
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
        self.current_weapon = WEAPON_STANDARD
        self.weapons = {
            WEAPON_STANDARD: -1,
            WEAPON_LASER: 0,
            WEAPON_MISSILE: 0,
            WEAPON_SHOTGUN: 0
        }

    def draw(self, screen):
        if (not self.invincible or pygame.time.get_ticks() % 200 < 100) or self.shield_active:
            pygame.draw.polygon(screen, "white", self.triangle(), 2)
        
        if self.shield_active:
            alpha = int(128 + 127 * abs(math.sin(pygame.time.get_ticks() * 0.005)))
            shield_color = POWERUP_COLORS["shield"]
            shield_surf = pygame.Surface((self.radius * 3, self.radius * 3), pygame.SRCALPHA)
        
            color_obj = pygame.Color(shield_color)
            rgba_color = (color_obj.r, color_obj.g, color_obj.b, alpha)
        
            pygame.draw.circle(shield_surf, rgba_color, 
                            (self.radius * 1.5, self.radius * 1.5), self.radius * 1.4, 2)
            screen.blit(shield_surf, (self.position.x - self.radius * 1.5, 
                                    self.position.y - self.radius * 1.5))

        if self.invincible and pygame.time.get_ticks() % 300 < 150:
            color = (100, 100, 255)
        else:
            color = (255, 255, 255)

        pygame.draw.polygon(screen, color, self.triangle(), 2)

    def triangle(self):
        forward = pygame.Vector2(0, -1).rotate(self.rotation)
        right = pygame.Vector2(1, 0).rotate(self.rotation) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def update(self, dt):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self.rotation -= PLAYER_ROTATION_SPEED * dt
        if keys[pygame.K_RIGHT]:
            self.rotation += PLAYER_ROTATION_SPEED * dt
        
        if keys[pygame.K_UP]:
            direction = pygame.Vector2(0, -1).rotate(self.rotation)
            self.velocity += direction * (PLAYER_ACCELERATION * 0.5) * dt
        
        if keys[pygame.K_DOWN]:
            direction = pygame.Vector2(0, 1).rotate(self.rotation)
            self.velocity += direction * PLAYER_ACCELERATION * dt
    
        if keys[pygame.K_w]:
            direction = pygame.Vector2(0, -1).rotate(self.rotation)
            self.velocity += direction * (PLAYER_ACCELERATION * 0.5) * dt
        
        if self.velocity.length() > PLAYER_MAX_SPEED:
            self.velocity.scale_to_length(PLAYER_MAX_SPEED)
        
        self.velocity *= (1 - PLAYER_FRICTION)
        
        self.position += self.velocity * dt

        if self.shoot_timer > 0:
            self.shoot_timer -= dt

        if self.invincible:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                self.invincible = False

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
                self.shoot_timer = self.original_cooldown

        if keys[pygame.K_SPACE] and self.shoot_timer <= 0:
            self.shoot()

    def shoot(self):
        if self.shoot_timer <= 0:
            if self.current_weapon != WEAPON_STANDARD and self.weapons[self.current_weapon] <= 0:
                self.current_weapon = WEAPON_STANDARD
            
            if self.current_weapon == WEAPON_STANDARD:
                if self.triple_shot_active:
                    self.fire_triple_shot()
                else:
                    shot = Shot(self.position.x, self.position.y)
                    shot.velocity = pygame.Vector2(0, -1).rotate(self.rotation) * PLAYER_SHOOT_SPEED
            
            elif self.current_weapon == WEAPON_LASER:
                shot = Shot(self.position.x, self.position.y, WEAPON_LASER)
                shot.velocity = pygame.Vector2(0, -1).rotate(self.rotation) * PLAYER_SHOOT_SPEED * 1.5
                self.weapons[WEAPON_LASER] -= 1
                
            elif self.current_weapon == WEAPON_MISSILE:
                shot = Shot(self.position.x, self.position.y, WEAPON_MISSILE)
                shot.velocity = pygame.Vector2(0, -1).rotate(self.rotation) * PLAYER_SHOOT_SPEED * 0.8
                self.weapons[WEAPON_MISSILE] -= 1
                
            elif self.current_weapon == WEAPON_SHOTGUN:
                spread = 30
                for i in range(5):
                    angle = self.rotation + (i - 2) * (spread / 4)
                    shot = Shot(self.position.x, self.position.y, WEAPON_SHOTGUN)
                    shot.velocity = pygame.Vector2(0, -1).rotate(angle) * PLAYER_SHOOT_SPEED
                self.weapons[WEAPON_SHOTGUN] -= 1
            
            if hasattr(self, 'sounds') and self.sounds:
                self.sounds.play_shoot()
            
            if self.rapid_fire_active:
                self.shoot_timer = RAPID_FIRE_COOLDOWN
            else:
                self.shoot_timer = PLAYER_SHOOT_COOLDOWN

    def fire_triple_shot(self):
        shot1 = Shot(self.position.x, self.position.y)
        shot1.velocity = pygame.Vector2(0, -1).rotate(self.rotation) * PLAYER_SHOOT_SPEED
        
        shot2 = Shot(self.position.x, self.position.y)
        shot2.velocity = pygame.Vector2(0, -1).rotate(self.rotation - 15) * PLAYER_SHOOT_SPEED
        
        shot3 = Shot(self.position.x, self.position.y)
        shot3.velocity = pygame.Vector2(0, -1).rotate(self.rotation + 15) * PLAYER_SHOOT_SPEED

    def make_invincible(self):
        self.invincible = True
        self.invincible_timer = INVINCIBILITY_TIME

    def respawn(self):
        self.position.x = SCREEN_WIDTH / 2
        self.position.y = SCREEN_HEIGHT / 2
        self.velocity = pygame.Vector2(0, 0)
        self.rotation = 0
        
        self.invincible = True
        self.invincible_timer = 3.0
        
        self.shield_active = False
        self.shield_timer = 0
        self.triple_shot_active = False  
        self.triple_shot_timer = 0
        self.rapid_fire_active = False
        self.rapid_fire_timer = 0
        self.shot_cooldown = 0
        
        print("Player respawned with 3 seconds of invincibility")

    def activate_powerup(self, powerup_type):
        if powerup_type == "shield":
            self.shield_active = True
            self.shield_timer = SHIELD_DURATION
            self.invincible = True
        
        elif powerup_type == "triple_shot":
            self.triple_shot_active = True
            self.triple_shot_timer = TRIPLE_SHOT_DURATION
        
        elif powerup_type == "rapid_fire":
            self.rapid_fire_active = True
            self.rapid_fire_timer = RAPID_FIRE_DURATION
            
        elif powerup_type == "laser_weapon":
            self.weapons[WEAPON_LASER] += LASER_AMMO
            self.current_weapon = WEAPON_LASER
            print(f"Laser weapon activated! Ammo: {self.weapons[WEAPON_LASER]}")
            
        elif powerup_type == "missile_weapon":
            self.weapons[WEAPON_MISSILE] += MISSILE_AMMO
            self.current_weapon = WEAPON_MISSILE
            print(f"Missile weapon activated! Ammo: {self.weapons[WEAPON_MISSILE]}")
            
        elif powerup_type == "shotgun_weapon":
            self.weapons[WEAPON_SHOTGUN] += SHOTGUN_AMMO
            self.current_weapon = WEAPON_SHOTGUN
            print(f"Shotgun activated! Ammo: {self.weapons[WEAPON_SHOTGUN]}")

    def cycle_weapon(self):
        weapon_list = list(self.weapons.keys())
        current_index = weapon_list.index(self.current_weapon)
        
        for i in range(1, len(weapon_list)):
            next_index = (current_index + i) % len(weapon_list)
            next_weapon = weapon_list[next_index]
            
            if next_weapon == WEAPON_STANDARD or self.weapons[next_weapon] > 0:
                self.current_weapon = next_weapon
                print(f"Weapon switched to: {self.current_weapon}, Ammo: {self.weapons[self.current_weapon]}")
                return
        
        self.current_weapon = WEAPON_STANDARD

    def draw_weapon_hud(self, screen):
        font = pygame.font.Font(None, 24)
        
        weapon_radius = 8
        weapon_pos = (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 30)
        pygame.draw.circle(screen, WEAPON_COLORS[self.current_weapon], weapon_pos, weapon_radius)
        
        if self.current_weapon != WEAPON_STANDARD:
            ammo_text = font.render(f"{self.weapons[self.current_weapon]}", True, WEAPON_COLORS[self.current_weapon])
            screen.blit(ammo_text, (SCREEN_WIDTH - 30, SCREEN_HEIGHT - 35))
