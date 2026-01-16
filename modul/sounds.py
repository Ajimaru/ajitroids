import pygame
import os
from pathlib import Path
from modul.audio_enhancements import SoundThemeManager, SoundTheme


def asset_path(name: str) -> str:
    """Resolve asset path from CWD or packaged assets directory."""
    cwd_candidate = Path.cwd() / "assets" / name
    if cwd_candidate.exists():
        return str(cwd_candidate)
    return str(Path(__file__).resolve().parent / "assets" / name)


def apply_volume_curve(slider_value):
    """Apply quadratic curve to volume slider for perceptual volume control.

    0.5 (50%) maps to 1.0 (normal/reference volume).
    Creates larger perceived differences between slider positions.

    Formula: 4^(2*(slider - 0.5))
    Gives: 0% → 0.0625x, 50% → 1.0x, 100% → 16.0x
    More dramatic changes than exponential base 2.
    """
    return 4 ** (2 * (slider_value - 0.5))


class Sounds:
    # Base volume levels for individual sound effects (relative to master volume)
    # Heavily reduced to account for WAV files being typically very loud
    # and to make volume slider changes actually perceptible
    BASE_VOLUMES = {
        "shoot": 0.1,
        "explosion": 0.12,
        "player_death": 0.14,
        "menu_move": 0.06,
        "menu_select": 0.06,
        "laser_shoot": 0.04,
        "rocket_shoot": 0.05,
        "boss_spawn": 0.08,
        "boss_death": 0.1,
        "powerup": 0.08,
        "shield_activate": 0.06,
        "level_up": 0.08,
        "game_over": 0.12,
        "player_hit": 0.14,
    }

    def __init__(self):
        pygame.mixer.init(44100, -16, 2, 2048)
        self.shoot = None
        self.explosion = None
        self.player_death = None
        self.menu_move = None
        self.menu_select = None
        self.level_up = None
        self.master_volume = 0.5  # Default to mid volume for consistent toggle behavior
        self.theme_manager = SoundThemeManager()
        self.current_theme = SoundTheme.DEFAULT
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
        """Set master volume for all sound effects (linear 0.0-1.0)."""
        slider_value = max(0.0, min(1.0, volume))
        self.master_volume = slider_value

        for attr_name in [
            "shoot",
            "explosion",
            "player_death",
            "menu_move",
            "menu_select",
            "laser_shoot",
            "rocket_shoot",
            "boss_spawn",
            "boss_death",
            "powerup",
            "shield_activate",
            "level_up",
            "game_over",
            "player_hit",
        ]:
            if hasattr(self, attr_name):
                sound = getattr(self, attr_name)
                if sound:
                    sound.set_volume(slider_value)
    
    def set_theme(self, theme_name: str) -> bool:
        """Change sound theme and reload all sounds"""
        try:
            # Convert string to SoundTheme enum
            theme = SoundTheme[theme_name.upper()]
            
            if self.theme_manager.set_theme(theme):
                self.current_theme = theme
                # Reload all sounds with new theme
                self._reload_all_sounds()
                print(f"Sound theme changed to: {theme_name}")
                return True
            return False
        except (KeyError, ValueError):
            print(f"Invalid theme: {theme_name}")
            return False
    
    def _reload_all_sounds(self):
        """Reload all sound effects with current theme"""
        # Get themed sound files
        sound_mappings = {
            'shoot': 'shoot',
            'explosion': 'explosion',
            'player_death': 'player_death',
            'menu_move': 'menu_move',
            'menu_select': 'menu_select',
            'laser_shoot': 'laser_shoot',
            'rocket_shoot': 'rocket_shoot',
            'boss_spawn': 'boss_spawn',
            'boss_death': 'boss_death',
            'powerup': 'powerup',
            'shield_activate': 'shield_activate',
            'level_up': 'level_up',
            'game_over': 'game_over',
            'player_hit': 'player_hit',
        }
        
        for attr_name, sound_name in sound_mappings.items():
            try:
                sound_file = self.theme_manager.get_sound_file(sound_name)
                if sound_file:
                    sound = pygame.mixer.Sound(asset_path(sound_file))
                    setattr(self, attr_name, sound)
                    # Apply current volume
                    sound.set_volume(self.master_volume)
            except Exception as e:
                print(f"Could not load {sound_name} for theme: {e}")
                setattr(self, attr_name, None)
    
    def get_current_theme(self) -> str:
        """Get current sound theme name"""
        return self.current_theme.value
    
    def get_available_themes(self) -> list:
        """Get list of available theme names"""
        return [theme.value for theme in self.theme_manager.get_available_themes()]
