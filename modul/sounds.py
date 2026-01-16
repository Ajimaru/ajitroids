import pygame
import os
from pathlib import Path


def asset_path(name: str) -> str:
    """Resolve asset path from CWD or packaged assets directory."""
    cwd_candidate = Path.cwd() / "assets" / name
    if cwd_candidate.exists():
        return str(cwd_candidate)
    return str(Path(__file__).resolve().parent / "assets" / name)


def apply_volume_curve(slider_value):
    """Apply exponential curve to volume slider.

    0.5 (50%) maps to 1.0 (normal/reference volume).
    Below 0.5: reduces volume exponentially.
    Above 0.5: increases volume exponentially.

    Formula: 2^(2*(x - 0.5))
    - 0% → 0.25x (very quiet)
    - 25% → ~0.7x
    - 50% → 1.0x (normal)
    - 75% → ~1.4x
    - 100% → 2.0x (double)
    """
    return 2 ** (2 * (slider_value - 0.5))


class Sounds:
    # Base volume levels for individual sound effects (relative to master volume)
    BASE_VOLUMES = {
        "shoot": 0.5,
        "explosion": 0.6,
        "player_death": 0.7,
        "menu_move": 0.3,
        "menu_select": 0.3,
        "laser_shoot": 0.2,
        "rocket_shoot": 0.25,
        "boss_spawn": 0.4,
        "boss_death": 0.5,
        "powerup": 0.4,
        "shield_activate": 0.3,
        "level_up": 0.4,
        "game_over": 0.6,
        "player_hit": 0.7,
    }

    def __init__(self):
        pygame.mixer.init(44100, -16, 2, 2048)
        self.shoot = None
        self.explosion = None
        self.player_death = None
        self.menu_move = None
        self.menu_select = None
        self.level_up = None
        self.master_volume = 1.0  # Track master volume for proper scaling
        try:
            self.shoot = pygame.mixer.Sound(asset_path("shoot.wav"))
        except:
            print("Shoot sound could not be loaded")
        try:
            self.explosion = pygame.mixer.Sound(asset_path("explosion.wav"))
        except:
            print("Explosion sound could not be loaded")
        try:
            self.player_death = pygame.mixer.Sound(asset_path("player_hit.wav"))
        except:
            print("Player-Death sound could not be loaded")
        try:
            self.menu_move = pygame.mixer.Sound(asset_path("menu_select.wav"))
            self.menu_select = pygame.mixer.Sound(asset_path("menu_confirm.wav"))
        except:
            self.menu_move = None
            self.menu_select = None
            print("Menu sounds could not be loaded")
        try:
            pygame.mixer.music.load(asset_path("background.mp3"))
        except Exception as e:
            print(f"Error loading background music: {e}")
            print(f"Current directory: {os.getcwd()}")
            print(f"File exists: {os.path.exists(asset_path('background.mp3'))}")
        self.sound_on = True
        self.load_new_sounds()

    def load_new_sounds(self):
        try:
            self.laser_shoot = pygame.mixer.Sound(asset_path("laser_shoot.wav"))
        except:
            self.laser_shoot = None
            print("Laser shoot sound could not be loaded")
        try:
            self.rocket_shoot = pygame.mixer.Sound(asset_path("rocket_shoot.wav"))
        except:
            self.rocket_shoot = None
            print("Rocket shoot sound could not be loaded")
        try:
            self.boss_spawn = pygame.mixer.Sound(asset_path("boss_spawn.wav"))
        except:
            self.boss_spawn = None
            print("Boss spawn sound could not be loaded")
        try:
            self.boss_death = pygame.mixer.Sound(asset_path("boss_death.wav"))
        except:
            self.boss_death = None
        try:
            self.powerup = pygame.mixer.Sound(asset_path("powerup.wav"))
        except:
            self.powerup = None
            print("PowerUp sound could not be loaded")
        try:
            self.shield_activate = pygame.mixer.Sound(asset_path("shield_hit.wav"))
        except:
            self.shield_activate = None
        try:
            self.level_up = pygame.mixer.Sound(asset_path("level_up.wav"))
        except:
            self.level_up = None
            print("Level-Up sound could not be loaded")
        try:
            self.game_over = pygame.mixer.Sound(asset_path("game_over.wav"))
        except:
            self.game_over = None
            print("Game-Over sound could not be loaded")
        try:
            self.player_hit = pygame.mixer.Sound(asset_path("player_hit.wav"))
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
        if self.sound_on and hasattr(self, "game_over") and self.game_over:
            self.game_over.play()
        else:
            print("Game Over sound not available or disabled")

    def set_music_volume(self, slider_value):
        """Set music volume using the exponential curve.

        0.5 (50%) = normal volume (1.0x).
        Below 0.5 = quieter, above 0.5 = louder.
        """
        slider_value = max(0.0, min(1.0, slider_value))
        curve_volume = apply_volume_curve(slider_value)
        pygame.mixer.music.set_volume(curve_volume)

    def toggle_music(self, enabled):
        try:
            if enabled:
                pygame.mixer.music.set_volume(0.6)
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.load(asset_path("background.mp3"))
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
        """Toggle sound on/off. Keep master volume unchanged."""
        self.sound_on = enabled
        # Re-apply current master_volume to all sounds
        if enabled:
            # Sound is enabled, apply current master volume
            self.set_effects_volume(self.master_volume)
        else:
            # Sound is disabled, mute all sounds
            sound_attributes = [
                "shoot", "explosion", "player_death", "powerup",
                "laser_shoot", "rocket_shoot", "boss_spawn", "boss_death",
                "shield_activate", "level_up", "game_over", "player_hit",
                "menu_move", "menu_select",
            ]
            for attr_name in sound_attributes:
                if hasattr(self, attr_name):
                    sound = getattr(self, attr_name)
                    if sound:
                        sound.set_volume(0.0)

    def play_boss_music(self):
        try:
            if pygame.mixer.get_init() is not None:
                pygame.mixer.music.load(asset_path("boss_music.mp3"))
                pygame.mixer.music.set_volume(0.6)
                pygame.mixer.music.play(-1)
                print("Boss music started")
        except Exception as e:
            print(f"Boss music could not be loaded: {e}")

    def play_hit(self):
        if self.sound_on and hasattr(self, "explosion") and self.explosion:
            self.explosion.play()

    def play_extra_life(self):
        if self.sound_on and hasattr(self, "level_up") and self.level_up:
            self.level_up.play()
        else:
            print("Extra Life sound not available or disabled")

    def play_enemy_shoot(self):
        if self.sound_on and hasattr(self, "boss_attack") and self.boss_attack:
            self.boss_attack.play()
        else:
            if self.sound_on and self.shoot:
                self.shoot.play()

    def play_player_hit(self):
        if self.sound_on and hasattr(self, "player_hit") and self.player_hit:
            self.player_hit.play()
            print("Player Hit Sound played")
        else:
            print("Player Hit Sound not available - using fallback")
            if self.sound_on and hasattr(self, "explosion") and self.explosion:
                self.explosion.play()

    def set_effects_volume(self, volume):
        """Set master volume for all sound effects.

        Applies exponential curve where 0.5 (50%) = normal.
        Each sound uses its base volume multiplied by the curve.
        """
        # Clamp slider value to 0.0-1.0
        slider_value = max(0.0, min(1.0, volume))
        # Apply exponential curve: 50% = 1.0x, below = quieter, above = louder
        curve_multiplier = apply_volume_curve(slider_value)
        self.master_volume = curve_multiplier

        # Apply master volume with base volume multiplication
        if self.shoot:
            vol = self.BASE_VOLUMES["shoot"] * self.master_volume
            self.shoot.set_volume(vol)
        if self.explosion:
            vol = self.BASE_VOLUMES["explosion"] * self.master_volume
            self.explosion.set_volume(vol)
        if self.player_death:
            vol = self.BASE_VOLUMES["player_death"] * self.master_volume
            self.player_death.set_volume(vol)
        if self.menu_move:
            vol = self.BASE_VOLUMES["menu_move"] * self.master_volume
            self.menu_move.set_volume(vol)
        if self.menu_select:
            vol = self.BASE_VOLUMES["menu_select"] * self.master_volume
            self.menu_select.set_volume(vol)
        if self.laser_shoot:
            vol = self.BASE_VOLUMES["laser_shoot"] * self.master_volume
            self.laser_shoot.set_volume(vol)
        if self.rocket_shoot:
            vol = self.BASE_VOLUMES["rocket_shoot"] * self.master_volume
            self.rocket_shoot.set_volume(vol)
        if self.boss_spawn:
            vol = self.BASE_VOLUMES["boss_spawn"] * self.master_volume
            self.boss_spawn.set_volume(vol)
        if self.boss_death:
            vol = self.BASE_VOLUMES["boss_death"] * self.master_volume
            self.boss_death.set_volume(vol)
        if self.powerup:
            vol = self.BASE_VOLUMES["powerup"] * self.master_volume
            self.powerup.set_volume(vol)
        if self.shield_activate:
            vol = self.BASE_VOLUMES["shield_activate"] * self.master_volume
            self.shield_activate.set_volume(vol)
        if self.level_up:
            vol = self.BASE_VOLUMES["level_up"] * self.master_volume
            self.level_up.set_volume(vol)
        if self.game_over:
            vol = self.BASE_VOLUMES["game_over"] * self.master_volume
            self.game_over.set_volume(vol)
        if self.player_hit:
            vol = self.BASE_VOLUMES["player_hit"] * self.master_volume
            self.player_hit.set_volume(vol)
