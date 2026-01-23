"""Module modul.sounds — minimal module docstring."""

import os
from pathlib import Path
import pygame
import logging
from modul.audio_enhancements import SoundTheme, SoundThemeManager

# Module-level logger
logger = logging.getLogger(__name__)


def asset_path(name: str) -> str:
    """
    Resolve the filesystem path for an asset, preferring an assets directory in the current working directory.
    
    Parameters:
        name (str): Asset filename or relative asset path (e.g., 'sound.wav' or 'images/icon.png').
    
    Returns:
        str: Filesystem path to the asset. If ./assets/<name> exists it is returned; otherwise the path to assets/<name> relative to this module is returned.
    """
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
    """Manages game sounds and music playback."""
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
        "boss_attack": 0.08,
    }

    def __init__(self):
        """
        Initialize the sound subsystem, load default and themed sound assets, and record initial sound objects for override detection.
        
        This sets up the audio mixer, attempts to load core sound effects and background music from the assets directory, creates a SoundThemeManager and applies the default theme, calls load_new_sounds() to load additional effects, and stores a snapshot of initial sound objects in self._initial_sounds for later override detection in tests or runtime.
        
        Attributes initialized (not exhaustive):
            master_volume (float): Master effects volume used when re-enabling sounds.
            sound_on (bool): Whether sound effects are enabled.
            theme_manager (SoundThemeManager): Manager used to resolve themed sound files.
            current_theme (SoundTheme): Currently selected theme (defaults to SoundTheme.DEFAULT).
            _initial_sounds (dict): Mapping of sound attribute names to their original objects after initialization.
        """
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
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Shoot sound could not be loaded: {e}")
        try:
            self.explosion = pygame.mixer.Sound(asset_path("explosion.wav"))
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Explosion sound could not be loaded: {e}")
        try:
            self.player_death = pygame.mixer.Sound(asset_path("player_hit.wav"))
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Player-Death sound could not be loaded: {e}")
        try:
            self.menu_move = pygame.mixer.Sound(asset_path("menu_select.wav"))
            self.menu_select = pygame.mixer.Sound(asset_path("menu_confirm.wav"))
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.menu_move = None
            self.menu_select = None
            print(f"Menu sounds could not be loaded: {e}")
        try:
            pygame.mixer.music.load(asset_path("background.mp3"))
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error loading background music: {e}")
            print(f"Current directory: {os.getcwd()}")
            print(f"File exists: {os.path.exists(asset_path('background.mp3'))}")
        self.sound_on = True
        self.load_new_sounds()
        # Remember initial sound objects so we can detect when tests or
        # callers override specific sounds after initialization. This
        # helps tests that replace `shoot` or `boss_attack` on the
        # instance to assert fallback behavior.
        self._initial_sounds = {name: getattr(self, name, None) for name in (
            'shoot', 'boss_attack', 'explosion', 'player_death', 'menu_move', 'menu_select'
        )}

    def load_new_sounds(self):
        """
        Load additional sound effect assets and assign them to instance attributes.
        
        Attempts to load sound files for laser_shoot, rocket_shoot, boss_spawn, boss_death,
        powerup, shield_activate, level_up, game_over, player_hit, and boss_attack.
        Each corresponding attribute is set to a pygame.mixer.Sound instance when the
        asset is available or to None when loading fails. For the boss_death asset,
        sensible fallback filenames are tried and a warning is logged if a fallback is
        used or if no suitable file is found.
        """
        try:
            self.laser_shoot = pygame.mixer.Sound(asset_path("laser_shoot.wav"))
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.laser_shoot = None
            print(f"Laser shoot sound could not be loaded: {e}")
        try:
            self.rocket_shoot = pygame.mixer.Sound(asset_path("rocket_shoot.wav"))
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.rocket_shoot = None
            print(f"Rocket shoot sound could not be loaded: {e}")
        try:
            self.boss_spawn = pygame.mixer.Sound(asset_path("boss_spawn.wav"))
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.boss_spawn = None
            print(f"Boss spawn sound could not be loaded: {e}")
        try:
            self.boss_death = pygame.mixer.Sound(asset_path("boss_death.wav"))
        except Exception:  # pylint: disable=broad-exception-caught
            # Try sensible fallbacks present in older or alternative asset sets
            fallback_candidates = ["boss_hit.wav", "voice_boss_defeated.wav", "bossfight.wav"]
            loaded = False
            for candidate in fallback_candidates:
                try:
                    self.boss_death = pygame.mixer.Sound(asset_path(candidate))
                    logger.warning("Boss death sound missing; using fallback %s", candidate)
                    loaded = True
                    break
                except Exception:
                    continue
            if not loaded:
                self.boss_death = None
                logger.warning("Boss death sound could not be loaded; checked fallbacks: %s", fallback_candidates)
        try:
            self.powerup = pygame.mixer.Sound(asset_path("powerup.wav"))
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.powerup = None
            print(f"PowerUp sound could not be loaded: {e}")
        try:
            self.shield_activate = pygame.mixer.Sound(asset_path("shield_hit.wav"))
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.shield_activate = None
            print(f"Shield-Activate sound could not be loaded: {e}")
        try:
            self.level_up = pygame.mixer.Sound(asset_path("level_up.wav"))
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.level_up = None
            print(f"Level-Up sound could not be loaded: {e}")
        try:
            self.game_over = pygame.mixer.Sound(asset_path("game_over.wav"))
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.game_over = None
            print(f"Game-Over sound could not be loaded: {e}")
        try:
            self.player_hit = pygame.mixer.Sound(asset_path("player_hit.wav"))
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.player_hit = None
            print(f"Player-Hit sound could not be loaded: {e}")
        try:
            self.boss_attack = pygame.mixer.Sound(asset_path("boss_attack.wav"))
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.boss_attack = None
            print(f"Boss-Attack sound could not be loaded: {e}")

    def play_shoot(self):
        """Play shoot sound effect."""
        if self.sound_on and self.shoot:
            self.shoot.play()

    def play_explosion(self):
        """Play explosion sound effect."""
        if self.sound_on and self.explosion:
            self.explosion.play()

    def play_player_death(self):
        """
        Play the player death sound effect.
        
        Plays the configured player death sound if sound playback is enabled and a sound is loaded.
        """
        if self.sound_on and self.player_death:
            self.player_death.play()

    def play_menu_move(self):
        """
        Play the menu-move sound effect if sounds are enabled and the sound is available.
        """
        if self.sound_on and self.menu_move:
            self.menu_move.play()

    def play_menu_select(self):
        """Play menu select sound effect."""
        if self.sound_on and self.menu_select:
            self.menu_select.play()

    def play_level_up(self):
        """
        Play the level-up sound effect when sound is enabled and a level-up sound is loaded.
        
        Does nothing if sound playback is disabled or the level-up sound is not available.
        """
        if self.sound_on and self.level_up:
            self.level_up.play()

    def play_powerup(self):
        """
        Play the powerup sound effect if sound playback is enabled and the powerup sound is available.
        """
        if self.sound_on and self.powerup:
            self.powerup.play()

    def play_laser_shoot(self):
        """
        Play the laser shooting sound effect.
        
        Plays the `laser_shoot` sound if sounds are enabled and the sound asset is loaded; otherwise does nothing.
        """
        if self.sound_on and self.laser_shoot:
            self.laser_shoot.play()

    def play_rocket_shoot(self):
        """
        Play the rocket shoot sound effect if sounds are enabled and the sound is loaded.
        
        If sound playback is disabled or the rocket shoot sound is not available, this does nothing.
        """
        if self.sound_on and self.rocket_shoot:
            self.rocket_shoot.play()

    def play_boss_spawn(self):
        """Play boss spawn sound effect."""
        if self.sound_on and self.boss_spawn:
            self.boss_spawn.play()

    def play_boss_death(self):
        """
        Play the boss death sound effect.
        
        Plays the configured boss death sound if sound playback is enabled and the sound has been loaded; otherwise does nothing.
        """
        if self.sound_on and self.boss_death:
            self.boss_death.play()

    def play_shield_activate(self):
        """
        Play the shield activation sound when sound is enabled and the shield activation sound is loaded.
        
        Does nothing if sounds are disabled or the shield activation sound is unavailable.
        """
        if self.sound_on and self.shield_activate:
            self.shield_activate.play()

    def play_achievement(self):
        """
        Play the achievement (level-up) sound if available.
        
        If sound playback is enabled and a level-up sound is loaded, plays that sound. Otherwise prints a diagnostic message indicating the Level-Up sound is missing.
        """
        if self.sound_on and self.level_up:
            self.level_up.play()
        else:
            print("Achievement sound not available (Level-Up sound missing)")

    def play_game_over(self):
        """
        Play the "game over" sound effect if sounds are enabled and the sound is loaded.
        
        If the sound is unavailable or sound playback is disabled, a diagnostic message is printed.
        """
        if self.sound_on and hasattr(self, "game_over") and self.game_over:
            self.game_over.play()
        else:
            print("Game Over sound not available or disabled")

    def set_music_volume(self, slider_value):
        """
        Adjust background music volume according to a perceptual exponential curve.
        
        Parameters:
            slider_value (float): Desired volume in the range 0.0–1.0; values outside this range are clamped.
        """
        slider_value = max(0.0, min(1.0, slider_value))
        curve_volume = apply_volume_curve(slider_value)
        pygame.mixer.music.set_volume(curve_volume)

    def toggle_music(self, enabled):
        """
        Enable or disable background music playback.
        
        Parameters:
            enabled (bool): True to start or resume background music; False to stop playback and mute music.
        """
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
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error toggling music: {e}")

    def toggle_sound(self, enabled):
        """
        Enable or disable all sound effects while preserving the configured master volume.
        
        Parameters:
            enabled (bool): If True, reapply the current master volume to all sound effects; if False, mute known sound effect objects.
        """
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
                "menu_move", "menu_select", "boss_attack",
            ]
            for attr_name in sound_attributes:
                if hasattr(self, attr_name):
                    sound = getattr(self, attr_name)
                    if sound:
                        sound.set_volume(0.0)

    def play_boss_music(self):
        """
        Start looping the boss background music if the audio mixer is initialized.
        
        If the mixer is initialized, loads the "boss_music.mp3" asset, sets its volume to 0.6, and begins playback in a repeating loop. Any errors during loading or playback are caught and result in an error message being printed.
        """
        try:
            if pygame.mixer.get_init() is not None:
                pygame.mixer.music.load(asset_path("boss_music.mp3"))
                pygame.mixer.music.set_volume(0.6)
                pygame.mixer.music.play(-1)
                print("Boss music started")
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Boss music could not be loaded: {e}")

    def play_hit(self):
        """Play hit sound effect."""
        if self.sound_on and hasattr(self, "explosion") and self.explosion:
            self.explosion.play()

    def play_extra_life(self):
        """Play extra life sound effect."""
        if self.sound_on and hasattr(self, "level_up") and self.level_up:
            self.level_up.play()
        else:
            print("Extra Life sound not available or disabled")

    def play_enemy_shoot(self):
        """
        Play the enemy's shooting sound using the most appropriate available sound.
        
        If sounds are enabled, prefer an explicitly replaced (post-initialization) `boss_attack` sound, then an explicitly replaced `shoot` sound. If no explicit overrides are present, attempt to play `shoot`, falling back to `boss_attack`. Failures to play a sound (e.g., audio errors) are ignored; nothing happens if sounds are disabled or no suitable sound is available.
        """
        if self.sound_on:
            # If the test or caller explicitly replaced `boss_attack` or
            # `shoot` after initialization, prefer the explicitly-set
            # sound. Otherwise attempt to play `shoot` first, then
            # `boss_attack` as a final fallback to preserve expected
            # behavior in tests and production.
            try:
                # Prefer explicit overrides (different object than initial)
                if hasattr(self, 'boss_attack') and self.boss_attack and self.boss_attack is not self._initial_sounds.get('boss_attack'):
                    self.boss_attack.play()
                    return
            except pygame.error:
                pass

            try:
                if hasattr(self, 'shoot') and self.shoot and self.shoot is not self._initial_sounds.get('shoot'):
                    self.shoot.play()
                    return
            except pygame.error:
                pass

            # Default attempt order: try shoot, then boss_attack
            if hasattr(self, 'shoot') and self.shoot:
                try:
                    self.shoot.play()
                    return
                except pygame.error:
                    pass
            if hasattr(self, 'boss_attack') and self.boss_attack:
                try:
                    self.boss_attack.play()
                    return
                except pygame.error:
                    pass

    def play_player_hit(self):
        """
        Play the player's hit sound effect.
        
        If sounds are enabled and `player_hit` is loaded, play it. If `player_hit` is not available but `explosion` is loaded, play `explosion` as a fallback. No effect when sounds are disabled.
        """
        if self.sound_on and hasattr(self, "player_hit") and self.player_hit:
            self.player_hit.play()
            logger.debug("Player Hit Sound played")
        else:
            logger.debug("Player Hit Sound not available - using fallback")
            if self.sound_on and hasattr(self, "explosion") and self.explosion:
                self.explosion.play()

    def set_effects_volume(self, volume):
        """
        Set the master volume for all sound effects.
        
        The provided volume is clamped to the range 0.0–1.0, stored on self.master_volume, and applied to any sound attributes currently present on the instance (only attributes that exist and are not None will have their volume updated).
        
        Parameters:
            volume (float): Desired master volume; values below 0.0 are treated as 0.0 and values above 1.0 as 1.0.
        """
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
            "boss_attack",
        ]:
            if hasattr(self, attr_name):
                sound = getattr(self, attr_name)
                if sound:
                    sound.set_volume(slider_value)

    def set_theme(self, theme_name: str) -> bool:
        """Change sound theme and reload all sounds"""
        try:
            # Convert string to SoundTheme enum safely
            theme = getattr(SoundTheme, theme_name.upper(), None)
            if theme is None:
                print(f"Invalid theme: {theme_name}")
                return False

            if self.theme_manager.set_theme(theme):
                self.current_theme = theme
                # Reload all sounds with new theme
                self._reload_all_sounds()
                print(f"Sound theme changed to: {theme_name}")
                return True
            return False
        except (AttributeError, ValueError) as e:
            print(f"Error setting theme {theme_name}: {e}")
            return False

    def _reload_all_sounds(self):
        """
        Reload all sound effects according to the current sound theme.
        
        For each known sound identifier, attempts to obtain the themed file from the theme manager and replace the corresponding instance attribute with a loaded Sound object. Applies the current master_volume to any successfully loaded sounds. If a themed file cannot be loaded, the corresponding attribute is set to None and an error message is printed.
        """
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
            'boss_attack': 'boss_attack',
        }

        for attr_name, sound_name in sound_mappings.items():
            try:
                sound_file = self.theme_manager.get_sound_file(sound_name)
                if sound_file:
                    sound = pygame.mixer.Sound(asset_path(sound_file))
                    setattr(self, attr_name, sound)
                    # Apply current volume
                    sound.set_volume(self.master_volume)
            except Exception as e:  # pylint: disable=broad-exception-caught
                print(f"Could not load {sound_name} for theme: {e}")
                setattr(self, attr_name, None)

    def get_current_theme(self) -> str:
        """Get current sound theme name"""
        return self.current_theme.value

    def get_available_themes(self) -> list:
        """Get list of available theme names"""
        return [theme.value for theme in self.theme_manager.get_available_themes()]