import pygame
from modul.constants import *
from modul.circleshape import CircleShape
from modul.shot import Shot
from modul.sounds import Sounds
from modul.ships import ship_manager, ShipRenderer
import math

class Player(CircleShape):
    def __init__(self, x, y, ship_type="standard"):
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
        
        self.ship_type = ship_type
        self.ship_data = ship_manager.get_ship_data(ship_type)
        self.apply_ship_modifiers()

    def apply_ship_modifiers(self):
        self.base_speed = PLAYER_SPEED * self.ship_data["speed_multiplier"]
        self.base_turn_speed = PLAYER_TURN_SPEED * self.ship_data["turn_speed_multiplier"]
        
        special = self.ship_data["special_ability"]
        if special == "rear_shot":
            self.shield_duration_multiplier = 1.0
            self.damage_multiplier = 1.0
            self.has_rear_shot = True
        elif special == "speed_boost":
            self.base_speed *= 1.2
            self.shield_duration_multiplier = 1.0
            self.damage_multiplier = 1.0
            self.has_rear_shot = False
        elif special == "double_damage":
            self.damage_multiplier = 2.0
            self.shield_duration_multiplier = 1.0
            self.has_rear_shot = False
        else:
            self.shield_duration_multiplier = 1.0
            self.damage_multiplier = 1.0
            self.has_rear_shot = False

    def draw(self, screen):
        if (not self.invincible or pygame.time.get_ticks() % 200 < 100) or self.shield_active:
            if self.shield_active:
                ship_color = POWERUP_COLORS.get("shield", "cyan")
            else:
                ship_color = self.ship_data.get("color", (255, 255, 255))
            ShipRenderer.draw_ship(screen, self.position.x, self.position.y, 
                                 self.rotation, self.ship_data["shape"], 1.0, ship_color)
        
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

    def triangle(self):
        forward = pygame.Vector2(0, -1).rotate(self.rotation)
        right = pygame.Vector2(1, 0).rotate(self.rotation) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def update(self, dt):
        keys = pygame.key.get_pressed()

        current_speed = self.base_speed
        current_turn_speed = self.base_turn_speed

        if keys[pygame.K_LEFT]:
            self.rotate(-current_turn_speed * dt)
        if keys[pygame.K_RIGHT]:
            self.rotate(current_turn_speed * dt)
        if keys[pygame.K_UP]:
            self.velocity += self.forward() * current_speed * dt
        if keys[pygame.K_DOWN]:
            self.velocity -= self.forward() * current_speed * dt
            
        if keys[pygame.K_SPACE]:
            self.shoot()

        max_speed = getattr(self, 'max_speed', 400)
        if self.velocity.length() > max_speed:
            self.velocity = self.velocity.normalize() * max_speed
            
        friction = 0.98
        self.velocity *= friction

        self.position += self.velocity * dt
        
        if self.shoot_timer > 0:
            self.shoot_timer -= dt
        
        if self.invincible_timer > 0:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                self.invincible = False
                
        if self.shield_timer > 0:
            self.shield_timer -= dt
            if self.shield_timer <= 0:
                self.shield_active = False
                self.invincible = False
                
        if self.triple_shot_timer > 0:
            self.triple_shot_timer -= dt
            if self.triple_shot_timer <= 0:
                self.triple_shot_active = False
                
        if self.rapid_fire_timer > 0:
            self.rapid_fire_timer -= dt
            if self.rapid_fire_timer <= 0:
                self.rapid_fire_active = False

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
                    
                    if hasattr(self, 'has_rear_shot') and self.has_rear_shot:
                        rear_shot = Shot(self.position.x, self.position.y)
                        rear_shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOOT_SPEED * 0.8
            
            elif self.current_weapon == WEAPON_LASER:
                shot = Shot(self.position.x, self.position.y, WEAPON_LASER)
                shot.velocity = pygame.Vector2(0, -1).rotate(self.rotation) * PLAYER_SHOOT_SPEED * 1.5
                self.weapons[WEAPON_LASER] -= 1
                
                if hasattr(self, 'has_rear_shot') and self.has_rear_shot:
                    rear_shot = Shot(self.position.x, self.position.y)
                    rear_shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOOT_SPEED * 0.8
                
            elif self.current_weapon == WEAPON_MISSILE:
                shot = Shot(self.position.x, self.position.y, WEAPON_MISSILE)
                shot.velocity = pygame.Vector2(0, -1).rotate(self.rotation) * PLAYER_SHOOT_SPEED * 0.8
                self.weapons[WEAPON_MISSILE] -= 1
                
                if hasattr(self, 'has_rear_shot') and self.has_rear_shot:
                    rear_shot = Shot(self.position.x, self.position.y)
                    rear_shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOOT_SPEED * 0.8
                
            elif self.current_weapon == WEAPON_SHOTGUN:
                spread = 30
                for i in range(5):
                    angle = self.rotation + (i - 2) * (spread / 4)
                    shot = Shot(self.position.x, self.position.y, WEAPON_SHOTGUN)
                    shot.velocity = pygame.Vector2(0, -1).rotate(angle) * PLAYER_SHOOT_SPEED
                self.weapons[WEAPON_SHOTGUN] -= 1
                
                if hasattr(self, 'has_rear_shot') and self.has_rear_shot:
                    rear_shot = Shot(self.position.x, self.position.y)
                    rear_shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOOT_SPEED * 0.8
            
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
        
        if hasattr(self, 'has_rear_shot') and self.has_rear_shot:
            rear_shot = Shot(self.position.x, self.position.y)
            rear_shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOOT_SPEED * 0.8

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
        self.shoot_timer = 0
        
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
