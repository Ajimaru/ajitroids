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

        # Waffen-System
        self.current_weapon = WEAPON_STANDARD
        self.weapons = {
            WEAPON_STANDARD: -1,  # Unendlich Munition
            WEAPON_LASER: 0,      # Keine Munition zu Beginn
            WEAPON_MISSILE: 0,
            WEAPON_SHOTGUN: 0
        }

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

        # Blinken bei Unverwundbarkeit
        if self.invincible and pygame.time.get_ticks() % 300 < 150:
            color = (100, 100, 255)  # Blau für Unverwundbarkeit
        else:
            color = (255, 255, 255)  # Normal weiß

        # Raumschiff mit dieser Farbe zeichnen
        pygame.draw.polygon(screen, color, self.triangle(), 2)

    def triangle(self):
        # Der Vektor (0, -1) zeigt nach oben, damit die Schussrichtung stimmt
        forward = pygame.Vector2(0, -1).rotate(self.rotation)
        right = pygame.Vector2(1, 0).rotate(self.rotation) * self.radius / 1.5
        a = self.position + forward * self.radius  # Spitze des Dreiecks
        b = self.position - forward * self.radius - right  # Untere linke Ecke
        c = self.position - forward * self.radius + right  # Untere rechte Ecke
        return [a, b, c]

    def update(self, dt):
        keys = pygame.key.get_pressed()
        
        # Rotation mit Pfeiltasten (statt A/D)
        if keys[pygame.K_LEFT]:  # Geändert von pygame.K_a
            self.rotation -= PLAYER_ROTATION_SPEED * dt
        if keys[pygame.K_RIGHT]:  # Geändert von pygame.K_d
            self.rotation += PLAYER_ROTATION_SPEED * dt
            
        # Beschleunigung mit Pfeiltasten (statt W/S)
        if keys[pygame.K_UP]:  # Geändert von pygame.K_w
            # Entgegengesetzt zur Dreiecksspitze
            direction = pygame.Vector2(0, -1).rotate(self.rotation)
            self.velocity += direction * (PLAYER_ACCELERATION * 0.5) * dt  # Langsamer rückwärts
            
        if keys[pygame.K_DOWN]:  # Geändert von pygame.K_s
            # Verwende den gleichen Vektor wie für die Dreiecksspitze
            direction = pygame.Vector2(0, 1).rotate(self.rotation)
            self.velocity += direction * PLAYER_ACCELERATION * dt
    
        # Rückwärts - jetzt mit passendem Vektor
        if keys[pygame.K_w]:
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
            # Prüfen, ob die aktuelle Waffe Munition hat
            if self.current_weapon != WEAPON_STANDARD and self.weapons[self.current_weapon] <= 0:
                # Automatisch zur Standard-Waffe zurückkehren
                self.current_weapon = WEAPON_STANDARD
            
            # Verschiedene Schuss-Typen basierend auf aktueller Waffe
            if self.current_weapon == WEAPON_STANDARD:
                # Standard-Schuss oder Triple-Shot
                if self.triple_shot_active:
                    self.fire_triple_shot()
                else:
                    shot = Shot(self.position.x, self.position.y)
                    shot.velocity = pygame.Vector2(0, -1).rotate(self.rotation) * PLAYER_SHOOT_SPEED
            
            elif self.current_weapon == WEAPON_LASER:
                # Laser-Schuss
                shot = Shot(self.position.x, self.position.y, WEAPON_LASER)
                shot.velocity = pygame.Vector2(0, -1).rotate(self.rotation) * PLAYER_SHOOT_SPEED * 1.5
                self.weapons[WEAPON_LASER] -= 1
                
            elif self.current_weapon == WEAPON_MISSILE:
                # Raketen-Schuss
                shot = Shot(self.position.x, self.position.y, WEAPON_MISSILE)
                shot.velocity = pygame.Vector2(0, -1).rotate(self.rotation) * PLAYER_SHOOT_SPEED * 0.8
                self.weapons[WEAPON_MISSILE] -= 1
                
            elif self.current_weapon == WEAPON_SHOTGUN:
                # Schrotflinte (5 Schüsse im Fächer)
                spread = 30  # Grad
                for i in range(5):
                    angle = self.rotation + (i - 2) * (spread / 4)
                    shot = Shot(self.position.x, self.position.y, WEAPON_SHOTGUN)
                    shot.velocity = pygame.Vector2(0, -1).rotate(angle) * PLAYER_SHOOT_SPEED
                self.weapons[WEAPON_SHOTGUN] -= 1
            
            # Sound abspielen
            if hasattr(self, 'sounds') and self.sounds:
                self.sounds.play_shoot()
            
            # Cooldown für nächsten Schuss
            if self.rapid_fire_active:
                self.shoot_timer = RAPID_FIRE_COOLDOWN
            else:
                self.shoot_timer = PLAYER_SHOOT_COOLDOWN

    def fire_triple_shot(self):
        # Dreifachschuss: Normal + 2 mit Winkel
        shot1 = Shot(self.position.x, self.position.y)
        # Hier ist der Fehler: (0, 1) zeigt nach unten, nicht nach oben
        # Ändern zu:
        shot1.velocity = pygame.Vector2(0, -1).rotate(self.rotation) * PLAYER_SHOOT_SPEED
        
        shot2 = Shot(self.position.x, self.position.y)
        # Auch hier korrigieren:
        shot2.velocity = pygame.Vector2(0, -1).rotate(self.rotation - 15) * PLAYER_SHOOT_SPEED
        
        shot3 = Shot(self.position.x, self.position.y)
        # Und hier:
        shot3.velocity = pygame.Vector2(0, -1).rotate(self.rotation + 15) * PLAYER_SHOOT_SPEED

    def make_invincible(self):
        self.invincible = True
        self.invincible_timer = INVINCIBILITY_TIME

    def respawn(self):
        """Setzt den Spieler zurück und macht ihn vorübergehend unverwundbar"""
        self.position.x = SCREEN_WIDTH / 2
        self.position.y = SCREEN_HEIGHT / 2
        self.velocity = pygame.Vector2(0, 0)
        self.rotation = 0
        
        # Drei Sekunden unverwundbar machen
        self.invincible = True
        self.invincible_timer = 3.0  # 3 Sekunden Unverwundbarkeit
        
        # Powerups zurücksetzen
        self.shield_active = False
        self.shield_timer = 0
        self.triple_shot_active = False  
        self.triple_shot_timer = 0
        self.rapid_fire_active = False
        self.rapid_fire_timer = 0
        self.shot_cooldown = 0
        
        print("Spieler respawnt mit 3 Sekunden Unverwundbarkeit")

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
            
        elif powerup_type == "laser_weapon":
            self.weapons[WEAPON_LASER] += LASER_AMMO
            self.current_weapon = WEAPON_LASER
            print(f"Laser-Waffe aktiviert! Munition: {self.weapons[WEAPON_LASER]}")
            
        elif powerup_type == "missile_weapon":
            self.weapons[WEAPON_MISSILE] += MISSILE_AMMO
            self.current_weapon = WEAPON_MISSILE
            print(f"Raketen-Waffe aktiviert! Munition: {self.weapons[WEAPON_MISSILE]}")
            
        elif powerup_type == "shotgun_weapon":
            self.weapons[WEAPON_SHOTGUN] += SHOTGUN_AMMO
            self.current_weapon = WEAPON_SHOTGUN
            print(f"Schrotgewehr aktiviert! Munition: {self.weapons[WEAPON_SHOTGUN]}")

    def cycle_weapon(self):
        """Wechselt zur nächsten verfügbaren Waffe"""
        weapon_list = list(self.weapons.keys())
        current_index = weapon_list.index(self.current_weapon)
        
        # Nach der nächsten Waffe mit Munition suchen
        for i in range(1, len(weapon_list)):
            next_index = (current_index + i) % len(weapon_list)
            next_weapon = weapon_list[next_index]
            
            # Standard-Waffe hat immer Munition, andere nur wenn > 0
            if next_weapon == WEAPON_STANDARD or self.weapons[next_weapon] > 0:
                self.current_weapon = next_weapon
                print(f"Waffe gewechselt zu: {self.current_weapon}, Munition: {self.weapons[self.current_weapon]}")
                return
        
        # Wenn keine Waffe Munition hat, bleib bei Standard
        self.current_weapon = WEAPON_STANDARD

    def draw_weapon_hud(self, screen):
        """Zeigt aktuelle Waffe und Munition auf dem Bildschirm an"""
        font = pygame.font.Font(None, 24)
        
        # Waffen-Symbol
        weapon_radius = 8
        weapon_pos = (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 30)
        pygame.draw.circle(screen, WEAPON_COLORS[self.current_weapon], weapon_pos, weapon_radius)
        
        # Munitionsanzeige
        if self.current_weapon != WEAPON_STANDARD:
            ammo_text = font.render(f"{self.weapons[self.current_weapon]}", True, WEAPON_COLORS[self.current_weapon])
            screen.blit(ammo_text, (SCREEN_WIDTH - 30, SCREEN_HEIGHT - 35))
