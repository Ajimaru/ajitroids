"""Audio Enhancement Module for Ajitroids

This module provides three major audio enhancements:
1. Dynamic Music System - Music changes based on game intensity
2. Voice Announcements - Audio announcements for key game events
3. Sound Themes - Multiple audio packs (retro, sci-fi, orchestral)
"""

import pygame
import time
import os
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from enum import Enum

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("pyttsx3 not available - voice announcements will be text-only")


class IntensityLevel(Enum):
    """Game intensity levels for dynamic music"""
    CALM = "calm"
    NORMAL = "normal"
    INTENSE = "intense"
    BOSS = "boss"


class SoundTheme(Enum):
    """Available sound themes"""
    DEFAULT = "default"
    RETRO = "retro"
    SCIFI = "scifi"
    ORCHESTRAL = "orchestral"


class DynamicMusicSystem:
    """Manages dynamic music that changes based on game intensity"""
    
    def __init__(self):
        self.current_intensity = IntensityLevel.CALM
        # Music tracks for different intensity levels
        # Note: Currently using the same track for CALM/NORMAL/INTENSE as only one background
        # music file exists. In future, add distinct tracks (e.g., background_calm.mp3,
        # background_intense.mp3) or implement volume/tempo variations for better effect.
        self.music_tracks = {
            IntensityLevel.CALM: "background.mp3",
            IntensityLevel.NORMAL: "background.mp3",
            IntensityLevel.INTENSE: "background.mp3",
            IntensityLevel.BOSS: "boss_music.mp3"
        }
        self.transition_cooldown = 0.0
        self.min_transition_time = 2.0  # Minimum seconds between transitions
        self.last_transition = 0.0
        self.enabled = True
        
    def calculate_intensity(self, asteroids_count: int, enemies_count: int, 
                          boss_active: bool, score: int, level: int) -> IntensityLevel:
        """Calculate game intensity based on current game state"""
        if boss_active:
            return IntensityLevel.BOSS
        
        # Calculate intensity score
        intensity_score = 0
        intensity_score += asteroids_count * 2
        intensity_score += enemies_count * 5
        intensity_score += (level - 1) * 3
        intensity_score += score // 10000
        
        # Determine intensity level
        if intensity_score >= 30:
            return IntensityLevel.INTENSE
        elif intensity_score >= 15:
            return IntensityLevel.NORMAL
        else:
            return IntensityLevel.CALM
    
    def update(self, dt: float, asteroids_count: int, enemies_count: int,
               boss_active: bool, score: int, level: int, asset_path_func) -> bool:
        """Update music based on game intensity. Returns True if music changed."""
        if not self.enabled:
            return False
            
        self.transition_cooldown -= dt
        
        new_intensity = self.calculate_intensity(
            asteroids_count, enemies_count, boss_active, score, level
        )
        
        # Only transition if cooldown expired and intensity changed
        if new_intensity != self.current_intensity and self.transition_cooldown <= 0:
            return self._transition_music(new_intensity, asset_path_func)
        
        return False
    
    def _transition_music(self, new_intensity: IntensityLevel, asset_path_func) -> bool:
        """Smoothly transition to new music track"""
        try:
            track = self.music_tracks[new_intensity]
            
            # Fade out current music (non-blocking)
            pygame.mixer.music.fadeout(1000)
            
            # Load and play new track
            pygame.mixer.music.load(asset_path_func(track))
            pygame.mixer.music.play(-1)
            
            self.current_intensity = new_intensity
            self.transition_cooldown = self.min_transition_time
            self.last_transition = time.time()
            
            print(f"Music transitioned to {new_intensity.value}")
            return True
        except Exception as e:
            print(f"Error transitioning music: {e}")
            return False
    
    def set_enabled(self, enabled: bool):
        """Enable or disable dynamic music system"""
        self.enabled = enabled


