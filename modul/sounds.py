import pygame
import os

class Sounds:
    def __init__(self):
        pygame.mixer.init(44100, -16, 2, 2048)
        self.shoot = None
        self.explosion = None
        self.player_death = None
        self.menu_move = None
        self.menu_select = None
        self.level_up = None
        try:
            self.shoot = pygame.mixer.Sound("assets/shoot.wav")
            self.shoot.set_volume(0.05)
        except:
            print("Shoot sound could not be loaded")
        try:
            self.explosion = pygame.mixer.Sound("assets/explosion.wav")
            self.explosion.set_volume(0.4)
        except:
            print("Explosion sound could not be loaded")
        try:
            self.player_death = pygame.mixer.Sound("assets/player_hit.wav")
            self.player_death.set_volume(0.5)
        except:
            print("Player-Death sound could not be loaded")
        try:
            self.menu_move = pygame.mixer.Sound("assets/menu_select.wav")
            self.menu_select = pygame.mixer.Sound("assets/menu_confirm.wav")
            if self.menu_move:
                self.menu_move.set_volume(0.3)
            if self.menu_select:
                self.menu_select.set_volume(0.4)
        except:
            self.menu_move = None
            self.menu_select = None
            print("Menu sounds could not be loaded")
        try:
            pygame.mixer.music.load("assets/background.mp3")
            pygame.mixer.music.set_volume(0.6)
        except Exception as e:
            print(f"Error loading background music: {e}")
            print(f"Current directory: {os.getcwd()}")
            print(f"File exists: {os.path.exists('assets/background.mp3')}")
        self.sound_on = True
        self.load_new_sounds()
    def load_new_sounds(self):
        try:
            self.laser_shoot = pygame.mixer.Sound("assets/laser_shoot.wav")
            self.laser_shoot.set_volume(0.2)
        except:
            self.laser_shoot = None
            print("Laser shoot sound could not be loaded")
        try:
            self.rocket_shoot = pygame.mixer.Sound("assets/rocket_shoot.wav")
            self.rocket_shoot.set_volume(0.3)
        except:
            self.rocket_shoot = None
            print("Rocket shoot sound could not be loaded")
        try:
            self.boss_spawn = pygame.mixer.Sound("assets/boss_spawn.wav")
            self.boss_spawn.set_volume(0.4)
        except:
            self.boss_spawn = None
            print("Boss spawn sound could not be loaded")
        try:
            self.boss_death = pygame.mixer.Sound("assets/boss_death.wav")
            self.boss_death.set_volume(0.5)
        except:
            self.boss_death = None
        try:
            self.powerup = pygame.mixer.Sound("assets/powerup.wav")
            self.powerup.set_volume(0.4)
        except:
            self.powerup = None
            print("PowerUp sound could not be loaded")
        try:
            self.shield_activate = pygame.mixer.Sound("assets/shield_hit.wav")
            self.shield_activate.set_volume(0.3)
        except:
            self.shield_activate = None
        try:
            self.level_up = pygame.mixer.Sound("assets/level_up.wav")
            self.level_up.set_volume(0.4)
        except:
            self.level_up = None
            print("Level-Up sound could not be loaded")
        try:
            self.game_over = pygame.mixer.Sound("assets/game_over.wav")
            self.game_over.set_volume(0.6)
        except:
            self.game_over = None
            print("Game-Over sound could not be loaded")
        try:
            self.player_hit = pygame.mixer.Sound("assets/player_hit.wav")
            self.player_hit.set_volume(0.7)
        except:
            self.player_hit = None
            print("Player-Hit sound could not be loaded")
    def play_shoot(self):
        if self.sound_on and self.shoot:
            self.shoot.play()
    def play_explosion(self):
        if self.sound_on and self.explosion:
            self.explosion.play()
    def play_player_death(self):
        if self.sound_on and self.player_death:
            self.player_death.play()
    def play_menu_move(self):
        if self.sound_on and self.menu_move:
            self.menu_move.play()
    def play_menu_select(self):
        if self.sound_on and self.menu_select:
            self.menu_select.play()
    def play_level_up(self):
        if self.sound_on and self.level_up:
            self.level_up.play()
    def play_achievement(self):
        if self.sound_on and self.level_up:
            self.level_up.play()
    def play_powerup(self):
        if self.sound_on and self.powerup:
            self.powerup.play()
    def play_laser_shoot(self):
        if self.sound_on and self.laser_shoot:
            self.laser_shoot.play()
    def play_rocket_shoot(self):
        if self.sound_on and self.rocket_shoot:
            self.rocket_shoot.play()
    def play_boss_spawn(self):
        if self.sound_on and self.boss_spawn:
            self.boss_spawn.play()
    def play_boss_death(self):
        if self.sound_on and self.boss_death:
            self.boss_death.play()
    def play_shield_activate(self):
        if self.sound_on and self.shield_activate:
            self.shield_activate.play()
    def play_achievement(self):
        if self.sound_on and self.level_up:
            self.level_up.play()
        else:
            print("Achievement sound not available (Level-Up sound missing)")
    def play_game_over(self):
        if self.sound_on and hasattr(self, 'game_over') and self.game_over:
            self.game_over.play()
        else:
            print("Game Over sound not available or disabled")
    def toggle_music(self, enabled):
        try:
            if enabled:
                pygame.mixer.music.set_volume(0.6)
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.load("assets/background.mp3")
                    pygame.mixer.music.play(-1)
                    print("toggle_music: Music reloaded and started")
                else:
                    print("toggle_music: Music is already playing")
            else:
                pygame.mixer.music.stop()
                pygame.mixer.music.set_volume(0.0)
                print("toggle_music: Music stopped and volume set to 0")
        except Exception as e:
            print(f"Error toggling music: {e}")
    def toggle_sound(self, enabled):
        self.sound_on = enabled
        volume = 0.5 if enabled else 0.0
        sound_attributes = ['shoot', 'explosion', 'player_death', 'powerup', 
                           'laser_shoot', 'rocket_shoot', 'boss_spawn', 'boss_death',
                           'shield_activate', 'level_up']
        for attr_name in sound_attributes:
            if hasattr(self, attr_name):
                sound = getattr(self, attr_name)
                if sound:
                    sound.set_volume(volume)
        menu_volume = 0.3 if enabled else 0.0
        if self.menu_move:
            self.menu_move.set_volume(menu_volume)
        if self.menu_select:
            self.menu_select.set_volume(menu_volume)
    def play_boss_music(self):
        try:
            if pygame.mixer.get_init() is not None:
                pygame.mixer.music.load("assets/boss_music.mp3")
                pygame.mixer.music.set_volume(0.6)
                pygame.mixer.music.play(-1)
                print("Boss music started")
        except Exception as e:
            print(f"Boss music could not be loaded: {e}")
    def play_hit(self):
        if self.sound_on and hasattr(self, 'explosion') and self.explosion:
            self.explosion.play()
    def play_extra_life(self):
        if self.sound_on and hasattr(self, 'level_up') and self.level_up:
            self.level_up.play()
        else:
            print("Extra Life sound not available or disabled")
    def play_enemy_shoot(self):
        if self.sound_on and hasattr(self, 'boss_attack') and self.boss_attack:
            self.boss_attack.play()
        else:
            if self.sound_on and self.shoot:
                self.shoot.play()
    def play_player_hit(self):
        if self.sound_on and hasattr(self, 'player_hit') and self.player_hit:
            self.player_hit.play()
            print("Player Hit Sound played")
        else:
            print("Player Hit Sound not available - using fallback")
            if self.sound_on and hasattr(self, 'explosion') and self.explosion:
                self.explosion.play()