class VoiceAnnouncement:
    """Manages voice announcements for game events"""
    
    def __init__(self):
        self.announcement_queue: List[Tuple[str, float]] = []  # (text, priority)
        self.current_announcement: Optional[str] = None
        self.announcement_timer = 0.0
        self.min_announcement_gap = 1.5  # Minimum seconds between announcements
        self.last_announcement_time = 0.0
        self.enabled = True
        self.tts_engine = None
        self.tts_initialized = False
        
        # Per-announcement type enable flags (defaults, can be overridden)
        self.announcement_enabled = {
            "level_up": True,
            "boss_incoming": True,
            "boss_defeated": True,
            "game_over": True,
            "new_weapon": False,
            "shield_active": False,
            "low_health": False,
            "powerup": False,
            "extra_life": True,
            "achievement": True,
            "high_score": True,
        }
        
        # Map of event types to announcement text
        self.announcements = {
            "level_up": "Level up!",
            "boss_incoming": "Boss incoming!",
            "boss_defeated": "Boss defeated!",
            "game_over": "Game over!",
            "new_weapon": "New weapon acquired!",
            "shield_active": "Shield activated!",
            "low_health": "Warning! Low health!",
            "powerup": "Power-up collected!",
            "extra_life": "Extra life!",
            "achievement": "Achievement unlocked!",
            "high_score": "New high score!"
        }
        
        # Announcement sounds (text-to-speech or pre-recorded)
        self.announcement_sounds: Dict[str, Optional[pygame.mixer.Sound]] = {}
        
        # Initialize TTS engine if available
        if TTS_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                # Configure TTS settings
                self.tts_engine.setProperty('rate', 180)  # Speed of speech
                self.tts_engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
                self.tts_initialized = True
            except Exception as e:
                print(f"Failed to initialize TTS engine: {e}")
                self.tts_initialized = False
        
    def trigger(self, event_type: str, priority: float = 5.0):
        """Trigger a voice announcement for a game event"""
        if not self.enabled or event_type not in self.announcements:
            return
        
        # Check if this specific announcement type is enabled
        if not self.announcement_enabled.get(event_type, True):
            return
        
        current_time = time.time()
        if current_time - self.last_announcement_time < self.min_announcement_gap:
            # Queue for later if too soon
            self.announcement_queue.append((event_type, priority))
            return
        
        self._play_announcement(event_type)
    
    def _play_announcement(self, event_type: str):
        """Play the announcement sound/voice"""
        try:
            announcement_text = self.announcements.get(event_type, "")
            print(f"🔊 Announcement: {announcement_text}")
            
            # If we have a sound file for this announcement, play it
            if event_type in self.announcement_sounds:
                sound = self.announcement_sounds[event_type]
                if sound:
                    sound.play()
            
            self.current_announcement = announcement_text
            self.announcement_timer = 2.0  # Display text for 2 seconds
            self.last_announcement_time = time.time()
            
        except Exception as e:
            print(f"Error playing announcement: {e}")
    
    def update(self, dt: float):
        """Update announcement system"""
        self.announcement_timer -= dt
        
        if self.announcement_timer <= 0:
            self.current_announcement = None
            
            # Process queued announcements
            if self.announcement_queue:
                # Sort by priority (higher first) and play the highest priority
                self.announcement_queue.sort(key=lambda x: x[1], reverse=True)
                event_type, _ = self.announcement_queue.pop(0)
                self._play_announcement(event_type)
    
    def get_current_announcement(self) -> Optional[str]:
        """Get current announcement text for display"""
        return self.current_announcement
    
    def set_enabled(self, enabled: bool):
        """Enable or disable voice announcements"""
        self.enabled = enabled
    
    def set_announcement_type_enabled(self, event_type: str, enabled: bool):
        """Enable or disable a specific announcement type"""
        if event_type in self.announcement_enabled:
            self.announcement_enabled[event_type] = enabled
    
    def update_from_settings(self, announcement_types: dict):
        """Update announcement type flags from settings"""
        for event_type, enabled in announcement_types.items():
            if event_type in self.announcement_enabled:
                self.announcement_enabled[event_type] = enabled
    
    def _generate_voice_file(self, text: str, output_path: str) -> bool:
        """Generate voice audio file using TTS"""
        if not self.tts_initialized or not self.tts_engine:
            return False
        
        try:
            # Save to file
            self.tts_engine.save_to_file(text, output_path)
            self.tts_engine.runAndWait()
            return os.path.exists(output_path)
        except Exception as e:
            print(f"Error generating voice file: {e}")
            return False
    
    def load_announcement_sounds(self, asset_path_func):
        """Load or generate announcement sounds"""
        announcement_files = {
            "level_up": "voice_level_up.wav",
            "boss_incoming": "voice_boss_incoming.wav",
            "boss_defeated": "voice_boss_defeated.wav",
            "game_over": "voice_game_over.wav",
            "new_weapon": "voice_new_weapon.wav",
            "shield_active": "voice_shield.wav",
            "low_health": "voice_low_health.wav",
            "powerup": "voice_powerup.wav",
            "extra_life": "voice_extra_life.wav",
            "achievement": "voice_achievement.wav",
            "high_score": "voice_high_score.wav"
        }
        
        # Get assets directory
        assets_dir = Path(__file__).resolve().parent / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        for event_type, filename in announcement_files.items():
            try:
                sound_path = asset_path_func(filename)
                
                # If file doesn't exist, try to generate it with TTS
                if not os.path.exists(sound_path) and self.tts_initialized:
                    announcement_text = self.announcements.get(event_type, "")
                    if announcement_text:
                        print(f"Generating voice for: {event_type}")
                        full_path = assets_dir / filename
                        if self._generate_voice_file(announcement_text, str(full_path)):
                            sound_path = str(full_path)
                
                # Load the sound file
                if os.path.exists(sound_path):
                    self.announcement_sounds[event_type] = pygame.mixer.Sound(sound_path)
                else:
                    self.announcement_sounds[event_type] = None
            except Exception as e:
                print(f"Error loading announcement sound {event_type}: {e}")
                self.announcement_sounds[event_type] = None


class SoundThemeManager:
    """Manages multiple sound themes (retro, sci-fi, orchestral)"""
    
    def __init__(self):
        self.current_theme = SoundTheme.DEFAULT
        
        # Define sound mappings for each theme
        # Format: {theme: {sound_name: filename}}
        self.theme_mappings = {
            SoundTheme.DEFAULT: {
                "shoot": "shoot.wav",
                "explosion": "explosion.wav",
                "player_death": "player_hit.wav",
                "menu_move": "menu_select.wav",
                "menu_select": "menu_confirm.wav",
                "laser_shoot": "laser_shoot.wav",
                "rocket_shoot": "rocket_shoot.wav",
                "boss_spawn": "boss_spawn.wav",
                "boss_death": "boss_death.wav",
                "powerup": "powerup.wav",
                "shield_activate": "shield_hit.wav",
                "level_up": "level_up.wav",
                "game_over": "game_over.wav",
                "player_hit": "player_hit.wav",
                "background_music": "background.mp3",
                "boss_music": "boss_music.mp3"
            },
            SoundTheme.RETRO: {
                # Retro 8-bit style sounds - uses same files with different processing
                "shoot": "shoot.wav",
                "explosion": "explosion.wav",
                "player_death": "player_hit.wav",
                "menu_move": "menu_select.wav",
                "menu_select": "menu_confirm.wav",
                "laser_shoot": "laser_shoot.wav",
                "rocket_shoot": "rocket_shoot.wav",
                "boss_spawn": "boss_spawn.wav",
                "boss_death": "boss_death.wav",
                "powerup": "powerup.wav",
                "shield_activate": "shield_hit.wav",
                "level_up": "level_up.wav",
                "game_over": "game_over.wav",
                "player_hit": "player_hit.wav",
                "background_music": "background.mp3",
                "boss_music": "boss_music.mp3"
            },
            SoundTheme.SCIFI: {
                # Sci-fi futuristic sounds - intentionally uses laser sounds for shooting
                # to create a more futuristic audio experience
                "shoot": "laser_shoot.wav",
                "explosion": "explosion.wav",
                "player_death": "player_hit.wav",
                "menu_move": "menu_select.wav",
                "menu_select": "menu_confirm.wav",
                "laser_shoot": "laser_shoot.wav",
                "rocket_shoot": "rocket_shoot.wav",
                "boss_spawn": "boss_spawn.wav",
                "boss_death": "boss_death.wav",
                "powerup": "powerup.wav",
                "shield_activate": "shield_hit.wav",
                "level_up": "level_up.wav",
                "game_over": "game_over.wav",
                "player_hit": "player_hit.wav",
                "background_music": "background.mp3",
                "boss_music": "boss_music.mp3"
            },
            SoundTheme.ORCHESTRAL: {
                # Orchestral epic sounds - uses boss music for more cinematic experience
                "shoot": "shoot.wav",
                "explosion": "explosion.wav",
                "player_death": "player_hit.wav",
                "menu_move": "menu_select.wav",
                "menu_select": "menu_confirm.wav",
                "laser_shoot": "laser_shoot.wav",
                "rocket_shoot": "rocket_shoot.wav",
                "boss_spawn": "boss_spawn.wav",
                "boss_death": "boss_death.wav",
                "powerup": "powerup.wav",
                "shield_activate": "shield_hit.wav",
                "level_up": "level_up.wav",
                "game_over": "game_over.wav",
                "player_hit": "player_hit.wav",
                "background_music": "boss_music.mp3",
                "boss_music": "boss_music.mp3"
            }
        }
    
    def get_sound_file(self, sound_name: str) -> str:
        """Get the appropriate sound file for the current theme"""
        theme_map = self.theme_mappings.get(self.current_theme, {})
        return theme_map.get(sound_name, self.theme_mappings[SoundTheme.DEFAULT].get(sound_name, ""))
    
    def set_theme(self, theme: SoundTheme):
        """Change the current sound theme"""
        if theme in self.theme_mappings:
            self.current_theme = theme
            print(f"Sound theme changed to: {theme.value}")
            return True
        return False
    
    def get_current_theme(self) -> SoundTheme:
        """Get the current sound theme"""
        return self.current_theme
    
    def get_available_themes(self) -> List[SoundTheme]:
        """Get list of available sound themes"""
        return list(self.theme_mappings.keys())
    
    def get_theme_description(self, theme: SoundTheme) -> str:
        """Get a description of a sound theme"""
        descriptions = {
            SoundTheme.DEFAULT: "Classic Ajitroids sounds",
            SoundTheme.RETRO: "8-bit retro arcade style",
            SoundTheme.SCIFI: "Futuristic sci-fi sounds",
            SoundTheme.ORCHESTRAL: "Epic orchestral soundtrack"
        }
        return descriptions.get(theme, "Unknown theme")


class AudioEnhancementManager:
    """Main manager for all audio enhancements"""
    
    def __init__(self):
        self.dynamic_music = DynamicMusicSystem()
        self.voice_announcements = VoiceAnnouncement()
        self.theme_manager = SoundThemeManager()
        self.low_health_announced = False
        
    def update(self, dt: float, game_state: dict, asset_path_func):
        """Update all audio enhancement systems"""
        # Update dynamic music
        if "asteroids" in game_state and "enemies" in game_state:
            self.dynamic_music.update(
                dt,
                game_state.get("asteroids_count", 0),
                game_state.get("enemies_count", 0),
                game_state.get("boss_active", False),
                game_state.get("score", 0),
                game_state.get("level", 1),
                asset_path_func
            )
        
        # Update voice announcements
        self.voice_announcements.update(dt)
    
    def trigger_announcement(self, event_type: str, priority: float = 5.0):
        """Trigger a voice announcement"""
        self.voice_announcements.trigger(event_type, priority)
    
    def get_announcement_text(self) -> Optional[str]:
        """Get current announcement text for display"""
        return self.voice_announcements.get_current_announcement()
    
    def set_theme(self, theme: SoundTheme) -> bool:
        """Change sound theme"""
        return self.theme_manager.set_theme(theme)
    
    def get_current_theme(self) -> SoundTheme:
        """Get current sound theme"""
        return self.theme_manager.get_current_theme()
    
    def set_dynamic_music_enabled(self, enabled: bool):
        """Enable/disable dynamic music"""
        self.dynamic_music.set_enabled(enabled)
    
    def set_voice_announcements_enabled(self, enabled: bool):
        """Enable/disable voice announcements"""
        self.voice_announcements.set_enabled(enabled)
    
    def check_low_health(self, lives: int):
        """Check and trigger low health announcement if needed"""
        if lives == 1 and not self.low_health_announced:
            self.trigger_announcement("low_health", priority=7.0)
            self.low_health_announced = True
        elif lives > 1:
            self.low_health_announced = False
